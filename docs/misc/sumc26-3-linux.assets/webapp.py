#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教室考勤系统 Web 服务 - 死锁修复版
- 特征提取移出锁外，避免阻塞
- 详细日志实时刷新
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

# 默认占位图
placeholder_path = os.path.join(STATIC_DIR, "placeholder.jpg")
if not os.path.exists(placeholder_path):
    placeholder = np.ones((100, 100, 3), dtype=np.uint8) * 240
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
    resized = cv2.resize(rgb, FACENET_INPUT_SIZE)
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
    if best_sim >= SIMILARITY_THRESHOLD:
        return best_id, face_database[best_id]["name"], best_sim
    return None, None, best_sim

def detect_faces(img_bgr):
    start = time.time()
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    boxes, _, scores = detector(rgb, target_size=TARGET_SIZE)
    faces = []
    for box, score in zip(boxes, scores):
        if score < CONFIDENCE_THRESHOLD:
            continue
        x1, y1, x2, y2 = [int(v) for v in box]
        faces.append((x1, y1, x2, y2, float(score)))
    elapsed = time.time() - start
    print(f"      [人脸检测] 耗时 {elapsed:.2f}秒，检测到 {len(faces)} 个人脸")
    return faces

# ==================== 业务逻辑 ====================
def register_student(student_id, student_name, face_crop_bgr, original_bgr=None):
    start_total = time.time()
    
    # 1. 特征提取（耗时操作，放在锁外）
    print(f"      [注册] 开始提取特征...")
    emb = extract_embedding(face_crop_bgr)
    
    # 2. 保存裁剪图
    crop_filename = f"{student_id}_crop_{int(time.time())}.jpg"
    crop_path = os.path.join(PROCESSED_DIR, crop_filename)
    cv2.imwrite(crop_path, face_crop_bgr)
    print(f"      [注册] 裁剪图已保存: {crop_filename}")
    
    # 3. 更新内存数据库（加锁）
    with db_lock:
        exists = student_id in face_database
        face_database[student_id] = {
            "name": student_name,
            "embedding": emb,
            "registered_at": datetime.now().isoformat()
        }
        print(f"      [注册] 内存数据库已更新")
    
    # 4. 保存数据库文件（锁外，避免I/O阻塞）
    save_database()
    
    # 5. 保存原始图片（可选）
    if original_bgr is not None:
        orig_filename = f"{student_id}_orig_{int(time.time())}.jpg"
        orig_path = os.path.join(PROCESSED_DIR, orig_filename)
        cv2.imwrite(orig_path, original_bgr)
        print(f"      [注册] 原始图已保存: {orig_filename}")
    
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
        color = (0, 255, 0) if sid else (0, 0, 255)
        label = f"{sid}_{name} ({sim:.2f})" if sid else "Unknown"
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

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
        students.append({
            "id": sid,
            "name": info["name"],
            "crop_url": crop_url
        })
    return jsonify(students)

