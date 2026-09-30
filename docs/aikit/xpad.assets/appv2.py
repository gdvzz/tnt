import gradio as gr
import requests
import json
import datetime
import tempfile
import os
import io
import time
from pydub import AudioSegment
from config_loader import config

# ================= 模型配置（从 config.json 读取） =================
# Whisper 语音识别配置
WHISPER_URL = config.get_model_url("whisper")
WHISPER_MODEL_ID = config.get_model_id("whisper")
WHISPER_API_KEY = config.get_api_key("whisper")

# TTS 语音合成配置
TTS_URL = config.get_model_url("tts")
TTS_MODEL_ID = config.get_model_id("tts")
TTS_API_KEY = config.get_api_key("tts")
TTS_VOICE = config.get_tts_voice()

# LLM 大语言模型配置
LLM_URL = config.get_model_url("llm")
LLM_MODEL_ID = config.get_model_id("llm")
LLM_API_KEY = config.get_api_key("llm")


# ================= 系统配置 =================
# 系统消息配置
ROLE_PROMPT = f"You are an AI assistant powered by {LLM_MODEL_ID} with speech by Coqui team. Current date: {{date}}. Answer short and professional."

# 界面常量
TITLE = "AI语音助手"
DESCRIPTION = """# AI语音助手"""
CSS = """.toast-wrap { display: none !important } """
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AVATAR_PATHS = (
    os.path.join(BASE_DIR, "assets", "avatars", "user.png"),  # 用户头像
    os.path.join(BASE_DIR, "assets", "avatars", "robot.png"),  # AI头像
)


class AudioFileManager:
    """
    管理临时音频文件的生命周期，定期清理过期文件

    属性：
        active_files (dict): 存储文件路径与最后访问时间戳的映射
    """

    def __init__(self):
        self.active_files = {}

    def create_temp_file(self, content, ext="mp3"):
        """创建临时音频文件"""
        temp_path = os.path.join(
            tempfile.gettempdir(), f"temp_audio_{os.urandom(4).hex()}.{ext}"
        )
        with open(temp_path, "wb") as f:
            f.write(content)
        self.active_files[temp_path] = time.time()
        return temp_path

    def cleanup(self):
        """清理超过5分钟未使用的临时文件"""
        now = time.time()
        for path in list(self.active_files.keys()):
            if now - self.active_files[path] > 300:
                try:
                    os.remove(path)
                    del self.active_files[path]
                except:
                    pass


# 初始化文件管理器单例
file_manager = AudioFileManager()


