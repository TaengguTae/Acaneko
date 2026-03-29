"""
模型测试服务
实现模型测试的业务逻辑，包括模型计算和分数生成
"""

import random
from typing import List, Dict
import logging

from models import ModelInfo, ModelTestRequest, DocScore, ModelTestResult, ModelTestResponse

logger = logging.getLogger(__name__)


class ModelTestService:
    """模型测试服务类"""

    def __init__(self):
        """初始化服务，加载模型配置"""
        self.embedding_models = self._init_embedding_models()
        self.rerank_models = self._init_rerank_models()
        logger.info("ModelTestService initialized with models")

    def _init_embedding_models(self) -> List[ModelInfo]:
        """初始化Embedding模型列表"""
        return [
            ModelInfo(
                id=1,
                name="OpenAI Embedding-3",
                provider="OpenAI",
                version="text-embedding-3-small",
                type="embedding",
                description="最新的OpenAI嵌入模型，支持多语言"
            ),
            ModelInfo(
                id=2,
                name="BGE-Large",
                provider="BAAI",
                version="bge-large-zh-v1.5",
                type="embedding",
                description="强大的中文嵌入模型，适合中文场景"
            ),
            ModelInfo(
                id=3,
                name="Cohere Embed",
                provider="Cohere",
                version="embed-multilingual-v3.0",
                type="embedding",
                description="多语言嵌入模型，支持100+语言"
            ),
            ModelInfo(
                id=4,
                name="E5-Large",
                provider="Intfloat",
                version="e5-large-v2",
                type="embedding",
                description="高性能嵌入模型，支持长文本"
            )
        ]

    def _init_rerank_models(self) -> List[ModelInfo]:
        """初始化Rerank模型列表"""
        return [
            ModelInfo(
                id=5,
                name="BGE Reranker",
                provider="BAAI",
                version="bge-reranker-v2-m3",
                type="rerank",
                description="高效的中文重排序模型"
            ),
            ModelInfo(
                id=6,
                name="Cohere Rerank",
                provider="Cohere",
                version="rerank-v3.5",
                type="rerank",
                description="多语言重排序模型，性能优异"
            ),
            ModelInfo(
                id=7,
                name="Cross Encoder",
                provider="Microsoft",
                version="cross-encoder-ms-marco",
                type="rerank",
                description="经典的重排序模型，稳定可靠"
            )
        ]

    def get_models_by_type(self, model_type: str) -> List[ModelInfo]:
        """根据类型获取模型列表"""
        if model_type == "embedding":
            return self.embedding_models
        elif model_type == "rerank":
            return self.rerank_models
        else:
            raise ValueError(f"Invalid model type: {model_type}")

    def get_model_by_id(self, model_id: int) -> ModelInfo:
        """根据ID获取模型信息"""
        all_models = self.embedding_models + self.rerank_models
        for model in all_models:
            if model.id == model_id:
                return model
        raise ValueError(f"Model not found with id: {model_id}")

    def validate_model_ids(self, model_ids: List[int]) -> None:
        """验证模型ID是否有效"""
        all_model_ids = [m.id for m in self.embedding_models + self.rerank_models]
        for model_id in model_ids:
            if model_id not in all_model_ids:
                raise ValueError(f"Invalid model id: {model_id}")

    def calculate_scores(self, query: str, documents: List[str], model_id: int) -> List[DocScore]:
        """
        计算文档分数
        这里使用模拟逻辑，实际应用中应该调用真实的模型API
        """
        model = self.get_model_by_id(model_id)
        logger.info(f"Calculating scores for model: {model.name}, query: {query[:50]}...")

        doc_scores = []
        for idx, doc in enumerate(documents, 1):
            if not doc.strip():
                continue
            
            score = random.uniform(0.5, 0.95)
            doc_scores.append(
                DocScore(
                    doc_id=idx,
                    doc_content=doc,
                    score=round(score, 3)
                )
            )

        doc_scores.sort(key=lambda x: x.score, reverse=True)
        logger.info(f"Calculated {len(doc_scores)} document scores for model {model.name}")
        return doc_scores

    def process_test_request(self, request: Dict) -> Dict:
        """
        处理模型测试请求
        """
        try:
            query = request.get("query", "")
            documents = request.get("documents", [])
            model_ids = request.get("model_ids", [])

            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            if not documents or len(documents) == 0:
                raise ValueError("Documents list cannot be empty")

            if not model_ids or len(model_ids) == 0:
                raise ValueError("Model IDs list cannot be empty")

            if len(model_ids) > 3:
                raise ValueError("Cannot test more than 3 models at once")

            self.validate_model_ids(model_ids)

            results = []
            for model_id in model_ids:
                model = self.get_model_by_id(model_id)
                doc_scores = self.calculate_scores(query, documents, model_id)
                
                results.append(
                    ModelTestResult(
                        model_id=model_id,
                        model_name=model.name,
                        doc_scores=doc_scores
                    )
                )

            logger.info(f"Test request processed successfully for {len(results)} models")
            
            return {
                "results": [result.dict() for result in results],
                "total_models": len(results),
                "total_documents": len([doc for doc in documents if doc.strip()])
            }

        except ValueError as e:
            logger.error(f"Validation error in test request: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing test request: {str(e)}")
            raise
