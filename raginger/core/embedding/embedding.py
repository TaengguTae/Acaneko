"""
文本向量化模块
使用sentence-transformers库实现文本到向量的转换
"""

from typing import Union, List, Optional
import json
import os
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger


class Embedding:
    """
    文本向量化类
    
    使用sentence-transformers库加载预训练模型，将文本转换为向量表示。
    支持单个文本和批量文本的向量化处理，并根据content_type自动应用相应的prefix。
    
    Attributes:
        model_path: 模型路径
        model: SentenceTransformer模型实例
        prefix: 从配置文件读取的prefix字典
        embedding_dim: 向量维度
    """
    
    def __init__(self, model_path: str):
        """
        初始化Embedding类
        
        Args:
            model_path: 模型路径，可以是本地路径或HuggingFace模型名称
            
        Raises:
            ValueError: 当模型路径无效时抛出
            FileNotFoundError: 当配置文件不存在时抛出
        """
        if not model_path or not isinstance(model_path, str):
            raise ValueError(
                f"model_path must be a non-empty string, got {model_path}"
            )
        
        self.model_path = model_path
        self.prefix = self._load_prefix_config()
        
        logger.info(f"Loading embedding model from: {model_path}")
        try:
            self.model = SentenceTransformer(model_path)
            self.embedding_dim = self.model.get_embedding_dimension()
            logger.success(
                f"Model loaded successfully, embedding dimension: {self.embedding_dim}"
            )
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            raise
    
    def _load_prefix_config(self) -> dict:
        """
        从模型路径下加载prefix配置
        
        Returns:
            dict: prefix配置字典
            
        Raises:
            FileNotFoundError: 当配置文件不存在时抛出
        """
        config_file = os.path.join(self.model_path, "config_sentence_transformers.json")
        
        if not os.path.exists(config_file):
            logger.warning(
                f"Config file not found: {config_file}, using empty prefix"
            )
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            prefix_config = {}
            for prompt_name, prompt in config['prompts'].items():
                prefix_config[prompt_name] = prompt

            logger.info(f"Loaded prefix config: {prefix_config}")
            return prefix_config
            
        except Exception as e:
            logger.error(f"Failed to load prefix config: {e}")
            return {}
    
    def _apply_prefix(
        self,
        text: Union[str, List[str]],
        content_type: str
    ) -> Union[str, List[str]]:
        """
        根据content_type应用相应的prefix
        
        Args:
            text: 输入文本或文本列表
            content_type: 内容类型，"query"或"document"
            
        Returns:
            Union[str, List[str]]: 应用prefix后的文本或文本列表
            
        Raises:
            ValueError: 当content_type无效时抛出
        """
        if content_type not in ["query", "document"]:
            raise ValueError(
                f"content_type must be 'query' or 'document', got '{content_type}'"
            )
        
        prefix = self.prefix.get(content_type, "")
        
        if isinstance(text, str):
            return f"{prefix}{text}" if prefix else text
        elif isinstance(text, list):
            return [f"{prefix}{t}" if prefix else t for t in text]
        else:
            raise ValueError(
                f"text must be str or list, got {type(text)}"
            )
    
    def get_embedding(
        self,
        text: Union[str, List[str]],
        content_type: str = "document"
    ) -> np.ndarray:
        """
        获取文本的向量表示
        
        Args:
            text: 输入文本，可以是单个字符串或字符串列表
            content_type: 内容类型，"query"或"document"（默认"document"）
            
        Returns:
            np.ndarray: 文本向量，形状为 (dimension,) 或 (n, dimension)
            
        Raises:
            ValueError: 当输入参数无效时抛出
            
        Examples:
            >>> embedding = Embedding("path/to/model")
            >>> # 单个文本
            >>> vec = embedding.get_embedding("这是一个查询", content_type="query")
            >>> print(vec.shape)  # (dimension,)
            
            >>> # 批量文本
            >>> texts = ["文档1", "文档2", "文档3"]
            >>> vecs = embedding.get_embedding(texts, content_type="document")
            >>> print(vecs.shape)  # (3, dimension)
        """
        if not text:
            raise ValueError("text cannot be empty")
        
        if not isinstance(text, (str, list)):
            raise ValueError(
                f"text must be str or list, got {type(text)}"
            )
        
        if isinstance(text, list) and not all(isinstance(t, str) for t in text):
            raise ValueError("All elements in text list must be strings")
        
        logger.debug(
            f"Generating embedding for {len(text) if isinstance(text, list) else 1} "
            f"text(s), content_type: {content_type}"
        )
        
        processed_text = self._apply_prefix(text, content_type)
        
        try:
            embeddings = self.model.encode(
                processed_text,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True
            )
            
            logger.debug(
                f"Embedding generated successfully, shape: {embeddings.shape}"
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """
        获取向量维度
        
        Returns:
            int: 向量维度
        """
        return self.embedding_dim
    
    def get_model_info(self) -> dict:
        """
        获取模型信息
        
        Returns:
            dict: 包含模型信息的字典
        """
        return {
            "model_path": self.model_path,
            "embedding_dimension": self.embedding_dim,
            "prefix_config": self.prefix,
            "max_seq_length": self.model.max_seq_length
        }
