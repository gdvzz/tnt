---
title: 昇腾开发板
layout: default
parent: aikit教具
# nav_order: 30
# nav_exclude: true
---

# 昇腾开发板
{: .no_toc }
`更新-260507` \| `发布-260506`

本文档描述 **昇腾开发板** 的相关信息，用于快速熟悉和入门教具。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!-- <details markdown="block">
    <summary>ℹ️ 更新历史</summary>
<br>
**260506**
- 新增：[连接外网](#连接外网)
</details> -->

---

## 默认信息
<br>
操作系统烧录后，有以下默认信息：

### 默认账号密码
<br>
昇腾开发板的默认账号密码如下：

- 账号：`HwHiAiUser` \| 密码：`Mind@123`
- 账号：`root` \| 密码：`Mind@123`

### 默认IP
<br>
鲲鹏开发板的默认 IP 如下：

- IP地址：`192.168.137.100`
- 子网掩码：`255.255.255.0`

---

<span id="nets"></span>
## 连接外网

### 方法一：共享网络
<br>
可参考开发板官网的 [通过PC共享网络联网（Windows）↗](https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/23.0.RC2/Hardware%20Interfaces/hiug/hiug_0010.html)

上述指导，以“可以访问互联网的 WiFi，共享给开发板”为例。也可以将“本地电脑可以访问互联网的以太网（插网线的），共享给开发板”，操作步骤是一样的。

本地电脑连2个网线（以太网），1个连开发板：**以太网（连开发板）**，1个连外网（可以访问互联网）：**以太网（连外网）**。

以太网（连外网）：
- 点击 **更多适配器选项** 右边的 **编辑** 按钮
- 在 **以太网（连外网）属性** 界面中，有2个 tab 页：网络和共享，选择 **共享** tab页
- 中间的**请选一个专用网络连接**，选择 **以太网（连开发板）**
- 2个 **允许其他网络用户……**，都勾选上
- 按 **确定** 按钮

![network-share0](./dkoo.assets/network-share0.jpg)

提示框显示：“Internet 连接共享被启用时……”，点击 **是(Y)**

![network-share1](./dkoo.assets/network-share1.jpg)

### 方法二：连网线

给开发板再接一根网线，通过这根网线是可以访问互联网的（比如实验室的网线）。该网线插入开发板上下排列的2个网口的 **👇下面那个网口**。

还需要对网络设置做微调。操作步骤如下：

1. 然后用另一根网线，连接本地电脑和开发板。这根网线插入开发板上下排列的2个网口的 **👆上面那个网口**。

2. 在本地电脑的 **终端** 应用中执行 `ssh root@192.168.137.100` 登录开发板。或者使用 MobeXterm 软件登录开发板。本地电脑先要配置 IP 地址，和开发板一个网段，比如 192.168.137.111。

3. 进入网络配置目录：

    ```bash
    cd /etc/netplan
    ```

4. 先备份原有网络配置信息：

    ```bash
    cp 01-netcfg.yaml 01-netcfg.bak年月曰
    ```

    比如，`cp 01-netcfg.yaml 01-netcfg.bak260506`

5. 修改 01-netcfg.yaml 为如下内容：

    ```yaml
    network:
    version: 2
    renderer: networkd
    ethernets:
        eth0:
        dhcp4: yes
        nameservers:
            addresses: [8.8.8.8, 114.114.114.114]   # 修正：合并为一个列表

        eth1:
        dhcp4: no
        addresses: [192.168.137.100/24]
        routes:
            - to: default
            via: 192.168.137.1
            metric: 200          # 添加 metric，值大于 eth0 的 100，降低优先级
        nameservers:
            addresses: [8.8.8.8, 114.114.114.114]   # 修正列表

        usb0:
        dhcp4: no
        addresses: [192.168.0.2/24]
    ```

6. 让修改后的网络配置生效：

    ```bash
    netplan try
    ```

    如果网络配置信息正确，屏幕提示按回车键生效。请按 **回车键** 生效。

    或者觉得配置肯定正确，也可以改为直接执行 `netplan apply`。

7. 验证是否可访问互联网：

    ```bash
    curl -fsSL www.baidu.com
    ```

    如果能获取网页的信息，就表明开发板可以访问互联网了。

---

<span id="onoff"></span>

## 关机、断电和开机
<br>
✴️ 完成实验后，请先关机，再断电（拔掉电源）。

✳️ 实验期间如需重启开发板，可先关机，再开机。

### 关机
<br>
**方法一：按关机按钮**

电源插头的附近，有3个小按钮。短按中间那个按钮，可关机。

**方法二：poweroff关机**

或者执行以下命令也可关机：

```bash
su - root        # 切换到 root，密码是 Mind@123
poweroff
```

**方法三：shutdown关机**

或者执行以下命令也可关机：

```bash
su - root        # 如果不是 root 用户，先切换到 root，密码是 Mind@123
shutdown -h now  # shutdown 马上关机
```

✅ **（3个绿灯：亮1个、灭2个）**表示开发板已安全关机。


### 断电
<br>
待关机后 **（3个绿灯：亮1个、灭2个）**，从电源接口处拔掉电源线切断外部电源，将开发板完全断电。

🚫 严禁开机状态直接拔电源（不能 3 个绿灯都亮着时，就拔电源）。在 Linux 系统运行的过程中，如果直接拔掉电源断电，可能会导致文件系统丢失某些数据。

### 开机
<br>
电源插头的附近，有3个小按钮。关机状态下，短按中间那个按钮，开发板开机，直到 3个绿灯都点亮，网络正常连通，代表开发板已正常开机运行。

断电状态下（没有插电源），插上电源即可开机。

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>