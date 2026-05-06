---
title: 手写数字识别-260509
layout: default
parent: ailab实验课
nav_order: -260509
# nav_exclude: true
---

# 手写数字识别-260509
{: .no_toc }
`更新-260506` \| `发布-260506`

<!--  -->
<!-- <details open markdown="block">
  <summary>
    目录
  </summary>
- TOC
{:toc}
</details> -->

<!-- <details>
    <summary>ℹ️ 更新历史</summary>
<br>

**260501：新增3个岗位**

- [产品运营-音乐方向](#产品运营-音乐方向)
- [前端开发工程师](#前端开发工程师)
- [移动端开发工程师-Android](#移动端开发工程师-android)

</details> -->

<details markdown="block">
    <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

---

## 连接外网


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

---

## 创建环境

用 conda 创建 Python 3.10 的虚拟环境：

```bash
conda create -n mnist0509 python=3.10
```

激活刚创建的虚拟环境：

```bash
conda activate mnist0509
```

在虚拟环境中安装：

```bash
pip3 install torch torchvision "numpy<2" flask
```

```bash
pip3 install torch torchvision "numpy<2" --index-url https://download.pytorch.org/whl/cpu
pip3 install flask opencv-python
```

