---
title: e4-玩转wsl
layout: default
parent: Linux速成-2607
nav_order: 4
# nav_exclude: true
---

# e4-玩转wsl（Linux速成-2607）
{: .no_toc }
`更新-260719` \| `发布-260718`

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

## 参考视频
<br>
本文主要参考：[Windows跑AI Agent，WSL才是终极答案，别羡慕Mac了， WSL保姆级全攻略，海量实战教程，一期视频精通↗]

---

## 操作规范
<br>
敬请按照以下要求操作：

- 🚫 **禁止：水杯、饮料瓶等放在桌上**。以免液体泼洒导致器材损坏。
    
    可放在实验室四周或地上或书包中。

- 🚫 **禁止：电源线、网线等，从桌子四周穿到桌面上**。以免磕碰导致器材跌落损坏。

    从桌子中间空洞穿到桌面上。

- 🚫 **禁止：开机状态直接拔电源断电**。以免器材意外损坏。

    可先按关机键关机。确认关机后再拔电源断电。

- ✴️ **书包等物品远离器材**。以免磕碰导致器材开发板跌落损坏。<br>

    可放在实验室四周或地上。

[🔝](#top)

---

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

    可以看到以下类似信息：

    ```text
      NAME      STATE           VERSION
      Ubuntu24  Stopped         2
    * ubtu24    Stopped         2
      kali      Stopped         2
    ```

- **查看所支持的发行版**

    ```bash
wsl -l -o
    ```

    可以得到以下类似信息：

    ```text
    The following is a list of valid distributions that can be installed.
    Install using 'wsl.exe --install <Distro>'.

    NAME                            FRIENDLY NAME
    Ubuntu                          Ubuntu
    Ubuntu-26.04                    Ubuntu 26.04 LTS
    Ubuntu-24.04                    Ubuntu 24.04 LTS
    Ubuntu-22.04                    Ubuntu 22.04 LTS
    openSUSE-Tumbleweed             openSUSE Tumbleweed
    openSUSE-Leap-16.0              openSUSE Leap 16.0
    SUSE-Linux-Enterprise-15-SP7    SUSE Linux Enterprise 15 SP7
    SUSE-Linux-Enterprise-16.0      SUSE Linux Enterprise 16.0
    kali-linux                      Kali Linux Rolling
    Debian                          Debian GNU/Linux
    AlmaLinux-8                     AlmaLinux OS 8
    AlmaLinux-9                     AlmaLinux OS 9
    AlmaLinux-Kitten-10             AlmaLinux OS Kitten 10
    AlmaLinux-10                    AlmaLinux OS 10
    archlinux                       Arch Linux
    FedoraLinux-44                  Fedora Linux 44
    FedoraLinux-43                  Fedora Linux 43
    eLxr                            eLxr 12.12.0.0 GNU/Linux
    OracleLinux_7_9                 Oracle Linux 7.9
    OracleLinux_8_10                Oracle Linux 8.10
    OracleLinux_9_5                 Oracle Linux 9.5
    SUSE-Linux-Enterprise-15-SP6    SUSE Linux Enterprise 15 SP6    
    ```

    > 编者按：如果网络超时，可多试几次，或稍候再试。

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

3. **安装 xrdp 和 GNOME 桌面**

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

---

## 安装几个智能体
<br>
参考视频，安装几个智能体。

### 安装几个软件
<br>
先安装智能体需要的几个软件，先安装下。

- python：已默认安装。可执行 `sudo apt install python-is-python3` 做个链接。
- git：已默认安装。
- node.js：[官网↗](https://nodejs.org/en/download)


### 安装 Pi
<br>
安装请参考：[Pi官网↗](https://pi.dev/)

### 安装 Hermes
<br>
安装请参考：[Hermes官网↗](https://hermes-agent.nousresearch.com/)

由于网速原因，建议使用国内镜像网站：

```bash
curl -fsSL https://res1.hermesagent.org.cn/install.sh | bash
```

### 让智能体工作
<br>
让智能体工作，完成一个任务。

可以用 Pi（或 Hermes、Codex、Claude Code等）

[🔝](#top)

<!-- ---

## 小结
<br>
回顾使用过的操作。（待补充）

[🔝](#top) -->

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
[Windows跑AI Agent，WSL才是终极答案，别羡慕Mac了， WSL保姆级全攻略，海量实战教程，一期视频精通↗]: https://www.bilibili.com/video/BV1pYNm69EPm