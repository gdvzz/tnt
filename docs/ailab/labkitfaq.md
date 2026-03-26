---
title: AI教具维护
layout: default
parent: AI Lab
# nav_order: 9001
nav_exclude: true
---

# AI教具维护
{: .no_toc }
`更新-260326` \| `发布-260326`

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

## 约定

视觉实验箱：vkai
NLP 实验箱：nlpx
昇腾开发板：asdk
鲲鹏开发板：kpdk

----

## vkai-硬盘只有50G

### 问题

在使用大于镜像内存的U盘或者固态硬盘烧录镜像以后，会出现一部分的空闲内存无法被使用，导致出现使用空间不足的报错，或运行大型项目不成功。

注意：本教程仅针对自行烧录镜像的用户，U盘或者固态硬盘内如有出厂镜像则可跳过本教程。U盘和固态硬盘的扩容方式相同，本节以Jetson Nano（U盘）为例。

### 解决方案

安装扩容软件，使用扩容软件进行扩容。

```bash
sudo apt install gparted
```

1. 打开该软件，找到硬盘。‼️注意，此步骤一定要确认操作的硬盘设备号是正确的。

    如果是Jetson Orin NX/Orin Nano主板使用固态硬盘，设备号是【/dev/nvme0n1】（👈 vkai 是这个）
    
    Jetson Nano系统找到【/dev/sda】设备。

2. 选中设备主分区【APP】，右键选择【Resize/Move】。

3. 将右边的框拉到顶，直至灰色区域变为全白，然后点击 **Resize**

4. 点击功能栏下方的绿色的钩，再点击 **Apply**

完成扩容后，使用指令在终端进行查询验证

```bash
df -h
```

> 参考资料：[JetCobot 机械臂 > Linux操作系统 > 13.扩容教程↗](https://www.yahboom.com/build/id/10424/cid/648)

> 要输入提取码才能访问。

