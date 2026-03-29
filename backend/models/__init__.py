"""
数据模型模块
导出所有数据模型，便于统一导入
"""

from .knowledge_base import (
    VectorModel,
    Language,
    DocumentInfo,
    KnowledgeBase,
    CreateKnowledgeBaseRequest,
    UpdateKnowledgeBaseRequest,
    BatchDeleteDocumentsRequest,
    ParseDocumentsRequest,
    ParseStatusResponse
)

from .chat import (
    ChatConfig,
    ChatRequest,
    QueryUnderstandingResult,
    RetrievalResult,
    ChatResponse
)

__all__ = [
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
    'ChatResponse'
]