@app.route("/api/register", methods=["POST"])
def api_register():
    request_start = time.time()
    print("\n========== 注册请求开始 ==========")
    try:
        data = request.get_json()
        if not data:
            print("[错误] 无效请求，无 JSON 数据")
            return jsonify({"error": "无效请求"}), 400
        
        sid = data.get("student_id", "").strip()
        name = data.get("student_name", "").strip()
        img_b64 = data.get("image")
        print(f"[2] 学号: {sid}, 姓名: {name}, 图片长度: {len(img_b64) if img_b64 else 0} 字符")
        
        if not sid or not name:
            print("[错误] 学号或姓名为空")
            return jsonify({"error": "学号和姓名不能为空"}), 400
        if not img_b64:
            print("[错误] 未提供图片")
            return jsonify({"error": "未提供图片"}), 400

        print("[3] 解码 base64 图片...")
        decode_start = time.time()
        try:
            header, encoded = img_b64.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("cv2.imdecode 返回 None")
            decode_elapsed = time.time() - decode_start
            print(f"    解码成功，耗时 {decode_elapsed:.2f}秒，图像尺寸: {img.shape}")
        except Exception as e:
            print(f"[错误] 图片解码失败: {e}")
            return jsonify({"error": "图片解析失败"}), 400

        print("[4] 开始人脸检测...")
        detect_start = time.time()
        faces = detect_faces(img)
        detect_elapsed = time.time() - detect_start
        print(f"    检测到 {len(faces)} 个人脸，耗时 {detect_elapsed:.2f}秒")
        
        if len(faces) == 0:
            print("[错误] 未检测到人脸")
            return jsonify({"error": "未检测到人脸，请重新拍摄/上传"}), 400

        extra_msg = ""
        if len(faces) > 1:
            print(f"[5] 检测到 {len(faces)} 张人脸，按面积排序取最大...")
            faces.sort(key=lambda f: (f[2]-f[0])*(f[3]-f[1]), reverse=True)
            extra_msg = "检测到多张人脸，已自动使用最大人脸进行注册"
            print(f"    最大人脸面积: {(faces[0][2]-faces[0][0])*(faces[0][3]-faces[0][1])}")
        else:
            print("[5] 单张人脸，直接使用")

        print("[6] 裁剪人脸区域...")
        x1, y1, x2, y2, _ = faces[0]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
        face_crop = img[y1:y2, x1:x2]
        if face_crop.size == 0:
            print("[错误] 人脸区域无效")
            return jsonify({"error": "人脸区域无效"}), 400
        print(f"    裁剪区域: ({x1},{y1}) -> ({x2},{y2})，尺寸: {face_crop.shape}")

        print("[7] 执行注册（特征提取、保存图片、更新数据库）...")
        success, msg, crop_filename = register_student(sid, name, face_crop, original_bgr=img)
        
        if extra_msg:
            msg = f"{extra_msg}，{msg}"
        
        total_elapsed = time.time() - request_start
        print(f"[完成] 注册{'成功' if success else '失败'}，总耗时 {total_elapsed:.2f}秒")
        print("========== 注册请求结束 ==========\n")
        
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
        print("========== 注册请求异常结束 ==========\n")
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500

# 其他路由（/api/attendance, /api/report）保持不变，省略以节省篇幅
# 但为了完整性，保留前面的代码
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

        try:
            header, encoded = img_b64.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError
        except Exception as e:
            print(f"[识别错误] 图片解码失败: {e}")
            return jsonify({"error": "图片解析失败"}), 400

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
        if isinstance(record, list):
            present_ids = record
        elif isinstance(record, dict) and "present_ids" in record:
            present_ids = record["present_ids"]
        else:
            present_ids = []
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

