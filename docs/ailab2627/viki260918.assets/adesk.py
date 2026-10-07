#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面小管家 Agent - 语音播报版
Jetson 环境感知 + 本地 Ollama 生活助手 + edge-tts 语音

依赖：
    pip install ollama opencv-python numpy edge-tts
    sudo apt install -y mpg123

可选真实传感器：
    pip install smbus2
    并把 USE_REAL_BME280 改为 True
"""

import asyncio
import json
import os
import random
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional

import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False


# ===========================================================================
# 终端颜色
# ===========================================================================

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def cprint(text: str, color: str = "", bold: bool = False) -> None:
    prefix = (C.BOLD if bold else "") + color
    print(f"{prefix}{text}{C.RESET}")


# ===========================================================================
# 配置
# ===========================================================================

OLLAMA_MODEL = "qwen2.5:3b"
CAMERA_INDEX = 0
USE_REAL_BME280 = False
BME280_I2C_ADDR = 0x76
PHOTO_DIR = os.path.expanduser("~/desktop_agent_photos")
MAX_TOOL_ROUNDS = 2
KEEP_ALIVE = "30m"
LLM_OPTIONS = {
    "num_predict": 120,
    "temperature": 0.3,
    "num_ctx": 1024,
    "keep_alive": KEEP_ALIVE,
}

# 语音配置
VOICE_ENABLED_DEFAULT = True
EDGE_VOICE = "zh-CN-XiaoxiaoNeural"
EDGE_RATE = "+10%"
EDGE_VOLUME = "+0%"
ALSA_DEVICE = "plughw:3,0"   # 根据 aplay -l 修改
TTS_TMP = "/tmp/agent_tts.mp3"


# ===========================================================================
# 样例问题
# ===========================================================================

SAMPLES = [
    ("看看现在房间环境怎么样，给我一点居家建议", "环境总览（get_room_status）"),
    ("外面光线够不够，要不要开台灯？", "亮度判断（capture_light_estimate）"),
    ("帮我拍张照", "拍照（take_photo）"),
    ("现在温度和湿度是多少？", "温湿度（get_temphum）"),
    ("请自我介绍", "不调工具，直接回答"),
]


# ===========================================================================
# 语音播报
# ===========================================================================

async def _tts_generate(text: str, path: str) -> None:
    communicate = edge_tts.Communicate(
        text, EDGE_VOICE, rate=EDGE_RATE, volume=EDGE_VOLUME
    )
    await communicate.save(path)


def speak(text: str, verbose: bool = False) -> None:
    """用 edge-tts 生成语音并用 mpg123 播放。"""
    if not HAS_EDGE_TTS or not text:
        if verbose and not HAS_EDGE_TTS:
            cprint("[语音] 未安装 edge-tts，跳过播报。", C.YELLOW)
        return

    clean = text.replace("℃", "度").replace("%", "百分之")
    clean = clean.replace("/", " ").replace("_", " ").replace("*", "")

    try:
        asyncio.run(_tts_generate(clean, TTS_TMP))
    except Exception as e:
        cprint(f"[语音] 生成失败: {e}", C.RED)
        return

    try:
        subprocess.Popen(
            ["mpg123", "-q", "-a", ALSA_DEVICE, TTS_TMP],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        cprint(f"[语音] 播放失败: {e}", C.RED)


# ===========================================================================
# BME280
# ===========================================================================

class MockBME280:
    def __init__(self):
        self.temp = 24.0
        self.hum = 55.0
        self.pres = 1013.0

    def read(self) -> Dict[str, float]:
        self.temp += random.uniform(-0.3, 0.3)
        self.hum += random.uniform(-1.0, 1.0)
        self.pres += random.uniform(-0.5, 0.5)
        self.temp = max(15.0, min(35.0, self.temp))
        self.hum = max(20.0, min(90.0, self.hum))
        self.pres = max(980.0, min(1040.0, self.pres))
        return {
            "temperature_c": round(self.temp, 1),
            "humidity_pct": round(self.hum, 1),
            "pressure_hpa": round(self.pres, 1),
        }


class RealBME280:
    def __init__(self, addr: int = BME280_I2C_ADDR):
        try:
            from smbus2 import SMBus
        except ImportError as e:
            raise RuntimeError("请先安装 smbus2: pip install smbus2") from e
        self.bus = SMBus(1)
        self.addr = addr
        self._load_calibration()

    def _read_u16(self, reg: int) -> int:
        d = self.bus.read_i2c_block_data(self.addr, reg, 2)
        return (d[1] << 8) | d[0]

    def _read_s16(self, reg: int) -> int:
        v = self._read_u16(reg)
        return v - 65536 if v > 32767 else v

    def _load_calibration(self):
        self.dig_T = [self._read_u16(0x88), self._read_s16(0x8A), self._read_s16(0x8C)]
        self.dig_P = [
            self._read_u16(0x8E), self._read_s16(0x90), self._read_s16(0x92),
            self._read_s16(0x94), self._read_s16(0x96), self._read_s16(0x98),
            self._read_s16(0x9A), self._read_s16(0x9C), self._read_s16(0x9E),
        ]
        self.dig_H = [
            self.bus.read_byte_data(self.addr, 0xA1),
            self._read_u16(0xE1), self.bus.read_byte_data(self.addr, 0xE3),
        ]

    def _read_raw(self):
        self.bus.write_byte_data(self.addr, 0xF4, 0x27)
        self.bus.write_byte_data(self.addr, 0xF5, 0xA0)
        time.sleep(0.1)
        data = self.bus.read_i2c_block_data(self.addr, 0xF7, 8)
        adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        adc_h = (data[6] << 8) | data[7]
        return adc_p, adc_t, adc_h

    def read(self) -> Dict[str, float]:
        adc_p, adc_t, adc_h = self._read_raw()
        var1 = (adc_t / 16384.0 - self.dig_T[0] / 1024.0) * self.dig_T[1]
        var2 = (adc_t / 131072.0 - self.dig_T[0] / 8192.0) ** 2 * self.dig_T[2]
        t_fine = var1 + var2
        temp = t_fine / 5120.0

        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * self.dig_P[5] / 32768.0
        var2 += var1 * self.dig_P[4] * 2.0
        var2 = var2 / 4.0 + self.dig_P[3] * 65536.0
        var1 = (self.dig_P[2] * var1 * var1 / 524288.0 + self.dig_P[1] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P[0]
        if var1 == 0:
            pres = 0.0
        else:
            pres = 1048576.0 - adc_p
            pres = (pres - var2 / 4096.0) * 6250.0 / var1
            var1 = self.dig_P[8] * pres * pres / 2147483648.0
            var2 = pres * self.dig_P[7] / 32768.0
            pres = (pres + (var1 + var2 + self.dig_P[6]) / 16.0) / 100.0

        var_H = t_fine - 76800.0
        var_H = (adc_h - (self.dig_H[2] * 64.0 + self.dig_H[1] / 16384.0 * var_H)) * (
            self.dig_H[0] / 65536.0 * (
                1.0 + self.dig_H[3] / 67108864.0 * var_H *
                (1.0 + self.dig_H[4] / 67108864.0 * var_H)
            )
        )
        hum = var_H * (1.0 - self.dig_H[5] * var_H / 524288.0)
        hum = max(0.0, min(100.0, hum))

        return {
            "temperature_c": round(temp, 1),
            "humidity_pct": round(hum, 1),
            "pressure_hpa": round(pres, 1),
        }


def build_bme280():
    if USE_REAL_BME280:
        try:
            sensor = RealBME280(BME280_I2C_ADDR)
            cprint("[信息] 已连接真实 BME280。", C.GREEN)
            return sensor
        except Exception as e:
            cprint(f"[警告] 真实 BME280 失败，改用模拟: {e}", C.YELLOW)
    else:
        cprint("[信息] 使用模拟 BME280。", C.DIM)
    return MockBME280()


_bme = build_bme280()


# ===========================================================================
# 摄像头复用
# ===========================================================================

_camera = None


def _get_camera():
    global _camera
    if _camera is None and HAS_CV2:
        _camera = cv2.VideoCapture(CAMERA_INDEX)
        if not _camera.isOpened():
            _camera = None
    return _camera


def _read_brightness() -> tuple:
    brightness = None
    cam = _get_camera()
    if cam is not None:
        ret, frame = cam.read()
        if ret and frame is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = float(np.mean(gray))

    if brightness is None:
        brightness = float(np.random.randint(30, 220))
        simulated = True
    else:
        simulated = False

    if brightness < 60:
        level = "偏暗"
    elif brightness < 150:
        level = "适中"
    else:
        level = "偏亮"

    return round(brightness, 1), level, simulated


# ===========================================================================
# 工具函数
# ===========================================================================

def get_temphum() -> str:
    d = _bme.read()
    return f"温度{d['temperature_c']}℃,湿度{d['humidity_pct']}%,气压{d['pressure_hpa']}hPa"


def capture_light_estimate() -> str:
    brightness, level, simulated = _read_brightness()
    tag = "模拟" if simulated else "真实"
    return f"亮度{brightness}/255({level},{tag})"


def take_photo() -> str:
    os.makedirs(PHOTO_DIR, exist_ok=True)
    path = os.path.join(PHOTO_DIR, f"snapshot_{int(time.time())}.jpg")
    cam = _get_camera()
    if cam is not None:
        ret, frame = cam.read()
        if ret and frame is not None:
            cv2.imwrite(path, frame)
            return f"已保存到{path}"
    return "拍照失败:摄像头不可用"


def get_room_status() -> str:
    d = _bme.read()
    brightness, level, simulated = _read_brightness()
    tag = "模拟" if simulated else "真实"
    return (f"温度{d['temperature_c']}℃,湿度{d['humidity_pct']}%,"
            f"气压{d['pressure_hpa']}hPa,亮度{brightness}/255({level},{tag})")


# ===========================================================================
# 工具注册
# ===========================================================================

TOOLS_SCHEMA: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_room_status",
            "description": "获取房间整体环境：温湿度、气压、亮度",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_temphum",
            "description": "读取室内温度湿度气压",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "capture_light_estimate",
            "description": "估算环境亮度",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_photo",
            "description": "保存当前画面快照",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_MAP: Dict[str, Callable[..., str]] = {
    "get_room_status": get_room_status,
    "get_temphum": get_temphum,
    "capture_light_estimate": capture_light_estimate,
    "take_photo": take_photo,
}

TOOL_LABEL = {
    "get_room_status": "获取房间整体环境",
    "get_temphum": "读取温湿度气压",
    "capture_light_estimate": "估算环境亮度",
    "take_photo": "保存画面快照",
}


# ===========================================================================
# Agent 核心
# ===========================================================================

SYSTEM_PROMPT = (
    "你是桌面环境小管家。用户问房间整体状况时用 get_room_status；"
    "只问温度湿度用 get_temphum；只问亮度用 capture_light_estimate；"
    "要拍照用 take_photo。拿到数据后给 1-2 句口语化建议，不要编造。"
)


def _parse_args(raw: Any) -> Dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    return {}


def run_agent(user_input: str, verbose: bool = True) -> str:
    if not HAS_OLLAMA:
        return "[错误] 未安装 ollama Python 包。"

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=TOOLS_SCHEMA,
                options=LLM_OPTIONS,
            )
        except Exception as e:
            return f"[错误] 调用 Ollama 失败: {e}"

        msg = response.get("message", {})
        tool_calls = msg.get("tool_calls") or []

        if not tool_calls:
            return msg.get("content", "").strip() or "(模型没有返回内容)"

        messages.append(msg)

        for call in tool_calls:
            fn = call.get("function", {})
            name = fn.get("name", "")
            args = _parse_args(fn.get("arguments"))

            if verbose:
                label = TOOL_LABEL.get(name, name)
                cprint(f"  🔧 {label}", C.CYAN)

            if name not in TOOL_MAP:
                result = f"未知工具{name}"
            else:
                try:
                    result = TOOL_MAP[name](**args)
                except Exception as e:
                    result = f"工具出错:{e}"

            if verbose:
                cprint(f"     ↳ {result}", C.DIM)

            messages.append({"role": "tool", "name": name, "content": result})

    try:
        final = ollama.chat(model=OLLAMA_MODEL, messages=messages, options=LLM_OPTIONS)
        return final.get("message", {}).get("content", "").strip() or "(无内容)"
    except Exception as e:
        return f"[错误] 最终总结失败: {e}"


def run_fast(user_input: str, verbose: bool = True) -> str:
    if not HAS_OLLAMA:
        return "[错误] 未安装 ollama Python 包。"

    if verbose:
        cprint("  ⚡ 快速模式：直接读取环境数据", C.YELLOW)

    status = get_room_status()
    if verbose:
        cprint(f"     ↳ {status}", C.DIM)

    messages = [
        {"role": "system", "content": "你是桌面环境小管家。根据环境数据给 1-2 句口语化生活建议，不要编造。"},
        {"role": "user", "content": f"{user_input}\n\n当前环境数据：{status}"},
    ]
    try:
        final = ollama.chat(model=OLLAMA_MODEL, messages=messages, options=LLM_OPTIONS)
        return final.get("message", {}).get("content", "").strip() or "(无内容)"
    except Exception as e:
        return f"[错误] 总结失败: {e}"


# ===========================================================================
# 预热
# ===========================================================================

def warmup() -> None:
    if not HAS_OLLAMA:
        return
    cprint("[预热] 加载模型...", C.YELLOW)
    t0 = time.time()
    try:
        ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": "你好"}],
            options={"num_predict": 5, "keep_alive": KEEP_ALIVE},
        )
        cprint(f"[预热] 完成，用时 {time.time()-t0:.1f}s", C.GREEN)
    except Exception as e:
        cprint(f"[预热] 失败: {e}", C.RED)


# ===========================================================================
# 帮助与样例
# ===========================================================================

def print_help() -> None:
    print()
    cprint("可用命令：", C.BOLD)
    print(f"  {C.CYAN}/help{C.RESET}         显示本帮助")
    print(f"  {C.CYAN}/samples{C.RESET}      显示样例问题")
    print(f"  {C.CYAN}/fast 问题{C.RESET}    快速模式，跳过第一轮 LLM")
    print(f"  {C.CYAN}/voice{C.RESET}        开关语音播报")
    print(f"  {C.CYAN}1-{len(SAMPLES)}{C.RESET}           直接输入编号，运行对应样例")
    print(f"  {C.CYAN}q{C.RESET}             退出")
    print()
    print_samples()


def print_samples() -> None:
    cprint("样例问题：", C.BOLD)
    for i, (q, desc) in enumerate(SAMPLES, 1):
        print(f"  {C.GREEN}{i}{C.RESET}. {q}  {C.DIM}({desc}){C.RESET}")
    print()


# ===========================================================================
# 终端入口
# ===========================================================================

BANNER = f"""{C.CYAN}{C.BOLD}
========================================
  桌面小管家 Agent (Jetson + Ollama)
  输入自然语言提问，q 退出
  输入 /help 查看命令和样例
