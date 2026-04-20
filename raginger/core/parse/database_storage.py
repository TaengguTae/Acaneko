"""
数据库存储模块
使用SQLite实现切片信息的持久化存储
"""

from typing import Dict, List, Optional, Any
import sqlite3
from pathlib import Path

from loguru import logger


class DatabaseStorage:
    """
    数据库存储类
    
    使用SQLite数据库引擎实现切片信息的持久化存储。
    提供数据插入和查询功能。
    
    Attributes:
        db_path: 数据库文件路径
        connection: SQLite数据库连接
    """
    
    def __init__(self, db_path: str):
        """
        初始化数据库存储类
        
        Args:
            db_path: 数据库文件路径
            
        Raises:
            ValueError: 当db_path无效时抛出
            sqlite3.Error: 当数据库连接失败时抛出
        """
        if not db_path or not isinstance(db_path, str):
            raise ValueError(
                f"db_path must be a non-empty string, got {db_path}"
            )
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
        logger.info(f"Initializing DatabaseStorage with path: {db_path}")
        
        self._connect()
        self._create_table()
        
        logger.success("DatabaseStorage initialized successfully")
    
    def _connect(self) -> None:
        """
        建立数据库连接
        
        Raises:
            sqlite3.Error: 当连接失败时抛出
        """
        try:
            db_dir = Path(self.db_path).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created database directory: {db_dir}")
            
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            logger.info(f"Database connection established: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _create_table(self) -> None:
        """
        创建数据表
        
        表结构：
        - chunk_id: TEXT PRIMARY KEY
        - doc_id: TEXT
        - vector_id: TEXT
        - chunk_position: INTEGER
        - title: TEXT
        - content: TEXT
        - file_type: TEXT
        - file_src: TEXT
        - vertical: TEXT
        - timestamp: INTEGER
        
        Raises:
            sqlite3.Error: 当创建表失败时抛出
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            doc_id TEXT NOT NULL,
            vector_id TEXT,
            chunk_position INTEGER,
            title TEXT,
            content TEXT,
            file_type TEXT,
            file_src TEXT,
            vertical TEXT,
            timestamp INTEGER
        )
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            self.connection.commit()
            
            logger.info("Table 'chunks' created or already exists")
            
        except sqlite3.Error as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def insert_chunk(self, chunk_data: Dict[str, Any]) -> None:
        """
        插入切片数据
        
        Args:
            chunk_data: 包含切片数据的字典，必须包含以下字段：
                - chunk_id: 切片ID（主键）
                - doc_id: 文档ID
                - vector_id: 向量ID
                - chunk_position: 切片位置
                - title: 标题
                - content: 内容
                - file_type: 文件类型
                - file_src: 文件来源
                - vertical: 垂直分类
                - timestamp: 时间戳
                
        Raises:
            ValueError: 当chunk_data无效时抛出
            sqlite3.IntegrityError: 当chunk_id已存在时抛出
            sqlite3.Error: 当插入失败时抛出
        """
        if not chunk_data or not isinstance(chunk_data, dict):
            raise ValueError(
                f"chunk_data must be a non-empty dictionary, got {chunk_data}"
            )
        
        chunk_id = chunk_data.get("chunk_id")
        if not chunk_id:
            raise ValueError("chunk_id is required")
        
        logger.debug(f"Inserting chunk: {chunk_id}")
        
        insert_sql = """
        INSERT INTO chunks (
            chunk_id, doc_id, vector_id, chunk_position,
            title, content, file_type, file_src, vertical, timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                insert_sql,
                (
                    chunk_data.get("chunk_id"),
                    chunk_data.get("doc_id"),
                    chunk_data.get("vector_id"),
                    chunk_data.get("chunk_position"),
                    chunk_data.get("title"),
                    chunk_data.get("content"),
                    chunk_data.get("file_type"),
                    chunk_data.get("file_src"),
                    chunk_data.get("vertical"),
                    chunk_data.get("timestamp")
                )
            )
            self.connection.commit()
            
            logger.info(f"Chunk inserted successfully: {chunk_id}")
            
        except sqlite3.IntegrityError as e:
            logger.error(f"Chunk already exists: {chunk_id}, error: {e}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to insert chunk {chunk_id}: {e}")
            raise
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        根据chunk_id查询单条记录
        
        Args:
            chunk_id: 切片ID
            
        Returns:
            Optional[Dict[str, Any]]: 查询到的记录，未找到返回None
            
        Raises:
            ValueError: 当chunk_id无效时抛出
            sqlite3.Error: 当查询失败时抛出
        """
        if not chunk_id or not isinstance(chunk_id, str):
            raise ValueError(
                f"chunk_id must be a non-empty string, got {chunk_id}"
            )
        
        logger.debug(f"Querying chunk by id: {chunk_id}")
        
        query_sql = "SELECT * FROM chunks WHERE chunk_id = ?"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_sql, (chunk_id,))
            row = cursor.fetchone()
            
            if row:
                result = dict(row)
                logger.debug(f"Chunk found: {chunk_id}")
                return result
            else:
                logger.debug(f"Chunk not found: {chunk_id}")
                return None
                
        except sqlite3.Error as e:
            logger.error(f"Failed to query chunk {chunk_id}: {e}")
            raise
    
    def get_chunks_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        根据doc_id查询多条记录
        
        Args:
            doc_id: 文档ID
            
        Returns:
            List[Dict[str, Any]]: 查询到的记录列表
            
        Raises:
            ValueError: 当doc_id无效时抛出
            sqlite3.Error: 当查询失败时抛出
        """
        if not doc_id or not isinstance(doc_id, str):
            raise ValueError(
                f"doc_id must be a non-empty string, got {doc_id}"
            )
        
        logger.debug(f"Querying chunks by doc_id: {doc_id}")
        
        query_sql = "SELECT * FROM chunks WHERE doc_id = ? ORDER BY chunk_position"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_sql, (doc_id,))
            rows = cursor.fetchall()
            
            results = [dict(row) for row in rows]
            logger.debug(f"Found {len(results)} chunks for doc_id: {doc_id}")
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Failed to query chunks by doc_id {doc_id}: {e}")
            raise
    
    def get_chunks_by_vector_id(self, vector_id: str) -> List[Dict[str, Any]]:
        """
        根据vector_id查询记录
        
        Args:
            vector_id: 向量ID
            
        Returns:
            List[Dict[str, Any]]: 查询到的记录列表
            
        Raises:
            ValueError: 当vector_id无效时抛出
            sqlite3.Error: 当查询失败时抛出
        """
        if not vector_id or not isinstance(vector_id, str):
            raise ValueError(
                f"vector_id must be a non-empty string, got {vector_id}"
            )
        
        logger.debug(f"Querying chunks by vector_id: {vector_id}")
        
        query_sql = "SELECT * FROM chunks WHERE vector_id = ?"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_sql, (vector_id,))
            rows = cursor.fetchall()
            
            results = [dict(row) for row in rows]
            logger.debug(f"Found {len(results)} chunks for vector_id: {vector_id}")
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Failed to query chunks by vector_id {vector_id}: {e}")
            raise
    
    def get_chunks_by_vertical(self, vertical: str) -> List[Dict[str, Any]]:
        """
        根据vertical分类查询记录
        
        Args:
            vertical: 垂直分类
            
        Returns:
            List[Dict[str, Any]]: 查询到的记录列表
            
        Raises:
            ValueError: 当vertical无效时抛出
            sqlite3.Error: 当查询失败时抛出
        """
        if not vertical or not isinstance(vertical, str):
            raise ValueError(
                f"vertical must be a non-empty string, got {vertical}"
            )
        
        logger.debug(f"Querying chunks by vertical: {vertical}")
        
        query_sql = "SELECT * FROM chunks WHERE vertical = ?"
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_sql, (vertical,))
            rows = cursor.fetchall()
            
            results = [dict(row) for row in rows]
            logger.debug(f"Found {len(results)} chunks for vertical: {vertical}")
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Failed to query chunks by vertical {vertical}: {e}")
            raise
    
    def close(self) -> None:
        """
        关闭数据库连接
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Failed to close database connection: {e}")
            finally:
                self.connection = None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        获取表信息
        
        Returns:
            Dict[str, Any]: 表信息
        """
        info = {
            "db_path": self.db_path,
            "connected": self.connection is not None
        }
        
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM chunks")
                count = cursor.fetchone()[0]
                info["total_chunks"] = count
                
                cursor.execute("SELECT COUNT(DISTINCT doc_id) FROM chunks")
                doc_count = cursor.fetchone()[0]
                info["total_docs"] = doc_count
                
            except sqlite3.Error as e:
                logger.error(f"Failed to get table info: {e}")
        
        return info
