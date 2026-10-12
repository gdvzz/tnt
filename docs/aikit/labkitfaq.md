---
title: AI教具维护
layout: default
parent: aikit教具
# nav_order: 9001
nav_exclude: true
---

# AI教具维护
{: .no_toc }
`更新-261012` \| `发布-260326`

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<details markdown="block">
  <summary>✳️ 历史</summary>
261012<br>
  （1）增加“插网线 6 小时会断网”
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