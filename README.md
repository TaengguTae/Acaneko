# RAG测试平台

一个完整的前后端一体化RAG（检索增强生成）测试平台，包含知识库管理、Chat问答、测试集评估、模型测试等功能。

## 项目结构

```
Acaneko/
├── acaneko-vue/              # Vue3前端项目
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── services/       # API服务
│   │   ├── router/         # 路由配置
│   │   └── App.vue         # 根组件
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI后端项目
│   ├── main.py            # FastAPI主应用
│   ├── models.py           # 数据模型
│   ├── config.py           # 配置管理
│   ├── data_manager.py     # 数据存储管理
│   ├── parse_service.py    # 文档解析服务
│   ├── requirements.txt     # Python依赖
│   └── README.md          # 后端文档
├── data/                     # 数据存储目录
│   └── metadata.json     # 知识库元数据
├── start_backend.bat          # 后端启动脚本
└── README.md               # 项目说明文档
```

## 功能特性

### 前端功能
- 📚 **知识库管理**
  - 创建、编辑、删除知识库
  - 配置分块大小、重叠大小
  - 选择向量模型和语言
  - 文档上传和管理
  - 文档解析状态跟踪

- 💬 **Chat问答**
  - 实时对话界面
  - 消息历史记录
  - 支持多轮对话

- 📊 **测试集评估**
  - 测试用例管理
  - 批量测试执行
  - 结果统计和分析

- 🧪 **模型测试**
  - 多模型支持
  - 性能对比测试
  - 延迟统计

### 后端功能
- 🔧 **知识库管理API**
  - RESTful API设计
  - 自动ID生成
  - 元数据持久化存储

- 📁 **文件管理**
  - 文件上传和存储
  - 批量删除支持
  - 文件状态同步

- ⚙️ **配置管理**
  - 动态向量模型列表
  - 多语言支持
  - 前端可获取配置

- 🔍 **文档解析**
  - 异步解析处理
  - 进度状态跟踪
  - 索引文件生成

## 快速开始

### 1. 环境要求
- Node.js >= 20.19.0 或 >= 22.12.0
- Python >= 3.8
- npm 或 yarn

### 2. 安装前端依赖
```bash
cd acaneko-vue
npm install
```

### 3. 安装后端依赖
```bash
# Windows
start_backend.bat

# Linux/Mac
cd backend
pip install -r requirements.txt
```

### 4. 启动服务

#### 启动后端服务
```bash
# Windows
start_backend.bat

# Linux/Mac
cd backend
python main.py
```

后端服务将在 `http://localhost:8000` 启动

#### 启动前端服务
```bash
cd acaneko-vue
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

### 5. 访问应用
打开浏览器访问：`http://localhost:5173`

## API文档

后端API文档：`http://localhost:8000/docs`

主要API端点：
- `GET /api/vector-models` - 获取向量模型列表
- `GET /api/languages` - 获取语言列表
- `GET /api/knowledge-bases` - 获取所有知识库
- `POST /api/knowledge-bases` - 创建知识库
- `POST /api/knowledge-bases/{id}/documents/upload` - 上传文档
- `POST /api/knowledge-bases/{id}/parse` - 开始解析
- `GET /api/knowledge-bases/{id}/parse-status` - 获取解析状态

## 技术栈

### 前端
- **框架**：Vue 3.5.30
- **构建工具**：Vite 7.3.1
- **路由**：Vue Router 5.0.3
- **状态管理**：Pinia 3.0.4
- **UI组件**：Element Plus 2.13.6
- **HTTP客户端**：Axios 1.14.0
- **语言**：TypeScript 5.9.3

### 后端
- **框架**：FastAPI 0.104.1
- **服务器**：Uvicorn 0.24.0
- **数据验证**：Pydantic 2.5.0
- **异步处理**：aiohttp 3.9.1
- **文件上传**：python-multipart 0.0.6

## 数据存储

所有数据存储在项目根目录的 `data/` 目录：

```
data/
├── metadata.json              # 知识库元数据
├── {知识库ID}/
│   ├── Documents/            # 原始文档文件
│   └── Index/               # 解析后的索引文件
```

## 配置选项

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

## 开发说明

### 前端开发
```bash
cd acaneko-vue
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run preview      # 预览生产构建
npm run type-check  # 类型检查
npm run format       # 代码格式化
```

### 后端开发
```bash
cd backend
python main.py       # 启动开发服务器（自动重载）
```

## 部署说明

### 生产环境部署

1. **前端部署**
```bash
cd acaneko-vue
npm run build
# 将 dist/ 目录部署到Web服务器
```

2. **后端部署**
```bash
cd backend
# 使用 Gunicorn 或 Uvicorn 部署
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## 安全性

- CORS配置允许跨域访问
- 输入验证和清理
- 文件上传大小限制
- 异常处理和错误日志
- API密钥管理（待实现）

## 扩展性

项目设计遵循以下原则：
- 模块化架构
- RESTful API设计
- 类型安全（TypeScript + Pydantic）
- 异步处理
- 易于测试和维护
- 前后端分离

## 故障排除

### 常见问题

1. **端口冲突**
   - 前端默认端口：5173
   - 后端默认端口：8000
   - 如有冲突，请修改配置

2. **依赖安装失败**
   - 确保Node.js和Python版本正确
   - 清理缓存后重新安装

3. **API连接失败**
   - 确保后端服务已启动
   - 检查CORS配置
   - 查看浏览器控制台错误信息

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

## 更新日志

### v1.0.0 (2024-03-29)
- ✅ 初始版本发布
- ✅ 知识库管理功能
- ✅ Chat问答功能
- ✅ 测试集评估功能
- ✅ 模型测试功能
- ✅ 前后端一体化架构
- ✅ RESTful API设计
- ✅ 响应式UI设计
