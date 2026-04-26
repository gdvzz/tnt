---
title: AI教具使用简要说明
layout: default
parent: AI Lab
nav_order: 2
---

# AI教具使用简要说明
{: .no_toc }



<details open markdown="block">
  <summary>
    目录
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## 视觉实验箱

登录后，执行 `cd /elephant-ai` 切换到目录 `/elephant-ai`：
```bash
# cd 
jetson@jetson-Yahboom:~$ cd /elephant-ai

# pwd 确认是在 /elephant-ai 目录
jetson@jetson-Yahboom:/elephant-ai$ pwd
/elephant-ai
```

<br>

执行 `sudo python3 agent.py`，启动视觉实验箱样例程序： 
```bash
jetson@jetson-Yahboom:/elephant-ai$ sudo python3 agent.py
WARNING: Carrier board is not from a Jetson Developer Kit.
WARNNIG: Jetson.GPIO library has not been verified with this carrier board,
WARNING: and in fact is unlikely to work correctly.
<USER>:
```

<br>

放置一些积木，在桌上图纸的带 + 号的方框内。积木上的蓝色、红色、绿色等朝上。

在 `<USER>:` 提示符后面，输入 `grab green cube and move -80,200`

```bash
<USER>:grab green cube and move -80,200
<LLM>:我需要先抓取绿色方块，然后将其移动到指定位置。根据指令，我需要先使用grab_object，然后使用move_to。

✿FUNCTION✿: grab_object
✿ARGS✿: {"object_name": "green cube"}

✿FUNCTION✿: move_to
✿ARGS✿: {"target_coord": [-80,200], "target_height": 110}
functions_and_args: [('grab_object', {'object_name': 'green cube'}), ('move_to', {'target_coord': [-80, 200], 'target_height': 110})]
#################### <函数执行> ####################
Image saved as captured_image.jpg
[{'x1': 0, 'x2': 179, 'y1': 332, 'y2': 584}]
像素坐标 (57.28, 219.84) 对应的机械臂坐标为: [212.8  68.1]
#################### <函数执行> #################### 

#################### <函数执行> ####################
*************
[-80, 200]
Objects arranged successfully
#################### <函数执行> #################### 

<USER>:
```

{: .note}
move -80,200。分别是 x、y、z坐标。z可以省略，默认是110。x和y是什么方向，可参考图纸上的标识。z的正方向是桌面向上。

同时按下 `ctrl`和`c`，可退出。
```bash
<USER>:^CTraceback (most recent call last):
  File "agent.py", line 50, in <module>
    user_input = input("<USER>:")
KeyboardInterrupt

jetson@jetson-Yahboom:/elephant-ai$ 
```

### 抓不准该如何调整

- 机械臂上的摄像头，是否可以拍摄到图像。运行开发板上的应用 `文件(files)`，找到机械臂所在目录中的文件 `captured_image.jpg`，看看是否有图像。期望是有图像的。

- 其次，看看机械臂底座，是否在图纸的矩形中。

- 如果还抓不准，可以调整 `/elephant-ai/config.json` 中的 x、y、z 的偏移量。
```json
{
    "points_pixel": [
        [320,220],
        [590,430],
        [72,31],
        [590,26]
    ],
    "points_arm": [
        [210,-30],
        [140, -110],
        [280,70],
        [280,-110]
    ],
    "x": 10,
    "y": -7,
    "z": -5,
    "voice":false,
    "threshold": 110
}
```

如何修改 `config.json`：
- 执行 `sudo vim config.json` 打开文件
- 删除。光标移动到要删除字符的位置，按 `Esc` 键，然后再按 `x`，可删除字符。
- 插入。光标移动到要插入字符的位置，按 `Esc` 键，然后再按 `i`，然后输入新的字符。
- 保存退出。按 `Esc` 键，然后输入 `:wq`，再按`回车`键。

执行 `cat config.json`，确认确实修改了。
```bash
jetson@jetson-Yahboom:/elephant-ai$ cat config.json
```

<hr>

## 华为昇腾开发板

**0、账号密码**
- 账号：`HwHiAiUser` / 密码：`Mind@123`
- 账号：`root` / 密码：`Mind@123`

**1、登录后，执行 `su - root` 切换到 `root` 用户**

