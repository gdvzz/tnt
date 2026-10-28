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


运行后报错，修改后版本：<br>
[appv2.py](./xpad.assets/appv2.py)

## 体验网址

[AI语音助手↗](https://172.18.144.18/plugin/frontend#/appview/975WwGQ5?i=1)
[AI同声传译↗](https://172.18.144.18/plugin/frontend#/appview/975WwGQ5?i=1)
[AI外语助教↗](https://172.18.144.18/plugin/frontend#/appview/AJ62kgyj?i=1)

---

1、下载 zerotermux。从官网 zerotermux.dev

2、termux-setup-storage ()

3、termux-change-repo 改成清华镜像源头

# 给 zt 自动启动 sshd
<!--  -->
pkg install termux-services
<!-- pkg install openssh-server -->
pkg install openssh

xpad关闭zt，再运行zt

执行：sv-enable sshd

passwd # 设置口令，ssh用
whoami # 得到用户名，类似 u0_axxx，ssh用
ifconfig # ip地址

本地电脑ssh到xpad 的zt：
ssh <用户名>@<平板IP> -p 8022

ssh -p 8022 u0_a296@192.168.31.211

# 1. 更新基础包
pkg update -y && pkg upgrade -y

问的问题，都是回复 default，即按 回车

# 2. 安装必要组件
<!-- pkg install proot-distro wget git nano -y --> 
<!-- nano 有了 -->
pkg install proot-distro wget git vim -y



=== ssh 到xpad 上操作 ====

<!-- proot-distro install ubuntu:22.04 -->
proot-distro install docker.1panel.live/library/ubuntu:22.04  # 很快

# 4. 登录Ubuntu系统 
proot-distro login ubuntu


=== ubuntu 里面执行一下命令 ===

备份

```bash
cp /etc/apt/sources.list /etc/apt/sources.list.bak 
```

换源

```bash
cat > /etc/apt/sources.list << 'EOF'
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu-ports/ jammy-security main restricted universe multiverse
EOF
```

更新

```bash
apt-get update -o "Acquire::https::Verify-Peer=false" 
apt-get install -y ca-certificates --no-install-recommends -o "Acquire::https::Verify-Peer=false"
apt upgrade -y
```

<!-- 安装证书
apt install ca-certificates

update-ca-certificates # 刷新证书库（非常关键，让系统信任新证书）（可能是多余的） -->

安装必要的应用

```bash
apt install sudo vim nano wget git curl apt-utils -y
```

<!-- 否则都是在 /data/data/com.termux/files/usr/bin下
root@localhost:~# which vim
/data/data/com.termux/files/usr/bin/vim
root@localhost:~# which nano
/data/data/com.termux/files/usr/bin/nano
root@localhost:~# which wget
/data/data/com.termux/files/usr/bin/wget
root@localhost:~# which git
/data/data/com.termux/files/usr/bin/git -->

<!-- apt install sudo apt-utils # 其他几个都已经有了 -->



=== 1026 ===
<!-- proot-distro login ubuntu 后，在 ubuntu 里面执行 -->

块 1 - 安装 OpenSSH 服务端

```bash
apt update && apt install -y openssh-server && which sshd && ls -l /etc/ssh/sshd_config && dpkg -l | grep openssh-server
```

块 2 - 备份并修改 sshd_config

```bash
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak && \
sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config && \
sed -i 's/^#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
sed -i 's/^UsePAM yes/UsePAM no/' /etc/ssh/sshd_config && \
grep -E '^(Port|PermitRootLogin|PasswordAuthentication|UsePAM)' /etc/ssh/sshd_config
```

期望输出：
```
Port 2222
PermitRootLogin yes
PasswordAuthentication yes
UsePAM no
```

块 3 - 生成主机密钥 + 创建 /run/sshd

```bash
ssh-keygen -A && mkdir -p /run/sshd && ls -l /etc/ssh/ssh_host_*
```

改密码（默认密码为 `xpad7`）

```bash
passwd
```

块 4 - 首次启动 sshd（前台方式验证一次）

```bash
pkill -f '/usr/sbin/sshd' 2>/dev/null; /usr/sbin/sshd && timeout 2 bash -c 'echo > /dev/tcp/127.0.0.1/2222' && echo "端口 2222 通" || echo "端口 2222 不通"
```

🚀 第二阶段：每次重启平板/ZeroTermux 后的启动
以下命令都在 Termux 宿主（不是 Ubuntu 容器内）执行，通过 proot-distro 直接拉起容器内的 sshd，并以 -D 前台模式让 proot 进程常驻后台。

块 A- 后台启动 sshd + 确认进程 + 查 IP（一块粘完）
```bash
pkill -f 'sshd -D' 2>/dev/null; \
nohup proot-distro login ubuntu -- bash -c "mkdir -p /run/sshd && exec /usr/sbin/sshd -D" > /tmp/ubuntu-sshd.log 2>&1 & \
sleep 2 && ps aux | grep '[s]shd -D' && echo "--- IP ---" && proot-distro login ubuntu -- ip addr | grep 'inet '
```

/usr/sbin/sshd

=== conda ===

不默认启动base，否则有点慢
```bash
conda config --set auto_activate false
conda config --show auto_activate
```

zt开机自启动

DONE✅

=== xiaoai ===

scp -P 2222 -r backend frontend models root@192.168.31.211:~/vesh1030/ # 还是有点多。继续优化

<!-- conda create -n veshau python=3.11 -y -->
conda create -n veshau python=3.11 pip -y
conda activate veshau
pip install -r backend/requirements.txt
pip install edge-tts
bash backend/run.sh

=== ss ===

pip3 install sounddevice numpy sherpa-onnx --prefer-binary openai edge-tts


=== demo-app.py ===

conda create -n veshau python=3.10 pip setuptools wheel

mkdir -p ~/vesh1030

你的代码里用了 pydub（需要 ffmpeg 处理音频）和 sounddevice（需要 portaudio 访问麦克风）。在 pip 安装之前，必须先在 Ubuntu 里装系统库：
apt update
apt install ffmpeg libportaudio2

在虚拟环境 veshau 中安装 Python 包：
conda activate veshau
pip3 install flask requests sounddevice numpy scipy pydub

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

<!--  -->