# ==================== 前端模板 ====================
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>教室考勤系统 | Neo-minimalism</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #f5f0e8; font-family: 'Inter', system-ui, sans-serif; }
        .card { background: rgba(255,255,255,0.88); backdrop-filter: blur(2px); border-radius: 2rem; box-shadow: 0 8px 20px rgba(0,0,0,0.03), 0 2px 6px rgba(0,0,0,0.05); transition: all 0.2s ease; border: 1px solid #e6dfd3; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 20px 30px -12px rgba(0,0,0,0.08); }
        .btn { background-color: #d9cdb0; color: #4a3b2c; font-weight: 500; border-radius: 9999px; padding: 0.5rem 1.2rem; transition: all 0.2s; border: none; cursor: pointer; }
        .btn-primary { background-color: #8c7a5b; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .btn-primary:hover { background-color: #6b5b45; transform: scale(0.98); }
        .btn-outline { background: transparent; border: 1px solid #cbc2b2; color: #6b5b45; }
        .btn-outline:hover { background: #f0eadf; }
        input, textarea { background: #fefcf8; border: 1px solid #e2d9ce; border-radius: 2rem; padding: 0.6rem 1rem; width: 100%; transition: 0.2s; }
        input:focus, textarea:focus { outline: none; border-color: #b8aa92; box-shadow: 0 0 0 3px rgba(140,122,91,0.1); }
        .badge { background-color: #e8e0d5; border-radius: 40px; padding: 0.2rem 0.8rem; font-size: 0.75rem; color: #5e4e3a; }
        .result-stats { background: #ffffffcc; border-radius: 1.5rem; padding: 1rem; margin-top: 1rem; }
        video, canvas { border-radius: 1rem; width: 100%; }
        .student-card { transition: all 0.1s; }
        .student-card:hover { transform: scale(1.02); background: rgba(255,255,245,0.9); }
    </style>
</head>
<body class="p-4 md:p-8 max-w-7xl mx-auto">
    <div class="text-center mb-8">
        <h1 class="text-4xl font-light tracking-tight text-[#5a4a34]">教室考勤系统</h1>
        <p class="text-[#8c7a5b] mt-2 text-sm">YOLOv5-Face + FaceNet | Neo‑minimalism</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 注册卡片 -->
        <div class="card p-6">
            <h2 class="text-2xl font-medium text-[#5a4a34] mb-1">📝 注册学生</h2>
            <p class="text-sm text-[#9b8b74] mb-5">单人正面照片，支持摄像头或上传（若有多人自动选最大人脸）</p>
            <div class="space-y-4">
                <div><label class="block text-sm font-medium text-[#6b5b45] mb-1">学号 (唯一)</label><input type="text" id="reg_id" placeholder="例如 2024001"></div>
                <div><label class="block text-sm font-medium text-[#6b5b45] mb-1">姓名</label><input type="text" id="reg_name" placeholder="张三"></div>
                <div class="flex flex-wrap gap-3">
                    <button id="openCameraRegBtn" class="btn btn-outline">📸 摄像头拍摄</button>
                    <button id="uploadFileRegBtn" class="btn btn-outline">🖼️ 上传照片</button>
                </div>
                <div id="regCameraPanel" style="display:none;" class="mt-3">
                    <video id="regVideo" autoplay playsinline></video>
                    <canvas id="regCanvas" style="display:none;"></canvas>
                    <div class="flex gap-2 mt-3"><button id="captureRegBtn" class="btn btn-primary flex-1">拍摄并注册</button><button id="closeRegCamBtn" class="btn btn-outline flex-1">关闭摄像头</button></div>
                </div>
                <div id="regResult" class="result-stats text-sm hidden"></div>
            </div>
        </div>

        <!-- 考勤卡片 -->
        <div class="card p-6">
            <h2 class="text-2xl font-medium text-[#5a4a34] mb-1">🎓 考勤识别</h2>
            <p class="text-sm text-[#9b8b74] mb-5">支持多人照片，自动标注学号+姓名+相似度，统计缺勤名单</p>
            <div class="space-y-4">
                <div class="flex flex-wrap gap-3">
                    <button id="openCameraAttBtn" class="btn btn-outline">📸 摄像头识别</button>
                    <button id="uploadFileAttBtn" class="btn btn-outline">🖼️ 上传照片</button>
                </div>
                <div id="attCameraPanel" style="display:none;" class="mt-3">
                    <video id="attVideo" autoplay playsinline></video>
                    <canvas id="attCanvas" style="display:none;"></canvas>
                    <div class="flex gap-2 mt-3"><button id="captureAttBtn" class="btn btn-primary flex-1">拍摄并识别</button><button id="closeAttCamBtn" class="btn btn-outline flex-1">关闭摄像头</button></div>
                </div>
                <div id="attResult" class="result-stats hidden"></div>
                <div id="attImagePreview" class="mt-3 text-center hidden"><p class="text-xs text-[#8c7a5b] mb-1">标注结果预览</p><img id="resultImg" class="rounded-xl max-w-full shadow-sm border border-[#e2d9ce]"></div>
            </div>
        </div>
    </div>

    <!-- 已注册学生列表 -->
    <div class="card p-6 mt-6">
        <h2 class="text-2xl font-medium text-[#5a4a34] mb-3">📋 已注册学生</h2>
        <div id="studentList" class="grid grid-cols-2 md:grid-cols-4 gap-4"></div>
    </div>

    <!-- 今日报告 -->
    <div class="card p-4 mt-6 flex flex-wrap justify-between items-center">
        <div class="text-[#6b5b45]">📋 今日考勤报告</div>
        <button id="reportBtn" class="btn btn-outline text-sm">刷新报告</button>
    </div>
    <div id="reportPanel" class="card p-4 mt-3 text-sm hidden"></div>

    <script>
        let regStream=null, attStream=null;
        const TIMEOUT_MS = 30000;

        function captureFrame(v,c){
            const ctx=c.getContext('2d');
            c.width=v.videoWidth;
            c.height=v.videoHeight;
            ctx.drawImage(v,0,0,c.width,c.height);
            return c.toDataURL('image/jpeg',0.8);
        }

        function stopStream(s){
            if(s) s.getTracks().forEach(t=>t.stop());
        }

        async function apiCall(endpoint, data, timeout=TIMEOUT_MS){
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            try{
                const resp = await fetch(endpoint, {
                    method:'POST',
                    headers:{'Content-Type':'application/json'},
                    body:JSON.stringify(data),
                    signal: controller.signal
                });
                clearTimeout(timeoutId);
                return await resp.json();
            }catch(e){
                clearTimeout(timeoutId);
                if(e.name === 'AbortError') throw new Error(`请求超时（${timeout/1000}秒），请缩小图片或稍后重试`);
                throw e;
            }
        }

        async function loadStudentList(){
            try{
                const resp=await fetch('/api/students');
                const students=await resp.json();
                const container=document.getElementById('studentList');
                if(students.length===0){
                    container.innerHTML='<div class="col-span-full text-center text-[#8c7a5b]">暂无学生，请注册</div>';
                    return;
                }
                let html='';
                for(const s of students){
                    html+=`<div class="student-card bg-white/70 rounded-xl p-3 text-center shadow-sm"><img src="${s.crop_url}" class="w-24 h-24 object-cover rounded-full mx-auto mb-2 border-2 border-[#d9cdb0]" onerror="this.src='/static/placeholder.jpg'"><div class="font-medium text-[#5a4a34]">${escapeHtml(s.name)}</div><div class="text-xs text-[#8c7a5b]">${escapeHtml(s.id)}</div></div>`;
                }
                container.innerHTML=html;
            }catch(e){console.error('加载学生列表失败',e);}
        }

        function escapeHtml(str){ return str.replace(/[&<>]/g, function(m){if(m==='&') return '&amp;'; if(m==='<') return '&lt;'; if(m==='>') return '&gt;'; return m;}); }

        async function register(id,name,img){
            const resultDiv=document.getElementById('regResult');
            resultDiv.innerHTML='<div class="animate-pulse">⏳ 注册中（约10-20秒）...</div>';
            resultDiv.classList.remove('hidden');
            try{
                const resp=await apiCall('/api/register',{student_id:id,student_name:name,image:img});
                if(resp.success){
                    resultDiv.innerHTML=`<span>✅ ${escapeHtml(resp.message)}</span><br><span class="text-xs">裁剪图已保存</span>`;
                    loadStudentList();
                }else{
                    resultDiv.innerHTML=`<span>❌ 注册失败: ${escapeHtml(resp.error)}</span>`;
                }
            }catch(e){
                console.error(e);
                resultDiv.innerHTML=`<span>⚠️ 注册失败: ${e.message}</span>`;
            }
        }

        async function attendanceCheck(img,mark=false){
            const resultDiv=document.getElementById('attResult');
            resultDiv.innerHTML='<div class="animate-pulse">⏳ 识别中（约10-20秒）...</div>';
            resultDiv.classList.remove('hidden');
            try{
                const resp=await apiCall('/api/attendance',{image:img,mark_attendance:mark});
                if(resp.success){
                    const s=resp.stats;
                    let h=`<div class="font-medium">📊 考勤统计</div><div class="grid grid-cols-3 gap-2 mt-2 text-center"><div><span class="block text-lg font-bold">${s.total}</span><span class="text-xs">应到</span></div><div><span class="block text-lg font-bold text-green-700">${s.present_count}</span><span class="text-xs">实到</span></div><div><span class="block text-lg font-bold text-amber-700">${s.absent_count}</span><span class="text-xs">缺勤</span></div></div>`;
                    if(s.present_list.length) h+=`<div class="mt-2"><span class="badge">出勤:</span> ${escapeHtml(s.present_list.join(', '))}</div>`;
                    if(s.absent_list.length) h+=`<div class="mt-2"><span class="badge">缺勤:</span> ${escapeHtml(s.absent_list.join(', '))}</div>`;
                    resultDiv.innerHTML=h;
                    if(resp.annotated_url){
                        document.getElementById('resultImg').src=resp.annotated_url;
                        document.getElementById('attImagePreview').classList.remove('hidden');
                    }
                }else{
                    resultDiv.innerHTML=`<span>❌ 识别失败: ${escapeHtml(resp.error)}</span>`;
                }
            }catch(e){
                console.error(e);
                resultDiv.innerHTML=`<span>⚠️ 识别失败: ${e.message}</span>`;
            }
        }

        async function loadReport(){
            try{
                const resp=await fetch('/api/report');
                if(!resp.ok) throw new Error('无记录');
                const d=await resp.json();
                let h=`<div class="flex justify-between"><span>📅 ${d.date}</span><span>总人数 ${d.total}</span></div><div class="mt-2"><span class="badge">出勤 (${d.present_count})</span> ${escapeHtml(d.present_names.join(', ')||'无')}</div><div><span class="badge">缺勤 (${d.absent_count})</span> ${escapeHtml(d.absent_names.join(', ')||'无')}</div>`;
                document.getElementById('reportPanel').innerHTML=h;
                document.getElementById('reportPanel').classList.remove('hidden');
            }catch(e){
                document.getElementById('reportPanel').innerHTML='<span class="text-rose-600">暂无今日考勤记录</span>';
                document.getElementById('reportPanel').classList.remove('hidden');
            }
        }

        async function initRegCamera(){
            if(regStream) stopStream(regStream);
            try{
                const s=await navigator.mediaDevices.getUserMedia({video:true});
                regStream=s;
                const v=document.getElementById('regVideo');
                v.srcObject=s;
                document.getElementById('regCameraPanel').style.display='block';
                document.getElementById('captureRegBtn').onclick=()=>{
                    const c=document.getElementById('regCanvas');
                    const img=captureFrame(v,c);
                    const id=document.getElementById('reg_id').value.trim();
                    const name=document.getElementById('reg_name').value.trim();
                    if(!id||!name){ alert('请填写学号和姓名'); return; }
                    register(id,name,img);
                };
                document.getElementById('closeRegCamBtn').onclick=()=>{ stopStream(regStream); regStream=null; document.getElementById('regCameraPanel').style.display='none'; };
            }catch(e){ alert('无法访问摄像头: '+e.message); }
        }

        function initAttCamera(){
            if(attStream) stopStream(attStream);
            navigator.mediaDevices.getUserMedia({video:true}).then(s=>{
                attStream=s;
                const v=document.getElementById('attVideo');
                v.srcObject=s;
                document.getElementById('attCameraPanel').style.display='block';
                document.getElementById('captureAttBtn').onclick=()=>{
                    const c=document.getElementById('attCanvas');
                    const img=captureFrame(v,c);
                    const mark=confirm('是否将此照片计入考勤记录？');
                    attendanceCheck(img,mark);
                };
                document.getElementById('closeAttCamBtn').onclick=()=>{ stopStream(attStream); attStream=null; document.getElementById('attCameraPanel').style.display='none'; };
            }).catch(e=>alert('摄像头不可用: '+e.message));
        }

        function uploadFile(mode){
            const input=document.createElement('input');
            input.type='file';
            input.accept='image/jpeg,image/png,image/jpg';
            input.onchange=e=>{
                const file=e.target.files[0];
                if(!file) return;
                const reader=new FileReader();
                reader.onload=ev=>{
                    const b64=ev.target.result;
                    if(mode==='reg'){
                        const id=document.getElementById('reg_id').value.trim();
                        const name=document.getElementById('reg_name').value.trim();
                        if(!id||!name){ alert('请填写学号姓名'); return; }
                        register(id,name,b64);
                    }else{
                        const mark=confirm('是否将此照片计入考勤记录？');
                        attendanceCheck(b64,mark);
                    }
                };
                reader.readAsDataURL(file);
            };
            input.click();
        }

        document.getElementById('openCameraRegBtn').onclick=initRegCamera;
        document.getElementById('uploadFileRegBtn').onclick=()=>uploadFile('reg');
        document.getElementById('openCameraAttBtn').onclick=initAttCamera;
        document.getElementById('uploadFileAttBtn').onclick=()=>uploadFile('att');
        document.getElementById('reportBtn').onclick=loadReport;
        loadStudentList();
        loadReport();
    </script>
</body>
</html>"""

with open(os.path.join(TEMPLATES_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML_TEMPLATE)

if __name__ == "__main__":
    print("=" * 50)
    print("教室考勤系统 Web 服务已启动（死锁修复版）")
    print(f"数据库文件: {FACE_DB_PATH}")
    print("访问地址: http://0.0.0.0:5000")
    print("特征提取已移出锁外，支持并发注册")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
