---
title: e4-玩转wsl
layout: default
parent: Linux速成-2607
nav_order: 4
# nav_exclude: true
---

# e4-玩转wsl（Linux速成-2607）
{: .no_toc }
`更新-260718` \| `发布-260718`

在 Windows 的 WSL 进行相关操作，进一步熟悉 Linux 相关操作。

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

## 安装和卸载
<br>
安装和卸载某个 Linux 发行版，相关操作可参考如下建议。

- **安装的常用命令**

    ```bash
wsl --install  Ubuntu-24.04 --name ubtu24 --location d:\wsl\ubtu24 --web-download
    ```

    命令行参数含义如下：

    - `wsl --install`: 这是安装 WSL 及其 Linux 发行版的主命令。
    - `Ubuntu-24.04`: 这个参数跟在 --install 后面，相当于 -d Ubuntu-24.04，用于指定要安装的发行版是 Ubuntu 24.04 LTS。
    - `--name ubtu24`: 它的作用是给即将安装的发行版自定义一个简短易记的名称（ubtu24），方便后续管理。
    - `--location d:\wsl\ubtu24`: 它指定了发行版的安装路径为 D:\wsl\ubtu24，可以实现将系统安装到其他盘符，避免占用系统盘（C盘）空间。
    - `--web-download`: 它的作用是从网络源（而非 Microsoft Store）下载发行版进行安装。在国内网络环境下，或当你希望获得最新版本时，这个参数有助于提升安装的灵活性和稳定性。

- **已经安装了 Ubuntu-24.04，还可以再装一个 Ubuntu-24.04。**比如：

    ```bash
wsl --install  Ubuntu-24.04 --name Ubuntu24 --location d:\wsl\ubuntu24
    ```

- **安装其他发行版。** 比如：kali-linux

    ```bash
wsl --install  kali-linux  --name kali --location d:\wsl\kali --web-download
    ```

    屏幕上显示如下类似信息：

    ```text
Downloading: Kali Linux Rolling
Installing: Kali Linux Rolling
Distribution successfully installed. It can be launched via 'wsl.exe -d kali'
Launching kali...
Waiting for systemd to start...
running
Please create a default Kali WSL user. The username does not need to match your Windows username.
For more information visit: https://aka.ms/wslusers
Enter new UNIX username: gdv2
New password:
Retype new password:
passwd: password updated successfully
┌──(gdv2㉿gdv2-winbook)-[/mnt/c/Users/gdv2]
└─$
    ```

    > （编者注）Linux 不是 UNIX。上述提示中 `Enter new UNIX username` 可能有点不妥。

- **查看当前安装了哪些 Linux 发行版**

    ```bash
wsl -l -v 
    ```

    屏幕显示如下类似信息：

    ```text
  NAME        STATE           VERSION
* Ubuntu24    Stopped         2
  ubtu24      Stopped         2
  kali        Stopped         2
    ```

- **查看所支持的发行版**

    ```bash
wsl -l -o
    ```

- **卸载某个发行版**

    ```bash
wsl --unregister ubtu24
    ```

---

## 进入和退出
<br>
进入和退出某个 Linux 发行版，可参考以下操作。

- **启动进入 wsl 某发行版**

    先看看已安装的发行版：

    ```bash
wsl -l -v 
    ```

    得到如下类似信息：

    ```text
  NAME        STATE           VERSION
* Ubuntu24    Stopped         2
  ubtu24      Stopped         2
  kali        Stopped         2
    ```

    执行以下命令进入某个 Linux 发行版：

    ```bash
wsl -d ubtn24
    ```

- **退出**

    在某个 Linux 发行版里面时，执行 `exit` 即可退到 Windows 的 PowerShell：

    ```bash
exit
    ```

---

## 安装桌面（可选）
<br>
希望的 wsl 下看到桌面的同学，可尝试安装桌面。相关参考操作步骤如下：

1. **启动进入 wsl 某发行版**

    ```bash
wsl -l -v 
    ```

    可看到如下类似信息：

    ```text
  NAME        STATE           VERSION
* Ubuntu24    Stopped         2
  ubtu24      Stopped         2
  kali        Stopped         2
    ```

    然后启动进入某个 Linux 发行版：

    ```bash
wsl -d ubtn24
    ```

2. **更新 Linux**

    ```bash
sudo apt update && sudo apt upgrade -y
    ```

