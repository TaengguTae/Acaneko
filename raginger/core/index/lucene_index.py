"""
Lucene索引模块
通过JPype集成Acaneko-Lucene JAR包实现全文检索功能
"""

from typing import List, Dict, Optional, Any, Union
import os
import json
from pathlib import Path
from enum import Enum

from loguru import logger

try:
    import jpype
    import jpype.imports
    JPYPE_AVAILABLE = True
except ImportError:
    JPYPE_AVAILABLE = False
    logger.warning("JPype is not installed. LuceneIndex will not be available.")


class FieldType(Enum):
    """字段类型枚举"""
    ID = "ID"
    TEXT = "TEXT"
    STORED_ONLY = "STORED_ONLY"
    LONG = "LONG"
    INT = "INT"


class LuceneIndex:
    """
    Lucene索引类
    
    通过JPype集成Acaneko-Lucene JAR包，实现基于Lucene的全文检索功能。
    支持索引构建、自然语言查询和结构化JSON查询。
    
    Attributes:
        index_path: 索引文件路径
        language: 语言代码（如"zh"表示中文）
        _jvm_started: JVM是否已启动
        _index_creator: IndexCreator实例
        _searcher: Searcher实例
    """
    
    _jvm_started = False
    _jar_path = None
    
    @classmethod
    def set_jar_path(cls, jar_path: str) -> None:
        """
        设置JAR包路径
        
        Args:
            jar_path: JAR包的绝对路径
        """
        cls._jar_path = jar_path
        logger.info(f"JAR path set to: {jar_path}")
    
    @classmethod
    def _start_jvm(cls) -> None:
        """
        启动JVM
        
        Raises:
            RuntimeError: 当JPype不可用或JAR包路径未设置时抛出
            Exception: 当JVM启动失败时抛出
        """
        if not JPYPE_AVAILABLE:
            raise RuntimeError(
                "JPype is not installed. Please install it with: pip install jpype1"
            )
        
        if cls._jvm_started:
            logger.debug("JVM already started")
            return
        
        if not cls._jar_path:
            default_jar_path = os.path.join(
                os.path.dirname(__file__),
                "libs",
                "Acaneko-Lucene9.12.3-v1.0.jar"
            )
            if os.path.exists(default_jar_path):
                cls._jar_path = default_jar_path
            else:
                raise RuntimeError(
                    "JAR path not set. Please call LuceneIndex.set_jar_path() first "
                    "or ensure the JAR file exists in the libs directory."
                )
        
        if not os.path.exists(cls._jar_path):
            raise FileNotFoundError(f"JAR file not found: {cls._jar_path}")
        
        logger.info(f"Starting JVM with JAR: {cls._jar_path}")
        
        try:
            jpype.startJVM(classpath=[cls._jar_path])
            cls._jvm_started = True
            logger.success("JVM started successfully")
        except Exception as e:
            logger.error(f"Failed to start JVM: {e}")
            raise
    
    def __init__(self, index_path: str, language: str = "zh"):
        """
        初始化LuceneIndex类
        
        Args:
            index_path: 索引文件路径
            language: 语言代码（默认"zh"表示中文）
            
        Raises:
            ValueError: 当参数无效时抛出
            RuntimeError: 当JVM启动失败时抛出
        """
        if not index_path or not isinstance(index_path, str):
            raise ValueError(
                f"index_path must be a non-empty string, got {index_path}"
            )
        
        if not language or not isinstance(language, str):
            raise ValueError(
                f"language must be a non-empty string, got {language}"
            )
        
        self.index_path = index_path
        self.language = language
        self._index_creator = None
        self._searcher = None
        
        logger.info(f"Initializing LuceneIndex: path={index_path}, language={language}")
        
        self._start_jvm()
        
        try:
            from org.acaneko import IndexCreator, Searcher
            self._IndexCreator = IndexCreator
            self._Searcher = Searcher
            self._FieldType = IndexCreator.FieldType
            self._FieldConfig = IndexCreator.FieldConfig
            self._QueryCondition = Searcher.QueryCondition
            self._Occur = Searcher.QueryCondition.Occur
            
            logger.success("LuceneIndex initialized successfully")
        except Exception as e:
            logger.error(f"Failed to import Java classes: {e}")
            raise RuntimeError(f"Failed to import Java classes: {e}")
    
    def _get_java_list(self) -> Any:
        """获取Java ArrayList实例"""
        return jpype.java.util.ArrayList()
    
    def _get_java_map(self) -> Any:
        """获取Java LinkedHashMap实例"""
        return jpype.java.util.LinkedHashMap()
    
    def _get_java_long(self, value: int) -> Any:
        """获取Java Long实例"""
        return jpype.java.lang.Long(value)
    
    def _get_java_arrays(self) -> Any:
        """获取Java Arrays类"""
        return jpype.java.util.Arrays
    
    def _convert_field_type(self, field_type: Union[str, FieldType]) -> Any:
        """
        转换字段类型为Java FieldType
        
        Args:
            field_type: 字段类型（字符串或枚举）
            
        Returns:
            Java FieldType枚举值
        """
        if isinstance(field_type, str):
            field_type = FieldType(field_type.upper())
        
        type_mapping = {
            FieldType.ID: self._FieldType.ID,
            FieldType.TEXT: self._FieldType.TEXT,
            FieldType.STORED_ONLY: self._FieldType.STORED_ONLY,
            FieldType.LONG: self._FieldType.LONG,
            FieldType.INT: self._FieldType.INT
        }
        
        return type_mapping.get(field_type, self._FieldType.TEXT)
    
    def _convert_occur(self, occur: str) -> Any:
        """
        转换Occur字符串为Java枚举
        
        Args:
            occur: Occur字符串（"MUST", "SHOULD", "FILTER"）
            
        Returns:
            Java Occur枚举值
        """
        occur_mapping = {
            "MUST": self._Occur.MUST,
            "SHOULD": self._Occur.SHOULD,
            "FILTER": self._Occur.FILTER
        }
        
        return occur_mapping.get(occur.upper(), self._Occur.SHOULD)
    
    def create_index_creator(self) -> None:
        """
        创建IndexCreator实例
        
        用于构建索引，每次调用会清空旧索引
        """
        try:
            self._index_creator = self._IndexCreator(self.index_path, self.language)
            logger.info(f"IndexCreator created for path: {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to create IndexCreator: {e}")
            raise
    
    def create_searcher(self) -> None:
        """
        创建Searcher实例
        
        用于执行检索
        """
        try:
            self._searcher = self._Searcher(self.index_path, self.language)
            logger.info(f"Searcher created for path: {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to create Searcher: {e}")
            raise
    
    def add_document(
        self,
        fields: List[Dict[str, Any]]
    ) -> None:
        """
        添加单个文档到索引
        
        Args:
            fields: 字段配置列表，每个元素包含:
                - name: 字段名称
                - value: 字段值
                - type: 字段类型（"ID", "TEXT", "STORED_ONLY", "LONG", "INT"）
                - store: 是否存储（默认True）
                
        Raises:
            ValueError: 当IndexCreator未初始化或参数无效时抛出
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        if not fields:
            raise ValueError("fields cannot be empty")
        
        logger.debug(f"Adding document with {len(fields)} fields")
        
        try:
            field_list = self._get_java_list()
            
            for field in fields:
                name = field.get("name")
                value = field.get("value")
                field_type = field.get("type", "TEXT")
                store = field.get("store", True)
                
                if not name:
                    raise ValueError("Field name is required")
                
                java_field_type = self._convert_field_type(field_type)
                
                if field_type in [FieldType.LONG, "LONG"] and isinstance(value, int):
                    value = self._get_java_long(value)
                
                field_config = self._FieldConfig(name, value, java_field_type, store)
                field_list.add(field_config)
            
            self._index_creator.addDocument(field_list)
            logger.debug("Document added successfully")
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    def add_document_from_map(
        self,
        fields: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        使用Map方式添加单个文档
        
        Args:
            fields: 字段配置字典，键为字段名，值为字段配置
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        if not fields:
            raise ValueError("fields cannot be empty")
        
        logger.debug(f"Adding document from map with {len(fields)} fields")
        
        try:
            field_map = self._get_java_map()
            
            for name, config in fields.items():
                value = config.get("value")
                field_type = config.get("type", "TEXT")
                store = config.get("store", True)
                
                java_field_type = self._convert_field_type(field_type)
                
                if field_type in [FieldType.LONG, "LONG"] and isinstance(value, int):
                    value = self._get_java_long(value)
                
                field_config = self._FieldConfig(name, value, java_field_type, store)
                field_map.put(name, field_config)
            
            self._index_creator.addDocument(field_map)
            logger.debug("Document added from map successfully")
            
        except Exception as e:
            logger.error(f"Failed to add document from map: {e}")
            raise
    
    def add_documents_batch(
        self,
        documents: List[List[Dict[str, Any]]]
    ) -> None:
        """
        批量添加文档
        
        Args:
            documents: 文档列表，每个文档是字段配置列表
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        if not documents:
            raise ValueError("documents cannot be empty")
        
        logger.info(f"Adding {len(documents)} documents in batch")
        
        try:
            batch_list = self._get_java_list()
            
            for doc_fields in documents:
                field_list = self._get_java_list()
                
                for field in doc_fields:
                    name = field.get("name")
                    value = field.get("value")
                    field_type = field.get("type", "TEXT")
                    store = field.get("store", True)
                    
                    java_field_type = self._convert_field_type(field_type)
                    
                    if field_type in [FieldType.LONG, "LONG"] and isinstance(value, int):
                        value = self._get_java_long(value)
                    
                    field_config = self._FieldConfig(name, value, java_field_type, store)
                    field_list.add(field_config)
                
                batch_list.add(field_list)
            
            self._index_creator.addDocuments(batch_list)
            logger.info(f"Batch add completed: {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to add documents batch: {e}")
            raise
    
    def add_documents_from_maps(
        self,
        documents: List[Dict[str, Dict[str, Any]]]
    ) -> None:
        """
        使用Map方式批量添加文档
        
        Args:
            documents: 文档列表，每个文档是字段配置字典
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        if not documents:
            raise ValueError("documents cannot be empty")
        
        logger.info(f"Adding {len(documents)} documents from maps in batch")
        
        try:
            batch_list = self._get_java_list()
            
            for doc_fields in documents:
                field_map = self._get_java_map()
                
                for name, config in doc_fields.items():
                    value = config.get("value")
                    field_type = config.get("type", "TEXT")
                    store = config.get("store", True)
                    
                    java_field_type = self._convert_field_type(field_type)
                    
                    if field_type in [FieldType.LONG, "LONG"] and isinstance(value, int):
                        value = self._get_java_long(value)
                    
                    field_config = self._FieldConfig(name, value, java_field_type, store)
                    field_map.put(name, field_config)
                
                batch_list.add(field_map)
            
            self._index_creator.addDocumentsFromMaps(batch_list)
            logger.info(f"Batch add from maps completed: {len(documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to add documents from maps: {e}")
            raise
    
    def commit(self) -> None:
        """
        提交索引更改到磁盘
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        try:
            self._index_creator.commit()
            logger.info("Index committed successfully")
        except Exception as e:
            logger.error(f"Failed to commit index: {e}")
            raise
    
    def get_doc_count(self) -> int:
        """
        获取已提交的文档数量
        
        Returns:
            int: 文档数量
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        return self._index_creator.getDocCount()
    
    def get_pending_doc_count(self) -> int:
        """
        获取待提交的文档数量
        
        Returns:
            int: 待提交文档数量
        """
        if self._index_creator is None:
            raise ValueError("IndexCreator not initialized. Call create_index_creator() first.")
        
        return self._index_creator.getPendingDocCount()
    
    def close_index_creator(self) -> None:
        """
        关闭IndexCreator，释放资源
        """
        if self._index_creator is not None:
            try:
                self._index_creator.close()
                logger.info("IndexCreator closed")
            except Exception as e:
                logger.error(f"Failed to close IndexCreator: {e}")
            finally:
                self._index_creator = None
    
    def _convert_search_result(self, result: Any) -> Dict[str, Any]:
        """
        转换Java搜索结果为Python字典
        
        Args:
            result: Java SearchResult对象
            
        Returns:
            Dict[str, Any]: Python格式的检索结果
        """
        hits = []
        for hit in result.getHits():
            hit_dict = {
                "chunk_id": hit.getChunkId(),
                "score": hit.getScore(),
                "fields": {}
            }
            
            fields = hit.getFields()
            if fields:
                for key in fields.keySet():
                    hit_dict["fields"][key] = fields.get(key)
            
            hits.append(hit_dict)
        
        return {
            "total_hits": result.getTotalHits(),
            "hits": hits
        }
    
    def search(
        self,
        query: str,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        执行检索（统一入口）
        
        Java的search方法会自动判断查询类型：
        - 如果query以{或[开头，视为JSON查询
        - 否则视为自然语言查询
        
        Args:
            query: 查询字符串（自然语言或JSON格式）
            top_n: 返回结果数量
            
        Returns:
            Dict[str, Any]: 检索结果，包含:
                - total_hits: 总命中数
                - hits: 命中结果列表
        """
        if self._searcher is None:
            self.create_searcher()
        
        if not query:
            raise ValueError("query cannot be empty")
        
        if top_n <= 0:
            raise ValueError(f"top_n must be positive, got {top_n}")
        
        logger.info(f"Searching with query, top_n={top_n}")
        
        try:
            result = self._searcher.search(query, top_n)
            result_dict = self._convert_search_result(result)
            logger.info(f"Search completed: {result_dict['total_hits']} hits found")
            return result_dict
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def search_natural(
        self,
        query_text: str,
        fields: Optional[List[str]] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        执行自然语言查询（指定搜索字段）
        
        Args:
            query_text: 自然语言查询文本
            fields: 搜索字段列表（默认["content", "title"]）
            top_n: 返回结果数量
            
        Returns:
            Dict[str, Any]: 检索结果
        """
        if self._searcher is None:
            self.create_searcher()
        
        if not query_text:
            raise ValueError("query_text cannot be empty")
        
        if fields is None:
            fields = ["content", "title"]
        
        logger.info(f"Natural language search: '{query_text[:50]}...', fields={fields}")
        
        try:
            java_fields = self._get_java_list()
            for field in fields:
                java_fields.add(field)
            
            result = self._searcher.searchNatural(query_text, java_fields, top_n)
            result_dict = self._convert_search_result(result)
            logger.info(f"Natural search completed: {result_dict['total_hits']} hits found")
            return result_dict
        except Exception as e:
            logger.error(f"Natural search failed: {e}")
            raise
    
    def search_composite(
        self,
        conditions: List[Dict[str, Any]],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        执行结构化组合查询
        
        Args:
            conditions: 查询条件列表，每个条件包含:
                - type: 条件类型（"TEXT", "FILTER", "RANGE"）
                - 其他参数根据类型不同而不同
            top_n: 返回结果数量
            
        Returns:
            Dict[str, Any]: 检索结果
        """
        if self._searcher is None:
            self.create_searcher()
        
        if not conditions:
            raise ValueError("conditions cannot be empty")
        
        logger.info(f"Composite search with {len(conditions)} conditions")
        
        try:
            java_conditions = self._get_java_list()
            arrays = self._get_java_arrays()
            
            for cond in conditions:
                query_cond = self._build_query_condition(cond, arrays)
                java_conditions.add(query_cond)
            
            result = self._searcher.searchComposite(java_conditions, top_n)
            result_dict = self._convert_search_result(result)
            logger.info(f"Composite search completed: {result_dict['total_hits']} hits found")
            return result_dict
        except Exception as e:
            logger.error(f"Composite search failed: {e}")
            raise
    
    def _build_query_condition(self, cond: Dict[str, Any], arrays: Any) -> Any:
        """
        构建Java QueryCondition对象
        
        Args:
            cond: Python字典格式的查询条件
            arrays: Java Arrays类
            
        Returns:
            Java QueryCondition对象
        """
        cond_type = cond.get("type", "TEXT")
        
        if cond_type == "TEXT":
            return self._QueryCondition(
                arrays.asList(cond.get("fields", ["content"])),
                arrays.asList(cond.get("keywords", [])),
                self._convert_occur(cond.get("occur", "SHOULD"))
            )
        elif cond_type == "FILTER":
            return self._QueryCondition(
                cond.get("field"),
                arrays.asList(cond.get("values", []))
            )
        elif cond_type == "RANGE":
            start = cond.get("start")
            end = cond.get("end")
            return self._QueryCondition(
                cond.get("field"),
                self._get_java_long(start) if start is not None else None,
                self._get_java_long(end) if end is not None else None,
                self._convert_occur(cond.get("occur", "FILTER"))
            )
        else:
            raise ValueError(f"Unknown condition type: {cond_type}")
    
    def get_searcher_doc_count(self) -> int:
        """
        获取Searcher视角的文档数量
        
        Returns:
            int: 文档数量
        """
        if self._searcher is None:
            self.create_searcher()
        
        return self._searcher.getDocCount()
    
    def close_searcher(self) -> None:
        """
        关闭Searcher，释放资源
        """
        if self._searcher is not None:
            try:
                self._searcher.close()
                logger.info("Searcher closed")
            except Exception as e:
                logger.error(f"Failed to close Searcher: {e}")
            finally:
                self._searcher = None
    
    def close(self) -> None:
        """
        关闭所有资源
        """
        self.close_index_creator()
        self.close_searcher()
        logger.info("All resources closed")
    
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
            Dict[str, Any]: 索引信息
        """
        info = {
            "index_path": self.index_path,
            "language": self.language,
            "jvm_started": self._jvm_started,
            "jar_path": self._jar_path
        }
        
        if self._index_creator is not None:
            info["doc_count"] = self.get_doc_count()
            info["pending_doc_count"] = self.get_pending_doc_count()
        
        if self._searcher is not None:
            info["searcher_doc_count"] = self.get_searcher_doc_count()
        
        return info
