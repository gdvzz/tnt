---
title: 人工智能算力平台
layout: default
parent: aicr算力平台
# nav_order: 5
---

# 人工智能算力平台
{: .no_toc }

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

<!--  -->
<details markdown="block">
  <summary>ℹ️ 更新历史</summary>
<br>

**260706**
- 更新：[转账充值全攻略](#转账充值全攻略)
</details>

关于学院算力平台的使用说明、费用查看，以及转账充值。

---

## 使用简要说明
<br>
下载链接：[算力平台使用简要说明-v1.30-221107](./aicr.assets/算力平台使用简要说明-v1.30-251107.pdf)

---

## 费用查看
<br>
L40 和 A100 费用，可在相应功能中查看。

### L40费用查看
<br>
L40 的费用，可在 `资源&任务 | 配额使用统计` 中查看。

[![L40charge](./aicr.assets/L40charge.png)](./aicr.assets/L40charge.png)

### A100费用查看
<br>
A100 的费用，可在 `计费管理 | 账单管理` 中查看。

[![A100charge](./aicr.assets/A100charge.png)](./aicr.assets/A100charge.png)

---

<!--  -->
<span id="transfer"></span>

## 转账充值全攻略
`[aka] transfer`

转账充值全攻略，请参考：[【江南大仪共享】大仪开放共享系统转账充值全攻略↗](https://mp.weixin.qq.com/s/O6HFNKmMqv9C-ygCutl_KA)

以下是简要说明，供参考。

### 0-关注微信通知
<br>
算力平台管理员，将在月初发信息给老师，关于上个月的费用。收到信息后，可进行后续步骤操作。

- ✳️ 对费用金额有疑问，可 [费用查看](#费用查看)。或联系算力平台管理员（董老师）
- ✳️ 当年度的费用，需要在当年 12月份之前完成转账。

<!--  -->
<span id="sinup"></span>

### 1-登录大仪共享平台
`[aka] sinup`

e江南  → 大仪共享（电脑端）

[![signin](./aicr.assets/aicr1t.png)](./aicr.assets/aicr1.png)

如尚未注册大仪共享平台，则要求先注册，如下所示：

[![signup](./aicr.assets/aicr2t.png)](./aicr.assets/aicr2.png)

- ✳️ 加入已有课题组的，申请账号的时候，选择对应课题组就好，由课题组负责人激活。（找到课题组中要激活的老师 → 点 “修改”按钮 → **是否激活** 选“是”→ 点击“更新”按钮）

- ✳️ 需成立新课题组的，老师注册好后（注册时，课题组先暂选 <ins>“问题课题组”</ins>），将老师的新课题组名称、姓名、工号、电话发给算力平台管理员（董老师）。将联系大仪共享平台管理员（管老师）处理。

- 课题组负责人对本课题组成员的费用负责。

### 2-生成报销单
<br>
参考以下步骤，在大仪共享平台，生成报销单。

**1、点击“报销管理”**

[![reimb](./aicr.assets/aicr3t.png)](./aicr.assets/aicr3.png)

**2、选择收费记录并生成报销单**

点击“报销项目（或课题组报销项目）” → 选择收费记录 → 点击“生成报销单”按钮 

[![reimb-gf](./aicr.assets/aicr4t.png)](./aicr.assets/aicr4.png)

**3、查看报销单，并记录单号和金额**

点击“报销单（或课题组报销单）” → 查看并记录“<ins>报销单号</ins>”和金额（“<ins>计费结果</ins>”）

[![reimb-vf](./aicr.assets/aicr5t.png)](./aicr.assets/aicr5.png)

### 3-在财务系统转账
<br>
参考以下步骤，在财务系统转账缴费。

**1、选择“网上物流报销”**

[![reimb-fin](./aicr.assets/aicr6t.png)](./aicr.assets/aicr6.png)

**2、发起“校内转账申请”**

点击“结算点转账” → 点击“付款业务” → 选择“江南大学大仪开放共享平台” → 点击“校内转账申请”按钮

[![reimb-trans](./aicr.assets/aicr7t.png)](./aicr.assets/aicr7.png)

**3、选择项目（本子）**

选择“江南大学大仪开放共享平台” → 选择项目（本子） → 点击“下一步”按钮 

[![reimb-book](./aicr.assets/aicr8t.png)](./aicr.assets/aicr8.png)

**4、输入单号和金额**

- **转账金额**：大仪平台的报销单的金额（“<ins>计费结果</ins>”）
- **交易备注**：大仪平台的报销单号 + 课题组名称

[![reimb-fee](./aicr.assets/aicr9t.png)](./aicr.assets/aicr9.png)

点击“下一步”后，出现“校内经费转账确认单”，如无误则确认。✅ DONE

<!--  -->
<!-- 

1、Nvidia L40，32张

参考资料：https://images.nvidia.cn/content/Solutions/data-center/vgpu-L40-datasheet.pdf

Nvidia L40, 90.5 TFLOPS(FP32) / 48GB

L40 算力，共：2896 TFLOPS(FP32)


2、NVIDIA A100 80GB PCIe，3张

参考资料：https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf

Nvidia A100，19.5 TFLOPS(FP32) / 80GB
Nvidia A100，312 TFLOPS(FP16) / 80GB

A100 算力，共：58.5 TFLOPS(FP32)

3、Nvidia H100 80GB，1张

参考资料：https://resources.nvidia.com/en-us-hopper-architecture/nvidia-tensor-core-gpu-datasheet?ncid=no-ncid

Nvidia H100，67 TFLOPS(FP32) / 80GB
Nvidia H100，1979 TFLOPS(FP16) / 80GB

H100 算力，共：67 TFLOPS(FP32)
 -->