# face_door_edge.py - 刷脸开门系统（Edge-TTS 自然语音，过滤 /status 日志）
import os
import cv2
import base64
import signal
import sys
import asyncio
import threading
import subprocess
import tempfile
import numpy as np
import logging
from flask import Flask, render_template, Response, jsonify
from utils.predictor import Predictor

# ---------- 配置 ----------
CAMERA_INDEX = 2                     # USB摄像头设备号（根据 `ls /dev/video*` 修改）
MTCNN_MODEL_PATH = "save_model/mtcnn"
MOBILEFACENET_MODEL_PATH = "save_model/mobilefacenet.pth"
FACE_DB_PATH = "face_db"
THRESHOLD = 0.6
EDGE_TTS_VOICE = "zh-CN-YunxiNeural"   # 云希男声，自然适合门禁
# -------------------------

app = Flask(__name__)

# 全局变量
cap = None
predictor = None
box_coords = None
recognition_result = "等待拍照"
latest_face_b64 = None
latest_result_text = ""

# ---------- Edge-TTS 语音播报 ----------
def speak_edge_tts(text: str, voice: str = EDGE_TTS_VOICE):
    """在独立线程中运行 Edge-TTS 并播放"""
    def _speak():
        tmp_file = None
        try:
            # 创建临时 MP3 文件
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp_file = f.name

            # 合成语音
            async def _tts():
                await edge_tts.Communicate(text, voice).save(tmp_file)

            asyncio.run(_tts())

            # 播放
            subprocess.run(['mpg123', '-q', tmp_file], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Edge-TTS 播报失败: {e}")
        finally:
            if tmp_file and os.path.exists(tmp_file):
                os.unlink(tmp_file)

    threading.Thread(target=_speak, daemon=True).start()

# ---------- 摄像头与黄框 ----------
def init_camera():
    global cap, box_coords
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开摄像头 {CAMERA_INDEX}")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # 计算正方形黄框（边长 = 短边，居中）
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("无法读取摄像头画面")
    h, w = frame.shape[:2]
    side = min(h, w)
    x1 = (w - side) // 2
    y1 = (h - side) // 2
    x2 = x1 + side
    y2 = y1 + side
    box_coords = (x1, y1, x2, y2)
    print(f"✅ 黄框坐标: {box_coords}, 尺寸: {side}x{side}")
    return box_coords

# ---------- 中文字体绘制 ----------
font_path = os.path.join(os.path.dirname(__file__), 'utils', 'simfang.ttf')
if not os.path.exists(font_path):
    font_path = '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'

def draw_chinese_text(img, text, pos, font_size=24, color=(255,255,255), bg_color=(0,0,0)):
    from PIL import Image, ImageDraw, ImageFont
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    if os.path.exists(font_path):
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0,0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.rectangle([pos[0], pos[1], pos[0]+text_w, pos[1]+text_h], fill=bg_color)
    draw.text((pos[0], pos[1]), text, fill=color, font=font)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# ---------- 视频流生成器 ----------
def generate_frames():
    global recognition_result
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        x1, y1, x2, y2 = box_coords
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
        cv2.putText(frame, "Place face here", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        # 在顶部叠加识别结果
        frame = draw_chinese_text(frame, f"识别结果: {recognition_result}", (10, 10), 24)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

# ---------- 拍照识别 ----------
def capture_and_recognize():
    global recognition_result, latest_face_b64, latest_result_text
    ret, frame = cap.read()
    if not ret:
        return None, "读取摄像头失败"
    x1, y1, x2, y2 = box_coords
    roi = frame[y1:y2, x1:x2]
    if roi.size == 0:
        return None, "黄框区域无效"

    # 编码图片
    _, buffer = cv2.imencode('.jpg', roi)
    face_b64 = base64.b64encode(buffer).decode('utf-8')
    latest_face_b64 = face_b64

    # 识别
    try:
        results = predictor.recognition(roi)
        if results is None or len(results) == 0:
            result_text = "没有人脸"
            recognition_result = "没有人脸"
            speak_text = "未识别到人脸"
            latest_result_text = "未识别到人脸"
        else:
            name = results[0]['name']
            prob = results[0]['prob']
            if name == "unknow" or prob <= THRESHOLD:
                result_text = "不认识"
                recognition_result = "不认识"
                speak_text = "不认识您"
                latest_result_text = "不认识您"
            else:
                result_text = f"{name}，请进"
                recognition_result = f"{name}，请进"
                speak_text = f"{name}，请进"
                latest_result_text = speak_text
        # 异步语音播报
        speak_edge_tts(speak_text)
        return face_b64, result_text
    except Exception as e:
        print(f"识别异常: {e}")
        return None, str(e)

# ---------- Flask 路由 ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture_route():
    face_b64, result = capture_and_recognize()
    if face_b64 is None:
        return jsonify({'error': result}), 500
    return jsonify({'success': True, 'face_image': face_b64, 'result': result})

@app.route('/status')
def status():
    """前端轮询获取最新结果（用于自动更新右侧面板）"""
    return jsonify({'face_image': latest_face_b64, 'result': latest_result_text})

# ---------- 主函数 ----------
def main():
    global predictor, cap, box_coords
    # 加载人脸识别模型
    predictor = Predictor(
        mtcnn_model_path=MTCNN_MODEL_PATH,
        mobilefacenet_model_path=MOBILEFACENET_MODEL_PATH,
        face_db_path=FACE_DB_PATH,
        threshold=THRESHOLD
    )
    print("✅ 人脸识别器加载完成")

    # 初始化摄像头和黄框
    box_coords = init_camera()

    # 创建 HTML 模板目录
    os.makedirs('templates', exist_ok=True)
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE)

    # 设置 Flask 日志过滤器，屏蔽 /status 请求的日志
    log = logging.getLogger('werkzeug')
    log.addFilter(lambda record: '/status' not in record.getMessage())

    # 启动 Flask
    print("🚪 刷脸开门系统启动")
    print("🌐 访问 http://<开发板IP>:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# ---------- HTML 模板 ----------
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>刷脸开门 - 自然语音</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 20px; background: #2c3e50; color: #ecf0f1; }
        .container { display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-top: 20px; }
        .video-panel { background: #34495e; border-radius: 12px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        .result-panel { background: #34495e; border-radius: 12px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); min-width: 300px; display: flex; flex-direction: column; align-items: center; }
        img { border: 2px solid #f1c40f; border-radius: 8px; max-width: 100%; }
        .face-img { width: 220px; height: 220px; object-fit: cover; border: 3px solid #f1c40f; border-radius: 12px; margin-top: 10px; }
        h1, h2 { margin: 10px 0; }
        button { background: #e67e22; color: white; border: none; padding: 12px 28px; font-size: 18px; border-radius: 40px; cursor: pointer; margin-top: 15px; transition: 0.2s; }
        button:hover { background: #f39c12; transform: scale(1.02); }
        button:disabled { background: #95a5a6; cursor: not-allowed; }
        .info { margin-top: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <h1>🚪 刷脸开门系统（自然语音）</h1>
    <div class="container">
        <div class="video-panel">
            <h2>📹 实时画面（请将人脸放入黄框内）</h2>
            <img src="/video_feed" width="640" height="480" alt="摄像头画面">
            <div class="info">🎤 点击下方按钮拍照，系统会使用自然语音播报结果</div>
            <button id="captureBtn">📷 拍照识别</button>
        </div>
        <div class="result-panel">
            <h2>📸 拍摄结果</h2>
            <div id="capturedImgArea"><p>尚未拍照</p></div>
            <div id="recogResultArea"><p>等待识别</p></div>
        </div>
    </div>
    <script>
        const captureBtn = document.getElementById('captureBtn');
        const capturedImgArea = document.getElementById('capturedImgArea');
        const recogResultArea = document.getElementById('recogResultArea');
        captureBtn.addEventListener('click', async () => {
            captureBtn.disabled = true;
            captureBtn.innerText = '识别中...';
            capturedImgArea.innerHTML = '<p>处理中...</p>';
            recogResultArea.innerHTML = '<p>识别中...</p>';
            try {
                const resp = await fetch('/capture', { method: 'POST' });
                const data = await resp.json();
                if (data.success) {
                    capturedImgArea.innerHTML = `<strong>拍摄到的图片：</strong><br><img class="face-img" src="data:image/jpeg;base64,${data.face_image}" alt="拍摄区域">`;
                    recogResultArea.innerHTML = `<div style="font-size:22px; font-weight:bold; padding:12px; background:#2c3e50; border-left:5px solid #f1c40f;">识别结果：${data.result}</div>`;
                } else {
                    capturedImgArea.innerHTML = `<p style="color:#e74c3c;">错误：${data.error}</p>`;
                    recogResultArea.innerHTML = '';
                }
            } catch (err) {
                capturedImgArea.innerHTML = `<p style="color:#e74c3c;">请求失败：${err.message}</p>`;
                recogResultArea.innerHTML = '';
            } finally {
                captureBtn.disabled = false;
                captureBtn.innerText = '📷 拍照识别';
            }
        });
        // 可选：轮询状态（保留以支持未来可能的语音唤醒自动更新，但不会输出日志）
        function fetchStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.face_image) {
                        // 自动更新右侧显示（可选）
                    }
                })
                .catch(err => console.error(err));
        }
        setInterval(fetchStatus, 2000);
    </script>
</body>
</html>'''

if __name__ == '__main__':
    # 确保 edge_tts 已导入（放在主程序内，避免循环导入）
    import edge_tts
    # 信号处理
    def signal_handler(sig, frame):
        if cap is not None:
            cap.release()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
