"""
路由模块
导出所有路由初始化函数
"""

from .knowledge_base import init_router as init_kb_router
from .chat import init_router as init_chat_router
from .config import init_router as init_config_router

__all__ = ['init_kb_router', 'init_chat_router', 'init_config_router']