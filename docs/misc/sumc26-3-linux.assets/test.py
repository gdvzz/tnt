#!/usr/bin/env python3
"""
CIFAR-10 accuracy evaluation script
支持 Ascend NPU (torch-npu) / CUDA / CPU 三种后端。

昇腾 AIPRO20T 快速上手：
  1. 安装 CANN 工具包（与开发板固件版本匹配）
  2. pip install torch==2.1.0  torch_npu==2.1.0.post3   # 版本号以实际为准
  3. python eval_cifar10_npu.py --cifar-dir /path/to/cifar10 --pth model.pth
     （加 --half 可开启 FP16，NPU 上推理速度提升明显）
"""

import argparse
import pickle
import time
from pathlib import Path

import numpy as np
import torch

# ── Ascend NPU (torch-npu) ──────────────────────────────────────────────────
# 导入后 torch.npu 命名空间自动注册，其余代码无需感知 torch_npu 细节。
try:
    import torch_npu  # noqa: F401  # 注册 torch.npu 后端
    _NPU_AVAILABLE: bool = torch.npu.is_available()
except ImportError:
    _NPU_AVAILABLE = False

# ── CIFAR-10 常量 ───────────────────────────────────────────────────────────
CIFAR10_CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog",      "frog",       "horse", "ship", "truck",
]

CIFAR10_MEAN = np.array([0.4914, 0.4822, 0.4465], dtype=np.float32).reshape(1, 3, 1, 1)
CIFAR10_STD  = np.array([0.2023, 0.1994, 0.2010], dtype=np.float32).reshape(1, 3, 1, 1)


# ── 数据加载 ────────────────────────────────────────────────────────────────
def load_cifar10_test_batch(cifar_dir):
    cifar_dir = Path(cifar_dir)
    candidates = [
        cifar_dir / "test_batch",
        cifar_dir / "cifar-10-batches-py" / "test_batch",
    ]
    test_batch = next((p for p in candidates if p.is_file()), None)
    if test_batch is None:
        raise FileNotFoundError(
            "Cannot find CIFAR-10 test_batch. Expected one of:\n"
            + "\n".join(str(p) for p in candidates)
        )
    with test_batch.open("rb") as f:
        data = pickle.load(f, encoding="latin1")
    images = data["data"].reshape(-1, 3, 32, 32).astype(np.float32) / 255.0
    labels = np.asarray(data["labels"], dtype=np.int64)
    return images, labels, test_batch


def normalize_images(images: np.ndarray) -> np.ndarray:
    return (images - CIFAR10_MEAN) / CIFAR10_STD


# ── 设备工具 ────────────────────────────────────────────────────────────────
def resolve_device(device_str: str) -> torch.device:
    """
    解析目标设备字符串，当请求的加速器不可用时自动回退到 CPU。

    优先级：
      npu:N  →  如果 torch_npu 已安装且 NPU 可用则使用，否则 CPU
      cuda:N →  如果 CUDA 可用则使用，否则 CPU
      cpu    →  直接使用
    """
    ds = device_str.lower()
    if ds.startswith("npu"):
        if _NPU_AVAILABLE:
            return torch.device(device_str)
        print("[WARN] torch_npu 未安装或未检测到 NPU，回退到 CPU。")
        return torch.device("cpu")
    if ds.startswith("cuda"):
        if torch.cuda.is_available():
            return torch.device(device_str)
        print("[WARN] CUDA 不可用，回退到 CPU。")
        return torch.device("cpu")
    return torch.device(device_str)


def sync_device(device: torch.device) -> None:
    """阻塞直到指定设备上所有 kernel 执行完毕（用于精确计时）。"""
    if device.type == "cuda":
        torch.cuda.synchronize(device)
    elif device.type == "npu":
        # torch_npu 已将 synchronize 注入到 torch.npu 命名空间
        torch.npu.synchronize(device)
    # CPU 无需同步


