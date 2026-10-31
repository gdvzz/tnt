---
title: AI教具维护
layout: default
parent: aikit教具
# nav_order: 9001
nav_exclude: true
---

# AI教具维护
{: .no_toc }
`更新-261013` \| `发布-260326`

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<details markdown="block">
  <summary>✳️ 历史</summary>
261013<br>
    （1）增加 [开发板开机快速时间同步（sntp-once）操作说明](#开发板开机快速时间同步sntp-once操作说明)
    （2）增加 [日志持久化操作](#日志持久化操作)
<br>
261012<br>
    （1）增加 [插网线 6 小时会断网](#插网线-6-小时会断网dhcp-客户端-id-修复方案)
</details>
---

## 约定

- 视觉实验箱：viki (VIsual KIt)
- NLP 实验箱：nlpx (NLP)
- 昇腾开发板：aidk (Ascend Innovation / Artificial Intelligence Developer Kit )
- 鲲鹏开发板：dkoo (Like 'd cool'. dk = Developer Kit, k also for Kunpeng, oo = 2 Orange Pi)

----

## vkai-硬盘只有50G

### 问题

在使用大于镜像内存的U盘或者固态硬盘烧录镜像以后，会出现一部分的空闲内存无法被使用，导致出现使用空间不足的报错，或运行大型项目不成功。

注意：本教程仅针对自行烧录镜像的用户，U盘或者固态硬盘内如有出厂镜像则可跳过本教程。U盘和固态硬盘的扩容方式相同，本节以Jetson Nano（U盘）为例。

### 解决方案

1. 安装扩容软件，使用扩容软件进行扩容。

    ```bash
sudo apt install gparted
    ```

2. 打开该软件，找到硬盘。‼️注意，此步骤一定要确认操作的硬盘设备号是正确的。

    如果是Jetson Orin NX/Orin Nano主板使用固态硬盘，设备号是【/dev/nvme0n1】（👈 vkai 是这个）
    
    Jetson Nano系统找到【/dev/sda】设备。

3. 选中设备主分区【APP】，右键选择【Resize/Move】。

4. 将右边的框拉到顶，直至灰色区域变为全白，然后点击 **Resize**

5. 点击功能栏下方的绿色的钩，再点击 **Apply**

6. 完成扩容后，使用指令在终端进行查询验证

    ```bash
df -h
    ```

> 参考资料：[JetCobot 机械臂 > Linux操作系统 > 13.扩容教程↗](https://www.yahboom.com/build/id/10424/cid/648)

> 要输入提取码才能访问。


---

## 插网线 6 小时会断网（DHCP 客户端 ID 修复方案）

### 问题背景

Ubuntu / NetworkManager 内置 DHCP 客户端默认使用 **RFC 4361 规定的 DUID 形式**的客户端 ID（类型码 `255` + IAID + DUID）。部分 DHCP 服务器（校园网、企业网关、老旧设备）只认传统的 **MAC 形式**（类型码 `1` + MAC），导致客户端 ID 不匹配，DHCP 流程中断，并可能伴随 `ICMP Destination Unreachable` 异常。

现象：开发板插网线 6 小时左右，会断网。

**修复方式**：将 DHCP 客户端 ID 改为 `mac`，让双方“说同一种语言”。

---

### 一、修改步骤

**1. 查看当前状态（体检，可选但推荐）**

```bash
nmcli -f ipv4.method,ipv4.dhcp-client-id,ipv4.dhcp-timeout,ipv4.route-metric connection show "Wired connection 1"
```

期望看到（修改前）：

```text
ipv4.method:                            auto
ipv4.dhcp-client-id:                    --
ipv4.dhcp-timeout:                      0 (default)
ipv4.route-metric:                      -1
```

**2. 确认连接名称**

```bash
nmcli connection show
```

找到你实际使用的有线连接名（本例为 `Wired connection 1`，设备 `eth0`）。下文命令中的连接名请按需替换。

**3. 修改 DHCP 客户端 ID 为 MAC 地址**

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.dhcp-client-id mac
```

**4. 重新激活连接**

```bash
sudo nmcli connection up "Wired connection 1"
```

> ⚠️ 若通过 SSH 操作，此步会短暂断线。建议在开发板本地终端执行，或准备好备用登录方式。

**5. 验证 IP 是否获取成功**

```bash
ip -4 addr show eth0
nmcli -f IP4 connection show "Wired connection 1"
```

期望输出示例：

```text
IP4.ADDRESS[1]:                         172.18.145.90/24
IP4.GATEWAY:                            172.18.145.1
IP4.DNS[1]:                             210.28.28.28
IP4.DNS[2]:                             210.28.29.30
```

**6. 查看日志确认 DHCP 成功绑定**

```bash
journalctl -u NetworkManager -b --no-pager | grep -i -E 'dhcp4 \(eth0\)|icmp|unreachable' | tail -30
```

关键标志：

```text
dhcp4 (eth0): state changed unknown -> bound
dhcp4 (eth0): option ip_address => '172.18.145.90'
dhcp4 (eth0): option routers    => '172.18.145.1'
```

看到 `bound` 且有正确地址，即成功。**若日志中不再出现 `icmp` / `unreachable`**，说明 ICMP 异常也随之消失（它是“果”不是“因”）。

**7. 测试网络连通性**

```bash
ping -c 3 172.18.145.1        # 网关
ping -c 3 210.28.28.28        # DNS
ping -c 3 www.baidu.com       # 外网 + DNS 解析
ping -4 -c 3 www.baidu.com    # 强制走 IPv4 测外网
```

**8. 确认配置已持久化**

```bash
nmcli -f ipv4.dhcp-client-id connection show "Wired connection 1"
```

应输出：

```text
ipv4.dhcp-client-id:                    mac
```

该配置写入连接文件，**重启后自动生效**，无需额外操作。

---

### 二、回滚步骤

**1. 恢复默认客户端 ID**

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.dhcp-client-id ""
```

`""` 表示恢复为空，即使用 NetworkManager 默认的 DUID 形式。

**2. 重新激活连接**

```bash
sudo nmcli connection up "Wired connection 1"
```

**3. 验证是否恢复**

```bash
nmcli -f ipv4.dhcp-client-id connection show "Wired connection 1"
```

应输出：

```text
ipv4.dhcp-client-id:                    --
```

**4. 若之前还改过其他参数（本例未改）**

如果曾经调整过超时或 MTU，一并恢复：

```bash
sudo nmcli connection modify "Wired connection 1" \
  ipv4.dhcp-timeout 0 \
  ethernet.mtu 1500
sudo nmcli connection up "Wired connection 1"
```

**5. 确认网络仍正常**

```bash
ip -4 addr show eth0
ping -c 3 172.18.145.1
```

---

### 三、命令速查表

| 操作 | 命令 |
|---|---|
| 查看 DHCP 相关配置 | `nmcli -f ipv4.method,ipv4.dhcp-client-id,ipv4.dhcp-timeout connection show "<连接名>"` |
| 查看所有连接 | `nmcli connection show` |
| **修改**为 MAC 客户端 ID | `sudo nmcli connection modify "<连接名>" ipv4.dhcp-client-id mac` |
| 重新激活连接 | `sudo nmcli connection up "<连接名>"` |
| 断开连接 | `sudo nmcli connection down "<连接名>"` |
| 查看 IP | `ip -4 addr show eth0` |
| 查看 IP4 详情 | `nmcli -f IP4 connection show "<连接名>"` |
| 查看 DHCP 日志 | `journalctl -u NetworkManager -b --no-pager \| grep -i -E 'dhcp\|icmp\|unreachable' \| tail -30` |
| **回滚**为默认 | `sudo nmcli connection modify "<连接名>" ipv4.dhcp-client-id ""` |
| 恢复 MTU 默认 | `sudo nmcli connection modify "<连接名>" ethernet.mtu 1500` |

---

### 四、注意事项

1. **连接名要替换**：`"Wired connection 1"` 是本例名称，请用 `nmcli connection show` 确认你自己的连接名。
2. **SSH 会断线**：`connection up/down` 会中断网络，SSH 操作时请准备好本地终端或备用方式。
3. **配置自动持久化**：`nmcli connection modify` 会立即写入配置文件，重启后依然生效。
4. **不要画蛇添足**：本问题只需改 `ipv4.dhcp-client-id` 一项，**不需要**改 MTU、超时，**不需要**更换 `dhclient`/`dhcpcd`，**不需要**加防火墙规则丢弃 ICMP。
5. **换网络环境**：`ipv4.dhcp-client-id mac` 是通用且安全的选择，换到家庭路由器等其他环境通常无需改回。
6. **回滚后问题复现属正常**：回滚到默认 DUID 形式后，如果服务器仍不兼容，原问题会重新出现——这正说明修复是针对 client-id 不匹配的。

---

### 五、原理简述

| 项目 | 默认（internal 客户端） | 修复后（`mac`） |
|---|---|---|
| client-id 类型码 | `255`（RFC 4361 DUID） | `1`（RFC 2132 硬件地址） |
| 实际内容 | IAID + DUID（基于 machine-id 等） | 直接使用 eth0 的 MAC |
| 服务器兼容性 | 需支持 RFC 4361 | 传统服务器普遍支持 |
| 现象 | 不匹配时 DHCP 中断，可能伴随 ICMP 异常 | 正常 `bound`，无异常 |

**本质**：协议扩展（RFC 4361）与传统实现之间的兼容性问题。改成 `mac` 就是让客户端和服务器“说同一种语言”。

---

### 思考

原来会断网时，先 `nmcli conn down <连接名称>`，再 `nmcli conn up <连接名称>`，是否应该拿不到 IP 地址？

试了 1 台，是可以拿到 IP 地址的（← 不符合期望）。

大模型一通解释，大致是这是偶然，可以对不同的 IP 段，处理有点不同（← 不符合期望）

先放过大模型。先到此为止。

### 还是要改成 dhclient
<br>
经比对测试，还是要改成 dhclient 方式。相关操作如下：

```bash
# 安装
sudo apt update; sudo apt install -y isc-dhcp-client

# 配置
sudo tee /etc/NetworkManager/conf.d/10-use-dhclient.conf > /dev/null << 'EOF'
[main]
dhcp=dhclient
EOF

# 重启 NetworkManager（SSH 会短暂断线）
sudo systemctl restart NetworkManager
```

改完后验证：

```bash
echo "=== dhcp backend ==="; NetworkManager --print-config | grep -i dhcp; echo "=== client-id ==="; nmcli -f ipv4.dhcp-client-id connection show "Wired connection 1"; echo "=== IP ==="; ip -4 addr show eth0 | grep inet; echo "=== 路由 ==="; ip route; echo "=== dhclient ==="; ps aux | grep dhclient | grep -v grep
```

[🔝](#top)

---

## 开发板开机快速时间同步（sntp-once）操作说明

适用于无 RTC 电池的 ARM 开发板（Jetson、树莓派等），系统使用 `systemd` 且已安装 `ntp` 包（包含 `sntp` 命令）。解决开机后系统时间停留在 1970 或旧日期，需等待 1–2 分钟才被 `ntpd` 校正的问题。

---

### 一、问题背景

- 开发板没有 RTC 电池，断电后 RTC 丢失，开机默认时间常为 `1970-01-01` 或 `2023-11-22`。
- 系统使用 `ntp` 服务同步时间，但 `ntpd` 首次同步需要 1–2 分钟（轮询周期 + 步进确认）。
- 期间依赖正确时间的程序（ROS、日志、证书校验等）会异常。
- 需要一个开机时快速、一次性强制校时的服务，在 `ntpd` 之前把时间大致调对。

---

### 二、原理

- `sntp` 是 `ntp` 包自带的一次性 SNTP 客户端，可与 NTP 服务器通信并立即调整系统时间。
- 使用 `-S`（大写）选项：**强制步进（step）** 系统时间，适合冷启动时时间偏差巨大的场景。
- 若使用 `-s`（小写）：尝试平滑调整，时间差过大时会报 `adj_systime: Invalid argument` 而失败。
- 配合 `systemd` 服务，在网络就绪后、`ntp.service` 之前执行，失败自动重试。

---

### 三、前置检查

```bash
# 1. 确认系统使用 systemd
systemctl --version

# 2. 确认已安装 ntp 包（含 sntp）
which sntp
# 若未安装：
# sudo apt update && sudo apt install ntp

# 3. 确认没有使用 chrony（两者冲突）
systemctl is-active chrony chronyd 2>/dev/null
# 若 chrony 处于 active，请勿使用本方案，改用 chrony 的 makestep 配置

# 4. 确认当前时间同步服务
timedatectl
systemctl is-enabled ntp
```

---

### 四、配置步骤

**1. 创建 systemd 服务文件**

将下方命令中的 NTP 服务器地址替换为你网络中最快、最稳定的源（可用 `ntpq -p` 查看当前 `*` 标记的服务器）。

```bash
sudo tee /etc/systemd/system/sntp-once.service > /dev/null << 'EOF'
[Unit]
Description=One-shot SNTP sync at boot
After=network-online.target
Wants=network-online.target
Before=ntp.service

[Service]
Type=oneshot
ExecStart=/usr/bin/sntp -S -t 10 210.28.130.4 time.neu.edu.cn
Restart=on-failure
RestartSec=5
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
```

参数说明：

| 参数 | 作用 |
|---|---|
| `After=network-online.target` | 等待网络就绪 |
| `Wants=network-online.target` | 拉入网络依赖 |
| `Before=ntp.service` | 在 ntpd 之前执行，避免 socket 冲突 |
| `-S` | 强制步进时间，解决大时间差 |
| `-t 10` | 超时 10 秒 |
| `Restart=on-failure` | 失败自动重试 |
| `RestartSec=5` | 重试间隔 5 秒 |
| `RemainAfterExit=yes` | 执行完保持 active (exited) 状态 |

**2. 重载并启用服务**

```bash
sudo systemctl daemon-reload
sudo systemctl enable sntp-once.service
systemctl is-enabled sntp-once.service
# 应输出 enabled
```

**3. 立即测试（非冷启动）**

```bash
sudo systemctl start sntp-once.service
systemctl status sntp-once.service --no-pager
journalctl -u sntp-once.service --no-pager -n 20
```

期望看到：

- `Active: active (exited)` + `status=0/SUCCESS`
- 日志中有 `sntp[...]: 2026-xx-xx ... +0.xxx ... <服务器地址>`
- 无 `adj_systime: Invalid argument`

---

### 五、冷启动验证（必须）

热重启（`reboot`）不会丢失 RTC，无法验证。必须**完全断电**后重新上电。

```bash
# 1. 关机
sudo shutdown -h now

# 2. 等待指示灯全灭，拔掉电源，等 5–10 秒

# 3. 重新上电，立即登录系统

# 4. 第一时间执行以下命令
date
systemctl status sntp-once.service --no-pager
journalctl -b -u sntp-once.service --no-pager | head -30
```

判断标准：

| 观察 | 结论 |
|---|---|
| 登录后 `date` 在 30 秒内显示正确年份 | ✅ 成功 |
| 服务最终 `active (exited)` + `status=0/SUCCESS` | ✅ 成功 |
| 日志中有成功同步记录 `sntp[...]: 2026-...` | ✅ 成功 |
| 日志开头为 `1970-01-01` 但随后跳到正确时间 | 正常，说明 RTC 丢失，sntp 已校正 |
| 无 `adj_systime: Invalid argument` | ✅ `-S` 生效 |
| 第一次 `Network is unreachable` 后自动重试成功 | ✅ `Restart` 机制生效 |

---

### 六、日志持久化（推荐）

默认 journal 日志保存在内存，重启后丢失。建议持久化，便于排查。

```bash
sudo mkdir -p /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo systemctl restart systemd-journald
ls -l /var/log/journal/
```

---

### 七、排错

| 现象 | 原因 | 解决 |
|---|---|---|
| `adj_systime: Invalid argument` | 使用了 `-s` 而非 `-S` | 修改 `ExecStart` 为 `-S` |
| `Network is unreachable` | 网络未就绪，首次执行失败 | 已配置 `Restart` 自动重试；若持续失败，可适当增加 `RestartSec` 或检查 `network-online.target` |
| `time.neu.edu.cn lookup error` | DNS 未就绪 | 可改用纯 IP 的 NTP 服务器，或等待重试 |
| 服务未执行 | 未 enable 或未 daemon-reload | 执行 `systemctl enable sntp-once` 并 `daemon-reload` |
| 时间仍然很慢 | `ntp` 与 `sntp-once` 顺序颠倒 | 确认 `Before=ntp.service`，检查 `systemctl list-dependencies` |
| `which sntp` 无输出 | 未安装 ntp 包 | `sudo apt install ntp` |

---

### 八、回滚

```bash
# 停止并禁用服务
sudo systemctl stop sntp-once.service
sudo systemctl disable sntp-once.service

# 删除服务文件
sudo rm /etc/systemd/system/sntp-once.service

# 重载 systemd
sudo systemctl daemon-reload

# 确认 ntp 仍然正常
systemctl status ntp --no-pager
```

---

### 九、可选优化

**1. 缩短重试间隔**

将 `RestartSec=5` 改为 `2`，使首次同步更快：

```bash
sudo sed -i 's|RestartSec=5|RestartSec=2|' /etc/systemd/system/sntp-once.service
sudo systemctl daemon-reload
sudo systemctl restart sntp-once.service
```

**2. 使用多个 NTP 服务器**

在 `ExecStart` 中追加备用服务器，提高成功率：

```bash
ExecStart=/usr/bin/sntp -S -t 10 210.28.130.4 time.neu.edu.cn ntp.ubuntu.com
```

**3. 更换为 chrony（更现代的替代方案）**

若系统允许，可改用 `chrony`，其 `makestep` 配置对开机校时支持更好：

```bash
sudo apt install chrony
echo "makestep 1.0 3" | sudo tee -a /etc/chrony/chrony.conf
sudo systemctl disable --now ntp sntp-once.service
sudo systemctl enable --now chrony
```

**4. 硬件加装 RTC 电池（最彻底）**

为开发板加装 RTC 纽扣电池（如 CR1220），断电后时间不丢失，开机即准，无需网络校时。

---

### 十、总结

- 核心命令：`sntp -S -t 10 <NTP服务器>`，`-S` 必须大写。
- 服务必须在 `ntp.service` 之前运行（`Before=ntp.service`）。
- 依赖 `network-online.target` 并配置自动重试，可容忍首次网络未就绪。
- 冷启动验证是唯一可靠的验证方式（`reboot` 不算）。
- 建议同时做日志持久化，便于长期观察。

[🔝](#top)

---

## 日志持久化操作

解决 Ubuntu / Jetson 等设备默认将系统日志保存在内存（`/run/log/journal`）、重启后丢失的问题。持久化后日志写入磁盘，重启后仍可查询，便于排查故障。同时限制日志大小，防止占满 eMMC / SD 卡。

---

### 一、操作步骤

**1. 创建持久化目录**

```bash
sudo mkdir -p /var/log/journal
```

**2. 创建配置目录**

```bash
sudo mkdir -p /etc/systemd/journald.conf.d
```

**3. 写入配置（限制 500M，保留 7 天）**

```bash
sudo tee /etc/systemd/journald.conf.d/persistent.conf > /dev/null << 'EOF'
[Journal]
Storage=persistent
SystemMaxUse=500M
SystemKeepFree=1G
SystemMaxFileSize=100M
MaxRetentionSec=7day
EOF
```

**4. 初始化 journal 目录结构（关键步骤）**

```bash
sudo systemd-tmpfiles --create --prefix /var/log/journal
```

> 这一步会创建 `/var/log/journal/<machine-id>/` 子目录并设置正确权限（`root:systemd-journal` + `2755` + ACL）。只用 `mkdir` 不够，journald 不会识别。

**5. 重载并重启 journald**

```bash
sudo systemctl daemon-reload
sudo systemctl restart systemd-journald
```

---

### 二、验证

```bash
# 1. 确认目录和文件已创建
ls -lh /var/log/journal/
ls -lh /var/log/journal/<machine-id>/

# 2. 确认 File path 已切到 /var/log/journal
journalctl --header | head -3

# 3. 确认配置已加载
systemd-analyze cat-config systemd/journald.conf | tail -10

# 4. 查看当前占用
journalctl --disk-usage
```

**成功标志**：

- `ls` 能看到 `/var/log/journal/<machine-id>/` 目录，里面有 `system.journal` 等文件；
- `journalctl --header` 第一行为 `File path: /var/log/journal/<machine-id>/system.journal`（而不是 `/run/log/journal/`）；
- `cat-config` 末尾显示 `Storage=persistent` 等配置；
- `--disk-usage` 显示非零大小。

---

### 三、配置参数说明

| 参数 | 值 | 作用 |
|---|---|---|
| `Storage=persistent` | 持久化 | 日志写入磁盘，重启保留 |
| `SystemMaxUse=500M` | 500MB | 日志总占用上限 |
| `SystemKeepFree=1G` | 1GB | 磁盘至少保留的空闲空间 |
| `SystemMaxFileSize=100M` | 100MB | 单个日志文件上限 |
| `MaxRetentionSec=7day` | 7 天 | 日志最长保留时间 |

两个限制**同时生效，先到先得**：达到 500MB 或超过 7 天，都会触发清理。

---

### 四、日常维护（可选）

```bash
# 只保留最近 7 天
sudo journalctl --vacuum-time=7d

# 只保留最近 500MB
sudo journalctl --vacuum-size=500M

# 只保留最近 5 个日志文件
sudo journalctl --vacuum-files=5

# 查看当前占用
journalctl --disk-usage
```

---

### 五、常见问题

| 现象 | 原因 | 解决 |
|---|---|---|
| `tee: ... No such file or directory` | 配置目录不存在 | `sudo mkdir -p /etc/systemd/journald.conf.d` |
| `File path` 仍是 `/run/log/journal/` | 缺少 tmpfiles 初始化 | `sudo systemd-tmpfiles --create --prefix /var/log/journal` 后重启 journald |
| 配置写了但未生效 | journald 未重启或未 daemon-reload | `sudo systemctl daemon-reload && sudo systemctl restart systemd-journald` |
| 目录权限不对 | 手动 mkdir 未设权限 | `sudo chown root:systemd-journal /var/log/journal && sudo chmod 2755 /var/log/journal`，或重跑 tmpfiles |
| 主配置冲突 | `/etc/systemd/journald.conf` 里有 `Storage=volatile` | 注释掉主配置里的 `Storage=` 行 |
| `--list-boots` 只有一个 | 时间跳变（无 RTC 电池） | 正常现象，非配置问题；根治需加装 RTC 电池 |

---

### 六、回滚

```bash
# 1. 删除自定义配置
sudo rm /etc/systemd/journald.conf.d/persistent.conf

# 2. 重载并重启
sudo systemctl daemon-reload
sudo systemctl restart systemd-journald

# 3. 可选：删除持久化目录，回到内存模式
sudo rm -rf /var/log/journal
sudo systemctl restart systemd-journald
```

回滚后，`journalctl --header` 的 `File path` 会变回 `/run/log/journal/...`。

---

### 七、说明

- 默认情况下 journald 已限制日志为磁盘的 10%（上限 4GB），不会无限增长。
- 本方案将上限压到 500MB + 7 天，更适合 eMMC / SD 卡空间有限的开发板。
- 500MB 通常能保留数周日志，加 7 天上限后实际占用一般远低于 500MB。
- `SystemKeepFree=1G` 保证磁盘至少留 1GB 空闲，进一步防止撑爆。
- 若磁盘非常紧张（< 8GB 可用），可将 `SystemMaxUse` 调到 `200M`。

[🔝](#top)

---

## 相关脚本
<br>
以下为相关脚本，用于 boardfleet 主控管理系统。

### viki-dhcp-dhclient
`更新-261022` \| `发布-261020`

- 现象：插网线时，每 6 小时会断网
- 方案：修改 dhcp 方式为 dhclient
- 适用：viki


```bash
#!/bin/bash
set -e

CONF="/etc/NetworkManager/conf.d/10-use-dhclient.conf"
CURRENT_DHCP=$(NetworkManager --print-config 2>/dev/null | grep -E "^dhcp=" | head -1)
NEED_RESTART=0

echo "开始检查并配置 dhclient..."

# 1. 检查并安装依赖
if ! dpkg -l 2>/dev/null | grep -q "^ii.*isc-dhcp-client"; then
    echo "未安装 isc-dhcp-client，开始安装..."
    apt update
    apt install -y isc-dhcp-client
else
    echo "isc-dhcp-client 已安装，跳过。"
fi

# 2. 检查并写入配置文件
mkdir -p /etc/NetworkManager/conf.d
if [ ! -f "$CONF" ] || ! grep -q "^dhcp=dhclient" "$CONF"; then
    echo "写入配置 $CONF..."
    cat > "$CONF" << 'EOF'
[main]
dhcp=dhclient
EOF
    NEED_RESTART=1
else
    echo "配置文件已存在且正确，跳过。"
fi

# 3. 检查运行状态
if [ "$CURRENT_DHCP" != "dhcp=dhclient" ]; then
    echo "当前运行状态不是 dhclient，准备重启 NetworkManager..."
    NEED_RESTART=1
fi

# 4. 按需重启 NetworkManager
if [ "$NEED_RESTART" = "1" ]; then
    echo "正在重启 NetworkManager，网络会短暂断开（主控会自动重连并回传结果）..."
    systemctl restart NetworkManager
    echo "NetworkManager 重启完成。"
    # 等待几秒让网络稳定
    sleep 3
else
    echo "已经是 dhclient 模式且运行正常，无需重启 NetworkManager。"
fi

# 5. 【新增】自动清理 secondary IP 残留
echo "检查并清理多余的次要 IP 残留..."
# 获取所有 IPv4 地址
IPS=$(ip -4 addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1)
IP_COUNT=$(echo "$IPS" | wc -l)

if [ "$IP_COUNT" -gt 1 ]; then
    echo "检测到多个 IP：$IPS，开始清理..."
    # 跳过第一个（主 IP），删除剩下的
    FIRST=1
    for IP in $IPS; do
        if [ $FIRST -eq 1 ]; then
            FIRST=0
            echo "保留主 IP: $IP"
        else
            echo "删除次要 IP: $IP"
            ip addr del "$IP/24" dev eth0 || true
        fi
    done
else
    echo "IP 状态正常，无残留。"
fi

# 6. 最终验证输出（这些输出会回传到主控日志里）
echo "================ 验证信息 ================"
echo "=== dhcp backend ==="; NetworkManager --print-config | grep -i dhcp
echo "=== client-id ==="; nmcli -f ipv4.dhcp-client-id connection show "Wired connection 1"
echo "=== IP ==="; ip -4 addr show eth0 | grep inet
echo "=== 路由 ==="; ip route
echo "=== dhclient 进程 ==="; ps aux | grep dhclient | grep -v grep
echo "=========================================="
echo "脚本执行完毕。"
```

以下脚本废弃

```bash
#!/bin/bash
set -e

CONF="/etc/NetworkManager/conf.d/10-use-dhclient.conf"
CURRENT_DHCP=$(NetworkManager --print-config 2>/dev/null | grep -E "^dhcp=" | head -1)
NEED_RESTART=0

echo "开始检查并配置 dhclient..."

# 0. 自动探测网卡名称 (根据默认路由)
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
# 如果没获取到（比如刚断网），通过 nmcli 找第一个连上的设备
if [ -z "$INTERFACE" ]; then
    INTERFACE=$(nmcli -t -f DEVICE,STATE device | grep ':connected' | cut -d: -f1 | head -n1)
fi
# 自动探测连接名称 (根据网卡名称找对应的连接)
CONNECTION=$(nmcli -t -f NAME,DEVICE connection show --active | grep ":$INTERFACE$" | cut -d: -f1 | head -n1)

echo "自动探测结果：网卡名=$INTERFACE, 连接名=$CONNECTION"

# 1. 检查并安装依赖
if ! dpkg -l 2>/dev/null | grep -q "^ii.*isc-dhcp-client"; then
    echo "未安装 isc-dhcp-client，开始安装..."
    apt update
    apt install -y isc-dhcp-client
else
    echo "isc-dhcp-client 已安装，跳过。"
fi

# 2. 检查并写入配置文件
mkdir -p /etc/NetworkManager/conf.d
if [ ! -f "$CONF" ] || ! grep -q "^dhcp=dhclient" "$CONF"; then
    echo "写入配置 $CONF..."
    cat > "$CONF" << 'EOF'
[main]
dhcp=dhclient
EOF
    NEED_RESTART=1
else
    echo "配置文件已存在且正确，跳过。"
fi

# 3. 检查运行状态
if [ "$CURRENT_DHCP" != "dhcp=dhclient" ]; then
    echo "当前运行状态不是 dhclient，准备重启 NetworkManager..."
    NEED_RESTART=1
fi

# 4. 按需重启 NetworkManager
if [ "$NEED_RESTART" = "1" ]; then
    echo "正在重启 NetworkManager，网络会短暂断开（主控会自动重连并回传结果）..."
    systemctl restart NetworkManager
    echo "NetworkManager 重启完成。"
    sleep 3 # 等待网络重新拉起
    
    # 重启后重新探测一下名称（以防连网后重新分配了名字）
    INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
    CONNECTION=$(nmcli -t -f NAME,DEVICE connection show --active | grep ":$INTERFACE$" | cut -d: -f1 | head -n1)
else
    echo "已经是 dhclient 模式且运行正常，无需重启 NetworkManager。"
fi

# 5. 自动清理 secondary IP 残留
if [ -n "$INTERFACE" ]; then
    echo "检查并清理多余的次要 IP 残留..."
    IPS=$(ip -4 addr show "$INTERFACE" | grep inet | awk '{print $2}' | cut -d/ -f1)
    IP_COUNT=$(echo "$IPS" | wc -w)

    if [ "$IP_COUNT" -gt 1 ]; then
        echo "检测到多个 IP：$IPS，开始清理..."
        FIRST=1
        for IP in $IPS; do
            if [ $FIRST -eq 1 ]; then
                FIRST=0
                echo "保留主 IP: $IP"
            else
                echo "删除次要 IP: $IP"
                ip addr del "$IP/24" dev "$INTERFACE" || true
            fi
        done
    else
        echo "IP 状态正常，无残留。"
    fi
else
    echo "警告：未能探测到活动网卡，跳过 IP 清理。"
fi

# 6. 最终验证输出
echo "================ 验证信息 ================"
echo "=== dhcp backend ==="; NetworkManager --print-config | grep -i dhcp
if [ -n "$CONNECTION" ]; then
    echo "=== client-id ==="; nmcli -f ipv4.dhcp-client-id connection show "$CONNECTION"
else
    echo "=== client-id === 未知（未找到活动连接）"
fi
if [ -n "$INTERFACE" ]; then
    echo "=== IP ==="; ip -4 addr show "$INTERFACE" | grep inet
    echo "=== dhclient 进程 ==="; ps aux | grep dhclient | grep -v grep
fi
echo "=== 路由 ==="; ip route
echo "=========================================="
echo "脚本执行完毕。"
```

### viki-sntp-once
`更新-261022` \| `发布-261022`

- 现象：冷启动后要等一会才同步正确的网络时间
- 方案：先大致同步下，再精确同步时间
- 适用：viki

```bash
#!/bin/bash

# ==========================================
# 开发板开机快速时间同步 (sntp-once) 自动配置脚本
# ==========================================

# 1. 检查是否为 root 权限
if [ "$EUID" -ne 0 ]; then
  echo "❌ 错误：请使用 root 权限运行此脚本 (sudo ./setup.sh)"
  exit 1
fi

echo "⏳ 开始配置 sntp-once 服务..."

# 2. 前置检查：chrony 冲突检测
if systemctl is-active --quiet chrony || systemctl is-active --quiet chronyd; then
  echo "❌ 错误：检测到 chrony 或 chronyd 正在运行！"
  echo "请先禁用 chrony (systemctl disable --now chrony) 再使用本方案。"
  exit 1
fi

# 3. 前置检查：sntp 是否安装
if ! command -v sntp &> /dev/null; then
  echo "⚠️ 未检测到 sntp 命令，尝试自动安装 ntp 包..."
  apt-get update && apt-get install -y ntp
  if [ $? -ne 0 ]; then
    echo "❌ 错误：ntp 包安装失败，请检查网络或软件源。"
    exit 1
  fi
fi

# 4. 配置 NTP 服务器 (可根据你的实际网络环境修改)
# 这里默认使用文档中的 210.28.130.4 time.neu.edu.cn
NTP_SERVER_IP="210.28.130.4"
NTP_SERVER_HOST="time.neu.edu.cn"

# 5. 创建 systemd 服务文件
echo "📝 正在创建 /etc/systemd/system/sntp-once.service ..."
cat << EOF > /etc/systemd/system/sntp-once.service
[Unit]
Description=One-shot SNTP sync at boot
After=network-online.target
Wants=network-online.target
Before=ntp.service

[Service]
Type=oneshot
ExecStart=/usr/bin/sntp -S -t 10 ${NTP_SERVER_IP} ${NTP_SERVER_HOST}
Restart=on-failure
RestartSec=5
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# 6. 重载系统服务并设置开机自启
echo "🔄 重载 systemd 配置..."
systemctl daemon-reload
echo "🚀 启用 sntp-once 开机自启..."
systemctl enable sntp-once.service

# 7. 立即执行一次测试（热重启测试）
echo "⚡ 立即执行一次时间同步..."
systemctl start sntp-once.service

# 8. 检查执行结果
sleep 2
echo "=========================================="
echo "✅ 配置完成！当前服务状态如下："
systemctl status sntp-once.service --no-pager
echo "=========================================="

# 9. 打印当前系统时间
echo "🕒 当前系统时间为："
date

exit 0
```
---

### viki-install-sshpass
`更新-261022` \| `发布-261022`

用于 scp 复制文件等。

```bash
#!/bin/bash

# ==========================================
# 开发板批量安装 sshpass 脚本 (修复版)
# ==========================================

echo "=========================================="
echo "开始检查 sshpass 环境..."

# 1. 检查是否已经安装
if command -v sshpass >/dev/null 2>&1; then
    echo "✅ sshpass 已经安装，版本信息："
    sshpass -V | head -n 1
    echo "无需重复安装，脚本结束。"
    exit 0
fi

# 2. 检查系统权限并确定 sudo 命令
if [ "$EUID" -ne 0 ]; then
    echo "⚠️ 非 root 用户运行，将尝试使用 sudo..."
    SUDO="sudo"
else
    SUDO=""
fi

# 3. 随机延迟 (防止并发过高)
# sleep $((RANDOM % 10))

# 4. 开始安装
echo "⏳ 正在更新软件源 (忽略 ROS 源报错)..."
# 加上 || true 防止 ROS 源的 GPG 警告导致脚本中断
$SUDO apt-get update -qq || true

echo "⏳ 正在安装 sshpass..."
# 修复语法：将环境变量独立出来，避免 root 权限下被当成命令执行
export DEBIAN_FRONTEND=noninteractive
$SUDO apt-get install -y -qq sshpass

# 5. 验证安装结果
if command -v sshpass >/dev/null 2>&1; then
    echo "✅ 安装成功！"
    sshpass -V | head -n 1
    echo "=========================================="
    exit 0
else
    echo "❌ 安装失败！请检查开发板是否能够正常访问 apt 软件源，或者网络是否通畅。"
    echo "=========================================="
    exit 1
fi
```

### viki-cp-file
`更新-261022` \| `发布-261022`



```bash
#!/bin/bash

# ==========================================
# 自动复制 106v 目录到 /home/jetson/ 并设置归属
# ==========================================

# 1. 配置变量 (⚠️ 请务必替换为你真实的密码)
TARGET_DIR="/home/jetson/106v"
SOURCE_ADDR="jetson@172.18.145.11:/home/jetson/106v"
PASSWORD="yahboom" 

echo "=========================================="
echo "开始检测目录: $TARGET_DIR"

# 2. 检测目录是否存在
if [ -d "$TARGET_DIR" ]; then
    echo "✅ 目录 $TARGET_DIR 已存在，脚本结束。"
    exit 0
fi

# 3. 确保 sshpass 已安装
if ! command -v sshpass >/dev/null 2>&1; then
    echo "❌ 未检测到 sshpass，请先执行安装脚本。"
    exit 1
fi

# 4. 随机延迟（强烈建议保留，防止几十台板卡同时向 viki36 发起 scp 导致卡死）
sleep $((RANDOM % 10))

echo "⏳ 目录不存在，开始从 $SOURCE_ADDR 拷贝到 /home/jetson/ ..."

# 5. 执行 scp 拷贝
# 参数说明：
# -o StrictHostKeyChecking=no 和 UserKnownHostsFile=/dev/null 用于跳过首次连接的指纹确认
sshpass -p "$PASSWORD" scp -r \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$SOURCE_ADDR" "/home/jetson/"

# 6. 检查复制结果并修改归属
if [ $? -eq 0 ] && [ -d "$TARGET_DIR" ]; then
    echo "✅ 复制成功！正在修正目录归属为 jetson:jetson ..."
    
    # 判断当前执行用户，决定是否使用 sudo
    if [ "$EUID" -ne 0 ]; then
        sudo chown -R jetson:jetson "$TARGET_DIR"
    else
        chown -R jetson:jetson "$TARGET_DIR"
    fi

    # 检查 chown 是否成功
    if [ $? -eq 0 ]; then
        echo "✅ 权限修改成功！"
        ls -ld "$TARGET_DIR"
        echo "=========================================="
        exit 0
    else
        echo "⚠️ 复制成功，但修改归属失败，请检查当前执行用户是否有 sudo 权限。"
        echo "=========================================="
        exit 1
    fi
else
    echo "❌ 拷贝失败！请检查网络、密码或源路径是否正确。"
    echo "=========================================="
    exit 1
fi
```

### viki-check-conda

```bash
#!/bin/bash

# ==========================================
# 检查 jetson 用户下的 Conda 安装情况
# ==========================================

JETSON_HOME="/home/jetson"
CONDA_FOUND=0
CONDA_BASE_PATH=""

echo "=========================================="
echo "🔍 开始检查 jetson 用户的 Conda 环境..."

# 1. 扫描最常见的安装路径
for dir in "$JETSON_HOME/miniconda3" "$JETSON_HOME/anaconda3"; do
    if [ -f "$dir/bin/conda" ]; then
        CONDA_FOUND=1
        CONDA_BASE_PATH="$dir"
        break
    fi
done

# 2. 如果常规路径没找到，解析 .bashrc 寻找线索
if [ $CONDA_FOUND -eq 0 ] && [ -f "$JETSON_HOME/.bashrc" ]; then
    # 查找 conda initialize 代码块中的安装路径
    # 通常格式为: __conda_setup="$('/home/jetson/miniconda3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
    INIT_PATH=$(grep -oP '(?<=__conda_setup="\$\(\x27)[^ \x27]+(?=\x27)' "$JETSON_HOME/.bashrc" | head -n 1)
    
    if [ -n "$INIT_PATH" ] && [ -f "$INIT_PATH" ]; then
        CONDA_FOUND=1
        # 去掉尾部的 /bin/conda 得到 base 路径
        CONDA_BASE_PATH=$(dirname $(dirname "$INIT_PATH"))
    fi
fi

echo "------------------------------------------"

# 3. 输出检测结果
if [ $CONDA_FOUND -eq 1 ]; then
    echo "✅ 成功找到 jetson 用户的 Conda 安装！"
    echo "   -> 安装路径: $CONDA_BASE_PATH"
    
    # 尝试以 jetson 用户执行 conda --version (如果是 root 下发的脚本)
    if [ "$EUID" -eq 0 ]; then
        CONDA_VERSION=$(sudo -u jetson "$CONDA_BASE_PATH/bin/conda" --version 2>/dev/null)
    else
        CONDA_VERSION=$("$CONDA_BASE_PATH/bin/conda" --version 2>/dev/null)
    fi
    
    if [ -n "$CONDA_VERSION" ]; then
        echo "   -> 版本信息: $CONDA_VERSION"
    else
        echo "   -> 版本信息: 获取失败（可能权限不足或环境损坏）"
    fi
    echo "=========================================="
    exit 0
else
    echo "❌ 未能在 jetson 用户下找到 Conda。"
    echo "   (已检查: $JETSON_HOME/miniconda3, $JETSON_HOME/anaconda3, 以及 .bashrc)"
    echo "=========================================="
    exit 1
fi
```

<!-- 
261019，来自赵老师

董老师，这是我整理的用到的模型：
AI语音实验箱用到的模型：
whisper-large-v3-turbo、qwen2.5:32b、ChatTTS
自然语言处理实验箱：
qwen3-embedding:8b、qwen2.5:32b、whisper-large-v3-turbo、BAAI/bge-small-en
视觉实验箱：
后续更新。 -->

<span style="font-size:12px; color:#999">THE END</span>