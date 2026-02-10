---
title: 关于本站
layout: default
nav_order: 9.90
# nav_exclude: true
# parent: <父页面的title>
last_modified_date: 2026-01-22 20:09:00
---

# 关于本站
{: .no_toc}

本文记录了相关测试和建站过程，供后续类似网站的建设供参考。本站使用 [Just the Docs](https://github.com/just-the-docs/just-the-docs) 主题，在此鸣谢作者！

如需要技术支持或其他交流，请 [邮件联系我](mailto:georgedonnev2@outlook.com)。

参考 [配置configuration], 复制了相关代码在此，供预览深色模式。尚不会设置深色模式，后续持续探索。<br>

<button class="btn js-toggle-dark-mode">Preview dark color scheme</button>

<script>
const toggleDarkMode = document.querySelector('.js-toggle-dark-mode');

jtd.addEvent(toggleDarkMode, 'click', function(){
  if (jtd.getTheme() === 'dark') {
    jtd.setTheme('light');
    toggleDarkMode.textContent = 'Preview dark color scheme';
  } else {
    jtd.setTheme('dark');
    toggleDarkMode.textContent = 'Return to the light side';
  }
});
</script>

<details open markdown="block">
  <summary>
    目录
  </summary>
  <!-- {: .text-delta } -->
- TOC
{:toc}
</details>

## 整体说明

以下操作都是在 MacOS 上进行的，Windows 操作可能有细微差别。

- `~/gdv5` 是指当前 Mac 用户的根目录下的 gdv5 目录。以本机为例，绝对路径是 `/Users/george1442/gdv5`。

## 新建仓库 tnt

先新建仓库用于存放网站内容。在 github 账号 gdv5 下，新建仓库 tnt，过程从略。

## 关联远程仓库

1. 在本地电脑已有目录 `~/gdv5` 下，新建子目录 `tnt`，用于本地存放网站内容。

2. 新建文档 `~/gdv5/tnt/docs/index.md`，作为网站的首页。

    - 可以先随便写一些内容，以跑通全流程。内容可后续持续更新。
    - index.md 放在 ~/gdv5/tnt/docs/ 下，是后续网站内容都存放在 docs 目录下。存放在  ~/gdv5/tnt 也是同样可行的，对应配置做微调即可。建议网站内容放在 docs 目录下，同级可建目录 codes 存放代码之类的。
    - 建议编写 `readme.md` 用于 github 展示。

3. 添加ssh密钥到 github，如尚未。操作步骤请参考：[用 Github + Markdown 创建个人网站]。

4. 在 `~/gdv5/tnt` 依次执行以下命令，将本地仓库关联到远程仓库，并完成首次提交。如下：

    ```bash
    ~/gdv5/tnt % git status
    ~/gdv5/tnt % git add .
    ~/gdv5/tnt % git commit -m "1st commit"
    ~/gdv5/tnt % git branch -M master
    ~/gdv5/tnt % git remote add tnt git@gitubv5.com:gdv5/tnt.git
    ~/gdv5/tnt % git push -u tnt master
    ```

    上述命令参考了 github 新建仓库后（尚未有代码时）的如下提示信息：
    
    ```bash
    …or create a new repository on the command line
    
    echo "# tnt" >> README.md
    git init
    git add README.md
    git commit -m "first commit"
    git branch -M main
    git remote add origin git@github.com:gdv5/tnt.git
    git push -u origin main
    
    …or push an existing repository from the command line
    
    git remote add origin git@github.com:gdv5/tnt.git
    git branch -M main
    git push -u origin main
    ```

## 基础配置

参考 [主题模板说明]，做相关基础配置。

1. 复制 pages.yml
    
    在网站的根目录下，新建子目录 `.github/workfolws`, 然后复制 `pages.yml` 到该子目录。该文件就是 GitHuab Actions 需要的工作流文件。

    经测试，应该放在 `~/gdv5/tnt` 目录下。因为 `pages.yml` 中指定了网站内容放在 `~/gdv5/tnt/docs` 中。

2. 复制 .gitignore 到 ~/gdv5/tnt 目录中。

3. 复制 Gemfile 到 ~/gdv5/tnt/docs 目录中。

    ```yml
    source 'https://rubygems.org'

    gem "jekyll", "~> 4.4.1" # installed by `gem jekyll`
    # gem "webrick"        # required when using Ruby >= 3 and Jekyll <= 4.2.2

    gem "just-the-docs", "0.11.1" # pinned to the current release
    # gem "just-the-docs"        # always download the latest release
    ```

4. 复制了 Gemfile.lock 到 ~/gdvzz/tnt/docs 目录中。

5. 复制了 _config.yml 到 ~/gdvzz/tnt/docs 目录中。

    ```yml
    title: Just the Docs Template
    description: A starter template for a Jeykll site using the Just the Docs theme!
    theme: just-the-docs
    
    url: https://just-the-docs.github.io
    
    aux_links:
    Template Repository: https://github.com/just-the-docs/just-the-docs-template
    ```

## 修改配置文件

上述配置文件复制到相关目录后，要对内容做相应修改。具体如下：

1. 修改后的 `pages.yml` 内容如下：

    ```yml
    # This workflow uses actions that are not certified by GitHub.
    # They are provided by a third-party and are governed by
    # separate terms of service, privacy policy, and support
    # documentation.
    
    # Sample workflow for building and deploying a Jekyll site to GitHub Pages
    name: Deploy Jekyll site tnt to Pages
    
    on: # 只有 master 分支的 docs 下的文件变化，才会重新编译和部署网站
      push:
        branches: 
          - "master"
        paths:
          - "docs/**"
    
      # Allows you to run this workflow manually from the Actions tab
      workflow_dispatch:
    
    # Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub     Pages
    permissions:
      contents: read
      pages: write
      id-token: write
    
    # Allow one concurrent deployment
    concurrency:
      group: "pages"
      cancel-in-progress: true
    
    jobs:
      # Build job
      build:
        runs-on: ubuntu-latest
        
        defaults: # 设置工作目录为 /docs
          run:
            working-directory: docs
        
        steps:
          - name: Checkout
            uses: actions/checkout@v6
          - name: Setup Ruby
            uses: ruby/setup-ruby@v1
            with:
              ruby-version: '3.3' # Not needed with a .ruby-version file
              bundler-cache: true # runs 'bundle install' and caches     installed gems automatically
              cache-version: 0 # Increment this number if you need to     re-download cached gems
              working-directory: '${{ github.workspace }}/docs' # 增加工    作目录参数
          - name: Setup Pages
            id: pages
            uses: actions/configure-pages@v5
          - name: Build with Jekyll
            # Outputs to the './_site' directory by default
            run: bundle exec jekyll build --baseurl "${{ steps.pages.    outputs.base_path }}"
            env:
              JEKYLL_ENV: production
          - name: Upload artifact
            # Automatically uploads an artifact from the './_site'     directory by default
            uses: actions/upload-pages-artifact@v4 # readme是 V3？
            with: # 增加 path
              path: docs/_site/
    
      # Deployment job
      deploy:
        environment:
          name: github-pages
          url: ${{ steps.deployment.outputs.page_url }}
        runs-on: ubuntu-latest
        needs: build
        steps:
          - name: Deploy to GitHub Pages
            id: deployment
            uses: actions/deploy-pages@v4
    ```

2. `.gitignore` 的内容没有修改。此处从略。

3. 修改后的 `Gemfile` 如下：
    ```yml
    source 'https://rubygems.org'

    gem "jekyll"
    # gem "jekyll", "~> 4.4.1" # installed by `gem jekyll`
    # gem "webrick"        # required when using Ruby >= 3 and Jekyll <= 4.2.2

    gem "just-the-docs", "0.11.1" # pinned to the current release
    # gem "just-the-docs"        # always download the latest release

    # 增加试试
    gem "github-pages", group: :jekyll_plugins
    ```

4. `Gemfile.lock` 的内容没有修改。此处从略。

5. 修改后的 `_config.yml` 如下：

    ```yml
    # title: Just the Docs Template
    # description: A starter template for a Jeykll site using the Just the Docs theme!
    title: "Try and Test"
    description: "学习笔记，使用指导文档，等"
    theme: just-the-docs
        
    # url: https://just-the-docs.github.io
    url: https://gdv5.github.io
        
    # aux_links:
    # Template Repository: https://github.com/just-the-docs/just-the-docs-template
    ```

## 发布网站

上述初步调整后，依次执行如下命令推送到 github：

```bash
~/gdv5/tnt % git status
~/gdv5/tnt % git add .
~/gdv5/tnt % git commit -m "update config"
~/gdv5/tnt % git push tnt
```

参考 [主题模板说明]，到对应仓库下，然后进入 Settings > Pages > Build and deployment > Source, 选择 `GitHub Actions` 即可。

- 选择 GitHub Actions 后，可不必理会屏幕提示 “Use a suggested workflow, browse all workflows, or create your own. ”，因为 `pages.yml` 都已经写好了。
- 查看仓库的 Action。如果运行不成功，手工点击运行一次即可。
- 不要选择 `Deploy from a branch`。应该也是可以的，但相关配置文件要做对应调整，才可以部署成功。

至此，网站发布成功！


## 定制配置网站

为了让网站样式能被接受，已经让网站更美观，对网站进行如下定制和配置。

### 修改css样式

主题文字存在如下个人觉得可以改善的点：

- 部分文字大小不合理。比如 h3 有点偏小。
- 小屏幕浏览时，文字还会缩小，比如 20px缩小为16px。其实不必缩小，因为缩小后更不易看清。
- 代码块文字行间距过大。可以紧凑些。

参考该主题的 [定制customization]，css 样式定制可以写在 `_sass/custom/custom.scss` 中。经测试验证，定制了如下样式：

```scss
// 对相关 css 设置做定制
// 以下设置将覆盖 just-the-docs theme 原有对应数值

body {
    font-size: 16px !important;
    line-height: 1.5 !important;
    // color: #24292e !important; // 涉及深色浅色模式，不改了。
}

// 使用 !important，用于阻止 jtd 主题在小屏幕下缩小h1-h6的字号
h1 {
    font-size: 2em !important; // 32px
}

h2 {
    font-size: 1.5em !important; // 24px
}

h3 {
    font-size: 1.25em !important; // 20px
}

h4 {
    font-size: 1em !important; // 16px
}

h5 {
    font-size: 0.875em !important; // 14px
}

h6 {
    font-size: 0.85em !important;
    color: #6a737d;
}

.main-content {
    line-height: 1.5;
    // line-height: 1;
}

// 让代码块行距紧凑些
pre {
    // line-height: 1.5;
    line-height: 1;
}

.main-content ol {
    list-style-type: decimal;
}

.main-content ul {
    list-style-type: disc;
}

.main-content ol>li::before {
    display: none;
    content: none;
    visibility: hidden;
}

.main-content ul>li::before {
    display: none;
    content: none;
    visibility: hidden;
}
```

后续如有其他样式改动，也可写在这个文件中。先用浏览器的 Inspect 功能确定期望改动的样式是什么标签（或 class），然后再在该文件中写上对应的样式，才能覆盖成功。

### 主题配置

参考该主题的 [配置configuration] 文档，从上到下逐个尝试和配置。

设置了以下配置：

- site logo
- mermaid diagrams
- aux links
- navigation sidebar
- heading anchor links
- external navigation links
- footer content
- color scheme

尚未设置（或不计划设置）以下配置：

- site favicon


遗留问题：

- 要支持搜索中文。当前无法搜索中文。

## 配置后的测试

### 测试 callouts

{: .highlight}
**注意：** 这是 highlight 文本

{: .important}
这是 important 文本

{: .new}
这是 new 文本

{: .note}
这是 note 文本

{: .warning}
这是 warning 文本

遗留：思考什么样的颜色配置，更符合大众习惯。比如红色表示xx，黄色表示xx，蓝色表示xx，灰色表示xx。

### 测试颜色

{: .text-blue-100}
这是 bule-100 文字 
你好你好！

绿色绿色
{: .text-green-100}

这是 green-100 文字
{: .text-green-100} 

{: .text-red-200}
这是 red-200 文字 

### 测试 h1-h6 的大小

测试标题开始 

| head|size|
|:----|:---|
|`# h1 标题1`|32px|
|`## h2 标题2`|24px|
|`### h3 标题3`|20px|
|`#### h4 标题4`|12px|
|`##### h5 标题5`|14px|
|`###### h6 标题6`|12px|

测试标题结束

### 测试引用

以下是引用

> 这是引用
> 这是引用1

## 编写说明

### 左侧页面导航栏

```yml
---
title: 关于本站
layout: default
nav_order: 0.01
# nav_exclude: true
# parent: <父页面的title>
last_modified_date: 2026-01-22 11:58:00
---
```

说明：

- 在页首设置 `nav_order`，用于同级别页面的排序。可以是 数字、浮点数、字符串。用 0.00 ~ 9.99，是推荐的方式。
- 在页首设置 `nav_exclude: true`，可不显示在左侧导航栏中。
- 在页首设置 `parent: <父页面的title>`，可成为子页面。导航栏也呈现层次结构。

### Markdown 相关

1. 序号列表下的文字，要缩进 4 个空格。以确保序号不被打断，且下方文字相对于序号列表是缩进的。
2. 多使用 h2，可以用 h3，少用 h4。


[主题模板说明]: https://github.com/just-the-docs/just-the-docs-template/blob/main/README.md
[定制customization]: https://just-the-docs.github.io/just-the-docs/docs/customization/#customization
[配置configuration]: https://just-the-docs.github.io/just-the-docs/docs/configuration/
[用 Github + Markdown 创建个人网站]: https://gdv5.github.io/wssh/