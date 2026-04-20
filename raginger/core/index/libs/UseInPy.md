# Python 调用指南（基于 JPype）

本文档介绍如何在 Python 环境中通过 **JPype** 调用已打包好的 `IndexCreator` 和 `Searcher` 类，实现 Lucene 索引的创建与检索。

---

## 目录

- [环境准备](#环境准备)
- [启动 JVM 与导入 Java 类](#启动-jvm-与导入-java-类)
- [创建索引（IndexCreator）](#创建索引indexcreator)
    - [添加单个文档](#添加单个文档)
    - [批量添加文档](#批量添加文档)
- [执行检索（Searcher）](#执行检索searcher)
    - [自然语言查询](#自然语言查询)
    - [JSON 结构化查询](#json-结构化查询)
    - [编程式组合查询](#编程式组合查询)
- [完整示例脚本](#完整示例脚本)
- [常见问题与注意事项](#常见问题与注意事项)

---

## 环境准备

### 1. 安装 JPype

```bash
pip install jpype1
```

### 2. 准备 JAR 包

确保已将 `IndexCreator` 和 `Searcher` 及其所有依赖（Lucene、Jackson 等）打包成一个 **uber JAR**（例如 `lucene-rag-1.0.jar`），并放置在 Python 脚本可访问的路径下。

### 3. 确保 Java 运行时可用

JPype 需要本地安装 Java 11 或更高版本（推荐 Java 17）。可通过以下命令验证：

```bash
java -version
```

---

## 启动 JVM 与导入 Java 类

在使用任何 Java 类之前，必须先启动 JVM。**注意：JVM 只能启动一次**，通常放在脚本开头。

```python
import jpype
import jpype.imports

# 启动 JVM，指定 JAR 包路径
jar_path = "/path/to/lucene-rag-1.0.jar"
jpype.startJVM(classpath=[jar_path])

# 导入 Java 类
from org.acaneko import IndexCreator, Searcher
```
  
> 若需传递 JVM 参数（如内存设置），可通过 `jpype.startJVM(jvmpath=..., *args)` 添加，例如 `"-Xmx2g"`。

---

## 创建索引（IndexCreator）

### 添加单个文档

`IndexCreator` 支持通过 `FieldConfig` 列表或 `Map` 添加文档。Python 中可使用 `java.util.ArrayList` 和 `java.util.LinkedHashMap` 构建参数。

```python
# 创建 IndexCreator 实例（索引路径，语言）
creator = IndexCreator("/data/lucene_index", "zh")

# 构建字段配置列表
fields = jpype.java.util.ArrayList()
fields.add(IndexCreator.FieldConfig("chunk_id", "doc001_chunk1", IndexCreator.FieldType.ID, True))
fields.add(IndexCreator.FieldConfig("title", "全文检索入门", IndexCreator.FieldType.TEXT, True))
fields.add(IndexCreator.FieldConfig("content", "Lucene 是一个高性能的全文检索库。", IndexCreator.FieldType.TEXT, True))
fields.add(IndexCreator.FieldConfig("position", 1, IndexCreator.FieldType.INT, True))

# 添加文档并提交
creator.addDocument(fields)
creator.commit()

print(f"索引文档数：{creator.getDocCount()}")

# 关闭（释放资源）
creator.close()
```

**使用 Map 方式：**

```python
doc_map = jpype.java.util.LinkedHashMap()
doc_map.put("chunk_id", IndexCreator.FieldConfig("chunk_id", "doc002_chunk1", IndexCreator.FieldType.ID, True))
doc_map.put("content", IndexCreator.FieldConfig("content", "倒排索引是全文检索的核心。", IndexCreator.FieldType.TEXT, True))

creator.addDocument(doc_map)
```

### 批量添加文档

```python
batch = jpype.java.util.ArrayList()

for i in range(10):
    doc = jpype.java.util.LinkedHashMap()
    doc.put("chunk_id", IndexCreator.FieldConfig("chunk_id", f"chunk_{i}", IndexCreator.FieldType.ID, True))
    doc.put("content", IndexCreator.FieldConfig("content", f"这是第 {i} 个片段的内容。", IndexCreator.FieldType.TEXT, True))
    batch.add(doc)

creator.addDocumentsFromMaps(batch)
creator.commit()
```

---

## 执行检索（Searcher）

### 自然语言查询

```python
searcher = Searcher("/data/lucene_index", "zh")

# 直接传入问句，自动分词并检索
result = searcher.search("什么是倒排索引？", 10)

print(f"共找到 {result.getTotalHits()} 条结果")
for hit in result.getHits():
    print(f"ID: {hit.getChunkId()}, Score: {hit.getScore():.4f}")
    # 获取存储字段
    print(f"Content: {hit.getField('content')}")

searcher.close()
```

### JSON 结构化查询

```python
import json

query_json = """
[
    {
        "type": "TEXT",
        "fields": ["content", "title"],
        "keywords": ["RAG", "检索"],
        "occur": "SHOULD"
    },
    {
        "type": "FILTER",
        "field": "file_type",
        "values": ["pdf", "md"]
    },
    {
        "type": "RANGE",
        "field": "create_time",
        "start": 1700000000000,
        "end": 1710000000000
    }
]
"""

result = searcher.search(query_json, 20)
```

### 编程式组合查询

```python
# 构建条件列表
conditions = jpype.java.util.ArrayList()

# 文本查询
text_cond = Searcher.QueryCondition(
    jpype.java.util.Arrays.asList(["content", "title"]),
    jpype.java.util.Arrays.asList(["人工智能", "机器学习"]),
    Searcher.QueryCondition.Occur.SHOULD
)
conditions.add(text_cond)

# 元数据过滤
filter_cond = Searcher.QueryCondition(
    "knowledge_base",
    jpype.java.util.Arrays.asList(["技术文档", "内部Wiki"])
)
conditions.add(filter_cond)

# 时间范围过滤
time_cond = Searcher.QueryCondition(
    "publish_time",
    jpype.java.lang.Long(1700000000000),
    None,
    Searcher.QueryCondition.Occur.FILTER
)
conditions.add(time_cond)

result = searcher.searchComposite(conditions, 30)
```

---

## 完整示例脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import jpype
import jpype.imports

def main():
    # 1. 启动 JVM
    jar_path = "./lucene-rag-1.0.jar"
    jpype.startJVM(classpath=[jar_path])

    from org.acaneko import IndexCreator, Searcher

    # 2. 创建索引
    print("正在创建索引...")
    creator = IndexCreator("./test_index", "zh")

    batch = jpype.java.util.ArrayList()
    chunks = [
        ("chunk_0", "Lucene 是一个基于 Java 的全文检索库。"),
        ("chunk_1", "倒排索引是实现快速搜索的核心数据结构。"),
        ("chunk_2", "BM25 是 Lucene 默认的相关性评分算法。"),
    ]

    for cid, content in chunks:
        doc = jpype.java.util.LinkedHashMap()
        doc.put("chunk_id", IndexCreator.FieldConfig("chunk_id", cid, IndexCreator.FieldType.ID, True))
        doc.put("content", IndexCreator.FieldConfig("content", content, IndexCreator.FieldType.TEXT, True))
        batch.add(doc)

    creator.addDocumentsFromMaps(batch)
    creator.commit()
    print(f"索引创建完成，共 {creator.getDocCount()} 篇文档。")
    creator.close()

    # 3. 执行检索
    print("\n正在检索...")
    searcher = Searcher("./test_index", "zh")
    result = searcher.search("全文检索", 5)

    print(f"命中 {result.getTotalHits()} 条结果：")
    for hit in result.getHits():
        print(f"- ID: {hit.getChunkId()}, Score: {hit.getScore():.2f}, Content: {hit.getField('content')}")

    searcher.close()

    # 4. 关闭 JVM（可选，脚本结束时通常自动关闭）
    jpype.shutdownJVM()

if __name__ == "__main__":
    main()
```

---

## 常见问题与注意事项

### 1. JVM 启动失败
- 确保 `JAVA_HOME` 环境变量正确指向 JDK 安装目录。
- 检查 JAR 包路径是否正确，依赖是否完整。
- 若出现 `ClassNotFoundException`，说明 uber JAR 未包含所有依赖，需重新打包。

### 2. Python 与 Java 类型转换
- **Java 集合**：必须使用 `jpype.java.util.ArrayList`、`jpype.java.util.LinkedHashMap` 等显式构造，Python 原生 `list`/`dict` 无法直接传递。
- **基本类型**：`int`、`float`、`bool` 可自动转换；`long` 类型需使用 `jpype.java.lang.Long(value)` 包装，否则可能被识别为 `int` 导致方法签名不匹配。
- **枚举值**：通过 `IndexCreator.FieldType.ID`、`Searcher.QueryCondition.Occur.SHOULD` 直接访问。

### 3. 资源释放
- `IndexCreator` 和 `Searcher` 均实现了 `Closeable`，建议显式调用 `close()`，或使用 Python 的 `with` 语法（需自定义上下文管理器，或直接 `try-finally`）。
- 未正确关闭可能导致索引目录锁残留，下次启动时报 `LockObtainFailedException`。

### 4. 中文分词支持
- 构造器中的 `language` 参数必须与索引时一致。支持的语言代码：`"zh"`、`"zh-cn"`、`"zh-tw"` 等。

### 5. 路径问题
- 索引路径和 JAR 路径建议使用绝对路径，或相对于脚本执行目录的路径。

### 6. JVM 单例限制
- JPype 的 JVM 只能启动一次，若需在交互式环境（如 Jupyter）中重复测试，可先启动 JVM 再执行后续代码，避免重复调用 `startJVM`。

---

通过以上指南，你可以在 Python 中无缝调用 Java 实现的 Lucene 索引与检索功能，充分发挥 Python 的灵活性与 Lucene 的高性能。