---
title: 视觉实验-260304
layout: default
parent: AI实验课
nav_order: 2601
---

# 视觉实验-260304
{: .no_toc }
`更新-260301` \| `发布-260301`

本次实验用视觉实验箱体验 3 个视觉功能：

- 76285 实验1-3：面部检测 
- 76286 实验1-4：人脸检测
- 76287 实验1-5：手势识别

原理和代码解读，可参考 CG 平台相关说明。本文档主要描述操作相关的说明。

<!--  -->
<details open markdown="block">
  <summary>
    目录
  </summary>
  {: .text-delta }
- TOC
{:toc}
</details>

---

## 实验箱简介

和常见的台式机一样。视觉实验箱的相关部件：

- 主机。也是有个小小机箱，内部是英伟达开发板（Nvidia Jetson）。
- 屏幕。通过 HDMI 线连接 Jetson 开发板。
- 鼠标和键盘。通过 USB 连接 Jetson 开发板。
- 操作系统。Ubuntu。Linux 的发行版的一种。（常见操作系统有： Windows、MacOS、Linux，等）
- 机械臂。由 Jetson 开发板控制的一个外部设备。

---

## 上电开机

- 视觉实验箱配有 1 个电源，一端连视觉实验箱，一端插头插在桌子下面的插座上。
- 可以看到电源插在桌子下面的正方体的插座上，有个开关。按下开关，指示灯亮，即表明上电了。
- 稍等片刻可完成启动。视觉实验箱的机械臂站立起来，且屏幕显示 Ubuntu 的主界面，就启动完成了。

---

## 连接USB摄像头

1. 先将机械臂的摄像头的 USB 连接线，从 Jetson 开发板上拔下来。
2. 然后将桌子上的单目摄像头（海康 hikvision）的 USB 连接线，插入实验箱的 USB 扩展坞中。
3. 启动 **终端 Terminal** App [^1]，在终端中执行 `cheese` 命令，可在弹出的窗口中看到图像，即表明摄像头能正常工作。

说明：也可以用机械臂的摄像头做本次几个实验。但该摄像头是固定在机械臂顶部的，就是不大方便而已。

---

## Python环境准备

### 为啥需要 Conda [^2]

Python是一种有特别多用处的计算机语言，可以用来做网页开发、数据分析以及AI等几乎大多数事情。每一个目的都需要特定的“包（packages）”。

与此同时，不仅会用到不同包的，甚至用到的Python版本都是不一样的。

问题是，你只有一台电脑，不可能为了新作一个项目就需要买一台新电脑......因此，我们通过“虚拟环境”来完成同一台电脑 开发管理多个项目的事情。我们可以针对具体的项目、逐一对应地开发虚拟环境。可以用多个虚拟环境来做多个数据开发、多个虚拟环境来做网页开发的事情ect.。

因此，在做不同的python项目，用到不同包、不同python版本时，虚拟环境的作用就出来了。

在python官网下载python，与此同时就会下载pip（Python integrated package managemer）（所以顾名思义，pip的目的就是用来管理包）；如果想要管理一台电脑上的多个环节，那就可以下载virtualenv，帮助我们管理虚拟环境（但也并不是说管理虚拟环境只有这一个工具）。

如果想用python，也不一定必须要在python官网下载，替代方案是：下载Ananconda（Anaconda 和 Python 是“包含关系”，Anaconda 包含了 Python）。在下载Anaconda（或者是miniconda）后，Conda就会装在我们的电脑系统上。 Conda既可以做包的管理，也可以管理虚拟环境。（PS：miniconda可以理解为轻量化的Anaconda；miniconda通常在终端操作，Anaconda通常是图形化页面）

那 pip 和 venv 还用不用？

- Pip 是 Python 官方的包管理工具，更“原生”，适合轻量项目
- Conda 更适合安装大型包和管理多个项目的环境
- 二者可以搭配使用：Conda 管环境，pip 装特定包