# ── 模型加载 ────────────────────────────────────────────────────────────────
def torch_load_model(path: Path, device: torch.device):
    try:
        model = torch.load(path, map_location=device, weights_only=False)
    except TypeError:
        model = torch.load(path, map_location=device)
    if isinstance(model, dict):
        keys = ", ".join(model.keys())
        raise TypeError(
            "输入的 .pth 是 checkpoint dict，而非完整模型。"
            f"Keys: {keys}。请改用对应的 CModel_*.pth 文件。"
        )
    model.to(device)
    model.eval()
    return model


# ── 参数解析 ────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="在 Ascend NPU / CUDA / CPU 上评估 CIFAR-10 精度（PyTorch .pth 模型）。"
    )
    parser.add_argument(
        "--pth",
        default="records/saved/CModel_CIFAR10_Param_1.0197M_Scale_D_1_W_2_Index_41.pth",
        help="完整模型 .pth 路径（CModel_*.pth），不要传 ckpt_*.pth。",
    )
    parser.add_argument(
        "--cifar-dir",
        required=True,
        help="CIFAR-10 数据目录，内含 test_batch 或 cifar-10-batches-py/test_batch。",
    )
    parser.add_argument(
        "--device",
        default="npu:0",                  # ← 默认改为昇腾 NPU
        help="设备字符串：npu:0（昇腾）、cuda:0 或 cpu。",
    )
    parser.add_argument("--batch-size",   type=int, default=1,   help="推理批大小。")
    parser.add_argument("--limit",        type=int, default=0,
                        help="只评估前 N 张图片（0 表示全部）。")
    parser.add_argument("--topk",         type=int, default=5,   help="报告 Top-K 精度。")
    parser.add_argument("--print-freq",   type=int, default=500, help="进度打印间隔（样本数）。")
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="禁用 CIFAR-10 均值/标准差归一化。",
    )
    parser.add_argument(
        "--warmup",
        type=int, default=10,
        help="计时前的预热 batch 数（不影响精度统计）。",
    )
    parser.add_argument(
        "--half",
        action="store_true",
        help="使用 FP16 推理（NPU 上推荐开启，可显著提升吞吐）。",
    )
    return parser.parse_args()


