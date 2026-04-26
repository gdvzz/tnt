---
title: 昇腾开发板_pyACL(tbc)
layout: default
parent: aikit教具
# nav_order: 30
# nav_exclude: true
---

# 昇腾开发板 pyACL 快速入门(tbc)
{: .no_toc }
`更新-260422` \| `发布-260422`

本文档描述 **昇腾开发板** AscendCL 应用开发指南（Python）快速入门。

pyACL（Python Ascend Computing Language）是一套在AscendCL的基础上使用CPython封装得到的Python API库，使用户可以通过Python进行昇腾AI处理器的运行管理、资源管理等，实现在昇腾CANN平台上进行深度学习推理计算、图形图像预处理、单算子加速计算等能力。

参考资料：[昇腾pyACL↗]

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

## 搭建环境

### 新建用户

用 root 用户创建新用户 gdv2：

```bash
adduser --home /home/gdv2 --shell /bin/bash gdv2
```

并把 gdv2 加入 HwHiAiUser 组：

```bash
adduser gdv2 HwHiAiUser
```

> 1. 问题的根源在于对硬件设备文件的访问权限不足。将用户加入HwHiAiUser组，这是最安全、规范的永久性解决方案。HwHiAiUser 是昇腾CANN平台安装时创建的专用用户组，拥有访问 /dev/davinci_manager 等硬件设备文件的权限。

> 2. sudo 方式不一定能把环境变量带入。虽然有权限访问硬件设备文件，但还是报错说找不到 acl。

并把 gdv2 加入 sudo 组：（可选，主要是方便执行 apt 等）

```bash
adduser gdv2 sudo
```

### 设置环境变量

在安装完CANN软件包之后，请务必自行配置以下环境变量，否则，将无法正常使用“import acl”。设置完环境变量后，在Python脚本中加入“import acl”，就可以使用pyACL中的函数了。

在创建的 gdv2 用户的 .bashrc 文件最后，增加一行：

```shell
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

增加完成后，执行 `source .bashrc`

### 测试 acl

用 gdv2 用户执行：

```python
import acl
print("hello world!")
```

### 创建 Python 虚拟环境

在创建的 gdv2 用户的 .bashrc 文件最后，增加一行：

```shell
export PATH="/usr/local/miniconda3/bin:$PATH"
```

gdv2@davinci-mini:~$ conda activate pyacl
                                                                                                   提示信息如下：
                                                                                                   ```bash   
CommandNotFoundError: Your shell has not been properly configured to use 'conda activate'.            
To initialize your shell, run

    $ conda init <SHELL_NAME>

Currently supported shells are:
  - bash
  - fish
  - tcsh
  - xonsh
  - zsh
  - powershell

See 'conda init --help' for more information and options.

IMPORTANT: You may need to close and restart your shell after running 'conda init'.

```

按提示执行

```bash
gdv2@davinci-mini:~$ conda init bash
no change     /usr/local/miniconda3/condabin/conda
no change     /usr/local/miniconda3/bin/conda
no change     /usr/local/miniconda3/bin/conda-env
no change     /usr/local/miniconda3/bin/activate
no change     /usr/local/miniconda3/bin/deactivate
no change     /usr/local/miniconda3/etc/profile.d/conda.sh
no change     /usr/local/miniconda3/etc/fish/conf.d/conda.fish
no change     /usr/local/miniconda3/shell/condabin/Conda.psm1
no change     /usr/local/miniconda3/shell/condabin/conda-hook.ps1
no change     /usr/local/miniconda3/lib/python3.9/site-packages/xontrib/conda.xsh
no change     /usr/local/miniconda3/etc/profile.d/conda.csh
modified      /home/gdv2/.bashrc

==> For changes to take effect, close and re-open your current shell. <==
```

执行完成后，conda 在 .bashrc 中增加了

```shell
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/usr/local/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/usr/local/miniconda3/etc/profile.d/conda.sh" ]; then
        . "/usr/local/miniconda3/etc/profile.d/conda.sh"
    else
        export PATH="/usr/local/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```

重新登录 gdv2，再执行如下命令激活新创建的 pyacl 虚拟环境：

```bash
conda activate pyacl
```

按文档要求，在虚拟环境 pyacl 中安装 Python 包：

```bash
pip3 install pillow numpy
```

