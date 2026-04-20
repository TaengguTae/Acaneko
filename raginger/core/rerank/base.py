"""
Reranker基类模块
定义所有Reranker模型必须实现的接口
"""

from typing import List, Optional, Tuple, Dict, Any
from abc import ABC, abstractmethod


class BaseReranker(ABC):
    """
    Reranker抽象基类
    
    所有具体的reranker模型都需要继承此类并实现其抽象方法。
    """
    
    @abstractmethod
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
            batch_size: 批处理大小
            
        Returns:
            List[Tuple[int, float]]: 排序后的结果列表，每个元素为(文档索引, 分数)
        """
        pass
    
    @abstractmethod
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
            batch_size: 批处理大小
            
        Returns:
            List[Tuple[int, float, str]]: 重排序后的结果列表，
                每个元素为(文档索引, 分数, 文档内容)
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 模型配置信息
        """
        pass
