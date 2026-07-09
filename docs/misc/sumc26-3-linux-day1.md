---
title: Linux速成-2607-Day#1
layout: default
parent: Linux速成-2607
nav_order: 1
# nav_exclude: true
---

# Linux速成-2607-Day#1
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

## 实验简介

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


<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

<!--  -->
[鲲鹏开发板指南-外观↗]: https://tnt.gdvzz.com/aikit/dkoo.html#photo
[Windows指南-设置PC（个人电脑）IP↗]: https://tnt.gdvzz.com/aikit/windowsug.html#setip
[Windows指南-ping开发板↗]: https://tnt.gdvzz.com/aikit/windowsug.html#pingdk
[MobaXterm指南-ssh登录↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html#ssh
[鲲鹏开发板指南-普通用户访问摄像头↗]: https://tnt.gdvzz.com/aikit/dkoo.html#access-camera