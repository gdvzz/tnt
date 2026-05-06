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

<details markdown="block">
  <summary>
    目录
  </summary>
- TOC
{:toc}
</details>

---

## 连接外网



---

## 创建环境

用 conda 创建 Python 3.10 的虚拟环境：

```bash
conda create -n minst0509 python=3.10
```

激活刚创建的虚拟环境：

```bash
conda activate minst0509
```

在虚拟环境中安装：

```bash
pip3 install torch torchvision "numpy<2" flask
```

```bash
pip3 install torch torchvision "numpy<2" flask --index-url https://download.pytorch.org/whl/cpu
```