def _build_headers(api_key: str = "") -> dict:
    """构建通用请求头"""
    headers = {"User-Agent": "Gradio-App/1.0"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def transcribe_audio(file_path):
    """语音转文字功能（调用Whisper API）"""
    try:
        if not file_path or not os.path.isfile(file_path):
            raise ValueError(f"音频文件不存在: {file_path}")

        # 音频预处理：统一为 ASR 接口兼容性更好的 PCM WAV
        audio = AudioSegment.from_file(file_path)
        audio = (
            audio.set_frame_rate(16000)
            .set_channels(1)
            .set_sample_width(2)  # 16-bit PCM
        )

        # 转换为标准 WAV 字节流，避免部分接口无法解析重新编码的 MP3
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav", codec="pcm_s16le")
        wav_buffer.seek(0)

        if wav_buffer.getbuffer().nbytes <= 44:
            raise ValueError("音频文件为空或无有效音频数据")

        # 构建API请求
        files = {"file": ("audio.wav", wav_buffer, "audio/wav")}
        data = {"model": WHISPER_MODEL_ID}
        headers = _build_headers(WHISPER_API_KEY)

        # 发送请求并处理响应
        resp = requests.post(
            WHISPER_URL,
            files=files,
            data=data,
            headers=headers,
            timeout=config.timeouts.get("whisper", 60),
        )
        resp.raise_for_status()
        return resp.json().get("text", "请再说一遍").strip()

    except requests.exceptions.HTTPError as e:
        print(f"API请求失败: {e.response.text}")
        return "识别服务错误"
    except Exception as e:
        print(f"全局错误: {str(e)}")
        return "请再说一遍"


def generate_speech_bytes(text):
    """文字转语音功能（调用TTS API）"""
    try:
        payload = {
            "model": TTS_MODEL_ID,
            "input": text,
            "voice": TTS_VOICE,
        }
        headers = _build_headers(TTS_API_KEY)
        headers["Content-Type"] = "application/json"

        response = requests.post(
            TTS_URL,
            json=payload,
            headers=headers,
            timeout=config.timeouts.get("tts", 60),
        )
        response.raise_for_status()
        return file_manager.create_temp_file(response.content, "mp3")

    except Exception as e:
        print(f"语音生成错误: {e}")
    return None


def query_llm_stream(prompt, history):
    """大语言模型交互（流式响应）"""
    system_message = ROLE_PROMPT.format(date=datetime.date.today())
    messages = [{"role": "system", "content": system_message}]

    # 【修改点 3】直接继承字典格式的 history
    for msg in history:
        messages.append(msg)
    messages.append({"role": "user", "content": prompt})

    # 配置请求头
    headers = {
        "Content-Type": "application/json",
    }
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    else:
        headers["Authorization"] = "Bearer EMPTY"

    # 构建请求体
    payload = {
        "model": LLM_MODEL_ID,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
        "stream": True,
    }

    try:
        with requests.Session() as session:
            response = session.post(LLM_URL, headers=headers, json=payload, stream=True)
            response.raise_for_status()
            full_response = ""

            for line in response.iter_lines():
                if not line:
                    continue
                decoded = line.decode("utf-8").strip()
                if decoded.startswith("data:"):
                    decoded = decoded[5:].strip()
                if decoded == "[DONE]":
                    break
                try:
                    data = json.loads(decoded)
                    if data.get("choices"):
                        delta = data["choices"][0].get("delta", {})
                        token = delta.get("content", "")
                        full_response += token
                        yield full_response
                except:
                    continue
                yield full_response

    except Exception as e:
        yield f"请求失败: {str(e)}"


# ================= 交互处理函数 =================
def process_interaction(history, new_input):
    """
    处理完整交互流程
    1. 语音转文字
    2. 大模型生成回复
    3. 文字转语音
    4. 清理临时文件
    """
    history = history or []
    try:
        # 语音识别阶段
        text = transcribe_audio(new_input)

        # 【修改点 2】使用字典格式添加历史记录
        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": ""})

        # 传入当前输入，以及除去刚刚添加的这两条之外的历史记录
        text_generator = query_llm_stream(text, history[:-2])
        full_text = ""
        for partial_text in text_generator:
            history[-1]["content"] = partial_text  # 字典更新方式
            full_text = partial_text
            yield history, history, None

        # 语音合成阶段
        audio_path = generate_speech_bytes(full_text)
        yield history, history, audio_path

        # 清理临时文件
        file_manager.cleanup()

    except Exception as e:
        print(f"处理交互时发生错误: {e}")
        yield history, history, None


# ================= Gradio 界面 =================
with gr.Blocks(title=TITLE, css=CSS) as demo:
    gr.Markdown(DESCRIPTION)  # 渲染描述文本

    # 【修改点 1】已移除 type="tuples" 参数
    chatbot = gr.Chatbot(
        [],
        elem_id="chatbot",
        avatar_images=AVATAR_PATHS,
    )

    # 语音输入组件
    with gr.Row():
        btn = gr.Audio(
            sources="microphone",
            type="filepath",
            format="mp3",
            label="语音输入",
            show_label=True,
        )

    # 语音输出组件
    with gr.Row():
        audio = gr.Audio(
            value=None,
            label="AI语音回复",
            autoplay=True,  # 自动播放音频
            interactive=False,  # 禁止用户操作
            show_label=True,
            format="mp3",
        )

    # 清理按钮
    clear_btn = gr.ClearButton([chatbot, audio])

    # 事件绑定
    file_msg = btn.stop_recording(
        fn=lambda h, a: (h, a),
        inputs=[chatbot, btn],
        outputs=[chatbot, btn],
        queue=False,
    ).then(
        process_interaction, inputs=[chatbot, btn], outputs=[chatbot, chatbot, audio]
    )

    # 重置麦克风状态
    file_msg.then(
        lambda: gr.update(interactive=True, value=None), None, [btn], queue=False
    )


if __name__ == "__main__":
    demo.queue()  # 启用请求队列
    demo.launch(server_port=7860, height=800)  # 启动Web服务
