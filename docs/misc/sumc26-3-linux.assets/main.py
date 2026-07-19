#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教室考勤系统 (YOLOv5-Face + FaceNet)
优化版：支持批量注册、SSH无界面运行、输出缺勤名单
"""

import cv2
import numpy as np
import torch
from yolo5face.get_model import get_model
from facenet_pytorch import InceptionResnetV1
import time
import os
import json
from datetime import datetime
import sys
import select
from pathlib import Path

# ==================== 系统参数配置 ====================
FACE_DB_PATH = "face_database.npz"
ATTENDANCE_RECORD_PATH = "attendance_records.json"
ROSTER_DIR = "roster"  # 批量注册照片存放目录

CONFIDENCE_THRESHOLD = 0.5
SIMILARITY_THRESHOLD = 0.5
TARGET_SIZE = 320  # 降低尺寸，提高CPU推理速度
MIN_FACE_SIZE = 24
FACENET_INPUT_SIZE = (160, 160)

torch.set_num_threads(4)
device = torch.device("cpu")
if torch.backends.mkl.is_available():
    print("[INFO] Intel MKL 已启用，CPU推理性能优化")

# 检测是否有图形界面（SSH下通常没有）
HAS_GUI = bool(os.environ.get("DISPLAY"))
if not HAS_GUI:
    print("[提示] 未检测到图形界面，将禁用窗口显示，所有结果仅输出文本")


# ==================== 辅助函数 ====================
def input_with_timeout(prompt, timeout=10):
    """带超时的输入函数，超时返回 None"""
    print(prompt, end="", flush=True)
    if sys.platform == "win32":
        return input()
    else:
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().rstrip("\n")
        else:
            print("\n[超时] 未在 {} 秒内输入，自动取消注册".format(timeout))
            return None


def safe_imshow(window_name, img, wait_ms=0):
    """安全显示图像：仅在图形界面环境下显示"""
    if HAS_GUI and img is not None:
        cv2.imshow(window_name, img)
        if wait_ms > 0:
            cv2.waitKey(wait_ms)
            cv2.destroyWindow(window_name)
        return True
    return False


# ==================== 核心类 ====================
class ClassroomAttendanceSystem:
    def __init__(self):
        print("[系统] 正在初始化教室考勤系统...")
        self.detector = get_model("yolov5n", device=-1, min_face=MIN_FACE_SIZE)
        self.recognizer = InceptionResnetV1(pretrained="vggface2").eval().to(device)
        self.face_database = {}
        self.attendance_records = {}
        self.load_database()
        self.attendance_records = self.load_attendance_records()
        print(f"[系统] 初始化完成，已注册 {len(self.face_database)} 名学生")

    # ---------- 数据库管理 ----------
    def load_database(self):
        if os.path.exists(FACE_DB_PATH):
            data = np.load(FACE_DB_PATH, allow_pickle=True)
            self.face_database = data["database"].item()
            print(f"[数据库] 加载 {len(self.face_database)} 个学生")
        else:
            print("[数据库] 未找到学生数据库，请先注册学生")

    def save_database(self):
        np.savez(FACE_DB_PATH, database=self.face_database)
        print(f"[数据库] 已保存 {len(self.face_database)} 个学生")

    def load_attendance_records(self):
        if os.path.exists(ATTENDANCE_RECORD_PATH):
            with open(ATTENDANCE_RECORD_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_attendance_records(self):
        with open(ATTENDANCE_RECORD_PATH, "w", encoding="utf-8") as f:
            json.dump(self.attendance_records, f, ensure_ascii=False, indent=2)

    # ---------- 特征提取与识别 ----------
    def _extract_embedding(self, face_img_bgr):
        face_rgb = cv2.cvtColor(face_img_bgr, cv2.COLOR_BGR2RGB)
        face_resized = cv2.resize(face_rgb, FACENET_INPUT_SIZE)
        tensor = torch.tensor(face_resized).permute(2, 0, 1).float() / 255.0
        tensor = tensor.unsqueeze(0).to(device)
        with torch.no_grad():
            emb = self.recognizer(tensor)
        return emb.cpu().numpy().flatten()

    def _recognize_student(self, embedding):
        if not self.face_database:
            return None, "未知", 0.0
        best_id = None
        best_sim = -1.0
        for sid, info in self.face_database.items():
            sim = np.dot(embedding, info["embedding"]) / (
                np.linalg.norm(embedding) * np.linalg.norm(info["embedding"])
            )
            if sim > best_sim:
                best_sim = sim
                best_id = sid
        if best_sim >= SIMILARITY_THRESHOLD:
            return best_id, self.face_database[best_id]["name"], best_sim
        else:
            return None, "未知", best_sim

    def register_student(self, student_id, student_name, face_img):
        embedding = self._extract_embedding(face_img)
        if embedding is not None:
            self.face_database[student_id] = {
                "name": student_name,
                "embedding": embedding,
            }
            self.save_database()
            print(f"[注册] 成功: {student_name} ({student_id})")
            return True
        else:
            print(f"[注册] 失败: {student_name}")
            return False

    # ---------- 批量注册（从 roster 目录读取） ----------
    def batch_register_from_roster(self):
        """扫描 roster 目录，自动注册所有 学号_姓名.扩展名 照片"""
        if not os.path.isdir(ROSTER_DIR):
            print(f"[错误] roster目录不存在: {ROSTER_DIR}")
            return

        image_files = [
            f
            for f in os.listdir(ROSTER_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
        ]
        if not image_files:
            print(f"[提示] roster目录中没有图片文件")
            return

        print(f"\n[批量注册] 发现 {len(image_files)} 张照片，开始注册...")
        success = 0
        for fname in image_files:
            # 解析文件名：学号_姓名.扩展名
            stem = Path(fname).stem
            parts = stem.split("_", 1)
            if len(parts) != 2:
                print(f"[跳过] 文件名格式错误: {fname}，应为 学号_姓名.扩展名")
                continue
            sid, name = parts[0], parts[1]

            img_path = os.path.join(ROSTER_DIR, fname)
            img = cv2.imread(img_path)
            if img is None:
                print(f"[跳过] 无法读取图片: {fname}")
                continue

            # 检测人脸
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes, _, scores = self.detector(rgb, target_size=TARGET_SIZE)
            valid = [
                (box, score)
                for box, score in zip(boxes, scores)
                if score >= CONFIDENCE_THRESHOLD
            ]
            if len(valid) == 0:
                print(f"[跳过] 未检测到人脸: {fname}")
                continue
            if len(valid) > 1:
                print(f"[警告] {fname} 含多张人脸，将使用面积最大的进行注册")
                valid.sort(
                    key=lambda x: (x[0][2] - x[0][0]) * (x[0][3] - x[0][1]),
                    reverse=True,
                )

            box = valid[0][0]
            x1, y1, x2, y2 = [int(v) for v in box]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img.shape[1], x2), min(img.shape[0], y2)
            face_crop = img[y1:y2, x1:x2]
            if face_crop.size == 0:
                print(f"[跳过] 人脸区域无效: {fname}")
                continue

            self.register_student(sid, name, face_crop)
            success += 1

        print(f"\n[批量注册] 完成，成功注册 {success} 人\n")

    # ---------- 核心处理：单帧图像 ----------
    def process_frame(self, frame_bgr):
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        boxes, _, scores = self.detector(rgb_frame, target_size=TARGET_SIZE)

        recognized_students = []
        for box, score in zip(boxes, scores):
            if score < CONFIDENCE_THRESHOLD:
                continue
            x1, y1, x2, y2 = [int(v) for v in box]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame_bgr.shape[1], x2), min(frame_bgr.shape[0], y2)
            if x2 <= x1 or y2 <= y1:
                continue
            face_crop = frame_bgr[y1:y2, x1:x2]
            if face_crop.size == 0:
                continue

            embedding = self._extract_embedding(face_crop)
            if embedding is None:
                continue

            student_id, student_name, similarity = self._recognize_student(embedding)
            recognized_students.append(
                {
                    "id": student_id,
                    "name": student_name,
                    "similarity": similarity,
                    "bbox": (x1, y1, x2, y2),
                }
            )

            # 绘制
            color = (0, 255, 0) if student_id else (0, 0, 255)
            label = f"{student_name} ({similarity:.2f})" if student_id else "Unknown"
            cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                frame_bgr, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )

        return frame_bgr, recognized_students

    # ---------- 考勤统计 ----------
    def mark_attendance(self, recognized_students, session_id=None):
        if session_id is None:
            session_id = datetime.now().strftime("%Y-%m-%d")
        if session_id not in self.attendance_records:
            self.attendance_records[session_id] = {
                "timestamp": datetime.now().isoformat(),
                "present_students": [],
            }
        present_ids = set(self.attendance_records[session_id]["present_students"])
        for stu in recognized_students:
            if stu["id"] and stu["id"] not in present_ids:
                present_ids.add(stu["id"])
        self.attendance_records[session_id]["present_students"] = list(present_ids)
        self.save_attendance_records()

        total = len(self.face_database)
        present_count = len(present_ids)
        absent_count = total - present_count
        return {
            "session_id": session_id,
            "total_students": total,
            "present_count": present_count,
            "absent_count": absent_count,
            "present_list": [self.face_database[sid]["name"] for sid in present_ids],
            "absent_list": [
                self.face_database[sid]["name"]
                for sid in self.face_database.keys()
                if sid not in present_ids
            ],
        }

    def get_attendance_report(self, session_id=None):
        if session_id is None:
            session_id = datetime.now().strftime("%Y-%m-%d")
        if session_id not in self.attendance_records:
            return f"暂无 {session_id} 的考勤记录"
        record = self.attendance_records[session_id]
        present_names = [
            self.face_database.get(sid, {}).get("name", sid)
            for sid in record["present_students"]
        ]
        absent_names = [
            self.face_database.get(sid, {}).get("name", sid)
            for sid in self.face_database.keys()
            if sid not in record["present_students"]
        ]
        report = f"""
