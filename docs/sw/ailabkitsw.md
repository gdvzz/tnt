---
title: 教具相关软件安装使用
layout: default
parent: 软件使用
nav_order: 10
---

# 教具相关软件安装使用
{: .no_toc }

相关实验箱、开发板的相关软件安装和使用说明。

<details open markdown="block">
  <summary>
    目录
  </summary>
  {: .text-delta }
1. TOC
{:toc}

<hr>

## 开发板安装VSCode

点击界面左下角的 `九宫格(Show Applications)`，然后搜索 `VSCode`。如能找到则打开直接使用。如没有找到，参考如下步骤安装 VSCode 到开发板。

- 打开开发板上的浏览器，访问 VSCode 官网 Download 页面：[https://code.visualstudio.com/Download](https://code.visualstudio.com/Download)
- 选择下载 `.deb` `Arm64`。通常下载到用户的 HOME 目录的 `Downloads` 子目录中，比如 `/home/jetson/Downloads`。
- 依次执行以下命令，安装 VSCode：

```bash
cd /home/jetson/Downloads # 假定 .deb 安装包下载到 /home/jetson/Downloads 目录中
sudo dpkg -i 下载的.deb安装包文件
```

- 点击界面左下角的 `九宫格(Show Applications)`，然后搜索 `VSCode`，就可以找到该应用。打开应用后，在界面左侧导航栏中找到该应用，鼠标右键选 `Add to Favorites`，以方便下次使用。

<hr>

## 安装Google拼音

在开发板上启一个 `终端(Terminal)`，然后按 `Ctrl` + `空格` 键，看看是否已安装中文输入法。如已有，则可使用。如没有，请参考如下步骤安装。

- 依次执行以下命令，安装中文输入法：

```bash
sudo apt update
sudo apt install fcitx fcitx-tools fcitx-config* fcitx-frontend* fcitx-module* fcitx-ui-* presage
sudo apt install fcitx-googlepinyin
```

{: .note}
第2个命令只执行 `sudo apt install fcitx`，也能安装成功中文输入法，但中文输入时候选词框很小。按上述第2个命令安装后，中文输入时候选词框能看清楚。

- 按以下步骤修改配置：
  1. 点击 `Settings`，点击 `Region & Language`
  2. 点击 Region & Language 界面的底部的 `Manage Installed Languages`
  3. Language Support 界面有 2 个页签，选择 `Language` 页签（默认选中的）
  4. 更改 Language 页签的底部的 `Keyboard input method system:` 为 `fcitx`
  5. 再点击 Language 页签的中部的 `Appy System-Wide` 按钮，然后点击右下角 `Close` 关闭窗口

{: .note}
如果想把界面改成中文显示，可将 Language 页签的顶部的 `Language for menus and windows:` 中的 `Chinese(China)`，用鼠标点住后拖动到最上面，然后也是要点击中部的 `Appy System-Wide` 按钮，然后点击右下角 `Close` 关闭窗口。

-  在 `终端(Terminal)` 输入 `reboot` （或者 `sudo reboot`）后按回车，重启系统。

- 配置并启用输入法
  - 重启后，桌面右上角任务栏会出现一个键盘或企鹅图标，点击它。
  - 选择 “配置” (Configure) 或 “配置当前输入法” (Configure Current Input Method)。
  - 在弹出的配置窗口中，点击左下角的 “+” 号添加输入法。
  - 取消勾选“只显示当前语言”，在列表中找到并选择 “Google Pinyin”，点击“OK”添加。
  - 完成后，你就可以使用 Ctrl + 空格 或 Shift 键切换中英文输入了。

<hr>

## 开发板Screenshot截图

在英伟达开发板上，如需要截图，除了手机拍照，还可使用内置应用 `Screenshot`。点击界面左下角的 `九宫格(Show Applications)`，然后搜索 `Screenshot`，就可以找到该应用。

截图可以通过 `微信文件传输网页版`，或 `scp` 命令等，传到微信或电脑中。此处从略。

在界面左侧导航栏中找到该应用，鼠标右键选 `Add to Favorites`，以方便下次使用。