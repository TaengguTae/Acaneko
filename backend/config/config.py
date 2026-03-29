"""
配置管理
提供向量模型、语言等配置选项
"""

from typing import List
from models import VectorModel, Language


class ConfigManager:
    """配置管理器"""

    @staticmethod
    def get_vector_models() -> List[VectorModel]:
        """获取向量模型列表"""
        return [
            VectorModel(value="openai-ada-002", label="OpenAI Ada-002"),
            VectorModel(value="openai-3-small", label="OpenAI Embedding-3 Small"),
            VectorModel(value="openai-3-large", label="OpenAI Embedding-3 Large"),
            VectorModel(value="bge-small", label="BGE-Small"),
            VectorModel(value="bge-large", label="BGE-Large")
        ]

    @staticmethod
    def get_languages() -> List[Language]:
        """获取语言列表"""
        return [
            Language(value="zh-CN", label="简体中文"),
            Language(value="zh-TW", label="繁体中文"),
            Language(value="en", label="英语"),
            Language(value="ms", label="马来语"),
            Language(value="es", label="西班牙语")
        ]
