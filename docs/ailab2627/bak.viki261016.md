---
title: 旅游agent+rag-261016
layout: default
parent: ailab实验课2627
# nav_order: -261016
nav_exclude: true
---

#  旅游agent+rag-261016
{: .no_toc }
`更新-261009` \| `发布-261009`

<!--  -->
<details markdown="block">
  <summary>✳️ 目录</summary>
- TOC
{:toc}
</details>

---

## 实验简介

### 背景

大语言模型（LLM）在开放域问答上表现优异，但在垂直领域存在两个突出问题：

1. **幻觉**：模型会编造门票价格、预约规则、开放时间等细节。例如问"鼓浪屿船票怎么买"，模型常回答"现场购票即可"，而实际必须提前 15 天在小程序抢票。
2. **知识陈旧**：模型训练数据有截止日期，无法覆盖最新的预约政策、学生票规则。

**检索增强生成（RAG）** 通过"先检索、后生成"缓解上述问题。但 RAG 与 Agent 的**集成方式**有多种，本实验递进实现三个版本：

- **V1 固定 RAG**：每次提问无条件检索；
- **V2 Tool-RAG**：把 RAG 封装为工具，Agent 自主调用；
- **V3 Agent-RAG + 反思**：在 V2 基础上加 Reranker、缺失追问、Self-Reflection。

### 实验目标

1. 理解 ReAct 智能体的推理循环；
2. 掌握 RAG 完整链路：切分 → 向量化 → 检索 → 注入；
3. 实现 Tool-RAG 范式，理解 function calling 协议；
4. 引入 Self-Reflection，让 Agent 对生成结果二次校验；
5. 在 **Jetson Orin NX 边缘设备**上完成全离线部署；
6. 通过 V1/V2/V3 对比实验，量化三种方案的差异。
7. 实现带 Web 界面的旅游智能体（agent）。

### 开发板
<br>
和常见的台式机很相似：

- 主机。有个小小机箱，内部是英伟达开发板（Nvidia Jetson）。
- 屏幕。支持 HDMI 接口的屏幕，都可以通过 HDMI 线连接到 Jetson 开发板。
- 鼠标和键盘。常见的鼠标和键盘，通过 USB 连接 Jetson 开发板。
- 操作系统。Ubuntu，Linux 的发行版的一种。（常见操作系统有： Windows、MacOS、Linux，等）
- 机械臂。由 Jetson 开发板控制的一个外部设备。本次实验不使用。

---

## 操作规范
<br>
敬请按照以下要求操作开发板：

- 🚫 **禁止：水杯、饮料瓶等放在桌上**。以免液体泼洒导致教具等损坏。
    
    可放在实验室四周或地上或书包中。

- 🚫 **禁止：电源线、网线等，从桌子四周穿到桌面上**。以免磕碰导致教具等跌落损坏。

    从桌子中间空洞穿到桌面上。

<!-- - 🚫 **禁止：开机状态直接拔电源断电**。以免开发板意外损坏。

    可先按关机键关机。确认关机后再拔电源断电。 -->

- ✴️ **书包等物品远离开发板**。以免磕碰导致教具等跌落损坏。<br>

    可放在实验室四周或地上。

**‼️未按操作规范使用教具导致损坏的，要照价赔偿‼️**

