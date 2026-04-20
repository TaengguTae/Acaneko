"""
文档切片器单元测试
"""

import unittest
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from raginger.core.parse.splitter import DocumentSplitter


class MockTokenizer:
    """模拟的分词器类"""
    
    def encode(self, text):
        """模拟encode方法，简单按空格分割"""
        return text.split()
    
    def decode(self, tokens):
        """模拟decode方法"""
        return ' '.join(tokens)


class TestDocumentSplitter(unittest.TestCase):
    """文档切片器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.tokenizer = MockTokenizer()
        self.sample_document = """
        这是第一段文本内容。它包含多个句子和一些标点符号。
        
        这是第二段文本内容。这段内容稍长一些，用于测试切片功能。
        我们需要确保切片器能够正确处理不同长度的文本段落。
        
        这是第三段文本内容。最后一段用于验证切片的完整性。
        """
    
    def test_init_with_valid_parameters(self):
        """测试使用有效参数初始化"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        self.assertEqual(splitter.split_type, "character")
        self.assertEqual(splitter.chunk_size, 100)
        self.assertEqual(splitter.chunk_overlap, 20)
        self.assertIsNotNone(splitter._splitter)
    
    def test_init_with_invalid_split_type(self):
        """测试使用无效的split_type参数"""
        with self.assertRaises(ValueError) as context:
            DocumentSplitter(
                tokenizer=self.tokenizer,
                split_type="invalid",
                chunk_size=100,
                chunk_overlap=20
            )
        
        self.assertIn("split_type must be 'character' or 'token'", str(context.exception))
    
    def test_init_with_invalid_chunk_size(self):
        """测试使用无效的chunk_size参数"""
        with self.assertRaises(ValueError) as context:
            DocumentSplitter(
                tokenizer=self.tokenizer,
                split_type="character",
                chunk_size=0,
                chunk_overlap=20
            )
        
        self.assertIn("chunk_size must be greater than 0", str(context.exception))
    
    def test_init_with_invalid_chunk_overlap(self):
        """测试使用无效的chunk_overlap参数"""
        with self.assertRaises(ValueError) as context:
            DocumentSplitter(
                tokenizer=self.tokenizer,
                split_type="character",
                chunk_size=100,
                chunk_overlap=100
            )
        
        self.assertIn("chunk_overlap", str(context.exception))
    
    def test_split_single_document_character_mode(self):
        """测试按字符模式切分单个文档"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=50,
            chunk_overlap=10
        )
        
        chunks = splitter.split_single_document(
            document=self.sample_document,
            doc_id="test_doc_1",
            doc_name="test_document.txt"
        )
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        for chunk in chunks:
            self.assertIn("chunk_id", chunk)
            self.assertIn("content", chunk)
            self.assertIn("doc_id", chunk)
            self.assertIn("doc_name", chunk)
            self.assertIn("chunk_length", chunk)
            self.assertIn("chunk_index", chunk)
            self.assertIn("token_count", chunk)
            self.assertIn("start_index", chunk)
            self.assertIn("end_index", chunk)
            
            self.assertEqual(chunk["doc_id"], "test_doc_1")
            self.assertEqual(chunk["doc_name"], "test_document.txt")
            self.assertIsInstance(chunk["chunk_length"], int)
            self.assertGreater(chunk["chunk_length"], 0)
    
    def test_split_single_document_token_mode(self):
        """测试按token模式切分单个文档"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="token",
            chunk_size=10,
            chunk_overlap=2
        )
        
        chunks = splitter.split_single_document(
            document=self.sample_document,
            doc_id="test_doc_2",
            doc_name="test_document.txt"
        )
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        for chunk in chunks:
            self.assertIn("token_count", chunk)
            self.assertGreater(chunk["token_count"], 0)
    
    def test_split_empty_document(self):
        """测试切分空文档"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        chunks = splitter.split_single_document(
            document="",
            doc_id="empty_doc",
            doc_name="empty.txt"
        )
        
        self.assertEqual(chunks, [])
    
    def test_split_whitespace_document(self):
        """测试切分仅包含空白字符的文档"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        chunks = splitter.split_single_document(
            document="   \n\n\t  ",
            doc_id="whitespace_doc",
            doc_name="whitespace.txt"
        )
        
        self.assertEqual(chunks, [])
    
    def test_split_documents_batch(self):
        """测试批量切分文档"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        documents = [
            {
                "content": "这是第一个文档的内容。" * 10,
                "doc_id": "doc_1",
                "doc_name": "document1.txt"
            },
            {
                "content": "这是第二个文档的内容。" * 10,
                "doc_id": "doc_2",
                "doc_name": "document2.txt"
            },
            {
                "content": "这是第三个文档的内容。" * 10,
                "doc_id": "doc_3",
                "doc_name": "document3.txt"
            }
        ]
        
        chunks = splitter.split_documents(documents, max_workers=2)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        doc_ids = set(chunk["doc_id"] for chunk in chunks)
        self.assertEqual(len(doc_ids), 3)
    
    def test_split_documents_batch_empty(self):
        """测试批量切分空文档列表"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        chunks = splitter.split_documents([])
        
        self.assertEqual(chunks, [])
    
    def test_split_documents_batch_invalid_format(self):
        """测试批量切分格式错误的文档"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        documents = [
            {
                "content": "文档内容",
                "doc_id": "doc_1"
            }
        ]
        
        with self.assertRaises(ValueError) as context:
            splitter.split_documents(documents)
        
        self.assertIn("missing required fields", str(context.exception))
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        document = "这是一个测试文档。" * 20
        doc_id = "cache_test"
        doc_name = "cache.txt"
        
        chunks1 = splitter.split_single_document(document, doc_id, doc_name)
        cache_size = splitter.get_cache_size()
        
        self.assertGreater(cache_size, 0)
        
        chunks2 = splitter.split_single_document(document, doc_id, doc_name)
        
        self.assertEqual(chunks1, chunks2)
    
    def test_clear_cache(self):
        """测试清空缓存"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20
        )
        
        document = "这是一个测试文档。" * 20
        splitter.split_single_document(document, "doc1", "test.txt")
        
        self.assertGreater(splitter.get_cache_size(), 0)
        
        splitter.clear_cache()
        
        self.assertEqual(splitter.get_cache_size(), 0)
    
    def test_additional_metadata_fields(self):
        """测试额外的元数据字段"""
        additional_fields = {
            "language": "zh",
            "source": "web",
            "category": "tech"
        }
        
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20,
            additional_metadata_fields=additional_fields
        )
        
        chunks = splitter.split_single_document(
            document=self.sample_document,
            doc_id="metadata_test",
            doc_name="test.txt"
        )
        
        for chunk in chunks:
            self.assertEqual(chunk["language"], "zh")
            self.assertEqual(chunk["source"], "web")
            self.assertEqual(chunk["category"], "tech")
    
    def test_get_splitter_info(self):
        """测试获取切片器信息"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=100,
            chunk_overlap=20,
            additional_metadata_fields={"test": "value"}
        )
        
        info = splitter.get_splitter_info()
        
        self.assertEqual(info["split_type"], "character")
        self.assertEqual(info["chunk_size"], 100)
        self.assertEqual(info["chunk_overlap"], 20)
        self.assertIn("test", info["additional_metadata_fields"])
        self.assertIn("cache_size", info)
    
    def test_chunk_indices(self):
        """测试切片索引的正确性"""
        splitter = DocumentSplitter(
            tokenizer=self.tokenizer,
            split_type="character",
            chunk_size=50,
            chunk_overlap=10
        )
        
        document = "这是一段测试文本，用于验证切片索引的正确性。"
        chunks = splitter.split_single_document(document, "index_test", "test.txt")
        
        for chunk in chunks:
            start_idx = chunk["start_index"]
            end_idx = chunk["end_index"]
            
            self.assertGreaterEqual(start_idx, 0)
            self.assertGreater(end_idx, start_idx)
            self.assertLessEqual(end_idx, len(document))
            
            extracted_content = document[start_idx:end_idx]
            self.assertIn(chunk["content"].strip(), extracted_content.strip())


if __name__ == '__main__':
    unittest.main()
