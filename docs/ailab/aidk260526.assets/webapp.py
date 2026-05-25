# face_door.py (支持中文显示)
import os
import cv2
import base64
import signal
import sys
import numpy as np
from flask import Flask, render_template, Response, jsonify
from PIL import Image, ImageDraw, ImageFont

from utils.predictor import Predictor

# ---------- 配置 ----------
CAMERA_INDEX = 2                     # USB摄像头设备号（/dev/video2）
MTCNN_MODEL_PATH = "save_model/mtcnn"
MOBILEFACENET_MODEL_PATH = "save_model/mobilefacenet.pth"
FACE_DB_PATH = "face_db"
THRESHOLD = 0.6                      # 识别阈值
# -------------------------

app = Flask(__name__)

# 全局变量
cap = None
predictor = None
box_coords = None
recognition_result = "等待识别"

# 加载中文字体
font_path = os.path.join(os.path.dirname(__file__), 'utils', 'simfang.ttf')
try:
    font = ImageFont.truetype(font_path, 24)
except:
    font = ImageFont.load_default()
    print("⚠️ 中文字体加载失败，使用默认字体（可能无法显示中文）")

def cleanup():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()
        print("✅ 摄像头已释放")

def signal_handler(sig, frame):
    print("\n收到退出信号，正在清理...")
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 初始化预测器
predictor = Predictor(
    mtcnn_model_path=MTCNN_MODEL_PATH,
    mobilefacenet_model_path=MOBILEFACENET_MODEL_PATH,
    face_db_path=FACE_DB_PATH,
    threshold=THRESHOLD
)
print("✅ 人脸识别器加载完成")

# 打开摄像头
cap = cv2.VideoCapture(CAMERA_INDEX)
if not cap.isOpened():
    raise RuntimeError(f"无法打开摄像头 /dev/video{CAMERA_INDEX}")
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
print(f"✅ 摄像头 /dev/video{CAMERA_INDEX} 已打开")

# 获取一帧计算黄框位置（与短边等大的正方形，居中）
ret, sample_frame = cap.read()
if ret:
    h, w = sample_frame.shape[:2]
    short_side = min(w, h)
    box_size = short_side
    center_x, center_y = w // 2, h // 2
    x1 = center_x - box_size // 2
    y1 = center_y - box_size // 2
    x2 = x1 + box_size
    y2 = y1 + box_size
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)
    box_coords = (x1, y1, x2, y2)
    print(f"✅ 黄框坐标: {box_coords}, 大小: {box_size}x{box_size}")
else:
    raise RuntimeError("无法获取摄像头画面以计算黄框位置")

