"""
FastAPI主应用
提供知识库管理、聊天交互等API端点
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import sys
import logging

sys.path.insert(0, str(__file__).replace('\\', '/').rsplit('/', 1)[0])

from service import DataManager, ParseService, ChatService, ModelTestService
from routers import init_kb_router, init_chat_router, init_config_router, init_model_test_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="RAG知识库与聊天API",
    description="提供知识库管理、文档解析、聊天对话等功能",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_services():
    """初始化服务实例"""
    data_manager = DataManager()
    parse_service = ParseService(data_manager)
    chat_service = ChatService(data_manager)
    model_test_service = ModelTestService()
    
    return data_manager, parse_service, chat_service, model_test_service


data_manager, parse_service, chat_service, model_test_service = init_services()


def register_routers():
    """注册所有路由"""
    kb_router = init_kb_router(data_manager, parse_service)
    chat_router = init_chat_router(chat_service)
    config_router = init_config_router()
    model_test_router = init_model_test_router(model_test_service)
    
    app.include_router(kb_router)
    app.include_router(chat_router)
    app.include_router(config_router)
    app.include_router(model_test_router)
    
    logger.info("All routers registered successfully")


register_routers()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RAG Knowledge Base and Chat API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "rag-api"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)