3. **安装 xrdp 和 GNOME 桌面 **

    ```bash
sudo apt install xrdp -y
    ```

    ```bash
sudo apt install --no-install-recommends ubuntu-desktop -y
    ```

    > 或者安装 ubuntu-desktop-minimal，可能会减少安装的时间。

    > Ubuntu 24.04 中，firefox 和 thunderbird 默认通过 Snap 方式安装，而 WSL 2 默认不支持 Snap（需要额外的 systemd 配置）。因此这两个包在安装时失败，拖累了整个 ubuntu-desktop 的安装。



4. **配置 xrdp 并修改 GNOME 启动参数**

    这是最关键的一步。为了避免与 Windows 本身的远程桌面冲突，将 xrdp 的端口从默认的 3389 改为 3390，并调整一些 GNOME 所需的显示参数和色彩深度。

    备份 xrdp 配置文件：

    ```bash
sudo cp /etc/xrdp/xrdp.ini /etc/xrdp/xrdp.ini.bak
    ```

    修改端口为 3390：

    ```bash
sudo sed -i 's/3389/3390/g' /etc/xrdp/xrdp.ini
    ```

    调整色彩深度 (可提升显示质量)：

    ```bash
sudo sed -i 's/max_bpp=32/#max_bpp=32\nmax_bpp=128/g' /etc/xrdp/xrdp.ini
sudo sed -i 's/xserverbpp=24/#xserverbpp=24\nxserverbpp=128/g' /etc/xrdp/xrdp.ini
    ```

5. **创建 GNOME 会话启动配置**

    这是让 GNOME 桌面顺利启动的关键。需要创建一个 ~/.xsessionrc 文件，并为 GNOME 设置正确的环境变量。

    ```bash
cat > ~/.xsessionrc << EOF
export GNOME_SHELL_SESSION_MODE=ubuntu
export XDG_CURRENT_DESKTOP=ubuntu:GNOME
export XDG_DATA_DIRS=/usr/share/ubuntu:/usr/local/share:/usr/share:/var/lib/snapd/desktop
export WAYLAND_DISPLAY=
export XDG_CONFIG_DIRS=/etc/xdg/xdg-ubuntu:/etc/xdg
EOF
    ```

6. **修改 xrdp 启动脚本**
    
    与 XFCE 类似，你也需要修改 /etc/xrdp/startwm.sh 文件，确保 xrdp 在连接时能找到并启动 GNOME 会话。这里需要注释掉原有的 Xsession 行，并添加 gnome-session 等配置。

    用 nano 或你喜欢的编辑器编辑 startwm.sh
    
    ```bash
sudo nano /etc/xrdp/startwm.sh
    ```

    在文件中找到类似 test -x /etc/X11/Xsession && exec /etc/X11/Xsession 的行，将它们注释掉（在前面加 #），然后添加以下内容：

    ```bash
# 注释掉原来的 Xsession 启动
# test -x /etc/X11/Xsession && exec /etc/X11/Xsession
# exec /bin/sh /etc/X11/Xsession

# 添加以下内容，确保 GNOME 顺利启动
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
gnome-session
    ```

- **启动服务并连接**

    完成配置后，启动 xrdp 服务。

    ```bash
sudo systemctl enable xrdp --now
    ```

    现在，在 Windows 中打开“远程桌面连接”应用：

    - 计算机栏填写：localhost:3390
    - 点击“连接”。
    - 在登录界面，Session 选择 Xorg，然后输入你的 Ubuntu 用户名和密码。


## 简介

### 关于开发板
<br>
本次实践将使用 <img src="https://tnt.gdvzz.com/aikit/dkoo.assets/kunpeng-logo.svg" alt="kunpeng-log" style=" width: auto; height: 1.2rem; max-width: 100%;"> **鲲鹏开发板**，完成相关任务。

开发板外观请参考：

- [鲲鹏开发板指南-外观↗]

### 账号信息
<br>
相关账号信息如下：

- 开发板（账号/密码）： HwHiAiUser / Mind@123
- 开发板（账号/密码）： root / Mind@123
- WiFi（名称/密码）  ： b102 / b102b102

