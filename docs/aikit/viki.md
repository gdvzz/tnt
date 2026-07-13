---
title: 视觉实验箱
layout: default
parent: aikit教具
nav_order: 10
# nav_exclude: true
---

# 视觉实验箱
{: .no_toc }
`更新-260713` \| `发布-260515`

本文档描述 **视觉实验箱** 的相关信息，用于快速熟悉和入门教具。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<details markdown="block">
  <summary>ℹ️ 更新</summary>

**260713**
- 新增：[组装和装箱](#组装和装箱)
</details>

---

## 账号信息
<br>
默认账号信息如下：

- 账号 / 密码： root / yahboom
- 账号 / 密码： jetson / yahboom
- WiFi 热点 / 密码：b102 / b102班02

---

## 组装和装箱
<br>
带离实验室，需要装箱。到达目的地后，需要组装后才能使用。

### 装箱
<br>
需要先做以下事宜，才能装箱：

1. **拔下夹爪**

    - 双手分别抓住机械臂（其余部分）和夹爪。
    - 往外柔和拔夹爪，并上下左右轻微晃动。
    - 不要拔下夹爪和机械臂（其余部分）之间的连线。

    拔下后的夹爪（样例图）：
    
    [![claw](./viki.assets/claw-s.jpg)](./viki.assets/claw.jpg)

    在样例图中：

    - 夹爪有 7 字形的四个空洞
    - 另一端有 7 字形的四个接头
    - 对其后插入，夹爪即组装好了。

2. **拔下电源盒的3个插头**

    拔下电源盒的 3 个插头，3 个插头分别插：USB 扩展坞、英伟达开发板、机械臂。如下图所示：

    [![power-plug](./viki.assets/power-plug-s.jpg)](./viki.assets/power-plug.jpg)

3. **拔下电源盒的2个USB口**

    拔下电源盒的 2 个USB口，2 个USB分别插：USB 扩展坞、英伟达开发板。如下图所示：

    [![power-usb](./viki.assets/power-usb-s.jpg)](./viki.assets/power-usb.jpg)

4. **拔下机械臂的2个USB口**

    拔下机械臂的 2 个USB口，2 个USB都插在英伟达开发板。如下图所示：

    [![irobot-usb](./viki.assets/irobot-usb-s.jpg)](./viki.assets/irobot-usb.jpg)

5. **拔下DP显示线**

    拔下连在英伟达开发板的 DP 显示线。如下图所示：

    [![dp](./viki.assets/dp-s.png)](./viki.assets/dp.png)

    ✅ DP线有个卡扣（如图红色箭头），要按下后才能拔出。❌ 不能直接硬拔，会损坏视频接口。

<br>
完成上述事项后，就可以装箱。装箱注意事项：

- 所有器材，都放在箱子的合适位置。❌不能有任何高出箱子的部分。
- 器材周边如有空隙，要安放泡沫（或蓬松纸团）塞紧。以防运输过程晃动而损坏器材。

### 组装
<br>
请按以下步骤组装视觉实验箱：

1. **安装夹爪**

    对齐接头，将夹爪柔和的插回机械臂。

2. **电源盒的3个插头，插入对应插孔**

    - 弯头1：插入USB扩展坞
    - 直头：插入英伟达开发板
    - 弯头2：插入机械臂

3. **电源盒的2个USB，插入对应插孔**

    分别插入：USB扩展坞，英伟达开发板

4. **机械臂的2个USB，插入开发板**

    - 机械臂的2个USB，都插到英伟达开发板。
    - 调整连夹爪顶端摄像头的USB线，不要太紧绷。以免机械臂转动时拉脱USB接口。

5. **连其他线**

    - 鼠标：插 USB 扩展坞
    - 键盘：插 USB 扩展坞
    - 屏幕电源线：一端插 USB 扩展坞，一端插屏幕的Type-C（2个Type-C，随便哪个都可以）
    - 视频线：一端（大）插英伟达开发板，一端（小）插显示屏

6. **插电源线到电源盒**

    插电源线到电源盒，即可启动。

---

## 机械臂体验

机械臂体验，详见：[机械臂体验↗]

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

<!--  -->
[机械臂体验↗]: https://tnt.gdvzz.com/aikit/irobots.html
