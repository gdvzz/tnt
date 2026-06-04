#!/usr/bin/env python3
# webapp.py - 手写数字识别系统（新极简主义风格 + 双语音播报）
# 依赖: flask opencv-python torch torchvision edge-tts numpy pillow

import os
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import numpy as np
import subprocess
import tempfile
import base64
import threading
import asyncio
import edge_tts
from flask import Flask, Response, render_template_string, jsonify, request


# ---------------------------- 1. 神经网络模型（与 model.py 一致） ----------------------------
class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.fc1 = nn.Linear(in_features=64 * 5 * 5, out_features=128)
        self.fc2 = nn.Linear(in_features=128, out_features=10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, kernel_size=2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, kernel_size=2)
        x = x.view(-1, 64 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


# ---------------------------- 2. 摄像头处理（带黄色方框） ----------------------------
class Camera:
    def __init__(self, camera_id=0):
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError("无法打开摄像头")
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("无法读取摄像头画面")
        self.height, self.width = frame.shape[:2]
        side = int(min(self.width, self.height) * 0.8)
        self.roi_x = (self.width - side) // 2
        self.roi_y = (self.height - side) // 2
        self.roi_size = side
        self.lock = threading.Lock()
        self.latest_frame = frame

    def get_frame_with_bbox(self):
        with self.lock:
            ret, frame = self.cap.read()
            if not ret:
                frame = self.latest_frame
            else:
                self.latest_frame = frame
        cv2.rectangle(
            frame,
            (self.roi_x, self.roi_y),
            (self.roi_x + self.roi_size, self.roi_y + self.roi_size),
            (0, 255, 255),
            3,
        )
        ret, jpeg = cv2.imencode(".jpg", frame)
        return jpeg.tobytes()

    def capture_roi(self):
        with self.lock:
            frame = self.latest_frame.copy()
        roi = frame[
            self.roi_y : self.roi_y + self.roi_size,
            self.roi_x : self.roi_x + self.roi_size,
        ]
        return roi

    def release(self):
        self.cap.release()


# ---------------------------- 3. 数字识别器（预处理 + 推理 + 置信度） ----------------------------
class DigitRecognizer:
    def __init__(self, weights_path="mnist.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = NeuralNetwork().to(self.device)
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"模型文件 {weights_path} 不存在")
        self.model.load_state_dict(torch.load(weights_path, map_location=self.device))
        self.model.eval()

    def preprocess(self, roi_bgr):
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        gray_inv = 255 - gray
        _, binary = cv2.threshold(gray_inv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if contours:
            x_min, y_min = 9999, 9999
            x_max, y_max = 0, 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x + w)
                y_max = max(y_max, y + h)
            digit_roi = binary[y_min:y_max, x_min:x_max]
        else:
            digit_roi = binary
        if digit_roi.size == 0:
            digit_roi = np.zeros((20, 20), dtype=np.uint8)
        else:
            digit_roi = cv2.resize(digit_roi, (20, 20), interpolation=cv2.INTER_AREA)
        final_img = np.zeros((28, 28), dtype=np.uint8)
        x_offset = (28 - 20) // 2
        y_offset = (28 - 20) // 2
        final_img[y_offset : y_offset + 20, x_offset : x_offset + 20] = digit_roi
        transform = torchvision.transforms.Compose(
            [
                torchvision.transforms.ToTensor(),
                torchvision.transforms.Normalize((0.1307,), (0.3081,)),
            ]
        )
        tensor = transform(final_img).unsqueeze(0).to(self.device)
        return tensor, final_img

    def predict(self, roi_bgr):
        tensor, processed_img = self.preprocess(roi_bgr)
        with torch.no_grad():
            output = self.model(tensor)
            probs = F.softmax(output, dim=1)
            pred = output.argmax(dim=1).item()
        prob_list = probs.squeeze().cpu().numpy().tolist()
        return pred, prob_list, processed_img


# ---------------------------- 4. 语音播报（开发板本地播放 + 返回音频） ----------------------------
"""
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
"""


async def speak_and_play_local(text: str, voice: str = "zh-CN-shaanxi-XiaoniNeural"):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_file = f.name
    try:
        await edge_tts.Communicate(text, voice).save(tmp_file)
        try:
            subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", tmp_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            subprocess.Popen(
                ["mpg123", "-q", tmp_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        return tmp_file
    except Exception as e:
        print(f"语音播报失败: {e}")
        if os.path.exists(tmp_file):
            os.unlink(tmp_file)
        return None


def cleanup_audio_file(filepath):
    if filepath and os.path.exists(filepath):
        os.unlink(filepath)


# ---------------------------- 5. Flask Web 服务（含新极简主义前端） ----------------------------
app = Flask(__name__)
camera = None
recognizer = None


def get_camera():
    global camera
    if camera is None:
        camera = Camera(camera_id=0)
    return camera


def get_recognizer():
    global recognizer
    if recognizer is None:
        recognizer = DigitRecognizer("mnist.pth")
    return recognizer


# 内嵌 HTML/CSS/JS (单色调柔和粉彩 + 卡片式 + 新极简主义)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>手写数字识别 | 新极简主义</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #f5f3f0;  /* 柔和米白基调 */
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, sans-serif;
            padding: 2rem 1.5rem;
            color: #3b3a36;
        }

        /* 主容器 */
        .main-container {
            max-width: 1400px;
            margin: 0 auto;
        }

        /* 页眉 */
        .header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        .header h1 {
            font-size: 2.2rem;
            font-weight: 500;
            letter-spacing: -0.01em;
            background: linear-gradient(135deg, #7c6e65, #b5a79b);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
        }
        .header p {
            color: #8e887e;
            font-size: 0.95rem;
        }

        /* 卡片网格 */
        .cards-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 1.8rem;
            justify-content: center;
        }

        /* 公用卡片样式: 柔和阴影+圆角+半透背景 */
        .card {
            background: rgba(250, 248, 245, 0.85);
            backdrop-filter: blur(2px);
            border-radius: 2rem;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.03), 0 2px 4px rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(200, 190, 180, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            overflow: hidden;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 20px 32px rgba(0, 0, 0, 0.05);
        }

        /* 视频卡片 */
        .video-card {
            flex: 2;
            min-width: 300px;
        }
        .video-wrapper {
            position: relative;
            background: #e9e4dd;
            padding: 0.8rem;
            border-radius: 1.5rem;
        }
        .video-feed {
            width: 100%;
            border-radius: 1rem;
            display: block;
            background: #dad3ca;
        }
        .video-label {
            position: absolute;
            bottom: 1.2rem;
            left: 1.5rem;
            background: rgba(60, 55, 50, 0.6);
            backdrop-filter: blur(8px);
            padding: 0.2rem 0.8rem;
            border-radius: 2rem;
            font-size: 0.7rem;
            color: #f0ece7;
            letter-spacing: 0.5px;
        }

        /* 按钮卡片 */
        .controls-card {
            flex: 0.8;
            min-width: 200px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            padding: 1.8rem 1rem;
        }
        .btn {
            width: 80%;
            padding: 0.9rem 0;
            border: none;
            border-radius: 3rem;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            background: #e3dbd1;
            color: #4e4740;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        .btn-primary {
            background: #c9bcae;
            color: #2f2c28;
        }
        .btn-primary:hover {
            background: #b9aa9a;
            transform: scale(0.97);
        }
        .btn-secondary {
            background: #e9e0d8;
        }
        .btn-secondary:hover {
            background: #ddd2c8;
            transform: scale(0.97);
        }

        /* 结果卡片组：三栏布局 */
        .results-row {
            display: flex;
            flex-wrap: wrap;
            gap: 1.8rem;
            margin-top: 2rem;
        }
        .result-card {
            flex: 1;
            min-width: 220px;
            padding: 1.2rem 1rem;
            text-align: center;
        }
        .result-card h3 {
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 1rem;
            color: #6f675e;
            letter-spacing: -0.2px;
        }
        .image-preview {
            background: #f1ede8;
            border-radius: 1.2rem;
            padding: 0.6rem;
            margin-bottom: 0.8rem;
        }
        .image-preview img {
            max-width: 100%;
            max-height: 160px;
            border-radius: 0.8rem;
            background: #e4ded7;
        }
        .digit-result {
            font-size: 2.2rem;
            font-weight: 600;
            color: #8b7e6e;
            margin-top: 0.5rem;
        }

        /* 置信度表格 新极简条 */
        .confidence-table {
            width: 100%;
            margin-top: 0.8rem;
        }
        .conf-row {
            display: flex;
            align-items: center;
            margin-bottom: 0.8rem;
            gap: 0.6rem;
        }
        .conf-digit {
            font-weight: 500;
            width: 28px;
            font-size: 0.9rem;
            color: #857a6e;
        }
        .conf-bar-bg {
            flex: 1;
            background: #e3dbd1;
            border-radius: 20px;
            height: 8px;
            overflow: hidden;
        }
        .conf-bar {
            background: #b8a897;
            width: 0%;
            height: 100%;
            border-radius: 20px;
            transition: width 0.3s ease;
        }
        .conf-percent {
            font-size: 0.7rem;
            width: 38px;
            text-align: right;
            color: #8a7f72;
        }

        /* 底部 */
        .footer {
            margin-top: 2.5rem;
            text-align: center;
            font-size: 0.7rem;
            color: #bbb0a4;
        }

        /* 音频播放器隐藏式 */
        audio {
            display: none;
        }

        @media (max-width: 780px) {
            body { padding: 1rem; }
            .cards-grid { flex-direction: column; }
            .controls-card { flex-direction: row; flex-wrap: wrap; }
            .btn { width: auto; padding: 0.6rem 1.2rem; }
        }
    </style>
</head>
<body>
<div class="main-container">
    <div class="header">
        <h1>✧ 手写数字识别 ✧</h1>
        <p>对准黄框 · 瞬时识别 · 置信可依</p>
    </div>

    <div class="cards-grid">
        <!-- 视频卡片 -->
        <div class="card video-card">
            <div class="video-wrapper">
                <img id="videoFeed" class="video-feed" src="/video_feed" alt="实时视频流">
                <div class="video-label">📷 拍摄区域</div>
            </div>
        </div>
        <!-- 按钮卡片 -->
        <div class="card controls-card">
            <button class="btn btn-primary" id="captureBtn">📸 拍照</button>
            <button class="btn btn-secondary" id="recognizeBtn">🔍 识别</button>
        </div>
    </div>

    <div class="results-row">
        <!-- 拍摄的照片卡片 -->
        <div class="card result-card">
            <h3>📷 拍摄的照片</h3>
            <div class="image-preview">
                <img id="capturedImg" src="" alt="暂无照片">
            </div>
        </div>
        <!-- 预处理 28x28 卡片 -->
        <div class="card result-card">
            <h3>✨ 预处理后 28x28</h3>
            <div class="image-preview">
                <img id="processedImg" src="" alt="等待识别">
            </div>
            <div id="resultText" class="digit-result"></div>
        </div>
        <!-- 置信度卡片 -->
        <div class="card result-card">
            <h3>📊 数字置信度</h3>
            <div id="confidenceTable" class="confidence-table"></div>
        </div>
    </div>
    <div class="footer">
        <span>新极简主义 · 柔和精准</span>
    </div>
    <audio id="audioPlayer" controls autoplay></audio>
</div>

<script>
    const captureBtn = document.getElementById('captureBtn');
    const recognizeBtn = document.getElementById('recognizeBtn');
    const capturedImg = document.getElementById('capturedImg');
    const processedImg = document.getElementById('processedImg');
    const resultText = document.getElementById('resultText');
    const confidenceDiv = document.getElementById('confidenceTable');
    const audioPlayer = document.getElementById('audioPlayer');

    let latestPhotoBase64 = null;

    function renderConfidence(probs) {
        let html = '';
        for (let i = 0; i < probs.length; i++) {
            let percent = (probs[i] * 100).toFixed(1);
            html += `
                <div class="conf-row">
                    <span class="conf-digit">${i}</span>
                    <div class="conf-bar-bg">
                        <div class="conf-bar" style="width: ${percent}%;"></div>
                    </div>
                    <span class="conf-percent">${percent}%</span>
                </div>
            `;
        }
        confidenceDiv.innerHTML = html;
    }

    captureBtn.onclick = async () => {
        const response = await fetch('/capture', { method: 'POST' });
        const data = await response.json();
        if (data.image) {
            latestPhotoBase64 = 'data:image/jpeg;base64,' + data.image;
            capturedImg.src = latestPhotoBase64;
            processedImg.src = '';
            resultText.innerText = '';
            confidenceDiv.innerHTML = '';
        } else {
            alert('拍照失败，请检查摄像头');
        }
    };

    recognizeBtn.onclick = async () => {
        if (!latestPhotoBase64) {
            alert('请先拍照');
            return;
        }
        const response = await fetch('/recognize', { method: 'POST' });
        const data = await response.json();
        if (data.error) {
            alert(data.error);
            return;
        }
        processedImg.src = 'data:image/png;base64,' + data.processed_image;
        resultText.innerText = `识别结果: ${data.digit}`;
        if (data.probabilities) {
            renderConfidence(data.probabilities);
        }
        if (data.audio_base64) {
            audioPlayer.src = 'data:audio/mp3;base64,' + data.audio_base64;
            audioPlayer.play().catch(e => console.log("自动播放限制"));
        } else {
            // 降级 Web Speech
            const msg = new SpeechSynthesisUtterance(`识别到的数字是${data.digit}`);
            window.speechSynthesis.speak(msg);
        }
    };
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/video_feed")
def video_feed():
    def generate():
        cam = get_camera()
        while True:
            frame = cam.get_frame_with_bbox()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/capture", methods=["POST"])
def capture():
    cam = get_camera()
    roi_img = cam.capture_roi()
    _, buffer = cv2.imencode(".jpg", roi_img)
    img_base64 = base64.b64encode(buffer).decode("utf-8")
    app.config["LATEST_ROI"] = roi_img
    return jsonify({"image": img_base64})


@app.route("/recognize", methods=["POST"])
def recognize():
    roi_img = app.config.get("LATEST_ROI")
    if roi_img is None:
        return jsonify({"error": "请先拍照"}), 400
    rec = get_recognizer()
    pred, prob_list, processed_img = rec.predict(roi_img)

    _, buffer = cv2.imencode(".png", processed_img)
    processed_base64 = base64.b64encode(buffer).decode("utf-8")

    text = f"识别到的数字是{pred}"
    tts_mp3_data = None
    try:
        audio_file = asyncio.run(speak_and_play_local(text))
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, "rb") as f:
                tts_mp3_data = base64.b64encode(f.read()).decode("utf-8")
            threading.Timer(5.0, lambda: cleanup_audio_file(audio_file)).start()
    except Exception as e:
        print(f"语音播报异常: {e}")

    return jsonify(
        {
            "digit": pred,
            "probabilities": prob_list,
            "processed_image": processed_base64,
            "audio_base64": tts_mp3_data,
        }
    )


