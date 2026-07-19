---
title: e3-重装开发板
layout: default
parent: Linux速成-2607
nav_order: 3
# nav_exclude: true
---

# e3-重装开发板（Linux速成-2607）
{: .no_toc }
`更新-260719` \| `发布-260719`

本文简介重装开发板，以进一步熟悉 Linux 相关操作。

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
<br>
主要完成以下任务：

- 重新烧录开发板的 Linux 操作系统
- 运行一款程序

以鲲鹏开发板（[外观↗]）为例。


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

## 烧录
<br>
烧录软件可以用： balenaEtcher，ascend-devkit-imager。

以下以 ascend-devkit-imager 为例。操作步骤请参考：[昇腾官网-Windows系统制卡↗]。

几点注意事项：

- 🚫 **禁止：开发板上电状态（插着电源，开机或未开机）插拔SD卡**。以免器材意外损坏。

    开发板断电后（先关机再拔掉电源），才能拔出（或插入）SD卡。

- ‼️ **注意：在烧录软件界面，选择要烧录的 SD卡**。以免意外覆盖PC（个人电脑）的硬盘。

- ✳️ **选择本地制卡**。以免从网上下载产生不必要的流量。

    有需要同学请索取本地镜像的 U 盘 或共享地址

[🔝](#top)

---

## 更改静态 IP
<br>
把新烧录的开发板的网口 IP，改成 `192.168.137.100`，以便用于其他实验。镜像中未配置静态 IP。

可以接屏幕、键鼠，然后通过 GUI 修改网口的静态 IP。（有需要同学请索取相关器材）

或者通过命令方式修改。相关步骤如下：

1. 下载 MobaXterm。详见：[MobaXterm指南↗]
2. 通过串口方式访问开发板。详见：[鲲鹏开发板指南-连接串口↗]
3. 修改开发板的静态IP。详见：[鲲鹏开发板指南-更改默认静态IP↗]

如果不喜欢第 2 步的串口界面，还可以让开发板连实验室的 WiFi（详见：[鲲鹏开发板指南-连WiFi↗]），PC（个人电脑）也连实验室的 WiFi，然后通过 `ssh HwHiAiUser@<开发板的WiFi IP地址>` 方式登录开发板。

更改完成后，请尝试连接网线，通过 SSH 登录开发板。详见：[e1-初识开发板（Linux速成-2607）↗]。

[🔝](#top)

---

## 跑通一个程序
<br>
尝试跑通一个使用了开发板 NPU 算力的程序。

样例程序：[test.py](./sumc26-3-linux.assets/test.py)

参考读物：[深入解析：“零”成本迁移：基于 CANN 8.0 生态的 PyTorch on NPU 910B 落地实践↗]

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
[Conda指南↗]: https://tnt.gdvzz.com/aikit/condaug.html
[Linux指南-vim文本编辑↗]: https://tnt.gdvzz.com/aikit/linuxug.html#vim
[MobaXterm指南-ssh登录↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html#ssh
[Windows指南-设置PC（个人电脑）IP↗]: https://tnt.gdvzz.com/aikit/windowsug.html#setip
[Windows指南-ping开发板↗]: https://tnt.gdvzz.com/aikit/windowsug.html#pingdk

<!--  -->
[鲲鹏开发板指南-更改默认静态IP↗]: https://tnt.gdvzz.com/aikit/dkoo.html#setip
[鲲鹏开发板指南-连接串口↗]: https://tnt.gdvzz.com/aikit/dkoo.html#serial
[鲲鹏开发板指南-连WiFi↗]: https://tnt.gdvzz.com/aikit/dkoo.html#wifi
[昇腾官网-Windows系统制卡↗]: https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/latest/qs/qs_0005.html
[外观↗]: https://tnt.gdvzz.com/aikit/dkoo.html#photo
[e1-初识开发板（Linux速成-2607）↗]: https://tnt.gdvzz.com/misc/sumc26-3-linux-e1.html
[MobaXterm指南↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html

<!--  -->
[Windows跑AI Agent，WSL才是终极答案，别羡慕Mac了， WSL保姆级全攻略，海量实战教程，一期视频精通↗]: https://www.bilibili.com/video/BV1pYNm69EPm
[深入解析：“零”成本迁移：基于 CANN 8.0 生态的 PyTorch on NPU 910B 落地实践↗]: https://www.cnblogs.com/ljbguanli/p/19357875