<!-- 采用 conda 创建 Python 虚拟环境。关于 conda，可参考 B 站视频：15分钟彻底搞懂！Anaconda Miniconda conda-forge miniforge Mamba [链接↗](https://www.bilibili.com/video/BV1Fm4ZzDEeY)。

采用 conda 创建所需的 Python 虚拟环境，可以确保实验环境干净（不出未预期错误），同时可不污染开发板现有环境。 -->

### 第1步：安装 conda

在开发板上启动 **终端 Terminal** App[^1]，然后输入 `conda` 并回车。执行后如果屏幕提示“命令没有找到”之类的，则表明尚未安装，请参考如下命令先安装 Conda。如果已经安装了 Conda，请跳到第2步。

```bash
mkdir ~/tmp2603 # 创建临时目录（目录名随意取）
cd ~/tmp2603    # 切换到临时目录
pwd             # 显示当前目录

# 从科大镜像下载安装包
wget https://mirrors.ustc.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-aarch64.sh

# 安装过程中，请仔细阅读提示。并在询问“是否初始化Miniforge3”时输入 yes。
bash Miniforge3-Linux-aarch64.sh

# 安装完成后，关闭并重新打开终端，或者执行以下命令使配置生效：
source ~/.bashrc

# 之后，你的命令行前会出现 (base) 字样，表示基础环境已激活。
```

### 第2步：创建虚拟环境

1. 在终端中[^1]执行以下 `conda create` 命令创建 Python3.9 虚拟环境。

    ```bash
    conda create -n pye39 python=3.9
    ```
    
    pye39 是给虚拟环境取的名字，方便识别，可以是其他名字。

2. 在终端中[^1]执行以下 `conda activate` 命令激活刚创建的虚拟环境。

    ```bash
    (base) jetson@jetson-Yahboom:~$ conda activate pye39
    (pye39) jetson@jetson-Yahboom:~$ python3 --version
    Python 3.9.23 # 屏幕显示的确是 Python3.9
    ```

    - pye39 是要激活的虚拟环境的名字。激活后可以看到命令行提示符头部已改为 `(pye39)`，表示已激活该虚拟环境。
    - 可以在该虚拟环境中执行 `python3 --version`，可以看到屏幕显示的确是 Python3.9。
    - $ 之前的是命令行提示符，仅为说明激活前后的变化。$ 之后的才是要执行的命令。

### 第3步：在虚拟环境中安装Python包

在终端中[^1]，依次执行以下 `pip3 install` 命令，安装本次实验所需的 Python包到创建的虚拟环境中。

```bash
(pye39) jetson@jetson-Yahboom:~$ pip3 install mediapipe==0.10.9
(pye39) jetson@jetson-Yahboom:~$ pip3 install opencv-python==4.12.0.88
(pye39) jetson@jetson-Yahboom:~$ pip3 install numpy==2.0.2
```

相关 Python包安装完成后，可以依次执行以下 `pip3 list | grep` 命令检查的确安装完成。

```bash
pip3 list | grep mediapipe
mediapipe 0.10.9 # 屏幕显示

pip3 list | grep opencv-python
opencv-python 4.12.0.88 # 屏幕显示

pip3 list | grep numpy
numpy 2.0.2 # 屏幕显示
```

- $ 之前的是命令行提示符，头部是当前激活的虚拟环境名。$ 之后的才是要执行的命令。
- 一定要把相关的 Python 包安装到对应的虚拟环境中。不能安装到其他虚拟环境（比如 base）或非虚拟环境。否则后续执行实验样例代码时，会报错“xx 找不到”。
- 和 CG 平台上要求的 Python 版本不一致（本文-3.9，CG-3.8），相关包的版本也不完全一样。可尝试参考本文的版本。

✅ 至此 Python 环境准备已完成。如何查看虚拟环境列表、激活/去激活、删除虚拟环境，请参考 [conda常用命令](#conda常用命令)。

---

## 下载解压样例代码

Python环境准备好后，就可以下载解压样例代码到 Jetson 开发板上。

1. 下载 zip 压缩包

    样例代码下载链接如下：
    
    - [76285. 实验1-3：面部检测 - face_mesh.zip](./imrobot260304.assets/face_mesh.zip)
    - [76286. 实验1-4：人脸检测 - haar_detection.zip](./imrobot260304.assets/haar_detection.zip)
    - [76287. 实验1-5：手势识别 - gesture_recognizer.zip](./imrobot260304.assets/gesture_recognizer.zip)
    
    样例代码也可从 CG 平台相关链接下载。CG 平台下载的 zip 包的名字是一长串数据字符，可从文件的时间确认哪个是哪个。


2. 解压

    在 Jetson 开发板上通过 Firefox 浏览器下载，默认存放在用户家目录（HOME目录）的 Downloads 子目录下。按 CG 平台手册建议，先新建 exp 子目录，再将样例代码从 Downloads 子目录移动到 exp 子目录。

    ```bash
    mkdir ~/exp                                 # 家目录下新建 exp 子目录
    mv ~/Downloads/face_mesh.zip ~/exp          # zip 包移动到 exp 子目录
    mv ~/Downloads/haar_detection.zip ~/exp
    mv ~/Downloads/gesture_recognizer.zip ~/exp
    ```

    解压 3 个 zip 包

    ```bash
    cd ~/exp # 先切换到 exp 目录
    unzip -oq face_mesh.zip -d ./  # 再执行 unzip解压
    unzip -oq haar_detection.zip -d ./
    unzip -oq gesture_recognizer.zip -d ./
    ```

    执行 `ls -l` 目录查看解压结果。应该有 3 个目录和 3 个 zip 文件。

    ```bash
    (pye39) jetson@jetson-Yahboom:~/exp$ ls -l
    face_mesh  gesture_recognizer  haar_detection  face_mesh.zip  gesture_recognizer.zip  haar_detection.zip # 屏幕显示应该有 3 个目录和 3 个 zip 文件
    ```
---

## 体验视觉功能

在 Jetson 开发板上启动 **终端 Terminal** App[^1]，并激活本实验所需的 Python 虚拟环境（请参考 [conda常用命令](#conda常用命令)）。然后可体验以下视觉功能：面部检测，人脸检测，手势识别。

**提示：** 在终端上输入命令时可用 `tab` 键文字以加快输入[^4]

### 面部检测 

1. 确保已激活本次实验所需 Python 虚拟环境

    如未激活或不确定，请参考 [conda常用命令](#conda常用命令)。

2. 执行 `Python3 main.py` 启动功能

    ```bash
    cd ~/exp
    cd face_mesh
    python3 main.py
    ```

    程序启动后会自动打开摄像头，实时检测画面中的人脸，并在窗口中显示检测结果。窗口被分为左右两部分：

    - 左侧窗口: 原始的摄像头画面（已做镜像翻转），并叠加了检测到的人脸轮廓线（绿色线条）和所有468个关键点（红色微小圆点）。左上角实时显示帧率（FPS）。

    - 右侧窗口: 在纯黑背景上只显示人脸网格和关键点，可以更清晰地观察细节。

    - 按 q 键（或 ctrl + c）退出程序。

    <br>

    更多信息请参考 CG 平台之“76285 实验1-3：面部检测”。

### 人脸检测 

1. 确保已激活本次实验所需 Python 虚拟环境

    如未激活或不确定，请参考 [conda常用命令](#conda常用命令)。

2. 执行 `Python3 main.py` 启动功能

    ```bash
    cd ~/exp
    cd haar_detection
    python3 main.py
    ```

    程序启动后会自动打开摄像头，并进入默认的“人脸检测”模式。你可以通过键盘进行交互：

    - 按 f 键: 在三种模式间循环切换：face (仅人脸检测), eye (仅眼睛检测), face_eye (同时检测人脸和眼睛)。
    - 按 q 键（或 ctrl + c）退出程序。

    窗口中会实时显示检测结果：

    - 人脸: 会被一个带有装饰性边角的紫色矩形框標出。
    - 眼睛: 会被一个红色的圆形框標出。
    - 左上角: 实时显示当前的FPS（帧率）和检测模式(Mode)。

    <br>

    更多信息请参考 CG 平台之“76286 实验1-4：人脸检测”。

### 手势识别 

1. 确保已激活本次实验所需 Python 虚拟环境

    如未激活或不确定，请参考 [conda常用命令](#conda常用命令)。

2. 执行 `Python3 main.py` 启动功能

    ```bash
    cd ~/exp
    cd gesture_recognizer
    python3 main.py
    ```

    程序启动后会自动打开摄像头，实时检测画面中的单只手并识别其手势。窗口被分为左右两部分：

    - 左侧窗口: 原始的摄像头画面（已做镜像翻转），并叠加了检测到的手部骨架（绿色线条）和关键点（红色圆点）。左上角会实时显示识别出的手势名称（如 "Five", "OK", "Thumb_up"），右上角显示FPS（帧率）。
    - 右侧窗口: 在纯黑背景上只显示手部骨架，方便观察。
    - 按 q 键（或 ctrl + c）退出程序。

    <br>

    更多信息请参考 CG 平台之“76287 实验1-5：手势识别”。

<!-- - 在开发板上打开 firefox 浏览器，访问 tnt.gdvzz.com  -->

<!--  -->
---

## 附录之参考信息

[^1]: 在 Ubuntu 主界面左侧导航栏找到对应的 App，或者在顶部搜索栏输入 App 的名字查找。
[^4]: 按 `tab` 键可补齐文字，加入输入。假定当前目录下有 3 个子目录（face_mesh，gesture_recognizer，haar_detection），输入 `cd ges` 后按 `tab` 键，则补齐为 `cd gesture_recognizer/`。
[^2]: [Python中的Anaconda（Conda）是什么？为什么需要它？](https://zhuanlan.zhihu.com/p/1919115719272010247)；知乎；2025-06-19
[^3]: [15分钟彻底搞懂！Anaconda Miniconda conda-forge miniforge Mamba](https://www.bilibili.com/video/BV1Fm4ZzDEeY)；B站；2025-08-07

### conda常用命令

- 显示虚拟环境列表

    ```bash
    conda env list
    ```

- 激活/去激活某个虚拟环境
    
    执行如下命令可激活某个虚拟环境：

    ```bash
    conda activate 虚拟环境名
    ```

    比如要激活虚拟环境名称叫 abc，则执行 `conda activate abc`。执行成功后，命令行提示符头部会显示`(abc)`。

    在某个虚拟环境中，执行如下命令可去激活该虚拟环境：

    ```bash
    conda deactivate
    ```

    假定当前在虚拟环境 abc 中。执行上述去激活命令后，命令行提示符头部的 `(abc)` 会变化：消失（回到非虚拟环境）；或者显示 `(base)`（假定是从 `(base)` 虚拟环境执行 `conda activate abc` 激活 abc 虚拟环境的）

- 删除虚拟环境

    执行 `conda remove` 命令可删除虚拟环境：

    ```bash
    conda remove -n 虚拟环境名 --all
    ```

    比如执行 `conda remove -n myenv --all`，可以 remove all packages from environment `myenv` and the environment itself。


<!--  -->
<span style="font-size:12px; color:#999">THE END</span>