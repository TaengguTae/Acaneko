# RAG知识库管理后端服务

基于FastAPI的知识库管理系统，提供知识库创建、文件管理、文档解析等功能。

## 项目结构

```
backend/
├── __init__.py          # 包初始化文件
├── main.py              # FastAPI主应用
├── models.py             # 数据模型定义
├── config.py             # 配置管理
├── data_manager.py       # 数据存储管理
├── parse_service.py      # 文档解析服务
└── requirements.txt       # 依赖包列表
```

## 功能特性

### 1. 知识库管理
- 创建知识库（自动生成唯一ID）
- 获取知识库列表
- 获取单个知识库详情
- 更新知识库信息
- 删除知识库

### 2. 文件管理
- 上传文档（支持多文件）
- 获取文档列表
- 删除单个文档
- 批量删除文档
- 文件存储在 `data/{知识库ID}/Documents/`

### 3. 配置管理
- 获取向量模型列表
- 获取语言列表
- 动态配置，前端可获取

### 4. 文档解析
- 触发文档解析
- 支持自定义分块大小、重叠大小
- 支持多种向量模型
- 支持多种语言
- 解析结果存储在 `data/{知识库ID}/Index/`

### 5. 解析状态同步
- 实时查询解析进度
- 定期状态更新
- 完成度百分比显示

## 数据存储

所有数据存储在项目根目录的 `data/` 目录下：

```
data/
├── metadata.json              # 知识库元数据
├── {知识库ID}/
│   ├── Documents/            # 文档文件
│   └── Index/               # 解析索引
```

## API端点

### 配置相关
- `GET /api/vector-models` - 获取向量模型列表
- `GET /api/languages` - 获取语言列表

### 知识库管理
- `GET /api/knowledge-bases` - 获取所有知识库
- `GET /api/knowledge-bases/{kb_id}` - 获取单个知识库
- `POST /api/knowledge-bases` - 创建知识库
- `PUT /api/knowledge-bases/{kb_id}` - 更新知识库
- `DELETE /api/knowledge-bases/{kb_id}` - 删除知识库

### 文档管理
- `GET /api/knowledge-bases/{kb_id}/documents` - 获取文档列表
- `POST /api/knowledge-bases/{kb_id}/documents/upload` - 上传文档
- `DELETE /api/knowledge-bases/{kb_id}/documents/{doc_id}` - 删除文档
- `POST /api/knowledge-bases/{kb_id}/documents/batch-delete` - 批量删除文档

### 文档解析
- `POST /api/knowledge-bases/{kb_id}/parse` - 开始解析
- `GET /api/knowledge-bases/{kb_id}/parse-status` - 获取解析状态

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动服务
```bash
# Windows
start_backend.bat

# Linux/Mac
python backend/main.py
```

### 3. 访问API文档
启动后访问：`http://localhost:8000/docs`

## 配置说明

### 向量模型
- OpenAI Ada-002
- OpenAI Embedding-3 Small
- OpenAI Embedding-3 Large
- BGE-Small
- BGE-Large

### 支持语言
- 简体中文 (zh-CN)
- 繁体中文 (zh-TW)
- 英语 (en)
- 马来语 (ms)
- 西班牙语 (es)

### 文档格式
- PDF (.pdf)
- Word (.doc, .docx)
- 文本 (.txt)
- Markdown (.md)

## 错误处理

所有API端点都包含适当的错误处理：
- 400 Bad Request - 请求参数错误
- 404 Not Found - 资源不存在
- 500 Internal Server Error - 服务器内部错误

## 安全性

- CORS配置允许跨域访问
- 文件上传大小限制
- 输入验证和清理
- 异常捕获和日志记录

## 扩展性

代码设计遵循以下原则：
- RESTful API设计
- 模块化架构
- 类型提示
- 异步处理
- 易于测试和维护
