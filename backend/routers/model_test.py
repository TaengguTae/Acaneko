"""
模型测试路由
提供模型列表获取和模型测试的API端点
"""

from fastapi import APIRouter, HTTPException
import logging

from models import ModelInfo, ModelTestRequest, ModelTestResponse
from service import ModelTestService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/model-test", tags=["模型测试"])


def init_router(model_test_service: ModelTestService):
    """初始化路由，注入依赖"""
    
    @router.get("/models/{model_type}", response_model=list[ModelInfo])
    async def get_models(model_type: str):
        """
        获取模型列表
        根据模型类型（embedding/rerank）返回对应的模型列表
        """
        try:
            logger.info(f"Fetching models for type: {model_type}")
            
            if model_type not in ["embedding", "rerank"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid model type: {model_type}. Must be 'embedding' or 'rerank'"
                )
            
            models = model_test_service.get_models_by_type(model_type)
            logger.info(f"Retrieved {len(models)} models for type: {model_type}")
            return models
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/test", response_model=ModelTestResponse)
    async def test_models(request: ModelTestRequest):
        """
        模型测试接口
        接收查询文本、文档列表和模型ID列表，返回各模型的计算结果
        """
        try:
            logger.info(f"Received test request for {len(request.model_ids)} models")
            
            request_dict = {
                "query": request.query,
                "documents": request.documents,
                "model_ids": request.model_ids
            }
            
            result = model_test_service.process_test_request(request_dict)
            
            logger.info(f"Test request processed successfully")
            return ModelTestResponse(**result)
            
        except ValueError as e:
            logger.error(f"Validation error in test request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing test request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router
