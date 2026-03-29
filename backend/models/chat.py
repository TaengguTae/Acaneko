"""
聊天交互相关的数据模型
定义聊天配置、请求、响应等数据结构
"""

from typing import List, Optional
from pydantic import BaseModel, Field


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