"""
向量索引单元测试
"""

import unittest
import numpy as np
import os
import tempfile
import shutil

from raginger.core.index.vector_index import FaissIndex


class TestFaissIndex(unittest.TestCase):
    """FAISS向量索引测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.dimension = 128
        self.index = FaissIndex(self.dimension)
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_valid_dimension(self):
        """测试使用有效维度初始化"""
        self.assertEqual(self.index.dimension, self.dimension)
        self.assertEqual(self.index.get_vector_count(), 0)
        self.assertIsNotNone(self.index.index)
    
    def test_init_with_invalid_dimension(self):
        """测试使用无效维度初始化"""
        with self.assertRaises(ValueError):
            FaissIndex(0)
        
        with self.assertRaises(ValueError):
            FaissIndex(-1)
        
        with self.assertRaises(ValueError):
            FaissIndex(1.5)
    
    def test_add_vectors(self):
        """测试添加向量"""
        vectors = np.random.randn(10, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(10)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        self.assertEqual(self.index.get_vector_count(), 10)
        
        for vid in vector_ids:
            self.assertTrue(self.index.has_vector(vid))
    
    def test_add_vectors_with_invalid_input(self):
        """测试添加无效向量"""
        vectors = np.random.randn(5, self.dimension).astype('float32')
        
        with self.assertRaises(ValueError):
            self.index.add_vectors(vectors, [])
        
        with self.assertRaises(ValueError):
            self.index.add_vectors(vectors, ["id1", "id2"])
        
        with self.assertRaises(ValueError):
            self.index.add_vectors("not_array", ["id1"])
        
        vectors_wrong_dim = np.random.randn(5, 64).astype('float32')
        with self.assertRaises(ValueError):
            self.index.add_vectors(vectors_wrong_dim, [f"id_{i}" for i in range(5)])
    
    def test_add_duplicate_vector_ids(self):
        """测试添加重复的向量ID"""
        vectors1 = np.random.randn(5, self.dimension).astype('float32')
        vectors2 = np.random.randn(5, self.dimension).astype('float32')
        
        vector_ids = [f"vec_{i}" for i in range(5)]
        
        self.index.add_vectors(vectors1, vector_ids)
        
        with self.assertRaises(ValueError):
            self.index.add_vectors(vectors2, vector_ids)
    
    def test_search_vectors(self):
        """测试向量搜索"""
        vectors = np.random.randn(20, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(20)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        query_vector = vectors[0]
        results = self.index.search(query_vector, top_k=5)
        
        self.assertEqual(len(results), 5)
        self.assertEqual(results[0][0], "vec_0")
        self.assertGreater(results[0][1], 0.9)
        
        for vid, score in results:
            self.assertIsInstance(vid, str)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, -1.0)
            self.assertLessEqual(score, 1.0)
    
    def test_search_with_empty_index(self):
        """测试在空索引中搜索"""
        query_vector = np.random.randn(self.dimension).astype('float32')
        results = self.index.search(query_vector, top_k=5)
        
        self.assertEqual(results, [])
    
    def test_search_with_invalid_input(self):
        """测试使用无效输入搜索"""
        vectors = np.random.randn(5, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(5)]
        self.index.add_vectors(vectors, vector_ids)
        
        with self.assertRaises(ValueError):
            self.index.search("not_array", top_k=5)
        
        with self.assertRaises(ValueError):
            self.index.search(vectors[0], top_k=0)
        
        with self.assertRaises(ValueError):
            self.index.search(vectors[0], top_k=-1)
    
    def test_save_and_load_index(self):
        """测试保存和加载索引"""
        vectors = np.random.randn(10, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(10)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        file_path = os.path.join(self.temp_dir, "test_index")
        self.index.save_index(file_path)
        
        self.assertTrue(os.path.exists(f"{file_path}.index"))
        self.assertTrue(os.path.exists(f"{file_path}.metadata"))
        
        loaded_index = FaissIndex.load_index(file_path)
        
        self.assertEqual(loaded_index.dimension, self.dimension)
        self.assertEqual(loaded_index.get_vector_count(), 10)
        
        for vid in vector_ids:
            self.assertTrue(loaded_index.has_vector(vid))
        
        query_vector = vectors[0]
        results_original = self.index.search(query_vector, top_k=3)
        results_loaded = loaded_index.search(query_vector, top_k=3)
        
        self.assertEqual(len(results_original), len(results_loaded))
        for (vid1, score1), (vid2, score2) in zip(results_original, results_loaded):
            self.assertEqual(vid1, vid2)
            self.assertAlmostEqual(score1, score2, places=5)
    
    def test_load_nonexistent_index(self):
        """测试加载不存在的索引"""
        with self.assertRaises(IOError):
            FaissIndex.load_index("nonexistent_path")
    
    def test_get_index_info(self):
        """测试获取索引信息"""
        info = self.index.get_index_info()
        
        self.assertEqual(info['dimension'], self.dimension)
        self.assertEqual(info['vector_count'], 0)
        self.assertEqual(info['index_type'], 'IndexFlatIP')
        self.assertTrue(info['is_trained'])
        self.assertEqual(info['ntotal'], 0)
        
        vectors = np.random.randn(5, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(5)]
        self.index.add_vectors(vectors, vector_ids)
        
        info = self.index.get_index_info()
        self.assertEqual(info['vector_count'], 5)
        self.assertEqual(info['ntotal'], 5)
    
    def test_clear_index(self):
        """测试清空索引"""
        vectors = np.random.randn(10, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(10)]
        
        self.index.add_vectors(vectors, vector_ids)
        self.assertEqual(self.index.get_vector_count(), 10)
        
        self.index.clear_index()
        
        self.assertEqual(self.index.get_vector_count(), 0)
        self.assertEqual(len(self.index.id_mapping), 0)
        
        for vid in vector_ids:
            self.assertFalse(self.index.has_vector(vid))
    
    def test_remove_vector(self):
        """测试移除向量"""
        vectors = np.random.randn(5, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(5)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        result = self.index.remove_vector("vec_2")
        self.assertTrue(result)
        self.assertFalse(self.index.has_vector("vec_2"))
        
        result = self.index.remove_vector("nonexistent")
        self.assertFalse(result)
    
    def test_get_vector_id(self):
        """测试根据内部索引获取向量ID"""
        vectors = np.random.randn(5, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(5)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        self.assertEqual(self.index.get_vector_id(0), "vec_0")
        self.assertEqual(self.index.get_vector_id(4), "vec_4")
        self.assertIsNone(self.index.get_vector_id(10))
    
    def test_vector_normalization(self):
        """测试向量归一化"""
        vectors = np.random.randn(5, self.dimension).astype('float32') * 10
        vector_ids = [f"vec_{i}" for i in range(5)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        query_vector = vectors[0]
        results = self.index.search(query_vector, top_k=1)
        
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0][1], 0.99)
    
    def test_large_batch_add(self):
        """测试大批量添加向量"""
        batch_size = 1000
        vectors = np.random.randn(batch_size, self.dimension).astype('float32')
        vector_ids = [f"vec_{i}" for i in range(batch_size)]
        
        self.index.add_vectors(vectors, vector_ids)
        
        self.assertEqual(self.index.get_vector_count(), batch_size)
        
        query_vector = vectors[0]
        results = self.index.search(query_vector, top_k=10)
        
        self.assertEqual(len(results), 10)


if __name__ == '__main__':
    unittest.main()