```bash
(base) HwHiAiUser@davinci-mini:~$ su - root
Password: 
(base) root@davinci-mini:~# 
```
{: .note}
输密码时，屏幕不会显示。输完密码后按回车即可。

{: .note}
切换到 root 用户，是为了体验摄像头识别物体。

**2、执行 `cd` 切换到相关目录中**

```bash
(base) root@davinci-mini:~# cd /home/HwHiAiUser/samples/notebooks
(base) root@davinci-mini:/home/HwHiAiUser/samples/notebooks# 
```

**3、执行 `jupyter lab --allow-root` 启动后台**

```bash
(base) root@davinci-mini:/home/HwHiAiUser/samples/notebooks# jupyter lab --allow-root
[I 2025-12-08 13:55:37.302 ServerApp] Package jupyterlab took 0.0001s to import
[I 2025-12-08 13:55:37.418 ServerApp] Package jupyter_lsp took 0.1141s to import
[W 2025-12-08 13:55:37.418 ServerApp] A `_jupyter_server_extension_points` function was not found in jupyter_lsp. Instead, a `_jupyter_server_extension_paths` function was found and will be used for now. This function name will be deprecated in future releases of Jupyter Server.
[I 2025-12-08 13:55:37.470 ServerApp] Package jupyter_server_terminals took 0.0502s to import
[I 2025-12-08 13:55:37.471 ServerApp] Package notebook_shim took 0.0001s to import
[W 2025-12-08 13:55:37.472 ServerApp] A `_jupyter_server_extension_points` function was not found in notebook_shim. Instead, a `_jupyter_server_extension_paths` function was found and will be used for now. This function name will be deprecated in future releases of Jupyter Server.
[I 2025-12-08 13:55:37.477 ServerApp] jupyter_lsp | extension was successfully linked.
[I 2025-12-08 13:55:37.494 ServerApp] jupyter_server_terminals | extension was successfully linked.
[I 2025-12-08 13:55:37.514 ServerApp] jupyterlab | extension was successfully linked.
[I 2025-12-08 13:55:39.552 ServerApp] notebook_shim | extension was successfully linked.
[I 2025-12-08 13:55:39.683 ServerApp] notebook_shim | extension was successfully loaded.
[I 2025-12-08 13:55:39.693 ServerApp] jupyter_lsp | extension was successfully loaded.
[I 2025-12-08 13:55:39.697 ServerApp] jupyter_server_terminals | extension was successfully loaded.
[I 2025-12-08 13:55:39.699 LabApp] JupyterLab extension loaded from /usr/local/miniconda3/lib/python3.9/site-packages/jupyterlab
[I 2025-12-08 13:55:39.699 LabApp] JupyterLab application directory is /usr/local/miniconda3/share/jupyter/lab
[I 2025-12-08 13:55:39.707 LabApp] Extension Manager is 'pypi'.
[I 2025-12-08 13:55:39.719 ServerApp] jupyterlab | extension was successfully loaded.
[I 2025-12-08 13:55:39.720 ServerApp] Serving notebooks from local directory: /home/HwHiAiUser/samples/notebooks
[I 2025-12-08 13:55:39.721 ServerApp] Jupyter Server 2.5.0 is running at:
[I 2025-12-08 13:55:39.721 ServerApp] http://localhost:8888/lab?token=f20c1335ecc7d52f63a372cbed8a12fccbd336bf590e1a96
[I 2025-12-08 13:55:39.721 ServerApp]     http://127.0.0.1:8888/lab?token=f20c1335ecc7d52f63a372cbed8a12fccbd336bf590e1a96
[I 2025-12-08 13:55:39.721 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[W 2025-12-08 13:55:39.750 ServerApp] No web browser found: Error('could not locate runnable browser').
[C 2025-12-08 13:55:39.750 ServerApp] 
    
    To access the server, open this file in a browser:
        file:///root/.local/share/jupyter/runtime/jpserver-9111-open.html
    Or copy and paste one of these URLs:
        http://localhost:8888/lab?token=f20c1335ecc7d52f63a372cbed8a12fccbd336bf590e1a96
        http://127.0.0.1:8888/lab?token=f20c1335ecc7d52f63a372cbed8a12fccbd336bf590e1a96
```

