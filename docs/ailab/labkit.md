---
title: AI教具使用简要说明New
layout: default
parent: AI Lab
nav_order: 9001
# nav_exclude: true
---

# AI实验室教具使用说明New
{: .no_toc }
`更新-260323` \| `发布-251101`

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

## 视觉实验箱-260325

### 上电开机

- 视觉实验箱配有 1 个电源，一端连实验箱，另一端插头插在桌子下面的插座上。
- 桌子下面有个带开关的的立方体插座。按下开关，电源指示灯亮，即表明接通电源。
- 稍等片刻可完成启动。视觉实验箱的机械臂站立起来，且屏幕显示 Ubuntu 的主界面，就启动完成。

==========

### 熟悉 Linux

- ✅ 建议：如果还不大熟悉 Linux 命令和操作，尽量手敲以尽快熟悉。
- ℹ️ 信息：Jetson 开发板账号密码是 jetson / yahboom，如需要。比如在笔记本电脑上通过 `ssh jetson@开发板IP地址` 登录开发板，。
- 🛎️ 提示：在 Ubuntu 主界面左侧导航栏找到对应的 App，或者点击左下角  **九宫格 Show Applications** 后出现顶部搜索栏输入 App 的名字查找。
- 🛎️ 提示：按 `tab` 键可补齐文字，加快输入。假定当前目录下有 3 个子目录（face_mesh，gesture_recognizer，haar_detection），输入 `cd ges` 后按 `tab` 键，则补齐为 `cd gesture_recognizer/`。
- 🛎️ 提示：按 `esc` 键后，再按 `↑↓箭头` 键，可以找到输入过的命令。不必每次都重复敲命令。
- 🛎️ 提示：浏览器和其他图形界面中，复制/粘贴的快捷键是 ctrl + c 和 ctrl + v。
- 🛎️ 提示：在 **终端 Terminal** App 中，复制/粘贴的快捷键是 ctrl + shift + c 和 ctrl + shift + v。
- 🛎️ 提示：`win` + `←↑↓→箭头`键，可排列屏幕。
- 🛎️ 如果习惯使用 Chrome 浏览器，可以在终端中执行 `sudo apt install chromium-browser` 安装。

开始 Linux 操作之旅……

- 启动浏览器访问网站

    在 Jetson 开发板上启动 **Firefox 浏览器** App（或者 Chrome 浏览器），输入网址访问，比如： `https://tnt.gdvzz.com/`。

- 在 Jetson 开发板上启动 **终端 Terminal** App。

- 查看 IP 地址：`ifconfig | grep 172`

    ```bash
    jetson@jetson-Yahboom:~$ ifconfig | grep 172
        inet 172.17.0.1  netmask 255.255.0.0  broadcast 172.17.255.255
        inet 172.18.139.99  netmask 255.255.255.0  broadcast 172.18.139.255
    ```

    > 类似于 `172.18.139.99`，就是 Jetson 开发板的 IP 地址。本实验室的 IP 地址都是 172.18.xxx.xxx。

    🛎️ 如果还有 `inet 172.22.22.201  netmask 255.255.0.0  broadcast 172.22.222.255`（即屏幕显示了 3 行输出），则表示 WiFi 也开启了。建议不要同时连接网线和WiFi（可能会出现网络相关问题，比如无法远程 ssh 登录 Jetson 开发板）。连接网线时要关闭 WiFi：点击屏幕右上角（网络+喇叭+电源+箭头 连在一起的区域），选择第二行 WiFi 点开，点击 **Turn Off**。

    🛎️ 如有网线断开了，还是点右上角，选择第一行 PCI Ethernet 点开，点击 **Connect** 重连就可。

- 创建/切换/显示当前目录：

    ```bash
    # 在用户的 HOME 目录下创建子目录 tmp2603
    mkdir ~/tmp2603
    
    # 切换到 HOME 目录
    cd
    pwd # 执行后屏幕应显示 /home/jetson
    
    # 切换到 tmp2603 子目录
    cd ~/tmp2603
    pwd # 执行后屏幕应显示 /home/jetson/tmp2603
    ```

    说明：pwd 是 Print Working Directory，显示当前所在的目录路径。

- 显示信息：`ls -l`

- 复制/改名

    ```bash
    # 先切换到 /home/jetson/tmp2603
    cd ~/tmp2603

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

==========

### 获取样例demo

**方法1**

- 启动 **终端 Terminal**，执行以下指令，从实验室某个视觉试验箱上复制一份：

    ```bash
    scp jetson@172.18.139.100:/home/jetson/vkai260325.zip .
    ```
    
    如果出现提示信息 `(yes/no/[fingerprint])? `，输入 `yes`：
    ```bash
    jetson@jetson-Yahboom:~$ scp jetson@172.18.139.100:/home/jetson/vkai260325.zip .
    The authenticity of host '172.18.139.100 (172.18.139.100)' can't be established.
    ECDSA key fingerprint is SHA256:FKxZyl0ul/cy21+QdY/SEYmeVEfCctq8SQlDi5XkUbg.
    Are you sure you want to continue connecting (yes/no/[fingerprint])? 
    ```

    要求输入口令时，输入 `yahboom`。随后可见复制文件完成。
    ```bash
    ...
    jetson@172.18.139.100's password: 
    vkai260325.zip            100%  463KB  77.7MB/s   00:00 
    ```

- 执行以下命令解压缩 zip 文件。解压缩完成后生成子目录 vkai。

    ```bash
    unzip vkai260325.zip
    ```

**方法2**

- 点击下载：[e江南云盘链接↗](https://pan.jiangnan.edu.cn/link/AA9E7A15CF025A49F9B9299B21A5448A83) 



<!-- ## 搭建环境

先执行：

pip3 install flask openai voice pyaudio soundfile -i https://mirrors.aliyun.com/pypi/simple/ 

还缺：

pip3 install requests
pip3 install Pillow
pip3 install pymycobot
pip3 install opencv-python
pip3 install Jetson.GPIO
<!-- Jetson.GPIO -->

<!-- ModuleNotFoundError: No module named 'jetcobot_utils'
(vkai3810) vkai@jetson-Yahboom:~/elephant-ai$ export PYTHONPATH=/home/jetson/jetcobot_ws/devel/lib/python3/dist-packages:/home/jetson/software/ar_track_ws/devel/lib/python3/dist-packages:/opt/ros/noetic/lib/python3/dist-packages

pip3 install scipy -->


## 演示程序

可访问以下链接获得演示程序源码：

- NLP演示程序：[链接↗](https://gitlab.educg.net/cg_zmy/Jetson_ai.git)
- 机械臂演示程序：[链接↗](https://pan.educg.net/s/QlQ0UX)
- 机械臂演示程序：[e江南云盘链接↗](https://pan.jiangnan.edu.cn/link/AA9E7A15CF025A49F9B9299B21A5448A83) -->
