---
title: aikit教具
layout: default
# parent: AI Lab
nav_order: 20
# nav_exclude: true
---

# AI教具说明
{: .no_toc }
`更新-260401` \| `发布-260101`

本文档描述 AI 教具的相关信息，用于快速熟悉和入门 AI 教具。

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
## AKA

<br>
后续文档将用以下缩写称呼相关 AI 教具：

- 视觉实验箱：**viki** (VIsual KIt)
- NLP 实验箱：**nlpx** (NLP)
- 昇腾开发板：**aidk** (Ascend Innovation / Artificial Intelligence Developer Kit )
- 鲲鹏开发板：**dkoo** (Like 'd cool'. dk = Developer Kit, k also for Kunpeng, oo = 2 Orange Pi)

---

## UserPassword

<br>
AI 教具的默认用户和密码如下，可用于登录和使用 AI 教具的 Linux（Ubuntu）系统。

> 以“用户 / 密码”方式表达。比如“jetson / yahoom”表示 Linux 用户 jetson 的默认密码是 yahboom。

1. 视觉实验箱（机械臂，Jetson开发板）

    - jetson / yahboom
    - root / yahboom

2. NLP实验箱（Jetson开发板）

    - cg / cgremote
    - root：可以通过 cg 用户执行 `sudo -i` 切换到 root

3. 昇腾开发板 + 鲲鹏开发板

    - HwHiAiUser / Mind@123
    - root / Mind@123

---

## WiFi

<br>
本章节介绍如何连接和断开 WiFi 的方法。（未完待续）

### viki

<br>
适用于视觉实验箱（viki）和 NLP实验箱（nlpx）。

- 点击屏幕右上角 **喇叭+电源+箭头** 连在一起的区域。（如果连了网线，还有**网络**标志，即 4 个图标连在一起的区域）
- 选择 **WiFi**相关的那行，点开。（WiFi Off，或 WiFi Not Connected，或某个已连接的 WiFi）
- 点击 **Turn On**（如果 WiFi Off）。然后重复上述第1、2 步，点击 **Select Network**，选择要连接 WiFi，输入 WiFi 密码等，就可以连接 WiFi 了。
- 关闭 WiFi。重复上述第1、2步，然后点击**Turn Off**。
- ✳️ 连接校园网的 WiFi 后，尝试打开浏览器是否可上网。如不能，可能需要登录校园网。

> 待补充命令行连接wifi。

### nlpx
<br>

同 [视觉实验箱viki](#viki)。

