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
mkdir ~/tmp2603 # 在用户的 HOME 目录下创建子目录 tmp2603
cd              # 切换到 HOME 目录
pwd             # 执行后屏幕应显示 /home/jetson

cd ~/tmp2603    # 切换到 tmp2603 子目录
pwd             # 执行后屏幕应显示 /home/jetson/tmp2603
    ```

    说明：pwd 是 Print Working Directory，显示当前所在的目录路径。

- 显示信息：`ls -l`

- 复制/改名

    ```bash
cd ~/tmp2603                    # 先切换到 /home/jetson/tmp2603
echo "Hello, World!" > test.txt # 在当前目录下生成文件 test.txt
cp test.txt hello.txt           # 复制文件 test.txt 到 hello.txt
mv hello.txt hiworld.txt        # 修改文件 hello.txt 为 hiworld.txt
ls -l                           # 列出当前目录下的文件
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
scp jetson@172.18.139.100:/home/jetson/vkai260325.zip /home/jetson
    ```

    如果出现提示信息 `(yes/no/[fingerprint])? `，输入 `yes`。下次再访问或登录该 Jetson 开发板时不会有此提示信息。
    ```bash
jetson@jetson-Yahboom:~$ scp jetson@172.18.139.100:/home/jetson/vkai260325.zip .
The authenticity of host '172.18.139.100 (172.18.139.100)' can't be established.
ECDSA key fingerprint is SHA256:FKxZyl0ul/cy21+QdY/SEYmeVEfCctq8SQlDi5XkUbg.
Are you sure you want to continue connecting (yes/no/[fingerprint])? 
    ```

    要求输入口令时，输入 `yahboom`。随后可见复制文件完成。✅ 输入口令时，屏幕不会有显示输入的口令内容，这是正常的（因为是口令，所以不能显示出来被别人看到）。输入口令完成后，按回车即可。输入过程中假定有误，可按退格键删除。
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

- 执行以下命令将下载的文件移动到 jetson 用户的 HOME 目录。浏览器下载文件通常存放在 jetson HOME 目录的 Downloads 子目录中。

    ```bash
mv ~/Downloads/vkai260325.zip ~/.
    ```

- 执行以下命令解压缩 zip 文件。解压缩完成后生成子目录 vkai。

    ```bash
unzip vkai260325.zip
    ```

==========

### 启动和退出样例demo

- 进入样例demo程序所在目录

    ```bash
cd ~/vkai
    ```

- （可选）如果命令行提示符行首有 `(base)`（有带括号的一串字母，不一定是 base），则执行以下命令退出 Python 虚拟环境。命令执行后，行首就没有带括号的一串字母了。

    ```bash
(base) jetson@jetson-Yahboom:~$ conda deactivate
jetson@jetson-Yahboom:~$ 
    ```

- 执行 `python3 agent.py` 启动样例demo。

    ```bash
jetson@jetson-Yahboom:~/vkai$ python3 agent.py
WARNING: Carrier board is not from a Jetson Developer Kit.
WARNNIG: Jetson.GPIO library has not been verified with this carrier board,
WARNING: and in fact is unlikely to work correctly.
<USER>:
    ```

- 按 `ctrl` + `c` 键，可退出样例demo程序。

==========

### 体验样例demo

- 先在机械臂前面的桌面上放置带抓取的积木。

- 然后在样例demo程序启动后的 `<USER>:` 提示符后，输入 `grab {颜色} cube and move to {xy坐标}` 指令体验，如下：

    ```bash
grab blue cube and move to -80,200
grab green cube and move to 0,200
grab red cube and move to 80,200
grab yellow cube and move to 160,200
    ```

🛎️ 目标 {xy坐标}，建议是 4 种组合之一：`-80,200`，`0,200`，`80,200`，`160,200`。

🚫 **如果目标 {xy坐标} 已有积木，不能让机械臂抓积木再移动到相同坐标。否则可能导致机械臂损坏。**

==========

### 相关说明

- 机械臂底座背部，和六角形空洞平齐。

    [![backend](./labkit.assets/irobot3.jpg)](./labkit.assets/irobot3.jpg)

- 待抓取积木放置范围：距离桌面边缘约 1 个积木位置，距离机械臂约 2 个积木位置，范围大约是 3 * 5 个积木。

    [![scope](./labkit.assets/irobot2.jpg)](./labkit.assets/irobot2.jpg)

- 整体外观：

    [![overall](./labkit.assets/irobot1.jpg)](./labkit.assets/irobot1.jpg)

    坐标原点，是机械臂底座上方圆柱体中心和底座的交点。

- 图纸样式：

    [![map](./labkit.assets/map.jpg)](./labkit.assets/map.jpg)

    X、Y的箭头方向是正方向。Z的正方向是水平朝上。

    以 `-80,200` 为例：移动到 X=-80、Y=200。Z默认是110。

- ✅ 如果抓取不大准，可略微移动机械臂的位置。或者修改 config.json 中的 xyz 的数值。

    ```json
{
    "points_pixel": [
        [320,220],
        [590,430],
        [72,31],
        [590,26]
    ],
    "points_arm": [
        [210,0],
        [140, -80],
        [280,80],
        [280,-80]
    ],
    "x": 0,
    "y": 0,
    "z": 0,
    "voice":false,
    "threshold": 110
}
    ```

    可执行 `vim config.json` 编辑文件。用 vim 打开文件后，

    **删除字符**：光标先移动到待删除字符，再按 `esc` 键，再按 `x` 键。

    **插入字符**：光标先移动到待插入位置，先按 `esc` 键，再按 `i` 键，然后输入字符。

    **保存修改**：先按 `esc` 键，再输入 `:wq`，再按 `回车` 键。

    **放弃修改**：先按 `esc` 键，再输入 `:q!`，再按 `回车` 键。

==========

### 关机

1. 在终端中执行关机命令 `shutdown -h now`。或者屏幕右上角：电源标志 → power off。
2. 观察开发板小机箱的散热风扇。风扇停止后，按桌子下面的立方体插座上的开关，电源指示灯熄灭。
3. 起身正对机械臂，将竖立的机械臂向前轻轻推倒，水平卧在 Jetson 开发板小机箱上即可。

🚫 电源线：不必从视觉实验箱拔下来；也不必从桌子下面的插座上拔下来。<br>
🚫 机械臂：水平自然卧倒在小机箱上即可。不必整理、扭成很好看的造型（可能导致下次启动时无法站立）。

### 椅子复原

椅子推到桌子下面。1 个桌子配备 6 个椅子。多余的椅子放到实验室的左右两侧。

### 带走物品

请带走个人物品。




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


<!-- ## 演示程序

可访问以下链接获得演示程序源码：

- NLP演示程序：[链接↗](https://gitlab.educg.net/cg_zmy/Jetson_ai.git)
- 机械臂演示程序：[链接↗](https://pan.educg.net/s/QlQ0UX)
- 机械臂演示程序：[e江南云盘链接↗](https://pan.jiangnan.edu.cn/link/AA9E7A15CF025A49F9B9299B21A5448A83) --> -->
