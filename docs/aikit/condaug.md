---
title: Conda指南
layout: default
parent: aikit教具
nav_order: 90
# nav_exclude: true
---

# Conda指南
{: .no_toc }
`更新-260607` \| `发布-260522`

本文档描述 Conda 常用操作，供同学参考。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<details>
    <summary>ℹ️ 更新历史</summary>
<br>

**260607：Conda 安装（Windows）**

</details>

---

## 为什么需要 Conda
<br>
以下信息摘自网络文章“<ins>Python中的Anaconda（Conda）是什么？为什么需要它？</ins>” [^2]，供了解 conda 大致是什么。

感兴趣同学还可查看：

- B 站视频“<ins>15分钟彻底搞懂！Anaconda Miniconda conda-forge miniforge Mamba</ins>”[^3] 
- 知乎文章“<ins>一文解释 conda,pip,anaconda,miniconda,miniforge</ins>”[^4]


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

<span id="conda-win"></span>

## Conda 安装（Windows）
`[aka] conda-win`

实际是选择安装 miniforge，而不是安装 miniconda。以下步骤在 **Windows 11 专业版 25H2** 验证通过。

1. **下载安装包**

    下载链接：[Miniforge3-Windows-x86_64.exe-清华镜像站↗](https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Windows-x86_64.exe)

    <!-- 下载链接：[Miniforge3-Windows-x86_64.exe-江大云盘↗](https://pan.jiangnan.edu.cn/link/AA8849245EBDE74332B58BD76F474FCE3E) -->

    也可访问：[conda-forge.org/miniforge↗](https://conda-forge.org/miniforge/)，选择 Miniforge3 → Windows → x86_64 对应的 .exe 文件下载。下载链接其实也是 github。

    或者访问：[github.com/conda-forge/miniforge/releases↗](https://github.com/conda-forge/miniforge/releases)，选择 Miniforge3-Windows-x86_64.exe 下载。

2. **安装**

    有2个建议点，如下。其他就也没有什么特别的。

    <ins>**建议点#1：** Select Installation Type（选 Just Me）</ins>

    - Just Me(recommended) （← 建议选择 Just Me）
    - All Users(requires admin privileges)

    建议选择 Just Me。选择后，conda（miniforge） 的路径会自动加入环境变量中，安装完成后就可以用了。

    > 在选择了“All Users（为所有用户）”安装后，后续步骤Advanced Installation Options的“Add installation to my PATH environment variable”选项确实会故意消失。这是 Miniforge（以及 Anaconda/Miniconda 新版安装程序）出于安全考虑所做的设计，而不是故障。这个变化始于 Anaconda 2022.05 和 Miniconda 4.12.0 版本。之所以禁用“所有用户”安装时自动添加 PATH 的选项，是为了修复一个安全漏洞，防止权限提升攻击。简单来说，就是避免低权限用户通过修改系统级 PATH 变量来劫持高权限程序。解决方案：手动添加环境变量，如下：
    >
    > 1. 找到安装路径。先确认你把 Miniforge3 安装在了哪个文件夹。例如：C:\Users\你的用户名\Miniforge3。如果在安装时选择了“所有用户”，它很可能会安装在一个如 C:\ProgramData\miniforge3 的路径下。
    > 
    > 2. 打开环境变量设置。按下键盘上的 `Win` + `S` 键，输入 “环境变量”→ 在搜索结果中选择 “编辑系统环境变量”→ 在弹出的“系统属性”窗口中，点击下方的 “环境变量(N)…” 按钮。
    > 
    > 3. 编辑 Path 变量。在环境变量窗口中，你会看到两个区域。在下面的 “系统变量” 列表中，找到并双击名为 Path 的变量。
    >
    > 4. 添加新的路径。在编辑窗口中，点击右侧的 “新建” 按钮。依次添加以下两条路径（请务必将 你的安装路径 替换成你在第1步找到的实际路径）：（1）你的安装路径\Miniforge3，（2）你的安装路径\Miniforge3\Scripts。例如：如果你的 Miniforge3 文件夹在 C:\ProgramData\Miniforge3，那么你需要添加的就是：（1）C:\ProgramData\Miniforge3；（2）C:\ProgramData\Miniforge3\Scripts
    >
    > 5. 保存并生效：点击每个窗口的 “确定” 按钮来保存你的修改。重要：请关闭你之前打开的所有命令行窗口 (cmd, PowerShell)。然后重新打开一个新的，再输入 conda --version 进行验证。


    <ins>**建议点#2：**Advanced Installation Options(都勾选上)</ins>

    - Create shortcuts(supported packages only).（← 建议勾选）
    - Add installation to my PATH environment variable（← 建议勾选）
    - Register Miniforge3 as my default Python 3.13（← 建议勾选）
    - Clear the package cache upon completion（← 建议勾选）

    建议都勾选上。

- **卸载**

    如不再使用 miniforge，则可以按如下步骤将 miniforge 从电脑中卸载（删除）。

    - 按 `win` + `i` 键，调出 **设置**
    - 左侧导航栏，点击 **应用**
    - 在右侧“应用”界面，选择 **安装的应用**
    - 在顶部搜索框输入 “forge”
    - 点击在找到的应用“Miniforge3 ...”行末3个点 ...，选择 **卸载**
    - 稍候可完成卸载

[🔝](#top)

--

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
[^4]: [一文解释 conda,pip,anaconda,miniconda,miniforge ↗](https://zhuanlan.zhihu.com/p/518926990)