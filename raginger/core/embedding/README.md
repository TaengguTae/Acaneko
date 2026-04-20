# 文本向量化 (Embedding)

基于sentence-transformers的文本向量化工具，支持将文本转换为高质量的向量表示。

## 功能特性

- ✅ 支持加载本地或HuggingFace预训练模型
- ✅ 自动读取和应用prefix配置
- ✅ 支持单个文本和批量文本向量化
- ✅ 区分query和doc两种内容类型
- ✅ 完善的错误处理和输入验证
- ✅ 详细的日志记录（使用loguru）
- ✅ 灵活的配置管理

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 基本使用

```python
from raginger.core.embedding.embedding import Embedding

# 加载模型（可以是本地路径或HuggingFace模型名称）
embedding = Embedding("sentence-transformers/all-MiniLM-L6-v2")

# 单个文本向量化
text = "这是一个测试文本"
vector = embedding.get_embedding(text, content_type="doc")
print(f"向量维度: {vector.shape}")  # (384,)

# 批量文本向量化
texts = ["文本1", "文本2", "文本3"]
vectors = embedding.get_embedding(texts, content_type="doc")
print(f"向量形状: {vectors.shape}")  # (3, 384)
```

### 2. 使用prefix配置

```python
# 模型目录下应有 config_sentence_transformers.json 文件
# 内容示例：
# {
#   "query_prefix": "query: ",
#   "doc_prefix": "passage: "
# }

embedding = Embedding("path/to/model")

# query会自动添加 "query: " 前缀
query_vec = embedding.get_embedding("搜索查询", content_type="query")

# doc会自动添加 "passage: " 前缀
doc_vec = embedding.get_embedding("文档内容", content_type="doc")
```

### 3. 获取模型信息

```python
# 获取向量维度
dim = embedding.get_embedding_dimension()
print(f"向量维度: {dim}")

# 获取模型详细信息
info = embedding.get_model_info()
print(f"模型信息: {info}")
```

## API 文档

### 初始化

```python
Embedding(model_path: str)
```

**参数：**
- `model_path`: 模型路径，可以是：
  - 本地目录路径
  - HuggingFace模型名称（如 "sentence-transformers/all-MiniLM-L6-v2"）

**异常：**
- `ValueError`: 当模型路径无效时抛出

**配置文件：**
- 自动读取 `{model_path}/config_sentence_transformers.json`
- 支持的配置字段：
  - `query_prefix`: query类型文本的前缀
  - `doc_prefix`: doc类型文本的前缀

### 获取向量

```python
get_embedding(text: Union[str, List[str]], content_type: str = "doc") -> np.ndarray
```

**参数：**
- `text`: 输入文本
  - 单个字符串：返回形状为 (dimension,) 的向量
  - 字符串列表：返回形状为 (n, dimension) 的向量数组
- `content_type`: 内容类型
  - `"query"`: 查询文本，应用query_prefix
  - `"doc"`: 文档文本（默认），应用doc_prefix

**返回：**
- `np.ndarray`: 文本向量
  - 单个文本：形状 (dimension,)
  - 批量文本：形状 (n, dimension)

**异常：**
- `ValueError`: 当输入参数无效时抛出

### 其他方法

```python
# 获取向量维度
get_embedding_dimension() -> int

# 获取模型信息
get_model_info() -> dict
```

## 使用示例

### 完整示例

```python
from raginger.core.embedding.embedding import Embedding
from loguru import logger
import numpy as np

# 配置日志
logger.add("embedding.log", rotation="10 MB")

# 加载模型
model_path = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
embedding = Embedding(model_path)

# 查询向量化
query = "什么是机器学习？"
query_vector = embedding.get_embedding(query, content_type="query")
logger.info(f"查询向量形状: {query_vector.shape}")

# 文档向量化
documents = [
    "机器学习是人工智能的一个分支。",
    "深度学习是机器学习的一种方法。",
    "自然语言处理是AI的重要应用领域。"
]

doc_vectors = embedding.get_embedding(documents, content_type="doc")
logger.info(f"文档向量形状: {doc_vectors.shape}")

# 计算相似度
from numpy.linalg import norm

cosine_similarities = np.dot(doc_vectors, query_vector) / (
    norm(doc_vectors, axis=1) * norm(query_vector)
)

logger.info("文档与查询的相似度:")
for i, (doc, sim) in enumerate(zip(documents, cosine_similarities)):
    logger.info(f"  文档{i+1}: {sim:.4f} - {doc}")
```

