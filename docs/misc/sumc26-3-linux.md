---
title: Linux速成-260720
layout: default
parent: misc其他
nav_order: -260720
# nav_exclude: true
---

# Linux速成-260720
{: .no_toc }
`更新-260624` \| `发布-260624`

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<!-- <details markdown="block">
    <summary>ℹ️ 更新历史</summary>
<br>
**260622**
- 新增：[外观](#外观)
</details> -->

<!-- [Windows指南-ping开发板↗]: https://tnt.gdvzz.com/aikit/windowsug.html#pingdk
[Windows指南↗]: https://tnt.gdvzz.com/aikit/windowsug.html -->


# Linux速成班（开发板实战班）课程设计

> 为期6天，每天2小时，以动手操作为主，最终在开发板上成功安装并运行OpenClaw。

---

## 课程总览

| 天数 | 主题 | 核心目标 |
|------|------|----------|
| 第1天 | Linux基础与开发板环境准备 | 掌握基本命令，完成系统烧录与首次启动 |
| 第2天 | Linux进阶与网络配置 | 熟练文件/进程/用户管理，配置SSH远程访问 |
| 第3天 | 开发板系统优化与依赖安装 | 更新系统、配置镜像源、安装Node.js等运行时 |
| 第4天 | OpenClaw安装与初始化配置 | 执行一键安装脚本，完成引导配置 |
| 第5天 | OpenClaw模型接入与通道配置 | 配置AI模型API，设置通信渠道 |
| 第6天 | 综合实战：OpenClaw运行与验收 | 完整部署并演示OpenClaw实际运行 |

---

## 第1天：Linux基础与开发板环境准备（2小时）

**主题：** 从零开始，让开发板“活”起来

### 核心操作内容

#### 1. Linux简介与开发板认识（20分钟）
- Linux是什么、为什么开发板用Linux
- 常见Linux发行版介绍（Debian、Ubuntu、Raspberry Pi OS）
- 认识你的开发板：型号、硬件规格、接口布局
- 开发板推荐配置：**树莓派4B/5（4GB+ RAM）** 或 瑞芯微RV1126B等ARM64开发板

#### 2. 系统镜像烧录（40分钟）
- 下载 Raspberry Pi Imager 或 BalenaEtcher
- 选择64位系统镜像（Raspberry Pi OS Lite 64-bit 或 Ubuntu 24.04）
- 预配置SSH、WiFi、主机名和用户名密码
- 将镜像烧录到MicroSD卡（16GB+）或USB SSD

#### 3. 首次启动与连接（40分钟）
- 插入SD卡、通电启动开发板
- 通过SSH连接到开发板（IP地址查找方法）
- 首次登录与基础探索：`whoami`、`pwd`、`ls`、`cd`

#### 4. 当天成果验收（20分钟）
- 每人确认SSH能成功连接到开发板
- 记录开发板的IP地址和登录信息

> **课后作业：** 练习10个基础命令（ls、cd、pwd、mkdir、rm、cp、mv、cat、echo、clear）

---

## 第2天：Linux进阶与网络配置（2小时）

**主题：** 掌握Linux核心操作，打通网络通路

### 核心操作内容

#### 1. 文件系统与权限管理（30分钟）
- Linux目录结构（`/`、`/home`、`/etc`、`/var`、`/opt`等）
- 文件权限：`chmod`、`chown` 实战
- 创建专用服务用户：`sudo useradd -m -s /bin/bash openclaw`

#### 2. 进程与服务管理（20分钟）
- 查看进程：`ps aux`、`top`/`htop`
- 系统服务管理：`systemctl` 基本用法

#### 3. 网络配置与SSH深入（30分钟）
- 查看网络状态：`ip a`、`ifconfig`
- 配置静态IP或确认DHCP
- SSH密钥登录配置（安全性提升）
- 时间同步：`sudo timedatectl set-ntp true`

#### 4. 包管理基础（30分钟）
- APT包管理器基本操作：
  - `sudo apt update` —— 更新软件源列表
  - `sudo apt upgrade -y` —— 升级所有软件包
  - `sudo apt install <package>` —— 安装软件
  - `sudo apt remove <package>` —— 卸载软件
- 实操：安装 `git`、`curl`、`wget`、`vim`/`nano`

#### 5. 当天成果验收（10分钟）
- 每人能独立使用SSH登录、执行文件操作、安装软件包

> **课后作业：** 在自己的开发板上安装 `tree` 和 `htop`，探索 `/etc` 目录结构

---

## 第3天：开发板系统优化与依赖安装（2小时）

**主题：** 搭建OpenClaw运行所需的所有环境

### 核心操作内容

#### 1. 系统全面更新（15分钟）
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget jq build-essential pkg-config



## 第4天：OpenClaw安装与初始化配置（2小时）

**主题：** 一键安装OpenClaw，完成首次引导配置

---

#### 1. 执行一键安装脚本（30分钟）

使用官方提供的安装脚本进行一键安装，该脚本会自动下载并安装OpenClaw的npm包及其依赖。

**使用官方安装脚本（推荐）**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```
使用备用镜像源（国内网络环境）

bash
curl -sSL https://get.openclaw.ai | bash
安装过程约需2-4分钟，期间会自动完成以下操作：

检测系统环境

安装OpenClaw npm包（全局安装）

创建默认配置目录 ~/.openclaw/

生成初始配置文件

安装完成后，脚本会提示安装位置和后续步骤。

2. 配置PATH环境变量（10分钟）
若安装后执行 openclaw 命令提示“command not found”，需将npm全局bin目录添加到PATH环境变量中。

bash
# 添加npm全局bin目录到PATH
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc

# 使配置立即生效
source ~/.bashrc
验证是否配置成功：

bash
which openclaw
openclaw --version
若能正常显示版本号（如 v1.x.x），则说明安装成功。

3. 运行Onboarding引导配置（40分钟）
执行Onboarding命令，该命令会以交互式向导方式引导你完成OpenClaw的首次配置，并自动安装系统服务（daemon）。

bash
openclaw onboard --install-daemon
交互步骤说明

安全警告
界面会显示安全提示，阅读后使用键盘方向键选择 Yes，按回车确认。

安装模式
选择 QuickStart（快速启动模式），该模式会使用推荐的默认配置。

配置方式
选择 Use existing values（使用现有值），即接受默认配置项（如端口、存储路径等）。

整个过程中，Onboarding会自动：

生成网关访问令牌（Access Token）

创建默认配置文件 ~/.openclaw/openclaw.json

注册系统服务（user service）用于后台运行

注意：若Onboarding过程中出现网络超时或镜像源问题，可先检查npm镜像源配置（参见第3天），或手动设置环境变量 NPM_CONFIG_REGISTRY=https://registry.npmmirror.com 后再执行。

4. 配置OpenClaw为系统服务（30分钟）
完成Onboarding后，OpenClaw已注册为用户级系统服务。需启用用户服务持久化，并验证服务状态。

启用用户服务持久化

bash
sudo loginctl enable-linger "$(whoami)"
该命令确保用户服务在用户未登录时也能保持运行（对开机自启至关重要）。

验证服务状态

bash
systemctl --user status openclaw-gateway.service
预期输出应包含 active (running) 字样。若服务未启动，可手动启动：

bash
systemctl --user start openclaw-gateway.service
查看服务日志（排查问题）

bash
journalctl --user -u openclaw-gateway.service -f
按 Ctrl+C 退出日志查看。

5. 当天成果验收（10分钟）
每位学员需独立完成以下验证项：

bash
# 1. 查看OpenClaw版本
openclaw --version

# 2. 检查服务运行状态
systemctl --user status openclaw-gateway.service --no-pager

# 3. 查看生成的配置文件是否存在
ls -la ~/.openclaw/

# 4. 查看网关访问令牌（后续配置需要）
cat ~/.openclaw/openclaw.json | grep access_token
验收标准：

✅ openclaw --version 正常输出版本号

✅ 服务状态为 active (running)

✅ ~/.openclaw/openclaw.json 文件存在且包含 access_token 字段

✅ Onboarding过程无报错，顺利完成

课后作业： 注册一个AI模型服务商账号（推荐阿里云百炼，获取通义千问API Key），为第5天的模型配置做好准备。同时，熟悉Telegram Bot的创建流程（通过 @BotFather），为后续配置通信渠道打基础。



<!--  -->
<span style="font-size:12px; color:#999">THE END</span>