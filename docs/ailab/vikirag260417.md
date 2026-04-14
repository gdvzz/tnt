---
title: RAG实验-260417(tbc)
layout: default
parent: ailab实验课
nav_order: -260417
# nav_exclude: true
---

# RAG实验-260417(tbc)
{: .no_toc }
`更新-260414` \| `发布-260410`

本文档参考 **CG 平台 \| NLP 实验箱 \| 实验5-3：ChatPDF达模型应用开发** 编写而成。

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

## 实验简介

### 实验内容
<br>
本实验将使用 RAG（Retrieval-Augmented Generation，检索增强生成）系统构建一个专门针对 PDF 文档的智能问答系统。与通用 RAG 系统不同，本实验专注于 PDF 文档的处理，并提供了基于 Gradio 的 Web 界面，让用户可以通过友好的图形界面与 PDF 文档进行交互。本实验将学习如何构建一个完整的 PDF 专用 RAG 系统，包括 PDF 文档加载、向量化存储、相似度检索、答案生成以及 Web 界面开发等核心模块。

### 实验要点
<br>
- 了解 RAG 系统的基本原理和工作流程
- 学习 LangChain 框架的使用方法
- 掌握 PDF 文档加载、文本分割、向量化存储等关键技术
- 学会使用 FAISS 进行高效的向量检索
- 理解如何将检索到的上下文信息与大语言模型结合生成答案
- 学习使用 Gradio 构建 Web 界面，提供友好的用户交互体验
- 理解 PDF 专用 RAG 系统与通用 RAG 系统的区别和优势

### 实验环境
<br>
- Python 3
- LangChain 框架
- FAISS 向量数据库
- Qwen 大语言模型（通过 API 端点访问）
- Gradio Web 框架

### RAG介绍
<br>
RAG（Retrieval-Augmented Generation，检索增强生成）系统是一种结合了信息检索和生成式 AI 的先进技术。其核心思想是：当用户提出问题时，系统首先从知识库中检索相关的文档片段，然后将这些上下文信息与大语言模型结合，生成更准确、更有依据的答案。相比直接使用大语言模型，RAG 系统能够：

1. **提供事实依据**：答案基于实际文档内容，而非模型训练数据
2. **减少幻觉**：通过检索到的上下文约束，降低模型编造信息的可能性
3. **支持知识更新**：只需更新知识库，无需重新训练模型
4. **提高准确性**：针对特定领域的知识库能够提供更专业的回答

