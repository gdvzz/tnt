---
title: Conda指南
layout: default
parent: aikit教具
nav_order: 90
# nav_exclude: true
---

# Conda指南
{: .no_toc }
`更新-260522` \| `发布-260522`

本文档描述 Conda 常用操作，供同学参考。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<!-- <details>
    <summary>ℹ️ 更新历史</summary>
<br>

**260519：新增vim**

</details> -->

---

## 为什么需要 Conda
<br>
以下信息摘自网络文章“<ins>Python中的Anaconda（Conda）是什么？为什么需要它？</ins>” [^2]，供了解 conda 大致是什么。感兴趣同学还可查看 B 站视频“<ins>15分钟彻底搞懂！Anaconda Miniconda conda-forge miniforge Mamba</ins>”[^3] 获得更多信息。

Python是一种有特别多用处的计算机语言，可以用来做网页开发、数据分析以及AI等几乎大多数事情。每一个目的都需要特定的“包（packages）”。

与此同时，不仅会用到不同包的，甚至用到的Python版本都是不一样的。

问题是，你只有一台电脑，不可能为了新作一个项目就需要买一台新电脑......因此，我们通过“虚拟环境”来完成同一台电脑 开发管理多个项目的事情。我们可以针对具体的项目、逐一对应地开发虚拟环境。可以用多个虚拟环境来做多个数据开发、多个虚拟环境来做网页开发的事情ect.。

因此，在做不同的python项目，用到不同包、不同python版本时，虚拟环境的作用就出来了。

在python官网下载python，与此同时就会下载 **pip（Python integrated package managemer）**（所以顾名思义，pip的目的就是用来管理包）；如果想要管理一台电脑上的多个环节，那就可以下载virtualenv，帮助我们管理虚拟环境（但也并不是说管理虚拟环境只有这一个工具）。

如果想用python，也不一定必须要在python官网下载，替代方案是：下载Ananconda（Anaconda 和 Python 是“包含关系”，Anaconda 包含了 Python）。在下载Anaconda（或者是miniconda）后，Conda就会装在我们的电脑系统上。 Conda既可以做包的管理，也可以管理虚拟环境。（PS：miniconda可以理解为轻量化的Anaconda；miniconda通常在终端操作，Anaconda通常是图形化页面）

那 pip 和 venv 还用不用？

- Pip 是 Python 官方的包管理工具，更“原生”，适合轻量项目
- Conda 更适合安装大型包和管理多个项目的环境
- 二者可以搭配使用：Conda 管环境，pip 装特定包

---

## 在 Jetson 开发板安装 conda
<br>
在 Jetson 开发板上启动 **终端 Terminal** App，然后输入 `conda` 并回车。执行后如果屏幕显示“命令没有找到”之类的信息，则表明尚未安装，请参考如下命令先安装 Conda。

1. **建个临时目录**

    ```bash
mkdir ~/tmp2603
    ```

    > 临时目录的名字可随意。

2. **进入临时目录**

    ```bash
cd ~/tmp2603
    ```
3. **从科大镜像下载安装包**

    ```bash
wget https://mirrors.ustc.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-aarch64.sh
    ```

4. **安装**

    ```bash
bash Miniforge3-Linux-aarch64.sh
    ```
    > 安装过程中，请仔细阅读提示。并在询问“是否初始化Miniforge3”时输入 yes。

5. **安装完成后，关闭并重新打开终端，或者执行以下命令使配置生效：**
    
    ```bash
source ~/.bashrc
    ```

✅ Done！之后，你的命令行前会出现 (base) 字样，表示基础环境已激活。

---

## Conda常用命令
<br>
以下是 Conda 常用命令。更多命令可执行 `conda --help` 得到。

- **显示虚拟环境列表**

    ```bash
conda env list
    ```

- **进入/退出某个虚拟环境**
    
    进入（激活）某个虚拟环境：

    ```bash
conda activate <虚拟环境名>
    ```

    > 比如要激活虚拟环境名称叫 abc，则执行 `conda activate abc`。执行成功后，命令行提示符头部会显示`(abc)`。

    在某个虚拟环境中，执行如下命令可退出（去激活）该虚拟环境：

    ```bash
conda deactivate
    ```

    假定当前在虚拟环境 abc 中。执行上述去激活命令后，命令行提示符头部的 `(abc)` 会变化：消失（回到非虚拟环境）；或者显示 `(base)`（假定是从 `(base)` 虚拟环境执行 `conda activate abc` 激活 abc 虚拟环境的）

- **删除虚拟环境**

    执行 `conda remove` 命令可删除虚拟环境：

    ```bash
conda remove -n <虚拟环境名> --all
    ```

    比如执行 `conda remove -n myenv --all`，可以 remove all packages from environment `myenv` and the environment itself。


<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

<!--  -->
[^1]: 在 Ubuntu 主界面左侧导航栏找到对应的 App，或者在顶部搜索栏输入 App 的名字查找。
[^2]: [Python中的Anaconda（Conda）是什么？为什么需要它？↗](https://zhuanlan.zhihu.com/p/1919115719272010247)；知乎；2025-06-19
[^3]: [15分钟彻底搞懂！Anaconda Miniconda conda-forge miniforge Mamba ↗](https://www.bilibili.com/video/BV1Fm4ZzDEeY)；B站；2025-08-07