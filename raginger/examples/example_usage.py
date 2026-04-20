"""
示例：使用文档切片器
演示如何使用loguru配置日志
"""

from loguru import logger
from core.parse.splitter import DocumentSplitter
from transformers import AutoTokenizer


class MockTokenizer:
    """模拟分词器"""
    
    def encode(self, text):
        return text.split()
    
    def decode(self, tokens):
        return ' '.join(tokens)


def main():
    logger.add("example.log", rotation="10 MB", level="INFO")
    
    logger.info("开始文档切片示例")
    
    # tokenizer = MockTokenizer()
    tokenizer = AutoTokenizer.from_pretrained(r"models\google\embeddinggemma-300m")
    
    splitter = DocumentSplitter(
        tokenizer=tokenizer,
        split_type="token",
        chunk_size=30,
        chunk_overlap=10,
        additional_metadata_fields={
            "language": "zh",
            "source": "example"
        }
    )
    
    document = """
    这是第一段文本内容。它包含多个句子和一些标点符号。
    
    这是第二段文本内容。这段内容稍长一些，用于测试切片功能。
    我们需要确保切片器能够正确处理不同长度的文本段落。
    
    这是第三段文本内容。最后一段用于验证切片的完整性。
    """
    
    logger.info("开始切分文档...")
    chunks = splitter.split_single_document(
        document=document,
        doc_id="example_doc",
        doc_name="example.txt"
    )
    
    logger.success(f"文档切分完成，共生成 {len(chunks)} 个切片")
    
    for i, chunk in enumerate(chunks[:3]):
        logger.info(f"切片 {i+1}:")
        logger.info(f"  ID: {chunk['chunk_id']}")
        logger.info(f"  长度: {chunk['chunk_length']}")
        logger.info(f"  Token数: {chunk['token_count']}")
        logger.info(f"  内容预览: {chunk['content']}")
    
    splitter_info = splitter.get_splitter_info()
    logger.info(f"切片器信息: {splitter_info}")
    
    logger.info("示例完成")


if __name__ == "__main__":
    main()