[🔝](#top)

---

## 操作规范
<br>
敬请按照以下要求操作开发板：

- 🚫 **禁止：水杯、饮料瓶等放在桌上**。以免液体泼洒导致开发板损坏。
    
    可放在实验室四周或地上或书包中。

- 🚫 **禁止：电源线、网线等，从桌子四周穿到桌面上**。以免磕碰导致开发板跌落损坏。

    从桌子中间空洞穿到桌面上。

- 🚫 **禁止：开机状态直接拔电源断电**。以免开发板意外损坏。

    可先按关机键关机。确认关机后再拔电源断电。

- ✴️ **书包等物品远离开发板**。以免磕碰导致开发板跌落损坏。<br>

    可放在实验室四周或地上。

[🔝](#top)

---




## 0-上电开机
<br>
插上电源即可开机：

- 鲲鹏：前面板有2个 Type-C 口，电源插入✅**边上**那个（标有 DC 字样）。❌ 不是插入中间的 Type-C。
- 鲲鹏：拿掉顶部的磁吸盖子，看到2个绿灯亮，**✴️ 并且风扇在转**，就表示开机完成。

[🔝](#top)

---

## 1-连网线
<br>
将PC（个人电脑）和开发板用网线连起来：

- 网线一端连接PC（个人电脑），另一端连接开发板的以太网口。
- 开发板以太网口指示灯绿色常亮，黄灯闪烁，表示连线正常。

[🔝](#top)

---

## 2-设置PC（个人电脑）IP
<br>
将 PC（个人电脑）的 IP 地址设置为和开发板同一个网段，以便通过网线访问开发板。详见：[Windows指南-设置PC（个人电脑）IP↗]

[🔝](#top)

---

## 3-ping开发板
<br>
在 PC（个人电脑）上 ping 开发板，测试网络连通性。详见：[Windows指南-ping开发板↗]

[🔝](#top)

---

## 4-ssh登录
<br>
可用 MobeXterm 软件登录开发板，详见：[MobaXterm指南-ssh登录↗]

或在PC（个人电脑）的终端 PowerShell 中执行：

```bash
ssh HwHiAiUser@192.168.137.100
```

在屏幕提示信息 `HwHiAiUser@192.168.137.100's password: ` 后面输入密码 `Mind@123`，输完后按 `回车` 键。**✳️ 输入密码过程中，在屏幕上不会显示信息，这是正常的（因为是密码，所以不能显示出来被TA人看到）**

如果遇到以下报错信息：

```bash
~ % ssh HwHiAiUser@192.168.137.100
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
...
```

可以先执行以下命令：

```bash
ssh-keygen -R 192.168.137.100
```

然后再尝试 `ssh HwHiAiUser@192.168.137.100`

[🔝](#top)

---

## 5-连外网
<br>
开发板上电开机后，先让开发板连接外网，即能访问互联网。后续创建本次实验所需的 Python 虚拟环境，需要开发板能访问外网。开发板如何连接外网，请参考：[鲲鹏开发板指南-连WiFi↗]

连接外网后，在开发板上执行以下命令，验证是否确实能访问外网：

```bash
curl -fsSL www.baidu.com
```

[🔝](#top)

---

## 6-代码调测
<br>
建议按如下步骤开展：

1. **创建 conda 虚拟环境**

    ```bash
conda create -n chke2607 python=3.10
    ```

    - ✅ Conda 应该是正常的。如果不能成功创建虚拟环境，请实验室老师协助。
    - ❌ 不要参考AI的建议，对 Conda 的相关设置做修改。
    - 在虚拟环境中开展实验，可和开发板上的其他项目互不影响。

2. **激活虚拟环境**

    ```bash
conda activate chke2607
    ```

3. **创建实验用目录**


    ```bash
mkdir ~/chkin2607
    ```

4. **上传源码到开发板的实验目录中**

    **方式一：** 在本地电脑敲命令传文件。请参考：[Linux常用操作↗](https://tnt.gdvzz.com/aikit/linuxug.html) \| scp 远程复制文件/目录。比如：
    
    ```bash
scp main.py HwHiAiUser@192.168.137.100:/home/HwHiAiUser/chkin2607
    ```

    **方式二：** 或者粘贴到开发板上**

    先进入开发板上的实验目录

    ```bash
cd ~/chkin2607    
    ```

    在实验目录下编辑文件（新建一个空文件）

    ```bash
vim main.py
    ```

    在 vim 界面上：按 `Esc` → 按 `i` → 粘贴 → 按 `Esc` → 输入 `:wq` → 按 `Enter回车`

    如果不保存：按 `Esc` → 输入 `:q!` → 按 `Enter回车`

    更多信息请参考：[Linux指南-vim文本编辑↗]

4. **在虚拟环境中安装 PyTorch (CPU 版)**

    ```bash
pip3 install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cpu
    ```

    ✳️ 要先激活虚拟环境，从而确保在虚拟环境中安装相关软件（而不是安装到其他环境中）。相关操作请参考：[Conda指南↗]。

5. **安装其他依赖库**
    
    ```bash
pip3 install yolo5face facenet-pytorch opencv-python-headless numpy==1.26.4 Pillow==10.2.0 pyyaml flask flask-cors
    ```

    ✳️ 要先激活虚拟环境，从而确保在虚拟环境中安装相关软件（而不是安装到其他环境中）。相关操作请参考：[Conda指南↗]。

<br>

**提示：**

- ✴️ Conda（Python）虚拟环境（本文名称样例是 chke0602），创建一次即可。不需要反复重复创建。
- ✳️ Conda 相关操作请参考：[Conda指南↗]

### 参考代码
<br>
以下是参考代码：

[主程序-main.py](./sumc26-3-linux-e2.assets/main.py)<br>
[参考界面1-webapp.py](./sumc26-3-linux-e2.assets/webapp.py)<br>
[参考界面2-app2.py](./sumc26-3-linux-e2.assets/app2.py)<br>
[摄像头可用-camapp.py](./sumc26-3-linux-e2.assets/webapp.py)

以下是部分参考界面：

- **参考界面1：**

    [![ss01](./sumc26-3-linux-e2.assets/ss01.jpg)](./sumc26-3-linux-e2.assets/ss01.jpg)

    <!-- <img src="./aidk260602.assets/ss01.jpg" alt="ss01" style=" width: auto; height: auto; max-width:100%;"> -->

- **参考界面2：**

    [![ss02](./sumc26-3-linux-e2.assets/ss02.jpg)](./sumc26-3-linux-e2.assets/ss02.jpg)
    
    <!-- <img src="./aidk260602.assets/ss02.jpg" alt="ss02" style=" width: auto; height: auto; max-width:100%;"> -->

[🔝](#top)

---

## 小结
<br>
回顾使用过的操作。（待补充）

[🔝](#top)

---

## 关机断电复位离开
<br>
实验结束后，请完成以下事项，再离开实验课。

1. **关机断电**

    开发板要先关机、再断电。🚫 **严谨开机状态直接断电（拔电源）！**

    - <img src="https://tnt.gdvzz.com/aikit/dkoo.assets/kunpeng-logo.svg" alt="kunpeng-log" style=" width: auto; height: 1.2rem; max-width: 100%;"> **鲲鹏**：[关机断电↗](https://tnt.gdvzz.com/aikit/dkoo.html#onoff) 

2. **归还实验器材，给实验室老师**

    - 开发板
    - 开发板电源
    - 网线
    - 借用的其他器材

3. **椅子复位**

    - 每个桌子，配套 6 个椅子。请将椅子推到桌子下面。
    - 西侧玻璃门，前中后靠墙，各 6 个。共 18 个。请按此数量靠墙摆放。

4. **带齐随身物品**

✅ 上述事项完成后，可离开实验室。

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

<!--  -->
[鲲鹏开发板指南-连WiFi↗]: https://tnt.gdvzz.com/aikit/dkoo.html#wifi
[鲲鹏开发板指南-普通用户访问摄像头↗]: https://tnt.gdvzz.com/aikit/dkoo.html#access-camera
[鲲鹏开发板指南-外观↗]: https://tnt.gdvzz.com/aikit/dkoo.html#photo
[Conda指南↗]: https://tnt.gdvzz.com/aikit/condaug.html
[Linux指南-vim文本编辑↗]: https://tnt.gdvzz.com/aikit/linuxug.html#vim
[MobaXterm指南-ssh登录↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html#ssh
[Windows指南-设置PC（个人电脑）IP↗]: https://tnt.gdvzz.com/aikit/windowsug.html#setip
[Windows指南-ping开发板↗]: https://tnt.gdvzz.com/aikit/windowsug.html#pingdk


<!--  -->
[Windows跑AI Agent，WSL才是终极答案，别羡慕Mac了， WSL保姆级全攻略，海量实战教程，一期视频精通]: https://www.bilibili.com/video/BV1pYNm69EPm