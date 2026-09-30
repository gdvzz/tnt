---
title: 语音实验箱
layout: default
parent: aikit教具
nav_order: 10
# nav_exclude: true
---

# 语音实验箱
{: .no_toc }
`更新-260930` \| `发布-260930`

本文档描述 **语音实验箱** 的相关信息，用于快速熟悉和入门教具。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<!-- <details markdown="block">
  <summary>ℹ️ 更新</summary>

<span style="font-size:12px; color:#999">--- end ---</span>
</details> -->
## termux 快捷键

粘贴：Ctrl + Alt + V

复制：Ctrl + Alt + C


## 本地安装demo
<br>
以下以“AI外语助教”为例。

**1、termux环境配置**

在 termux 中执行以下命令：

```bash
# 1. 更新基础包
pkg update -y && pkg upgrade -y

# 2. 安装必要组件
pkg install proot-distro wget git nano -y

# 3. 安装Ubuntu系统 
# proot-distro install ubuntu # 国内网络连接超时
proot-distro install docker.1panel.live/library/ubuntu:24.04

# 4. 登录Ubuntu系统 
proot-distro login ubuntu

# 5. 更新Ubuntu源(在Ubuntu环境中执行) 
apt update && apt upgrade -y

# 6. 安装基础编译工具
apt install build-essential python3-pip python3-venv ffmpeg mecab -y

# 7. 创建虚拟环境
python3 -m venv gradio_env

# 8. 激活虚拟环境
source gradio_env/bin/activate

```

**2、Python依赖安装**

在激活的虚拟环境中执行:

```bash

pip install --upgrade pip

#安装前置
apt install mecab mecab-ipadic ffmpeg 

# 安装核心库
pip install gradio
pip install pydub ffmpeg-python gradio_client librosa noisereduce pydantic

# 安装语音处理相关
pip install mecab-python3 unidic-lite cutlet langid

# 安装其他依赖
pip install typing-extensions emoji deepspeed asyncio
```

**AI语音助手** 样例：

[aiapp.zip](./xpad.assets/aiapp.zip)


降低 gradio 版本。在虚拟环境中（gradio_env）执行：
```bash
pip install gradio==4.44.0
```

> 似乎有更多错误 <br>
> 恢复到新的gradio版本，略修改了程序

## 体验网址

AI语音助手<br>
https://172.18.144.18/plugin/frontend#/appview/oNbnIDhD?i=1

AI同声传译<br>
https://172.18.144.18/plugin/frontend#/appview/975WwGQ5?i=1

AI外语助教<br>
https://172.18.144.18/plugin/frontend#/appview/AJ62kgyj?i=1

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

<!--  -->
