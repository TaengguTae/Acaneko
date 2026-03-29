# Routers 模块

## 职责范围

本模块包含所有FastAPI路由定义，负责API端点的组织和路由管理。

## 模块结构

### `knowledge_base.py`
知识库管理路由，提供：
- 知识库CRUD操作（GET/POST/PUT/DELETE）
- 文档管理（上传、删除、批量删除）
- 文档解析（开始解析、查询解析状态）
- 路径前缀：`/api/knowledge-bases`

### `chat.py`
聊天交互路由，提供：
- 聊天主接口（完整聊天流程）
- Query理解接口
- 检索召回接口
- 大模型回答接口
- 路径前缀：`/api`

### `config.py`
配置管理路由，提供：
- 向量模型列表接口
- 语言选项列表接口
- 路径前缀：`/api`

## 路由设计原则

所有路由遵循以下原则：
- RESTful API设计规范
- 统一的错误处理
- 详细的日志记录
- 清晰的路径命名
- 合理的HTTP状态码使用
- 完整的API文档（Swagger/OpenAPI）

## 使用说明

每个路由模块都提供`init_router()`函数，用于初始化路由并注入依赖：

```python
from routers import init_kb_router, init_chat_router, init_config_router

# 初始化路由
kb_router = init_kb_router(data_manager, parse_service)
chat_router = init_chat_router(chat_service)
config_router = init_config_router()

# 注册到FastAPI应用
app.include_router(kb_router)
app.include_router(chat_router)
app.include_router(config_router)
```

## API文档

启动服务后，可以通过以下地址查看完整的API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`