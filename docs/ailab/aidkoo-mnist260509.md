---
title: 手写数字识别-260509
layout: default
parent: ailab实验课
nav_order: -260509
# nav_exclude: true
---

# 手写数字识别-260509
{: .no_toc }
`更新-260506` \| `发布-260506`

<!--  -->
<!-- <details open markdown="block">
  <summary>
    目录
  </summary>
- TOC
{:toc}
</details> -->

<!-- <details>
    <summary>ℹ️ 更新历史</summary>
<br>

**260501：新增3个岗位**

- [产品运营-音乐方向](#产品运营-音乐方向)
- [前端开发工程师](#前端开发工程师)
- [移动端开发工程师-Android](#移动端开发工程师-android)

</details> -->

<details markdown="block">
  <summary>✳️ 目录1</summary>
- TOC
{:toc}
</details>

<details markdown="block">
    <summary>✳️ 目录2</summary>
- TOC
{:toc}
</details>

<details markdown="block">
    <summary>
        ✳️ 目录3
    </summary>
- TOC
{:toc}
</details>

---

## 实验简介



---

## 实验目的

---

## 座位设备对应

---

## 上电开机

---

## 连接外网
<br>
开发板上电开机后，先让开发板连接外网，即能访问互联网。后续创建本次实验所需的 Python 虚拟环境，需要开发板能访问外网。开发板如何连接外网，请参考：

- 昇腾开发板：[连接外网↗](https://tnt.gdvzz.com/aikit/aidk.html#nets)
- 鲲鹏开发板：[连接外网↗](https://tnt.gdvzz.com/aikit/dkoo.html#nets)

---

## 创建环境
<br>
创建本次实验所需环境，主要包括：
- 创建 Python 虚拟环境。在虚拟环境中开展实验，可做到和开发板的其他项目互不影响。
- 在 Python 虚拟环境中安装相关包。

1. **HwHiAiUser 登录开发板**

    用 MobeXterm 软件登录，或在本地电脑执行：

    ```bash
    ssh HwHiAiUser@192.168.137.100 # 昇腾
    ssh HwHiAiUser@192.168.137.200 # 鲲鹏
    ``` 

    或者已用 root 登录开发板，则切换到 HwHiAiUser：

    ```bash
    su - HwHiAiUser
    ```

    ✳️ 在权限满足实验要求的前提下，尽量不用超级用户 root 做实验。

1. **用 conda 创建 Python 3.10 的虚拟环境：**

    ```bash
    conda create -n mnist0509 python=3.10
    ```

    ✳️ mnist0509 是虚拟环境的名字。可以是其他名字。本文以 mnist0509 为例。

    ✳️ Python 3.10 可以完成本次实验。更高版本或更低版本，可能也可以完成本次实验。

2. **激活刚创建的虚拟环境：**

    ```bash
    conda activate mnist0509
    ```

3. **在虚拟环境中安装相关包：**

    先安装 CPU 版本的 PyTorch 和 torchvision。增加 `--index-url https://download.pytorch.org/whl/cpu` 是避免安装不必要的 nvidia 相关的包。

    ```bash
    pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    ```

    以及其他可以一起安装的包。

    ```bash
    pip3 install "numpy<2" flask opencv-python
    ```

---

## 获取源码
<br>
下载样例压缩包（源码+数据），并上传开发板，然后解压缩。

1. **下载样例压缩包**：[江大云盘链接↗]

    压缩包文件名是：demomnist.zip

2. **在开发板上新建实验用目录：**

    ```bash
    mkdir ~/mnist0509
    ```

    > 该实验目录的完整路径，应该是：`/home/HwHiAiUser/mnist0509`

3. **上传压缩包到开发板的实验目录中**

    用 MobaXterm 软件传文件。请参考：[MobaXterm简要说明](https://tnt.gdvzz.com/aikit/mobaxtermug.html) → **传文件**

    或者在本地电脑敲命令传文件。请参考：[Linux常用操作](https://tnt.gdvzz.com/aikit/linuxug.html) → **scp 远程复制文件/目录**

4. **在开发板上解压缩**

    先进入实验目录：

    ```bash
    cd ~/mnist0509
    ```

    再解压缩：

    ```bash
    unzip demomnist.zip
    ```

    解压缩后生成子目录 mnist_master，完整路径应该是：`/home/HwHiAiUser/mnist0509/mnist_master`。


<!--  -->
<span style="font-size:12px; color:#999">THE END</span>