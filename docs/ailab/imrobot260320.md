---
title: 大模型RestAPI编程开发-260320
layout: default
parent: AI实验课
nav_order: 260301
---

# 模型RestAPI编程开发-260320
{: .no_toc }
`更新-260319` \| `发布-260319`

本实验演示使用 Jetson 实验箱部署 OpenAI 兼容接口的大模型接口服务，使用该模型服务接口构建基于控制台的对话应用。

原理和代码解读，可参考 CG 平台相关说明。本文档主要描述操作相关。

登录 [CG平台↗](https://csonline.jiangnan.edu.cn/admin/index.jsp)

- 点击左上角 **我的课程**，选择 **NLP实验箱**
- 点击顶部水平导航栏的 **作业**，找到下方 **61724. 实验4-3：大模型RestAPI编程开发**，点击可进入

<!--  -->
<details open markdown="block">
  <summary>
    目录
  </summary>
  <!-- {: .text-delta } -->
- TOC
{:toc}
</details>

---

## 实验箱简介

和常见的台式机很相似。视觉实验箱的相关部件有：

- 主机。有个小小机箱，内部是英伟达开发板（Nvidia Jetson）。
- 屏幕。支持 HDMI 接口的屏幕，都可以通过 HDMI 线连接到 Jetson 开发板。
- 鼠标和键盘。常见的鼠标和键盘，通过 USB 连接 Jetson 开发板。
- 操作系统。Ubuntu，Linux 的发行版的一种。（常见操作系统有： Windows、MacOS、Linux，等）
- 机械臂。由 Jetson 开发板控制的一个外部设备。

--- 


## 上电开机

- 视觉实验箱配有 1 个电源，一端连实验箱，另一端插头插在桌子下面的插座上。
- 桌子下面有个带开关的的立方体插座。按下开关，电源指示灯亮，即表明接通电源。
- 稍等片刻可完成启动。视觉实验箱的机械臂站立起来，且屏幕显示 Ubuntu 的主界面，就启动完成。

---

## 熟悉 Linux 命令

请参考 [视觉实验-260304 \| 熟悉 Linux 命令↗](https://tnt.gdvzz.com/ailab/imrobot260304.html#%E7%86%9F%E6%82%89-linux-%E5%91%BD%E4%BB%A4)

---

## 安装 Ollama

### Ollama 简介

Ollama是一款面向大语言模型（LLM）的本地化部署与运行时管理框架，支持在个人计算设备或服务器端高效运行开源预训练模型。

其采用容器化架构实现模型的标准化封装与分发，通过动态量化技术优化内存占用，并提供与OpenAI API兼容的RESTful接口，便于集成至现有AI应用生态。

Ollama支持Llama、Qwen、DeepSeek等主流架构的模型仓库管理，具备异构计算资源调度能力，可基于CPU或GPU实现低延迟推理。

该工具广泛应用于数据隐私敏感场景的私有化部署、边缘计算环境下的离线推理及学术研究的模型微调与评测，为大规模语言模型的本地化应用提供了轻量级技术基座。

### 安装 Ollama 到 Jetson 开发板

使用开发板已有的 `jetson` 用户（初始密码：`yahboom`）执行以下操作。

**方法1（首选）**

```bash
mkdir ~/tmp26/03 # 创建临时目录，目录名字可随意去
cd ~/tmp26/03    # 切换到临时目录

# 将已下载的 ollama压缩包 从某个开发板复制到临时目录中
scp jetson@172.18.139.145:/home/jetson/tmp26/03/ollama.tar.gz .

# 解开压缩包
tar zxvf ollama.tar.gz

cd ollama_jetsonv5 # 切换到当前目录下的子目录（解压缩生成的）
sudo  mv ollama /usr/local/bin/    # 移动文件到目标目录
sudo  mv lib /usr/local/lib/ollama # 移动目录到目标目录

# 修改文件 ollama 的权限，所有用户都可执行 ollama
chmod a+x /usr/local/bin/ollama
```

> scp 命令最后有个点，表示复制到当前目录中。不要遗漏。

> Linux 文件权限 和 chmod 命令相关，可自行网上查找或与AI交流获得更多信息。


**方法2（其次）**

```bash
mkdir ~/tmp26/03 # 创建临时目录，目录名字可随意去
cd ~/tmp26/03    # 切换到临时目录

# 从网上下载 ollama 压缩包到临时目录中
wget https://pan.educg.net/f/voqt9/ollama.tar.gz

# 解开压缩包
tar zxvf ollama.tar.gz

cd ollama_jetsonv5 # 切换到当前目录下的子目录（解压缩生成的）
sudo  mv ollama /usr/local/bin/    # 移动文件到目标目录
sudo  mv lib /usr/local/lib/ollama # 移动目录到目标目录

# 修改文件 ollama 的权限，所有用户都可执行 ollama
chmod a+x /usr/local/bin/ollama
```

> 方法2 和 方法1 基本一致，除了 ollama 压缩包是用 wget 命令从网上下载的。

**方法3（备选）**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

> Ollama 官网安装指令。网络原因，不一定在实验室能成功。

---

## 启动qwen

1. 新启一个 **终端 Terminal**，在终端中执行以下命令：

    ```bash
    ollama serve          # 启动 API 服务（默认 11434 端口）
    ```

2. 再启一个 **终端 Terminal**，在终端中执行以下命令：

    ```bash
    ollama run qwen2.5:3b # 加载qwen2.5:3b量化模型，没有则下载
    ```

    > Jetson 开发板上若没有 qwen2.5:3b，会从网上下载。下载大约需要几分钟。

### ollama 常用管理

```bash
ollama list           # 查看已下载模型
ollama pull <模型名>   # 仅下载不运行
ollama rm <模型名>     # 删除本地模型
ollama ps             # 查看正在运行的模型进程
```

---

## 测试 Restful 接口

再启一个 **终端 Terminal**，在终端中执行以下命令：

```bash
curl --location --request POST "http://127.0.0.1:11434/v1/chat/completions" --header "Content-Type: application/json" --header "Authorization: Bearer EMPTY" --data-raw '{"model": "qwen2.5:3b", "messages":[{"role": "user", "content": "hi"}]}'
```

### 2.3 OpenAI兼容Restful接口

OpenAI兼容接口常用接口如下：

POST https://api.openai.com/v1/chat/completions

参数列表：

- model：必选；模型名称；要使用的模型的 ID；字符串
- message：必选；消息内容；要发送给大模型的消息数组，每条数据必须包含role和content字段；数组
- stream：可选；流式输出；是否启动流式输出；布尔；默认为false
- temperature：可选；采样温度；0 和 2 之间的采样温度。较高的值（例如 0.8）使输出更加随机，而较低的值（例如 0.2）使其更加焦虑和确定性；浮点数；默认值为1
- max_tokens：可选；可以在聊天完成中生成的最大数量的令牌；整数；默认值为null

返回：

- 返回一个聊天完成对象，或者如果请求是流式的，则返回一个流序列的聊天完成 chunk 对象。

---

## 