# Models 模块

## 职责范围

本模块包含所有数据模型定义，用于API请求、响应和内部数据结构。

## 模块结构

### `knowledge_base.py`
知识库管理相关的数据模型，包括：
- `VectorModel` - 向量模型配置
- `Language` - 语言配置
- `DocumentInfo` - 文档信息
- `KnowledgeBase` - 知识库元数据
- `CreateKnowledgeBaseRequest` - 创建知识库请求
- `UpdateKnowledgeBaseRequest` - 更新知识库请求
- `BatchDeleteDocumentsRequest` - 批量删除文档请求
- `ParseDocumentsRequest` - 文档解析请求
- `ParseStatusResponse` - 解析状态响应

### `chat.py`
聊天交互相关的数据模型，包括：
- `ChatConfig` - 聊天配置参数
- `ChatRequest` - 聊天请求
- `QueryUnderstandingResult` - Query理解结果
- `RetrievalResult` - 检索召回结果
- `ChatResponse` - 聊天响应

## 使用说明

所有模型都使用Pydantic进行数据验证和序列化，支持：
- 自动类型验证
- 字段描述和约束
- 别名生成（snake_case ↔ camelCase）
- JSON序列化/反序列化

## 导入方式

```python
from models import (
    KnowledgeBase,
    ChatRequest,
    ChatResponse,
    # ... 其他模型
)
```