if __name__ == "__main__":
    if not os.path.exists("mnist.pth"):
        print("错误：未找到 mnist.pth，请先训练模型。")
        exit(1)
    # 检查播放器
    try:
        subprocess.run(["ffplay", "-version"], capture_output=True, check=True)
        print("✅ 语音播放器 ffplay 已就绪")
    except:
        try:
            subprocess.run(["mpg123", "-V"], capture_output=True, check=True)
            print("✅ 语音播放器 mpg123 已就绪")
        except:
            print("⚠️ 未找到播放器，开发板可能无声。安装: sudo apt install ffmpeg")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)


# 1、USB摄像头，接在开发板上
# 2、在连接开发板的个人电脑上，通过网页方式访问开发板
# 3、在网页上，可以使用接在开发板上的USB摄像头拍照，对手写的数字拍照
# 4、然后让开发板上的程序做识别，并反馈识别结果到个人电脑的浏览器上
# 5、浏览器有个窗口，可以看到摄像头的画面。
# 6、拍摄窗口中，加个正方形的黄框，尽可能大。仅拍摄黄框内的画面。
# 7、拍照和识别，拆成2个按钮。拍照后，显示被拍到的照片；识别，对照片识别
# 8、处理为 28*28 的图片，送给推理程序识别的，也要显示在Web页面上
# 9、如果拍摄到3，识别到3， 0-9共10个数字的置性度，也要显示的web页面上
# 10、使用接在开发板上的喇叭加个语音播报，比如识别到的数字是3。web界面上播放也保留。
# 11、输出一个样例文件，不要分多个文件

# 12、web界面要有高级感，参照如下原则：
# - web界面的颜色：monochromatic muted  pastel
# - web界面的layout：card based design with layered elements
# - web界面的风格：Neo-minumalism
# - web界面的设计哲学：approachable sophistication

# 参考程序如下：
# 1、语音播报怎么写，请参考：语音try_tts.py
# 2、模型训练程序：train.py
# 3、模型定义：model.py
