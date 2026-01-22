---
title: 机械臂开发示例-251218
layout: default
parent: AI实验课
nav_order: 22
---

# 机械臂开发示例-251218
{: .no_toc }

[上次实验课](./imrobot251211.md) 通过 Python 程序实现对机械臂的语音控制。本次实验课将实现一个 Web 界面，在 Web 界面上语音控制机械臂。


<details open markdown="block">
  <summary>
    目录
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

<hr>

## 注意事项

- 接电源线时，从六边形桌子的中央六边形孔洞穿线到桌面上。不要从桌子边缘穿线到桌面上。
- 实验结束离开时，关机并拔掉电源。在开发板 `终端(Terminal)` 执行命令 `shutdown -h now` 后，从开发板透明窗口观察并等待散热风扇停止，然后拔掉机械臂电源、开发板电源、显示屏电源。 
- 机械臂电源拔出时，用手扶着机械臂，自然卧倒在开发板上面即可。不要折叠机械臂。
- 断电时，拔掉桌面上相关设备的电源接口即可。不必拔下桌子下面的插头。
- 实验结束离开时，椅子复位，放到桌子下面。
- 天干物燥，要多补充水分。水杯、饮料瓶等拧紧盖子，以免泼洒到教具上。

<hr>

## 相关信息

- elephant-ai 源代码。[点击下载](./imrobot251211.assets/elephant-ai-251211.zip)
- 开发板账号密码（如需要用到）：`jetson` / `yahboom`
- 开发板IP地址。开发板透明窗口顶部的小屏幕显示的 `IPA: 172.18.xxx.xxx`，就是IP地址。或者在 `终端(Terminal)` 执行命令 `ifconfig | grep 172` 也可获得。
- 开发板截图。如需对开发板界面截图，可参考：[开发板截图](../sw/ailabkitsw.md/#开发板screenshot截图)
- 安装 VSCode。如需要在开发板上安装 VSCode，可参考：[安装VSCode](../sw/ailabkitsw.md/#开发板安装vscode)
- 安装中文输入法。如需要在开发板上安装中文输入法，可参考：[安装Google拼音](../sw/ailabkitsw.md/#安装google拼音)

<hr>

## 参考方案

分析过程，和 [上次实验的分析过程](./imrobot251211.md/#参考方案) 类似，此处从略。直接列出参考方案如下：

- （和下面的方法，二选一即可）**[方法1]** 在开发板上启动一个 `终端(Terminal)`，执行 `sudo python3 agent2.py -v`。（命令行参数 `-v`  是告知开发板处理语音文件的意思。）
- （和上面的方法，二选一即可）**[方法2]** 或者，在开发板上启动一个 `终端(Terminal)`，修改 `config.json` 中 `voice` 配置为 `voice: true`，然后执行 `sudo python3 agent.py`。

- 在开发板上，再启动一个 `终端(Terminal)`，运行 `grall.py`（待编写），并在浏览器打开 `localhost:7860`，实现将麦克风说的话，生成 `Recording.flac` 语音文件，供机械臂识别语音并执行相关动作。


<hr>

## 步骤一：新建目录获取elephant-ai代码（建议）

1、用 `jetson` 账号登录开发板后，在 `jetson` 账号的 HOME 目录新建子目录 `ailab`，并切换到子目录 `ailab`。

```bash
cd
pwd # 命令执行结果应显示 /home/jetson
mkdir ailab
cd ailab
pwd # 命令执行结果应显示 /home/jetson/ailab
```

2、下载 elephant-ai 源码：[点击下载](./imrobot251211.assets/elephant-ai-251211.zip)

3、从 HOME 目录下的 `Downloads` 子目录，复制 `elephant-ai-251211.zip` 到当前目录 `ailab` 中，然后执行 `unzip` 解压缩。

```bash
cp ~/Downloads/elephant-ai-251211.zip .
unzip elephant-ai-251211.zip
```

4、验证样例代码是否工作正常。放几个积木到带 + 的方框中（比如绿色、蓝色积木，颜色面朝上），执行 `python3 agent2.py` （或者 `python3 agent.py`）启动样例程序。稍后出现 `<USER>:` 提示符，然后输入比如  `grab green cube and move to 0,200`，查看机械臂动作是否符合预期。

{: .highlight}
确保不是在某个 Python 虚拟环境中运行，即命令行提示符前没有 `(gdpy310)` 或 `(base)` 等字样。否则会报某些库找不到。如果已在某个 Python 虚拟环境中，用 `conda deactivate` 退出。

{: .highlight-title}
> 关于 `sudo python3 agent.py` 还是 `python3 agent.py`
> 
> 1、sudo 是 Linux 系统中的一个重要命令，它的全称是 "superuser do"。这个命令允许经过验证的用户以其他用户的身份来运行命令，通常是以超级用户（root）的身份运行命令。确实需要加 `sudo` 时再加。<br>
> 2、由于开发板环境安装差异（今后将统一），部分开发板仍需要加 `sudo` 才能执行，即使 [新复制代码](#步骤一新建目录获取elephant-ai代码建议) 以后。否则报 `openAI` 相关错误。<br>


```bash
jetson@jetson-Yahboom:~/ailab/elephant-ai-251211$ python3 agent2.py
WARNING: Carrier board is not from a Jetson Developer Kit.
WARNNIG: Jetson.GPIO library has not been verified with this carrier board,
WARNING: and in fact is unlikely to work correctly.
进入交互模式...
<USER>:grab green cube and move to 0,200
<LLM>:✿FUNCTION✿: grab_object
✿ARGS✿: {"object_name": "绿色方块"}
✿FUNCTION✿: move_to
✿ARGS✿: {"target_coord": [0, 200], "target_height": 110}
functions_and_args: [('grab_object', {'object_name': '绿色方块'}), ('move_to', {'target_coord': [0, 200], 'target_height': 110})]
#################### <函数执行> ####################
Image saved as captured_image.jpg
[{'x1': 408, 'x2': 589, 'y1': 745, 'y2': 980}]
像素坐标 (319.04, 414.0) 对应的机械臂坐标为: [144.7   2.1]
#################### <函数执行> #################### 

#################### <函数执行> ####################
*************
[0, 200]
Objects arranged successfully
#################### <函数执行> #################### 

<USER>:
```

{: .important}
如果抓取不大精确，可参考：[抓不准该如何调整](./ailabkit.md/#抓不准该如何调整) 做调整。

<hr>

## 步骤二：环境准备

Gradio 是一个开源 Python 包，允许你快速为你的机器学习模型、API 或任何任意 Python 函数构建一个演示或 Web 应用程序。然后，你可以使用 Gradio 内置的共享功能，在几秒钟内分享你的演示或 Web 应用程序的链接。无需 JavaScript、CSS 或 Web 托管经验！（来源：[Gradio 快速入门](https://gradio.org.cn/guides/quickstart)）

NLP实验箱也采用 Gradio 构建 Web 界面。因此本实验采用 Gradio 来构建语音相关的 Web 界面。

Gradio 需要 Python 3.10 的环境。如果开发板上不是 3.10 （通常是 3.8），则可以通过安装 `conda` 来创建一个 Python 3.10 的虚拟环境。不直接升级 Python 3.8 到 Python 3.10，以免导致其他应用无法运行。

```bash
python3 --version # 比如输出显示 Python 3.8.10
```

安装和启动 `conda` 虚拟环境步骤如下：

**1、执行 `conda`，确认 `conda` 是否已安装。如已安装，可跳过第2步。**

**2、如果尚未安装 `conda`，则依次执行以下命令安装并激活：（如已安装请跳过此步）**

```bash
cd # 切换到 jetson 用户的 HOME 目录
mkdir tmp2512 # 新建临时目录用于下载安装包
cd tmp2512
pwd # 执行结果应显示 /home/jetson/tmp2512

# 从科大镜像下载安装包
wget https://mirrors.ustc.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-aarch64.sh

# 安装过程中，请仔细阅读提示。并在询问“是否初始化Miniforge3”时输入 yes。
bash Miniforge3-Linux-aarch64.sh

# 安装完成后，关闭并重新打开终端，或者执行以下命令使配置生效：
source ~/.bashrc

# 之后，你的命令行前会出现 (base) 字样，表示基础环境已激活。
```

**3、创建Python 3.10虚拟环境**

执行以下命令创建 Python 3.10 的虚拟环境：

```bash
conda create -n gdpy310 python=3.10
```
- `-n gdpy310` 指定了环境名称，你可以自定义（如 `zspy310`、`lspy310`、`wwpy310`，等）。
- `python=3.10` 指定了要安装的Python版本。

**4、激活虚拟环境**

环境创建完成后，使用以下命令激活它：（以虚拟环境名字是 `gdpy310` 为例）

```bash
conda activate gdpy310
```

**激活/去激活相应 Python 虚拟环境：`conda activate 虚拟环境名` 和 `conda deactivate 虚拟环境名`**

```bash
jetson@jetson-Yahboom:~$ python3 --version
Python 3.8.10
jetson@jetson-Yahboom:~$ conda activate base
(base) jetson@jetson-Yahboom:~$ python3 --version
Python 3.12.12
(base) jetson@jetson-Yahboom:~$ conda activate gdpy310
(gdpy310) jetson@jetson-Yahboom:~$ python3 --version
Python 3.10.19
(gdpy310) jetson@jetson-Yahboom:~$ conda deactivate
(base) jetson@jetson-Yahboom:~$ conda deactivate
jetson@jetson-Yahboom:~$ 
```

{: .important}
激活某个 Python 虚拟环境后，命令行提示符前有 `(base)` 等字样，以便确定当前在哪个 Python 虚拟环境中。

{: .note}
conda 安装后 `(base)` 虚拟环境中，已是 Python 3.12，可以尝试就在 `(base)` 中进行实验，而不一定新建额外的虚拟环境。

<hr>

## 步骤三：尝试Web界面录制WAV文件

和大模型交互后得到如下样例代码:

```python
# grwav.py

import gradio as gr
import numpy as np
import soundfile as sf # 导入soundfile库
from datetime import datetime

def save_audio(audio):
    """
    处理录制的音频并保存为WAV文件。
    audio参数是一个元组: (采样率, 音频数据numpy数组)
    """
    if audio is None:
        return "未检测到音频输入。"

    sample_rate, audio_data = audio

    # 1. 生成带时间戳的唯一文件名，避免覆盖
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recording_{timestamp}.wav"

    # 2. 保存为WAV文件
    sf.write(filename, audio_data, sample_rate)

    # 3. 计算音频时长
    duration = len(audio_data) / sample_rate

    return f"✅ 音频已保存为：{filename}\n采样率：{sample_rate}Hz，时长：{duration:.2f}秒"

# 创建界面
demo = gr.Interface(
    fn=save_audio,
    inputs=gr.Audio(sources="microphone", type="numpy", label="点击开始录音", format="wav"),
    outputs="text",
    title="Jetson麦克风录音器",
    description="录音将自动保存为带时间戳的WAV文件。"
)

# 启动应用（允许局域网访问）
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

- 在实验目录（比如 `/home/jetson/elephant-ai-251211`）中新建文件 `grwav.py`, 复制上述代码到文件中。

- 执行命令激活 Python 虚拟环境（以 `gdpy310`）

```bash
jetson@jetson-Yahboom:~$ conda activate gdpy310
(gdpy310) jetson@jetson-Yahboom:~$ 
```

- 执行以下命令启动后端程序

```bash
python3 grwav.py
```

- 打开 FireFox 浏览器，输入网址：`localhost:7860`

- 测试是否可以录音。


{: .important}
如果缺少什么库，可以在当前虚拟环境（比如 `gdpy310`）中用 `pip3 install 库名` 安装。一定要在所需虚拟环境中安装。

{: .important-title}
> 关于浏览器输入网址
>
> 1、开发板浏览器输入网址是 `localhost:7860`（或 `127.0.0.1:7860`），而不是 `0.0.0.0:7860`。<br>
> 2、在局域网的其他电脑，还可以通过 `开发板IP地址:7860` 访问。<br>
> 3、`0.0.0.0` 并不是浏览器可访问的IP地址。<br>
> 4、`demo.launch(server_name="0.0.0.0", server_port=7860)` 中的 `0.0.0.0`，表示既可以在开发板上通过本机地址访问（即 `localhost:7860` 或 `127.0.0.1:7860`），还可以被局域网的其他电脑访问（即 `开发板IP地址:7860` ）。

{: .highlight-title}
> 假定没有录音不成功，可以检查 `Settings | sound` 相关设置是否恰当。
> 
> - System Volume 是否足够大<br>
> - Volume Levels 是否足够大<br>
> - Output 是否选择合适的设备，并点击 `Test` 做测试，听听是否有声音播放。<br>
> - Output 的 Balance 是否在中间。<br>
> - Input 是否选择合适的设备，并对着麦克风说话，查看下方红色虚线是否足够长。期望红色虚线较长。<br>
> 
> ![settings-sound](./imrobot251211.assets/sounds.png)

<hr>

## 步骤四：尝试Web界面录制FLAC文件

继续和大模型交互，获得如何录制 FLAC 文件的样例代码，如下。在实验目录中新建 `grflac.py`，启动并在 Web 界面测试。

```python
# grflac.py

import gradio as gr
import numpy as np
import soundfile as sf  # 关键库
from datetime import datetime
import os

def save_audio_as_flac(audio):
    """
    处理录制的音频并保存为FLAC文件。
    audio参数: (采样率, 音频数据numpy数组)
    """
    if audio is None:
        return "未检测到音频输入。"

    sample_rate, audio_data = audio

    # 1. 创建保存目录（可选）
    save_dir = "flac_recordings"
    os.makedirs(save_dir, exist_ok=True)

    # 2. 生成带时间戳的唯一FLAC文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"recording_{timestamp}.flac")  # 扩展名为.flac

    # 3. 保存为FLAC文件
    #    关键：指定格式为'FLAC'，并可选择压缩级别（0-8，默认5）
    sf.write(file=filename,
             data=audio_data,
             samplerate=sample_rate,
             format='FLAC',
             subtype='PCM_16')  # 也可用 'PCM_24' 如果音频数据是24位的

    # 4. 计算音频时长
    duration = len(audio_data) / sample_rate

    return f"✅ FLAC文件已保存至：{filename}\n采样率：{sample_rate}Hz，时长：{duration:.2f}秒"

# 创建界面
demo = gr.Interface(
    fn=save_audio_as_flac,
    inputs=gr.Audio(sources="microphone",
                    type="numpy",
                    label="点击开始录音",
                    format="wav"),  # Gradio内部仍以wav格式录制
    outputs="text",
    title="Jetson麦克风录音器 (FLAC格式)",
    description="录音将自动保存为无损压缩的FLAC格式文件。"
)

# 启动应用
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

如何启动后端程序、浏览器测试，和 [尝试web界面录制wav文件](#步骤三尝试web界面录制wav文件) 类似，此处从略。

<hr>

## 步骤五：完整可用样例

### 录制程序
<br>

继续和大模型交互，获得完整可用样例如下。在实验目录中新建 `grall.py`，然后启动并在 Web 界面测试。

```python
# grall.py

import gradio as gr
import numpy as np
import soundfile as sf
import shutil
import os

# 固定的文件名
FIXED_FLAC_FILE = "current_recording.flac"
TARGET_FLAC_FILE = "Recording.flac"

def save_and_process_audio(audio):
    """录音完成后自动保存为FLAC文件"""
    if audio is None:
        return "❌ 未检测到音频输入", None
    
    sample_rate, audio_data = audio
    
    try:
        # 保存为固定FLAC文件（覆盖模式）
        sf.write(file=FIXED_FLAC_FILE,
                 data=audio_data,
                 samplerate=sample_rate,
                 format='FLAC',
                 subtype='PCM_16')
        
        duration = len(audio_data) / sample_rate
        message = f"✅ 录音已保存: {FIXED_FLAC_FILE}\n时长: {duration:.1f}秒, 采样率: {sample_rate}Hz"
        
        return message, FIXED_FLAC_FILE
    except Exception as e:
        return f"❌ 保存失败: {str(e)}", None

def copy_to_recording():
    """复制文件到当前目录的Recording.flac"""
    if not os.path.exists(FIXED_FLAC_FILE):
        return f"❌ 找不到 {FIXED_FLAC_FILE}，请先录制音频"
    
    try:
        # 复制文件
        shutil.copy2(FIXED_FLAC_FILE, TARGET_FLAC_FILE)
        
        # 验证复制结果
        if os.path.exists(TARGET_FLAC_FILE):
            file_size = os.path.getsize(TARGET_FLAC_FILE) / 1024
            return f"✅ 复制成功: {TARGET_FLAC_FILE} ({file_size:.1f}KB)"
        else:
            return "❌ 复制失败：目标文件未创建"
    except Exception as e:
        return f"❌ 复制失败: {str(e)}"

# 创建精简界面
with gr.Blocks(title="Jetson FLAC录音器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🎤 Jetson FLAC录音器")
    gr.Markdown("点击下方录音按钮开始/停止录音，录音将自动保存")
    
    # 录音组件
    audio_input = gr.Audio(
        sources="microphone",
        type="numpy",
        label="录音控制",
        format="wav",
        interactive=True
    )
    
    # 状态显示
    status_display = gr.Textbox(label="状态", value="等待录音...", lines=2)
    
    # 播放界面（录音完成后自动显示）
    gr.Markdown("### 录音播放")
    audio_output = gr.Audio(label="最新录音", type="filepath", interactive=False)
    
    # 操作按钮
    gr.Markdown("### 文件操作")
    copy_button = gr.Button("📁 执行指令：复制到Recording.flac", variant="primary", size="lg")
    
    # 设置事件处理
    # 录音完成后自动保存并更新状态
    audio_input.change(
        fn=save_and_process_audio,
        inputs=[audio_input],
        outputs=[status_display, audio_output]
    )
    
    # 复制按钮
    copy_button.click(
        fn=copy_to_recording,
        inputs=None,
        outputs=[status_display]
    )

# 启动应用
if __name__ == "__main__":
    print("启动Jetson FLAC录音器...")
    print(f"录音文件: {FIXED_FLAC_FILE}")
    print(f"目标文件: {TARGET_FLAC_FILE}")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
```

Web 参考界面如下：
![参考web界面](./imrobot251218.assets/grweb.png)

简要说明如下：
- 上部“录音控制”。用于麦克风录制声音。
- 中间“状态”。显示相关信息。
- 下部“录音播放”。用于播放录制好的 flac 文件，确保内容是正确的。
- 底部“执行指令”按钮。将录制好的 flac 文件，复制到当前目录的 `Recording.flac`，供机械臂做后续处理。

{: .note}
移动到某个坐标，建议说：移动到 x 等于 0，y 等于 200。这样能够被识别得更准确。

### 启动机械臂程序
<br>

新建 `终端(Terminal)` 运行 `python3 agent2.py -v` （或者 修改 `config.json` 中 `voice:true` 后，运行 `python3 agent.py`）

{: .highlight}
确保不是在某个 Python 虚拟环境中运行，即命令行提示符前没有 `(gdpy310)` 或 `(base)` 等字样。否则会报某些库找不到。如果已在某个 Python 虚拟环境中，用 `conda deactivate` 退出。

{: .highlight-title}
> 关于 `sudo python3 agent.py` 还是 `python3 agent.py`
> 
> 1、sudo 是 Linux 系统中的一个重要命令，它的全称是 "superuser do"。这个命令允许经过验证的用户以其他用户的身份来运行命令，通常是以超级用户（root）的身份运行命令。确实需要加 `sudo` 时再加。<br>
> 2、由于开发板环境安装差异（今后将统一），部分开发板仍需要加 `sudo` 才能执行，即使 [新复制代码](#步骤一新建目录获取elephant-ai代码建议) 以后，否则报 `openAI` 相关错误。<br>


<hr>

## 建议

只是执行上述样例代码，意义不大。手册只是提供了一些思路供参考。
- 同学们可以做出不同的代码和界面，实现实验的目的。
- 至少理解样例代码的含义。

<hr>

## 拓展任务（可选）

1. 学习 Gradio 基本用法，然后优化录制 Web 界面。比如：
  - 调整界面元素布局。
  - 调整界面配色。
  - 学习如何分享界面：`你可以使用 Gradio 内置的共享功能，在几秒钟内分享你的演示或 Web 应用程序的链接。无需 JavaScript、CSS 或 Web 托管经验！`

2. 优化机械臂代码 `agent2.py` （或 `agent.py`），比如：
  - 提示正在等待 `Recording.flac`。当前界面提示不友好。
