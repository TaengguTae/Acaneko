"""
示例：使用数据库存储
演示如何使用DatabaseStorage进行切片数据的持久化存储
"""

import os
from loguru import logger

from core.parse.database_storage import DatabaseStorage


def demo_basic_usage():
    """演示基本用法"""
    logger.info("\n=== 基本用法示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        chunk_data = {
            "chunk_id": "doc_001_chunk_001",
            "doc_id": "doc_001",
            "vector_id": "vec_001",
            "chunk_position": 1,
            "title": "全文检索入门",
            "content": "Lucene是一个高性能的全文检索库，广泛应用于搜索引擎。",
            "file_type": "pdf",
            "file_src": "/data/docs/lucene_intro.pdf",
            "vertical": "tech",
            "timestamp": 1712908800000
        }
        
        storage.insert_chunk(chunk_data)
        logger.info("切片数据插入成功")
        
        result = storage.get_chunk_by_id("doc_001_chunk_001")
        logger.info(f"查询结果: {result}")


def demo_batch_insert():
    """演示批量插入"""
    logger.info("\n=== 批量插入示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        for i in range(5):
            chunk_data = {
                "chunk_id": f"doc_002_chunk_{i:03d}",
                "doc_id": "doc_002",
                "vector_id": f"vec_{i:03d}",
                "chunk_position": i,
                "title": f"文档切片 {i}",
                "content": f"这是第 {i} 个切片的内容，包含一些测试文本。",
                "file_type": "md",
                "file_src": "/data/docs/test.md",
                "vertical": "tech",
                "timestamp": 1712908800000 + i
            }
            
            storage.insert_chunk(chunk_data)
        
        logger.info("批量插入完成")


def demo_query_by_doc_id():
    """演示根据doc_id查询"""
    logger.info("\n=== 根据doc_id查询示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        results = storage.get_chunks_by_doc_id("doc_002")
        
        logger.info(f"找到 {len(results)} 条记录")
        for result in results:
            logger.info(f"  - {result['chunk_id']}: {result['title']}")


def demo_query_by_vector_id():
    """演示根据vector_id查询"""
    logger.info("\n=== 根据vector_id查询示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        results = storage.get_chunks_by_vector_id("vec_001")
        
        logger.info(f"找到 {len(results)} 条记录")
        for result in results:
            logger.info(f"  - {result['chunk_id']}: {result['title']}")


def demo_query_by_vertical():
    """演示根据vertical查询"""
    logger.info("\n=== 根据vertical查询示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        results = storage.get_chunks_by_vertical("tech")
        
        logger.info(f"找到 {len(results)} 条记录")
        for result in results:
            logger.info(f"  - {result['chunk_id']}: {result['title']}")


def demo_table_info():
    """演示获取表信息"""
    logger.info("\n=== 获取表信息示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        info = storage.get_table_info()
        
        logger.info(f"数据库路径: {info['db_path']}")
        logger.info(f"连接状态: {info['connected']}")
        logger.info(f"总切片数: {info.get('total_chunks', 0)}")
        logger.info(f"总文档数: {info.get('total_docs', 0)}")


def demo_error_handling():
    """演示错误处理"""
    logger.info("\n=== 错误处理示例 ===")
    
    db_path = "./demo_chunks.db"
    
    with DatabaseStorage(db_path) as storage:
        chunk_data = {
            "chunk_id": "doc_001_chunk_001",
            "doc_id": "doc_001",
            "vector_id": "vec_001",
            "chunk_position": 1,
            "title": "重复的切片",
            "content": "这个切片ID已存在",
            "file_type": "pdf",
            "file_src": "/data/docs/test.pdf",
            "vertical": "tech",
            "timestamp": 1712908800000
        }
        
        try:
            storage.insert_chunk(chunk_data)
        except Exception as e:
            logger.warning(f"预期错误: {e}")


def demo_integration_with_splitter():
    """演示与DocumentSplitter集成"""
    logger.info("\n=== 与DocumentSplitter集成示例 ===")
    
    logger.info("集成流程:")
    logger.info("  1. 使用DocumentSplitter切分文档")
    logger.info("  2. 为每个切片生成vector_id")
    logger.info("  3. 将切片信息存储到数据库")
    
    logger.info("\n示例代码:")
    logger.info("""
    from raginger.core.parse.splitter import DocumentSplitter
    from raginger.core.parse.database_storage import DatabaseStorage
    
    # 初始化
    splitter = DocumentSplitter(tokenizer, "token", 512, 50)
    storage = DatabaseStorage("chunks.db")
    
    # 切分文档
    chunks = splitter.split_single_document(
        document="文档内容...",
        doc_id="doc_001",
        doc_name="example.pdf"
    )
    
    # 存储到数据库
    for i, chunk in enumerate(chunks):
        chunk_data = {
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["doc_id"],
            "vector_id": f"vec_{i:03d}",  # 向量化后生成
            "chunk_position": chunk["chunk_index"],
            "title": chunk["doc_name"],
            "content": chunk["content"],
            "file_type": "pdf",
            "file_src": "/path/to/file.pdf",
            "vertical": "tech",
            "timestamp": int(time.time() * 1000)
        }
        storage.insert_chunk(chunk_data)
    """)


def cleanup_demo_files():
    """清理演示文件"""
    import glob
    
    demo_files = glob.glob("./demo_*.db")
    for file_path in demo_files:
        try:
            os.remove(file_path)
            logger.info(f"已清理: {file_path}")
        except Exception as e:
            logger.warning(f"清理失败 {file_path}: {e}")


def main():
    """主函数"""
    logger.add("database_storage_example.log", rotation="10 MB")
    
    logger.info("=== 数据库存储示例 ===")
    
    logger.info("\n注意：此示例将创建演示数据库文件")
    
    demo_basic_usage()
    
    demo_batch_insert()
    
    demo_query_by_doc_id()
    
    demo_query_by_vector_id()
    
    demo_query_by_vertical()
    
    demo_table_info()
    
    demo_error_handling()
    
    demo_integration_with_splitter()
    
    logger.info("\n是否清理演示文件？(y/n): ", end="")
    # cleanup_demo_files()
    
    logger.success("\n=== 示例完成 ===")


if __name__ == "__main__":
    main()
