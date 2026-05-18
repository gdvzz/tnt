---
title: Docker指南
layout: default
parent: aikit教具
nav_order: 90
# nav_exclude: true
---

# Docker指南
{: .no_toc }
`更新-260517` \| `发布-260517`

本文档描述 **Docker** 的相关信息，用于快速熟悉和入门Docker。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!-- <details markdown="block">
  <summary>ℹ️ 更新历史</summary>

**260509**
- 新增：[连WiFi](#连wifi)
- 新增：[更改默认静态IP](#更改默认静态ip)
- 新增：[普通用户访问摄像头](#普通用户访问摄像头)
- 默认IP地址改为 192.168.137.100

**260506**
- 新增：[连接外网](#连接外网)

</details> -->

---

<span id="save-load-image"></span>

## 导出和恢复镜像
<br>
下载镜像后要归档，或者要把镜像传到其他计算机上，可使用镜像的导出（保存）和恢复（加载）功能。操作步骤如下：

- **先查看镜像：**

    ```bash
docker image list
    ```

    屏幕显示信息如下：（样例）

    ```bash
REPOSITORY                             TAG            IMAGE ID       CREATED        SIZE
firecrawl-nuq-postgres                 latest         c12d105651ab   2 months ago   456MB
ghcr.io/firecrawl/firecrawl            latest         cbaaefb64a6a   2 months ago   854MB
redis                                  alpine         47ee395bd02d   2 months ago   97.2MB
ghcr.io/firecrawl/playwright-service   latest         665e3f996ed1   3 months ago   1.33GB
rabbitmq                               3-management   de912cbbf07f   5 months ago   252MB
    ```

- **导出镜像 rabbitmq:3-management：**
    
    导出镜像，并加上管道直接压缩：

    ```bash
docker save rabbitmq:3-management | gzip > rabbitmq_3-management.tar.gz
    ```

    导出镜像 rabbitmq:3-management（先导出再压缩）

    ```bash
docker save -o rabbitmq_3-management.tar rabbitmq:3-management
    ```

    可以用 gzip 压缩（会生成 rabbitmq_3-management.tar.gz，并删除原 rabbitmq_3-management.tar）

    ```bash
gzip rabbitmq_3-management.tar
    ```
    
- **导出其他镜像**

    导出镜像 firecrawl-nuq-postgres:latest

    ```bash
docker save firecrawl-nuq-postgres:latest | gzip > firecrawl-nuq-postgres_latest.tar.gz
    ```

    导出镜像 ghcr.io/firecrawl/firecrawl:latest

    ```bash
docker save ghcr.io/firecrawl/firecrawl:latest | gzip > ghcr.io_firecrawl_firecrawl_latest.tar.gz
    ```

    导出镜像 redis:alpine

    ```bash
docker save redis:alpine | gzip >redis_alpine.tar.gz
    ```

    导出镜像 ghcr.io/firecrawl/playwright-service:latest

    ```bash
docker save ghcr.io/firecrawl/playwright-service | gzip >ghcr.io_firecrawl_playwright-service.tar.gz
    ```

- **删除镜像**

    删除镜像 rabbitmq:3-management

    ```bash
docker image rm rabbitmq:3-management
    ```

    删除镜像 firecrawl-nuq-postgres:latest

    ```bash
docker image rm firecrawl-nuq-postgres
    ```

    删除镜像 ghcr.io/firecrawl/firecrawl:latest

    ```bash
docker image rm ghcr.io/firecrawl/firecrawl
    ```

    删除镜像 redis:alpine

    ```bash
docker image rm redis:alpine
    ```

- **恢复镜像：**

    恢复 rabbitmq 镜像：

    ```bash
docker load -i rabbitmq_3-management.tar 
    ```

    恢复 firecrawl-nuq-postgres 镜像：

    ```bash
docker image load -i firecrawl-nuq-postgres_latest.tar.gz 
    ```

    > （1）docker image load 可直接处理 gz 压缩文件。<br>
    > （2）用 zip 压缩的文件，需要先解压。

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>