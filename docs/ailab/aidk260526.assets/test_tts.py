# test_valid_voices.py
import asyncio
import subprocess
import tempfile
import os
import edge_tts

TEST_TEXT = "你好，欢迎使用人脸识别门禁系统。"
# 根据 edge-tts --list-voices | grep zh-CN 的输出手动更新
VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-liaoning-XiaobeiNeural",   # 辽宁方言
    "zh-CN-shaanxi-XiaoniNeural",    # 陕西方言
]

async def speak_and_play(voice: str, text: str):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_file = f.name
    try:
        await edge_tts.Communicate(text, voice).save(tmp_file)
        # 尝试使用 ffplay 播放（若已安装），否则用 mpg123
        try:
            subprocess.run(['ffplay', '-nodisp', '-autoexit', tmp_file], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            subprocess.run(['mpg123', '-q', tmp_file], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"  播放失败: {e}")
        return False
    finally:
        if os.path.exists(tmp_file):
            os.unlink(tmp_file)

async def main():
    print("测试可用 Edge-TTS 中文语音，共 {} 个。".format(len(VOICES)))
    for idx, voice in enumerate(VOICES, 1):
        print(f"\n[{idx}/{len(VOICES)}] 测试语音: {voice}")
        success = await speak_and_play(voice, TEST_TEXT)
        if success:
            print("  播放完毕。")
        else:
            print("  播放失败。")
        input("  按 Enter 继续下一个...")

if __name__ == "__main__":
    asyncio.run(main())
