"""
文本向量化单元测试
"""

import unittest
import numpy as np
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

from raginger.core.embedding.embedding import Embedding


class TestEmbedding(unittest.TestCase):
    """文本向量化测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.temp_dir, "test_model")
        os.makedirs(self.model_path, exist_ok=True)
        
        self.config_file = os.path.join(
            self.model_path, 
            "config_sentence_transformers.json"
        )
        
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_model_path(self):
        """测试使用有效模型路径初始化"""
        config = {
            "query_prefix": "query: ",
            "doc_prefix": "doc: "
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            self.assertEqual(embedding.model_path, self.model_path)
            self.assertEqual(embedding.embedding_dim, 768)
            self.assertEqual(embedding.prefix['query'], "query: ")
            self.assertEqual(embedding.prefix['doc'], "doc: ")
    
    def test_init_with_invalid_model_path(self):
        """测试使用无效模型路径初始化"""
        with self.assertRaises(ValueError):
            Embedding("")
        
        with self.assertRaises(ValueError):
            Embedding(123)
    
    def test_load_prefix_config_without_file(self):
        """测试配置文件不存在时的处理"""
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            self.assertEqual(embedding.prefix, {})
    
    def test_apply_prefix_with_query(self):
        """测试对query应用prefix"""
        config = {
            "query_prefix": "query: ",
            "doc_prefix": "doc: "
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            result = embedding._apply_prefix("test query", "query")
            self.assertEqual(result, "query: test query")
            
            result = embedding._apply_prefix(["q1", "q2"], "query")
            self.assertEqual(result, ["query: q1", "query: q2"])
    
    def test_apply_prefix_with_doc(self):
        """测试对doc应用prefix"""
        config = {
            "query_prefix": "query: ",
            "doc_prefix": "doc: "
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            result = embedding._apply_prefix("test doc", "doc")
            self.assertEqual(result, "doc: test doc")
            
            result = embedding._apply_prefix(["d1", "d2"], "doc")
            self.assertEqual(result, ["doc: d1", "doc: d2"])
    
    def test_apply_prefix_with_invalid_content_type(self):
        """测试使用无效的content_type"""
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            with self.assertRaises(ValueError):
                embedding._apply_prefix("test", "invalid")
    
    def test_get_embedding_single_text(self):
        """测试单个文本向量化"""
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_model.encode.return_value = np.random.randn(768)
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            result = embedding.get_embedding("test text", content_type="doc")
            
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, (768,))
    
    def test_get_embedding_batch_texts(self):
        """测试批量文本向量化"""
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_model.encode.return_value = np.random.randn(3, 768)
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            texts = ["text1", "text2", "text3"]
            result = embedding.get_embedding(texts, content_type="doc")
            
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, (3, 768))
    
    def test_get_embedding_with_invalid_input(self):
        """测试使用无效输入"""
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            with self.assertRaises(ValueError):
                embedding.get_embedding("")
            
            with self.assertRaises(ValueError):
                embedding.get_embedding(123)
            
            with self.assertRaises(ValueError):
                embedding.get_embedding(["text", 123])
    
    def test_get_embedding_dimension(self):
        """测试获取向量维度"""
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 1024
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            self.assertEqual(embedding.get_embedding_dimension(), 1024)
    
    def test_get_model_info(self):
        """测试获取模型信息"""
        config = {
            "query_prefix": "query: ",
            "doc_prefix": "doc: "
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_model.max_seq_length = 512
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            info = embedding.get_model_info()
            
            self.assertEqual(info['model_path'], self.model_path)
            self.assertEqual(info['embedding_dimension'], 768)
            self.assertEqual(info['prefix_config']['query'], "query: ")
            self.assertEqual(info['prefix_config']['doc'], "doc: ")
            self.assertEqual(info['max_seq_length'], 512)
    
    def test_prefix_application_consistency(self):
        """测试prefix应用的一致性"""
        config = {
            "query_prefix": "Q: ",
            "doc_prefix": "D: "
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)
        
        with patch('raginger.core.embedding.embedding.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 768
            mock_model.encode.return_value = np.random.randn(768)
            mock_st.return_value = mock_model
            
            embedding = Embedding(self.model_path)
            
            embedding.get_embedding("test", content_type="query")
            
            called_args = mock_model.encode.call_args[0][0]
            self.assertTrue(called_args.startswith("Q: "))
            
            embedding.get_embedding("test", content_type="doc")
            called_args = mock_model.encode.call_args[0][0]
            self.assertTrue(called_args.startswith("D: "))


if __name__ == '__main__':
    unittest.main()
