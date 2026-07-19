#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教室考勤系统 Web 服务 (YOLOv5-Face + FaceNet) - 苹果发布会风格
极简深色背景、玻璃质感卡片、大标题、精致动画
"""

import cv2
import numpy as np
import torch
from yolo5face.get_model import get_model
from facenet_pytorch import InceptionResnetV1
import time
import os
import json
import traceback
import sys
from datetime import datetime
import base64
import threading
from pathlib import Path

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from flask_cors import CORS

# 强制实时输出日志
sys.stdout.reconfigure(line_buffering=True)

# ==================== 配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FACE_DB_PATH = os.path.join(BASE_DIR, "face_database.npz")
ATTENDANCE_RECORD_PATH = os.path.join(BASE_DIR, "attendance_records.json")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# 默认占位图（深灰底）
placeholder_path = os.path.join(STATIC_DIR, "placeholder.jpg")
if not os.path.exists(placeholder_path):
    placeholder = np.ones((100, 100, 3), dtype=np.uint8) * 40
    cv2.imwrite(placeholder_path, placeholder)

CONFIDENCE_THRESHOLD = 0.5
SIMILARITY_THRESHOLD = 0.5
TARGET_SIZE = 320
MIN_FACE_SIZE = 24
FACENET_INPUT_SIZE = (160, 160)

torch.set_num_threads(2)
device = torch.device("cpu")

print(f"[启动] 工作目录: {BASE_DIR}")
print(f"[启动] 数据库路径: {FACE_DB_PATH}")

# ==================== 全局模型 ====================
print("[系统] 加载 YOLOv5-Face 检测器...")
detector = get_model("yolov5n", device=-1, min_face=MIN_FACE_SIZE)

print("[系统] 加载 FaceNet 识别器...")
recognizer = InceptionResnetV1(pretrained="vggface2").eval().to(device)

# ==================== 数据库 ====================
db_lock = threading.Lock()
face_database = {}
attendance_records = {}

def load_database():
    global face_database
    if os.path.exists(FACE_DB_PATH):
        try:
            data = np.load(FACE_DB_PATH, allow_pickle=True)
            face_database = data["database"].item()
            print(f"[数据库] 加载成功，共 {len(face_database)} 名学生")
            for sid, info in face_database.items():
                print(f"  - {sid}: {info['name']}")
        except Exception as e:
            print(f"[数据库] 加载失败: {e}")
            face_database = {}
    else:
        print("[数据库] 文件不存在，将创建新库")
        face_database = {}

def save_database():
    try:
        to_save = {sid: {"name": info["name"], "embedding": info["embedding"]} for sid, info in face_database.items()}
        np.savez(FACE_DB_PATH, database=to_save)
        print(f"[数据库] 已保存 {len(face_database)} 名学生到 {FACE_DB_PATH}")
    except Exception as e:
        print(f"[数据库] 保存失败: {e}")

def load_attendance():
    global attendance_records
    if os.path.exists(ATTENDANCE_RECORD_PATH):
        with open(ATTENDANCE_RECORD_PATH, "r", encoding="utf-8") as f:
            attendance_records = json.load(f)
        for date, record in attendance_records.items():
            if isinstance(record, list):
                attendance_records[date] = {"present_ids": record}
            elif isinstance(record, dict) and "present_ids" not in record:
                attendance_records[date] = {"present_ids": []}
        print(f"[考勤] 加载 {len(attendance_records)} 天记录")
    else:
        attendance_records = {}

def save_attendance():
    with open(ATTENDANCE_RECORD_PATH, "w", encoding="utf-8") as f:
        json.dump(attendance_records, f, ensure_ascii=False, indent=2)

load_database()
load_attendance()

# ==================== 人脸特征与识别 ====================
def extract_embedding(face_bgr):
    start = time.time()
    rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (160, 160))
    tensor = torch.tensor(resized).permute(2,0,1).float() / 255.0
    tensor = tensor.unsqueeze(0).to(device)
    with torch.no_grad():
        emb = recognizer(tensor)
    elapsed = time.time() - start
    print(f"      [特征提取] 耗时 {elapsed:.2f}秒")
    return emb.cpu().numpy().flatten()

def recognize_student(embedding):
    if not face_database:
        return None, None, 0.0
    best_id = None
    best_sim = -1.0
    for sid, info in face_database.items():
        sim = np.dot(embedding, info["embedding"]) / (np.linalg.norm(embedding) * np.linalg.norm(info["embedding"]))
        if sim > best_sim:
            best_sim = sim
            best_id = sid
    if best_sim >= 0.5:
        return best_id, face_database[best_id]["name"], best_sim
    return None, None, best_sim

def detect_faces(img_bgr):
    start = time.time()
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    boxes, _, scores = detector(rgb, target_size=320)
    faces = []
    for box, score in zip(boxes, scores):
        if score < 0.5:
            continue
        x1, y1, x2, y2 = [int(v) for v in box]
        faces.append((x1, y1, x2, y2, float(score)))
    elapsed = time.time() - start
    print(f"      [人脸检测] 耗时 {elapsed:.2f}秒，检测到 {len(faces)} 个人脸")
    return faces

# ==================== 业务逻辑 ====================
def register_student(student_id, student_name, face_crop_bgr, original_bgr=None):
    start_total = time.time()
    emb = extract_embedding(face_crop_bgr)
    crop_filename = f"{student_id}_crop_{int(time.time())}.jpg"
    crop_path = os.path.join(PROCESSED_DIR, crop_filename)
    cv2.imwrite(crop_path, face_crop_bgr)
    print(f"      [注册] 裁剪图已保存: {crop_filename}")
    
    with db_lock:
        exists = student_id in face_database
        face_database[student_id] = {
            "name": student_name,
            "embedding": emb,
            "registered_at": datetime.now().isoformat()
        }
    save_database()
    
    if original_bgr is not None:
        orig_filename = f"{student_id}_orig_{int(time.time())}.jpg"
        orig_path = os.path.join(PROCESSED_DIR, orig_filename)
        cv2.imwrite(orig_path, original_bgr)
    
    msg = "注册成功" if not exists else "已更新特征"
    elapsed = time.time() - start_total
    print(f"      [注册] 总耗时 {elapsed:.2f}秒，{msg}")
    return True, msg, crop_filename

def process_attendance(img_bgr):
    faces = detect_faces(img_bgr)
    annotated = img_bgr.copy()
    recognized = []
    for (x1, y1, x2, y2, score) in faces:
        if x2 <= x1 or y2 <= y1:
            continue
        face_crop = img_bgr[y1:y2, x1:x2]
        if face_crop.size == 0:
            continue
        emb = extract_embedding(face_crop)
        sid, name, sim = recognize_student(emb)
        recognized.append({
            "id": sid,
            "name": name,
            "similarity": sim,
            "bbox": (x1, y1, x2, y2)
        })
        color = (0, 255, 0) if sid else (255, 50, 50)
        label = f"{sid}_{name} ({sim:.2f})" if sid else "Unknown"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    total = len(face_database)
    present_ids = {r["id"] for r in recognized if r["id"]}
    present_names = [face_database[sid]["name"] for sid in present_ids if sid in face_database]
    absent_ids = set(face_database.keys()) - present_ids
    absent_names = [face_database[sid]["name"] for sid in absent_ids if sid in face_database]
    stats = {
        "total": total,
        "present_count": len(present_ids),
        "absent_count": total - len(present_ids),
        "present_names": present_names,
        "absent_names": absent_names,
        "recognized": recognized
    }
    return annotated, stats

def mark_attendance(stats, session_id=None):
    if session_id is None:
        session_id = datetime.now().strftime("%Y-%m-%d")
    present_ids = {r["id"] for r in stats["recognized"] if r["id"]}
    if session_id not in attendance_records:
        attendance_records[session_id] = {"present_ids": []}
    current = set(attendance_records[session_id]["present_ids"])
    current.update(present_ids)
    attendance_records[session_id]["present_ids"] = list(current)
    save_attendance()
    return True

# ==================== Flask 应用 ====================
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/processed/<filename>")
def processed_file(filename):
    return send_from_directory(PROCESSED_DIR, filename)

@app.route("/api/students")
def api_students():
    students = []
    for sid, info in face_database.items():
        crop_files = [f for f in os.listdir(PROCESSED_DIR) if f.startswith(f"{sid}_crop_")]
        if crop_files:
            crop_files.sort(key=lambda f: os.path.getmtime(os.path.join(PROCESSED_DIR, f)), reverse=True)
            crop_url = url_for("processed_file", filename=crop_files[0], _external=False)
        else:
            crop_url = url_for("static", filename="placeholder.jpg", _external=False)
        students.append({"id": sid, "name": info["name"], "crop_url": crop_url})
    return jsonify(students)

@app.route("/api/register", methods=["POST"])
def api_register():
    print("\n========== 注册请求开始 ==========")
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效请求"}), 400
        sid = data.get("student_id", "").strip()
        name = data.get("student_name", "").strip()
        img_b64 = data.get("image")
        if not sid or not name:
            return jsonify({"error": "学号和姓名不能为空"}), 400
        if not img_b64:
            return jsonify({"error": "未提供图片"}), 400
        
        header, encoded = img_b64.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("图片解码失败")
        print(f"    解码成功，图像尺寸: {img.shape}")
        
        faces = detect_faces(img)
        if len(faces) == 0:
            return jsonify({"error": "未检测到人脸"}), 400
        
        extra_msg = ""
        if len(faces) > 1:
            faces.sort(key=lambda f: (f[2]-f[0])*(f[3]-f[1]), reverse=True)
            extra_msg = "检测到多张人脸，已自动使用最大人脸进行注册"
        x1, y1, x2, y2, _ = faces[0]
        face_crop = img[y1:y2, x1:x2]
        if face_crop.size == 0:
            return jsonify({"error": "人脸区域无效"}), 400
        
        success, msg, crop_filename = register_student(sid, name, face_crop, original_bgr=img)
        if extra_msg:
            msg = f"{extra_msg}，{msg}"
        if success:
            return jsonify({
                "success": True,
                "message": msg,
                "crop_url": url_for("processed_file", filename=crop_filename, _external=False)
            })
        else:
            return jsonify({"error": msg}), 500
    except Exception as e:
        print(f"[异常] {traceback.format_exc()}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

@app.route("/api/attendance", methods=["POST"])
def api_attendance():
    print("[识别请求] 收到 POST /api/attendance")
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效请求"}), 400
        img_b64 = data.get("image")
        mark = data.get("mark_attendance", False)
        if not img_b64:
            return jsonify({"error": "未提供图片"}), 400
        
        header, encoded = img_b64.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError
        annotated, stats = process_attendance(img)
        out_fname = f"attendance_{int(time.time())}.jpg"
        out_path = os.path.join(PROCESSED_DIR, out_fname)
        cv2.imwrite(out_path, annotated)
        if mark:
            mark_attendance(stats)
        return jsonify({
            "success": True,
            "stats": {
                "total": int(stats["total"]),
                "present_count": int(stats["present_count"]),
                "absent_count": int(stats["absent_count"]),
                "present_list": stats["present_names"],
                "absent_list": stats["absent_names"]
            },
            "annotated_url": url_for("processed_file", filename=out_fname, _external=False),
            "recognized": [
                {"id": r["id"], "name": r["name"], "similarity": float(round(r["similarity"], 3))}
                for r in stats["recognized"] if r["id"]
            ]
        })
    except Exception as e:
        print(f"[识别异常] {traceback.format_exc()}")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

@app.route("/api/report")
def api_report():
    try:
        date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
        if date not in attendance_records:
            return jsonify({"error": f"暂无 {date} 的记录"}), 404
        record = attendance_records[date]
        present_ids = record["present_ids"] if isinstance(record, dict) else record
        present_names = [face_database[sid]["name"] for sid in present_ids if sid in face_database]
        absent_names = [face_database[sid]["name"] for sid in face_database if sid not in present_ids]
        return jsonify({
            "date": date,
            "total": len(face_database),
            "present_count": len(present_ids),
            "absent_count": len(face_database) - len(present_ids),
            "present_names": present_names,
            "absent_names": absent_names
        })
    except Exception as e:
        print(f"[报告异常] {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

# ==================== 前端模板 - 苹果发布会风格 ====================
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>教室考勤系统 | 苹果发布会风格</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0d0d0d;
            background-image: radial-gradient(circle at 25% 0%, rgba(80, 80, 90, 0.15) 0%, rgba(0,0,0,0) 70%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
            color: #f5f5f7;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }
        /* 主容器 */
        .container {
            max-width: 1440px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }
        /* 大标题 */
        .hero {
            text-align: center;
            margin-bottom: 4rem;
        }
        .hero h1 {
            font-size: 4.5rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0b0 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.5rem;
        }
        .hero .sub {
            font-size: 1.2rem;
            font-weight: 400;
            color: #86868b;
            letter-spacing: 0.3px;
        }
        /* 卡片网格 */
        .grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 2rem;
            margin-bottom: 3rem;
        }
        /* 玻璃卡片 */
        .glass-card {
            background: rgba(30, 30, 35, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 2rem 1.8rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .glass-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 35px -12px rgba(0,0,0,0.5);
            border-color: rgba(255,255,255,0.15);
        }
        .card-title {
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .card-desc {
            font-size: 0.9rem;
            color: #98989f;
            margin-bottom: 1.8rem;
            border-left: 2px solid #3a3a44;
            padding-left: 0.8rem;
        }
        /* 表单元素 */
        .input-group {
            margin-bottom: 1.2rem;
        }
        label {
            display: block;
            font-size: 0.8rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #aaaab0;
            margin-bottom: 0.4rem;
        }
        input, .btn {
            width: 100%;
            background: rgba(20, 20, 25, 0.8);
            border: 1px solid #3a3a44;
            border-radius: 1.2rem;
            padding: 0.8rem 1.2rem;
            font-size: 1rem;
            color: #fff;
            transition: all 0.2s;
        }
        input:focus {
            outline: none;
            border-color: #6e6e7a;
            background: rgba(30, 30, 38, 0.9);
        }
        .btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.15);
            cursor: pointer;
            font-weight: 500;
            text-align: center;
            transition: 0.2s;
        }
        .btn-primary {
            background: #ffffff;
            color: #1d1d1f;
            border: none;
            font-weight: 600;
        }
        .btn-primary:hover {
            background: #e0e0e6;
            transform: scale(0.98);
        }
        .btn-outline {
            background: transparent;
            border: 1px solid #5e5e68;
        }
        .btn-outline:hover {
            background: rgba(255,255,255,0.08);
            border-color: #8e8e98;
        }
        .flex-buttons {
            display: flex;
            gap: 0.8rem;
            margin-top: 0.5rem;
        }
        .flex-buttons .btn {
            flex: 1;
        }
        /* 视频/画布 */
        .camera-panel {
            margin-top: 1.2rem;
            border-radius: 1.5rem;
            overflow: hidden;
            background: #000;
        }
        video, canvas {
            width: 100%;
            display: block;
        }
        /* 结果卡片 */
        .result-card {
            background: rgba(0,0,0,0.4);
            border-radius: 1.2rem;
            padding: 1rem;
            margin-top: 1rem;
            font-size: 0.9rem;
            backdrop-filter: blur(8px);
        }
        /* 学生网格 */
        .student-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        .student-item {
            background: rgba(20,20,25,0.6);
            border-radius: 1.2rem;
            padding: 0.8rem;
            text-align: center;
            backdrop-filter: blur(4px);
            transition: 0.1s;
        }
        .student-item img {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 0.5rem;
            border: 1px solid #5a5a64;
        }
        .student-name {
            font-weight: 500;
            font-size: 0.9rem;
        }
        .student-id {
            font-size: 0.7rem;
            color: #8e8e98;
        }
        /* 报告区域 */
        .report-card {
            background: rgba(20,20,25,0.5);
            backdrop-filter: blur(16px);
            border-radius: 1.5rem;
            padding: 1.5rem;
            margin-top: 1rem;
        }
        .badge {
            background: #2c2c32;
            border-radius: 2rem;
            padding: 0.2rem 0.8rem;
            font-size: 0.75rem;
            color: #ddd;
            display: inline-block;
        }
        hr {
            border-color: #2a2a30;
            margin: 1rem 0;
        }
        @media (max-width: 768px) {
            .container { padding: 1.5rem; }
            .grid-2 { grid-template-columns: 1fr; gap: 1.5rem; }
            .hero h1 { font-size: 2.5rem; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="hero">
        <h1>教室考勤系统</h1>
        <div class="sub">YOLOv5‑Face + FaceNet · 苹果发布会风格</div>
    </div>

    <div class="grid-2">
        <!-- 注册卡片 -->
        <div class="glass-card">
            <div class="card-title">📝 注册学生</div>
            <div class="card-desc">单人正面照片，支持摄像头或上传（多人脸自动选最大）</div>
            <div class="input-group">
                <label>学号 (唯一)</label>
                <input type="text" id="reg_id" placeholder="例如 2024001">
            </div>
            <div class="input-group">
                <label>姓名</label>
                <input type="text" id="reg_name" placeholder="张三">
            </div>
            <div class="flex-buttons">
                <button id="openCameraRegBtn" class="btn btn-outline">📸 摄像头</button>
                <button id="uploadFileRegBtn" class="btn btn-outline">🖼️ 上传照片</button>
            </div>
            <div id="regCameraPanel" style="display:none;" class="camera-panel">
                <video id="regVideo" autoplay playsinline></video>
                <canvas id="regCanvas" style="display:none;"></canvas>
                <div class="flex-buttons" style="margin: 0.5rem;">
                    <button id="captureRegBtn" class="btn btn-primary">拍摄并注册</button>
                    <button id="closeRegCamBtn" class="btn btn-outline">关闭</button>
                </div>
            </div>
            <div id="regResult" class="result-card" style="display:none;"></div>
        </div>

        <!-- 考勤卡片 -->
        <div class="glass-card">
            <div class="card-title">🎓 考勤识别</div>
            <div class="card-desc">多人照片，自动标注学号+姓名+相似度，统计缺勤</div>
            <div class="flex-buttons">
                <button id="openCameraAttBtn" class="btn btn-outline">📸 摄像头识别</button>
                <button id="uploadFileAttBtn" class="btn btn-outline">🖼️ 上传照片</button>
            </div>
            <div id="attCameraPanel" style="display:none;" class="camera-panel">
                <video id="attVideo" autoplay playsinline></video>
                <canvas id="attCanvas" style="display:none;"></canvas>
                <div class="flex-buttons" style="margin: 0.5rem;">
                    <button id="captureAttBtn" class="btn btn-primary">拍摄并识别</button>
                    <button id="closeAttCamBtn" class="btn btn-outline">关闭</button>
                </div>
            </div>
            <div id="attResult" class="result-card" style="display:none;"></div>
            <div id="attImagePreview" style="display:none; margin-top: 1rem;">
                <div style="font-size:0.8rem; color:#aaa; margin-bottom:0.3rem;">标注结果预览</div>
                <img id="resultImg" style="width:100%; border-radius:1rem; border:1px solid #3a3a44;">
            </div>
        </div>
    </div>

    <!-- 已注册学生列表 -->
    <div class="glass-card" style="margin-bottom: 2rem;">
        <div class="card-title" style="font-size: 1.5rem;">📋 已注册学生</div>
        <div id="studentList" class="student-grid"></div>
    </div>

    <!-- 今日报告 -->
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="card-title" style="font-size: 1.5rem;">📋 今日考勤报告</div>
            <button id="reportBtn" class="btn btn-outline" style="width: auto; padding: 0.4rem 1rem;">刷新</button>
        </div>
        <div id="reportPanel" style="margin-top: 1rem;"></div>
    </div>
</div>

<script>
    let regStream = null, attStream = null;
    const TIMEOUT_MS = 30000;

    function captureFrame(v, c) {
        const ctx = c.getContext('2d');
        c.width = v.videoWidth;
        c.height = v.videoHeight;
        ctx.drawImage(v, 0, 0, c.width, c.height);
        return c.toDataURL('image/jpeg', 0.8);
    }
    function stopStream(s) { if(s) s.getTracks().forEach(t => t.stop()); }
    async function apiCall(endpoint, data, timeout = TIMEOUT_MS) {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), timeout);
        try {
            const resp = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                signal: controller.signal
            });
            clearTimeout(tid);
            return await resp.json();
        } catch(e) {
            clearTimeout(tid);
            if(e.name === 'AbortError') throw new Error(`请求超时（${timeout/1000}秒）`);
            throw e;
        }
    }
    function escapeHtml(s) { return s.replace(/[&<>]/g, function(m){ if(m==='&') return '&amp;'; if(m==='<') return '&lt;'; if(m==='>') return '&gt;'; return m;}); }

    async function loadStudentList() {
        try {
            const resp = await fetch('/api/students');
            const students = await resp.json();
            const container = document.getElementById('studentList');
            if(students.length === 0) {
                container.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:#86868b;">暂无学生，请注册</div>';
                return;
            }
            let html = '';
            for(const s of students) {
                html += `<div class="student-item">
                            <img src="${s.crop_url}" onerror="this.src='/static/placeholder.jpg'">
                            <div class="student-name">${escapeHtml(s.name)}</div>
                            <div class="student-id">${escapeHtml(s.id)}</div>
                         </div>`;
            }
            container.innerHTML = html;
        } catch(e) { console.error(e); }
    }

    async function register(id, name, img) {
        const resultDiv = document.getElementById('regResult');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div>⏳ 注册中（约10-20秒）...</div>';
        try {
            const res = await apiCall('/api/register', { student_id: id, student_name: name, image: img });
            if(res.success) {
                resultDiv.innerHTML = `<div>✅ ${escapeHtml(res.message)}<br><span style="font-size:0.8rem;">裁剪图已保存</span></div>`;
                loadStudentList();
            } else {
                resultDiv.innerHTML = `<div>❌ 注册失败: ${escapeHtml(res.error)}</div>`;
            }
        } catch(e) {
            resultDiv.innerHTML = `<div>⚠️ 注册失败: ${escapeHtml(e.message)}</div>`;
        }
    }

    async function attendanceCheck(img, mark=false) {
        const resultDiv = document.getElementById('attResult');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = '<div>⏳ 识别中（约10-20秒）...</div>';
        try {
            const res = await apiCall('/api/attendance', { image: img, mark_attendance: mark });
            if(res.success) {
                const s = res.stats;
                let html = `<div style="font-weight:600;">📊 考勤统计</div>
                            <div style="display:flex; gap:1rem; margin-top:0.5rem;">
                                <div><span style="font-size:1.2rem;">${s.total}</span><br>应到</div>
                                <div><span style="font-size:1.2rem;">${s.present_count}</span><br>实到</div>
                                <div><span style="font-size:1.2rem;">${s.absent_count}</span><br>缺勤</div>
                            </div>`;
                if(s.present_list.length) html += `<div style="margin-top:0.5rem;"><span class="badge">出勤</span> ${escapeHtml(s.present_list.join(', '))}</div>`;
                if(s.absent_list.length) html += `<div><span class="badge">缺勤</span> ${escapeHtml(s.absent_list.join(', '))}</div>`;
                resultDiv.innerHTML = html;
                if(res.annotated_url) {
                    document.getElementById('resultImg').src = res.annotated_url;
                    document.getElementById('attImagePreview').style.display = 'block';
                }
            } else {
                resultDiv.innerHTML = `<div>❌ 识别失败: ${escapeHtml(res.error)}</div>`;
            }
        } catch(e) {
            resultDiv.innerHTML = `<div>⚠️ 识别失败: ${escapeHtml(e.message)}</div>`;
        }
    }

    async function loadReport() {
        try {
            const resp = await fetch('/api/report');
            if(!resp.ok) throw new Error();
            const d = await resp.json();
            let html = `<div style="display:flex; justify-content:space-between;"><span>📅 ${d.date}</span><span>总人数 ${d.total}</span></div>
                        <div style="margin-top:0.5rem;"><span class="badge">出勤 (${d.present_count})</span> ${escapeHtml(d.present_names.join(', ')||'无')}</div>
                        <div><span class="badge">缺勤 (${d.absent_count})</span> ${escapeHtml(d.absent_names.join(', ')||'无')}</div>`;
            document.getElementById('reportPanel').innerHTML = html;
        } catch(e) {
            document.getElementById('reportPanel').innerHTML = '<span style="color:#c44;">暂无今日考勤记录</span>';
        }
    }

    // 摄像头注册
    async function initRegCamera() {
        if(regStream) stopStream(regStream);
        try {
            const s = await navigator.mediaDevices.getUserMedia({ video: true });
            regStream = s;
            const v = document.getElementById('regVideo');
            v.srcObject = s;
            document.getElementById('regCameraPanel').style.display = 'block';
            document.getElementById('captureRegBtn').onclick = () => {
                const canvas = document.getElementById('regCanvas');
                const img = captureFrame(v, canvas);
                const id = document.getElementById('reg_id').value.trim();
                const name = document.getElementById('reg_name').value.trim();
                if(!id || !name) { alert('请填写学号和姓名'); return; }
                register(id, name, img);
            };
            document.getElementById('closeRegCamBtn').onclick = () => {
                stopStream(regStream);
                regStream = null;
                document.getElementById('regCameraPanel').style.display = 'none';
            };
        } catch(e) { alert('无法访问摄像头: '+e.message); }
    }

    function initAttCamera() {
        if(attStream) stopStream(attStream);
        navigator.mediaDevices.getUserMedia({ video: true }).then(s => {
            attStream = s;
            const v = document.getElementById('attVideo');
            v.srcObject = s;
            document.getElementById('attCameraPanel').style.display = 'block';
            document.getElementById('captureAttBtn').onclick = () => {
                const canvas = document.getElementById('attCanvas');
                const img = captureFrame(v, canvas);
                const mark = confirm('是否将此照片计入考勤记录？');
                attendanceCheck(img, mark);
            };
            document.getElementById('closeAttCamBtn').onclick = () => {
                stopStream(attStream);
                attStream = null;
                document.getElementById('attCameraPanel').style.display = 'none';
            };
        }).catch(e => alert('摄像头不可用: '+e.message));
    }

    function uploadFile(mode) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/jpeg,image/png,image/jpg';
        input.onchange = e => {
            const file = e.target.files[0];
            if(!file) return;
            const reader = new FileReader();
            reader.onload = ev => {
                const b64 = ev.target.result;
                if(mode === 'reg') {
                    const id = document.getElementById('reg_id').value.trim();
                    const name = document.getElementById('reg_name').value.trim();
                    if(!id || !name) { alert('请填写学号姓名'); return; }
                    register(id, name, b64);
                } else {
                    const mark = confirm('是否将此照片计入考勤记录？');
                    attendanceCheck(b64, mark);
                }
            };
            reader.readAsDataURL(file);
        };
        input.click();
    }

    document.getElementById('openCameraRegBtn').onclick = initRegCamera;
    document.getElementById('uploadFileRegBtn').onclick = () => uploadFile('reg');
    document.getElementById('openCameraAttBtn').onclick = initAttCamera;
    document.getElementById('uploadFileAttBtn').onclick = () => uploadFile('att');
    document.getElementById('reportBtn').onclick = loadReport;
    loadStudentList();
    loadReport();
</script>
</body>
</html>"""

with open(os.path.join(TEMPLATES_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML_TEMPLATE)

if __name__ == "__main__":
    print("=" * 50)
    print("教室考勤系统 Web 服务已启动（苹果发布会风格）")
    print(f"数据库文件: {FACE_DB_PATH}")
    print("访问地址: http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
