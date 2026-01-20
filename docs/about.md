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
    
    在网站内容的根目录（当前是 `~/gdvzz/tnt/docs`）下，新建子目录 `.github/workfolws`, 然后复制 `pages.yml` 到该子目录。该文件就是 GitHuab Actions 需要的工作流文件。

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

## 定制

参考该主题的 [定制-customization], css 样式的定制可以写在 `_sass/custom/custom.scss` 中。比如：

```scss
// 文件路径：~/gdvzz/tnt/docs/_sass/custom/custom.scss
// 覆盖 H2 标题的样式
h2 {
    font-size: 60px !important; // 将字体大小设置为 60 像素
}
```

### 文字大小

```scss
body {
    // font-family: system-ui, -apple-system, blinkmacsystemfont, "Segoe UI", roboto, "Helvetica Neue", arial, sans-serif, "Segoe UI Emoji";
    // font-size: inherit;
    // line-height: 1.4;
    // color: #5c5962;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
    font-size: 16px;
    line-height: 1.5;
    color: #24292e;
}

h1 {
    font-size: 2rem !important; // 32px
}

h2 {
    font-size: 1.5rem !important; // 24px
}

h3 {
    font-size: 1.125rem !important; // 20px
}
```



[just-the-docs-template-README]: https://github.com/just-the-docs/just-the-docs-template/blob/main/README.md
[定制-customization]: https://just-the-docs.github.io/just-the-docs/docs/customization/#customization