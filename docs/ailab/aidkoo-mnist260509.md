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

<details markdown="block">
    <summary>
        ✳️ 目录
    </summary>
- TOC
{:toc}
</details>

---

## 实验简介



---

## 实验目的

---

## 座位设备对应

---

## 上电开机

---

## 连接外网
<br>
开发板上电开机后，先让开发板连接外网，即能访问互联网。后续创建本次实验所需的 Python 虚拟环境，需要开发板能访问外网。开发板如何连接外网，请参考：

- 昇腾开发板：[连接外网↗](https://tnt.gdvzz.com/aikit/aidk.html#nets)
- 鲲鹏开发板：[连接外网↗](https://tnt.gdvzz.com/aikit/dkoo.html#nets)

---

## 创建环境
<br>
创建
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

