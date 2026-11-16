#!/usr/bin/env python3
"""Standalone TM1638 test tool (LED / 7-segment / buttons).

This file is extracted from the old ``jeston_ai`` project and now lives in the
new ``app`` directory.  It is self-contained, so you can test the TM1638 board
without importing ``assistant`` or any other part of the demo:

  * low-level bit-banging:  rpi_TM1638/TM1638s.py
  * LED / segment / switch: rpi_TM1638/TMBoards.py
  * 7-segment font:         rpi_TM1638/Font.py

The original driver and font come from the ``rpi_TM1638`` project.  The
protocol constants and font are kept for compatibility.

Wiring (Jetson 40-pin header):

    TM1638 VCC -> pin 1  (3.3V)
    TM1638 GND -> pin 6  (GND)
    TM1638 STB -> pin 11 (GPIO17 / BCM 17)
    TM1638 CLK -> pin 13 (GPIO27 / BCM 27)
    TM1638 DIO -> pin 15 (GPIO22 / BCM 22)

The code uses BCM numbers (17/27/22), which are the defaults below.

Note: Jetson.GPIO ignores the internal pull-up/down setting.  Reading the
TM1638 buttons therefore needs an external 4.7k-10k resistor from DIO to
3.3V; otherwise the key-scan bytes may read as all zeros.

Usage on a Jetson (real hardware):

    python tm1638_standalone.py demo
    python tm1638_standalone.py led on 1 3
    python tm1638_standalone.py led off 2
    python tm1638_standalone.py led all
    python tm1638_standalone.py led clear
    python tm1638_standalone.py text HELLO
    python tm1638_standalone.py clear
    python tm1638_standalone.py keys
    python tm1638_standalone.py raw
    python tm1638_standalone.py watch
    python tm1638_standalone.py menu
    python tm1638_standalone.py --wiring
    python tm1638_standalone.py --check
    python tm1638_standalone.py --selftest
    python tm1638_standalone.py --test-keys

On a computer without ``Jetson.GPIO`` the script automatically uses a simple
simulation.  You can also force it with ``--sim``:

    python tm1638_standalone.py --sim demo

If nothing lights up on the Jetson, run ``--check`` first.  It reports whether
``Jetson.GPIO`` is importable, whether the pins can be configured, and prints
the wiring table.  ``--require-hardware`` disables the automatic simulation
fallback, so a missing GPIO library becomes an error instead of a silent
simulation.

In simulation mode the LEDs / display are printed to the terminal, and the
``watch`` command lets you type switch numbers to test the button logic.
"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from collections.abc import Iterable, Sequence

# ---------------------------------------------------------------------------
# 7-segment font (copied from rpi_TM1638/Font.py)
#
# Bit layout:
#      -- 0 --
#     |       |
#     5       1
#     |       |
#      -- 6 --
#     |       |
#     4       2
#     |       |
#      -- 3 --   o 7
# ---------------------------------------------------------------------------
FONT = {
    " ": 0b00000000,
    "!": 0b10000110,
    '"': 0b00100010,
    "(": 0b00110000,
    ")": 0b00000110,
    ",": 0b00000100,
    "-": 0b01000000,
    ".": 0b10000000,
    "/": 0b01010010,
    "0": 0b00111111,
    "1": 0b00000110,
    "2": 0b01011011,
    "3": 0b01001111,
    "4": 0b01100110,
    "5": 0b01101101,
    "6": 0b01111101,
    "7": 0b00100111,
    "8": 0b01111111,
    "9": 0b01101111,
    "=": 0b01001000,
    "?": 0b01010011,
    "@": 0b01011111,
    "A": 0b01110111,
    "B": 0b01111111,
    "C": 0b00111001,
    "D": 0b00111111,
    "E": 0b01111001,
    "F": 0b01110001,
    "G": 0b00111101,
    "H": 0b01110110,
    "I": 0b00000110,
    "J": 0b00011111,
    "K": 0b01101001,
    "L": 0b00111000,
    "M": 0b00010101,
    "N": 0b00110111,
    "O": 0b00111111,
    "P": 0b01110011,
    "Q": 0b01100111,
    "R": 0b00110001,
    "S": 0b01101101,
    "T": 0b01111000,
    "U": 0b00111110,
    "V": 0b00101010,
    "W": 0b00011101,
    "X": 0b01110110,
    "Y": 0b01101110,
    "Z": 0b01011011,
    "[": 0b00111001,
    "]": 0b00001111,
    "_": 0b00001000,
    "`": 0b00100000,
    "a": 0b01011111,
    "b": 0b01111100,
    "c": 0b01011000,
    "d": 0b01011110,
    "e": 0b01111011,
    "f": 0b00110001,
    "g": 0b01101111,
    "h": 0b01110100,
    "i": 0b00000100,
    "j": 0b00001110,
    "k": 0b01110101,
    "l": 0b00110000,
    "m": 0b01010101,
    "n": 0b01010100,
    "o": 0b01011100,
    "p": 0b01110011,
    "q": 0b01100111,
    "r": 0b01010000,
    "s": 0b01101101,
    "t": 0b01111000,
    "u": 0b00011100,
    "v": 0b00101010,
    "w": 0b00011101,
    "x": 0b01110110,
    "y": 0b01101110,
    "z": 0b01000111,
    "{": 0b01000110,
    "|": 0b00000110,
    "}": 0b01110000,
    "~": 0b00000001,
}

# TM1638 commands
WRITE_MODE = 0x00
READ_MODE = 0x02
INCR_ADDR = 0x00
FIXED_ADDR = 0x04
SEGMENT_BASE = 0xC0

# Jetson 40-pin header wiring used by this script.
WIRING = (
    ("VCC", "1", "3.3V", ""),
    ("GND", "6", "GND", ""),
    ("STB", "11", "GPIO17", "BCM 17"),
    ("CLK", "13", "GPIO27", "BCM 27"),
    ("DIO", "15", "GPIO22", "BCM 22"),
)


def print_wiring() -> None:
    """Print the physical pin mapping for the TM1638 board."""

    print("TM1638 -> Jetson 40PIN")
    print(f"{'信号':<6}{'物理引脚':<10}{'GPIO':<10}说明")
    for signal, pin, gpio, note in WIRING:
        print(f"{signal:<6}{pin:<10}{gpio:<10}{note}")
    print("\n代码使用 BCM 编号：STB=17, CLK=27, DIO=22")
    print("按键读取需要在 DIO（引脚 15）与 3.3V（引脚 1/17）之间")
    print("加一个 4.7k~10k 上拉电阻；Jetson.GPIO 不支持内部上拉。")
    print("如果 BCM 映射不一致，可改用物理引脚：")
    print("  python tm1638_standalone.py --pin-mode board --stb 11 --clk 13 --dio 15 demo")
    print("\n如果 3.3V 供电完全不亮，可尝试把 VCC 接到 5V（物理引脚 2 或 4），")
    print("GND 保持引脚 6；部分模块在 5V 下才足够亮，必要时请加电平转换。")


_GPIO_IMPORT_ERROR: str | None = None


def _load_gpio():
    """Import Jetson.GPIO, or return None when it is unavailable."""

    global _GPIO_IMPORT_ERROR
    try:
        import Jetson.GPIO as GPIO

        _GPIO_IMPORT_ERROR = None
        return GPIO
    except Exception as exc:  # pragma: no cover - depends on the host
        _GPIO_IMPORT_ERROR = f"{type(exc).__name__}: {exc}"
        return None


def _text_to_segments(text: str) -> list[int]:
    """Convert text to the 8 segment bytes used by the display.

    A '.' is merged into the previous digit (as in the original driver).  Any
    character missing from FONT is replaced by a space.
    """

    values: list[int] = []
    for char in text:
        if char == "." and values:
            values[-1] |= 0x80
        else:
            values.append(FONT.get(char, FONT[" "]))

    values = values[:8]
    values.extend([FONT[" "]] * (8 - len(values)))
    return values


class TM1638:
    """Control one TM1638 board: 8 LEDs, 8 digits, 8 switches."""

    def __init__(
        self,
        stb: int = 17,
        clk: int = 27,
        dio: int = 22,
        brightness: int = 3,
        simulate: bool = False,
        pin_mode: str = "bcm",
        delay_us: float = 5.0,
    ) -> None:
        self._stb = stb
        self._clk = clk
        self._dio = dio
        self._brightness = brightness & 0x07
        self._pin_mode = pin_mode.lower()
        if self._pin_mode not in {"bcm", "board"}:
            raise ValueError("pin_mode 只能是 'bcm' 或 'board'")
        self._delay = max(0.0, float(delay_us)) / 1_000_000

        self._gpio = None if simulate else _load_gpio()
        self.simulated = self._gpio is None

        self._leds = [False] * 8
        self._segments = [0] * 8
        self._simulated_keys = [0, 0, 0, 0]
        self._closed = False

        if self.simulated:
            if simulate:
                print("[sim] 已按 --sim 进入模拟模式（不会驱动真实 GPIO）")
            else:
                print("=" * 64)
                print("警告：未检测到 Jetson.GPIO，已自动进入模拟模式！")
                print("      这不会点亮真实 LED / 数码管。")
                if _GPIO_IMPORT_ERROR:
                    print(f"      原因: {_GPIO_IMPORT_ERROR}")
                print("      运行 python tm1638_standalone.py --check 查看详情。")
                print("=" * 64)
            print(
                "[sim] TM1638 simulated "
                f"(stb={stb}, clk={clk}, dio={dio}, brightness={self._brightness})"
            )
            return

        GPIO = self._gpio
        if hasattr(GPIO, "setwarnings"):
            GPIO.setwarnings(False)
        mode = GPIO.BOARD if self._pin_mode == "board" else GPIO.BCM
        GPIO.setmode(mode)
        GPIO.setup(self._stb, GPIO.OUT)
        GPIO.setup(self._clk, GPIO.OUT)
        GPIO.setup(self._dio, GPIO.OUT)

        self._write_pin(self._stb, True)
        self._write_pin(self._clk, True)
        self._write_pin(self._dio, True)
        time.sleep(0.05)

        # Turn display on and set brightness (0-7).
        self._send_command(0x88 | self._brightness)
        self.clear_all()

    @property
    def stb(self) -> int:
        return self._stb

    @property
    def clk(self) -> int:
        return self._clk

    @property
    def dio(self) -> int:
        return self._dio

    @property
    def pin_mode(self) -> str:
        return self._pin_mode

    # ------------------------------------------------------------------ LEDs
    def set_led(self, index: int, on: bool) -> None:
        """Set one LED. ``index`` is 0-based (0 is LED 1 on the board)."""

        if not 0 <= index < 8:
            raise ValueError(f"LED 序号必须在 0..7 之间，收到 {index}")

        self._leds[index] = bool(on)
        if self.simulated:
            print(f"[sim] LED {index + 1} -> {'ON' if on else 'OFF'}")
            return
        self._write_byte(index * 2 + 1, 1 if on else 0)

    def set_leds(self, states: Sequence[bool]) -> None:
        """Set all 8 LEDs from a boolean sequence."""

        states = list(states)[:8]
        for index in range(8):
            self.set_led(index, states[index] if index < len(states) else False)

    def led_on(self, *indexes: int) -> None:
        for index in indexes:
            self.set_led(index, True)

    def led_off(self, *indexes: int) -> None:
        for index in indexes:
            self.set_led(index, False)

    def all_leds(self, on: bool) -> None:
        for index in range(8):
            self.set_led(index, on)

    def clear_leds(self) -> None:
        self.all_leds(False)

    # -------------------------------------------------------------- 7-segment
    def show(self, text: str) -> None:
        """Display up to 8 characters (left aligned)."""

        values = _text_to_segments(text)
        self._segments = values

        if self.simulated:
            print(f"[sim] display: {text[:8]!r}  raw={values}")
            return

        # The digits live at even addresses: 0x00, 0x02, ... 0x0E.
        # The odd addresses are the LEDs, so write each digit separately with
        # a fixed-address command instead of using auto-increment.
        for index, value in enumerate(values):
            self._write_byte(index * 2, value)

    def set_segment(self, index: int, char: str) -> None:
        """Display one character at digit ``index`` (0-based)."""

        self.set_segment_bits(index, FONT.get(char, FONT[" "]))

    def set_segment_bits(self, index: int, value: int) -> None:
        """Write a raw segment bitmask to one digit (for advanced testing)."""

        if not 0 <= index < 8:
            raise ValueError(f"数码管序号必须在 0..7 之间，收到 {index}")

        self._segments[index] = value & 0xFF
        if self.simulated:
            print(f"[sim] digit {index + 1} raw=0x{value & 0xFF:02X}")
            return
        self._write_byte(index * 2, value & 0xFF)

    def clear_display(self) -> None:
        """Clear only the 8 digits; LEDs are left unchanged."""

        self.show(" " * 8)

    def clear_all(self) -> None:
        """Clear both digits and LEDs."""

        self._leds = [False] * 8
        self._segments = [0] * 8

        if self.simulated:
            print("[sim] clear display + LEDs")
            return

        self._stb_low()
        self._send_byte(0x40 | WRITE_MODE | INCR_ADDR)
        self._stb_high()

        self._stb_low()
        self._send_byte(SEGMENT_BASE)
        for _ in range(16):
            self._send_byte(0x00)
        self._stb_high()

    # ---------------------------------------------------------------- buttons
    def read_key_bytes(self) -> list[int]:
        """Read the 4 raw key-scan bytes (one byte per K0..K3 line)."""

        if self.simulated:
            return list(self._simulated_keys)

        GPIO = self._gpio
        self._stb_low()
        self._set_data_mode(READ_MODE, INCR_ADDR)
        time.sleep(20e-6)

        # DIO must stay an input for the whole 4-byte read.  Reconfiguring the
        # pin between bytes is slow on Jetson.GPIO and can break the key-scan
        # sequence.  The TM1638 needs a pull-up on DIO; Jetson.GPIO ignores
        # ``pull_up_down``, so an external 4.7k-10k resistor may be required.
        GPIO.setup(self._dio, GPIO.IN)
        time.sleep(50e-6)
        data = [self._read_byte() for _ in range(4)]
        GPIO.setup(self._dio, GPIO.OUT)
        self._stb_high()
        return data

    def read_dio_level(self) -> int | None:
        """Return the idle level of DIO (for wiring diagnostics)."""

        if self.simulated:
            return None
        GPIO = self._gpio
        GPIO.setup(self._dio, GPIO.IN)
        time.sleep(20e-6)
        value = GPIO.input(self._dio)
        GPIO.setup(self._dio, GPIO.OUT)
        return int(bool(value))

    def pressed_keys(self) -> list[int]:
        """Return raw key positions that are pressed.

        The result uses ``byte_index * 8 + bit_index`` (0..31), which is handy
        for checking the wiring of a board with a different key layout.
        """

        pressed: list[int] = []
        for byte_index, value in enumerate(self.read_key_bytes()):
            for bit_index in range(8):
                if value & (1 << bit_index):
                    pressed.append(byte_index * 8 + bit_index)
        return pressed

    def pressed_switches(self) -> list[bool]:
        """Return the 8 on-board switches using the old TMBoards mapping.

        The original ``TMBoards.Switches`` mapping for one board is:

            switch 1..4 -> bit 0 of key byte 0..3
            switch 5..8 -> bit 4 of key byte 0..3

        Unlike the old ``== 1`` / ``== 16`` check, this uses bit masks, so
        multiple simultaneously pressed switches are also detected.
        """

        key_bytes = self.read_key_bytes()
        states: list[bool] = []
        for switch_index in range(8):
            byte_index = switch_index % 4
            bit = 0 if switch_index < 4 else 4
            states.append(bool(key_bytes[byte_index] & (1 << bit)))
        return states

    def is_switch_pressed(self, index: int) -> bool:
        """Return whether switch ``index`` (0-based) is currently pressed."""

        if not 0 <= index < 8:
            raise ValueError(f"按键序号必须在 0..7 之间，收到 {index}")
        return self.pressed_switches()[index]

    def wait_for_switch(
        self,
        timeout: float | None = None,
        poll_interval: float = 0.01,
    ) -> int | None:
        """Wait for a new button press and return its 0-based index.

        A press is reported once (on the rising edge); holding the button does
        not repeat.  Returns ``None`` on timeout.
        """

        start = time.monotonic()
        previous = self.pressed_switches()

        while True:
            current = self.pressed_switches()
            for index in range(len(previous)):
                if current[index] and not previous[index]:
                    return index
            previous = current

            if timeout is not None and time.monotonic() - start >= timeout:
                return None
            time.sleep(poll_interval)

    def simulate_switch(self, index: int, pressed: bool = True) -> None:
        """Set a simulated switch state (only useful with ``simulate=True``)."""

        if not self.simulated:
            raise RuntimeError("simulate_switch() 只能在模拟模式下使用")
        if not 0 <= index < 8:
            raise ValueError(f"按键序号必须在 0..7 之间，收到 {index}")

        byte_index = index % 4
        bit = 0 if index < 4 else 4
        if pressed:
            self._simulated_keys[byte_index] |= 1 << bit
        else:
            self._simulated_keys[byte_index] &= ~(1 << bit)

    # ---------------------------------------------------------------- cleanup
    def test_pins(self, rounds: int = 2, interval: float = 0.5) -> None:
        """Toggle STB/CLK/DIO so the wiring can be checked with a meter.

        This is a diagnostic helper.  While it runs, each pin is driven high
        and low for ``interval`` seconds.  Afterwards the display is
        re-initialised.
        """

        if self.simulated:
            print("[sim] 模拟模式不会真正翻转引脚")
            return

        print("引脚自检：用万用表测量 STB / CLK / DIO 对 GND 的电压")
        print(f"每个引脚会高/低各保持 {interval:g} 秒，共 {rounds} 轮。")
        for name, pin in (("STB", self._stb), ("CLK", self._clk), ("DIO", self._dio)):
            print(f"  正在测试 {name} (pin {pin}) ...")
            for _ in range(rounds):
                self._write_pin(pin, True)
                time.sleep(interval)
                self._write_pin(pin, False)
                time.sleep(interval)

        # Restore the idle state and re-initialise the board.
        self._write_pin(self._stb, True)
        self._write_pin(self._clk, True)
        self._write_pin(self._dio, True)
        self._send_command(0x88 | self._brightness)
        self.clear_all()
        print("引脚自检结束。")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._gpio is None:
            return
        try:
            self._gpio.cleanup([self._stb, self._clk, self._dio])
        except Exception:
            try:
                self._gpio.cleanup()
            except Exception:
                pass

    def __enter__(self) -> TM1638:
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    # ---------------------------------------------------------------- internal
    def _send_command(self, command: int) -> None:
        self._stb_low()
        self._send_byte(command)
        self._stb_high()

    def _write_byte(self, address: int, value: int) -> None:
        self._stb_low()
        self._send_byte(0x40 | WRITE_MODE | FIXED_ADDR)
        self._stb_high()

        self._stb_low()
        self._send_byte(SEGMENT_BASE | (address & 0x0F))
        self._send_byte(value & 0xFF)
        self._stb_high()

    def _set_data_mode(self, write_mode: int, address_mode: int) -> None:
        self._send_byte(0x40 | write_mode | address_mode)

    def _send_byte(self, value: int) -> None:
        for _ in range(8):
            self._write_pin(self._clk, False)
            self._sleep()
            self._write_pin(self._dio, bool(value & 1))
            self._sleep()
            self._write_pin(self._clk, True)
            self._sleep()
            value >>= 1

    def _read_byte(self) -> int:
        GPIO = self._gpio
        value = 0
        for _ in range(8):
            value >>= 1
            # The TM1638 changes DIO on the falling edge, and the open-drain
            # line is unstable until the rising edge.  Sample after CLK goes
            # high, not immediately after it goes low.
            GPIO.output(self._clk, False)
            self._sleep()
            GPIO.output(self._clk, True)
            self._sleep()
            if GPIO.input(self._dio):
                value |= 0x80
        return value

    def _sleep(self) -> None:
        if self._delay:
            time.sleep(self._delay)

    def _stb_low(self) -> None:
        self._write_pin(self._stb, False)

    def _stb_high(self) -> None:
        self._write_pin(self._stb, True)

    def _write_pin(self, pin: int, value: bool) -> None:
        if self._gpio is None:
            return
        self._gpio.output(pin, self._gpio.HIGH if value else self._gpio.LOW)


# ---------------------------------------------------------------------------
# Command line helpers
# ---------------------------------------------------------------------------
def _parse_numbers(raw: Iterable[str]) -> list[int]:
    """Parse 1-based LED/switch numbers from the command line to 0-based."""

    numbers: list[int] = []
    for item in raw:
        try:
            number = int(item)
        except ValueError:
            raise ValueError(f"不是有效的序号: {item!r}") from None
        if not 1 <= number <= 8:
            raise ValueError(f"序号必须在 1..8 之间，收到 {number}")
        numbers.append(number - 1)
    return numbers


def run_demo(board: TM1638) -> None:
    print(
        f"引脚: STB={board.stb}, CLK={board.clk}, DIO={board.dio} "
        f"(mode={board.pin_mode})"
    )
    print("演示：依次点亮 8 个 LED")
    for index in range(8):
        board.set_led(index, True)
        time.sleep(0.15)
    time.sleep(0.5)
    board.clear_leds()

    print("演示：数码管显示 12345678 / HELLO / TM1638")
    for text in ("12345678", "HELLO", "TM1638"):
        board.show(text)
        time.sleep(0.8)
    board.clear_display()
    print("演示结束")


def run_keys(board: TM1638) -> None:
    raw = board.read_key_bytes()
    keys = board.pressed_keys()
    switches = board.pressed_switches()

    if not board.simulated:
        level = board.read_dio_level()
        print(f"DIO 空闲电平: {level} ({'高' if level else '低'})")
        if not level:
            print("警告：DIO 空闲为低，按键读取可能全部是 0。")
            print("      Jetson.GPIO 会忽略内部上拉，请在 DIO 与 3.3V 之间")
            print("      加一个 4.7k~10k 的上拉电阻。")

    print(f"原始 4 字节: {[f'0x{value:02X}' for value in raw]}")
    print(f"原始按键位 (0..31): {keys or '无'}")
    pressed = [index + 1 for index, value in enumerate(switches) if value]
    print(f"板载按键 (1..8): {pressed or '无'}")


def run_key_test(board: TM1638, timeout: float = 10.0) -> None:
    """Interactive end-to-end test for the button scan path."""

    if board.simulated:
        print("模拟模式：请用 --sim watch 测试按键逻辑。")
        return

    print("=== 按键链路测试 ===")
    print("请先松开所有按键。")

    start = time.monotonic()
    while any(board.pressed_switches()):
        if time.monotonic() - start > 3:
            print("检测到按键一直处于按下状态，请检查是否有按键卡住。")
            return
        time.sleep(0.02)

    print(f"请按住任意一个按键（{timeout:g} 秒内）...")
    index = board.wait_for_switch(timeout=timeout, poll_interval=0.01)
    if index is None:
        print("未检测到按键。")
        print("可能原因：")
        print("  1. 按键没有真正接好，或按键损坏")
        print("  2. DIO 没有上拉电阻（Jetson.GPIO 不支持内部上拉）")
        print("  3. 杜邦线接触不良")
        print("  4. 读取时序仍不稳定，可尝试 --delay-us 10")
        return

    print(f"检测到按键 {index + 1}：STB / CLK / DIO 和按键扫描链路正常。")


def run_raw_keys(board: TM1638, interval: float = 0.05) -> None:
    """Continuously print the raw key bytes when they change."""

    if board.simulated:
        print("模拟模式：请用 --sim watch 测试按键逻辑。")
        return

    print("持续读取原始按键字节，按 Ctrl+C 退出。")
    print("按住某个键时，观察哪一位从 0 变成 1。")
    last: list[int] | None = None
    try:
        while True:
            raw = board.read_key_bytes()
            if raw != last:
                formatted = " ".join(f"0x{value:02X}" for value in raw)
                print(f"原始 4 字节: [{formatted}]")
                last = raw
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n停止读取")


def run_watch(board: TM1638, timeout: float | None = None) -> None:
    if board.simulated:
        print("模拟模式：输入 1..8 模拟按下按键，输入 q 退出。")
        while True:
            try:
                text = input("按键> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if text.lower() in {"q", "quit", "exit"}:
                return
            try:
                index = int(text) - 1
                board.simulate_switch(index, True)
                pressed = [i + 1 for i, on in enumerate(board.pressed_switches()) if on]
                print(f"[sim] 按键 {index + 1} 按下，当前按键: {pressed}")
                board.simulate_switch(index, False)
            except (ValueError, RuntimeError) as exc:
                print(exc)
        return

    print("监听按键中，按 Ctrl+C 退出。")
    print("提示：按住不放只报告一次，需要松开后再按；每次按住至少 50ms。")
    try:
        while True:
            index = board.wait_for_switch(timeout=timeout)
            if index is None:
                print("等待超时，未检测到按键")
                return
            print(f"检测到按键 {index + 1}")
    except KeyboardInterrupt:
        print("\n停止监听")


def run_menu(board: TM1638) -> None:
    menu = """