========================================{C.RESET}
"""


def main():
    voice_on = VOICE_ENABLED_DEFAULT

    print(BANNER)
    cprint(
        f"[配置] 模型: {OLLAMA_MODEL} | 摄像头: {CAMERA_INDEX} | "
        f"真实BME280: {USE_REAL_BME280} | 语音: {'开' if voice_on else '关'}",
        C.DIM,
    )
    warmup()
    print_samples()

    while True:
        try:
            user_input = input(f"{C.GREEN}{C.BOLD}你：{C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            cprint("再见。", C.CYAN)
            break

        if not user_input:
            continue

        low = user_input.lower()
        if low in ("q", "quit", "exit"):
            cprint("再见。", C.CYAN)
            break
        if low in ("/help", "help", "?"):
            print_help()
            continue
        if low in ("/samples", "samples"):
            print_samples()
            continue
        if low == "/voice":
            voice_on = not voice_on
            cprint(f"  语音播报：{'开' if voice_on else '关'}", C.YELLOW)
            continue

        fast = False
        if low.startswith("/fast"):
            fast = True
            user_input = user_input[5:].strip() or SAMPLES[0][0]

        if user_input.isdigit():
            idx = int(user_input)
            if 1 <= idx <= len(SAMPLES):
                user_input = SAMPLES[idx - 1][0]
                cprint(f"  → 执行样例 {idx}：{user_input}", C.BLUE)
            else:
                cprint(f"  无效编号，请输入 1-{len(SAMPLES)}", C.RED)
                continue

        t0 = time.time()
        answer = run_fast(user_input) if fast else run_agent(user_input)
        elapsed = time.time() - t0

        cprint(f"小管家：{answer}", C.MAGENTA, bold=True)
        cprint(f"  (用时 {elapsed:.1f}s)", C.DIM)

        if voice_on:
            speak(answer)

        print()


if __name__ == "__main__":
    main()