# ── 主流程 ──────────────────────────────────────────────────────────────────
def main():
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    # 定位模型文件
    pth_path = Path(args.pth)
    if not pth_path.is_file():
        pth_path = repo_root / args.pth
    if not pth_path.is_file():
        raise FileNotFoundError(f"PyTorch 模型文件未找到：{args.pth}")

    if args.batch_size <= 0:
        raise ValueError("--batch-size 必须为正整数。")

    # 解析设备
    device = resolve_device(args.device)

    # 加载数据 & 预处理
    load_start = time.perf_counter()
    images, labels, test_batch = load_cifar10_test_batch(args.cifar_dir)
    if not args.no_normalize:
        images = normalize_images(images)
    images = np.ascontiguousarray(images, dtype=np.float32)

    if args.limit > 0:
        images = images[: args.limit]
        labels = labels[: args.limit]

    total = len(labels)
    if total == 0:
        raise ValueError("没有可评估的 CIFAR-10 样本。")

    # 加载模型
    model = torch_load_model(pth_path, device)
    if args.half:
        model = model.half()          # FP16：NPU 上可大幅提速

    load_time = time.perf_counter() - load_start

    dtype_str = "FP16" if args.half else "FP32"
    print("=" * 55)
    print(f"模型文件   : {pth_path}")
    print(f"测试集     : {test_batch}")
    print(f"样本数     : {total}")
    print(f"归一化     : {not args.no_normalize}")
    print(f"设备       : {device}  (NPU 可用: {_NPU_AVAILABLE})")
    print(f"数据类型   : {dtype_str}")
    print(f"批大小     : {args.batch_size}")
    print("=" * 55)

    # 将 numpy 数组转为目标设备 Tensor，支持 FP16
    def to_tensor(np_arr: np.ndarray) -> torch.Tensor:
        t = torch.from_numpy(np_arr).to(device)
        return t.half() if args.half else t

    correct1    = 0
    correctk    = 0
    infer_times: list[float] = []
    last_logits = None
    wall_start  = time.perf_counter()

    with torch.no_grad():
        # ── 预热 ─────────────────────────────────────────────────────────
        n_batches = (total + args.batch_size - 1) // args.batch_size
        warmup_batches = min(args.warmup, n_batches)
        print(f"预热中（{warmup_batches} 个 batch）…")
        for i in range(warmup_batches):
            s, e = i * args.batch_size, min((i + 1) * args.batch_size, total)
            model(to_tensor(images[s:e]))
        sync_device(device)
        print("预热完成，开始评估…\n")

        # ── 评估循环 ──────────────────────────────────────────────────────
        eval_start = time.perf_counter()
        for start in range(0, total, args.batch_size):
            end = min(start + args.batch_size, total)
            x = to_tensor(images[start:end])
            y = torch.from_numpy(labels[start:end]).to(device)

            sync_device(device)
            t0     = time.perf_counter()
            logits = model(x)
            sync_device(device)
            batch_time = time.perf_counter() - t0
            infer_times.extend([batch_time / (end - start)] * (end - start))

            k    = min(args.topk, logits.shape[1])
            pred = torch.topk(logits, k=k, dim=1).indices
            correct1 += int((pred[:, 0] == y).sum().item())
            correctk += int((pred == y.view(-1, 1)).any(dim=1).sum().item())
            last_logits = logits[-1].detach().float().cpu().numpy()

            processed = end
            if args.print_freq > 0 and (processed % args.print_freq == 0 or processed == total):
                top1_r = correct1 * 100.0 / processed
                topk_r = correctk * 100.0 / processed
                avg_ms = np.mean(infer_times) * 1000.0
                print(
                    f"[{processed:>6}/{total}]  "
                    f"top1={top1_r:.2f}%  top{args.topk}={topk_r:.2f}%  "
                    f"avg={avg_ms:.3f} ms/sample"
                )

        sync_device(device)
        eval_time = time.perf_counter() - eval_start

    wall_time   = time.perf_counter() - wall_start
    infer_arr   = np.asarray(infer_times, dtype=np.float64)
    top1  = correct1 * 100.0 / total
    topk  = correctk * 100.0 / total

    print("")
    print("─" * 45)
    print("评估结果")
    print(f"  Top-1 精度  : {top1:.2f}%  ({correct1}/{total})")
    print(f"  Top-{args.topk} 精度  : {topk:.2f}%  ({correctk}/{total})")
    print("")
    print("计时统计")
    print(f"  数据加载 & 预处理 : {load_time:.3f} s")
    print(f"  评估循环耗时      : {eval_time:.3f} s")
    print(f"  总墙钟时间        : {wall_time:.3f} s")
    print(f"  吞吐量            : {total / eval_time:.2f} samples/s")
    print(f"  推理均值 : {infer_arr.mean()               * 1000:.3f} ms/sample")
    print(f"  推理 p50 : {np.percentile(infer_arr, 50)   * 1000:.3f} ms/sample")
    print(f"  推理 p90 : {np.percentile(infer_arr, 90)   * 1000:.3f} ms/sample")
    print(f"  推理 p99 : {np.percentile(infer_arr, 99)   * 1000:.3f} ms/sample")
    print(f"  推理最小 : {infer_arr.min()                * 1000:.3f} ms/sample")
    print(f"  推理最大 : {infer_arr.max()                * 1000:.3f} ms/sample")
    print("─" * 45)

    best = int(np.argmax(last_logits))
    print(f"\n最后一张图片预测：class={best}  name={CIFAR10_CLASSES[best]}")


if __name__ == "__main__":
    main()