---
title: Linux常用操作
layout: default
parent: aikit教具
nav_order: 90
# nav_exclude: true
---

# Linux常用操作
{: .no_toc }
`更新-260427` \| `发布-260320`

本文档描述 Linux 常用操作，供同学参考。

<!--  -->
<details markdown="block">
  <summary>
    目录
  </summary>
  <!-- {: .text-delta } -->
- TOC
{:toc}
</details>

---

## 快捷操作

- ✳️ 按 `tab` 键可补齐文字，加快输入。假定当前目录下有 3 个子目录（face_mesh，gesture_recognizer，haar_detection），输入 `cd ges` 后按 `tab` 键，则补齐为 `cd gesture_recognizer/`。

- ✳️ 按 `esc` 键后，再按 `↑↓箭头` 键，可以找到输入过的命令。不必每次都重复敲命令。

---

## 常用命令

### ls 查看文件和目录

- `ls`：列出当前目录下的文件和子目录
- `ls -l`：列出详细信息

### cd/mkdir/pwd 创建/切换/显示目录

- `cd`：切换到用户的 HOME 目录
- `cd ~`：切换到用户的 HOME 目录
- `cd ..`：返回上一级目录
- `cd tmp`：切换到当前目录下的 tmp 子目录
- `mkdir tmp`：在当前目录下创建 tmp 子目录
- `pwd`：显示当前目录在哪里

### cp/mv 复制/改名文件

- `echo 'Hello, World!' > test.txt`：在当前目录下生成 test.txt 文件，文件内容是 Hello, World!
- `cp test.txt hello.txt`：复制文件 test.txt 到 hello.txt
- `mv hello.txt hiworld.txt`：将文件 hello.txt 改名为 hiworld.txt
- `mv hiworld.txt tmp/`：将文件 hiworld 移动到当前目录的子目录 tmp 下面

### ifconfig 查看IP地址

- `ifconfig`：查看 IP 地址
- `ifconfig | grep 172`：查看包含 172 的 IP 地址

### clear 清屏

- `clear`：清除屏幕信息

### su 切换用户

- `su - root`：切换到 root 用户
- `su - HwHiAiUser`：切换到 HwHiAiUser 用户

### sudo 提升权限

- `sudo python3 agent.py`：jetson 用户提升权限，用 root 权限执行 agent.py

