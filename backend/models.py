"""
数据模型定义
定义知识库、文档等数据结构
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class VectorModel(BaseModel):
    """向量模型配置"""
    value: str = Field(..., description="模型值")
    label: str = Field(..., description="模型显示名称")


class Language(BaseModel):
    """语言配置"""
    value: str = Field(..., description="语言代码")
    label: str = Field(..., description="语言显示名称")


class DocumentInfo(BaseModel):
    """文档信息"""
    id: str = Field(..., description="文档ID")
    name: str = Field(..., description="文档名称")
    size: int = Field(..., description="文件大小（字节）")
    upload_time: str = Field(..., description="上传时间")
    status: str = Field(..., description="解析状态：pending/parsing/completed/failed")
    chunks: int = Field(default=0, description="分块数量")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )


class KnowledgeBase(BaseModel):
    """知识库元数据"""
    id: str = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    description: str = Field(..., description="知识库描述")
    document_count: int = Field(default=0, description="文档数量")
    created_at: str = Field(..., description="创建时间")
    status: str = Field(default="active", description="状态：active/inactive")
    chunk_size: int = Field(default=500, description="分块大小")
    overlap_size: int = Field(default=50, description="切片重叠大小")
    vector_model: str = Field(default="openai-3-small", description="向量模型")
    language: str = Field(default="zh-CN", description="知识库语言")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )


class CreateKnowledgeBaseRequest(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: str = Field(..., max_length=500, description="知识库描述")
    chunk_size: int = Field(default=500, ge=100, le=2000, description="分块大小")
    overlap_size: int = Field(default=50, ge=0, le=500, description="切片重叠大小")
    vector_model: str = Field(default="openai-3-small", description="向量模型")
    language: str = Field(default="zh-CN", description="知识库语言")


class UpdateKnowledgeBaseRequest(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class BatchDeleteDocumentsRequest(BaseModel):
    """批量删除文档请求"""
    doc_ids: List[str] = Field(..., description="文档ID列表")


class ParseDocumentsRequest(BaseModel):
    """文档解析请求"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    chunk_size: int = Field(..., ge=100, le=2000, description="分块大小")
    overlap_size: int = Field(..., ge=0, le=500, description="切片重叠大小")
    vector_model: str = Field(..., description="向量模型")
    language: str = Field(..., description="知识库语言")


class ParseStatusResponse(BaseModel):
    """解析状态响应"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    total_documents: int = Field(..., description="总文档数")
    completed: int = Field(..., description="已完成数")
    failed: int = Field(..., description="失败数")
    in_progress: int = Field(..., description="进行中数")
    percentage: float = Field(..., description="完成百分比")


class ChatConfig(BaseModel):
    """聊天配置参数"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    llm_model: str = Field(..., description="大模型选择")
    similarity_threshold: float = Field(..., ge=0, le=1, description="相似度阈值")
    advanced_query_enabled: bool = Field(default=False, description="高级Query理解开关")
    query_understanding_options: dict = Field(default_factory=dict, description="Query理解选项")
    rerank_enabled: bool = Field(default=False, description="Rerank功能开关")
    rerank_model: str = Field(default="bge-reranker", description="Rerank模型")
    rerank_threshold: float = Field(default=0.5, ge=0, le=1, description="Rerank分数阈值")


class ChatRequest(BaseModel):
    """聊天请求"""
    query: str = Field(..., min_length=1, max_length=1000, description="用户查询")
    config: ChatConfig = Field(..., description="配置参数")


class QueryUnderstandingResult(BaseModel):
    """Query理解结果"""
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    slots: List[str] = Field(default_factory=list, description="槽位列表")
    rewritten_query: str = Field(default="", description="重写后的查询")
    hyde: str = Field(default="", description="假设性文档嵌入")


class RetrievalResult(BaseModel):
    """检索召回结果"""
    id: str = Field(..., description="结果ID")
    content: str = Field(..., description="文档片段内容")
    similarity: float = Field(..., ge=0, le=1, description="相似度分数")
    rank_score: float = Field(..., ge=0, le=1, description="Rank分数")
    file_name: str = Field(..., description="文件名")
    metadata: dict = Field(default_factory=dict, description="元数据")


class ChatResponse(BaseModel):
    """聊天响应"""
    message: str = Field(..., description="AI回复消息")
    query_understanding: Optional[QueryUnderstandingResult] = Field(None, description="Query理解结果")
    retrieval_results: List[RetrievalResult] = Field(default_factory=list, description="检索召回结果")
