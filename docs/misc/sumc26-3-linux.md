---
title: Linux速成-2607
layout: default
parent: misc其他
nav_order: -260720
# nav_exclude: true
---

# Linux速成-2607
{: .no_toc }
`更新-260709` \| `发布-260624`

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

## Linux 随处可见
<br>
Linux 随处可见。比如：

- **安卓Android**。基于 Linux 内核。它在 Linux 内核基础上做了定制和扩展，但通常不认为它是传统的 Linux 发行版。
- **macOS**。不是基于 Linux，而是基于 Unix。其核心是开源的 Darwin 系统，内核为 XNU（混合了 Mach 和 BSD 组件）。从使用角度，和 Linux 基本一致。更合适的说法：从使用角度，Linux 和 Unix 基本一致。
- **iOS**。也不是基于 Linux，同样基于 Unix。它与 macOS 同源，也基于 Darwin 和 XNU 内核。从使用角度，和 Linux 基本一致。更合适的说法：从使用角度，Linux 和 Unix 基本一致。
- **Windows - PowerShell**。也支持较多 Linux 命令。
- **Windows - WSL**。WSL（Windows Subsystem for Linux）是运行在 Windows 下的 App（不是双系统，不是虚拟机），提供了 Linux 环境。
<!--  -->
- **云厂家**。云厂商的庞大基础设施（物理服务器和绝大多数云主机）几乎都跑着 Linux，但为了满足特定客户的需求，他们也必须提供 Windows Server 等选项。
    
    - **Google Cloud**。高达 91.6% 的虚拟机运行 Linux。
    - **AWS**。这个比例是 83.5%。
    - **微软 Azure**。即便微软有自家的 Windows Server，Azure 上也有 61.8% 的虚拟机核心和超过 60% 的市场服务产品基于 Linux。
    - **华为云 Huawei Cloud**。华为云的整体情况和主流云厂商一致：绝大多数核心业务和云主机都跑在Linux上，同时也提供了Windows Server等选项以满足特定需求。但华为云最独特的一点是，它不仅有通用的Linux发行版，还专门打造了自研的、基于Linux的企业级操作系统——Huawei Cloud EulerOS (HCE)。

---

## 大家都要学点Linux
<br>
大家都要学点 Linux：

- Linux 随处可见，应用很广。
- 计算机专业的同学，总是要学点 Linux。
- 有较多实验课，要用到 Linux。

---

## Linux 和 Unix
<br>
Linux 不是 Unix。

**1、Unix**

- UNIX：源自早期项目 Multics（复杂信息系统），取其“反义”戏称为 Unics（单一信息系统），后谐音演变为 UNIX。它不是“用户网络操作系统”等单词的缩写。
- 血脉（代码来源）：UNIX 是“亲儿子”，其内核源码源自 AT&T 贝尔实验室，现在主流分支（如 macOS 的 XNU、IBM 的 AIX）均闭源且需商业授权。
- 灵魂（设计哲学）：UNIX 追求“极简稳定”，内核只做最基础的事情（如进程调度、文件管理），驱动等附加功能跑在用户空间，改动内核需严格审批，极其保守。

**2、Linux**

- Linux：是 Linus + Unix 的组合词，即 Linus Torvalds 开发的类 Unix 系统。官方全称是 GNU/Linux（因为核心工具来自 GNU 项目），而 GNU 本身是一个递归缩写，意为 “GNU's Not Unix”（GNU不是Unix）。
- 血脉（代码来源）：Linux 是“最佳复刻”，内核完全从零重写，基于 GPL 开源协议，任何人都能看源码、改代码。
- 灵魂（设计哲学）：Linux 拥抱“激进创新”，采用宏内核 + 动态模块加载，驱动随时能插拔，且拥有 CFS 调度器（完全公平调度）和 RCU 锁（读写并发优化），在高并发服务器场景下性能碾压老牌 UNIX。

**3、Linux 的发行版**

既然内核是“引擎”，那发行版（Distro）就是装上轮子和外壳的整车。市面上几百种发行版，主要分三大“帮派”：

- Debian 系（Ubuntu、Linux Mint）：主打“新手友好”。包管理用 apt-get，软件格式是 .deb。优点是大而全，驱动和软件库最丰富，适合桌面用户和入门服务器。缺点是稍微“臃肿”，部分激进更新可能不够稳。
- Red Hat 系（RHEL、CentOS、Fedora）：主打“企业稳如狗”。包管理用 yum 或 dnf，软件格式是 .rpm。RHEL 是付费商业版，CentOS 曾是它的免费克隆（现已转向CentOS Stream滚动版），Fedora 则是“试验田”最新技术。特点是软件版本偏旧但极度保守，银行、金融行业最爱。
- Arch 系（Arch Linux、Manjaro）：主打“极致极客”。无版本号，采用滚动更新（永远是最新内核）。包管理用 pacman，最著名的特点是 AUR（用户仓库）——几乎所有第三方软件一键编译安装。缺点是需要手动配置，容易滚挂（更新后崩溃），适合喜欢折腾的高手。

---

## 发音
<br>
Linux怎么读？

- Linux:/ˈlɪn.əks/。谐音：“林纳克斯”。u 发 ə，**不能读成 “林尼克斯”**。
- Ubuntu：/ʊˈbʊn.tuː/。谐音：“乌-本-图”（三个音节，重音在“本”上）。这是非洲祖鲁语/科萨语词汇，意为“人性善待他人”。**“乌” 不是“优”**。


<!-- 
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
 -->


<!--  -->
<span style="font-size:12px; color:#999">THE END</span>