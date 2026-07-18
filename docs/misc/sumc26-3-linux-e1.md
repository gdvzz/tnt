---
title: e1-初识开发板
layout: default
parent: Linux速成-2607
nav_order: 1
# nav_exclude: true
---

# e1-初识开发板（Linux速成-2607）
{: .no_toc }
`更新-260709` \| `发布-260709`

通过初识（华为）开发板，熟悉 Linux 相关操作。

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

---

## 0-上电开机
<br>
插上电源即可开机：

- 鲲鹏：前面板有2个 Type-C 口，电源插入✅**边上**那个（标有 DC 字样）。❌ 不是插入中间的 Type-C。
- 鲲鹏：拿掉顶部的磁吸盖子，看到2个绿灯亮，**✴️ 并且风扇在转**，就表示开机完成。

---

## 1-连网线
<br>
将PC（个人电脑）和开发板用网线连起来：

- 网线一端连接PC（个人电脑），另一端连接开发板的以太网口。
- 开发板以太网口指示灯绿色常亮，黄灯闪烁，表示连线正常。

---

## 2-设置PC（个人电脑）IP
<br>
将 PC（个人电脑）的 IP 地址设置为和开发板同一个网段，以便通过网线访问开发板。详见：[Windows指南-设置PC（个人电脑）IP↗]

---

## 3-ping开发板
<br>
在 PC（个人电脑）上 ping 开发板，测试网络连通性。详见：[Windows指南-ping开发板↗]

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


---

## 5-登录Jupyter Lab
<br>
为方便新手开发者进行应用开发和程序运行，镜像中已包含jupyter lab软件（可视化代码演示、数据分析工具），可为用户提供一个图形化运行推理样例的界面。

1. **进入 notebooks 目录**

    ```bash
cd ~/samples/notebooks
    ```

2. **启动 Jupyter Lab**

    ```bash
./start_notebook.sh 192.168.137.100
    ```

