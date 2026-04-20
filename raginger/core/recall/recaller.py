"""
召回模块
实现基于向量检索和BM25的混合召回功能
"""

from typing import List, Dict, Optional, Any
import os
from pathlib import Path

import numpy as np
from loguru import logger

from core.index.vector_index import FaissIndex
from core.index.lucene_index import LuceneIndex
from core.embedding.embedding import Embedding


class Recaller:
    """
    召回类
    
    支持向量召回和BM25召回的混合召回功能。
    向量召回使用FAISS索引，BM25召回使用Lucene索引。
    
    Attributes:
        faiss_index_path: FAISS索引路径
        lucene_index_path: Lucene索引路径
        embedding: Embedding模型实例
        faiss_index: FAISS索引实例
        lucene_index: Lucene索引实例
    """
    
    def __init__(
        self,
        faiss_index_path: str,
        lucene_index_path: str,
        embedding: Embedding,
        language: str = "zh"
    ):
        """
        初始化Recaller类
        
        Args:
            faiss_index_path: FAISS索引文件路径（不包含扩展名）
            lucene_index_path: Lucene索引目录路径
            embedding: Embedding模型实例
            language: Lucene索引语言（默认"zh"）
            
        Raises:
            ValueError: 当参数无效时抛出
            FileNotFoundError: 当索引文件不存在时抛出
        """
        if not faiss_index_path or not isinstance(faiss_index_path, str):
            raise ValueError(
                f"faiss_index_path must be a non-empty string, got {faiss_index_path}"
            )
        
        if not lucene_index_path or not isinstance(lucene_index_path, str):
            raise ValueError(
                f"lucene_index_path must be a non-empty string, got {lucene_index_path}"
            )
        
        required_methods = ['get_embedding', 'get_embedding_dimension']
        for method in required_methods:
            if not hasattr(embedding, method) or not callable(getattr(embedding, method)):
                raise ValueError(
                    f"embedding must have '{method}' method, got {type(embedding)}"
                )
        
        self.faiss_index_path = faiss_index_path
        self.lucene_index_path = lucene_index_path
        self.embedding = embedding
        self.language = language
        self.faiss_index: Optional[FaissIndex] = None
        self.lucene_index: Optional[LuceneIndex] = None
        
        logger.info("Initializing Recaller...")
        
        self._load_faiss_index()
        self._init_lucene_index()
        
        logger.success("Recaller initialized successfully")
    
    def _load_faiss_index(self) -> None:
        """
        加载FAISS索引
        
        Raises:
            FileNotFoundError: 当索引文件不存在时抛出
            IOError: 当索引加载失败时抛出
        """
        logger.info(f"Loading FAISS index from: {self.faiss_index_path}")
        
        try:
            self.faiss_index = FaissIndex.load_index(self.faiss_index_path)
            logger.success(
                f"FAISS index loaded successfully, "
                f"total vectors: {self.faiss_index.get_vector_count()}"
            )
        except FileNotFoundError as e:
            logger.error(f"FAISS index file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            raise IOError(f"Failed to load FAISS index: {e}")
    
    def _init_lucene_index(self) -> None:
        """
        初始化Lucene索引
        
        Raises:
            RuntimeError: 当Lucene初始化失败时抛出
        """
        logger.info(f"Initializing Lucene index from: {self.lucene_index_path}")
        
        try:
            self.lucene_index = LuceneIndex(self.lucene_index_path, self.language)
            logger.success("Lucene index initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Lucene index: {e}")
            raise RuntimeError(f"Failed to initialize Lucene index: {e}")
    
    def recall_vector(
        self,
        query: str,
        topk: int = 10,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        向量召回
        
        Args:
            query: 查询文本
            topk: 返回结果数量（默认10）
            threshold: 相似度阈值（默认0.0，不过滤）
            
        Returns:
            List[Dict[str, Any]]: 检索结果列表，每个结果包含：
                - chunk_id: 切片ID
                - score: 相似度分数
                
        Raises:
            ValueError: 当参数无效时抛出
        """
        if not query or not isinstance(query, str):
            raise ValueError(
                f"query must be a non-empty string, got {query}"
            )
        
        if topk <= 0:
            raise ValueError(f"topk must be positive, got {topk}")
        
        if not (0.0 <= threshold <= 1.0):
            raise ValueError(
                f"threshold must be between 0.0 and 1.0, got {threshold}"
            )
        
        logger.info(
            f"Vector recall: query='{query[:50]}...', topk={topk}, threshold={threshold}"
        )
        
        try:
            logger.debug("Encoding query to vector...")
            query_vector = self.embedding.get_embedding(query, content_type="query")
            
            logger.debug("Searching in FAISS index...")
            search_results = self.faiss_index.search(query_vector, top_k=topk)
            
            logger.debug("Filtering results by threshold...")
            filtered_results = []
            for chunk_id, score in search_results:
                if score >= threshold:
                    result = {
                        "chunk_id": chunk_id,
                        "score": score
                    }
                    filtered_results.append(result)
            
            logger.info(
                f"Vector recall completed: {len(search_results)} results found, "
                f"{len(filtered_results)} results after filtering"
            )
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Vector recall failed: {e}")
            raise
    
    def recall_bm25_natural(
        self,
        query: str,
        topk: int = 10,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        BM25召回（自然语言版）
        
        Args:
            query: 自然语言查询文本
            topk: 返回结果数量（默认10）
            fields: 搜索字段列表（默认["content", "title"]）
            
        Returns:
            List[Dict[str, Any]]: 检索结果列表，每个结果包含：
                - chunk_id: 切片ID
                - score: BM25分数
                - fields: 存储字段
                
        Raises:
            ValueError: 当参数无效时抛出
        """
        if not query or not isinstance(query, str):
            raise ValueError(
                f"query must be a non-empty string, got {query}"
            )
        
        if topk <= 0:
            raise ValueError(f"topk must be positive, got {topk}")
        
        logger.info(
            f"BM25 natural recall: query='{query[:50]}...', topk={topk}"
        )
        
        try:
            result = self.lucene_index.search_natural(query, fields, topk)
            
            hits = []
            for hit in result["hits"]:
                hits.append({
                    "chunk_id": hit["chunk_id"],
                    "score": hit["score"],
                    "fields": hit.get("fields", {})
                })
            
            logger.info(
                f"BM25 natural recall completed: {result['total_hits']} total hits, "
                f"{len(hits)} results returned"
            )
            
            return hits
            
        except Exception as e:
            logger.error(f"BM25 natural recall failed: {e}")
            raise
    
    def recall_bm25_composite(
        self,
        conditions: List[Dict[str, Any]],
        topk: int = 10
    ) -> List[Dict[str, Any]]:
        """
        BM25召回（JSON组合版）
        
        Args:
            conditions: 查询条件列表，每个条件包含：
                - type: 条件类型（"TEXT", "FILTER", "RANGE"）
                - 其他参数根据类型不同而不同
            topk: 返回结果数量（默认10）
            
        Returns:
            List[Dict[str, Any]]: 检索结果列表，每个结果包含：
                - chunk_id: 切片ID
                - score: BM25分数
                - fields: 存储字段
                
        Raises:
            ValueError: 当参数无效时抛出
        """
        if not conditions or not isinstance(conditions, list):
            raise ValueError(
                f"conditions must be a non-empty list, got {conditions}"
            )
        
        if topk <= 0:
            raise ValueError(f"topk must be positive, got {topk}")
        
        logger.info(
            f"BM25 composite recall: {len(conditions)} conditions, topk={topk}"
        )
        
        try:
            result = self.lucene_index.search_composite(conditions, topk)
            
            hits = []
            for hit in result["hits"]:
                hits.append({
                    "chunk_id": hit["chunk_id"],
                    "score": hit["score"],
                    "fields": hit.get("fields", {})
                })
            
            logger.info(
                f"BM25 composite recall completed: {result['total_hits']} total hits, "
                f"{len(hits)} results returned"
            )
            
            return hits
            
        except Exception as e:
            logger.error(f"BM25 composite recall failed: {e}")
            raise
    
    def recall_hybrid(
        self,
        query: str,
        topk: int = 10,
        vector_threshold: float = 0.0,
        bm25_fields: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        混合召回（向量 + BM25）
            
        Args:
            query: 查询文本
            topk: 每种召回方式返回的结果数量（默认10）
            vector_threshold: 向量召回的相似度阈值（默认0.0）
            bm25_fields: BM25搜索字段列表（默认["content", "title"]）
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: 包含两种召回结果的字典：
                - vector: 向量召回结果
                - bm25: BM25召回结果
        """
        logger.info(f"Hybrid recall: query='{query[:50]}...', topk={topk}")
        
        results = {}
        
        try:
            results["vector"] = self.recall_vector(query, topk, vector_threshold)
        except Exception as e:
            logger.warning(f"Vector recall failed in hybrid mode: {e}")
            results["vector"] = []
        
        try:
            results["bm25"] = self.recall_bm25_natural(query, topk, bm25_fields)
        except Exception as e:
            logger.warning(f"BM25 recall failed in hybrid mode: {e}")
            results["bm25"] = []
        
        logger.info(
            f"Hybrid recall completed: vector={len(results['vector'])}, "
            f"bm25={len(results['bm25'])}"
        )
        
        return results

    # TODO: 实现JSON组合版召回的混合召回
    # TODO: 合并向量召回和BM25召回的结果
    
    def close(self) -> None:
        """
        关闭所有资源
        """
        if self.lucene_index:
            self.lucene_index.close()
            logger.info("Lucene index closed")
        
        logger.info("Recaller closed")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        获取索引信息
        
        Returns:
            Dict[str, Any]: 索引信息字典
        """
        info = {
            "faiss_index_path": self.faiss_index_path,
            "lucene_index_path": self.lucene_index_path,
            "language": self.language,
            "embedding_dimension": self.embedding.get_embedding_dimension()
        }
        
        if self.faiss_index:
            info["faiss_vector_count"] = self.faiss_index.get_vector_count()
        
        if self.lucene_index:
            try:
                info["lucene_doc_count"] = self.lucene_index.get_searcher_doc_count()
            except Exception:
                pass
        
        return info
