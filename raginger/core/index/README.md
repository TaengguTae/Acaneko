# Lucene索引模块

基于Apache Lucene 9.12.3的全文检索模块，通过JPype集成Acaneko-Lucene JAR包实现。

## 功能特性

- ✅ 支持多种字段类型（ID、TEXT、LONG、INT、STORED_ONLY）
- ✅ 支持单文档和批量文档索引
- ✅ 支持自然语言查询
- ✅ 支持JSON结构化查询
- ✅ 支持组合条件查询
- ✅ 支持中文分词
- ✅ 完善的日志记录
- ✅ 资源自动管理

## 环境要求

- Python 3.8+
- Java 11+ (推荐Java 17)
- JPype1

## 安装依赖

```bash
pip install jpype1 loguru
```

## 快速开始

### 1. 基本用法

```python
from raginger.core.index.lucene_index import LuceneIndex

# 设置JAR包路径（可选，默认使用libs目录下的JAR）
LuceneIndex.set_jar_path("/path/to/Acaneko-Lucene9.12.3-v1.0.jar")

# 创建索引
with LuceneIndex("./my_index", "zh") as lucene:
    # 创建IndexCreator
    lucene.create_index_creator()
    
    # 添加文档
    documents = [
        {
            "chunk_id": {"value": "doc_001", "type": "ID"},
            "title": {"value": "全文检索入门", "type": "TEXT"},
            "content": {"value": "Lucene是一个高性能的全文检索库。", "type": "TEXT"}
        }
    ]
    
    lucene.add_documents_from_maps(documents)
    lucene.commit()

# 执行检索
with LuceneIndex("./my_index", "zh") as lucene:
    result = lucene.search("全文检索", 10)
    
    for hit in result['hits']:
        print(f"ID: {hit['chunk_id']}, Score: {hit['score']}")
```

### 2. 使用List方式添加文档

```python
with LuceneIndex("./my_index", "zh") as lucene:
    lucene.create_index_creator()
    
    fields = [
        {"name": "chunk_id", "value": "doc_001", "type": "ID"},
        {"name": "title", "value": "文档标题", "type": "TEXT"},
        {"name": "content", "value": "文档内容", "type": "TEXT"},
        {"name": "page_number", "value": 10, "type": "INT"},
        {"name": "create_time", "value": 1712908800000, "type": "LONG"}
    ]
    
    lucene.add_document(fields)
    lucene.commit()
```

## 字段类型

| 类型 | 说明 | 分词 | 索引 | 用途 |
|------|------|------|------|------|
| ID | 不分词字符串 | ❌ | ✅ 精确匹配 | 文档ID、编码等 |
| TEXT | 文本字段 | ✅ | ✅ 全文检索 | 标题、正文等 |
| STORED_ONLY | 仅存储 | ❌ | ❌ | 展示字段、关联数据 |
| LONG | 长整型 | - | ✅ 范围查询 | 时间戳、大数值 |
| INT | 整型 | - | ✅ 范围查询 | 页码、计数等 |

## 查询方式

### 1. 自然语言查询

```python
result = lucene.search("什么是全文检索？", 10)

# 或指定搜索字段
result = lucene.search_natural(
    query_text="什么是全文检索？",
    fields=["content", "title"],
    top_n=10
)
```

### 2. JSON查询

```python
json_query = """
[
    {
        "type": "TEXT",
        "fields": ["content", "title"],
        "keywords": ["Lucene", "检索"],
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

result = lucene.search(json_query, 20)
```

### 3. 组合查询

```python
conditions = [
    {
        "type": "TEXT",
        "fields": ["content", "title"],
        "keywords": ["机器学习", "深度学习"],
        "occur": "SHOULD"
    },
    {
        "type": "FILTER",
        "field": "category",
        "values": ["技术文档", "教程"]
    },
    {
        "type": "RANGE",
        "field": "publish_time",
        "start": 1704067200000,
        "occur": "FILTER"
    }
]

result = lucene.search_composite(conditions, 30)
```

## 查询条件类型

### TEXT - 文本查询

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定为"TEXT" |
| fields | array | 是 | 搜索字段列表 |
| keywords | array | 是 | 关键词列表 |
| occur | string | 否 | 逻辑：MUST/SHOULD/FILTER |

### FILTER - 元数据过滤

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定为"FILTER" |
| field | string | 是 | 字段名 |
| values | array | 是 | 允许的值列表 |

### RANGE - 范围过滤

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | 固定为"RANGE" |
| field | string | 是 | 数值字段名 |
| start | number | 否 | 起始值 |
| end | number | 否 | 结束值 |

## Occur逻辑说明

| 值 | 含义 | 评分影响 |
|------|------|------|
| MUST | 必须满足 | 参与评分 |
| SHOULD | 应该满足 | 参与评分 |
| FILTER | 必须满足 | 不参与评分 |

## API参考

### 初始化

```python
LuceneIndex(index_path: str, language: str = "zh")
```

### 索引构建方法

| 方法 | 说明 |
|------|------|
| `create_index_creator()` | 创建IndexCreator实例 |
| `add_document(fields)` | 添加单个文档（List方式） |
| `add_document_from_map(fields)` | 添加单个文档（Map方式） |
| `add_documents_batch(documents)` | 批量添加文档（List方式） |
| `add_documents_from_maps(documents)` | 批量添加文档（Map方式） |
| `commit()` | 提交索引更改 |
| `get_doc_count()` | 获取已提交文档数 |
| `get_pending_doc_count()` | 获取待提交文档数 |
| `close_index_creator()` | 关闭IndexCreator |

### 检索方法

| 方法 | 说明 |
|------|------|
| `search(query, top_n)` | 统一检索入口 |
| `search_natural(query_text, fields, top_n)` | 自然语言查询 |
| `search_composite(conditions, top_n)` | 组合查询 |
| `get_searcher_doc_count()` | 获取文档数 |
| `close_searcher()` | 关闭Searcher |

### 其他方法

| 方法 | 说明 |
|------|------|
| `close()` | 关闭所有资源 |
| `get_index_info()` | 获取索引信息 |
| `set_jar_path(path)` | 设置JAR包路径（类方法） |

## 注意事项

1. **JVM单例**：JVM只能启动一次，重复调用不会报错
2. **资源释放**：使用`with`语句或手动调用`close()`释放资源
3. **分词器一致性**：创建索引和检索时必须使用相同的语言参数
4. **索引覆盖**：每次创建IndexCreator会清空旧索引
5. **字段名大小写**：字段名区分大小写，建议统一使用小写

## 示例文件

- [example_lucene_index.py](../../examples/example_lucene_index.py) - 完整使用示例
- [test_lucene_index.py](../../tests/test_lucene_index.py) - 单元测试

## 依赖库

- Acaneko-Lucene9.12.3-v1.0.jar
- JPype1
- loguru