3. **在PC（个人电脑）访问 Jupyter Lab**

    复制界面上出现的 http://192.168.137.100 那行，在PC（个人电脑）的浏览器中访问

    ```bash
    ...
    [I 2026-04-27 23:11:42.675 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
    [C 2026-04-27 23:11:42.753 ServerApp] 
        
        To access the server, open this file in a browser:
            file:///root/.local/share/jupyter/runtime/jpserver-3838-open.html
        Or copy and paste one of these URLs:
            http://192.168.137.100:8888/lab?token=一串字母数字
            http://127.0.0.1:8888/lab?token=一串字母数字
    ...
    ```

    ✳️ 如上述界面信息提示：同时按下 `Control` + `C` 可停止Jupyter Lab Server。

    在PC（个人电脑）浏览器看到如下界面：

    ![aidk-demo](https://tnt.gdvzz.com/aikit/aidk.assets/aidk-demo.jpg)

---

## 6-体验目标检测样例
<br>
✳️ 以下操作在PC（个人电脑）的浏览器中执行。

1. 打开 **01-yolov5** 目录，再双击打开 **main.ipynb**

2. main.ipynb：修改 infer_mode 为 `infer_mode = 'image'` 

3. 点击浏览器顶部的双箭头 ▶︎▶︎，再点击 **Restart** 按钮。

    ![aidk-01yolors](https://tnt.gdvzz.com/aikit/aidk.assets/aidk-01yolors.jpg)
    
    稍后可看到图片识别结果：

    ![aidk-01yoloi](https://tnt.gdvzz.com/aikit/aidk.assets/aidk-01yoloi.jpg)

4. 修改 infer_mode 为 `infer_mode = 'video'` 

5. 点击浏览器顶部的双箭头 ▶︎▶︎，再点击 **Restart** 按钮。稍后可看到视频识别结果：

    ![aidk-01yolov](https://tnt.gdvzz.com/aikit/aidk.assets/aidk-01yolov.jpg)

6. 修改 infer_mode 为 `infer_mode = 'camera'`

7. 把 USB 摄像头连接到开发板的 USB 口

8. 点击浏览器顶部的双箭头 ▶︎▶︎，再点击 **Restart** 按钮。稍后可看到摄像头识别结果

    ![aidk-01yoloc](https://tnt.gdvzz.com/aikit/aidk.assets/aidk-01yoloc.jpg)

    > 注：截图展示了用摄像头拍摄另一个PC上显示的照片的识别结果。

    ✴️ 如无法使用摄像头，请参考：[鲲鹏开发板指南-普通用户访问摄像头↗]

---

## 7-修改目标检测
<br>
尝试修改目标检测样例代码，以加深对样例的理解：

1. 上传其他图片、视频，到开发者套件的相应目录中

2. 修改 **01-yolov5 / main.ipynb** 相关代码

3. 重新运行样例，查看识别结果。


---

## 8-体验其他预置应用
<br>
和目标检测样例类似运行方式，体验其他预置应用。

---

## 小结
<br>
回顾下使用过的操作。

### ping-测试网络连通性
<br>
以 `ping 192.168.137.100` 为例。

🌟 **命令的基本含义**

- ping：是一个最常用的网络诊断工具，用于测试你的设备（源主机）与目标设备（目的主机）之间的网络连通性。
- 192.168.137.100：这是一个私有IP地址，属于IPv4地址中的C类私有地址段（192.168.0.0 – 192.168.255.255）。它通常用于局域网（比如家庭、办公室或实验室网络）中的设备标识。
合起来，这个命令的意思就是：“我的电脑，请向IP地址为 192.168.137.100 的那台设备发送一个探测数据包，看看它是否在线，以及回应需要多长时间。”

🌟 **执行过程（发生了什么）**

当你按下回车键后，系统会依次进行以下操作：

1. 解析目标地址：系统先检查本机的路由表和ARP缓存，确认 192.168.137.100 是否在同一个局域网子网内。
2. 发送ICMP回显请求：你的设备向目标IP发送一个 ICMP（互联网控制报文协议） 类型的报文，叫做 Echo Request（回显请求）。
3. 等待回应：如果目标设备在线且网络正常，它会收到这个请求，并回复一个 Echo Reply（回显应答）。
4. 统计结果：ping 程序会记录发送和接收的时间差（往返时延，RTT），并显示在屏幕上。

🌟 **你会看到的典型输出（及解读）**

成功时，你会看到类似这样的信息：

```text
正在 Ping 192.168.137.100 具有 32 字节的数据:
来自 192.168.137.100 的回复: 字节=32 时间=2ms TTL=64
来自 192.168.137.100 的回复: 字节=32 时间=1ms TTL=64
来自 192.168.137.100 的回复: 字节=32 时间=3ms TTL=64
来自 192.168.137.100 的回复: 字节=32 时间=2ms TTL=64

192.168.137.100 的 Ping 统计信息:
    数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
往返行程的估计时间(以毫秒为单位):
    最短 = 1ms，最长 = 3ms，平均 = 2ms
```

- 时间=2ms：表示数据包一来一回用了2毫秒，数值越小说明网络延迟越低。
- TTL=64：表示数据包在网络中最多还能经过64个路由器（跳数），TTL初始值由目标设备的操作系统决定（Linux通常64，Windows通常128）。

🌟 **如果失败（不通），可能的原因**

如果显示“请求超时”或“无法访问目标主机”，常见原因有：

- 目标设备（192.168.137.100）没有开机或断网。
- 你的设备和目标设备不在同一个子网，且没有配置路由。
- 目标设备的防火墙拦截了ICMP请求（很多设备默认禁Ping）。
- IP地址输入错误，或该IP没有被分配给任何设备。

**实用扩展：常用参数**

你可以加上一些参数让 ping 更有用。此处从略，请和AI交流。

### ssh登录
<br>
以 `ssh HwHiAiUser@192.168.137.100` 为例。

🌟 **命令的基本含义**

- ssh：是 Secure Shell（安全外壳协议）的缩写，是一种加密的网络传输协议，主要用于远程安全登录到另一台计算机，并在远程执行命令。
- HwHiAiUser：这是登录用户名。这个用户名很特别，它是华为（Huawei） 昇腾（Ascend）AI处理器相关设备（如Atlas开发板、AI加速模块等）的默认系统用户名。
- @：分隔符，用来分隔用户名和主机地址。
- 192.168.137.100：目标设备的IP地址（和前面Ping的是同一个地址）。

合起来，这个命令的意思是：“我的电脑，请使用SSH协议，以‘HwHiAiUser’这个用户身份，安全地连接到IP地址为 192.168.137.100 的那台华为昇腾设备上。”

🌟 **执行过程（发生了什么）**

当你按下回车后，会经历以下几个阶段：

1. TCP连接建立。你的电脑向目标IP的 22号端口（SSH默认端口）发起TCP连接请求。
2. 版本协商。双方交换SSH协议版本号，确认使用相同的版本。
3. 密钥交换 & 加密协商。双方通过算法协商，生成会话加密密钥（这个过程是明文的，但用于建立后续的加密通道）。
4. 服务器身份验证。目标设备会出示自己的主机公钥，你的电脑会询问你是否信任该主机的指纹（如果是第一次连接）。
5. 用户认证。你被要求输入 HwHiAiUser 对应的密码（或使用密钥认证）。
6. 授权登录。密码验证通过后，SSH服务会为你启动一个Shell（命令行环境），你就成功登录到目标设备了。

🌟 **首次连接时的“指纹确认”**

如果是第一次连接这台设备，你会看到类似这样的提示：

```text
The authenticity of host '192.168.137.100 (192.168.137.100)' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)?
```

- 这是SSH为了防止中间人攻击而做的安全机制。
- 你可以输入 yes 并回车，该主机的公钥就会被保存到你电脑的 ~/.ssh/known_hosts 文件中，下次连接就不会再提示了。

🌟 **输入密码**

确认指纹后，系统会提示你输入密码：

```text
HwHiAiUser@192.168.137.100's password:
```

- 默认密码：华为昇腾设备（如Atlas 200 DK）的 HwHiAiUser 默认密码通常是 HwHiAiUser 或 Mind@123（具体视固件版本而定）。
- 输入密码时，屏幕上不会显示任何字符（包括星号），这是Linux的安全设计，正常输入后按回车即可。

🌟 **登录成功后的状态**

密码正确后，你会看到类似这样的欢迎信息，并进入目标设备的命令行：

```text
Welcome to Huawei Atlas 200 DK
HwHiAiUser@atlas:~$
```

此时，你就像坐在那台设备面前一样，可以执行各种Linux命令，比如：

- npu-smi info —— 查看AI芯片状态
- ls —— 查看文件列表
- ifconfig —— 查看网络配置
- python3 —— 运行Python程序


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
[鲲鹏开发板指南-外观↗]: https://tnt.gdvzz.com/aikit/dkoo.html#photo
[Windows指南-设置PC（个人电脑）IP↗]: https://tnt.gdvzz.com/aikit/windowsug.html#setip
[Windows指南-ping开发板↗]: https://tnt.gdvzz.com/aikit/windowsug.html#pingdk
[MobaXterm指南-ssh登录↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html#ssh
[鲲鹏开发板指南-普通用户访问摄像头↗]: https://tnt.gdvzz.com/aikit/dkoo.html#access-camera