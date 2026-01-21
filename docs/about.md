# 建站过程

本文记录了相关测试和建站过程，供后续类似网站的建设供参考。

## 新建仓库 tnt

在 github 账号 gdvzz 下，新建仓库 tnt。过程从略。

## 关联远程仓库

1. 在本地电脑已有目录 `~/gdvzz` 下，新建子目录 `tnt`，用于本地存放网站内容。

2. 新建文档 `~/gdvzz/tnt/docs/readme.md`，作为网站的首页。

3. 在 `~/gdvzz/tnt` 依次执行以下命令，将本地仓库关联到远程仓库，并完成首次提交。如下：

    ```bash
    ~/gdvzz/tnt % git status
    ~/gdvzz/tnt % git add .
    ~/gdvzz/tnt % git commit -m "1st commit"
    ~/gdvzz/tnt % git branch -M master
    ~/gdvzz/tnt % git remote add tnt git@githubvzz.com:gdvzz/tnt.git
    ~/gdvzz/tnt % git push -u tnt master
    ```

上述命令参考了 github 新建仓库后的如下提示信息：

```bash
…or create a new repository on the command line

echo "# tnt" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:gdvzz/tnt.git
git push -u origin main

…or push an existing repository from the command line

git remote add origin git@github.com:gdvzz/tnt.git
git branch -M main
git push -u origin main
```

## 基础配置

参考 [just-the-docs-template-README]，做相关基础配置。

1. 复制 pages.yml
    
    在网站的根目录下，新建子目录 `.github/workfolws`, 然后复制 `pages.yml` 到该子目录。该文件就是 GitHuab Actions 需要的工作流文件。

    经测试，应该放在 `~/gdvzz/tnt` 目录下。因为 `pages.yml` 中指定了网站内容放在 `~/gdvzz/tnt/docs` 中。

2. 复制了 .gitignore 到 ~/gdvzz/tnt 目录中。

3. 复制了 Gemfile 到 ~/gdvzz/tnt/docs 目录中。

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
    name: Deploy Jekyll site to Pages
    
    on: # 只有 master 分支的 docs 下的文件变化，才会重新编译和部署网站
      push:
        branches: 
          - "master"
        paths:
          - "docs/**"
    
      # Allows you to run this workflow manually from the Actions tab
      workflow_dispatch:
    
    # Sets permissions of the GITHUB_TOKEN to allow deployment to GitHub Pages
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
              bundler-cache: true # runs 'bundle install' and caches installed gems automatically
              cache-version: 0 # Increment this number if you need to re-download cached gems
              working-directory: '${{ github.workspace }}/docs' # 增加工作目录参数
          - name: Setup Pages
            id: pages
            uses: actions/configure-pages@v5
          - name: Build with Jekyll
            # Outputs to the './_site' directory by default
            run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
            env:
              JEKYLL_ENV: production
          - name: Upload artifact
            # Automatically uploads an artifact from the './_site' directory by default
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

5. 修改后的 `_coonfig.yml` 如下：

    ```yml
    # title: Just the Docs Template
    # description: A starter template for a Jeykll site using the Just the Docs theme!
    title: "Try and Test"
    description: "学习笔记，使用指导文档，等"
    theme: just-the-docs
        
    # url: https://just-the-docs.github.io
    url: https://gdvzz.github.io
        
    # aux_links:
    # Template Repository: https://github.com/just-the-docs/just-the-docs-template
    ```

## 定制样式

参考该主题的 [定制-customization], css 样式的定制可以写在 `_sass/custom/custom.scss` 中。比如：

```scss
// 文件路径：~/gdvzz/tnt/docs/_sass/custom/custom.scss
// 覆盖 H2 标题的样式
h2 {
    font-size: 60px !important; // 将字体大小设置为 60 像素
}
```

1. 对部分内容的字体和大小做更改

    ```scss
    // 对相关 css 设置做定制
    // 以下设置将覆盖 just-the-docs theme 原有对应数值
    
    body {
        // font-family: system-ui, -apple-system, blinkmacsystemfont, "Segoe UI", roboto, "Helvetica Neue",     arial, sans-serif, "Segoe UI Emoji";
        // font-size: inherit;
        // line-height: 1.4;
        // color: #5c5962;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color     Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        color: #24292e !important;
    }
    
    h1 {
        font-size: 2em !important; // 32px
    }
    
    h2 {
        font-size: 1.5em !important; // 24px
    }
    
    h3 {
        font-size: 1.25em !important; // 20px
    }
    ```

后续如有其他样式改动，也可写在这个文件中。先用浏览器的 Inspect 功能确定期望改动的样式是什么标签（或 class），然后再在该文件中写上对应的样式，才能覆盖成功。

## 发布网站

参考 [just-the-docs-template-README]，到对应仓库下，然后进入 Settings > Pages > Build and deployment > Source, 选择 `GitHub Actions` 即可。

- 选择 GitHub Actions 后，可不必理会屏幕提示 “Use a suggested workflow, browse all workflows, or create your own. ”，因为 `pages.yml` 都已经写好了。
- 不要选择 `Deploy from a branch`。应该上也是可以的，但相关配置文件要做对应调整，才可以部署成功。

## 主题配置

```yml
footer_content: 'Copyright &copy; 2017-2026 Patrick Marsceill and Just the Docs contributors. Distributed by an <a href="https://github.com/just-the-docs/just-the-docs/tree/main/LICENSE.txt">MIT license.</a> <a href="https://www.netlify.com/">This site is powered by Netlify.</a>'
```

[just-the-docs-template-README]: https://github.com/just-the-docs/just-the-docs-template/blob/main/README.md
[定制-customization]: https://just-the-docs.github.io/just-the-docs/docs/customization/#customization