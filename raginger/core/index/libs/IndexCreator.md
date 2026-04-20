# IndexCreator 使用文档

`IndexCreator` 是一个通用的 Lucene 索引创建器，专为 RAG（检索增强生成）等场景设计。它采用动态字段配置的方式，支持多种字段类型与多语言分词，并提供了便捷的批量添加与资源自动管理能力。

---

## 目录

- [快速开始](#快速开始)
- [构造器](#构造器)
- [字段类型与配置](#字段类型与配置)
    - [FieldType 枚举](#fieldtype-枚举)
    - [FieldConfig 类](#fieldconfig-类)
- [核心 API](#核心-api)
    - [添加单个文档 `addDocument`](#1-添加单个文档-adddocument)
    - [批量添加文档 `addDocuments` / `addDocumentsFromMaps`](#2-批量添加文档-adddocuments--adddocumentsfrommaps)
    - [提交与资源管理 `commit` / `close`](#3-提交与资源管理-commit--close)
    - [状态查询 `getDocCount` / `getPendingDocCount`](#4-状态查询-getdoccount--getpendingdoccount)
- [完整示例](#完整示例)
    - [示例 1：使用 List<FieldConfig> 添加文档](#示例-1使用-listfieldconfig-添加文档)
    - [示例 2：使用 Map 添加文档](#示例-2使用-map-添加文档)
    - [示例 3：批量添加多个文档](#示例-3批量添加多个文档)
- [注意事项](#注意事项)

---

## 快速开始

```java
// 1. 创建索引实例（中文索引）
try (IndexCreator creator = new IndexCreator("indexDir", "zh")) {

    // 2. 构建一个文档的字段配置
    List<IndexCreator.FieldConfig> fields = Arrays.asList(
        new IndexCreator.FieldConfig("chunk_id", "doc001_chunk_1", IndexCreator.FieldType.ID, true),
        new IndexCreator.FieldConfig("title", "全文检索原理", IndexCreator.FieldType.TEXT, true),
        new IndexCreator.FieldConfig("content", "倒排索引是 Lucene 的核心...", IndexCreator.FieldType.TEXT, true),
        new IndexCreator.FieldConfig("position", 1, IndexCreator.FieldType.INT, true)
    );

    // 3. 添加到索引并提交
    creator.addDocument(fields);
    creator.commit();

    System.out.println("索引创建完成，当前文档数：" + creator.getDocCount());
}
```

---

## 构造器

### `public IndexCreator(String indexPath, String language) throws IOException`

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `indexPath` | `String` | 索引文件存放的目录路径。**如果目录不存在将自动创建；若已存在且包含旧索引，将被覆盖重建**（`OpenMode.CREATE`）。 |
| `language` | `String` | 文档主要语言代码。支持 `"zh"` 及中文变体（如 `"zh-cn"`、`"zh-tw"`），其他语言默认使用 `StandardAnalyzer`。 |

**注意：** 构造器内部已将 `IndexWriterConfig.OpenMode` 固定为 `CREATE`，这意味着**每次运行都会删除旧索引并新建**，适用于全量重建场景。

---

## 字段类型与配置

### FieldType 枚举

| 枚举值 | 对应的 Lucene 字段 | 分词 | 索引 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `ID` | `StringField` | ❌ 不分词 | ✅ 精确匹配 | 适用于 ID、编码、状态等需整体匹配的字段。 |
| `TEXT` | `TextField` | ✅ 分词 | ✅ 全文检索 | 适用于标题、正文等需全文搜索的字段。 |
| `STORED_ONLY` | `StoredField` | ❌ 不分词 | ❌ 不索引 | 仅存储原始值，不可搜索，用于展示或关联。 |
| `LONG` | `LongPoint` + `StoredField` | — | ✅ 范围查询 | 长整型数值，支持区间过滤；若需存储原始值，将额外添加 `StoredField`。 |
| `INT` | `IntPoint` + `StoredField` | — | ✅ 范围查询 | 整型数值，支持区间过滤；存储逻辑同上。 |

### FieldConfig 类

用于描述一个字段的元信息。

| 构造器参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `name` | `String` | 字段名称，需与后续 `Searcher` 中使用的字段名一致。 |
| `value` | `Object` | 字段值，根据类型传入 `String` 或 `Number`。 |
| `type` | `FieldType` | 字段类型，决定 Lucene 如何处理该字段。 |
| `store` | `boolean` | 是否将原始值存入索引，以便检索后直接获取。 |

---

## 核心 API

### 1. 添加单个文档 `addDocument`

```java
public void addDocument(List<FieldConfig> fieldConfigs) throws IOException
public void addDocument(Map<String, FieldConfig> fieldMap) throws IOException
```

两种重载形式分别支持 **列表** 和 **字典** 方式传入字段配置。

| 参数 | 类型 | 说明 |
| :--- | :--- | :--- |
| `fieldConfigs` | `List<FieldConfig>` | 字段配置列表，每个元素描述一个字段。 |
| `fieldMap` | `Map<String, FieldConfig>` | 以字段名为键、`FieldConfig` 为值的映射。 |

**示例：**
```java
// 方式一：List 形式
List<IndexCreator.FieldConfig> configs = Arrays.asList(
    new IndexCreator.FieldConfig("id", "001", IndexCreator.FieldType.ID, true),
    new IndexCreator.FieldConfig("content", "测试文本", IndexCreator.FieldType.TEXT, true)
);
creator.addDocument(configs);

// 方式二：Map 形式
Map<String, IndexCreator.FieldConfig> map = new LinkedHashMap<>();
map.put("id", new IndexCreator.FieldConfig("id", "001", IndexCreator.FieldType.ID, true));
map.put("content", new IndexCreator.FieldConfig("content", "测试文本", IndexCreator.FieldType.TEXT, true));
creator.addDocument(map);
```

---

### 2. 批量添加文档 `addDocuments` / `addDocumentsFromMaps`

```java
public void addDocuments(List<List<FieldConfig>> batchConfigs) throws IOException
public void addDocumentsFromMaps(List<Map<String, FieldConfig>> batchMaps) throws IOException
```

批量添加多个文档，内部循环调用单文档添加方法，**不自动提交**。

**示例：**
```java
List<List<IndexCreator.FieldConfig>> batch = new ArrayList<>();
batch.add(Arrays.asList(
    new IndexCreator.FieldConfig("id", "doc1", IndexCreator.FieldType.ID, true),
    new IndexCreator.FieldConfig("text", "内容A", IndexCreator.FieldType.TEXT, true)
));
batch.add(Arrays.asList(
    new IndexCreator.FieldConfig("id", "doc2", IndexCreator.FieldType.ID, true),
    new IndexCreator.FieldConfig("text", "内容B", IndexCreator.FieldType.TEXT, true)
));
creator.addDocuments(batch);
creator.commit(); // 手动提交
```

---

### 3. 提交与资源管理 `commit` / `close`

| 方法 | 说明 |
| :--- | :--- |
| `public void commit() throws IOException` | 强制将内存中尚未刷盘的索引数据写入磁盘，并生成一个新的索引段。 |
| `public void close() throws IOException` | 关闭 `IndexWriter`，释放文件锁。**实现 `Closeable`，支持 try-with-resources**，会自动调用 `commit()`。 |

**最佳实践：** 使用 try-with-resources 确保资源释放，避免索引目录死锁。

```java
try (IndexCreator creator = new IndexCreator("indexDir", "zh")) {
    // 执行添加操作
    creator.addDocument(...);
    // 如需确保数据已持久化，可显式调用 commit()，否则 close() 时也会自动提交
} // 自动调用 close()
```

---

### 4. 状态查询 `getDocCount` / `getPendingDocCount`

| 方法 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `getDocCount()` | `int` | 返回当前已提交到磁盘的文档总数（不包含未提交的文档）。 |
| `getPendingDocCount()` | `int` | 返回内存缓冲区中尚未提交的文档数量。 |

---

## 完整示例

### 示例 1：使用 List<FieldConfig> 添加文档

```java
import org.acaneko.IndexCreator;
import java.util.Arrays;
import java.util.List;

public class SimpleIndexDemo {
    public static void main(String[] args) {
        try (IndexCreator creator = new IndexCreator("rag_index", "zh")) {
            List<IndexCreator.FieldConfig> fields = Arrays.asList(
                new IndexCreator.FieldConfig("chunk_id", "chunk_001", IndexCreator.FieldType.ID, true),
                new IndexCreator.FieldConfig("doc_id", "user_manual_v1.pdf", IndexCreator.FieldType.ID, true),
                new IndexCreator.FieldConfig("title", "快速入门", IndexCreator.FieldType.TEXT, true),
                new IndexCreator.FieldConfig("content", "Lucene 是一个高性能的全文检索库。", IndexCreator.FieldType.TEXT, true),
                new IndexCreator.FieldConfig("page_number", 12, IndexCreator.FieldType.INT, true),
                new IndexCreator.FieldConfig("word_count", 1024L, IndexCreator.FieldType.LONG, true)
            );

            creator.addDocument(fields);
            creator.commit();
            System.out.println("文档已索引，总数：" + creator.getDocCount());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 示例 2：使用 Map 添加文档

```java
Map<String, IndexCreator.FieldConfig> doc = new LinkedHashMap<>();
doc.put("chunk_id", new IndexCreator.FieldConfig("chunk_id", "chunk_002", IndexCreator.FieldType.ID, true));
doc.put("content", new IndexCreator.FieldConfig("content", "倒排索引是全文检索的核心。", IndexCreator.FieldType.TEXT, true));
doc.put("create_time", new IndexCreator.FieldConfig("create_time", 1712908800000L, IndexCreator.FieldType.LONG, true));

try (IndexCreator creator = new IndexCreator("rag_index", "zh")) {
    creator.addDocument(doc);
    System.out.println("待提交文档数：" + creator.getPendingDocCount());
    creator.commit();
}
```

### 示例 3：批量添加多个文档

```java
List<Map<String, IndexCreator.FieldConfig>> batch = new ArrayList<>();

for (int i = 0; i < 100; i++) {
    Map<String, IndexCreator.FieldConfig> doc = new LinkedHashMap<>();
    doc.put("chunk_id", new IndexCreator.FieldConfig("chunk_id", "chunk_" + i, IndexCreator.FieldType.ID, true));
    doc.put("content", new IndexCreator.FieldConfig("content", "这是第 " + i + " 个片段的内容。", IndexCreator.FieldType.TEXT, true));
    batch.add(doc);
}

try (IndexCreator creator = new IndexCreator("large_index", "zh")) {
    creator.addDocumentsFromMaps(batch);
    creator.commit();
    System.out.println("批量添加完成，总文档数：" + creator.getDocCount());
}
```

---

## 注意事项

1. **索引覆盖模式**：构造器默认使用 `IndexWriterConfig.OpenMode.CREATE`，每次运行会**清空旧索引**。若需增量追加，可修改源码将 `OpenMode` 改为 `CREATE_OR_APPEND`。

2. **分词器一致性**：创建索引时选择的语言分词器，必须与后续 `Searcher` 使用的分词器保持一致，否则搜索会失败。

3. **数值字段的存储**：`LONG` 和 `INT` 类型默认会添加 `LongPoint` / `IntPoint` 用于范围查询。若需在检索结果中显示原始数值，请将 `store` 设为 `true`。

4. **字段名大小写**：字段名区分大小写，推荐统一使用小写蛇形命名（如 `chunk_id`、`create_time`）。

5. **资源释放**：务必在 finally 块中或使用 try-with-resources 关闭 `IndexCreator`，否则可能导致索引目录被锁定，下次启动抛出 `LockObtainFailedException`。

6. **内存缓冲区**：默认 RAM 缓冲区设为 64MB，可根据硬件环境调整。较大的缓冲区可减少磁盘 I/O，但会占用更多堆内存。