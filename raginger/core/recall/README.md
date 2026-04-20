# 召回模块 (Recall)

基于向量检索的文本召回系统，结合FAISS索引和Embedding模型实现高效的文档检索。

## 功能特性

- ✅ 基于向量相似度的文档召回
- ✅ 支持单个查询和批量查询
- ✅ 可配置的相似度阈值过滤
- ✅ 文档存储管理
- ✅ 完善的错误处理和日志记录
- ✅ 支持文档元数据管理

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 基本使用

```python
from raginger.core.recall.recaller import Recaller
from raginger.core.embedding.embedding import Embedding

# 加载Embedding模型
embedding = Embedding("models/embedding")

# 初始化召回器
recaller = Recaller(
    index_path="path/to/index",
    embedding=embedding,
    doc_store_path="path/to/doc_store.json"
)

# 单个查询召回
query = "什么是机器学习？"
results = recaller.recall_embedding(query, topk=5, threshold=0.7)

# 查看结果
for result in results:
    print(f"文档ID: {result['doc_id']}")
    print(f"相似度: {result['score']:.4f}")
    print(f"内容: {result['content']}")
    print(f"元数据: {result['metadata']}")
    print("-" * 50)
```

### 2. 批量查询

```python
queries = [
    "什么是深度学习？",
    "自然语言处理有哪些应用？",
    "如何评估机器学习模型？"
]

results = recaller.recall_batch(queries, topk=3, threshold=0.6)

for i, query_results in enumerate(results):
    print(f"\n查询 {i+1}: {queries[i]}")
    for result in query_results:
        print(f"  - {result['doc_id']}: {result['score']:.4f}")
```

### 3. 文档管理

```python
# 添加文档
recaller.add_document(
    doc_id="doc_001",
    content="机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
    metadata={"source": "wiki", "category": "AI"}
)

# 获取文档
doc = recaller.get_document("doc_001")
print(doc)

# 检查文档是否存在
exists = recaller.has_document("doc_001")
print(f"文档存在: {exists}")

# 保存文档存储
recaller.save_doc_store("path/to/save/doc_store.json")
```

## API 文档

### 初始化

```python
Recaller(
    index_path: str,
    embedding: Embedding,
    doc_store_path: Optional[str] = None
)
```

**参数：**
- `index_path`: FAISS索引文件路径（不包含扩展名）
- `embedding`: Embedding模型实例
- `doc_store_path`: 文档存储文件路径（可选）

**异常：**
- `ValueError`: 当参数无效时抛出
- `FileNotFoundError`: 当索引文件不存在时抛出
- `IOError`: 当加载失败时抛出

### 向量召回

```python
recall_embedding(
    query: str,
    topk: int = 10,
    threshold: float = 0.0
) -> List[Dict[str, Any]]
```

**参数：**
- `query`: 查询文本
- `topk`: 返回结果数量（默认10）
- `threshold`: 相似度阈值（默认0.0，不过滤）

**返回：**
- `List[Dict[str, Any]]`: 检索结果列表，每个结果包含：
  - `doc_id`: 文档ID
  - `content`: 文档内容
  - `score`: 相似度分数
  - `metadata`: 文档元数据

**异常：**
- `ValueError`: 当参数无效时抛出

### 批量召回

```python
recall_batch(
    queries: List[str],
    topk: int = 10,
    threshold: float = 0.0
) -> List[List[Dict[str, Any]]]
```

**参数：**
- `queries`: 查询文本列表
- `topk`: 每个查询返回的结果数量（默认10）
- `threshold`: 相似度阈值（默认0.0，不过滤）

**返回：**
- `List[List[Dict[str, Any]]]`: 每个查询的检索结果列表

### 文档管理

```python
# 添加文档
add_document(
    doc_id: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None

# 获取文档
get_document(doc_id: str) -> Optional[Dict[str, Any]]

# 检查文档是否存在
has_document(doc_id: str) -> bool

# 保存文档存储
save_doc_store(doc_store_path: str) -> None
```

### 其他方法

```python
# 获取索引信息
get_index_info() -> Dict[str, Any]
```

## 使用示例

### 完整示例

```python
from raginger.core.recall.recaller import Recaller
from raginger.core.embedding.embedding import Embedding
from loguru import logger
import json

# 配置日志
logger.add("recall.log", rotation="10 MB")

# 加载Embedding模型
embedding = Embedding("models/embedding")

# 初始化召回器
recaller = Recaller(
    index_path="data/index",
    embedding=embedding,
    doc_store_path="data/doc_store.json"
)

# 查看索引信息
info = recaller.get_index_info()
logger.info(f"索引信息: {info}")

# 执行召回
query = "如何提高机器学习模型的性能？"
results = recaller.recall_embedding(query, topk=5, threshold=0.7)

logger.info(f"查询: {query}")
logger.info(f"找到 {len(results)} 个相关文档")

for i, result in enumerate(results, 1):
    logger.info(f"\n结果 {i}:")
    logger.info(f"  文档ID: {result['doc_id']}")
    logger.info(f"  相似度: {result['score']:.4f}")
    logger.info(f"  内容: {result['content'][:100]}...")
    logger.info(f"  元数据: {result['metadata']}")
```