### 批量处理示例

```python
from raginger.core.embedding.embedding import Embedding
import numpy as np

embedding = Embedding("sentence-transformers/all-MiniLM-L6-v2")

# 大批量文本处理
batch_size = 1000
all_texts = [f"文档内容 {i}" for i in range(10000)]

all_vectors = []
for i in range(0, len(all_texts), batch_size):
    batch = all_texts[i:i+batch_size]
    vectors = embedding.get_embedding(batch, content_type="doc")
    all_vectors.append(vectors)
    logger.info(f"已处理 {min(i+batch_size, len(all_texts))}/{len(all_texts)} 个文本")

# 合并所有向量
final_vectors = np.vstack(all_vectors)
logger.info(f"总向量形状: {final_vectors.shape}")
```

### 与向量索引结合使用

```python
from raginger.core.embedding.embedding import Embedding
from raginger.core.index.vector_index import FaissIndex
import numpy as np

# 初始化
embedding = Embedding("sentence-transformers/all-MiniLM-L6-v2")
index = FaissIndex(dimension=384)

# 添加文档到索引
documents = [
    {"id": "doc_1", "content": "机器学习基础"},
    {"id": "doc_2", "content": "深度学习进阶"},
    {"id": "doc_3", "content": "自然语言处理"}
]

# 批量向量化
contents = [doc["content"] for doc in documents]
doc_ids = [doc["id"] for doc in documents]
vectors = embedding.get_embedding(contents, content_type="doc")

# 添加到索引
index.add_vectors(vectors, doc_ids)

# 查询
query = "什么是机器学习？"
query_vector = embedding.get_embedding(query, content_type="query")
results = index.search(query_vector, top_k=2)

print("最相似的文档:")
for doc_id, score in results:
    print(f"  {doc_id}: {score:.4f}")
```

## 配置文件格式

在模型目录下创建 `config_sentence_transformers.json`：

```json
{
  "query_prefix": "query: ",
  "doc_prefix": "passage: "
}
```

**说明：**
- `query_prefix`: 用于查询文本的前缀
- `doc_prefix`: 用于文档文本的前缀
- 前缀会在向量化前自动添加到文本前面
- 配置文件可选，不存在则不应用前缀

## 性能优化建议

### 1. 批量处理
- 使用批量文本输入而不是逐个处理
- 推荐批量大小：32-256个文本

### 2. 模型选择
- 小模型（如 all-MiniLM-L6-v2）：速度快，适合实时场景
- 大模型（如 paraphrase-multilingual-mpnet-base-v2）：质量高，适合离线处理

### 3. 内存管理
- 对于大规模数据，分批处理避免内存溢出
- 及时释放不需要的向量数据

### 4. GPU加速
- 安装GPU版本的PyTorch
- sentence-transformers会自动使用GPU

## 常见问题

### Q: 如何选择合适的模型？
A: 
- 英文场景：`all-MiniLM-L6-v2`（快速）或 `all-mpnet-base-v2`（高质量）
- 中文场景：`paraphrase-multilingual-MiniLM-L12-v2` 或 `text2vec-chinese-base`
- 多语言场景：`paraphrase-multilingual-mpnet-base-v2`

### Q: prefix的作用是什么？
A: prefix用于区分不同类型的文本（query vs doc），某些模型在训练时使用了不同的前缀，使用正确的前缀可以提高检索效果。

### Q: 向量维度可以修改吗？
A: 不可以，向量维度由模型决定。如需不同维度，需要选择其他模型。

### Q: 如何处理超长文本？
A: 模型会自动截断超长文本（通常限制在256或512个token）。建议预处理时分割长文本。

## 运行测试

```bash
cd raginger
python -m pytest tests/test_embedding.py -v
```

或使用 unittest：

```bash
cd raginger
python -m unittest tests.test_embedding -v
```

## 许可证

MIT License
