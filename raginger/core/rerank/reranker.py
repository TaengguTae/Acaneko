"""
Reranker模块
提供统一的文档重排序接口，支持多种reranker模型
"""

from typing import List, Optional, Tuple, Dict, Any, Type
from enum import Enum

from loguru import logger

from core.rerank.base import BaseReranker


class RerankerType(Enum):
    """Reranker模型类型枚举"""
    QWEN3 = "qwen3"
    # 后续可添加更多模型类型
    # BGE = "bge"
    # COHERE = "cohere"


class Reranker:
    """
    统一的Reranker封装类
    
    使用工厂模式根据模型类型创建对应的reranker实例，
    提供统一的接口进行文档重排序。
    
    Attributes:
        reranker_type: reranker类型
        model: 具体的reranker实例
    """
    
    _registry: Dict[str, Type[BaseReranker]] = {}
    
    @classmethod
    def register(cls, reranker_type: str) -> callable:
        """
        注册reranker类的装饰器
        
        Args:
            reranker_type: reranker类型标识
            
        Returns:
            callable: 装饰器函数
            
        Example:
            @Reranker.register("qwen3")
            class Qwen3Reranker(BaseReranker):
                ...
        """
        def decorator(reranker_class: Type[BaseReranker]) -> Type[BaseReranker]:
            cls._registry[reranker_type] = reranker_class
            logger.info(f"Registered reranker: {reranker_type}")
            return reranker_class
        return decorator
    
    @classmethod
    def list_available_rerankers(cls) -> List[str]:
        """
        列出所有已注册的reranker类型
        
        Returns:
            List[str]: 已注册的reranker类型列表
        """
        return list(cls._registry.keys())
    
    def __init__(
        self,
        reranker_type: str,
        model_path: str,
        **kwargs
    ):
        """
        初始化Reranker
        
        Args:
            reranker_type: reranker类型（如"qwen3"）
            model_path: 模型路径
            **kwargs: 传递给具体reranker的其他参数
            
        Raises:
            ValueError: 当reranker类型未注册时抛出
        """
        if reranker_type not in self._registry:
            available = ", ".join(self._registry.keys()) if self._registry else "none"
            raise ValueError(
                f"Unknown reranker type: '{reranker_type}'. "
                f"Available types: {available}"
            )
        
        self.reranker_type = reranker_type
        self.model_path = model_path
        self._kwargs = kwargs
        
        reranker_class = self._registry[reranker_type]
        logger.info(f"Creating {reranker_type} reranker from: {model_path}")
        
        self._model = reranker_class(model_path=model_path, **kwargs)
        
        logger.success(f"Reranker initialized: {reranker_type}")
    
    def compute_rank_score(
        self,
        query: str,
        documents: List[str],
        batch_size: int = 8
    ) -> List[Tuple[int, float]]:
        """
        计算文档相关性分数
        
        Args:
            query: 查询文本
            documents: 文档列表
            batch_size: 批处理大小（默认8）
            
        Returns:
            List[Tuple[int, float]]: 排序后的结果列表，每个元素为(文档索引, 分数)
            
        Raises:
            ValueError: 当参数无效时抛出
        """
        return self._model.compute_rank_score(query, documents, batch_size)
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        batch_size: int = 8
    ) -> List[Tuple[int, float, str]]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前k个结果（默认返回全部）
            batch_size: 批处理大小（默认8）
            
        Returns:
            List[Tuple[int, float, str]]: 重排序后的结果列表，
                每个元素为(文档索引, 分数, 文档内容)
        """
        return self._model.rerank(query, documents, top_k, batch_size)
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 模型配置信息
        """
        info = self._model.get_model_info()
        info["reranker_type"] = self.reranker_type
        return info
    
    @property
    def model(self) -> BaseReranker:
        """
        获取底层reranker实例
        
        Returns:
            BaseReranker: 具体的reranker实例
        """
        return self._model


from core.rerank.qwen3_reranker import Qwen3Reranker

Reranker.register("qwen3")(Qwen3Reranker)


if __name__ == "__main__":
    logger.add("reranker.log", rotation="10 MB")
    
    print("已注册的Reranker类型:", Reranker.list_available_rerankers())
    
    model_path = r"models/Qwen/Qwen3-Reranker-0.6B"
    
    reranker = Reranker(
        reranker_type="qwen3",
        model_path=model_path
    )
    
    query = "What is the capital of China?"
    documents = [
        "The capital of China is Beijing.",
        "Gravity is a force that attracts two bodies towards each other.",
        "Beijing is the political and cultural center of China.",
        "Python is a popular programming language.",
    ]
    
    print("\n=== compute_rank_score 示例 ===")
    results = reranker.compute_rank_score(query, documents)
    for idx, score in results:
        print(f"文档 {idx}: 分数={score:.4f}, 内容={documents[idx][:50]}...")
    
    print("\n=== rerank 示例 (top_k=2) ===")
    top_results = reranker.rerank(query, documents, top_k=2)
    for idx, score, doc in top_results:
        print(f"文档 {idx}: 分数={score:.4f}")
        print(f"  内容: {doc}")
    
    print("\n=== 模型信息 ===")
    print(reranker.get_model_info())