### 构建索引和文档存储

```python
from raginger.core.index.vector_index import FaissIndex
from raginger.core.embedding.embedding import Embedding
from raginger.core.recall.recaller import Recaller
import numpy as np

# 初始化
embedding = Embedding("models/embedding")
index = FaissIndex(dimension=384)
doc_store = {}

# 添加文档
documents = [
    {"id": "doc_1", "content": "机器学习基础概念"},
    {"id": "doc_2", "content": "深度学习进阶教程"},
    {"id": "doc_3", "content": "自然语言处理应用"}
]

# 向量化并添加到索引
contents = [doc["content"] for doc in documents]
doc_ids = [doc["id"] for doc in documents]
vectors = embedding.get_embedding(contents, content_type="document")

index.add_vectors(vectors, doc_ids)

# 构建文档存储
for doc in documents:
    doc_store[doc["id"]] = {
        "content": doc["content"],
        "metadata": {}
    }

# 保存
index.save_index("data/index")

import json
with open("data/doc_store.json", 'w', encoding='utf-8') as f:
    json.dump(doc_store, f, ensure_ascii=False, indent=2)

# 使用召回器
recaller = Recaller(
    index_path="data/index",
    embedding=embedding,
    doc_store_path="data/doc_store.json"
)

results = recaller.recall_embedding("什么是机器学习？", topk=2)
```

### 与RAG系统集成

```python
from raginger.core.recall.recaller import Recaller
from raginger.core.embedding.embedding import Embedding

class RAGSystem:
    def __init__(self, index_path, embedding, doc_store_path):
        self.recaller = Recaller(index_path, embedding, doc_store_path)
    
    def retrieve(self, query, topk=5):
        """检索相关文档"""
        results = self.recaller.recall_embedding(query, topk=topk, threshold=0.6)
        return results
    
    def generate_answer(self, query, topk=5):
        """生成答案（示例）"""
        # 1. 检索相关文档
        docs = self.retrieve(query, topk)
        
        # 2. 构建上下文
        context = "\n".join([doc['content'] for doc in docs])
        
        # 3. 调用LLM生成答案（这里只是示例）
        # answer = llm.generate(query, context)
        
        return {
            "query": query,
            "context": context,
            "sources": docs
        }

# 使用
embedding = Embedding("models/embedding")
rag = RAGSystem("data/index", embedding, "data/doc_store.json")
result = rag.generate_answer("什么是机器学习？", topk=3)
```

## 文档存储格式

文档存储使用JSON格式，结构如下：

```json
{
  "doc_1": {
    "content": "文档内容",
    "metadata": {
      "source": "来源",
      "category": "分类",
      "timestamp": "时间戳"
    }
  },
  "doc_2": {
    "content": "另一个文档内容",
    "metadata": {}
  }
}
```

## 性能优化建议

### 1. 索引优化
- 使用合适的向量维度（通常384或768）
- 对于大规模数据，考虑使用IVF或HNSW索引

### 2. 查询优化
- 合理设置topk值，避免过大
- 使用合适的threshold过滤低质量结果
- 批量查询时控制并发数量

### 3. 内存管理
- 定期清理不需要的文档
- 对于大规模文档存储，考虑分片存储

### 4. 缓存策略
- 缓存热门查询结果
- 缓存频繁访问的文档内容

## 常见问题

### Q: 如何选择合适的threshold？
A: 
- threshold=0.0: 返回所有结果（不过滤）
- threshold=0.5-0.7: 推荐范围，过滤低相似度结果
- threshold=0.8+: 严格过滤，只保留高相似度结果

### Q: 如何处理大规模文档？
A: 
- 使用分片存储，每个分片包含一部分文档
- 使用数据库（如MongoDB）存储文档内容
- 考虑使用分布式索引

### Q: 如何提高召回质量？
A: 
- 使用高质量的Embedding模型
- 确保文档内容质量
- 优化文档切片策略
- 使用混合检索（向量+关键词）

### Q: 如何处理多语言文档？
A: 
- 使用多语言Embedding模型
- 为不同语言建立独立索引
- 使用翻译模型统一处理

## 运行测试

```bash
cd raginger
python -m pytest tests/test_recaller.py -v
```

或使用 unittest：

```bash
cd raginger
python -m unittest tests.test_recaller -v
```

## 许可证

MIT License
