# Searcher 使用文档

`Searcher` 是一个基于 Apache Lucene 9.12.3 的通用检索器，专为 RAG（检索增强生成）场景设计。它提供了统一的查询入口，支持自然语言分词查询与结构化 JSON 组合查询，并内置了元数据过滤、时间范围过滤等能力。

---

## 目录

- [快速开始](#快速开始)
- [构造器](#构造器)
- [核心 API](#核心-api)
    - [统一查询入口 `search`](#1-统一查询入口-search)
    - [自然语言查询 `searchNatural`](#2-自然语言查询-searchnatural)
    - [结构化组合查询 `searchComposite`](#3-结构化组合查询-searchcomposite)
    - [辅助方法 `getDocCount` / `close`](#4-辅助方法)
- [查询条件封装 `QueryCondition`](#查询条件封装-querycondition)
- [结果封装 `SearchResult` 与 `SearchHit`](#结果封装-searchresult-与-searchhit)
- [JSON 查询格式](#json-查询格式)
- [完整示例](#完整示例)
- [注意事项](#注意事项)

---

## 快速开始

```java
// 1. 打开索引（需与 IndexCreator 使用相同的索引路径和语言）
try (Searcher searcher = new Searcher("indexDir", "zh")) {

    // 2. 执行自然语言查询
    Searcher.SearchResult result = searcher.search("全文检索的原理", 10);

    // 3. 处理结果
    for (Searcher.SearchHit hit : result.getHits()) {
        System.out.println(hit.getChunkId() + " : " + hit.getScore());
    }
}
```

---

## 构造器

### `public Searcher(String indexPath, String language) throws IOException`

打开指定路径的 Lucene 索引，并初始化对应的语言分析器。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `indexPath` | `String` | 索引文件存放的目录路径。 |
| `language` | `String` | 索引时使用的语言代码。当前支持 `"zh"` 及中文变体（如 `"zh-cn"`、`"zh-tw"`），其他语言默认使用 `StandardAnalyzer`。**必须与创建索引时使用的分词器保持一致。** |

**示例：**
```java
Searcher searcher = new Searcher("/data/lucene_index", "zh");
```

---

## 核心 API

### 1. 统一查询入口 `search`

```java
public SearchResult search(String queryOrJson, int topN) throws IOException
```

根据输入内容自动选择查询模式：
- 若输入**不以 `{` 或 `[` 开头**，则视为自然语言文本，执行分词查询（默认搜索 `content` 和 `title` 字段）。
- 若输入**以 `{` 或 `[` 开头**，则视为 JSON 字符串，解析为组合查询条件执行。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `queryOrJson` | `String` | 普通问句文本 或 JSON 格式的查询条件。 |
| `topN` | `int` | 期望返回的最大结果条数。 |
| **返回值** | `SearchResult` | 包含命中列表和命中总数的结果对象。 |

**示例（自然语言）：**
```java
SearchResult result = searcher.search("什么是倒排索引？", 20);
```

**示例（JSON 组合查询）：**
```java
String json = """
    [
        {"type": "TEXT", "fields": ["content"], "keywords": ["RAG"], "occur": "SHOULD"},
        {"type": "FILTER", "field": "file_type", "values": ["pdf"]}
    ]
    """;
SearchResult result = searcher.search(json, 20);
```

---

### 2. 自然语言查询 `searchNatural`

```java
public SearchResult searchNatural(String queryText, List<String> defaultFields, int topN) throws IOException
```

将用户输入的完整自然语言句子进行分词，然后在指定的字段列表中以 `SHOULD`（OR）逻辑执行检索。适用于无法提前确定查询语法的终端用户。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `queryText` | `String` | 用户输入的自然语言文本。 |
| `defaultFields` | `List<String>` | 指定要搜索的字段名称列表，例如 `["content", "title"]`。 |
| `topN` | `int` | 返回结果数量。 |

**示例：**
```java
List<String> fields = Arrays.asList("content", "title", "summary");
SearchResult result = searcher.searchNatural("大语言模型的应用场景", fields, 15);
```

---

### 3. 结构化组合查询 `searchComposite`

```java
public SearchResult searchComposite(List<QueryCondition> conditions, int topN) throws IOException
```

通过编程方式构建复杂的布尔查询，支持文本匹配、元数据过滤、时间范围过滤等多种条件的任意组合。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `conditions` | `List<QueryCondition>` | 查询条件列表，每个条件定义了一种查询或过滤逻辑。 |
| `topN` | `int` | 返回结果数量。 |

**示例：**
```java
List<Searcher.QueryCondition> conditions = Arrays.asList(
    new Searcher.QueryCondition(
        Arrays.asList("content", "title"),
        Arrays.asList("RAG", "检索"),
        Searcher.QueryCondition.Occur.SHOULD
    ),
    new Searcher.QueryCondition("file_type", Arrays.asList("pdf", "docx")),
    new Searcher.QueryCondition("publish_time", 1609459200000L, 1640995200000L, Searcher.QueryCondition.Occur.FILTER)
);
SearchResult result = searcher.searchComposite(conditions, 50);
```

---

### 4. 辅助方法

| 方法 | 说明 |
| :--- | :--- |
| `public int getDocCount()` | 返回当前索引中的文档总数。 |
| `public void close()` | 关闭索引读取器和目录，释放资源。该类实现了 `Closeable`，**推荐使用 try-with-resources**。 |

---

## 查询条件封装 `QueryCondition`

`QueryCondition` 是用于构建结构化查询的核心类。通过不同的构造器，可以创建以下类型的条件：

| 构造器 | 用途 | 参数说明 |
| :--- | :--- | :--- |
| `QueryCondition(List<String> fields, List<String> keywords, Occur occur)` | **文本字段查询**。关键词会被分词，字段之间为 OR 关系。 | `fields`：字段名列表；`keywords`：关键词列表；`occur`：逻辑（MUST / SHOULD / FILTER）。 |
| `QueryCondition(String field, Long startTime, Long endTime, Occur occur)` | **时间范围过滤**。通常用于 `LongPoint` 类型的字段。 | `field`：字段名；`startTime`/`endTime`：毫秒级时间戳（可留空表示无边界）；`occur`：通常为 `FILTER`。 |
| `QueryCondition(String field, List<String> values)` | **元数据过滤**。同一字段内的多个值为 OR 关系，默认 `Occur.FILTER`。 | `field`：字段名；`values`：允许的值列表。 |
| `QueryCondition(String field, List<String> values, Occur occur)` | **元数据过滤 + 自定义 Occur**。允许调整该条件在整体查询中的逻辑。 | 同上，额外指定 `occur`。 |

### `Occur` 枚举说明

| 值 | 含义 | 对评分的影响 |
| :--- | :--- | :--- |
| `MUST` | 文档**必须**满足该条件。 | 参与 BM25 评分。 |
| `SHOULD` | 文档**应该**满足该条件，匹配则加分，不匹配也不淘汰。 | 参与 BM25 评分。 |
| `FILTER` | 文档**必须**满足该条件，但不影响评分。 | **不参与**评分，性能优于 `MUST`。 |

---

## 结果封装 `SearchResult` 与 `SearchHit`

### `SearchResult`

| 方法 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `getHits()` | `List<SearchHit>` | 获取命中结果列表（按相关性降序排列）。 |
| `getTotalHits()` | `long` | 获取满足查询条件的总命中数（可能大于 `hits.size()`）。 |

### `SearchHit`

| 方法 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `getChunkId()` | `String` | 获取该 Chunk 的唯一标识（`chunk_id` 字段的值）。 |
| `getScore()` | `float` | 获取该文档的相关性评分（BM25 得分）。 |
| `getFields()` | `Map<String, Object>` | 获取文档中所有存储字段的键值对。 |
| `getField(String name)` | `Object` | 获取指定字段的存储值。 |

---

## JSON 查询格式

当通过 `search` 方法传入 JSON 字符串时，需遵循以下格式规范：

### 整体结构
- 可以是**单个 JSON 对象**或 **JSON 数组**。
- 数组中每个元素代表一个 `QueryCondition`。

### 条件类型（`type` 字段）

#### 1. `TEXT` —— 文本字段查询

| 字段 | 类型 | 必需 | 说明 |
| :--- | :--- | :--- | :--- |
| `type` | `string` | 是 | 固定为 `"TEXT"`。 |
| `fields` | `array[string]` | 是 | 要搜索的字段名列表。 |
| `keywords` | `array[string]` | 是 | 关键词列表（会被分词）。 |
| `occur` | `string` | 否 | 逻辑，可选 `"MUST"`、`"SHOULD"`、`"FILTER"`，默认为 `"SHOULD"`。 |

**示例：**
```json
{
    "type": "TEXT",
    "fields": ["content", "title"],
    "keywords": ["大语言模型", "微调"],
    "occur": "SHOULD"
}
```

#### 2. `FILTER` —— 元数据多值过滤

| 字段 | 类型 | 必需 | 说明 |
| :--- | :--- | :--- | :--- |
| `type` | `string` | 是 | 固定为 `"FILTER"`。 |
| `field` | `string` | 是 | 元数据字段名。 |
| `values` | `array[string]` | 是 | 允许的值列表（**内部为 OR 关系**）。 |

**示例：**
```json
{
    "type": "FILTER",
    "field": "file_type",
    "values": ["pdf", "docx", "txt"]
}
```

#### 3. `RANGE` —— 时间范围过滤

| 字段 | 类型 | 必需 | 说明 |
| :--- | :--- | :--- | :--- |
| `type` | `string` | 是 | 固定为 `"RANGE"`。 |
| `field` | `string` | 是 | 数值型字段名（如 `publish_time`）。 |
| `start` | `number` | 否 | 起始时间戳（毫秒），省略表示无下限。 |
| `end` | `number` | 否 | 结束时间戳（毫秒），省略表示无上限。 |

**示例：**
```json
{
    "type": "RANGE",
    "field": "create_time",
    "start": 1672502400000,
    "end": 1704038400000
}
```

---

## 完整示例

### 示例 1：自然语言搜索（用户聊天输入）

```java
public class SearchDemo {
    public static void main(String[] args) {
        try (Searcher searcher = new Searcher("rag_index", "zh")) {
            String userQuery = "请问如何微调大语言模型？";
            Searcher.SearchResult result = searcher.search(userQuery, 5);

            System.out.println("共找到 " + result.getTotalHits() + " 条相关片段：");
            for (Searcher.SearchHit hit : result.getHits()) {
                System.out.println("- " + hit.getChunkId() + " (得分: " + hit.getScore() + ")");
                System.out.println("  内容预览: " + hit.getField("content"));
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### 示例 2：结构化 JSON 查询（API 接口接收）

```java
public class ApiSearchHandler {
    public SearchResult handleJsonQuery(String json) throws IOException {
        try (Searcher searcher = new Searcher("rag_index", "zh")) {
            return searcher.search(json, 20);
        }
    }

    public static void main(String[] args) throws IOException {
        String jsonQuery = """
            [
                {
                    "type": "TEXT",
                    "fields": ["content"],
                    "keywords": ["RAG", "检索增强"],
                    "occur": "SHOULD"
                },
                {
                    "type": "FILTER",
                    "field": "knowledge_base",
                    "values": ["技术文档", "内部Wiki"]
                },
                {
                    "type": "RANGE",
                    "field": "update_time",
                    "start": 1700000000000
                }
            ]
            """;

        ApiSearchHandler handler = new ApiSearchHandler();
        Searcher.SearchResult result = handler.handleJsonQuery(jsonQuery);

        result.getHits().forEach(System.out::println);
    }
}
```

### 示例 3：编程方式构建复杂查询

```interface
List<Searcher.QueryCondition> conditions = new ArrayList<>();

// 核心语义匹配：content 或 title 包含 "向量检索" 或 "embedding"
conditions.add(new Searcher.QueryCondition(
    Arrays.asList("content", "title"),
    Arrays.asList("向量检索", "embedding"),
    Searcher.QueryCondition.Occur.SHOULD
));

// 过滤：仅保留知识库 "product_manual"
conditions.add(new Searcher.QueryCondition("kb_name", Collections.singletonList("product_manual")));

// 过滤：文件类型为 PDF 或 Markdown
conditions.add(new Searcher.QueryCondition("file_type", Arrays.asList("pdf", "md")));

// 过滤：创建时间在 2024 年之后
conditions.add(new Searcher.QueryCondition("create_time", 1704067200000L, null, Searcher.QueryCondition.Occur.FILTER));

try (Searcher searcher = new Searcher("rag_index", "zh")) {
    Searcher.SearchResult result = searcher.searchComposite(conditions, 30);
    // 处理结果...
}
```

---

## 注意事项

1. **分词器一致性**：构造 `Searcher` 时传入的 `language` 参数必须与建立索引时 `IndexCreator` 使用的语言相同，否则可能导致查询词项无法匹配。
2. **字段名对应**：`QueryCondition` 中使用的字段名必须与索引中定义的字段名完全一致（包括大小写）。
3. **数值字段需使用 `LongPoint`**：范围过滤依赖索引时字段被添加为 `LongPoint` 类型，否则查询无效。
4. **资源释放**：`Searcher` 实现了 `Closeable`，请务必在 finally 块中或使用 try-with-resources 确保 `close()` 被调用。
5. **JSON 解析依赖**：JSON 解析功能依赖 Jackson 库，请在项目中添加对应依赖（如 `com.fasterxml.jackson.core:jackson-databind`）。
6. **默认字段**：自然语言查询默认搜索 `content` 和 `title` 字段，如果索引中字段名不同，请使用 `searchNatural` 显式指定字段列表。