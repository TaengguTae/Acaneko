"""
Recaller单元测试
"""

import unittest
import os
import tempfile
import shutil
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from raginger.core.recall.recaller import Recaller


class TestRecaller(unittest.TestCase):
    """Recaller测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.faiss_index_path = os.path.join(self.temp_dir, "test_faiss")
        self.lucene_index_path = os.path.join(self.temp_dir, "test_lucene")
        
        self._create_mock_embedding()
        self._create_mock_faiss_index()
    
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_mock_embedding(self):
        """创建模拟Embedding对象"""
        self.mock_embedding = Mock()
        self.mock_embedding.get_embedding_dimension.return_value = 128
        self.mock_embedding.get_embedding.return_value = np.random.randn(128).astype('float32')
    
    def _create_mock_faiss_index(self):
        """创建模拟FAISS索引文件"""
        import faiss
        import pickle
        
        dimension = 128
        index = faiss.IndexFlatIP(dimension)
        
        vectors = np.random.randn(3, dimension).astype('float32')
        faiss.normalize_L2(vectors)
        index.add(vectors)
        
        faiss.write_index(index, f"{self.faiss_index_path}.index")
        
        metadata = {
            'dimension': dimension,
            'id_mapping': {0: 'chunk_0', 1: 'chunk_1', 2: 'chunk_2'},
            'reverse_mapping': {'chunk_0': 0, 'chunk_1': 1, 'chunk_2': 2},
            'vector_count': 3
        }
        
        with open(f"{self.faiss_index_path}.metadata", 'wb') as f:
            pickle.dump(metadata, f)
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_init_with_valid_params(self, mock_lucene):
        """测试使用有效参数初始化"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        self.assertEqual(recaller.faiss_index_path, self.faiss_index_path)
        self.assertEqual(recaller.lucene_index_path, self.lucene_index_path)
        self.assertEqual(recaller.embedding, self.mock_embedding)
        self.assertIsNotNone(recaller.faiss_index)
        self.assertIsNotNone(recaller.lucene_index)
        
        recaller.close()
    
    def test_init_with_empty_faiss_path(self):
        """测试使用空FAISS路径初始化"""
        with self.assertRaises(ValueError):
            Recaller(
                faiss_index_path="",
                lucene_index_path=self.lucene_index_path,
                embedding=self.mock_embedding
            )
    
    def test_init_with_empty_lucene_path(self):
        """测试使用空Lucene路径初始化"""
        with self.assertRaises(ValueError):
            Recaller(
                faiss_index_path=self.faiss_index_path,
                lucene_index_path="",
                embedding=self.mock_embedding
            )
    
    def test_init_with_invalid_embedding(self):
        """测试使用无效的Embedding对象初始化"""
        with self.assertRaises(ValueError):
            Recaller(
                faiss_index_path=self.faiss_index_path,
                lucene_index_path=self.lucene_index_path,
                embedding="not_an_embedding"
            )
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_vector(self, mock_lucene):
        """测试向量召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        results = recaller.recall_vector("测试查询", topk=3, threshold=0.0)
        
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)
        
        for result in results:
            self.assertIn("chunk_id", result)
            self.assertIn("score", result)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_vector_with_threshold(self, mock_lucene):
        """测试带阈值的向量召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        results = recaller.recall_vector("测试查询", topk=3, threshold=0.9)
        
        for result in results:
            self.assertGreaterEqual(result["score"], 0.9)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_vector_with_empty_query(self, mock_lucene):
        """测试使用空查询进行向量召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        with self.assertRaises(ValueError):
            recaller.recall_vector("", topk=3)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_vector_with_invalid_topk(self, mock_lucene):
        """测试使用无效topk进行向量召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        with self.assertRaises(ValueError):
            recaller.recall_vector("测试查询", topk=0)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_bm25_natural(self, mock_lucene):
        """测试BM25自然语言召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene_instance.search_natural.return_value = {
            "total_hits": 2,
            "hits": [
                {"chunk_id": "chunk_1", "score": 1.5, "fields": {"content": "内容1"}},
                {"chunk_id": "chunk_2", "score": 1.2, "fields": {"content": "内容2"}}
            ]
        }
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        results = recaller.recall_bm25_natural("测试查询", topk=10)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["chunk_id"], "chunk_1")
        self.assertEqual(results[0]["score"], 1.5)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_bm25_natural_with_empty_query(self, mock_lucene):
        """测试使用空查询进行BM25自然语言召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        with self.assertRaises(ValueError):
            recaller.recall_bm25_natural("", topk=10)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_bm25_composite(self, mock_lucene):
        """测试BM25组合召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene_instance.search_composite.return_value = {
            "total_hits": 2,
            "hits": [
                {"chunk_id": "chunk_1", "score": 2.0, "fields": {"content": "内容1"}},
                {"chunk_id": "chunk_2", "score": 1.8, "fields": {"content": "内容2"}}
            ]
        }
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        conditions = [
            {
                "type": "TEXT",
                "fields": ["content"],
                "keywords": ["测试"],
                "occur": "SHOULD"
            }
        ]
        
        results = recaller.recall_bm25_composite(conditions, topk=10)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["chunk_id"], "chunk_1")
        self.assertEqual(results[0]["score"], 2.0)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_bm25_composite_with_empty_conditions(self, mock_lucene):
        """测试使用空条件进行BM25组合召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        with self.assertRaises(ValueError):
            recaller.recall_bm25_composite([], topk=10)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_recall_hybrid(self, mock_lucene):
        """测试混合召回"""
        mock_lucene_instance = MagicMock()
        mock_lucene_instance.search_natural.return_value = {
            "total_hits": 2,
            "hits": [
                {"chunk_id": "chunk_1", "score": 1.5, "fields": {}},
                {"chunk_id": "chunk_2", "score": 1.2, "fields": {}}
            ]
        }
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        results = recaller.recall_hybrid("测试查询", topk=3)
        
        self.assertIn("vector", results)
        self.assertIn("bm25", results)
        self.assertIsInstance(results["vector"], list)
        self.assertIsInstance(results["bm25"], list)
        
        recaller.close()
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_context_manager(self, mock_lucene):
        """测试上下文管理器"""
        mock_lucene_instance = MagicMock()
        mock_lucene.return_value = mock_lucene_instance
        
        with Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        ) as recaller:
            self.assertIsNotNone(recaller.faiss_index)
            self.assertIsNotNone(recaller.lucene_index)
    
    @patch('raginger.core.recall.recaller.LuceneIndex')
    def test_get_index_info(self, mock_lucene):
        """测试获取索引信息"""
        mock_lucene_instance = MagicMock()
        mock_lucene_instance.get_searcher_doc_count.return_value = 5
        mock_lucene.return_value = mock_lucene_instance
        
        recaller = Recaller(
            faiss_index_path=self.faiss_index_path,
            lucene_index_path=self.lucene_index_path,
            embedding=self.mock_embedding
        )
        
        info = recaller.get_index_info()
        
        self.assertEqual(info["faiss_index_path"], self.faiss_index_path)
        self.assertEqual(info["lucene_index_path"], self.lucene_index_path)
        self.assertEqual(info["embedding_dimension"], 128)
        self.assertEqual(info["faiss_vector_count"], 3)
        self.assertEqual(info["lucene_doc_count"], 5)
        
        recaller.close()


if __name__ == "__main__":
    unittest.main()