![image-20251113150634411](https://csonline.jiangnan.edu.cn/cguserImages?_img=aeb5270e4190b97c70399346374b63e1.png)

主要流程：

- 数据入库：读取 PDF 文档并切成小块，并把这些小块经过编码embedding后，存储在一个向量数据库中；
- 相关性检索：用户提出问题，问题经过编码，再在向量数据库中做相似性检索，获取与问题相关的信息块context，并通过重排序算法，输出最相关的N个context；
- 问题输出：相关段落context + 问题组合形成prompt输入大模型中，大模型输出一个答案或采取一个行动

本实验使用的 RAG 系统基于 LangChain 框架构建，采用模块化设计，代码结构清晰，便于理解和扩展。与通用 RAG 系统相比，本系统专门针对 PDF 文档进行了优化，并提供了 Web 界面支持。

### 项目结构介绍
<br>
本项目的代码采用模块化设计，主要包含以下目录和文件：

```
chatpdf/
├── config/              # 配置模块
│   ├── __init__.py
│   └── settings.py     # 配置文件
├── models/              # 模型封装
│   ├── __init__.py
│   ├── llm.py          # LLM 模型封装
│   └── embedding.py    # 嵌入模型封装
├── chains/              # RAG 链
│   ├── __init__.py
│   └── rag_chain.py    # RAG 链实现
├── utils/               # 工具函数
│   ├── __init__.py
│   └── pdf_loader.py   # PDF 文档加载工具（仅支持 PDF）
├── vectorstore/         # 向量存储目录（自动生成）
├── main.py              # 主程序入口（命令行接口）
├── gradio_app.py        # Gradio Web 应用
├── requirements.txt     # 依赖文件
└── handbook.md          # 本实验手册
```

---

## 搭建环境
<br>
本章节用于搭建本次实验的环境，主要完成以下操作：

- 创建用于本次实验的 Python 虚拟环境，在虚拟环境中完成本次实验。不被其他项目影响，也不影响其他项目。
- 安装本次实验需要的 Python 包。

1. 执行以下命令创建 Python 3.10 虚拟环境：

    ```bash
    conda create -n rag0417 python=3.10
    ```

    ✳️ `rag0417` 是虚拟环境的名字，可以是其他取值。本文以 rag0417 为例。

2. 激活刚创建的虚拟环境：

    ```bash
    conda activate rag0417
    ```

    ✳️ 激活虚拟环境后，命令行提示符首部有 `(rag0417)` 字样，比如：`(rag0417) jetson@jetson-Yahboom:~$ `

3. 在虚拟环境中安装所需的 Python 包：

    ```bash
    pip3 install faiss-cpu gradio==5.34.2 langchain langchain-community langchain-openai pydantic-settings pypdf
    ```
    
    ✴️ 一定要把 Python 包安装到虚拟环境中。

---

## 下载解压样例代码
<br>

1. 点击下载：[样例代码链接↗]

2. 移动下载文件到 HOME 目录。在 Jetson 开发板上用浏览器下载时，通常下载文件存放在 ~/Downloads 目录中。执行以下命令移动文件：

    ```bash
    mv ~/Downloads/chatpdf.zip ~/.
    ```

3. 以此执行以下命令，解压缩 zip 文件：

    ```bash
    cd
    unzip chatpdf.zip 
    ```

    解压缩完成后，在 HOME 目录生成 chatpdf 子目录，完整路径是 `/home/jetson/chatpdf`，其中存放样例代码。

---

## 体验样例代码
<br>
1. 构建向量存储。使用提供的知识库文件 `2026年本科直博研究生招生专业目录.pdf` 构建向量存储：

    ```bash
    cd ~/chatpdf
    python3 main.py --mode build --file 2026年本科直博研究生招生专业目录.pdf
    ```

    显示如下提示信息：

    ```bash
    (rag0417) jetson@jetson-Yahboom:~/chatpdf$ python3 main.py --mode build --file 2026年本科直博研究生招生专业目录.pdf
    正在加载 PDF 文档: 2026年本科直博研究生招生专业目录.pdf
    已加载 3 个文档页面
    正在构建向量存储...
    警告: 向量存储已存在，将被覆盖。如需增量添加，请使用 append=True 参数。
    向量存储已构建并保存到: ./vectorstore
    ```

2. 命令行交互式查询

    构建向量存储后，启动交互式查询：

    ```bash
    python3 main.py --mode interactive
    ```

3. 命令行单次查询

    也可以使用单次查询模式：

    ```bash
    python3 main.py --mode query --question "2026江南大学本科直博研究生招生专业目录中，食品学院的招生专业有哪些？"
    ```

    得到如下信息：

    ```bash
    (rag0417) jetson@jetson-Yahboom:~/chatpdf$ python3 main.py --mode query --question "2026江南大学本科直博研究生招生专业目录中，食品学院的招生专业有哪些？"
    正在加载向量存储...
    问题: 2026江南大学本科直博研究生招生专业目录中，食品学院的招生专业有哪些？
    正在生成答案...

    答案:
    根据提供的文档内容，2026年江南大学食品学院的本科直博研究生招生专业包括：

    1. 083200 食品科学与工程
    2. 086003 食品工程（专业学位）
    ```

4. 使用 Gradio Web 界面

    ```bash
    python3 gradio_app.py
    ```
<!--  -->
[样例代码链接↗]: ./vikirag260417.assets/chatpdf.zip
<!--  -->
<span style="font-size:12px; color:#999">THE END</span>