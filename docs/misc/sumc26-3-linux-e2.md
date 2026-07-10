---
title: E2
layout: default
parent: Linux速成-2607
nav_order: 1
# nav_exclude: true
---

# Linux速成-2607-E2
{: .no_toc }
`更新-260710` \| `发布-260710`

通过在（华为）开发板实现《基于FaceNet的多人身份识别考勤签到系统》，熟悉 Linux 相关操作。

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

[主程序-main.py](./aidk260602.assets/main.py)<br>
[参考界面1-webapp.py](./aidk260602.assets/webapp.py)<br>
[参考界面2-app2.py](./aidk260602.assets/app2.py)<br>
[摄像头可用-camapp.py](./aidk260602.assets/camapp.py)

以下是部分参考界面：

- **参考界面1：**

    <img src="./aidk260602.assets/ss01.jpg" alt="ss01" style=" width: auto; height: auto; max-width:100%;">

- **参考界面2：**

    <img src="./aidk260602.assets/ss02.jpg" alt="ss02" style=" width: auto; height: auto; max-width:100%;">

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