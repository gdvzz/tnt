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
  <summary>✳️ 目录</summary>
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

1. **HwHiAiUser 用户登录开发板**

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

    先安装 CPU 版本的 PyTorch 和 torchvision。
    
    增加 `--index-url https://download.pytorch.org/whl/cpu` 是避免安装不必要的 nvidia 相关的包。

    ```bash
    pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    ```

    再安装其他可以一起安装的包。

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

    用 MobaXterm 软件传文件。请参考：[MobaXterm简要说明↗](https://tnt.gdvzz.com/aikit/mobaxtermug.html) \| 传文件

    或者在本地电脑敲命令传文件。请参考：[Linux常用操作↗](https://tnt.gdvzz.com/aikit/linuxug.html) \| scp 远程复制文件/目录

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

---

## 体验样例

### 训练模型
<br>
使用压缩包中的数据集，对CNN模型做训练。在开发板上执行 1个 epoch，大约需要 2 分钟左右。样例中 epochs = 5，因此建议先改小些，比如改成 1。

1. **先进入样例代码目录**

    ```bash
    cd ~/mnist0509/mnist_master
    ```

2. **并确保虚拟环境已激活**

    命令行提示符首部有 `(mnist0509)` 字样，即表示本次实验用虚拟环境已激活。如需激活，可执行以下命令：

    ```bash
    conda activate mnist0509
    ```

3. **（可选）修改 epochs 数字**

    修改 `train.py`，将 `epochs = 5` 改为 `epochs = 1`

    ```python
    ...
    def main():
        ...
        loss_fn = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        # epochs = 5
        epochs = 1   # 先改成 1 用于体验
        ...
    ```

4. **训练模型**

    ```bash
    python3 train.py
    ```

    ✴️ Python3.10 + 对应 PyTorch，完成 1 个 epoch 约需要 2 分钟。

### 推理验证
<br>
样例中的目录 `input` 有 0 ~ 9 共 10 张图片。可执行以下命令体验推理验证：

```bash
python3 test.py
```

### 产品化
<br>
增加 Web 界面。可在 Web 界面手写数字、要求识别，并得到识别结果。

1. **微调样例代码**

    修改 `serve.py` 的最后一行，改为 `app.run(host='0.0.0.0', port=5000)` 

    ```python
    ...
    if __name__ == '__main__':
        # app.run(port=5000)
        app.run(host='0.0.0.0', port=5000) # 可在本地电脑浏览器访问“开发板IP:5000”
    ```
2. **开发板上启动 Web 服务端**

    在开发板上执行以下命令：

    ```bash
    python3 serve.py
    ```

3. **本地电脑浏览器访问开发板**

    在本地电脑浏览器输入以下 **IP:端口** 访问

    - 昇腾开发板：`192.168.137.100:5000` 
    - 鲲鹏开发板：`192.168.137.100:5000` 

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>