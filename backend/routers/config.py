"""
配置管理路由
提供向量模型、语言等配置选项的API端点
"""

from fastapi import APIRouter
import logging

from models import VectorModel, Language
from config import ConfigManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["配置管理"])


def init_router():
    """初始化路由"""
    
    @router.get("/vector-models", response_model=list[VectorModel])
    async def get_vector_models():
        """获取向量模型列表"""
        try:
            models = ConfigManager.get_vector_models()
            logger.info(f"Retrieved {len(models)} vector models")
            return models
        except Exception as e:
            logger.error(f"Failed to get vector models: {str(e)}")
            raise

    @router.get("/languages", response_model=list[Language])
    async def get_languages():
        """获取语言列表"""
        try:
            languages = ConfigManager.get_languages()
            logger.info(f"Retrieved {len(languages)} languages")
            return languages
        except Exception as e:
            logger.error(f"Failed to get languages: {str(e)}")
            raise
    
    return router