def generate_frames():
    """视频流：绘制黄框并使用 PIL 叠加中文识别结果"""
    global recognition_result
    while True:
        success, frame = cap.read()
        if not success:
            break

        # 绘制黄色正方形框
        x1, y1, x2, y2 = box_coords
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
        cv2.putText(frame, "Place face here", (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        # 使用 PIL 绘制中文文本
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(pil_img)
        # 黑色背景条
        draw.rectangle([(0, 0), (frame.shape[1], 40)], fill=(0, 0, 0))
        # 白色中文
        draw.text((10, 10), f"识别结果: {recognition_result}", font=font, fill=(255, 255, 255))
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('door.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    global recognition_result
    success, frame = cap.read()
    if not success:
        return jsonify({'error': '读取摄像头失败'}), 500

    x1, y1, x2, y2 = box_coords
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return jsonify({'error': '黄框区域无效'}), 400

    _, buffer = cv2.imencode('.jpg', roi)
    face_b64 = base64.b64encode(buffer).decode('utf-8')

    try:
        results = predictor.recognition(roi)
        if results is None or len(results) == 0:
            recognition_result = "没有人脸"
            result_text = "没有人脸"
        else:
            name = results[0]['name']
            prob = results[0]['prob']
            if name == "unknow" or prob <= THRESHOLD:
                recognition_result = "不认识"
                result_text = "不认识"
            else:
                recognition_result = f"{name}，请进"
                result_text = f"{name}，请进"
        return jsonify({
            'success': True,
            'face_image': face_b64,
            'result': result_text
        })
    except Exception as e:
        print("识别异常:", e)
        recognition_result = "识别错误"
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>刷脸开门系统</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 20px; background: #2c3e50; color: #ecf0f1; }
        .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-top: 20px; }
        .video-panel { background: #34495e; border-radius: 12px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .result-panel { background: #34495e; border-radius: 12px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); min-width: 300px; display: flex; flex-direction: column; align-items: center; }
        img { border: 2px solid #f1c40f; border-radius: 8px; max-width: 100%; }
        button { background-color: #e67e22; color: white; border: none; padding: 12px 28px;
                 font-size: 18px; border-radius: 40px; cursor: pointer; margin-top: 15px; transition: 0.2s; font-weight: bold; }
        button:hover { background-color: #f39c12; transform: scale(1.02); }
        button:disabled { background-color: #7f8c8d; cursor: not-allowed; transform: none; }
        .result-text { font-size: 22px; font-weight: bold; margin: 15px 0; padding: 12px; background: #2c3e50; border-radius: 8px; border-left: 5px solid #f1c40f; }
        .face-img { width: 220px; height: 220px; object-fit: cover; border: 3px solid #f1c40f; border-radius: 12px; margin-top: 10px; }
        h1, h2 { margin: 10px 0; }
        .info { margin-top: 20px; font-size: 14px; color: #bdc3c7; }
    </style>
</head>
<body>
    <h1>🚪 刷脸开门系统</h1>
    <div class="container">
        <div class="video-panel">
            <h2>📹 实时画面（请将人脸放入黄框内）</h2>
            <img src="/video_feed" width="640" height="480" alt="摄像头画面">
            <br>
            <button id="captureBtn">📷 拍摄并识别</button>
        </div>
        <div class="result-panel">
            <h2>📸 本次拍摄内容</h2>
            <div id="capturedImgArea">
                <p style="color:#bdc3c7;">尚未拍摄</p>
            </div>
            <div id="recogResultArea">
                <p style="color:#bdc3c7;">等待识别</p>
            </div>
        </div>
    </div>
    <div class="info">
        💡 识别结果会实时显示在左侧视频画面顶部，同时右侧展示裁剪图片和本次识别结果。
    </div>

    <script>
        const captureBtn = document.getElementById('captureBtn');
        const capturedImgArea = document.getElementById('capturedImgArea');
        const recogResultArea = document.getElementById('recogResultArea');

        captureBtn.addEventListener('click', async () => {
            captureBtn.disabled = true;
            captureBtn.innerText = '⏳ 识别中...';
            capturedImgArea.innerHTML = '<p>处理中...</p>';
            recogResultArea.innerHTML = '<p>识别中...</p>';
            try {
                const resp = await fetch('/capture', { method: 'POST' });
                const data = await resp.json();
                if (data.success) {
                    capturedImgArea.innerHTML = `
                        <strong>拍摄到的图片：</strong><br>
                        <img class="face-img" src="data:image/jpeg;base64,${data.face_image}" alt="拍摄区域">
                    `;
                    recogResultArea.innerHTML = `
                        <div class="result-text">识别结果：${data.result}</div>
                    `;
                } else {
                    capturedImgArea.innerHTML = `<p style="color:#e74c3c;">拍摄失败：${data.error}</p>`;
                    recogResultArea.innerHTML = '';
                }
            } catch (err) {
                capturedImgArea.innerHTML = `<p style="color:#e74c3c;">请求失败：${err.message}</p>`;
                recogResultArea.innerHTML = '';
            } finally {
                captureBtn.disabled = false;
                captureBtn.innerText = '📷 拍摄并识别';
            }
        });
    </script>
</body>
</html>'''
    with open('templates/door.html', 'w', encoding='utf-8') as f:
        f.write(html)

    try:
        print("🚪 刷脸开门系统启动")
        print("🌐 请访问 http://<开发板IP>:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        cleanup()
