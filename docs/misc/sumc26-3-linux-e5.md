---
title: e5-综合练习
layout: default
parent: Linux速成-2607
nav_order: 5
# nav_exclude: true
---

# e5-综合练习（Linux速成-2607）
{: .no_toc }
`更新-260722` \| `发布-260722`

通过综合练习，进一步熟悉 Linux 相关操作。

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<!-- <details markdown="block">
    <summary>ℹ️ 更新历史</summary>
<br>
**260622**
- 新增：[外观](#外观)
</details> -->

---

## 一切皆文件
<br>
这句话确实是理解Linux世界观的第一性原理，但它不是字面意思，而是一种设计哲学。我用最直白的方式拆解给你：

**1、到底什么是“文件”？**

在Linux眼里，文件就是一个字节流，也就是一串可以读、可以写的数据。为了管理这些数据，内核给每个“文件”都挂上了一个文件描述符（File Descriptor）——就是个整数编号（比如0、1、2）。

**2、“一切”都包含了什么？**

Linux把下面这几类东西，统统抽象成了文件：

- **普通数据文件**（txt、图片、视频）——这最好理解。
- **目录**（文件夹）——也被当成特殊文件，里面存的是文件名和inode的对应表。
- **硬件设备**（键盘、鼠标、硬盘、显示器）——在 `/dev/` 下体现。你往 `/dev/lp0`（打印机设备）写数据，打印机就动了；读 `/dev/input/mouse0`，就能拿到鼠标移动的原始数据。
- **进程信息**（内存、CPU状态）——在 `/proc/` 下。比如 `/proc/cpuinfo` 是个虚拟文件，你读它，内核就实时把CPU信息拼成字节流给你。
- **网络通信**（Socket套接字）——也被抽象成文件描述符，所以你可以用 `read()` 和 `write()` 去收发网络数据包。

**3、这么设计有什么惊天好处？**

统一的操作接口。不管操作对象是什么，你只需要学会5个系统调用：

> open() → read() → write() → close() → ioctl()

这就好比练武只练一套**基础拳法**，无论对面是木头人（硬盘文件）还是水流（键盘输入），都用同一套招式应对。程序员不必为每种新硬件学习新API，内核开发者只需把新设备驱动成“看起来像文件”即可。

**4、最容易踩的认知误区（重点）**

✳️“一切皆文件”不等于“一切皆普通文件”。

- 很多虚拟文件（如 `/dev/zero`、`/proc/meminfo`）**没有实际占用硬盘空间**，它们是内核凭空造出来的数据流。
- **管道（Pipe）**和 **Socket** 不支持 `lseek()`（文件指针跳转），因为数据像水流，流过去就没了，不能往回退着读。

**5、这个理念最生动的体现**

你试试在终端执行这条命令，就能亲眼看到“文件”的魔力：

```bash
echo "hello" > /dev/pts/0
```

（把/dev/pts/0换成你当前终端名，用 `tty` 命令查看）——你会看到自己发送的消息又显示在屏幕上，因为终端设备被当成文件，写进去就显示出来。大致步骤如下：

1. 启动 2 个终端

2. 在 2 个终端中，分别执行

    ```bash
tty
    ```

    可得到 2 个终端名。比如：第 1 个终端名是 `/dev/pts/1`，第 2 个终端名是 `/dev/pts/2`

3. 在第 1 个终端中执行

    ```bash
echo "hi pts#2, greeting from pts#1" > /dev/pts/2
    ```

    可在第 2 个终端中看到显示 `hi pts#2, greeting from pts#1`

4. 在第 2 个终端中执行

    ```bash
echo "hi pts#1, greeting from pts#2" > /dev/pts/1
    ```

    可在第 1 个终端中看到显示 `hi pts#1, greeting from pts#2`


✳️ **一句话总结：** Linux通过“文件”这个万能插座，统一了 **存储**、**计算**、**通信**、**控制** 四大领域。这是它40年长盛不衰的核心抽象。

[🔝](#top)

---

## 几种文件类型标志
<br>
执行 `ls -l`，你会看到类似这样的输出：

```bash
-rw-r--r--  1 user group  1024 Jul 22 10:00 normal.txt
drwxr-xr-x  2 user group  4096 Jul 22 10:00 mydir/
lrwxrwxrwx  1 user group    11 Jul 22 10:00 link -> target
crw-rw-rw-  1 root root   1,3  Jul 22 10:00 /dev/null
brw-rw----  1 root disk   8,1  Jul 22 10:00 /dev/sda1
srwxr-xr-x  1 user group     0 Jul 22 10:00 mysocket
prw-r--r--  1 user group     0 Jul 22 10:00 mypipe
```

**第一列首字符**就是类型标志：

|首字符|文件类型|中文名|典型例子|
|:---:|---|---|---|
|-	|普通文件	|常规数据文件|	.txt, .jpg, 可执行程序|
|d	|目录	|文件夹|	/home/, /etc/|
|l	|符号链接	|快捷方式（软链接）|	指向另一个文件的指针|
|c	|字符设备	|按字节流传输的设备|	键盘、鼠标、/dev/null|
|b	|块设备	|按数据块传输的设备|	硬盘 /dev/sda, U盘|
|s	|套接字	|进程间网络通信|	/var/run/docker.sock|
|p	|管道	|进程间单向数据传输（FIFO）|	命名管道（用mkfifo创建）|

### 逐行样例精讲（盯着第一列看）
<br>
```bash
-rw-r--r--  1 alice alice  1024 Jul 22 10:00 report.pdf
```
- `-` → 普通文件。这是最常见的数据文件。
- `rw-r--r--` 是权限位（后9个字符），与类型无关。


```bash
drwxr-xr-x  2 alice alice  4096 Jul 22 10:00 documents/
```
- `d` → 目录。注意权限中的 `x`（执行）对目录意味着**能否进入该目录**。


```bash
lrwxrwxrwx  1 alice alice    11 Jul 22 10:00 shortcut -> report.pdf
```
- `l` → 符号链接。箭头 `->` 指向真实文件。权限位永远是 `rwxrwxrwx`（实际权限看目标文件）。


```bash
crw-rw-rw-  1 root root   1, 3 Jul 22 10:00 /dev/null
```
- `c` → 字符设备。注意第五列不是文件大小，而是**主设备号（1）和次设备号（3）**，内核靠这个识别驱动程序。


```bash
brw-rw----  1 root disk   8, 1 Jul 22 10:00 /dev/sda1
```
- `b` → 块设备。同样显示主次设备号（8,1），表示硬盘第一个分区。


```bash
srwxr-xr-x  1 alice alice     0 Jul 22 10:00 mysocket
```
- `s` → 套接字。文件大小为0，因为数据不在硬盘上，只在内存中流通。


```bash
prw-r--r--  1 alice alice     0 Jul 22 10:00 mypipe
```
- `p` → 管道（FIFO）。数据流单向，写入端和读取端必须同时存在。

### 核心知识点补丁

1. 为什么设备文件（c/b）显示“主次设备号”而不是大小？

    因为设备文件不占用硬盘空间，它只是内核的一个访问入口。主设备号决定用哪个驱动，次设备号决定驱动管理哪个具体硬件。

2. 如何用命令快速查看文件类型？

    除了 `ls -l`，还可以用：

    ```bash
file report.pdf   # 输出：PDF document, version 1.4
    ```

    `file` 命令会读取文件内容特征（魔数），告诉你“这到底是个什么格式”，比 `ls` 更智能。

3. 如何创建这些特殊文件？

    - 普通文件：`touch file.txt`
    - 目录：`mkdir mydir`
    - 符号链接：`ln -s target linkname`
    - 管道：`mkfifo mypipe`
    - 套接字：通常由程序（如Nginx、Docker）自动创建
    - 设备文件：由内核在 `/dev/` 下自动生成（现代Linux用udev管理）

✳️ 一句话总结：

> `ls -l` 第一列的首字符，是Linux告诉你“这玩意儿本质是什么”的暗号——`-` 是数据，`d` 是抽屉，`l` 是标签，`c/b` 是硬件接口，`s/p` 是通信管道。

[🔝](#top)

---

## 权限位的结构拆解（3组 × 3个字符）
<br>
`-rw-r--r--` 去掉第一个的类型标志（比如 `-`），剩下的就是 9 位权限。按每3个字符一组，正好三组：

```text
 rw-  r--  r--
 [  ] [  ] [  ]
 用户  组  其他人
 (u)  (g)  (o)
```

对应关系：

- 第1-3位：文件所有者（User）的权限 → `rw-`
- 第4-6位：文件所属组（Group）的权限 →` r--`
- 第7-9位：其他人（Others）的权限 → `r--`

每个位置的字符含义是固定的：

|字符|	含义|	数值（二进制位）|
|:---:|---|---|
|r|	读权限（Read）	|4（100）|
|w|	写权限（Write）	|2（010）|
|x|	执行权限（eXecute）	|1（001）|
|-|	无此权限	|0|

所以 `rw-r--r--` 的数值表示是：

- 所有者：`rw-` = 4+2+0 = 6
- 组：`r--` = 4+0+0 = 4
- 其他人：`r--` = 4+0+0 = 4

合起来就是权限数字 **644**（这是Linux中最常见的文件权限）。

### `rwx` 在不同对象上的含义完全不同！（重点）
<br>
同样三个字母，对文件和目录的解释天差地别：

|权限|	对普通文件的含义|	对目录的含义|
|---|---|---|
|r（读）|	能读取文件内容（如cat）|	能列出目录内容（如ls），但前提是必须有x权限才能进入
|w（写）|	能修改/删除文件内容（如vim）|	能在目录内创建/删除/重命名文件（必须同时有x权限）
|x（执行）|	能执行该文件（如二进制程序或脚本）|	能进入该目录（如cd），是访问目录内任何文件的前提

关键陷阱：

- 对目录有 `w` 权限但没有 `x`，你无法删除里面的文件（因为进不去目录）。
- 对文件有 `r` 权限但没有 `x`，你能读脚本源码，但无法执行它。

### 权限位的“特殊附加项”
<br>
`ls -l` 显示的第一列是10个字符，不是9个。第1个是类型，后9个是标准权限，有时在第10个位置会出现额外字符：

```bash
-rwsr-xr-x  1 root root   /usr/bin/passwd
drwxrwsr-x  2 root staff  /shared/
drwxrwxrwt  1 root root   /tmp/
```

注意看：

- `rws` 中的 `s` → **SetUID**（执行时以文件所有者身份运行）
- `rws` 中的 `s`（组权限位）→ **SetGID**（执行时以文件所属组身份运行）
- 最后一位 `t` → **Sticky Bit**（粘滞位，只有文件所有者才能删除文件，**/tmp** 就是典型）

这些是高级权限，用数字表示时放在最前面：

- `4755` 表示 SetUID（4开头）
- `2770` 表示 SetGID（2开头）
- `1777` 表示 Sticky Bit（1开头，`/tmp` 就是 `drwxrwxrwt`）

### 实战演练：如何修改权限

1. **符号方式（更直观）**

    ```bash
chmod u+x file.txt    # 给所有者添加执行权限
chmod g-w file.txt    # 移除组的写权限
chmod o=r file.txt    # 设置其他人的权限为只读
chmod a+rwx file.txt  # 给所有人（all）所有权限
    ```

2. **数字方式（更快捷）**

    ```bash
chmod 644 file.txt    # rw-r--r--
chmod 755 script.sh   # rwxr-xr-x（所有者全权，组和其他只读+执行）
chmod 600 secret.txt  # rw-------（只有所有者能读写）
    ```

3. **查看当前用户的权限**

    ```bash
whoami          # 查看当前用户名
groups          # 查看当前用户所属组
    ```

### 一个容易混淆的经典例子
<br>
看这个权限：`-rw-r-----`

- 所有者：`rw-` → 可读可写
- 组：`r--` → 只读
- 其他人：`---` → 没有任何权限

如果我是其他人，想读这个文件 → **Permission denied**（即使我知道文件路径也不行）。

如果我是 **文件所有者**，但我不在文件所属组里 → 我拥有的是 `rw-`（所有者权限），而不是 `r--`（组权限）。

**核心规则：Linux权限检查按顺序匹配，命中即停。**

1. 你是所有者吗？是 → 用 `rw-`，不再看组权限。
1. 你不是所有者，但属于文件所属组？是 → 用 `r--`。
1. 两者都不是 → 用其他人权限 `---`。

✳️ **一句话总结**

> `rw-r--r--` 不是密码，而是一份权力清单：所有者能读写，同组人能看，其他人只能看。其中 `r` 是眼睛，`w` 是手，`x` 是脚——对文件来说是“能跑”，对目录来说是“能进”。

[🔝](#top)

---

## Linux综述
<br>
列一个 "Linux 生存必备清单" ，按紧急程度排序，每样都是刚需：

### 一、必须立刻补上的三块基石（优先级最高）
<br>

1. **文件操作三件套（你已经会 ls，还要会 cp/mv/rm）**

    - `cp -r` 复制目录
    - `mv` 移动或重命名（同一分区内是秒级，只是改文件名）
    - ‼️`rm -rf` 删除（极度危险，删了就没了，没有回收站）

2. **文本查看四兄弟（查日志必备）**

    |命令|	场景	|核心参数|
    |---|---|---|
    |cat|	看小文件	|没有分页，直接全量输出|
    |less|	看大文件（重点学）	|空格翻页，/搜索，q退出，G跳到最后|
    |head|	看文件开头	|-n 100 看前100行|
    |tail|	看文件结尾（看日志最常用）	|-f 实时跟踪（tail -f /var/log/syslog）|

3. **权限管理补刀**

    - `chmod` 改权限
    - `chown` 改所有者：`chown user:group file.txt`
    - `sudo` 临时提权（用root身份执行）

### 二、进程管理

查看进程：

|命令	|用途	|看什么|
|---|---|---|
|ps -ef	|看进程树关系	|父进程ID（PPID）、完整命令路径|
|ps aux	|看资源占用	|CPU%、内存%、VSZ/RSS（排查性能问题首选）|

三个高频搭配：

```bash
# 1. 找特定进程（最常用）
ps -ef | grep nginx

# 2. 找CPU/内存前10名
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# 3. 看树形结构（查服务启动依赖）
ps -ef --forest
```

<br>
信号控制（杀死/暂停进程）:

```bash
kill -15 PID    # 优雅终止（默认），进程可以清理现场
kill -9 PID     # 强制杀死（暴力，直接拔电源）
kill -1 PID     # 重新加载配置（不重启进程，nginx常用）
```

补充： pkill 按名字杀，killall 按名字杀所有同名进程。

### 三、网络与远程操作（服务器运维必备）
<br>
1. **远程连接**

    ```bash
ssh user@192.168.1.100 -p 22
    ```

加 -i key.pem 用密钥登录（云服务器标配）

2. **文件传输**

    ```bash
scp file.txt user@192.168.1.100:/home/user/   # 上传
scp user@192.168.1.100:/remote/file.txt .      # 下载
    ```

3. **端口与连接检查**

    ```bash
netstat -tulnp   # 看哪些端口在监听（-t TCP, -u UDP, -l 监听, -n 数字显示, -p 显示进程）
ss -tulnp        # netstat的现代替代，更快
    ```

### 四、文本处理三剑客（以后写脚本的命根子）
<br>
这三个是Linux文本处理的灵魂，你现在不必全懂，但必须知道它们能干什么：

- `grep` → 搜内容：`grep "error" /var/log/syslog`
- `sed` → 替换/编辑：`sed 's/old/new/g' file.txt`
- `awk` → 切列/统计：`ps aux | awk '{print $2}'`（打印第二列）

实战例子： 找出所有nginx进程的PID

```bash
ps -ef | grep nginx | grep -v grep | awk '{print $2}'
```

### 五、系统信息查看（出问题先看这些）

```bash
top / htop          # 实时资源监控（htop更友好，需要安装）
df -h               # 磁盘使用情况（-h 人类可读）
du -sh *            # 查看当前目录下每个文件/文件夹的大小
free -h             # 内存使用情况
uname -a            # 内核版本信息
uptime              # 系统运行时间和负载
dmesg | tail        # 内核日志（看硬件报错）
```

### 六、包管理与服务控制（软件装与启）
<br>

1. **安装软件（不同发行版不一样）**

    ```bash
apt update && apt install nginx # Debian/Ubuntu

yum install nginx   # CentOS/RHEL 老版本 
dnf install nginx   # CentOS/RHEL 新版本
    ```

2. **管理服务（systemd）**

    ```bash
systemctl start nginx   # 启动
systemctl stop nginx    # 停止
systemctl restart nginx # 重启
systemctl status nginx  # 看状态
systemctl enable nginx  # 开机自启
    ````

### 七、管道与重定向（把命令串起来的胶水）
<br>
这是Linux最酷的设计，把前面学的所有东西串起来：

```bash
# | 管道：把左边输出作为右边输入
ps aux | grep nginx

# > 重定向：输出到文件（覆盖）
echo "hello" > file.txt

# >> 重定向：追加到文件
echo "world" >> file.txt

# 2> 错误重定向
command 2> error.log

# &> 所有输出重定向
command &> output.log
```

### 八、学习路线图（按这个顺序刷）
<br>
- 文件操作（ls/cp/mv/rm）+ 文本查看（cat/less/tail）
- 权限（chmod/chown）+ 进程（ps/kill）
- 网络（ssh/scp/netstat）+ 服务（systemctl）
- 文本三剑客（grep/sed/awk）入门
- 综合实战（写一个监控脚本）

### 九、两个救命技能（必须会）

1. **查命令用法**

    ```bash
man ps      # 完整手册（按 q 退出）
ps --help   # 快速帮助
    ```

    > [编者按] 也可以问问大模型

2. **在vim里怎么退出（新手必死题）**

    ```text
按 Esc → 输入 :q! → 回车（强制退出不保存）
按 Esc → 输入 :wq → 回车（保存并退出）
    ```

<br>
✳️ **一句话总结**

> **你已经有了"看懂Linux"的底子，现在差的是"操作肌肉记忆"：文件搬移、日志查看、进程管理、网络连通、软件安装——这五件事熟练了，你就是合格的运维工程师。**

> 建议你现在打开终端，把每个命令都敲一遍。

<!--  -->
<span style="font-size:12px; color:#999">THE END</span>