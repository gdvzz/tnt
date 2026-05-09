---
title: 鲲鹏开发板
layout: default
parent: aikit教具
# nav_order: 30
# nav_exclude: true
---

# 鲲鹏开发板
{: .no_toc }
`更新-260509` \| `发布-260420`

本文档描述 **鲲鹏开发板** 的相关信息，用于快速熟悉和入门教具。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<details markdown="block">
  <summary>ℹ️ 更新历史</summary>

**260509**
- 新增：[连WiFi](#连wifi)
- 新增：[更改默认静态IP](#更改默认静态ip)

**260506**
- 新增：[连接外网](#连接外网)

</details>

---

## 默认信息
<br>
操作系统烧录后，有以下默认信息：

### 默认账号密码
<br>
鲲鹏开发板的默认账号密码如下：

- 账号：`HwHiAiUser` \| 密码：`Mind@123`
- 账号：`root` \| 密码：`Mind@123`

### 默认IP
<br>
鲲鹏开发板的默认 IP 如下：

- IP地址：`192.168.137.200`
- 子网掩码：`255.255.255.0`

---

<span id="nets"></span>
## 连接外网
<br>
可以有几种方法：

- 找一个可以连接外网的PC（个人电脑），将可以连接外网的那个网络，共享给开发板
- 开发板连接可以访问外网的WiFi

### PC共享网络
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

### 连WiFi

先 root 用户登录开发板。或者已登录开发板，切换为 root 用户。

- `nmcli dev wifi`：查看有哪些WiFi

    ```bash
    (base) root@orangepiaipro:~# nmcli dev wifi
    IN-USE  BSSID              SSID                MODE   CHAN  RATE        SIGNAL  BARS  SECURITY    
            44:DF:65:E7:BC:65  b102                Infra  6     130 Mbit/s  100     ▂▄▆█  WPA2        
            44:DF:65:E7:BC:64  b102                Infra  48    270 Mbit/s  84      ▂▄▆█  WPA2        
            14:D8:64:D1:D4:F3  b216                Infra  1     270 Mbit/s  80      ▂▄▆_  WPA1 WPA2   
    ```

- `nmcli dev wifi connect "b102" password "b102b102"`：密码方式连接WiFi（WiFi是b102）

    ```bash
    (base) root@orangepiaipro:~# nmcli dev wifi connect "b102" password "b102b102"
    Device 'wlan0' successfully activated with '3d96022d-1711-4206-8ff9-cfb991408b80'.
    ```

    连接 WiFi 成功后，可以执行 `curl -fsSL www.baidu.com` 访问百度是否成功。访问成功表示开发板可以访问外网了。

- `nmcli con down "b102"`：断开和b102的连接
- `nmcli con up "b102"`：连接（曾经连接过的）b102

    ```bash
    (base) root@orangepiaipro:/etc/netplan# nmcli con up "b102"
    Connection successfully activated (D-Bus active path: /org/freedesktop/NetworkManager/ActiveConnection/6)
    ```

- `nmcli con show`：看看连接过哪些 WiFi

    ```bash
    (base) root@orangepiaipro:/etc/netplan# nmcli con show
    NAME          UUID                                  TYPE      DEVICE  
    b102          3d96022d-1711-4206-8ff9-cfb991408b80  wifi      wlan0   
    eth0          112f0b6a-e274-4f66-8198-1c1ac5705217  ethernet  eth0    
    docker0       6fdb6ff7-4ec5-46dc-9937-946a7988d084  bridge    docker0 
    netplan-eth1  8bf25856-ca0b-388e-823c-b898666ab9d2  ethernet  --      
    ```

- `nmcli con del "b102"`：忘记（曾经连接过的）b102

    ```bash
    (base) root@orangepiaipro:/etc/netplan# nmcli con del "b102"
    Connection 'b102' (3d96022d-1711-4206-8ff9-cfb991408b80) successfully deleted.
    ```

- `nmcli radio wifi`：查看 WiFi 状态（开 或 关）

    ```bash
    (base) root@orangepiaipro:/etc/netplan# nmcli radio wifi
    enabled
    ```

- `nmcli radio wifi off`：关闭 WiFi
- `nmcli radio wifi on`：打开 WiFi

- `nmcli device status`：查看网络设备的状态

    ```bash
    (base) root@orangepiaipro:~# nmcli device status
    DEVICE         TYPE      STATE                   CONNECTION 
    eth0           ethernet  connected               eth0       
    docker0        bridge    connected (externally)  docker0    
    wlan0          wifi      disconnected            --         
    p2p-dev-wlan0  wifi-p2p  disconnected            --         
    bond0          bond      unmanaged               --         
    lo             loopback  unmanaged               --   
    ```

---

## 更改默认静态IP
<br>
将开发板默认IP地址修改为 `192.168.137.100`。

- root 用户登录开发板

- 修改 /etc/netplan/01-netcfg.yaml，内容如下：

```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.137.100/24
      routes:
        - to: default
          via: 192.168.137.1
          metric: 700
      nameservers:
        addresses: [8.8.8.8, 114.114.114.114]
```

- 先应用新的 IP 地址

```bash
netplan try
```

- 再删除通过 UI 界面配置的 IP 地址

先看看 eth0 对应的配置 NAME（看到是 `Profile 1`）

```bash
(base) root@orangepiaipro:/etc/netplan# nmcli conn show
NAME          UUID                                  TYPE      DEVICE  
b102          1363b997-7e0b-4953-a004-807b7d6de1fc  wifi      wlan0   
Profile 1     14db5d66-2a23-4b83-893e-f7e53ff1db06  ethernet  eth0    
docker0       6fdb6ff7-4ec5-46dc-9937-946a7988d084  bridge    docker0 
netplan-eth0  626dd384-8b3d-3690-9511-192b2c79b3fd  ethernet  --      
```

然后删除 eth0 对应的 `Profile 1`：

```bash
(base) root@orangepiaipro:/etc/netplan# nmcli conn del "Profile 1"
Connection 'Profile 1' (14db5d66-2a23-4b83-893e-f7e53ff1db06) successfully deleted.
```

---

## 体验样例代码
<br>
除了可体验鲲鹏开发板自带的预置样例外，还可以通过如下方式体验升腾开发板的预置样例。

1. 点击下载：[昇腾开发板预置样例代码↗]

2. 建议放到开发板指定目录下。zip 包名为 `samples_aidk.zip`，600多MB，网速不同下载耗时不同。将下载的 zip 包上传 / 移动到用户 `HwHiAiUser` 的 HOME 目录下，完整路径是  `/home/HwHiAiUser`。

3. 解压缩。依次执行以下命令：

    先切换到 HOME 目录

    ```bash
    cd ~
    ```

    然后解压缩

    ```bash
    unzip samples_aidk.zip
    ```

    解压缩完成后，生成目录 samples_aidk，完整路径是  `/home/HwHiAiUser/samples_aidk`。

4. 启动样例代码服务端。依次执行以下命令：

    先切换样例所在目录

    ```bash
    cd ~/samples_aidk/notebook
    ```

    然后启动 Jupyter lab 服务端

    ```bash
    ./start_notebook.sh 192.168.137.200
    ```

    ✳️ 然后复制界面上出现的 `http://192.168.137.100:8888/lab?token=一串数字字母`。

5. 本地电脑 Web 浏览器体验。在本地电脑 Web 浏览器访问刚才复制的 `http://192.168.137.100:8888/lab?token=一串数字字母`

    ✳️ 后续体验步骤，可参考：[熟悉昇腾开发者套件↗]。

6. 部分截图

![dkoo-01yolo1](./dkoo.assets/dkoo-01yolo1.jpg)
![dkoo-01yolo2](./dkoo.assets/dkoo-01yolo2.jpg)
![dkoo-01yolo3](./dkoo.assets/dkoo-01yolo3.jpg)
![dkoo-01yolo4](./dkoo.assets/dkoo-01yolo4.jpg)
![dkoo-01yolo5](./dkoo.assets/dkoo-01yolo5.jpg)
![dkoo-01yolo6](./dkoo.assets/dkoo-01yolo6.jpg)
<!-- ![aidk-01yoloc](./dkoo.assets/aidk-01yoloc.jpg)
![aidk-01yoloi](./dkoo.assets/aidk-01yoloi.jpg)
![aidk-01yolov](./dkoo.assets/aidk-01yolov.jpg)
![aidk-01yolors](./dkoo.assets/aidk-01yolors.jpg)
![aidk-demo](./dkoo.assets/aidk-demo.jpg) -->

---

<span id="onoff"></span>

## 关机、断电和开机
<br>
✴️ 完成实验后，请先关机，再断电（拔掉电源）。

✳️ 实验期间如需重启开发板，可先关机，再开机。

### 关机
<br>
**方法一：按关机按钮**

开发板盒子的绿灯边上有个**关机按钮**。按一下，就可以关机。

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

✳️ 可以拿掉顶部的磁吸盖子，就可以看到散热风扇，**散热风扇停止转动**则表示已安全关机。


### 断电
<br>
待关机后 **（散热风扇停止转动）**，从电源接口处拔掉电源线切断外部电源，将开发板完全断电。

🚫 严禁开机状态直接拔电源（不能散热风扇还在转动，就拔电源）。在 Linux 系统运行的过程中，如果直接拔掉电源断电，可能会导致文件系统丢失某些数据。

### 开机
<br>
插上电源即可开机。

✳️ 可以在本地电脑执行 `~ % ping 192.168.137.200`，ping 通了就表示开机完成。

✳️ 也可以拿掉顶部的磁吸盖子，看到2个绿灯亮，就表示开机完成。

✴️ **关机按钮** 只能关机，不能开机。

<!--  -->
[昇腾开发板预置样例代码↗]: https://pan.jiangnan.edu.cn/link/AA3111BE7AEEE54D8486377047D3375185
[熟悉昇腾开发者套件↗]: https://tnt.gdvzz.com/ailab/aidk2604.html

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>