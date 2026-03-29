# Service 模块

## 职责范围

本模块包含所有业务逻辑服务类，负责处理核心业务功能。

## 模块结构

### `data_manager.py`
数据存储管理服务，负责：
- metadata.json的读写操作
- 知识库CRUD操作
- 文档上传、删除、状态管理
- 文件系统操作
- 数据持久化

### `parse_service.py`
文档解析服务，负责：
- 文档解析任务调度
- 与远程解析API集成
- 解析状态跟踪
- 异步任务管理
- 索引文件存储

### `chat_service.py`
聊天交互服务，负责：
- Query理解处理（关键词提取、槽位提取、Query改写、HyDE）
- 检索召回功能（相似度过滤、Rerank重排序）
- 大模型回答生成
- 完整聊天流程处理

## 使用说明

所有服务类都遵循以下原则：
- 单一职责原则
- 依赖注入模式
- 完整的错误处理
- 详细的日志记录

## 导入方式

```python
from service import DataManager, ParseService, ChatService

# 初始化服务
data_manager = DataManager()
parse_service = ParseService(data_manager)
chat_service = ChatService(data_manager)
```