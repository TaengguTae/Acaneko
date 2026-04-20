"""
LuceneIndex单元测试
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

from raginger.core.index.lucene_index import LuceneIndex, FieldType, JPYPE_AVAILABLE


class TestLuceneIndex(unittest.TestCase):
    """LuceneIndex测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_index")
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(not JPYPE_AVAILABLE, "JPype is not installed")
    def test_init_with_valid_params(self):
        """测试使用有效参数初始化"""
        jar_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "core",
            "index",
            "libs",
            "Acaneko-Lucene9.12.3-v1.0.jar"
        )
        
        if not os.path.exists(jar_path):
            self.skipTest("JAR file not found")
        
        LuceneIndex.set_jar_path(jar_path)
        
        lucene_index = LuceneIndex(self.index_path, "zh")
        
        self.assertEqual(lucene_index.index_path, self.index_path)
        self.assertEqual(lucene_index.language, "zh")
        self.assertTrue(lucene_index._jvm_started)
        
        lucene_index.close()
    
    def test_init_with_empty_index_path(self):
        """测试使用空索引路径初始化"""
        with self.assertRaises(ValueError):
            LuceneIndex("", "zh")
    
    def test_init_with_empty_language(self):
        """测试使用空语言参数初始化"""
        with self.assertRaises(ValueError):
            LuceneIndex(self.index_path, "")
    
    def test_init_with_invalid_index_path_type(self):
        """测试使用无效类型的索引路径初始化"""
        with self.assertRaises(ValueError):
            LuceneIndex(123, "zh")
    
    def test_init_with_invalid_language_type(self):
        """测试使用无效类型的语言参数初始化"""
        with self.assertRaises(ValueError):
            LuceneIndex(self.index_path, 123)
    
    def test_field_type_enum(self):
        """测试FieldType枚举"""
        self.assertEqual(FieldType.ID.value, "ID")
        self.assertEqual(FieldType.TEXT.value, "TEXT")
        self.assertEqual(FieldType.STORED_ONLY.value, "STORED_ONLY")
        self.assertEqual(FieldType.LONG.value, "LONG")
        self.assertEqual(FieldType.INT.value, "INT")
    
    @patch('raginger.core.index.lucene_index.JPYPE_AVAILABLE', False)
    def test_jpype_not_available(self):
        """测试JPype不可用时的行为"""
        with self.assertRaises(RuntimeError) as context:
            LuceneIndex(self.index_path, "zh")
        
        self.assertIn("JPype is not installed", str(context.exception))


