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

```bash
conda create -n pye39 python=3.9
```

```bash
(base) jetson@jetson-Yahboom:~$ conda activate pye39
(pye39) jetson@jetson-Yahboom:~$ python3 --version
Python 3.9.23
```

```bash
pip3 list | grep mediapipe
pip3 list | grep opencv-python
pip3 list | grep numpy
```

```bash
pip3 install mediapipe==0.10.9
pip3 install opencv-python==4.12.0.88
pip3 install numpy==2.0.2
```

---

## 下载解压样例代码

样例代码下载链接如下：

- [76285. 实验1-3：面部检测 - face_mesh.zip](./imrobot260304.assets/face_mesh.zip)
- [76286. 实验1-4：人脸检测 - haar_detection.zip](./imrobot260304.assets/haar_detection.zip)
- [76287. 实验1-5：手势识别 - gesture_recognizer.zip](./imrobot260304.assets/gesture_recognizer.zip)


```bash
mkdir ~/exp
mv ~/Downloads/face_mesh.zip ~/exp
mv ~/Downloads/haar_detection.zip ~/exp
mv ~/Downloads/gesture_recognizer.zip ~/exp
```

```bash
cd ~/exp
unzip -oq face_mesh.zip -d ./
unzip -oq haar_detection.zip -d ./
unzip -oq gesture_recognizer.zip -d ./
```

```bash
(pye39) jetson@jetson-Yahboom:~/exp$ ls --group-directories-first
face_mesh  gesture_recognizer  haar_detection  face_mesh.zip  gesture_recognizer.zip  haar_detection.zip
```
---

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


Remove all packages from environment `myenv` and the environment itself::

    conda remove -n myenv --all

## 

##

conda create -n pye39 python=3.9

pip3 list | grep mediapipe
pip3 list | grep opencv-python
pip3 list | grep numpy

pip3 install mediapipe==0.10.9
pip3 install opencv-python==4.12.0.88


(pye39) jetson@jetson-Yahboom:~$ pip3 install opencv-python==4.12
ERROR: Ignored the following yanked versions: 3.4.11.39, 3.4.17.61, 4.4.0.42, 4.4.0.44, 4.5.4.58, 4.5.5.62, 4.7.0.68
ERROR: Could not find a version that satisfies the requirement opencv-python==4.12 (from versions: 3.4.0.14, 3.4.10.37, 3.4.11.41, 3.4.11.43, 3.4.11.45, 3.4.13.47, 3.4.14.53, 3.4.15.55, 3.4.16.57, 3.4.16.59, 3.4.17.63, 3.4.18.65, 4.3.0.38, 4.4.0.40, 4.4.0.46, 4.5.1.48, 4.5.2.54, 4.5.3.56, 4.5.4.60, 4.5.5.64, 4.6.0.66, 4.7.0.72, 4.8.0.74, 4.8.0.76, 4.8.1.78, 4.9.0.80, 4.10.0.82, 4.10.0.84, 4.11.0.86, 4.12.0.88, 4.13.0.90, 4.13.0.92)
ERROR: No matching distribution found for opencv-python==4.12

pip3 install mediapipe==0.10.9
pip3 install opencv-python==4.12.0.88
pip3 install numpy==2.0.2


(pye39) jetson@jetson-Yahboom:~$ conda activate pye38
(pye38) jetson@jetson-Yahboom:~$ pip3 list | grep mediapipe
mediapipe                     0.10.5
(pye38) jetson@jetson-Yahboom:~$ pip3 list | grep opencv-python
(pye38) jetson@jetson-Yahboom:~$ pip3 list | grep numpy
numpy                         1.19.5



下载 face_mesh.zip。
在 ~/Download 中不是这个名字。按文件时间可以找到。

pip3 install pyparsing
pip3 install cycler

## 待合入

- cheese。看看摄像头是否OK
- 拔掉机械臂色摄像头。接上海康摄像头
- 没有conda，则安装conda