**后续步骤，请参考如下链接**
- [登录 jupyter lab](https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/23.0.RC2/Getting%20Started%20with%20Application%20Development/paqe/paqe_0002.html)
- [目标检测样例](https://www.hiascend.com/document/detail/zh/Atlas200IDKA2DeveloperKit/23.0.RC2/Getting%20Started%20with%20Application%20Development/paqe/paqe_0003.html)

<hr>

## 语音实验箱

访问：[https://172.18.144.18/plugin/frontend/#/appview/AJ62kgyj?i=1](https://172.18.144.18/plugin/frontend/#/appview/AJ62kgyj?i=1)

也可在 Pad 上部署一系列软件后，在 Pad 启动语音服务。

在 Pad 部署，可参考手册：[语音对话实验指导手册](./ailabkit.assets/语音对话实验指导手册.pdf)


## 自然语言实验箱

相关手册：[自然语言处理实验箱V1](./ailabkit.assets/自然语言处理实验箱V1.pdf)

---

## NLP自然语言实验箱

### 环境搭建

在视觉实验箱上搭建。

- 创建 python 虚拟环境

```bash
conda create -n nlpdemo python=3.8.10
```

- 安装 python 包

在 NLP 实验箱执行 `pip3 list --format=freeze > requirements.txt` 得到 requirements.txt，该文件内容如下：

执行 `pip3 install -r requirement.txt`

`pip3 install --no-cache-dir -v -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`



```markdown
accelerate==1.0.1
aiofiles==23.2.1
aiohappyeyeballs==2.4.4
aiohttp==3.10.11
aiosignal==1.3.1
altair==5.4.1
annotated-types==0.7.0
anyio==4.5.2
apt-clone==0.2.1
apturl==0.5.2
async-timeout==4.0.3
attrs==25.1.0
bcrypt==3.1.7
beautifulsoup4==4.14.3
black==24.8.0
blinker==1.4
Brlapi==0.7.0
cachetools==5.5.2
certifi==2025.11.12
cfgv==3.4.0
chardet==3.0.4
charset-normalizer==3.4.4
click==8.1.8
clip==1.0
colorama==0.4.3
cryptography==2.8
cupshelpers==1.0
cycler==0.10.0
dataclasses-json==0.6.7
dbus-python==1.2.16
decorator==4.4.2
defer==1.0.6
Deprecated==1.3.1
deprecation==2.1.0
dirtyjson==1.0.8
distlib==0.4.0
distro==1.9.0
distro-info==0.23+ubuntu1.1
DockerHub-API==0.5
duplicity==0.8.12.0
entrypoints==0.3
exceptiongroup==1.2.2
faiss-cpu==1.8.0.post1
fastapi==0.115.9
fasteners==0.14.1
ffmpy==0.5.0
filelock==3.16.1
filetype==1.2.0
flake8==7.1.2
frozenlist==1.5.0
fsspec==2025.2.0
ftfy==6.2.3
furl==2.1.4
future==0.18.2
gradio==3.50.2
gradio_client==0.6.1
greenlet==3.1.1
h11==0.14.0
httpcore==1.0.7
httplib2==0.14.0
httpx==0.28.1
huggingface-hub==0.23.5
identify==2.6.1
idna==2.8
imageio==2.35.1
imageio-ffmpeg==0.5.1
importlib_metadata==8.5.0
importlib_resources==6.4.5
Jetson.GPIO==2.1.6
jetson-stats==4.3.2
Jinja2==3.1.5
jiter==0.8.2
joblib==1.4.2
jsonpatch==1.33
jsonpointer==3.0.0
jsonschema==4.23.0
jsonschema-specifications==2023.12.1
keyring==18.0.1
kiwisolver==1.0.1
lancedb==0.5.7
langchain==0.2.17
langchain-community==0.2.19
langchain-core==0.2.43
langchain-openai==0.1.25
langchain-text-splitters==0.2.4
langsmith==0.1.147
language-selector==0.1
launchpadlib==1.10.13
lazr.restfulclient==0.14.2
lazr.uri==1.0.3
llama-cloud==0.1.45
llama-index==0.11.23
llama-index-agent-openai==0.3.4
llama-index-cli==0.3.1
llama-index-core==0.11.23
llama-index-embeddings-clip==0.2.0
llama-index-embeddings-huggingface==0.3.1
llama-index-embeddings-openai==0.2.5
llama-index-indices-managed-llama-cloud==0.5.0
llama-index-legacy==0.9.48.post4
llama-index-llms-huggingface==0.3.5
llama-index-llms-ollama==0.3.6
llama-index-llms-openai==0.2.16
llama-index-multi-modal-llms-ollama==0.3.3
llama-index-multi-modal-llms-openai==0.2.3
llama-index-program-openai==0.2.0
llama-index-question-gen-openai==0.2.0
llama-index-readers-file==0.3.0
llama-index-readers-llama-parse==0.3.0
llama-index-vector-stores-lancedb==0.1.5
llama-parse==0.5.15
llvmlite==0.41.1
lockfile==0.12.2
louis==3.12.0
macaroonbakery==1.3.1
Mako==1.1.0
MarkupSafe==2.1.5
marshmallow==3.22.0
matplotlib==3.1.2
mccabe==0.7.0
minijinja==2.13.0
monotonic==1.5
more-itertools==10.5.0
moviepy==1.0.3
mpmath==1.3.0
multidict==6.1.0
mypy_extensions==1.1.0
narwhals==1.28.0
nest-asyncio==1.6.0
networkx==3.1
nltk==3.9.1
nodeenv==1.9.1
numba==0.58.1
numpy==1.24.4
oauthlib==3.1.0
olefile==0.46
ollama==0.6.1
onboard==1.4.1
openai==1.65.1
openai-whisper==20250625
orderedmultidict==1.0.2
orjson==3.10.15
overrides==7.7.0
packaging==24.2
PAM==0.4.2
pandas==2.0.3
paramiko==2.6.0
pathspec==0.12.1
pexpect==4.6.0
pillow==10.4.0
pip==25.0.1
pkgutil_resolve_name==1.3.10
platformdirs==4.3.6
pre-commit==3.5.0
proglog==0.1.12
propcache==0.2.0
protobuf==3.6.1
psutil==7.1.3
py==1.11.0
pyarrow==17.0.0
pycairo==1.16.2
pycodestyle==2.12.1
pycrypto==2.6.1
pycups==1.9.73
pydantic==2.10.6
pydantic_core==2.27.2
pydantic-settings==2.8.1
pydub==0.25.1
pyflakes==3.2.0
pygame==2.6.1
PyGObject==3.36.0
PyICU==2.4.2
PyJWT==1.7.1
pylance==0.9.18
pymacaroons==0.13.0
PyNaCl==1.3.0
pyparsing==2.4.6
pypdf==5.9.0
pyRFC3339==1.1
python-apt==2.0.1+ubuntu0.20.4.1
python-dateutil==2.9.0.post0
python-dbusmock==0.19
python-debian==0.1.36+ubuntu1.1
python-dotenv==1.0.1
python-multipart==0.0.20
pytz==2025.1
pyxdg==0.26
PyYAML==6.0.3
ratelimiter==1.2.0.post0
referencing==0.35.1
regex==2024.11.6
requests==2.32.4
requests-toolbelt==1.0.0
requests-unixsocket==0.2.0
retry==0.9.2
rpds-py==0.20.1
safetensors==0.5.3
scikit-learn==1.3.2
scipy==1.10.1
SecretStorage==2.3.1
semantic-version==2.10.0
semver==3.0.4
sentence-transformers==3.2.1
setuptools==45.2.0
simplejson==3.16.0
six==1.14.0
smbus2==0.5.0
sniffio==1.3.1
soupsieve==2.7
SQLAlchemy==2.0.44
starlette==0.44.0
striprtf==0.0.26
sympy==1.13.3
systemd-python==234
tabulate==0.9.0
tantivy==0.22.0
tenacity==8.5.0
termcolor==2.4.0
text-generation==0.7.0
threadpoolctl==3.5.0
tiktoken==0.7.0
tokenizers==0.20.3
tomli==2.3.0
torch==2.2.2
torchvision==0.17.2
tqdm==4.67.1
transformers==4.46.3
typing_extensions==4.13.2
typing-inspect==0.9.0
tzdata==2025.1
ubuntu-advantage-tools==8001
ubuntu-drivers-common==0.0.0
urllib3==1.25.8
urwid==2.0.1
uvicorn==0.33.0
virtualenv==20.35.4
wadllib==1.3.3
wcwidth==0.2.14
websockets==11.0.3
wget==3.2
wheel==0.34.2
wrapt==2.0.1
xkit==0.0.0
yarl==1.15.2
zipp==3.20.2
```

---

以下找不到对应版本

```markdown
apt-clone==0.2.1
apturl==0.5.2
Brlapi==0.7.0
clip==1.0
cupshelpers==1.0
defer==1.0.6
distro-info==0.23+ubuntu1.1
DockerHub-API==0.5
```

```markdown
accelerate==1.0.1
aiofiles==23.2.1
aiohappyeyeballs==2.4.4
aiohttp==3.10.11
aiosignal==1.3.1
altair==5.4.1
annotated-types==0.7.0
anyio==4.5.2
async-timeout==4.0.3
attrs==25.1.0
bcrypt==3.1.7
beautifulsoup4==4.14.3
black==24.8.0
blinker==1.4
cachetools==5.5.2
certifi==2025.11.12
cfgv==3.4.0
chardet==3.0.4
charset-normalizer==3.4.4
click==8.1.8
colorama==0.4.3
cryptography==2.8
cycler==0.10.0
dataclasses-json==0.6.7
dbus-python==1.2.16
decorator==4.4.2
Deprecated==1.3.1
deprecation==2.1.0
dirtyjson==1.0.8
distlib==0.4.0
distro==1.9.0
distro-info==0.23+ubuntu1.1
DockerHub-API==0.5
duplicity==0.8.12.0
entrypoints==0.3
exceptiongroup==1.2.2
faiss-cpu==1.8.0.post1
fastapi==0.115.9
fasteners==0.14.1
ffmpy==0.5.0
filelock==3.16.1
filetype==1.2.0
flake8==7.1.2
frozenlist==1.5.0
fsspec==2025.2.0
ftfy==6.2.3
furl==2.1.4
future==0.18.2
gradio==3.50.2
gradio_client==0.6.1
greenlet==3.1.1
h11==0.14.0
httpcore==1.0.7
httplib2==0.14.0
httpx==0.28.1
huggingface-hub==0.23.5
identify==2.6.1
idna==2.8
imageio==2.35.1
imageio-ffmpeg==0.5.1
importlib_metadata==8.5.0
importlib_resources==6.4.5
Jetson.GPIO==2.1.6
jetson-stats==4.3.2
Jinja2==3.1.5
jiter==0.8.2
joblib==1.4.2
jsonpatch==1.33
jsonpointer==3.0.0
jsonschema==4.23.0
jsonschema-specifications==2023.12.1
keyring==18.0.1
kiwisolver==1.0.1
lancedb==0.5.7
langchain==0.2.17
langchain-community==0.2.19
langchain-core==0.2.43
langchain-openai==0.1.25
langchain-text-splitters==0.2.4
langsmith==0.1.147
language-selector==0.1
launchpadlib==1.10.13
lazr.restfulclient==0.14.2
lazr.uri==1.0.3
llama-cloud==0.1.45
llama-index==0.11.23
llama-index-agent-openai==0.3.4
llama-index-cli==0.3.1
llama-index-core==0.11.23
llama-index-embeddings-clip==0.2.0
llama-index-embeddings-huggingface==0.3.1
llama-index-embeddings-openai==0.2.5
llama-index-indices-managed-llama-cloud==0.5.0
llama-index-legacy==0.9.48.post4
llama-index-llms-huggingface==0.3.5
llama-index-llms-ollama==0.3.6
llama-index-llms-openai==0.2.16
llama-index-multi-modal-llms-ollama==0.3.3
llama-index-multi-modal-llms-openai==0.2.3
llama-index-program-openai==0.2.0
llama-index-question-gen-openai==0.2.0
llama-index-readers-file==0.3.0
llama-index-readers-llama-parse==0.3.0
llama-index-vector-stores-lancedb==0.1.5
llama-parse==0.5.15
llvmlite==0.41.1
lockfile==0.12.2
louis==3.12.0
macaroonbakery==1.3.1
Mako==1.1.0
MarkupSafe==2.1.5
marshmallow==3.22.0
matplotlib==3.1.2
mccabe==0.7.0
minijinja==2.13.0
monotonic==1.5
more-itertools==10.5.0
moviepy==1.0.3
mpmath==1.3.0
multidict==6.1.0
mypy_extensions==1.1.0
narwhals==1.28.0
nest-asyncio==1.6.0
networkx==3.1
nltk==3.9.1
nodeenv==1.9.1
numba==0.58.1
numpy==1.24.4
oauthlib==3.1.0
olefile==0.46
ollama==0.6.1
onboard==1.4.1
openai==1.65.1
openai-whisper==20250625
orderedmultidict==1.0.2
orjson==3.10.15
overrides==7.7.0
packaging==24.2
PAM==0.4.2
pandas==2.0.3
paramiko==2.6.0
pathspec==0.12.1
pexpect==4.6.0
pillow==10.4.0
pip==25.0.1
pkgutil_resolve_name==1.3.10
platformdirs==4.3.6
pre-commit==3.5.0
proglog==0.1.12
propcache==0.2.0
protobuf==3.6.1
psutil==7.1.3
py==1.11.0
pyarrow==17.0.0
pycairo==1.16.2
pycodestyle==2.12.1
pycrypto==2.6.1
pycups==1.9.73
pydantic==2.10.6
pydantic_core==2.27.2
pydantic-settings==2.8.1
pydub==0.25.1
pyflakes==3.2.0
pygame==2.6.1
PyGObject==3.36.0
PyICU==2.4.2
PyJWT==1.7.1
pylance==0.9.18
pymacaroons==0.13.0
PyNaCl==1.3.0
pyparsing==2.4.6
pypdf==5.9.0
pyRFC3339==1.1
python-apt==2.0.1+ubuntu0.20.4.1
python-dateutil==2.9.0.post0
python-dbusmock==0.19
python-debian==0.1.36+ubuntu1.1
python-dotenv==1.0.1
python-multipart==0.0.20
pytz==2025.1
pyxdg==0.26
PyYAML==6.0.3
ratelimiter==1.2.0.post0
referencing==0.35.1
regex==2024.11.6
requests==2.32.4
requests-toolbelt==1.0.0
requests-unixsocket==0.2.0
retry==0.9.2
rpds-py==0.20.1
safetensors==0.5.3
scikit-learn==1.3.2
scipy==1.10.1
SecretStorage==2.3.1
semantic-version==2.10.0
semver==3.0.4
sentence-transformers==3.2.1
setuptools==45.2.0
simplejson==3.16.0
six==1.14.0
smbus2==0.5.0
sniffio==1.3.1
soupsieve==2.7
SQLAlchemy==2.0.44
starlette==0.44.0
striprtf==0.0.26
sympy==1.13.3
systemd-python==234
tabulate==0.9.0
tantivy==0.22.0
tenacity==8.5.0
termcolor==2.4.0
text-generation==0.7.0
threadpoolctl==3.5.0
tiktoken==0.7.0
tokenizers==0.20.3
tomli==2.3.0
torch==2.2.2
torchvision==0.17.2
tqdm==4.67.1
transformers==4.46.3
typing_extensions==4.13.2
typing-inspect==0.9.0
tzdata==2025.1
ubuntu-advantage-tools==8001
ubuntu-drivers-common==0.0.0
urllib3==1.25.8
urwid==2.0.1
uvicorn==0.33.0
virtualenv==20.35.4
wadllib==1.3.3
wcwidth==0.2.14
websockets==11.0.3
wget==3.2
wheel==0.34.2
wrapt==2.0.1
xkit==0.0.0
yarl==1.15.2
zipp==3.20.2
```

260305：需要得到进一步指导。先暂停。

---

## NLP实验箱demo

- 源码地址：https://gitlab.educg.net/cg_zmy/Jetson_ai.git

### 环境搭建

先用 conda 建个 python=3.9 的环境

```bash
conda create -n nlpx39 python=3.9
```

从 git 上下载源码，然后复制到 ~/nlpx/jetson_ai

```bash
(nlpx39) jetson@jetson-Yahboom:~/nlpx/jetson_ai$ python3 main.py
```

缺什么 python 包，就装什么包


```bash
pip3 install gradio
```

```markdown
ModuleNotFoundError: No module named 'gradio' # 大模型说要 Python 3.10以上，貌似 3.9 也能装
```

```
ImportError: cannot import name 'HfFolder' from 'huggingface_hub' (/home/jetson/miniforge3/envs/nlpx39/lib/python3.9/site-packages/huggingface_hub/__init__.py)

(nlpx39) jetson@jetson-Yahboom:~$ pip3 list | grep hugg
huggingface_hub               1.5.0



```

**以下是 python=3.10**

- ModuleNotFoundError: No module named 'gradio' 
    - pip3 install gradio

- ModuleNotFoundError: No module named 'openai'
    - pip3 install openai

-     import Jetson.GPIO as GPIO
ModuleNotFoundError: No module named 'Jetson'

    - pip3 install Jetson.GPIO

-     from smbus2 import SMBus, i2c_msg
ModuleNotFoundError: No module named 'smbus2'

    - pip3 install smbus2

- ModuleNotFoundError: No module named 'pygame'
    - pip3 install pygame    

ModuleNotFoundError: No module named 'requests'
    - pip3 install requests

-     import soundfile as sf
ModuleNotFoundError: No module named 'soundfile'
    - pip3 install soundfile

-   File "/home/jetson/nlpx/jetson_ai/main.py", line 52, in <module>
    user_audio = gr.Audio(source="microphone", type="filepath", label="输入语音", optional=True)
  File "/home/jetson/miniforge3/envs/nlpx310/lib/python3.10/site-packages/gradio/component_meta.py", line 194, in wrapper
    return fn(self, **kwargs)
TypeError: Audio.__init__() got an unexpected keyword argument 'source'

    - # user_audio = gr.Audio(source="microphone", type="filepath", label="输入语音", optional=True)
            user_audio = gr.Audio(sources=["microphone"], type="filepath", label="输入语音", optional=True)
---

老师好！

汇报下进展，关于 NLP样例程序，在机械臂上的安装情况。

===
1. 源码地址：https://gitlab.educg.net/cg_zmy/Jetson_ai.git，git clone 到开发板上。然后复制到 ~/nlpx/jetson_ai 中

===
2. 创建了python=3.10 虚拟环境：conda create -n nlpx310 python=3.10

===
3. 在虚拟环境中安装了相关的包：pip3 install gradio openai Jetson.GPIO smbus2 pygame requests soundfile

===
4. 可能是包的版本，对 main.py 做了很小的改动。大约在 50 行左右的地方

    with gr.Row():
        with gr.Column():
            # user_audio = gr.Audio(source="microphone", type="filepath", label="输入语音", optional=True)
            user_audio = gr.Audio(sources=["microphone"], type="filepath", label="输入语音")
        with gr.Column():
            # output_audio = gr.Audio(show_download_button=False, label="输出语音", autoplay=True)
            output_audio = gr.Audio(label="输出语音", autoplay=True)

===
5. 后台执行了，有 function <lambda> 什么 warning，暂时没有管

(nlpx310) jetson@jetson-Yahboom:~/nlpx/jetson_ai$ python3 main.py
WARNING: Carrier board is not from a Jetson Developer Kit.
WARNNIG: Jetson.GPIO library has not been verified with this carrier board,
WARNING: and in fact is unlikely to work correctly.
pygame 2.6.1 (SDL 2.28.4, Python 3.10.19)
Hello from the pygame community. https://www.pygame.org/contribute.html
/home/jetson/miniforge3/envs/nlpx310/lib/python3.10/site-packages/gradio/utils.py:1179: UserWarning: Expected 1 arguments for function <function <lambda> at 0xffff33fc0b80>, received 0.
  warnings.warn(
/home/jetson/miniforge3/envs/nlpx310/lib/python3.10/site-packages/gradio/utils.py:1183: UserWarning: Expected at least 1 arguments for function <function <lambda> at 0xffff33fc0b80>, received 0.
  warnings.warn(
* Running on local URL:  http://0.0.0.0:7860
* To create a public link, set `share=True` in `launch()`.


===

6. 在开发板上装了 chrome：pip3 install chromium-browser

===

7. chrome 访问 127.0.0.1:7860。麦克风说话 或者 打字，都报同样的错。


有空的时候，帮忙指导指导。

感谢！


---

pip3 install gradio==5.44.1 openai Jetson.GPIO smbus2 pygame requests soundfile

---
## 视觉实验箱

### 环境搭建

这里的环境，主要是用于视觉实验箱之机械臂演示程序。视觉实验箱可以做另外很多实验，其环境和此环境无关。

- 样例代码

这个是机械臂的样例代码地址。https://pan.educg.net/s/QlQ0UX