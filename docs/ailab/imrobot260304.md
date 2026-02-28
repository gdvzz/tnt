---
title: 视觉实验-260304
layout: default
parent: AI实验课
nav_order: 2601
---

# 视觉实验-260304
{: .no_toc }

<details open markdown="block">
  <summary>
    目录
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

---

## 环境准备

- Python 3.8
- mediapipe 0.10.11
- opencv-python 4.12.0.88
- numpy 1.24.4

执行以下命令创建 Python 3.8 的虚拟环境：

```bash
conda create -n pye38 python=3.8
```

激活 Python3.8 虚拟环境

```bash
conda env list                 
conda activate pye38
(pye38) jetson@jetson-Yahboom:~$ 
(pye38) jetson@jetson-Yahboom:~$ python3 --version
Python 3.8.20
```

```bash
(pye38) jetson@jetson-Yahboom:~$ pip3 install mediapipe==0.10.11
(pye38) jetson@jetson-Yahboom:~$ pip3 install opencv-python==4.12.0.88
(pye38) jetson@jetson-Yahboom:~$ pip3 install numpy==1.24.4
```
原版本


- mediapipe 0.10.5 
- opencv-python 4.7.0.68 
- numpy 1.23.2

- mediapipe 0.10.11 -- 找不到该版本
- opencv-python 4.12.0.88 -- 安装了，但有一堆依赖报错
- numpy 1.24.4 -- 安装了，但有一堆依赖报错

##

下载 face_mesh.zip。
在 ~/Download 中不是这个名字。按文件时间可以找到。

pip3 install pyparsing
pip3 install cycler

## 待合入

- cheese。看看摄像头是否OK
- 拔掉机械臂色摄像头。接上海康摄像头
- 没有conda，则安装conda