[🔝](#top)

---

## 实验原理

### RAG 基础链路

```
文档 → 切分 → Embedding → 向量库 → 相似度检索 → Top-K 片段 → 注入 Prompt → LLM 生成
```

本实验中各环节的实现：

| 环节 | 实现 |
|---|---|
| 切分 | `build_knowledge.py` 中 `split_text()`，按段落 + 句号切分 |
| Embedding | `core.embed()` 调 Ollama `/api/embeddings` |
| 向量库 | `chromadb.PersistentClient`（嵌入式，本地持久化） |
| 检索 | `core.retrieve()` 调 `collection.query()` |
| 生成 | `core.chat()` 调 Ollama `/api/chat` |

### 三种集成方式的差异

| 方式 | 检索时机 | 优点 | 缺点 |
|---|---|---|---|
| V1 固定 RAG | 每轮必检索 | 实现简单，稳定性高 | 闲聊也检索，浪费算力；Prompt 冗长 |
| V2 Tool-RAG | Agent 自主判断 | 节省算力；更接近工业实践 | 依赖模型判断能力 |
| V3 Agent-RAG | V2 + 反思 | 进一步降低遗漏 | 复杂度高，耗时增加 |

### ReAct 循环

ReAct（Reasoning + Acting）的核心是把 LLM 输出结构化：

```
Thought → Action → Observation → Thought → ... → Final Answer
```

LLM 通过文本化思考，**自主决定是否调用工具、调用哪个工具、传什么参数**。

### Function Calling 协议

本实验使用 Ollama 原生支持的 function calling：

**请求体**：
```json
{
  "model": "qwen2.5:3b",
  "messages": [],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_travel_knowledge",
        "description": "检索本地旅游知识库...",
        "parameters": {
          "type": "object",
          "properties": {"query": {"type": "string"}},
          "required": ["query"]
        }
      }
    }
  ]
}
```

**响应体**：
```json
{
  "message": {
    "role": "assistant",
    "content": "",
    "tool_calls": [
      {
        "function": {
          "name": "search_travel_knowledge",
          "arguments": {"query": "无锡灵山大佛学生票"}
        }
      }
    ]
  }
}
```

### Self-Reflection

生成初版行程后，用独立 LLM 调用审核 5 项：

1. 时间冲突：同一天路线是否可行
2. 学生优惠：涉及学生票的景点是否提示带学生证
3. 预约提醒：需要预约的景点是否提醒
4. 避坑提示：是否包含当地注意事项
5. 开放时间：景点时间是否与行程匹配

若发现问题，把问题反馈给主 LLM 修正，最多循环 2 次。

---

## V1/V2/V3 对比实验

‼️ **以下为样例文本，仅供参考** ‼️

### 实验设计

选 10 个测试问题，覆盖 5 类场景：

| 类别 | 问题示例 |
|---|---|
| A 闲聊 | "你好"、"谢谢" |
| B 事实查询 | "灵山大佛学生票多少钱"、"鼓浪屿船票怎么抢" |
| C 行程规划 | "学生党无锡 2 日游，预算 800" |
| D 缺城市规划 | "帮我规划 3 天行程" |
| E 知识库外 | "无锡到上海高铁多久" |

评估维度：幻觉率、检索准确率、工具调用准确率、追问正确率、响应时间。

### 结果数据

**幻觉率对比**：

| 问题类别 | V1 幻觉率 | V2 幻觉率 | V3 幻觉率 |
|---|---|---|---|
| A 闲聊 | 0% | 0% | 0% |
| B 事实查询 | 10% | 5% | 0% |
| C 行程规划 | 20% | 10% | 0% |
| D 缺城市 | 30% | 20% | 0%（追问） |
| E 知识库外 | 40% | 30% | 20% |

**综合指标对比**：

| 指标 | V1 | V2 | V3 |
|---|---|---|---|
| 平均响应时间（Jetson 3B） | 4s | 12s | 22s |
| 闲聊时无关检索占比 | 100% | 0% | 0% |
| 行程遗漏率 | 40% | 30% | 5% |
| 追问准确率 | — | — | 90% |

---

## 样例简介

‼️ **以下为样例，仅供参考** ‼️

### 项目结构

```md
tar1016/
├── requirements.txt      # Python 依赖清单
│
├── core.py               # 底层封装：Ollama API + Chroma 检索
├── tools.py              # 工具定义：天气/景点/美食/住宿/RAG 检索等
├── build_knowledge.py    # 向量库构建
│
├── v1_fixed_rag.py       # V1 固定 RAG：每次提问无条件检索
├── v2_tool_rag.py        # V2 Tool-RAG：Agent 通过自主调用 RAG
├── v3_agent_rag.py       # V3 Agent-RAG：V2 的增强版
│
├── app_chainlit.py       # Chainlit Web 界面：V1/V2/V3 切换、对话交互
├── chainlit.md           # Chainlit 欢迎页 Markdown（显示在聊天开头）
│
└── knowledge/            # RAG 知识库源文件（纯文本，中文攻略）
    ├── wuxi.txt          # 无锡攻略
    ├── xiamen.txt        # 厦门攻略
    ├── hangzhou.txt      # 杭州攻略
    └── xi_an.txt         # 西安攻略
```

### 样例源码

<!--  -->
<details markdown="block">
  <summary>requirements.txt</summary>

```md
numpy>=1.23,<2.0
requests>=2.28
chromadb>=0.4.22
chainlit>=2.0
pydantic==2.10.1
sniffio>=1.3
```
</details>

<!--  -->
<details markdown="block">
  <summary>core.py</summary>

```python
# core.py
"""
Jetson 原生封装：Ollama /api/embeddings + /api/chat + Chroma。
不用 LangChain，全部手写。
v3.8: num_predict 从 1024 降到 512，加快响应。
"""
import json
import requests
import chromadb

OLLAMA_URL = "http://localhost:11434"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "travel_kb"


def embed(text: str, model: str = "nomic-embed-text") -> list:
    """调用 Ollama 生成嵌入向量。"""
    r = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": model, "prompt": text},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def chat(messages: list, model: str = "qwen2.5:3b",
         tools: list = None, temperature: float = 0.1,
         timeout: int = 300) -> dict:
    """调用 Ollama 对话接口（含 function calling）。"""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": temperature,
        "options": {"num_predict": 512},
    }
    if tools:
        payload["tools"] = tools
    r = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]


_client = None


def get_collection():
    """惰性创建 Chroma collection。"""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client.get_or_create_collection(name=COLLECTION_NAME)


def retrieve(query: str, k: int = 3, city: str = None) -> list:
    """
    检索 Top-K 相关文档。
    city：可选，按城市元数据过滤（传入拼音，如 'wuxi'）。
    """
    coll = get_collection()
    q_emb = embed(query)

    kwargs = {"query_embeddings": [q_emb], "n_results": k}
    if city:
        kwargs["where"] = {"city": city}

    results = coll.query(**kwargs)

    docs = []
    n = len(results["documents"][0]) if results["documents"] else 0
    for i in range(n):
        docs.append({
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
        })
    return docs
```
</details>

<!--  -->
<details markdown="block">
  <summary>tools.py</summary>

```python
# tools.py
"""
工具定义：普通函数 + 手写 function calling schema。
v3.7: search_travel_knowledge 支持 city 参数，按城市过滤。
"""
import json
from core import retrieve

# 中文城市名 → 拼音（与 build_knowledge.py 存的 metadata 一致）
CITY_PINYIN = {
    "无锡": "wuxi",
    "厦门": "xiamen",
    "杭州": "hangzhou",
    "西安": "xi_an",
}


# ==================== 工具实现 ====================
def get_weather(city: str, date: str = "today") -> dict:
    mock = {
        "无锡": {"condition": "多云转晴，18-26℃，东南风3级", "tip": "适合户外，早晚加薄外套"},
        "厦门": {"condition": "多云，24-30℃，偶有微风", "tip": "海边注意补水，随身带折叠伞"},
        "杭州": {"condition": "晴，22-28℃", "tip": "带防晒、薄外套"},
        "西安": {"condition": "阴天，16-22℃", "tip": "早晚偏凉加衣"},
    }
    info = mock.get(city, {"condition": "暂无数据", "tip": "出行前自行核实"})
    return {"city": city, "date": date, **info}


def get_top_attractions(city: str) -> dict:
    attr = {
        "无锡": ["鼋头渚", "灵山大佛", "拈花湾", "惠山古镇", "无锡博物院", "南长街"],
        "厦门": ["鼓浪屿", "沙坡尾", "南普陀寺", "环岛路", "厦门大学"],
        "杭州": ["西湖环湖", "灵隐寺飞来峰", "龙井村", "九溪烟树", "河坊街"],
        "西安": ["秦始皇兵马俑", "陕西历史博物馆", "大唐不夜城", "回民街", "洒金桥"],
    }
    return {"city": city, "attractions": attr.get(city, ["暂无数据"])}


def get_food_recommend(city: str) -> dict:
    food = {
        "无锡": ["无锡小笼包", "酱排骨", "开洋馄饨", "玉兰饼", "太湖三白"],
        "厦门": ["沙茶面", "海蛎煎", "土笋冻", "花生汤", "八市海肠捞饭"],
        "杭州": ["片儿川", "葱包烩", "东坡肉", "西湖醋鱼", "定胜糕"],
        "西安": ["腊汁肉夹馍", "牛羊肉泡馍", "甑糕", "肉丸胡辣汤", "麻酱凉皮"],
    }
    return {"city": city, "foods": food.get(city, ["暂无数据"])}


def get_hotel_suggest(city: str, budget: str = "中等") -> dict:
    tips = {
        "无锡": "推荐三阳广场/清名桥地铁站周边",
        "厦门": "首选思明区中山路附近，出门即小吃街",
        "杭州": "推荐凤起路/定安路地铁口附近",
        "西安": "推荐钟楼/南门附近，地铁便利",
    }
    return {
        "city": city, "budget": budget,
        "suggest": f"建议选地铁口或景区附近；{budget}档位优先连锁酒店或学生友好民宿，节假日提前预订。{tips.get(city, '')}",
    }


def search_travel_knowledge(query: str, city: str = None) -> dict:
    """
    【RAG工具】检索本地旅游知识库。
    city：必填，用于按城市过滤（避免跨城市召回）。
    """
    city_pinyin = CITY_PINYIN.get(city) if city else None
    docs = retrieve(query, k=3, city=city_pinyin)
    return {
        "rag_query": query,
        "city": city,
        "filtered_by": city_pinyin,
        "retrieved": [d["content"] for d in docs] if docs else [],
        "note": "知识库中未找到相关信息" if not docs else None,
    }


TOOL_REGISTRY = {
    "get_weather": get_weather,
    "get_top_attractions": get_top_attractions,
    "get_food_recommend": get_food_recommend,
    "get_hotel_suggest": get_hotel_suggest,
    "search_travel_knowledge": search_travel_knowledge,
}


# ==================== Function Calling Schema ====================
def _schema(name: str, desc: str, properties: dict, required: list) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


TOOLS_SCHEMA = [
    _schema("get_weather", "查询城市指定日期的天气与出行提示。",
            {"city": {"type": "string"}, "date": {"type": "string"}}, ["city"]),
    _schema("get_top_attractions", "查询城市热门景点列表。",
            {"city": {"type": "string"}}, ["city"]),
    _schema("get_food_recommend", "查询城市特色美食推荐。",
            {"city": {"type": "string"}}, ["city"]),
    _schema("get_hotel_suggest", "按预算给住宿建议。",
            {"city": {"type": "string"}, "budget": {"type": "string"}}, ["city"]),
    _schema("search_travel_knowledge",
            "【RAG工具·必须调用】检索本地旅游知识库，获取门票价格、预约方式、开放时间、学生优惠、避坑贴士。"
            "**务必传入 city 参数限定城市，否则会检索到其他城市的信息**。",
            {
                "query": {"type": "string", "description": "自然语言关键词，如'灵山大佛学生票'"},
                "city": {"type": "string", "description": "城市名，如'无锡'，必须传入"},
            },
            ["query", "city"]),
]


def execute_tool(name: str, args: dict) -> str:
    fn = TOOL_REGISTRY.get(name)
    if fn is None:
        return json.dumps({"error": f"未知工具 {name}"}, ensure_ascii=False)
    try:
        result = fn(**args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"工具执行失败：{e}"}, ensure_ascii=False)
```
</details>

<!--  -->
<details markdown="block">
  <summary>build_knowledge.py</summary>

```python
# build_knowledge.py
"""
构建向量库。优化版：
- 清空前提示旧数据统计
- 显示进度百分比
- 汇总每城市结果
- 支持 --force 跳过确认
"""
import os
import sys
from core import embed, get_collection

KNOWLEDGE_FOLDER = "./knowledge"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50


def split_text(text: str, size: int, overlap: int) -> list:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        if len(p) <= size:
            chunks.append(p)
        else:
            sentences = p.replace("。", "。\n").split("\n")
            buf = ""
            for s in sentences:
                if len(buf) + len(s) <= size:
                    buf += s
                else:
                    if buf:
                        chunks.append(buf.strip())
                    buf = s
            if buf:
                chunks.append(buf.strip())
    overlapped = []
    for i, c in enumerate(chunks):
        if i > 0:
            tail = chunks[i - 1][-overlap:] if len(chunks[i - 1]) > overlap else chunks[i - 1]
            overlapped.append(tail + c)
        else:
            overlapped.append(c)
    return overlapped


def inspect_existing(coll) -> dict:
    """统计现有向量库的内容分布。"""
    existing = coll.get()
    if not existing["ids"]:
        return {"total": 0, "cities": {}}

    cities = {}
    for meta in existing["metadatas"]:
        city = (meta or {}).get("city", "unknown")
        cities[city] = cities.get(city, 0) + 1

    return {"total": len(existing["ids"]), "cities": cities}


def clear_collection(coll, force: bool = False) -> None:
    """清空向量库，带提示和确认。"""
    info = inspect_existing(coll)

    if info["total"] == 0:
        print("📦 向量库当前为空，无需清空")
        return

    # 提示旧数据
    print(f"📦 检测到向量库已有数据：共 {info['total']} 个 chunk")
    for city, cnt in sorted(info["cities"].items()):
        print(f"     · {city}: {cnt} 个")

    # 确认
    if not force:
        answer = input("⚠️  是否清空并重建？(y/N) ").strip().lower()
        if answer not in ("y", "yes"):
            print("❌ 已取消")
            sys.exit(0)

    # 清空
    existing = coll.get()
    coll.delete(ids=existing["ids"])
    print("🗑️  旧数据已清空\n")


def build(force: bool = False):
    print("=" * 55)
    print("  构建旅游知识库向量库")
    print("=" * 55)

    coll = get_collection()

    # ---------- 清空（带提示）----------
    clear_collection(coll, force=force)

    # ---------- 加载知识库文件 ----------
    files = [f for f in sorted(os.listdir(KNOWLEDGE_FOLDER)) if f.endswith(".txt")]
    if not files:
        print(f"❌ {KNOWLEDGE_FOLDER} 目录下没有 .txt 文件")
        sys.exit(1)

    print(f"📚 待处理知识库：{len(files)} 个文件")
    for f in files:
        print(f"     · {f}")
    print()

    # ---------- 逐个城市处理 ----------
    total = 0
    summary = []
    all_chunks = []  # (city, idx, chunk)

    # 先切分全部，方便算总进度
    for fname in files:
        city = fname.replace(".txt", "")
        path = os.path.join(KNOWLEDGE_FOLDER, fname)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks = split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        all_chunks.append((city, fname, chunks))
        summary.append((city, len(chunks)))

    grand_total = sum(n for _, _, chunks in all_chunks for n in [len(chunks)])
    print(f"✂️  共切分 {grand_total} 个 chunk，开始向量化...\n")

    # 向量化 + 入库
    for city, fname, chunks in all_chunks:
        print(f"[{city}] {len(chunks)} 个 chunk")
        for i, chunk in enumerate(chunks):
            emb = embed(chunk)
            doc_id = f"{city}_{i}"
            coll.add(
                documents=[chunk],
                embeddings=[emb],
                ids=[doc_id],
                metadatas=[{"city": city, "source": fname, "chunk_idx": i}],
            )
            total += 1
            # 全局进度
            pct = total / grand_total * 100
            bar_len = 30
            filled = int(bar_len * total / grand_total)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"     [{bar}] {total}/{grand_total} ({pct:.1f}%)", end="\r")
        print(f"     [{('█' * bar_len)}] {total}/{grand_total} (100.0%)  ✅ {city} 完成")

    # ---------- 汇总 ----------
    print()
    print("=" * 55)
    print("  ✅ 向量库构建完成")
    print("=" * 55)
    for city, cnt in summary:
        print(f"  · {city:<12} {cnt:>3} 个 chunk")
    print(f"  {'-' * 30}")
    print(f"  · {'合计':<12} {total:>3} 个 chunk")
    print(f"\n  存储位置：chroma_db/")
    print("=" * 55)


if __name__ == "__main__":
    force = "--force" in sys.argv or "-f" in sys.argv
    build(force=force)
```
</details>

<!--  -->
<details markdown="block">
  <summary>v1_fixed_rag.py</summary>

```python
# v1_fixed_rag.py
"""
V1 固定 RAG：每次提问都无条件检索，直接注入 Prompt。
"""

from core import retrieve, chat

SYSTEM_PROMPT = """你是一个旅游助手。根据提供的知识库片段回答用户问题。
如果知识库没有相关信息，如实告知，不要编造。
回答要具体、可执行，包含价格、时间、避坑提示。"""


def ask(query: str, verbose: bool = False) -> str:
    docs = retrieve(query, k=3)
    context = "\n\n".join(f"[片段{i+1}] {d['content']}" for i, d in enumerate(docs))

    if verbose:
        print(f"\n[V1 检索到 {len(docs)} 条片段]")

    prompt = f"""知识库片段：
{context}

用户问题：{query}

请基于以上片段回答。"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    resp = chat(messages, temperature=0.3)
    return resp["content"]


if __name__ == "__main__":
    print("=" * 55)
    print("  V1 固定 RAG｜Jetson Orin NX｜覆盖：无锡/厦门/杭州/西安")
    print("=" * 55)
    while True:
        q = input("\n你：").strip()
        if q.lower() == "q":
            break
        if not q:
            continue
        print(f"\n🤖 V1：{ask(q, verbose=True)}")

```
</details>

<!--  -->
<details markdown="block">
  <summary>v2_tool_rag.py</summary>

```python
# v2_tool_rag.py
"""
V2 Tool-RAG：RAG 封装成工具，Agent 通过 function calling 自主判断何时调用。
"""
import json
from core import chat
from tools import TOOLS_SCHEMA, execute_tool

LLM_MODEL = "qwen2.5:3b"
MAX_HISTORY = 6
MAX_TOOL_ROUNDS = 5

SYSTEM_PROMPT = """你是一个专业的学生旅游规划智能体，采用 ReAct 模式工作。

工具使用规则：
1. 涉及景点门票、预约方式、学生优惠、开放时间、避坑提醒时，必须调用 search_travel_knowledge。
2. 规划行程前，先调用 get_top_attractions 拿到景点清单，再针对关键景点调用 RAG 检索细节。
3. 天气、美食、住宿按需调用对应工具。
4. 最多连续调用 5 轮工具，信息足够后直接输出完整方案。
5. 最终输出结构化按天行程，含：每日路线、用餐建议、住宿参考、学生提示、避坑提醒。
6. 回答要简洁。同一信息只说一次，不要重复。不要复述工具返回的原文，用自己的话整合。
7. 只回答用户问的内容。用户没问的信息不要主动展开，除非与问题直接相关。"""


class V2ToolRAGAgent:
    def __init__(self):
        self.history = []

    def _truncate(self):
        if len(self.history) > MAX_HISTORY * 2:
            self.history = self.history[-MAX_HISTORY * 2:]

    def run(self, query: str, verbose: bool = False) -> str:
        self._truncate()
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.history)
        messages.append({"role": "user", "content": query})

        for r in range(MAX_TOOL_ROUNDS):
            try:
                resp = chat(messages, model=LLM_MODEL, tools=TOOLS_SCHEMA, temperature=0.1)
            except Exception as e:
                return f"⚠️ 模型调用失败：{e}"

            tool_calls = resp.get("tool_calls") or []
            if not tool_calls:
                final = resp.get("content", "")
                self.history.append({"role": "user", "content": query})
                self.history.append({"role": "assistant", "content": final})
                return final

            messages.append(resp)
            for tc in tool_calls:
                fn_info = tc.get("function", {})
                name = fn_info.get("name")
                args = fn_info.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}

                if verbose:
                    print(f"  [V2 调用工具] {name}({args})")

                result = execute_tool(name, args)
                messages.append({"role": "tool", "content": result})

        try:
            return chat(messages, model=LLM_MODEL, temperature=0.1).get("content", "")
        except Exception as e:
            return f"⚠️ 达到最大轮次：{e}"


if __name__ == "__main__":
    agent = V2ToolRAGAgent()
    print("=" * 55)
    print("  V2 Tool-RAG｜Jetson Orin NX｜覆盖：无锡/厦门/杭州/西安")
    print("=" * 55)
    while True:
        q = input("\n你：").strip()
        if q.lower() == "q":
            break
        if not q:
            continue
        print(f"\n🤖 V2：{agent.run(q, verbose=True)}")
```
</details>

<!--  -->
<details markdown="block">
  <summary>v3_agent_rag.py</summary>

```python
# v3_agent_rag.py
"""
V3 Agent-RAG  v3.8
优化：
  1. Rerank 改关键词匹配（无 LLM 调用）
  2. RAG 会话级缓存
  3. Reflection 增量修正
  4. RAG 强制按 city 过滤
  5. SYSTEM_PROMPT 明确按天分节
  6. core.py num_predict 降到 512（加快响应）
"""
import json
import re
import time
from core import retrieve, chat
from tools import TOOLS_SCHEMA, execute_tool, TOOL_REGISTRY, CITY_PINYIN

LLM_MODEL = "qwen2.5:3b"
MAX_HISTORY = 6
MAX_TOOL_ROUNDS = 5
MAX_REFLECTION_ROUNDS = 3

KNOWN_CITIES = ["无锡", "厦门", "杭州", "西安"]


# ============================================================
#  输出工具
# ============================================================
def _fmt_ms(ms: float) -> str:
    return f"{ms/1000:.2f}s" if ms >= 1000 else f"{ms:.0f}ms"


def emit(icon: str, name: str, ms: float, note: str = "", level: int = 0):
    indent = "  " * level
    line = f"{indent}{icon} {name:<22} {_fmt_ms(ms):>8}"
    if note:
        line += f"   {note}"
    print(line, flush=True)


def hr(width: int = 64):
    print("─" * width, flush=True)


# ============================================================
#  Prompt
# ============================================================
SYSTEM_PROMPT = """你是一个专业的学生旅游规划智能体。

【硬约束】
- 景点名称、门票价格、开放时间、预约方式，**必须严格来自用户消息中提供的【知识库真实信息】**。
- **绝对禁止编造景点名**。不确定存在的景点不要写。
- **只能规划用户指定城市的景点**，不要提其他城市。

工具使用规则：
1. 涉及景点门票、预约、学生优惠、开放时间时，必须调用 search_travel_knowledge。
2. **调用 search_travel_knowledge 时必须传入 city 参数**（如 city='无锡'）。
3. 规划行程前，先调用 get_top_attractions 拿景点清单。
4. 天气、美食、住宿按需调用。
5. 最多 5 轮工具调用。

**输出格式（必须严格遵守，按天分节）**：

### 第一天
- 【路线】具体景点顺序 + 交通方式
- 【用餐】早/午/晚推荐
- 【住宿】区域建议
- 【学生提示 & 避坑】学生优惠、预约提醒、注意事项

### 第二天
- 【路线】...
- 【用餐】...
- 【住宿】...
- 【学生提示 & 避坑】...

（以此类推，共 N 天）

**规则**：
- 每天 4 项必须齐全（路线/用餐/住宿/学生提示）
- 必须是具体的景点名，不要笼统描述
- 同一信息只说一次，不要重复
- 回答简洁，不要客套话
"""

SLOT_PROMPT = """从用户查询中提取以下槽位，只输出 JSON：
{{"city": "城市名或 null", "days": 天数或 null, "budget": "预算或 null"}}

用户查询：{query}
只输出 JSON。"""

REFLECTION_PROMPT = """检查以下行程是否存在**明确的具体问题**。严格输出 JSON。

用户需求：{user_query}
行程草案：
{draft}

只检查以下 3 类硬性问题：
1. 景点不存在或明显编造
2. 同一天景点跨城
3. 关键信息缺失（如没提学生票或预约）

符合则输出 {{"has_issue": false, "issues": []}}
否则输出 {{"has_issue": true, "issues": [{{"type": "类型", "detail": "描述"}}]}}

只输出 JSON。"""

FIX_PROMPT = """根据审核意见，**只输出需要补充的条目**（不重写整个行程）。

【当前行程】
{draft}

【审核意见】
{issues_text}

【要求】
- 每条以 "- " 开头，简洁
- 最多 5 条
- 不要重复行程中已有的内容
- 只输出条目，不要其他解释
"""


# ============================================================
#  Rerank：关键词匹配
# ============================================================
def _keyword_rerank(query: str, docs: list, top_k: int = 3) -> list:
    """关键词命中数重排，O(n)，毫秒级"""
    keywords = set(re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]+', query))
    if not keywords:
        return docs[:top_k]
    scored = []
    for i, d in enumerate(docs):
        content = d.get("content", "")
        hits = sum(1 for kw in keywords if kw in content)
        scored.append((i, hits))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return [docs[i] for i, _ in scored[:top_k]]


def rag_retrieve(query: str, city: str = None) -> dict:
    """向量检索（按 city 过滤）+ 关键词重排"""
    city_pinyin = CITY_PINYIN.get(city) if city else None
    docs = retrieve(query, k=4, city=city_pinyin)
    if not docs:
        return {"rag_query": query, "city": city, "retrieved": [], "note": "未找到"}
    top_docs = _keyword_rerank(query, docs, top_k=3)
    return {
        "rag_query": query,
        "city": city,
        "retrieved": [d["content"] for d in top_docs],
    }


# ============================================================
#  Agent
# ============================================================
class V3AgentRAG:
    def __init__(self, enable_reflection: bool = True, enable_ask: bool = True):
        self.history = []
        self.context = {"city": None, "days": None, "budget": None}
        self.enable_reflection = enable_reflection
        self.enable_ask = enable_ask

        self._rag_cache = {}

        TOOL_REGISTRY["search_travel_knowledge"] = (
            lambda q, city=None: self._cached_rag(q, city=city)
        )

    def _cached_rag(self, query: str, city: str = None) -> dict:
        key = f"{city or ''}|{query.strip()}"
        if key in self._rag_cache:
            return self._rag_cache[key]
        result = rag_retrieve(query, city=city)
        self._rag_cache[key] = result
        return result

    def _extract_slots(self, query: str) -> dict:
        t0 = time.perf_counter()

        detected_city = None
        for city in KNOWN_CITIES:
            if city in query:
                detected_city = city
                break

        days, budget = None, None
        try:
            resp = chat(
                [{"role": "user", "content": SLOT_PROMPT.format(query=query)}],
                model=LLM_MODEL, temperature=0.0,
            )
            raw = str(resp.get("content", "")).strip()

            m = re.search(r'"days"\s*:\s*"?(\d+)"?', raw)
            if m:
                days = int(m.group(1))

            m = re.search(r'"budget"\s*:\s*"?([^",}\s]+)"?', raw)
            if m and m.group(1).lower() not in ("null", "none"):
                budget = m.group(1)

            if not detected_city:
                m = re.search(r'"city"\s*:\s*"([^"]+)"', raw)
                if m and m.group(1).lower() not in ("null", "none"):
                    for c in KNOWN_CITIES:
                        if c in m.group(1):
                            detected_city = c
                            break
        except Exception as ex:
            print(f"  ⚠️  slots 解析异常：{type(ex).__name__}: {ex}")

        emit("📝", "槽位提取", (time.perf_counter() - t0) * 1000,
             f"city={detected_city}  days={days}  budget={budget}")
        return {"city": detected_city, "days": days, "budget": budget}

    def _should_ask_city(self, query: str) -> bool:
        if not self.enable_ask:
            return False
        planning_kw = ["规划", "行程", "安排", "路线", "日游", "旅游", "玩"]
        if not any(k in query for k in planning_kw):
            return False
        return self.context["city"] is None

    def _truncate(self):
        if len(self.history) > MAX_HISTORY * 2:
            self.history = self.history[-MAX_HISTORY * 2:]

    def _react(self, query: str, city: str = None, extra_context: str = None) -> str:
        t_start = time.perf_counter()

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.history)

        if extra_context:
            user_content = f"""【知识库真实信息 —— 必须严格使用，不得编造景点名称】
{extra_context}

【用户需求】
{query}"""
        else:
            user_content = query
        messages.append({"role": "user", "content": user_content})

        n_llm = 0
        n_tool = 0

        for rnd in range(MAX_TOOL_ROUNDS):
            try:
                resp = chat(messages, model=LLM_MODEL, tools=TOOLS_SCHEMA, temperature=0.1)
                n_llm += 1
            except Exception as e:
                emit("🤖", "ReAct 循环", (time.perf_counter() - t_start) * 1000,
                     f"LLM 异常：{e}")
                return f"⚠️ 模型调用失败：{e}"

            tool_calls = resp.get("tool_calls") or []
            if not tool_calls:
                emit("🤖", "ReAct 循环", (time.perf_counter() - t_start) * 1000,
                     f"{n_llm} 轮 LLM  ·  {n_tool} 次工具")
                return resp.get("content", "")

            messages.append(resp)
            for tc in tool_calls:
                fn_info = tc.get("function", {})
                name = fn_info.get("name")
                args = fn_info.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}

                if name == "search_travel_knowledge" and city and not args.get("city"):
                    args["city"] = city

                t0 = time.perf_counter()
                result = execute_tool(name, args)
                t_tool = (time.perf_counter() - t0) * 1000
                n_tool += 1
                city_note = f"  city={args.get('city')}" if name == "search_travel_knowledge" else ""
                print(f"     ├─ {name:<28} {_fmt_ms(t_tool):>8}{city_note}", flush=True)
                messages.append({"role": "tool", "content": result})

        try:
            resp = chat(messages, model=LLM_MODEL, temperature=0.1)
            emit("🤖", "ReAct 循环", (time.perf_counter() - t_start) * 1000,
                 f"{n_llm} 轮 LLM  ·  {n_tool} 次工具  ⚠️ 达上限")
            return resp.get("content", "")
        except Exception as e:
            emit("🤖", "ReAct 循环", (time.perf_counter() - t_start) * 1000,
                 f"达上限且生成失败")
            return f"⚠️ 达到最大轮次：{e}"

    def _reflect(self, query: str, draft: str) -> dict:
        try:
            resp = chat(
                [{"role": "user", "content": REFLECTION_PROMPT.format(user_query=query, draft=draft)}],
                model=LLM_MODEL, temperature=0.0,
            )
            text = str(resp.get("content", "")).strip()

            s, e = text.find("{"), text.rfind("}")
            if s != -1 and e != -1:
                try:
                    data = json.loads(text[s:e + 1])
                    if isinstance(data, dict) and "has_issue" in data:
                        return data
                except json.JSONDecodeError:
                    pass

            if re.search(r'"has_issue"\s*:\s*true', text):
                return {"has_issue": True, "issues": [{"type": "一般问题", "detail": "见草案"}]}
        except Exception as ex:
            print(f"  ⚠️  reflect 异常：{type(ex).__name__}: {ex}")
        return {"has_issue": False, "issues": []}

    def run(self, query: str, verbose: bool = False) -> str:
        t_run = time.perf_counter()
        self._truncate()

        print()
        hr()
        print(f"🎫 你：{query}")
        hr()

        # 1. slots
        slots = self._extract_slots(query)
        if slots.get("city"):
            self.context["city"] = slots["city"]
        if slots.get("days"):
            self.context["days"] = slots["days"]
        if slots.get("budget"):
            self.context["budget"] = slots["budget"]

        # 2. 追问
        if self._should_ask_city(query):
            emit("❓", "追问城市", (time.perf_counter() - t_run) * 1000)
            hr()
            return "请问您想去哪个城市呢？（目前知识库覆盖：无锡、厦门、杭州、西安）"

        # 3. 前置检索
        t_pre = time.perf_counter()
        planning_kw = ["规划", "行程", "安排", "路线", "日游", "旅游", "玩"]
        is_planning = any(k in query for k in planning_kw)
        extra_context = None

        if is_planning and self.context["city"]:
            city = self.context["city"]

            attr_result = execute_tool("get_top_attractions", {"city": city})

            prefetch_query = f"{city} 门票 预约 学生优惠 开放时间 避坑"
            rag_result = self._cached_rag(prefetch_query, city=city)
            retrieved = rag_result.get("retrieved", [])

            extra_context = (f"【{city}热门景点列表】\n{attr_result}\n\n"
                             f"【{city}详细知识】\n" + "\n\n".join(retrieved))
            emit("🔍", "前置检索", (time.perf_counter() - t_pre) * 1000,
                 f"city={city}  景点清单 + {len(retrieved)} 条知识")

        # 4. ReAct
        draft = self._react(query, city=self.context["city"], extra_context=extra_context)

        # 5. Reflection（增量修正）
        t_refl = time.perf_counter()
        n_fix = 0
        if self.enable_reflection:
            for i in range(MAX_REFLECTION_ROUNDS):
                result = self._reflect(query, draft)
                has_issue = result.get("has_issue") and result.get("issues")

                if not has_issue:
                    emit("🪞", "自检反思", (time.perf_counter() - t_refl) * 1000,
                         f"{i} 次修正  ·  通过")
                    break

                issues_text = "\n".join(
                    f"- [{it.get('type')}] {it.get('detail')}" for it in result["issues"]
                )
                try:
                    resp = chat(
                        [{"role": "user", "content": FIX_PROMPT.format(draft=draft, issues_text=issues_text)}],
                        model=LLM_MODEL, temperature=0.1,
                    )
                    fix_text = str(resp.get("content", "")).strip()
                    draft = draft + f"\n\n### 补充说明（根据自检）\n{fix_text}"
                    n_fix += 1
                except Exception:
                    break
            else:
                emit("🪞", "自检反思", (time.perf_counter() - t_refl) * 1000,
                     f"{n_fix} 次修正  ·  达上限")

        # 6. 收尾
        self.history.append({"role": "user", "content": query})
        self.history.append({"role": "assistant", "content": draft})

        hr()
        emit("⏱️", "总耗时", (time.perf_counter() - t_run) * 1000,
             f"RAG 缓存 {len(self._rag_cache)} 条")
        hr()
        return draft


# ============================================================
#  CLI
# ============================================================
if __name__ == "__main__":
    agent = V3AgentRAG()
    print("=" * 64)
    print("  V3 Agent-RAG（rerank 关键词 · 缓存 · 增量反思 · city 过滤）")
    print("=" * 64)
    while True:
        q = input("\n你：").strip()
        if q.lower() == "q":
            break
        if not q:
            continue
        ans = agent.run(q, verbose=True)
        print(f"\n🤖 V3：{ans}")

```
</details>

<!--  -->
<details markdown="block">
  <summary>app_chainlit.py</summary>

```python
# app_chainlit.py
"""
Chainlit Web 界面，Jetson 上运行。
版本切换用 Action 按钮（Chainlit 2.x 兼容）。
启动：chainlit run app_chainlit.py --host 0.0.0.0 --port 8000
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chainlit as cl


def _make_agent(version_key: str):
    """version_key: 'V1' / 'V2' / 'V3'"""
    if version_key == "V1":
        import v1_fixed_rag
        return v1_fixed_rag
    elif version_key == "V2":
        from v2_tool_rag import V2ToolRAGAgent
        return V2ToolRAGAgent()
    else:
        from v3_agent_rag import V3AgentRAG
        return V3AgentRAG()


def _version_label(key: str) -> str:
    return {
        "V1": "V1 固定 RAG（每次无脑检索）",
        "V2": "V2 Tool-RAG（Agent 自主调用）",
        "V3": "V3 Agent-RAG（重排序+追问+自检）",
    }.get(key, key)


async def _show_version_picker():
    """显示三个版本切换按钮"""
    actions = [
        cl.Action(name="switch_v1", value="V1", label="V1 固定 RAG", description="每次无脑检索"),
        cl.Action(name="switch_v2", value="V2", label="V2 Tool-RAG", description="Agent 自主调用"),
        cl.Action(name="switch_v3", value="V3", label="V3 Agent-RAG", description="重排序+追问+自检"),
    ]
    await cl.Message(
        content="**请选择要运行的版本**（点击下方按钮切换）：",
        actions=actions,
    ).send()


@cl.on_chat_start
async def on_chat_start():
    # 默认 V2
    cl.user_session.set("version", "V2")
    cl.user_session.set("agent", _make_agent("V2"))

    await cl.Message(
        content=f"""🧳 **旅游智能体已就绪**（当前版本：{_version_label('V2')}）

运行平台：**NVIDIA Jetson Orin NX 16GB / JetPack 5.1.3**

知识库覆盖：**无锡、厦门、杭州、西安**

试试这样问：
- 学生党无锡 2 日游，预算 800
- 鼓浪屿船票怎么抢？学生票多少钱？
- 灵隐寺飞来峰学生票多少？
- 陕西历史博物馆怎么约？

⏱️ 提示：Jetson 上 3B 模型响应约 30-50 秒，请耐心等待。"""
    ).send()

    await _show_version_picker()


# ---------- 三个版本切换回调 ----------
@cl.action_callback("switch_v1")
async def on_switch_v1(action: cl.Action):
    cl.user_session.set("version", "V1")
    cl.user_session.set("agent", _make_agent("V1"))
    await cl.Message(content=f"✅ 已切换到 **{_version_label('V1')}**").send()


@cl.action_callback("switch_v2")
async def on_switch_v2(action: cl.Action):
    cl.user_session.set("version", "V2")
    cl.user_session.set("agent", _make_agent("V2"))
    await cl.Message(content=f"✅ 已切换到 **{_version_label('V2')}**").send()


@cl.action_callback("switch_v3")
async def on_switch_v3(action: cl.Action):
    cl.user_session.set("version", "V3")
    cl.user_session.set("agent", _make_agent("V3"))
    await cl.Message(content=f"✅ 已切换到 **{_version_label('V3')}**").send()


# ---------- 处理用户消息 ----------
@cl.on_message
async def on_message(message: cl.Message):
    agent = cl.user_session.get("agent")
    version_key = cl.user_session.get("version", "V2")
    query = message.content.strip()

    # 支持 /v1 /v2 /v3 文本切换
    if query.lower() in ("/v1", "/v2", "/v3"):
        key = query[1:].upper()
        cl.user_session.set("version", key)
        cl.user_session.set("agent", _make_agent(key))
        await cl.Message(content=f"✅ 已切换到 **{_version_label(key)}**").send()
        return

    # 欢迎语
    if query in ("你好", "hi", "hello", "帮助", "/help"):
        await cl.Message(
            content=f"""当前版本：**{_version_label(version_key)}**

切换版本：点击上方按钮，或输入 `/v1` `/v2` `/v3`

推荐问题：
- 学生党无锡 2 日游，预算 800
- 无锡灵山大佛学生票多少？
- 帮我规划 3 天行程"""
        ).send()
        return

    # 正常处理
    msg = cl.Message(content="")
    await msg.send()
    msg.content = f"⏳ **{_version_label(version_key)}** 正在处理，请稍候（约 30-50 秒）..."
    await msg.update()

    try:
        if version_key == "V1":
            answer = agent.ask(query)
        elif version_key == "V2":
            answer = agent.run(query)
        else:
            answer = agent.run(query)
    except Exception as e:
        import traceback
        answer = f"⚠️ 出错：{type(e).__name__}: {e}\n\n```\n{traceback.format_exc()}\n```"

    msg.content = answer
    await msg.update()

```
</details>

<!--  -->
<details markdown="block">
  <summary>chainlit.md</summary>

```md
# 🧳 旅游智能体 · Jetson Orin NX

基于 **ReAct + RAG** 的学生旅游规划智能体，覆盖**无锡、厦门、杭州、西安**四城。

## 三个版本

- **V1 固定 RAG**：每次提问无条件检索
- **V2 Tool-RAG**：RAG 封装成工具，Agent 自主调用
- **V3 Agent-RAG**：V2 + 重排序 + 缺失追问 + Self-Reflection

## 试试这样问

- `学生党无锡 2 日游，预算 800`
- `鼓浪屿船票怎么抢？学生票多少钱？`
- `灵隐寺飞来峰学生票多少？`
- `陕西历史博物馆怎么约？`
```
</details>

<!--  -->
<details markdown="block">
  <summary>hangzhou.txt</summary>

```md
【西湖】
门票：全天免费开放。三潭印月需上岛船票55元（含往返）。苏堤、白堤、断桥均免费。
开放时间：全天。
建议：傍晚断桥人很多，建议早上7-9点环湖骑行更舒服。西湖周边共享单车很多，但景区部分区域禁止电动车。
交通：地铁1号线龙翔桥站、定安路站均近西湖。节假日停车位紧张，优先地铁出行。
雷峰塔：门票40元，学生20元。登塔可俯瞰西湖全景。
特色：西湖十景（苏堤春晓、断桥残雪、雷峰夕照等），世界文化遗产。

【灵隐寺·飞来峰】
门票：先购飞来峰入园票45元（学生22.5元，凭证件半价），进入飞来峰景区后，灵隐寺境内需另购香花券30元。灵隐寺全年免门票。
预约：自2025年12月1日起，灵隐飞来峰景区（含灵隐寺）实行提前7天实名预约、分时游览制度，需在"杭州灵隐飞来峰"小程序预约。
开放时间：飞来峰景区常规开放；建议早上8点前到避开旅行团。
地址：西湖区灵隐路法云弄1号。
交通：地铁3号线黄龙洞站或东岳站下车，换乘公交1314路或7路直达灵隐寺站。
游玩路线：入口检票→飞来峰石刻佛像→永福禅寺（人少清静）→灵隐寺本殿→五百罗汉堂→冷泉→法云古村。
避坑：不要在外面高价买香，寺内免费发放。节假日交通管制，不建议自驾。可只逛飞来峰+永福寺+龙井村+九溪，省下灵隐寺香花券。

【龙井村·九溪烟树】
门票：龙井村不需要门票；九溪烟树免费。
徒步路线：九溪烟树→龙井村徒步线，全程约2.5小时。
避坑：不要在路边茶摊高价买茶，可只逛不买。

【河坊街·高银街】
河坊街：小吃偏商业化，不建议在主街正餐。
高银街：紧邻河坊街，更适合吃饭，本地餐厅集中。

【杭州美食】
片儿川：老溜面馆、阿奇面馆等本地面馆仅14-20元，量大料足。奎元馆、楼外楼等老字号建议下午2-4点错峰用餐。
葱包烩、定胜糕、桂花糕：3-5元，街头小吃。
新白鹿（游泳馆店）：人均43元，糖醋里脊和蛋黄鸡翅必点。
戒坛寺巷二十年麻辣烫店：两人吃饱不超过60元。
东坡肉、西湖醋鱼、龙井虾仁：经典杭帮菜，老字号有售。

【杭州避坑与贴士】
灵隐寺学生票22.5元（原价45），岳庙学生票12.5元，省下的钱可以买杯龙井。
住宿选凤起路/定安路地铁口附近，交通方便。
西湖周边共享单车多，但景区部分区域禁停电动车。
节假日灵隐寺有交通管制，自驾停车困难，建议地铁+公交。
河坊街主街偏商业化，旁边高银街更适合吃饭。
不要在路边茶摊高价买龙井茶。
```
</details>

<!--  -->
<details markdown="block">
  <summary>wuxi.txt</summary>

```md
【无锡博物院】
门票：免费开放，已取消实名预约制，可直接到馆。
开放时间：周二至周日9:00-17:00（16:00停止入场），周一闭馆（法定节假日除外）。
地址：梁溪区钟书路100号，地铁1号线清名桥站。
建议游览：2-3小时。
特色：国家一级博物馆，镇馆之宝包括元代青花瓷、春秋吴王僚剑等。

【鼋头渚风景区】
门票：成人现场90元，线上提前购85元（含园内接驳车、太湖仙岛游船）。全日制学生、60-69岁老人凭证半价45元；70岁以上、1.4米以下儿童、军人、残疾人免票。
开放时间：常规8:00-17:30（16:30停止入园）；冬季8:30-17:00；3-4月樱花季延长并设夜樱时段（17:00-21:00，成人票90元，优惠票45元）。太湖仙岛返程末班船16:50。
樱花季：3月中至4月中，需在"无锡太湖鼋头渚"公众号提前预约，建议早上7点前入园。
交通：无锡站乘1路/乐游1号线直达充山大门；地铁2号线梅园开原寺站、4号线夏家边站换乘。
避坑：拒绝场外低价非官方票和收费野导；樱花季/节假日8点后停车位紧张。

【灵山大佛（灵山胜境）】
门票：成人现场210元，线上提前1天订195元；学生票105元，需全日制本科及以下学生凭学生证。
免票：70周岁以上老人、1.4米以下儿童。
预约方式：微信"灵山胜境官方商城"实名预约。
开放时间：07:30-17:30（17:00停止入场）。
地址：滨湖区马山灵山路1号。
特色：88米青铜立佛，灵山梵宫、九龙灌浴表演。

【拈花湾禅意小镇】
门票：成人现场120元，线上提前购99元；夜场票（16:00后入园）约80元；全日制学生半价。
开放时间：旺季（4-10月）9:00-21:30。
地址：滨湖区马山环山西路68号，紧邻灵山大佛。
福利：入住景区内酒店/客栈套餐大多含双人门票+双早，可多次进出。灵山大佛+拈花湾可一日联游，两地相距约5公里。

【惠山古镇·寄畅园】
门票：古镇大部分区域免费；文物古迹区+锡惠名胜区联票70元（含寄畅园、天下第二泉），线上提前1天65元，联票2日有效。
预约：微信公众号"惠山古镇"实名预约。

【无锡美食】
无锡小笼包：推荐熙盛源（南禅寺店/健康路店），皮薄汁多、甜而不腻。
酱排骨：三凤桥肉庄（中山路总店），百年老字号，酥烂脱骨。
开洋馄饨：熙盛源招牌，配小笼包是经典组合。
玉兰饼：毛华美食、穆桂英美食（南长街店），现炸外脆内糯。
太湖三白：白鱼、白虾、银鱼，清蒸最鲜。
梅花糕：南长街/南禅寺附近，不用专程排队。

【无锡避坑与贴士】
无锡菜偏甜，北方游客需有心理准备，点菜时可要求少糖。
南长街河边网红店本地人绕行，推荐穆桂英美食、熙盛源等老字号，人均30-50元。
惠山古镇"青稞馍""银丝面"多为营销，不必排队。
学生党务必带学生证，灵山、拈花湾、鼋头渚均有半价优惠。
地铁1号线连接火车站、三阳广场、清名桥等核心区域。
```
</details>

<!--  -->
<details markdown="block">
  <summary>xi_an.txt</summary>

```md
【秦始皇兵马俑（秦始皇帝陵博物院）】
门票：成人票120元，全日制学生半价60元；65岁以上老人、16岁及以下未成年人、现役军人、消防员、残疾人免费（免票人群也需提前预约）。
预约：需提前7天在"秦始皇帝陵博物院"公众号预约。景区全程无现场售票。
开放时间：平日8:30-17:00（闭园19:00）；国庆7:30-20:00（停止检票18:00）；暑期（7月11日-8月21日）开始检票8:00，停止检票17:30，闭馆19:30。
地址：西安市临潼区代王街道秦俑路1号。
交通：距市区较远，地铁+打车约1.5小时。
避坑：不要相信路边"低价一日游"。建议请官方讲解或提前看资料。
特色：世界第八大奇迹，含一号坑、二号坑、三号坑、铜车马展厅。

【陕西历史博物馆】
门票：免费，但必须提前预约。实行提前5天放票制度，每天17:00放票（秦汉馆17:30放票），约满即止，非常难抢。特展需额外购票（含基础馆参观资格）。所有参观者包含小朋友都需要实名预约。
预约：官方唯一渠道为"陕西历史博物馆"微信公众号。建议提前填写并保存参观计划，在放票时间点击预约。仅提交参观计划单并非完成预约。
开放时间：周一闭馆（法定节假日除外）。
避坑：名额极紧张，一放票就约。抢不到免费票可以预约特展票（含基础馆参观资格）。
特色：镇馆之宝包括镶金兽首玛瑙杯、皇后之玺、鎏金舞马衔杯银壶。

【大唐不夜城】
门票：免费。
开放时间：晚上灯光好看；表演有固定时间，可提前查。
提示：人非常多，注意财物。
特色：不倒翁小姐姐、盛唐密盒、花车巡游等互动表演。

【回民街·洒金桥】
回民街：主街较贵，旁边洒金桥更地道。肉夹馍推荐腊汁口味。
避坑：主街（北院门）上的"网红店"慎入，价格虚高、味道一般。不要相信门口拉客的。

【西安美食】
腊汁肉夹馍：推荐子午路张记肉夹馍（小寨店）或秦豫肉夹馍。
牛羊肉泡馍：推荐果渊斋米家泡馍馆或老刘家泡馍。馍要自己掰成黄豆大小，这是灵魂。
甑糕：洒金桥附近，早餐好选择。
肉丸胡辣汤：本地人早餐标配。
麻酱凉皮：西安经典小吃。
洒金桥早餐：油茶麻花+腊牛肉夹馍约18元。
测绘西路午餐：油泼面约15元。
东木头市晚餐：胡辣汤+油条约12元。
学生党人均30元/天可以吃遍本地人私藏美食街。

【西安避坑与贴士】
避开钟楼、大雁塔周边的网红泡馍/肉夹馍店，价格高口味参差，认准本地人常去的老店。
回民街主街只逛不买，去洒金桥吃正餐。
春秋早晚温差大，带薄外套。
兵马俑建议请官方讲解或提前看资料，否则看不懂。
陕西历史博物馆周一闭馆，行程安排要避开。
```
</details>

<!--  -->
<details markdown="block">
  <summary>xiamen.txt</summary>

```md
【鼓浪屿】
门票：无大门票，上岛唯一门票为轮渡船票，普通客船35元/人（往返），精品船班50元/80元。核心景点联票（日光岩、菽庄花园、皓月园、风琴博物馆、毓园）约100元，学生、老人凭证半价。
预约：唯一官方入口「屿见厦门」小程序。自2026年2月1日起，预售周期从提前10天延长至提前15天，每日9:00放出第15日船票，系统开放时间07:00-23:00。现场不设任何售票窗口，无临时票可买。
码头选择：绝大多数游客从邮轮中心厦鼓码头（东渡）出发，抵达三丘田码头（下船即核心区，步行数分钟到龙头路）；喜欢安静或票源紧张时，可选内厝澳码头（人少易中签）。带娃家庭首选三丘田，学生/情侣可捡漏内厝澳。
票价档次：35元硬座（无玻璃窗挡风，甲板不开放，预算有限学生党首选）；60元软座（密闭船舱有玻璃窗，可上甲板观景，带老人小孩家庭推荐）；100元软座（更宽敞船舶）；158元环岛+上岛（含环岛游体验，首次来厦推荐）。
抢票技巧：提前在「屿见厦门」小程序"我的-乘船人管理"中录入所有同行人身份证信息，抢票时直接勾选提交，可节省约15秒。错峰选12:00-15:00下午时段，竞争压力明显降低。
返程规则：船票为往返联票，去程票已包含返程，凭同一张船票在登岛之日起20天内均可乘坐返程航班，无需额外购票。
避坑：不要相信码头"50元快速上岛"的转卖黄牛，均为骗局。不要在任何第三方平台（OTA、闲鱼、路边摊）购买船票。岛上全程步行，穿平底鞋。联票出园后不能重新进入。

【厦门大学·南普陀寺】
厦门大学：需提前在"厦门大学"公众号预约，免费，名额有限。芙蓉隧道、芙蓉湖、上弦场是经典打卡点。
南普陀寺：免费，香可现场领；素饼可当伴手礼。与厦大相邻，可一并游览。

【沙坡尾·环岛路】
沙坡尾：免费，适合傍晚拍照；附近很多创意小店；注意避开正午暴晒。
环岛路：租自行车沿海骑行很合适；注意防晒；曾厝垵餐饮溢价较高，建议只逛不在此正餐。

【厦门美食】
沙茶面：去四里、大中这种老字号，汤头更浓；不要选景区连锁店。第一次吃建议选豆腐+鱿鱼，汤底最入味。
海蛎煎：一定要选现点现煎的，预制品口感差很多。
土笋冻：厦门经典小吃，八市附近的老店最正宗。
花生汤：沙坡尾古早甜品店有售，配油条是经典吃法。
八市（第八市场）：海肠捞饭（28元/份）、巴掌大鲅鱼水饺、烤海肠是本地人带外地朋友必吃的三大招牌，人均40元吃到撑。
中山路小吃：老思西鸡蛋汉堡、豪香里脊肉串、局口拌面配海鲜汤、1980烧肉粽，人均50元吃到撑。
桥底麻辣烫（成功大道）：学生党友好，油炸花生酱是灵魂，人均20元。

【厦门避坑与贴士】
住宿首选思明区中山路附近，出门就是小吃街，日均花费约300元/人（不含住宿）。
鼓浪屿只逛免费景点（如日光岩收费50元，可根据预算决定是否进入）。
厦门夏天多阵雨，随身带折叠伞。
沙茶面自选配料，内脏和海鲜各有拥趸，不习惯内脏可选豆腐+鱿鱼。
曾厝垵餐饮溢价高，建议只拍照不吃饭。
```
</details>


<!--  -->
<!-- <details markdown="block">
  <summary>zip包</summary>

[tar1016.zip](./viki261016.assets/tar1016.zip)

</details> -->

<!-- ```md
1、体现v1v2v3
2、输出完整代码
3、输出完整文档
4、厦门、杭州、西安，旅游信息要和无锡一样丰富
5、web界面采用Chainlit
6、不用langChain
7、用于jetson开发板上实现
8、用于jetson开发板上实现。jtop信息：NVidia Orin NX Developer KIt - Jetpack 5.1.3 [L4T 35.5.0]
9、实验报告用md格式写
``` -->

---

## 生成代码

### 方式1、大模型辅助生成

可使用某个大模型，辅助生成旅游 agent + rag 代码。此处从略。

### 方式2、复制样例代码

**1、创建实验目录**

```bash
mkdir ~/tar1016
```

**2、复制代码到相应文件**

参考 [样例简介](#样例简介)，生成相应文件。

可用个人电脑上的 VSCode 访问开发板，直接编辑开发板上的文件。更多信息可参考：[VSCode指南-远程连接↗]

或者用开发板上的 VSCode，编辑开发板上的文件。如开发板上没有 VSCode，可以安装一个，更多信息可参考：[VSCode指南-Jetson安装↗]。

或者在开发板上用 vim 生成文件。更多信息可参考：[Linux指南-vim文本编辑↗]。

或者先 ssh 到开发板，再用 vim 生成文件。更多信息可参考：[MobaXterm指南-ssh登录↗]。

或者在个人电脑编辑好了文件，上传到开发板上。更多信息可参考：[MobaXterm指南-传文件↗]，[Linux指南-scp远程复制文件/目录↗]。

### 方式3、下载zip包

**1、开发板上浏览器下载**

[tar1016.zip](./viki261016.assets/tar1016.zip)

**2、将下载的zip包移动到 HOME 目录**

```bash
mv ~/Downloads/tar1016.zip ~/
```

**3、解压**

```bash
unzip ~/tar1016.zip
```

解压后生成目录 `/home/jetson/tar1016`，相关样例代码在该目录中。

---

## 搭建实验环境
<br>
参考以下步骤搭建实验用虚拟环境。在虚拟环境中做实验，可和开发板上的其他项目互不影响。

**1、创建虚拟环境**

```bash
conda create -n tar1016 python=3.9
```

**2、激活虚拟环境**

```bash
conda activate tar1016
```

> 虚拟环境激活后，命令行提示符前有 `(tar1016) ` 字样，比如：`(tar1016) jetson@jetson-Yahboom:~$ `

**3、切换到实验目录**

假设实验目录是 /home/jetson/tar1016

```bash
cd ~/tar1016
```

**4、安装实验所需 Python 包**

```bash
pip3 install -r requirements.txt 
```

> （1）后续运行代码过程中，如还缺少什么包，就再安装什么包。<br>
> （2）确保安装在虚拟环境中。即应先激活虚拟环境，然后再安装。<br>
> （3）实验环境搭建一次即可。不必重复搭建。<br>
> （4）更多操作请参考：[Conda指南↗]。

---

## 连接大模型

### 方式一、连已有大模型

如果同学已使用某些大模型的 API，则可以使用已有的大模型的 sk。微调相关代码即可，此处从略。

‼️ **实验结束离开时，记得删除 sk 信息。以免信息泄漏** ‼️

### 方式二、商汤日日新

可访问 [商汤日日新↗](https://www.sensenova.cn/) 获得免费额度：5小时内，有 60000 积分的免费调用额度。

获得 sk 后，微调相关代码即可使用，此处从略。

‼️ **实验结束离开时，记得删除 sk 信息。以免信息泄漏** ‼️

### 方式三、用 ollama 运行本地大模型
<br>
如需在本地部署大模型LLM，可使用 ollama （或其他熟悉的框架）。

Ollama是一款面向大语言模型（LLM）的本地化部署与运行时管理框架，支持在个人计算设备或服务器端高效运行开源预训练模型。

其采用容器化架构实现模型的标准化封装与分发，通过动态量化技术优化内存占用，并提供与OpenAI API兼容的RESTful接口，便于集成至现有AI应用生态。

Ollama支持Llama、Qwen、DeepSeek等主流架构的模型仓库管理，具备异构计算资源调度能力，可基于CPU或GPU实现低延迟推理。

该工具广泛应用于数据隐私敏感场景的私有化部署、边缘计算环境下的离线推理及学术研究的模型微调与评测，为大规模语言模型的本地化应用提供了轻量级技术基座。

**1、是否已安装 ollama**

在开发板 **终端APP** 中运行以下命令：

```bash
ollama --version
```

**2、安装 ollama（如尚未安装）**

复制安装文件到开发板

```bash
scp -r jetson@172.18.145.90:/home/jetson/ollama-0.34.1 ~/
```

> 安装文件从实验室某个开发板 `172.18.145.90` 上复制到你的开发板上，存放在 `/home/jetson/ollama-0.34.1` 目录下。

如何安装，可借助大模型。此处从略。

**3、启动 Ollama（后台）**

```bash
ollama serve &
```

> 建议新开（再开）一个 **终端 App** 运行 ollama 后台。

**4、拉取模型**

qwen2.5:3b，负责“说人话”：

```bash
ollama pull qwen2.5:3b
```

> 也可以尝试其他大模型。

nomic-embed-text，RAG 的"翻译官"，“找资料”相关

```bash
ollama pull nomic-embed-text
```

**4、测试**

执行以下命令：

```bash
curl http://localhost:11434/api/tags
```

屏幕显示信息有 `nomic-embed-text`，则表明模型工作正常。

```
{"models":[{"name":"nomic-embed-text:latest","model":"nomic-embed-text:latest",
...
```

**ollama 常用管理**

```bash
ollama list           # 查看已下载模型
ollama pull <模型名>   # 仅下载不运行
ollama rm <模型名>     # 删除本地模型
ollama ps             # 查看正在运行的模型进程
ollama serve
```

---

## 建rag库

**1、切换到实验目录**

```bash
cd ~/tar1016
```

**2、建库**

```bash
python3 build_knowledge.py
```

---

## 调测代码

### 调测 v1

**1、切换到实验目录**

```bash
cd ~/tar1016
```

**2、运行 v1**

```bash
python3 v1_fixed_rag.py 
```

**3、和 agent 交互**

比如：

```
python3 v1_fixed_rag.py 
=======================================================
  V1 固定 RAG｜Jetson Orin NX｜覆盖：无锡/厦门/杭州/西安
=======================================================

你：你好 

[V1 检索到 0 条片段]

🤖 V1：你好，看起来你还没有提出具体的问题哦，可以向我咨询旅游相关的问题，比如景区游玩攻略、交通方式、住宿推荐等。我将尽力提供帮助。
```

**4、调测代码（略）**

### 调测 v2

**1、切换到实验目录**

```bash
cd ~/tar1016
```

**2、运行 v2**

```bash
python3 v2_tool_rag.py 
```

**3、和 agent 交互**

比如：

```
python3 v2_tool_rag.py 
=======================================================
  V2 Tool-RAG｜Jetson Orin NX｜覆盖：无锡/厦门/杭州/西安
=======================================================

你：你好 

🤖 V2：你好！我可以帮助你规划旅游行程。请告诉我你的目的地和你希望了解的信息或开始规划行程的日期。例如，你想知道无锡有哪些热门景点，或者你计划在某个日期出行，希望找到合适的住宿和餐饮建议。

你：谢谢！

🤖 V2：好的，请告诉我你的目的地和你希望了解的具体信息或行程的日期。例如，你想知道无锡有哪些热门景点，或者你计划在某个日期出行，希望找到合适的住宿和餐饮建议。

你：无锡 3 日游， 商务 人士，预算 2000
  [V2 调用工具] get_top_attractions({'city': '无锡'})
  [V2 调用工具] get_hotel_suggest({'city': '无锡', 'budget': '2000'})
  [V2 调用工具] get_food_recommend({'city': '无锡'})

🤖 V2：根据你的需求，以下是你的无锡三日游建议：

**景点游览**
- 3日游推荐：鼋头渚、灵山大佛、拈花湾、惠山古镇、无锡博物院、南长街。

**住宿建议**
- 预算2000元，建议选择地铁口或景区附近的酒店或学生友好民宿。推荐在三阳广场或清名桥地铁站附近的酒店。

**餐饮推荐**
- 无锡小笼包、酱排骨、开洋馄饨、玉兰饼、太湖三白等无锡特色美食。

此外，灵山大佛对持有学生证的游客有优惠，如果学生证有效，记得提前咨询是否可以享受优惠。在行程中，也要注意避免高峰期，这样可以享受更好的旅行体验。祝您旅途愉快！
```

**4、调测代码（略）**

### 调测 v3

**1、切换到实验目录**

```bash
cd ~/tar1016
```

**2、运行 v2**

```bash
python3 v3_agent_rag.py 
```

**3、和 agent 交互**

比如：

```
python3 v3_agent_rag.py 
================================================================
  V3 Agent-RAG（rerank 关键词 · 缓存 · 增量反思 · city 过滤）
================================================================

你：规划3天行程

────────────────────────────────────────────────────────────────
🎫 你：规划3天行程
────────────────────────────────────────────────────────────────
📝 槽位提取                      2.02s   city=None  days=3  budget=None
❓ 追问城市                      2.02s
────────────────────────────────────────────────────────────────

🤖 V3：请问您想去哪个城市呢？（目前知识库覆盖：无锡、厦门、杭州、西安）

你：无锡3日游，学生党，预算800

────────────────────────────────────────────────────────────────
🎫 你：无锡3日游，学生党，预算800
────────────────────────────────────────────────────────────────
📝 槽位提取                      2.12s   city=无锡  days=3  budget=800
🔍 前置检索                      2.67s   city=无锡  景点清单 + 0 条知识
     ├─ get_top_attractions               0ms
     ├─ get_food_recommend                0ms
     ├─ get_hotel_suggest                 0ms
     ├─ search_travel_knowledge           0ms  city=无锡
     ├─ search_travel_knowledge           0ms  city=无锡
     ├─ search_travel_knowledge           0ms  city=无锡
🤖 ReAct 循环                 55.27s   2 轮 LLM  ·  6 次工具
🪞 自检反思                     41.29s   3 次修正  ·  达上限
────────────────────────────────────────────────────────────────
⏱️ 总耗时                     101.35s   RAG 缓存 1 条
────────────────────────────────────────────────────────────────

🤖 V3：### 第一天
- 【路线】鼋头渚 → 惠山古镇 → 无锡博物院
- 【用餐】早/午尝试无锡小笼包
- 【住宿】建议选三阳广场/清名桥地铁站附近的学生友好民宿
- 【学生提示 & 避坑】
  - 无锡博物院学生票免费。
  - 早/午尝试餐厅时，可以询问是否有学生优惠。
  - 晚餐建议在南长街尝试锡帮菜。
  - 无锡博物院开放时间为 9:00 - 17:00。
  - 无锡博物院预约方式需关注官方微信公众号。

### 第二天
- 【路线】拈花湾 → 南长街
- 【用餐】尝试开洋馄饨
- 【住宿】同第一天建议
- 【学生提示 & 避坑】
  - 南长街有学生折扣的餐厅，可以尝试。
  - 晚餐建议在南长街尝试锡帮菜。
  - 惠山古镇的开放时间为 8:30 - 17:00。
  - 无锡博物院和惠山古镇的开放时间可能有时间重叠，需要关注具体开放信息。

### 第三天
- 【路线】惠山古镇 → 无锡博物院
- 【用餐】尝试无锡小笼包
- 【住宿】同第一天建议
- 【学生提示 & 避坑】
  - 无锡博物院开放时间为 9:00 - 17:00。
  - 惠山古镇开放时间为 8:30 - 17:00。
  - 南长街有学生折扣的餐厅，可以尝试。
  - 晚餐建议在南长街尝试锡帮菜。

### 补充说明（根据自检）
- [硬性问题2] 第二日行程包含两个地点（拈花湾和南长街），实际行程可能存在跨城的问题
- 第二日行程建议改为拈花湾或南长街中的一个，避免跨城
- 增加拈花湾的行程，如拈花湾 → 南长街
- 增加南长街的行程，如拈花湾 → 惠山古镇
- 第三天行程改为无锡博物院 → 惠山古镇
- 第四日行程改为南长街或无锡博物院

### 补充说明（根据自检）
- 【路线】拈花湾 → 南长街
- 【路线】拈花湾 → 惠山古镇
- 【路线】无锡博物院 → 惠山古镇
- 【路线】南长街 → 无锡博物院

你：

```

**4、调测代码（略）**


### 运行 Web 界面

**1、切换到实验目录**

```bash
cd ~/tar1016
```

**2、启动 Web 后台**

```bash
chainlit run app_chainlit.py --host 0.0.0.0 --port 8000
```

**3、浏览器访问**

在浏览器地址栏输入 `http://<开发板IP地址>:8000/`，比如：`http://172.18.145.90:8000/`，可以得到如下界面。可在 Web 界面中和 agent 交互。

![web](./viki261016.assets/web.jpg)

---

## 适配商汤模型

### 项目结构
<br>
主要文件和简短说明如下：

```
tar1016/
├── requirements.txt            # Python 依赖清单
│
├── core.py                     # 底层封装：商汤 chat + Chroma 检索，等
├── tools.py                    # 工具定义：天气/景点/美食/住宿/RAG 检索，等
├── build_knowledge.py          # 向量库构建
│
├── v1_fixed_rag.py             # V1 固定 RAG：每次提问无条件检索
├── v2_tool_rag.py              # V2 Tool-RAG：Agent 自主调用 RAG 工具
├── v3_agent_rag.py             # V3 Agent-RAG：V2 增强版
│
├── app_chainlit.py             # Chainlit Web 界面：默认 V3
├── chainlit.md                 # Chainlit 欢迎页 Markdown（首次打开显示）
│
├── knowledge/                  # RAG 知识库源文件（纯文本，中文攻略）
│   ├── wuxi.txt                # 无锡攻略
│   ├── xiamen.txt              # 厦门攻略
│   ├── hangzhou.txt            # 杭州攻略
│   └── xi_an.txt               # 西安攻略
│
├── tests/                      # 测试输入
│   └── inputs.txt              # 36 题测试用例
│
├── test_rag.py                 # 检索功能测试
├── test_retrieve.py            # 检索细节测试
└── test_ss.py                  # 商汤 API 连通性测试
```

### 获取样例代码

**1、下载 zip 包**

在开发板上运行浏览器，下载：[sntar1016.zip](./viki261016.assets/sntar1016.zip)

**2、移动 zip 包到 HOME 目录**

在开发板 **终端App** 中执行：

```bash
mv ~/Downloads/sntar1016.zip ~/
```

**3、解压 zip 包**

在开发板 **终端App** 中执行：

```bash
unzip ~/sntar1016.zip
```

解压完成后生成目录 `/home/jetson/sntar1016`，样例代码等文件在该目录中。


### 获取商汤模型的sk
<br>
可访问 [商汤日日新↗](https://www.sensenova.cn/) 获得免费额度：5小时内，有 60000 积分的免费调用额度。

获得的sk，写入 `core.py`。相关片段如下：

```python
...
# ============================================================
#  商汤（对话，联网）
# ============================================================
SENSENOVA_API_KEY = "{your key}"
SENSENOVA_BASE_URL = "https://token.sensenova.cn/v1"
SENSENOVA_MODEL = "sensenova-6.8-flash-lite"

_client_sensenova = OpenAI(
    api_key=SENSENOVA_API_KEY,
    base_url=SENSENOVA_BASE_URL,
)
...
```

### 运行 Ollama

参考 [方式三、用 ollama 运行本地大模型](#方式三、用 ollama 运行本地大模型)，运行 Ollama

只需要拉取 `nomic-embed-text`：

```bash
ollama pull nomic-embed-text
```

> 也可以尝试其他 RAG 建库方式，就不一定需要用 Ollama 运行模型。

`qwen2.5:3b` 不需要拉取，因为将被商汤模型替代。 

### 体验V3
<br>
通过以下步骤，可体验V3。

**1、进入实验目录**

```bash
cd ~/sntar1016
```

**2、激活虚拟环境（若尚未激活）**

```bash
conda activate tarag
```

**3、启动V3**

```bash
python3 v3_agent_rag.py 
```

**4、和智能体交互**
<br>
可请大模型输出一些测试用例集。或者参考如下测试用例集。

<details markdown="block">
  <summary>V3 Agent-RAG 测试用例集</summary>

```
# ================================================================
# V3 Agent-RAG 测试用例集
# ----------------------------------------------------------------
# 格式：每行一个问题；空行和 # 开头的行会被跳过
# 覆盖：闲聊 / 追问 / 事实查询 / 完整规划 / 宽召回 / 跨城 / 拒答 / 多轮 / 预算
# 知识库覆盖城市：无锡、厦门、杭州、西安
# ================================================================

# ---------- 1. 闲聊（不调工具）----------
你好
你是谁？
谢谢，再见

# ---------- 2. 缺失槽位追问 ----------
帮我规划 3 天行程
我想出去玩，有什么推荐？

# ---------- 3. 单事实查询（RAG 精确检索）----------
无锡灵山大佛学生票多少？
鼋头渚门票多少钱？
鼓浪屿船票怎么买？
陕西历史博物馆周一开门吗？
西湖需要门票吗？
灵隐寺飞来峰学生票多少？
兵马俑要提前几天预约？
拈花湾几点关门？

# ---------- 4. 完整规划（全流程）----------
学生党无锡 3 日游，预算 800
厦门 2 日游，预算 1000，喜欢海边
杭州周末 2 日游
西安 3 日游，学生党，预算 1200

# ---------- 5. 具体景点细节（宽召回 + 精排）----------
拈花湾门票多少？几点关门？
灵山大佛的开放时间和预约方式是什么？
鼋头渚樱花季要提前预约吗？
鼓浪屿船票有哪些档次？

# ---------- 6. 跨城市查询（city 自动切换）----------
厦门有什么特色美食？
杭州西湖周边有什么好吃的？
西安有哪些必去景点？
无锡小笼包哪家好吃？

# ---------- 7. 知识库外问题（应拒答，不编造）----------
无锡到上海高铁多久？
北京故宫门票多少？
如何办理护照？
今天天气怎么样？

# ---------- 8. 跨城对比 ----------
无锡和杭州哪个学生优惠更多？
厦门和西安哪个更适合学生穷游？

# ---------- 9. 多轮修改（上下文继承）----------
学生党无锡 2 日游
改成 3 天
预算加到 1000

# ---------- 10. 预算利用（主动给升级建议）----------
西安 3 日游，学生党，预算 1200
无锡 2 日游，预算 2000
```

</details>

### 体验 Web 界面
通过以下步骤，可体验 Web 界面。

**1、进入实验目录**

```bash
cd ~/sntar1016
```

**2、激活虚拟环境（若尚未激活）**

```bash
conda activate tarag
```

**3、启动 Web 后端**

```bash
chainlit run app_chainlit.py --host 0.0.0.0 --port 8000
```

**4、打开 Web 页面**

在开发板上，或者PC（个人电脑）上，打开浏览器，地址栏输入 `http://<开发板IP地址>:8000`。比如：`http://172.18.145.90:8000`。

**5、和智能体交互**

在 Web 界面上和智能体交互。此处从略。

---

## 关机断电复位离开
<br>
实验结束后，请完成以下事项，再离开实验课。

1. **关机断电**

    开发板要先关机、再断电。🚫 **严谨开机状态直接断电！**

    - 点击屏幕右上角 **电源标志** → power off → power off
    - 观察开发板的散热风扇。风扇停止后，表示已关机。
    <!--  -->
    - 桌子下面有个带开关的的立方体插座。按下开关，电源指示灯熄灭，即表明断开电源。

2. **归还实验器材，给实验室老师**

    - 喇叭麦克风
    - 借用的其他器材

3. **椅子复位**

    - 每个桌子，配套 6 个椅子。请将椅子推到桌子下面。

4. **带齐随身物品**

✅ 上述事项完成后，可离开实验室。


<!--  -->
<span style="font-size:12px; color:#999">THE END</span>

[VSCode指南-远程连接↗]: https://tnt.gdvzz.com/aikit/vscodeug.html#remote-ssh
[Linux指南-vim文本编辑↗]: https://tnt.gdvzz.com/aikit/linuxug.html#vim
[VSCode指南-Jetson安装↗]: https://tnt.gdvzz.com/aikit/vscodeug.html#jetson
[Linux指南-scp远程复制文件/目录↗]: https://tnt.gdvzz.com/aikit/linuxug.html#scp
[MobaXterm指南-传文件↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html#sftp
[MobaXterm指南-ssh登录↗]: https://tnt.gdvzz.com/aikit/mobaxtermug.html#ssh
[Conda指南↗]: https://tnt.gdvzz.com/aikit/condaug.html
<!--  -->
[Linux指南↗]: https://tnt.gdvzz.com/aikit/linuxug.html


