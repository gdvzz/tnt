---
title: 工作日志
layout: default
# parent: AI Lab
# nav_order: 9001
nav_exclude: true
---

# 工作日志
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

## vkai-搭建虚拟环境

1. 创建并激活虚拟环境

    ```bash
conda create -n vkai python=3.9
conda activate vkai
    ```

2. 获取源代码 + 解压缩（略）

3. 运行样例demo程序，缺什么 Python 包就装什么包

    ```bash
cd ~/vkai # 假设样例程序在 jetson 用户的 HOME 目录下的 vkai 目录
(vkai) jetson@jetson-Yahboom:~/vkai$ python3 agent.py
    ```

    虚拟环境缺什么包就装什么包。经过反复运行 + 反复安装，得到需要安装如下 Python 包：

    ```bash
pip3 install openai pyaudio numpy soundfile requests Pillow pymycobot==3.4.9 opencv-python Jetson.GPIO scipy
    ```

Successfully installed packaging-26.0 pymycobot-3.4.9 pyserial-3.5 python-can-4.6.1 wrapt-1.17.3

<!-- Successfully installed pymycobot-4.0.4 pyserial-3.5
jetson@jetson-Yahboom:~$ pip3 list | grep pymy
pymycobot                            3.4.9   -->

Successfully installed Jetson.GPIO-2.1.12
jetson@jetson-Yahboom:~$ pip3 list | grep GPIO
Adafruit-GPIO                        1.0.3               
Jetson.GPIO                          2.1.6     