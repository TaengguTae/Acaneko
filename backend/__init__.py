"""
RAG知识库与聊天后端服务
提供知识库管理、文档解析、聊天对话等功能
"""

__version__ = "2.0.0"

from models import *
from service import *
from config import *

__all__ = [
    # Models
    'VectorModel',
    'Language',
    'DocumentInfo',
    'KnowledgeBase',
    'CreateKnowledgeBaseRequest',
    'UpdateKnowledgeBaseRequest',
    'BatchDeleteDocumentsRequest',
    'ParseDocumentsRequest',
    'ParseStatusResponse',
    'ChatConfig',
    'ChatRequest',
    'QueryUnderstandingResult',
    'RetrievalResult',
    'ChatResponse',
    # Services
    'DataManager',
    'ParseService',
    'ChatService',
    # Config
    'ConfigManager'
]