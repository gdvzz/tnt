---
title: Linux常用操作
layout: default
parent: aikit教具
nav_order: 90
# nav_exclude: true
---

# Linux常用操作
{: .no_toc }
`更新-260428` \| `发布-260320`

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

### cp/mv 复制/改名移动文件

- `echo 'Hello, World!' > test.txt`：在当前目录下生成 test.txt 文件，文件内容是 Hello, World!
- `cp test.txt hello.txt`：复制文件 test.txt 到 hello.txt
- `mv hello.txt hiworld.txt`：将文件 hello.txt 改名为 hiworld.txt
- `mv hiworld.txt tmp/`：将文件 hiworld 移动到当前目录的子目录 tmp 下面

### zip/unzip 打包/解压

- `zip -r 1stapp.zip 1stapp/`：把当前目录下的 1stapp 子目录，打包压缩成 1stapp.zip
- `unzip -t 1stapp.zip`：验证 zip 文件是否正确，并不解压
- `unzip 1stapp.zip`：解压 zip 文件到当前目录。解压后生成子目录 1stapp/
- `zip res1.zip resnet50.onnx`：将文件 resnet50.onnx，压缩为 res1.zip

### scp 远程复制文件/目录

- `scp /local/path/file.txt user@remote_host:/remote/path/`：从本地复制文件到远程主机

    ```bash
    scp vscode1.jpg HwHiAiUser@172.18.145.125:/home/HwHiAiUser/samples/notebooks/01-yolov5
    HwHiAiUser@172.18.145.125's password: 
    vscode1.jpg    100% 1098KB  11.2MB/s   00:00    
    ```

    ✳️ 说明：将本地电脑当前目录下的文件 vscode1.jpg，复制到远程主机 172.18.145.125 的 /home/HwHiAiUser/samples/notebooks/01-yolov5 目录中，以用户 HwHiAiUser 访问远程主机

- `scp -r /local/path/dir user@remote_host:/remote/path/`：从本地复制目录（递归，以及目录下的子目录和文件）到远程主机

    ```bash
    scp -r tmp123 HwHiAiUser@172.18.145.125:/home/HwHiAiUser/samples/notebooks/01-yolov5
    HwHiAiUser@172.18.145.125's password: 
    vscode9.jpg  100%  573KB  10.2MB/s   00:00    
    vscode8.jpg  100%  570KB  10.6MB/s   00:00    
    vscode1.jpg  100% 1098KB  12.0MB/s   00:00    
    vscode2.jpg  100%  475KB  10.7MB/s   00:00    
    vscode3.jpg  100%  499KB  11.0MB/s   00:00    
    vscode7.jpg  100%  501KB   9.6MB/s   00:00    
    vscode6.jpg  100%  530KB  11.8MB/s   00:00    
    vscode4.jpg  100%  480KB   9.5MB/s   00:00    
    vscode5.jpg  100%  537KB  12.2MB/s   00:00    
    vscodea.jpg  100%  713KB  11.4MB/s   00:00    
    vscodeb.jpg  100%  490KB  10.5MB/s   00:00     
    ```

    ✳️ 说明：将本地电脑当前目录下的子目录 tmp123（以及 tmp123 目录下的子目录和文件），复制到远程主机 172.18.145.125 的 /home/HwHiAiUser/samples/notebooks/01-yolov5 目录中，以用户 HwHiAiUser 访问远程主机。tmp123 目录下有 10 多个图片文件。

- `scp user@remote_host:/remote/path/file.txt /local/path/`：从远程主机复制文件到本地

    ```bash
    scp HwHiAiUser@172.18.145.125:/home/HwHiAiUser/1stapp.zip .
    HwHiAiUser@172.18.145.125's password: 
    1stapp.zip  100%  136MB  16.2MB/s   00:08    
    ```

    ✳️ 说明：复制远程主机 172.18.145.125 的 /home/HwHiAiUser/1stapp.zip 文件，到本地的当前 目录中，以用户 HwHiAiUser 访问远程主机

- `scp -r user@remote_host:/remote/path/dir /local/path/`：从远程主机复制目录（递归，以及目录下的子目录和文件）到本地

    ```bash
    scp -r HwHiAiUser@172.18.145.125:/home/HwHiAiUser/1stapp .
    HwHiAiUser@172.18.145.125's password: 
    first_app.py        100% 6689     1.4MB/s   00:00    
    dog2_1024_683.jpg   100%   40KB   3.4MB/s   00:00    
    dog1_1024_683.jpg   100%   35KB   4.1MB/s   00:00    
    fusion_result.json  100% 3248   624.5KB/s   00:00    
    resnet50.om         100%   49MB  16.1MB/s   00:03    
    resnet50.onnx       100%   98MB  16.4MB/s   00:05 
    ```
    ✳️ 说明：复制远程主机 172.18.145.125 的 /home/HwHiAiUser/1stapp 目录递归，以及目录下的子目录和文件），到本地的当前目录中，以用户 HwHiAiUser 访问远程主机

### ifconfig 查看IP地址

- `ifconfig`：查看 IP 地址
- `ifconfig | grep 172`：查看包含 172 的 IP 地址

### clear 清屏

- `clear`：清除屏幕信息

### whoami/id/su 显示/切换用户

- `whoami`：显示用户名
- `id`：显示用户id（用户名）、组id（组名）、其他组id（组名）
- `su - root`：切换到 root 用户
- `su - HwHiAiUser`：切换到 HwHiAiUser 用户

### sudo 提权操作

- `sudo python3 agent.py`：普通用户A提升权限，用 root 权限执行 agent.py。普通用户A先要加入 sudo 组，才能执行 sudo 提权操作。

### shutdown/poweroff 关机

- `sudo shutdown -h now`：马上关机
- `sudo poweroff`：关机

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>