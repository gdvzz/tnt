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

### ifconfig 查看IP地址

- `ifconfig`：查看 IP 地址
- `ifconfig | grep 172`：查看包含 172 的 IP 地址

### ls 查看文件和目录

- `ls`：列出当前目录下的文件和子目录
- `ls -l`

- 查看 IP 地址：`ifconfig | grep 172`

- 创建/切换/显示当前目录：

    ```bash
    # 在用户的 HOME 目录下创建子目录 tmp260304
    mkdir ~/tmp260304
    
    # 切换到 HOME 目录
    cd
    pwd # 执行后屏幕应显示 /home/jetson
    
    # 切换到 tmp260304 子目录
    cd ~/tmp260304
    pwd # 执行后屏幕应显示 /home/jetson/tmp260304
    ```

    说明：pwd 是 Print Working Directory，显示当前所在的目录路径。

- 显示信息：`ls -l`

- 复制/改名

    ```bash
    # 先切换到 /home/jetson/tmp260304
    cd ~/tmp260304

    # 在当前目录下生成文件 test.txt
    echo "Hello, World!" > test.txt

    # 复制文件 test.txt 到 hello.txt
    cp test.txt hello.txt

    # 修改文件 hello.txt 为 hiworld.txt
    mv hello.txt hiworld.txt

    # 列出当前目录下的文件
    ls -l
    ```

- 清除屏幕信息

    ```bash
    clear
    ```