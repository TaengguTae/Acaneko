"""
知识库管理相关的数据模型
定义知识库、文档、解析等数据结构
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


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