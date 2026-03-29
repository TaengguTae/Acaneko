"""
模型测试相关的数据模型
定义模型、测试请求、测试结果等数据结构
"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ModelInfo(BaseModel):
    """模型信息"""
    id: int = Field(..., description="模型ID")
    name: str = Field(..., description="模型名称")
    provider: str = Field(..., description="提供商")
    version: str = Field(..., description="版本号")
    type: str = Field(..., description="模型类型：embedding/rerank")
    description: str = Field(..., description="模型描述")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )


class ModelTestRequest(BaseModel):
    """模型测试请求"""
    query: str = Field(..., min_length=1, max_length=1000, description="查询文本")
    documents: List[str] = Field(..., min_length=1, max_length=10, description="文档列表")
    model_ids: List[int] = Field(..., min_length=1, max_length=3, description="模型ID列表")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )


class DocScore(BaseModel):
    """文档分数"""
    doc_id: int = Field(..., description="文档ID")
    doc_content: str = Field(..., description="文档内容")
    score: float = Field(..., ge=0.0, le=1.0, description="分数值")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )


class ModelTestResult(BaseModel):
    """模型测试结果"""
    model_id: int = Field(..., description="模型ID")
    model_name: str = Field(..., description="模型名称")
    doc_scores: List[DocScore] = Field(..., description="文档分数列表")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )


class ModelTestResponse(BaseModel):
    """模型测试响应"""
    results: List[ModelTestResult] = Field(..., description="测试结果列表")
    total_models: int = Field(..., description="测试的模型总数")
    total_documents: int = Field(..., description="测试的文档总数")

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda field_name: ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split('_'))
        )
    )