有一些警告，但不影响使用 pillow 和 numpy。可执行以下命令检查是否干净：

```bash
(pyacl) gdv2@davinci-mini:~$ pip3 check
op-compile-tool 0.1.0 requires getopt, which is not installed.
op-compile-tool 0.1.0 requires inspect, which is not installed.
op-compile-tool 0.1.0 requires multiprocessing, which is not installed.
op-test-frame 0.1 is not supported on this platform
te 0.4.0 is not supported on this platform
```

---

## 创建代码目录

依次执行以下命令，创建目录，并下载图片和模型：

```bash
# 创建目录
mkdir -p $HOME/first_app/data
mkdir -p $HOME/first_app/model

# 下载图片和模型
cd $HOME/first_app/data
wget https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/models/aclsample/dog1_1024_683.jpg
cd $HOME/first_app/data
wget https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/models/aclsample/dog2_1024_683.jpg
cd $HOME/first_app/model  
wget https://obs-9be7.obs.cn-east-2.myhuaweicloud.com/003_Atc_Models/resnet50/resnet50.onnx
```

模型转换，对于开源框架的模型，不能直接在昇腾AI处理器上进行推理，需要使用ATC（Ascend Tensor Compiler）工具将开源框架的网络模型转换为适配昇腾AI处理器的离线模型（*.om文件）。
执行以下命令，将原始模型转换为昇腾AI处理器能识别的*.om模型文件。请注意，执行命令的用户需具有命令中相关路径的可读、可写权限。

```bash
atc --model=resnet50.onnx --framework=5 --output=resnet50 --input_shape="actual_input_1:1,3,224,224"  --soc_version=Ascend310B4
```

```bash
(pyacl) gdv2@davinci-mini:~$ sudo npu-smi info
[sudo] password for gdv2: 
+--------------------------------------------------------------------------------------------------------+
| npu-smi 23.0.rc3                                 Version: 23.0.rc3                                     |
+-------------------------------+-----------------+------------------------------------------------------+
| NPU     Name                  | Health          | Power(W)     Temp(C)           Hugepages-Usage(page) |
| Chip    Device                | Bus-Id          | AICore(%)    Memory-Usage(MB)                        |
+===============================+=================+======================================================+
| 0       310B4                 | OK              | 7.2          37                15    / 15            |
| 0       0                     | NA              | 0            1797 / 3513                             |
+===============================+=================+======================================================+
```

> 如果无法确定当前设备的soc_version，则在安装NPU驱动包的服务器执行npu-smi info命令进行查询，在查询到的“Name”前增加Ascend信息，例如“Name”对应取值为xxxyy，实际配置的soc_version值为Ascendxxxyy。

atc 报错 numpy Failed to import Python module [AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead..].

```bash
pip3 install "numpy<2.0"
```

Failed to import Python module [ModuleNotFoundError: No module named 'sympy'.].


```bash
pip3 install sympy
```

```bash
atc --model=resnet50.onnx --framework=5 --output=resnet50 --input_shape="actual_input_1:1,3,224,224"  --soc_version=Ascend310B4
```

```bash
ATC start working now, please wait for a moment.
<frozen importlib._bootstrap>:914: ImportWarning: TEMetaPathFinder.find_spec() not found; falling back to find_module()
<frozen importlib._bootstrap>:914: ImportWarning: TEMetaPathFinder.find_spec() not found; falling back to find_module()
<frozen importlib._bootstrap>:671: ImportWarning: TBEMetaPathLoader.exec_module() not found; falling back to load_module()
...
...
ATC run success, welcome to the next use.
```

---

## 准备环境

```bash
conda create -n pyacl39 python=3.9.1
pip3 install numpy==1.24.0 pillow
```
numpy==1.24.0

---

## 开发应用

---

## 运行应用

```bash
python3 first_app.py 
Traceback (most recent call last):
  File "/home/gdv2/first_app/first_app.py", line 164, in <module>
    result = resnet50.forward([image])
  File "/home/gdv2/first_app/first_app.py", line 79, in forward
    self.input_data[i]["buffer"],  # 目标地址 device
IndexError: list index out of range
```
<!--  -->
[昇腾pyACL↗]: https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/23.0.RC2/Application%20Development%20Guide/aadgp/aclpythondevg_0000.html