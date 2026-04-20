# 文档切片器 (Document Splitter)

用于RAG系统的文档预处理，支持按字符和按token两种切分模式。

## 功能特性

- ✅ 支持按字符和按token两种切分模式
- ✅ 灵活的切片大小和重叠配置
- ✅ 完善的错误处理和参数验证
- ✅ 缓存机制，避免重复处理
- ✅ 并行处理批量文档
- ✅ 支持自定义元数据字段
- ✅ 详细的日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 基本使用

```python
from transformers import AutoTokenizer
from raginger.core.parse.splitter import DocumentSplitter

# 加载分词器
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

# 创建切片器实例
splitter = DocumentSplitter(
    tokenizer=tokenizer,
    split_type="character",  # 或 "token"
    chunk_size=500,
    chunk_overlap=50
)

# 切分单个文档
chunks = splitter.split_single_document(
    document="你的文档内容...",
    doc_id="doc_001",
    doc_name="example.txt"
)

# 查看切片结果
for chunk in chunks:
    print(f"Chunk ID: {chunk['chunk_id']}")
    print(f"Content: {chunk['content']}")
    print(f"Length: {chunk['chunk_length']}")
    print(f"Tokens: {chunk['token_count']}")
```

### 2. 批量处理文档

```python
documents = [
    {
        "content": "第一个文档的内容...",
        "doc_id": "doc_001",
        "doc_name": "document1.txt"
    },
    {
        "content": "第二个文档的内容...",
        "doc_id": "doc_002",
        "doc_name": "document2.txt"
    }
]

# 批量切分（支持并行处理）
chunks = splitter.split_documents(documents, max_workers=4)
```

### 3. 添加自定义元数据

```python
splitter = DocumentSplitter(
    tokenizer=tokenizer,
    split_type="character",
    chunk_size=500,
    chunk_overlap=50,
    additional_metadata_fields={
        "language": "zh",
        "source": "web",
        "category": "tech"
    }
)

chunks = splitter.split_single_document(
    document="文档内容...",
    doc_id="doc_001",
    doc_name="example.txt"
)

# 每个切片都会包含自定义字段
for chunk in chunks:
    print(f"Language: {chunk['language']}")
    print(f"Source: {chunk['source']}")
    print(f"Category: {chunk['category']}")
```

## 切片结果格式

每个切片包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `chunk_id` | str | 切片唯一标识符（格式：{doc_id}_{chunk_index}） |
| `content` | str | 切片内容字符串 |
| `doc_id` | str | 原始文档ID |
| `doc_name` | str | 原始文档名称 |
| `chunk_length` | int | 切片长度（字符数或token数，取决于split_type） |
| `chunk_index` | int | 切片在原始文档中的序号（从0开始） |
| `token_count` | int | 切片的token数量 |
| `start_index` | int | 切片在原始文档中的起始位置索引 |
| `end_index` | int | 切片在原始文档中的结束位置索引 |

## 参数说明

### 初始化参数

- `tokenizer`: 分词器实例（必需）
- `split_type`: 切分类型，可选 "character" 或 "token"（默认："character"）
- `chunk_size`: 切片大小（默认：500）
- `chunk_overlap`: 切片重叠大小（默认：50）
- `additional_metadata_fields`: 额外的元数据字段字典（可选）

### 参数约束

- `chunk_size` 必须大于 0
- `chunk_overlap` 必须非负
- `chunk_overlap` 必须小于 `chunk_size`

## 性能优化

### 缓存机制

切片器会自动缓存已处理的文档，避免重复处理：

```python
# 第一次处理
chunks1 = splitter.split_single_document(doc, "doc_001", "test.txt")

# 第二次处理相同文档（从缓存读取）
chunks2 = splitter.split_single_document(doc, "doc_001", "test.txt")

# 清空缓存
splitter.clear_cache()
```

### 并行处理

批量处理时支持多线程并行：

```python
# 使用4个线程并行处理
chunks = splitter.split_documents(documents, max_workers=4)
```

## 运行测试

```bash
cd raginger
python -m pytest tests/test_splitter.py -v
```

或使用unittest：

```bash
cd raginger
python -m unittest tests.test_splitter -v
```

## 日志记录

切片器使用 loguru 库记录日志，提供更美观和功能强大的日志输出：

```python
from loguru import logger

# loguru 默认配置已经很好，无需额外配置
# 如需自定义，可以这样：
logger.add("splitter.log", rotation="500 MB", level="INFO")
```

loguru 的优势：
- 彩色输出，更易阅读
- 自动包含时间戳、文件名、行号等信息
- 支持文件轮转和保留策略
- 更简洁的API

## 错误处理

切片器包含完善的错误处理：

- 参数验证：初始化时验证参数有效性
- 空文档处理：自动跳过空文档或仅包含空白字符的文档
- 异常捕获：切分过程中的异常会被捕获并记录日志
- 格式验证：批量处理时验证文档格式

## 最佳实践

1. **选择合适的切分模式**：
   - 对于中文文档，推荐使用 "character" 模式
   - 对于英文文档或需要精确控制token数量的场景，使用 "token" 模式

2. **设置合理的切片大小**：
   - 字符模式：建议 300-800 字符
   - Token模式：建议 100-500 tokens

3. **调整重叠大小**：
   - 一般设置为切片大小的 10-20%
   - 重叠可以确保上下文连续性

4. **使用缓存**：
   - 对于重复处理的文档，利用缓存提高性能
   - 定期清空缓存避免内存占用过大

## 许可证

MIT License