class TestLuceneIndexMocked(unittest.TestCase):
    """使用Mock测试LuceneIndex"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.index_path = os.path.join(self.temp_dir, "test_index")
        
        self.mock_jpype = MagicMock()
        self.mock_jpype.java.util.ArrayList = MagicMock
        self.mock_jpype.java.util.LinkedHashMap = MagicMock
        self.mock_jpype.java.lang.Long = MagicMock
        self.mock_jpype.java.util.Arrays = MagicMock
        
        self.patcher = patch('raginger.core.index.lucene_index.jpype', self.mock_jpype)
        self.patcher.start()
        
        self.patcher2 = patch('raginger.core.index.lucene_index.JPYPE_AVAILABLE', True)
        self.patcher2.start()
    
    def tearDown(self):
        """测试后清理"""
        self.patcher.stop()
        self.patcher2.stop()
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_set_jar_path(self):
        """测试设置JAR路径"""
        jar_path = "/path/to/jar.jar"
        LuceneIndex.set_jar_path(jar_path)
        
        self.assertEqual(LuceneIndex._jar_path, jar_path)
    
    def test_get_java_list(self):
        """测试获取Java ArrayList"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        result = lucene_index._get_java_list()
        
        self.assertIsNotNone(result)
    
    def test_get_java_map(self):
        """测试获取Java LinkedHashMap"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        result = lucene_index._get_java_map()
        
        self.assertIsNotNone(result)
    
    def test_get_java_long(self):
        """测试获取Java Long"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        result = lucene_index._get_java_long(123)
        
        self.assertIsNotNone(result)
    
    def test_convert_field_type(self):
        """测试字段类型转换"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        mock_field_type = MagicMock()
        mock_field_type.ID = "ID"
        mock_field_type.TEXT = "TEXT"
        mock_field_type.STORED_ONLY = "STORED_ONLY"
        mock_field_type.LONG = "LONG"
        mock_field_type.INT = "INT"
        
        lucene_index._FieldType = mock_field_type
        
        result = lucene_index._convert_field_type("ID")
        self.assertEqual(result, "ID")
        
        result = lucene_index._convert_field_type(FieldType.TEXT)
        self.assertEqual(result, "TEXT")
    
    def test_convert_occur(self):
        """测试Occur转换"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        mock_occur = MagicMock()
        mock_occur.MUST = "MUST"
        mock_occur.SHOULD = "SHOULD"
        mock_occur.FILTER = "FILTER"
        
        lucene_index._Occur = mock_occur
        
        result = lucene_index._convert_occur("MUST")
        self.assertEqual(result, "MUST")
        
        result = lucene_index._convert_occur("should")
        self.assertEqual(result, "SHOULD")
    
    def test_add_document_without_index_creator(self):
        """测试未初始化IndexCreator时添加文档"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        with self.assertRaises(ValueError) as context:
            lucene_index.add_document([{"name": "test", "value": "test"}])
        
        self.assertIn("IndexCreator not initialized", str(context.exception))
    
    def test_add_document_with_empty_fields(self):
        """测试使用空字段列表添加文档"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = MagicMock()
        lucene_index._searcher = None
        
        with self.assertRaises(ValueError) as context:
            lucene_index.add_document([])
        
        self.assertIn("fields cannot be empty", str(context.exception))
    
    def test_add_document_without_field_name(self):
        """测试字段缺少名称时添加文档"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = MagicMock()
        lucene_index._searcher = None
        
        mock_list = MagicMock()
        lucene_index._get_java_list = MagicMock(return_value=mock_list)
        
        mock_field_type = MagicMock()
        lucene_index._FieldType = mock_field_type
        lucene_index._convert_field_type = MagicMock(return_value="TEXT")
        
        lucene_index._FieldConfig = MagicMock()
        
        with self.assertRaises(ValueError) as context:
            lucene_index.add_document([{"value": "test"}])
        
        self.assertIn("Field name is required", str(context.exception))
    
    def test_commit_without_index_creator(self):
        """测试未初始化IndexCreator时提交"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        with self.assertRaises(ValueError) as context:
            lucene_index.commit()
        
        self.assertIn("IndexCreator not initialized", str(context.exception))
    
    def test_get_doc_count_without_index_creator(self):
        """测试未初始化IndexCreator时获取文档数"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        with self.assertRaises(ValueError) as context:
            lucene_index.get_doc_count()
        
        self.assertIn("IndexCreator not initialized", str(context.exception))
    
    def test_search_with_empty_query(self):
        """测试使用空查询字符串搜索"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = MagicMock()
        
        with self.assertRaises(ValueError) as context:
            lucene_index.search("", 10)
        
        self.assertIn("query cannot be empty", str(context.exception))
    
    def test_search_with_invalid_top_n(self):
        """测试使用无效的top_n参数搜索"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = MagicMock()
        
        with self.assertRaises(ValueError) as context:
            lucene_index.search("test", 0)
        
        self.assertIn("top_n must be positive", str(context.exception))
    
    def test_search_natural_with_empty_query(self):
        """测试自然语言查询使用空字符串"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = MagicMock()
        
        with self.assertRaises(ValueError) as context:
            lucene_index.search_natural("", ["content"])
        
        self.assertIn("query_text cannot be empty", str(context.exception))
    
    def test_search_composite_with_empty_conditions(self):
        """测试组合查询使用空条件列表"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = MagicMock()
        
        with self.assertRaises(ValueError) as context:
            lucene_index.search_composite([], 10)
        
        self.assertIn("conditions cannot be empty", str(context.exception))
    
    def test_get_index_info(self):
        """测试获取索引信息"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index.index_path = self.index_path
        lucene_index.language = "zh"
        lucene_index._jvm_started = True
        lucene_index._jar_path = "/path/to/jar.jar"
        lucene_index._index_creator = None
        lucene_index._searcher = None
        
        info = lucene_index.get_index_info()
        
        self.assertEqual(info["index_path"], self.index_path)
        self.assertEqual(info["language"], "zh")
        self.assertTrue(info["jvm_started"])
        self.assertEqual(info["jar_path"], "/path/to/jar.jar")
    
    def test_context_manager(self):
        """测试上下文管理器"""
        lucene_index = LuceneIndex.__new__(LuceneIndex)
        lucene_index._jvm_started = True
        lucene_index._index_creator = None
        lucene_index._searcher = None
        lucene_index.close = MagicMock()
        
        with lucene_index:
            pass
        
        lucene_index.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
