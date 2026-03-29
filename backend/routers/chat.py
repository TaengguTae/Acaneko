"""
聊天交互路由
提供聊天、Query理解、检索召回、大模型回答等API端点
"""

from fastapi import APIRouter, HTTPException
import logging

from models import (
    ChatRequest,
    ChatResponse,
    QueryUnderstandingResult,
    RetrievalResult
)
from service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["聊天交互"])


def init_router(chat_service: ChatService):
    """初始化路由，注入依赖"""
    
    @router.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        """
        聊天主接口
        接收用户查询和配置参数，返回AI回复、Query理解结果和检索召回结果
        """
        try:
            logger.info(f"Received chat request: {request.query}")
            
            request_dict = {
                "query": request.query,
                "config": request.config.dict()
            }
            
            result = chat_service.process_chat_request(request_dict)
            
            logger.info(f"Chat request processed successfully")
            return ChatResponse(**result)
        except ValueError as e:
            logger.error(f"Validation error in chat request: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/query/understand", response_model=QueryUnderstandingResult)
    async def understand_query(query: str, config: dict):
        """
        Query理解接口
        对用户查询进行意图解析和预处理
        """
        try:
            logger.info(f"Processing query understanding: {query}")
            
            result = chat_service.understand_query(query, config)
            
            logger.info(f"Query understanding completed")
            return QueryUnderstandingResult(**result)
        except Exception as e:
            logger.error(f"Query understanding failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/query/retrieve", response_model=list[RetrievalResult])
    async def retrieve_documents(query: str, kb_id: str, config: dict):
        """
        检索召回接口
        基于query从知识库中检索相关文档
        """
        try:
            logger.info(f"Retrieving documents for query: {query}, KB: {kb_id}")
            
            config["knowledge_base_id"] = kb_id
            results = chat_service.retrieve_documents(query, kb_id, config)
            
            logger.info(f"Retrieved {len(results)} documents")
            return [RetrievalResult(**result) for result in results]
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/query/generate")
    async def generate_response(query: str, context: str, config: dict):
        """
        大模型回答接口
        基于查询和检索上下文生成最终回答
        """
        try:
            logger.info(f"Generating response for query: {query}")
            
            response = chat_service.generate_response(query, context, config)
            
            logger.info(f"Response generated successfully")
            return {"response": response}
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router