=== {session_id} 考勤报告 ===
总人数: {len(self.face_database)}
实到: {len(record['present_students'])}
缺勤: {len(self.face_database) - len(record['present_students'])}
出勤率: {len(record['present_students'])/len(self.face_database)*100:.1f}%

实到名单: {', '.join(present_names) if present_names else '无'}
缺勤名单: {', '.join(absent_names) if absent_names else '无'}
"""
        return report

    def process_image(self, image_path, output_path=None, mark_attendance=False):
        """处理单张图片，支持无界面运行，直接打印缺勤名单"""
        if not os.path.exists(image_path):
            print(f"[错误] 图片不存在: {image_path}")
            return
        frame = cv2.imread(image_path)
        if frame is None:
            print(f"[错误] 无法读取图片: {image_path}")
            return

        print(f"[图片处理] 处理中: {image_path}")
        start = time.time()
        annotated_frame, recognized = self.process_frame(frame)
        elapsed = time.time() - start

        print(f"[图片处理] 检测到 {len(recognized)} 张人脸，耗时 {elapsed:.2f} 秒")
        for stu in recognized:
            if stu["id"]:
                print(f"  识别: {stu['name']} (相似度 {stu['similarity']:.2f})")
            else:
                print(f"  未知人脸 (最高相似度 {stu['similarity']:.2f})")

        # 统计并打印缺勤名单
        total_students = len(self.face_database)
        present_ids = set()
        for stu in recognized:
            if stu["id"]:
                present_ids.add(stu["id"])
        absent_ids = set(self.face_database.keys()) - present_ids

        print("\n========== 考勤统计 ==========")
        print(f"应到人数: {total_students}")
        print(f"实到人数: {len(present_ids)}")
        print(f"缺勤人数: {len(absent_ids)}")
        print(
            "出勤名单:",
            (
                ", ".join([self.face_database[sid]["name"] for sid in present_ids])
                if present_ids
                else "无"
            ),
        )
        print(
            "缺勤名单:",
            (
                ", ".join([self.face_database[sid]["name"] for sid in absent_ids])
                if absent_ids
                else "无"
            ),
        )
        print("==============================\n")

        if mark_attendance:
            stats = self.mark_attendance(recognized)
            print(
                f"[考勤更新] 已标记 {stats['present_count']}/{stats['total_students']} 人"
            )
            print(self.get_attendance_report())

        # 仅在图形界面下显示窗口
        if HAS_GUI:
            safe_imshow("识别结果", annotated_frame, wait_ms=3000)
        else:
            print("[提示] 无图形界面，未显示标注窗口")

        if output_path:
            cv2.imwrite(output_path, annotated_frame)
            print(f"结果已保存: {output_path}")


# ==================== 交互模式（简化，突出批量注册和识别） ====================
def image_mode(system):
    """图片识别模式，直接输出缺勤名单"""
    print("\n=== 图片考勤模式 ===")
    while True:
        path = input("图片路径 (输入 q 返回): ").strip()
        if path.lower() == "q":
            break
        if not os.path.exists(path):
            print("文件不存在")
            continue
        mark = input("是否将此图片计入考勤？(y/n): ").strip().lower() == "y"
        save = input("是否保存标注结果？(y/n): ").strip().lower() == "y"
        out_path = None
        if save:
            default = os.path.splitext(path)[0] + "_out.jpg"
            out_path = input(f"保存路径 (回车默认 {default}): ").strip() or default
        system.process_image(path, out_path, mark)


def camera_mode(system):
    """摄像头模式（仅在GUI环境有效）"""
    if not HAS_GUI:
        print("[错误] 当前无图形界面，无法使用摄像头模式")
        return
    print("\n=== 摄像头考勤模式 ===")
    print("操作: 's' 标记考勤, 'r' 查看今日报告, 'q' 退出")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    accumulated = {}
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        processed, students = system.process_frame(frame)
        for s in students:
            if s["id"]:
                accumulated[s["id"]] = {
                    "name": s["name"],
                    "similarity": s["similarity"],
                }
        cv2.putText(
            processed,
            f"Faces: {len(students)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )
        cv2.putText(
            processed,
            f"Accumulated: {len(accumulated)}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2,
        )
        cv2.imshow("教室考勤系统", processed)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("s"):
            if accumulated:
                to_mark = [
                    {"id": sid, "name": info["name"], "similarity": info["similarity"]}
                    for sid, info in accumulated.items()
                ]
                stats = system.mark_attendance(to_mark)
                print(
                    f"[考勤] 已标记 {stats['present_count']}/{stats['total_students']} 人"
                )
                accumulated.clear()
            else:
                print("未检测到任何学生，无法标记")
        elif key == ord("r"):
            print(system.get_attendance_report())
    cap.release()
    cv2.destroyAllWindows()


def register_mode(system):
    """学生注册入口：摄像头或照片"""
    print("\n=== 学生注册模式 ===")
    print("请选择注册方式:")
    print("  1. 摄像头实时拍摄")
    print("  2. 从照片文件注册")
    print("  3. 批量注册（从 roster 目录自动扫描）")
    choice = input("请输入数字 (1/2/3): ").strip()
    if choice == "1":
        if HAS_GUI:
            # 此处可调用原有的 register_by_camera 函数，为简洁略，可复用原代码
            print("摄像头注册功能请参考原代码或使用批量注册")
        else:
            print("无图形界面，无法使用摄像头注册")
    elif choice == "2":
        # 单张照片注册（可复用原 register_by_photo，此处简化）
        print("单张照片注册请使用批量注册功能（将照片放入 roster 目录）")
    elif choice == "3":
        system.batch_register_from_roster()
    else:
        print("无效选择")


def main():
    print("=" * 50)
    print("教室考勤系统 (YOLOv5-Face + FaceNet) 优化版")
    print("支持批量注册、SSH无界面运行、缺勤名单输出")
    print("=" * 50)
    system = ClassroomAttendanceSystem()
    while True:
        print("\n请选择模式:")
        print("  1. 摄像头考勤模式（需图形界面）")
        print("  2. 图片识别模式（单张多人照片，输出缺勤名单）")
        print("  3. 注册学生（推荐使用批量注册）")
        print("  4. 查看考勤报告")
        print("  5. 退出")
        choice = input("请输入数字 (1/2/3/4/5): ").strip()
        if choice == "1":
            camera_mode(system)
        elif choice == "2":
            image_mode(system)
        elif choice == "3":
            register_mode(system)
        elif choice == "4":
            date = input("请输入日期 (YYYY-MM-DD，直接回车查看今日): ").strip()
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            print(system.get_attendance_report(date))
        elif choice == "5":
            print("退出系统")
            break
        else:
            print("无效输入，请重新选择")


if __name__ == "__main__":
    main()
