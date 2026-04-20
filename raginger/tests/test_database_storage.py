"""
DatabaseStorage单元测试
"""

import unittest
import os
import tempfile
import shutil

from raginger.core.parse.database_storage import DatabaseStorage


class TestDatabaseStorage(unittest.TestCase):
    """DatabaseStorage测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        storage = DatabaseStorage(self.db_path)
        
        self.assertEqual(storage.db_path, self.db_path)
        self.assertIsNotNone(storage.connection)
        
        storage.close()
    
    def test_init_with_empty_path(self):
        """测试使用空路径初始化"""
        with self.assertRaises(ValueError):
            DatabaseStorage("")
    
    def test_init_with_invalid_path_type(self):
        """测试使用无效类型的路径初始化"""
        with self.assertRaises(ValueError):
            DatabaseStorage(123)
    
    def test_insert_chunk(self):
        """测试插入切片数据"""
        with DatabaseStorage(self.db_path) as storage:
            chunk_data = {
                "chunk_id": "chunk_001",
                "doc_id": "doc_001",
                "vector_id": "vec_001",
                "chunk_position": 1,
                "title": "Test Title",
                "content": "Test content",
                "file_type": "pdf",
                "file_src": "/path/to/file.pdf",
                "vertical": "tech",
                "timestamp": 1712908800000
            }
            
            storage.insert_chunk(chunk_data)
            
            result = storage.get_chunk_by_id("chunk_001")
            
            self.assertIsNotNone(result)
            self.assertEqual(result["chunk_id"], "chunk_001")
            self.assertEqual(result["doc_id"], "doc_001")
            self.assertEqual(result["vector_id"], "vec_001")
            self.assertEqual(result["chunk_position"], 1)
            self.assertEqual(result["title"], "Test Title")
            self.assertEqual(result["content"], "Test content")
            self.assertEqual(result["file_type"], "pdf")
            self.assertEqual(result["file_src"], "/path/to/file.pdf")
            self.assertEqual(result["vertical"], "tech")
            self.assertEqual(result["timestamp"], 1712908800000)
    
    def test_insert_duplicate_chunk(self):
        """测试插入重复的chunk_id"""
        with DatabaseStorage(self.db_path) as storage:
            chunk_data = {
                "chunk_id": "chunk_001",
                "doc_id": "doc_001",
                "vector_id": "vec_001",
                "chunk_position": 1,
                "title": "Test Title",
                "content": "Test content",
                "file_type": "pdf",
                "file_src": "/path/to/file.pdf",
                "vertical": "tech",
                "timestamp": 1712908800000
            }
            
            storage.insert_chunk(chunk_data)
            
            with self.assertRaises(Exception):
                storage.insert_chunk(chunk_data)
    
    def test_insert_chunk_with_empty_data(self):
        """测试使用空数据插入"""
        with DatabaseStorage(self.db_path) as storage:
            with self.assertRaises(ValueError):
                storage.insert_chunk({})
    
    def test_insert_chunk_without_chunk_id(self):
        """测试插入缺少chunk_id的数据"""
        with DatabaseStorage(self.db_path) as storage:
            chunk_data = {
                "doc_id": "doc_001"
            }
            
            with self.assertRaises(ValueError):
                storage.insert_chunk(chunk_data)
    
    def test_get_chunk_by_id(self):
        """测试根据chunk_id查询"""
        with DatabaseStorage(self.db_path) as storage:
            chunk_data = {
                "chunk_id": "chunk_001",
                "doc_id": "doc_001",
                "vector_id": "vec_001",
                "chunk_position": 1,
                "title": "Test Title",
                "content": "Test content",
                "file_type": "pdf",
                "file_src": "/path/to/file.pdf",
                "vertical": "tech",
                "timestamp": 1712908800000
            }
            
            storage.insert_chunk(chunk_data)
            
            result = storage.get_chunk_by_id("chunk_001")
            
            self.assertIsNotNone(result)
            self.assertEqual(result["chunk_id"], "chunk_001")
    
    def test_get_chunk_by_id_not_found(self):
        """测试查询不存在的chunk_id"""
        with DatabaseStorage(self.db_path) as storage:
            result = storage.get_chunk_by_id("non_existent")
            
            self.assertIsNone(result)
    
    def test_get_chunk_by_id_with_empty_id(self):
        """测试使用空chunk_id查询"""
        with DatabaseStorage(self.db_path) as storage:
            with self.assertRaises(ValueError):
                storage.get_chunk_by_id("")
    
    def test_get_chunks_by_doc_id(self):
        """测试根据doc_id查询"""
        with DatabaseStorage(self.db_path) as storage:
            for i in range(3):
                chunk_data = {
                    "chunk_id": f"chunk_{i:03d}",
                    "doc_id": "doc_001",
                    "vector_id": f"vec_{i:03d}",
                    "chunk_position": i,
                    "title": f"Test Title {i}",
                    "content": f"Test content {i}",
                    "file_type": "pdf",
                    "file_src": "/path/to/file.pdf",
                    "vertical": "tech",
                    "timestamp": 1712908800000
                }
                storage.insert_chunk(chunk_data)
            
            results = storage.get_chunks_by_doc_id("doc_001")
            
            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]["chunk_position"], 0)
            self.assertEqual(results[1]["chunk_position"], 1)
            self.assertEqual(results[2]["chunk_position"], 2)
    
    def test_get_chunks_by_doc_id_not_found(self):
        """测试查询不存在的doc_id"""
        with DatabaseStorage(self.db_path) as storage:
            results = storage.get_chunks_by_doc_id("non_existent")
            
            self.assertEqual(len(results), 0)
    
    def test_get_chunks_by_doc_id_with_empty_id(self):
        """测试使用空doc_id查询"""
        with DatabaseStorage(self.db_path) as storage:
            with self.assertRaises(ValueError):
                storage.get_chunks_by_doc_id("")
    
    def test_get_chunks_by_vector_id(self):
        """测试根据vector_id查询"""
        with DatabaseStorage(self.db_path) as storage:
            chunk_data = {
                "chunk_id": "chunk_001",
                "doc_id": "doc_001",
                "vector_id": "vec_001",
                "chunk_position": 1,
                "title": "Test Title",
                "content": "Test content",
                "file_type": "pdf",
                "file_src": "/path/to/file.pdf",
                "vertical": "tech",
                "timestamp": 1712908800000
            }
            
            storage.insert_chunk(chunk_data)
            
            results = storage.get_chunks_by_vector_id("vec_001")
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["vector_id"], "vec_001")
    
    def test_get_chunks_by_vector_id_not_found(self):
        """测试查询不存在的vector_id"""
        with DatabaseStorage(self.db_path) as storage:
            results = storage.get_chunks_by_vector_id("non_existent")
            
            self.assertEqual(len(results), 0)
    
    def test_get_chunks_by_vector_id_with_empty_id(self):
        """测试使用空vector_id查询"""
        with DatabaseStorage(self.db_path) as storage:
            with self.assertRaises(ValueError):
                storage.get_chunks_by_vector_id("")
    
    def test_get_chunks_by_vertical(self):
        """测试根据vertical查询"""
        with DatabaseStorage(self.db_path) as storage:
            for i in range(3):
                chunk_data = {
                    "chunk_id": f"chunk_{i:03d}",
                    "doc_id": f"doc_{i:03d}",
                    "vector_id": f"vec_{i:03d}",
                    "chunk_position": i,
                    "title": f"Test Title {i}",
                    "content": f"Test content {i}",
                    "file_type": "pdf",
                    "file_src": "/path/to/file.pdf",
                    "vertical": "tech",
                    "timestamp": 1712908800000
                }
                storage.insert_chunk(chunk_data)
            
            results = storage.get_chunks_by_vertical("tech")
            
            self.assertEqual(len(results), 3)
    
    def test_get_chunks_by_vertical_not_found(self):
        """测试查询不存在的vertical"""
        with DatabaseStorage(self.db_path) as storage:
            results = storage.get_chunks_by_vertical("non_existent")
            
            self.assertEqual(len(results), 0)
    
    def test_get_chunks_by_vertical_with_empty_vertical(self):
        """测试使用空vertical查询"""
        with DatabaseStorage(self.db_path) as storage:
            with self.assertRaises(ValueError):
                storage.get_chunks_by_vertical("")
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with DatabaseStorage(self.db_path) as storage:
            self.assertIsNotNone(storage.connection)
        
        self.assertIsNone(storage.connection)
    
    def test_close(self):
        """测试关闭连接"""
        storage = DatabaseStorage(self.db_path)
        self.assertIsNotNone(storage.connection)
        
        storage.close()
        self.assertIsNone(storage.connection)
    
    def test_get_table_info(self):
        """测试获取表信息"""
        with DatabaseStorage(self.db_path) as storage:
            chunk_data = {
                "chunk_id": "chunk_001",
                "doc_id": "doc_001",
                "vector_id": "vec_001",
                "chunk_position": 1,
                "title": "Test Title",
                "content": "Test content",
                "file_type": "pdf",
                "file_src": "/path/to/file.pdf",
                "vertical": "tech",
                "timestamp": 1712908800000
            }
            
            storage.insert_chunk(chunk_data)
            
            info = storage.get_table_info()
            
            self.assertEqual(info["db_path"], self.db_path)
            self.assertTrue(info["connected"])
            self.assertEqual(info["total_chunks"], 1)
            self.assertEqual(info["total_docs"], 1)
    
    def test_auto_create_directory(self):
        """测试自动创建数据库目录"""
        db_path = os.path.join(self.temp_dir, "subdir", "test.db")
        
        with DatabaseStorage(db_path) as storage:
            self.assertTrue(os.path.exists(db_path))


if __name__ == "__main__":
    unittest.main()
