"""
向量索引模块
使用FAISS库实现高效的向量索引和检索功能
"""

from typing import List, Tuple, Dict, Optional, Any
import numpy as np
import faiss
import os
import pickle
from pathlib import Path

from loguru import logger


class FaissIndex:
    """
    FAISS向量索引类
    
    使用FAISS库实现高效的向量索引、检索和管理功能。
    支持向量的批量添加、相似度查询、索引持久化等操作。
    
    Attributes:
        dimension: 向量维度
        index: FAISS索引实例
        id_mapping: 向量ID到内部索引的映射字典
        _vector_count: 已添加的向量数量
    """
    
    def __init__(self, dimension: int):
        """
        初始化FAISS索引
        
        Args:
            dimension: 向量维度，必须为正整数
            
        Raises:
            ValueError: 当维度参数无效时抛出
        """
        if not isinstance(dimension, int) or dimension <= 0:
            raise ValueError(
                f"dimension must be a positive integer, got {dimension}"
            )
        
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.id_mapping: Dict[int, str] = {}
        self._reverse_mapping: Dict[str, int] = {}
        self._vector_count = 0
        
        logger.info(
            f"FaissIndex initialized with dimension={dimension}, "
            f"index_type=IndexFlatIP"
        )
    
    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """
        对向量进行L2归一化
        
        Args:
            vectors: 输入向量数组，形状为 (n, dimension)
            
        Returns:
            np.ndarray: 归一化后的向量数组
            
        Raises:
            ValueError: 当向量数组为空或维度不匹配时抛出
        """
        if vectors.size == 0:
            raise ValueError("Vectors array is empty")
        
        if vectors.ndim != 2:
            raise ValueError(
                f"Vectors must be 2D array, got {vectors.ndim}D"
            )
        
        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {self.dimension}, "
                f"got {vectors.shape[1]}"
            )
        
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = vectors / norms
        
        return normalized.astype('float32')
    
    def _validate_vector_ids(self, vector_ids: List[str]) -> None:
        """
        验证向量ID列表
        
        Args:
            vector_ids: 向量ID列表
            
        Raises:
            ValueError: 当ID列表无效或存在重复时抛出
        """
        if not vector_ids:
            raise ValueError("Vector IDs list cannot be empty")
        
        if not all(isinstance(vid, str) for vid in vector_ids):
            raise ValueError("All vector IDs must be strings")
        
        duplicate_ids = set(vector_ids) & set(self._reverse_mapping.keys())
        if duplicate_ids:
            raise ValueError(
                f"Duplicate vector IDs found: {duplicate_ids}"
            )
    
    def add_vectors(
        self,
        vectors: np.ndarray,
        vector_ids: List[str]
    ) -> None:
        """
        批量添加向量到索引
        
        Args:
            vectors: 向量数组，形状为 (n, dimension)
            vector_ids: 向量ID列表，长度必须与向量数量一致
            
        Raises:
            ValueError: 当输入数据无效时抛出
        """
        if not isinstance(vectors, np.ndarray):
            raise ValueError(
                f"Vectors must be numpy array, got {type(vectors)}"
            )
        
        if len(vectors) != len(vector_ids):
            raise ValueError(
                f"Number of vectors ({len(vectors)}) must match "
                f"number of IDs ({len(vector_ids)})"
            )
        
        self._validate_vector_ids(vector_ids)
        
        normalized_vectors = self._normalize_vectors(vectors)
        
        start_idx = self._vector_count
        self.index.add(normalized_vectors)
        
        for i, vector_id in enumerate(vector_ids):
            internal_idx = start_idx + i
            self.id_mapping[internal_idx] = vector_id
            self._reverse_mapping[vector_id] = internal_idx
        
        self._vector_count += len(vectors)
        
        logger.info(
            f"Added {len(vectors)} vectors to index, "
            f"total vectors: {self._vector_count}"
        )
    
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        查询最相似的向量
        
        Args:
            query_vector: 查询向量，形状为 (dimension,) 或 (1, dimension)
            top_k: 返回的最相似向量数量
            
        Returns:
            List[Tuple[str, float]]: 包含 (vector_id, similarity_score) 的列表
            
        Raises:
            ValueError: 当输入数据无效时抛出
        """
        if not isinstance(query_vector, np.ndarray):
            raise ValueError(
                f"Query vector must be numpy array, got {type(query_vector)}"
            )
        
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        elif query_vector.ndim != 2 or query_vector.shape[0] != 1:
            raise ValueError(
                "Query vector must be 1D or 2D with shape (1, dimension)"
            )
        
        if top_k <= 0:
            raise ValueError(f"top_k must be positive, got {top_k}")
        
        if self._vector_count == 0:
            logger.warning("Index is empty, returning empty results")
            return []
        
        normalized_query = self._normalize_vectors(query_vector)
        
        actual_k = min(top_k, self._vector_count)
        scores, indices = self.index.search(normalized_query, actual_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                vector_id = self.id_mapping.get(idx)
                if vector_id is not None:
                    results.append((vector_id, float(score)))
        
        logger.debug(
            f"Search completed: query returned {len(results)} results"
        )
        
        return results
    
    def save_index(self, file_path: str) -> None:
        """
        保存索引到磁盘
        
        Args:
            file_path: 保存路径（不包含扩展名）
            
        Raises:
            IOError: 当保存失败时抛出
        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            index_file = f"{file_path}/.index"
            faiss.write_index(self.index, index_file)
            
            metadata_file = f"{file_path}/.metadata"
            metadata = {
                'dimension': self.dimension,
                'id_mapping': self.id_mapping,
                'reverse_mapping': self._reverse_mapping,
                'vector_count': self._vector_count
            }
            
            with open(metadata_file, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(
                f"Index saved successfully to {file_path}, "
                f"total vectors: {self._vector_count}"
            )
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise IOError(f"Failed to save index: {e}")
    
    @classmethod
    def load_index(cls, file_path: str) -> 'FaissIndex':
        """
        从磁盘加载索引
        
        Args:
            file_path: 索引文件路径（不包含扩展名）
            
        Returns:
            FaissIndex: 加载的索引实例
            
        Raises:
            IOError: 当加载失败时抛出
        """
        try:
            index_file = f"{file_path}/.index"
            metadata_file = f"{file_path}/.metadata"
            
            if not os.path.exists(index_file):
                raise FileNotFoundError(f"Index file not found: {index_file}")
            
            if not os.path.exists(metadata_file):
                raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
            
            index = faiss.read_index(index_file)
            
            with open(metadata_file, 'rb') as f:
                metadata = pickle.load(f)
            
            instance = cls(metadata['dimension'])
            instance.index = index
            instance.id_mapping = metadata['id_mapping']
            instance._reverse_mapping = metadata['reverse_mapping']
            instance._vector_count = metadata['vector_count']
            
            logger.info(
                f"Index loaded successfully from {file_path}, "
                f"total vectors: {instance._vector_count}"
            )
            
            return instance
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            raise IOError(f"Failed to load index: {e}")
    
    def get_vector_count(self) -> int:
        """
        获取索引中的向量数量
        
        Returns:
            int: 向量数量
        """
        return self._vector_count
    
    def get_dimension(self) -> int:
        """
        获取向量维度
        
        Returns:
            int: 向量维度
        """
        return self.dimension
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        获取索引的详细信息
        
        Returns:
            Dict[str, Any]: 包含索引信息的字典
        """
        return {
            'dimension': self.dimension,
            'vector_count': self._vector_count,
            'index_type': 'IndexFlatIP',
            'is_trained': self.index.is_trained,
            'ntotal': self.index.ntotal
        }
    
    def clear_index(self) -> None:
        """
        清空索引中的所有向量
        """
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_mapping.clear()
        self._reverse_mapping.clear()
        self._vector_count = 0
        
        logger.info("Index cleared")
    
    def remove_vector(self, vector_id: str) -> bool:
        """
        移除指定ID的向量（注意：FAISS不支持直接删除，此方法仅从映射中移除）
        
        Args:
            vector_id: 要移除的向量ID
            
        Returns:
            bool: 是否成功移除
            
        Note:
            此方法仅从ID映射中移除，不会从FAISS索引中实际删除向量。
            如需完全重建索引，请使用 clear_index() 后重新添加向量。
        """
        if vector_id not in self._reverse_mapping:
            logger.warning(f"Vector ID {vector_id} not found in index")
            return False
        
        internal_idx = self._reverse_mapping[vector_id]
        del self.id_mapping[internal_idx]
        del self._reverse_mapping[vector_id]
        
        logger.info(f"Vector {vector_id} removed from mapping")
        return True
    
    def get_vector_id(self, internal_index: int) -> Optional[str]:
        """
        根据内部索引获取向量ID
        
        Args:
            internal_index: 内部索引
            
        Returns:
            Optional[str]: 向量ID，如果不存在则返回None
        """
        return self.id_mapping.get(internal_index)
    
    def has_vector(self, vector_id: str) -> bool:
        """
        检查向量ID是否存在于索引中
        
        Args:
            vector_id: 向量ID
            
        Returns:
            bool: 是否存在
        """
        return vector_id in self._reverse_mapping
