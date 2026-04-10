---
title: RAG实验-260417(tbc)
layout: default
parent: AI实验课
nav_order: -260417
# nav_exclude: true
---

# RAG实验-260417(tbc)
{: .no_toc }
`更新-260410` \| `发布-260410`

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

本章节用于搭建本次实验的环境，主要完成以下操作：

- 创建用于本次实验的 Python 虚拟环境。在虚拟环境中完成本次实验，不被其他项目的环境所影响，也不影响其他项目的环境。
- 安装本次实验需要的 Python 包。

1. 执行以下命令创建 Python 3.9 虚拟环境：

    ```bash
    conda create -n rag0417 python=3.9
    ```

2. 激活刚创建的虚拟环境：

    ```bash
    conda activate rag0417
    ```

3. 在虚拟环境中安装所需的 Python 包：

    ```bash
    pip3 install faiss-cpu langchain langchain-community langchain-openai pydantic-settings pypdf
    ```

---

## 下载样例代码

```bash
unzip rag_starter.zip 
```

---

## 体验样例代码

1. 构建向量存储。使用提供的知识库文件 kb.txt 构建向量存储：

    ```bash
    cd ~/rag_starter
    python3 main.py --mode build --file kb.txt
    ```

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>