========== TM1638 测试菜单 ==========
1. 点亮指定 LED
2. 关闭指定 LED
3. 全部 LED 点亮
4. 全部 LED 关闭
5. 数码管显示文本
6. 清空数码管
7. 读取按键
8. 监听按键
9. 运行演示
0. 退出
=====================================
"""
    while True:
        print(menu)
        try:
            choice = input("请选择> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        try:
            if choice == "1":
                board.led_on(*_parse_numbers(input("LED 序号(1-8，空格分隔)> ").split()))
            elif choice == "2":
                board.led_off(*_parse_numbers(input("LED 序号(1-8，空格分隔)> ").split()))
            elif choice == "3":
                board.all_leds(True)
            elif choice == "4":
                board.clear_leds()
            elif choice == "5":
                board.show(input("要显示的文本(最多 8 个字符)> "))
            elif choice == "6":
                board.clear_display()
            elif choice == "7":
                run_keys(board)
            elif choice == "8":
                run_watch(board)
            elif choice == "9":
                run_demo(board)
            elif choice == "0":
                return
            else:
                print("无效选项")
        except (ValueError, RuntimeError) as exc:
            print(f"错误: {exc}")


def run_selftest(board: TM1638) -> None:
    """Toggle the GPIO pins, then light every LED and digit."""

    if board.simulated:
        print("模拟模式：跳过真实引脚自检。")
        return

    board.test_pins()
    print("点亮全部 LED，并显示 88888888 ...")
    board.all_leds(True)
    board.show("88888888")
    time.sleep(2)
    board.clear_all()
    print("自检结束。")


def run_check(args: argparse.Namespace) -> int:
    """Report whether Jetson.GPIO and the configured pins are usable."""

    print("=== TM1638 / Jetson.GPIO 检查（GPIO 配置与 DIO 上拉）===")
    print(f"Python:   {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"引脚模式: {args.pin_mode.upper()}")
    print(f"引脚:     STB={args.stb}  CLK={args.clk}  DIO={args.dio}")

    gpio = _load_gpio()
    if gpio is None:
        print("\nJetson.GPIO: 不可用")
        if _GPIO_IMPORT_ERROR:
            print(f"原因: {_GPIO_IMPORT_ERROR}")
        print("\n在 Jetson 上安装：")
        print("  sudo apt-get install python3-pip")
        print("  sudo pip3 install Jetson.GPIO")
        print("  sudo groupadd -f -r gpio")
        print("  sudo usermod -a -G gpio $USER")
        print("  # 重新登录或重启后再试")
        return 1

    version = getattr(gpio, "__version__", "unknown")
    print(f"\nJetson.GPIO: 可用（版本 {version}）")

    try:
        if hasattr(gpio, "setwarnings"):
            gpio.setwarnings(False)
        mode = gpio.BOARD if args.pin_mode == "board" else gpio.BCM
        gpio.setmode(mode)
        for name, pin in (
            ("STB", args.stb),
            ("CLK", args.clk),
            ("DIO", args.dio),
        ):
            gpio.setup(pin, gpio.OUT)
            print(f"  {name}: pin {pin} -> 输出模式 OK")

        # DIO is bidirectional.  Read its idle level to detect a missing
        # pull-up, which is the usual reason key reads return all zeros.
        gpio.setup(args.dio, gpio.IN)
        time.sleep(0.02)
        dio_level = gpio.input(args.dio)
        print(f"  DIO 空闲电平: {dio_level} ({'高' if dio_level else '低'})")
        if not dio_level:
            print("  警告：DIO 空闲为低。Jetson.GPIO 会忽略内部上拉，")
            print("        请在 DIO 与 3.3V 之间加 4.7k~10k 上拉电阻。")

        gpio.cleanup([args.stb, args.clk, args.dio])
    except Exception as exc:  # pragma: no cover - depends on the host
        print(f"\nGPIO 初始化失败: {type(exc).__name__}: {exc}")
        print("提示：可能需要 sudo，或把当前用户加入 gpio 组。")
        return 1

    print("\nGPIO 初始化: 成功")
    print("说明：本检查只验证 GPIO 能否配置、DIO 是否有上拉，")
    print("      不能单独证明 STB/CLK/DIO 已经正确连到 TM1638。")
    print("      请再运行：python tm1638_standalone.py --test-keys")
    print_wiring()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TM1638 独立测试工具（LED / 数码管 / 按键）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--stb", type=int, default=17, help="STB 引脚，默认 GPIO17")
    parser.add_argument("--clk", type=int, default=27, help="CLK 引脚，默认 GPIO27")
    parser.add_argument("--dio", type=int, default=22, help="DIO 引脚，默认 GPIO22")
    parser.add_argument(
        "--brightness", type=int, default=3, choices=range(8), help="亮度 0-7，默认 3"
    )
    parser.add_argument(
        "--pin-mode",
        choices=["bcm", "board"],
        default="bcm",
        help="引脚编号方式：bcm（默认）或 board（物理引脚）",
    )
    parser.add_argument(
        "--physical",
        action="store_true",
        help="使用 40PIN 物理引脚号（等价于 --pin-mode board 且引脚为 11/13/15）",
    )
    parser.add_argument(
        "--delay-us",
        type=float,
        default=5.0,
        help="每个时钟边沿额外延时（微秒），默认 5；接线很长时可试 10",
    )
    parser.add_argument(
        "--sim", action="store_true", help="强制模拟模式（没有 Jetson.GPIO 时自动启用）"
    )
    parser.add_argument(
        "--require-hardware",
        action="store_true",
        help="没有 Jetson.GPIO 时直接报错，而不是自动进入模拟模式",
    )
    parser.add_argument(
        "--wiring", action="store_true", help="打印 TM1638 与 Jetson 40PIN 的接线表"
    )
    parser.add_argument(
        "--check", action="store_true", help="检查 Jetson.GPIO 和引脚是否可用"
    )
    parser.add_argument(
        "--selftest", action="store_true", help="翻转引脚并点亮全部 LED / 数码管"
    )
    parser.add_argument(
        "--test-keys", action="store_true", help="交互式测试按键扫描链路"
    )

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("demo", help="运行 LED / 数码管演示")
    sub.add_parser("menu", help="交互式菜单（默认）")
    sub.add_parser("clear", help="清空数码管和 LED")
    sub.add_parser("keys", help="读取一次按键状态")
    sub.add_parser("raw", help="持续输出原始按键字节")
    sub.add_parser("text", help="在数码管上显示文本").add_argument("value")
    sub.add_parser("watch", help="持续监听按键").add_argument(
        "--timeout", type=float, default=None, help="单次等待超时（秒）"
    )

    led = sub.add_parser("led", help="控制 LED")
    led.add_argument("action", choices=["on", "off", "all", "clear"])
    led.add_argument("numbers", nargs="*", help="LED 序号 1-8（on/off 时使用）")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.physical:
        args.pin_mode = "board"
        if args.stb == 17:
            args.stb = 11
        if args.clk == 27:
            args.clk = 13
        if args.dio == 22:
            args.dio = 15

    if args.wiring:
        print_wiring()
        return 0

    if args.check:
        return run_check(args)

    if not args.sim and args.require_hardware and _load_gpio() is None:
        print("错误：未检测到 Jetson.GPIO，且指定了 --require-hardware。")
        if _GPIO_IMPORT_ERROR:
            print(f"原因: {_GPIO_IMPORT_ERROR}")
        print("请先运行 python tm1638_standalone.py --check 查看详情。")
        return 1

    board = TM1638(
        stb=args.stb,
        clk=args.clk,
        dio=args.dio,
        brightness=args.brightness,
        simulate=args.sim,
        pin_mode=args.pin_mode,
        delay_us=args.delay_us,
    )

    try:
        command = args.command or "menu"

        if args.test_keys:
            run_key_test(board)
        elif args.selftest:
            run_selftest(board)
        elif command == "demo":
            run_demo(board)
        elif command == "menu":
            run_menu(board)
        elif command == "clear":
            board.clear_all()
        elif command == "keys":
            run_keys(board)
        elif command == "raw":
            run_raw_keys(board)
        elif command == "text":
            board.show(args.value)
        elif command == "watch":
            run_watch(board, timeout=args.timeout)
        elif command == "led":
            try:
                numbers = _parse_numbers(args.numbers)
            except ValueError as exc:
                raise SystemExit(str(exc)) from None
            if args.action == "on":
                if not numbers:
                    raise SystemExit("led on 需要至少一个 LED 序号，例如: led on 1 3")
                board.led_on(*numbers)
            elif args.action == "off":
                if not numbers:
                    raise SystemExit("led off 需要至少一个 LED 序号，例如: led off 2")
                board.led_off(*numbers)
            elif args.action == "all":
                board.all_leds(True)
            elif args.action == "clear":
                board.clear_leds()
        else:
            raise SystemExit(f"未知命令: {command}")
    finally:
        board.close()

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        sys.exit(0)
