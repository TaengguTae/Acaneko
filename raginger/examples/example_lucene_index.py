"""
示例：使用Lucene索引
演示如何使用LuceneIndex进行全文检索
"""

import os
from loguru import logger

from core.index.lucene_index import LuceneIndex, FieldType


def demo_basic_usage():
    """演示基本用法"""
    logger.info("\n=== 基本用法示例 ===")
    
    jar_path = r"core\index\libs\Acaneko-Lucene9.12.3-v1.0.jar"
    
    if not os.path.exists(jar_path):
        logger.warning(f"JAR file not found: {jar_path}")
        logger.info("Please ensure the JAR file exists in the libs directory")
        return
    
    LuceneIndex.set_jar_path(jar_path)
    
    index_path = "./demo_lucene_index"
    
    with LuceneIndex(index_path, "zh") as lucene:
        lucene.create_index_creator()
        
        documents = [
            {
                "chunk_id": {"value": "doc_001", "type": "ID"},
                "title": {"value": "全文检索入门", "type": "TEXT"},
                "content": {"value": "Lucene是一个高性能的全文检索库，广泛应用于搜索引擎。", "type": "TEXT"}
            },
            {
                "chunk_id": {"value": "doc_002", "type": "ID"},
                "title": {"value": "倒排索引原理", "type": "TEXT"},
                "content": {"value": "倒排索引是实现快速搜索的核心数据结构。", "type": "TEXT"}
            },
            {
                "chunk_id": {"value": "doc_003", "type": "ID"},
                "title": {"value": "BM25算法", "type": "TEXT"},
                "content": {"value": "BM25是Lucene默认的相关性评分算法。", "type": "TEXT"}
            }
        ]
        
        lucene.add_documents_from_maps(documents)
        lucene.commit()
        
        logger.info(f"索引创建完成，文档数: {lucene.get_doc_count()}")
    
    logger.info("\n=== 执行检索 ===")
    
    with LuceneIndex(index_path, "zh") as lucene:
        result = lucene.search("全文检索", 5)
        
        logger.info(f"找到 {result['total_hits']} 条结果")
        for hit in result['hits']:
            logger.info(f"  ID: {hit['chunk_id']}, Score: {hit['score']:.4f}")
            logger.info(f"  Title: {hit['fields'].get('title', 'N/A')}")


def demo_add_document_list():
    """演示使用List方式添加文档"""
    logger.info("\n=== 使用List方式添加文档 ===")
    
    jar_path = r"core\index\libs\Acaneko-Lucene9.12.3-v1.0.jar"
    
    if not os.path.exists(jar_path):
        logger.warning(f"JAR file not found: {jar_path}")
        return
    
    LuceneIndex.set_jar_path(jar_path)
    
    index_path = "./demo_lucene_index_list"
    
    with LuceneIndex(index_path, "zh") as lucene:
        lucene.create_index_creator()
        
        fields = [
            {"name": "chunk_id", "value": "doc_list_001", "type": "ID"},
            {"name": "title", "value": "Python编程", "type": "TEXT"},
            {"name": "content", "value": "Python是一种简单易学的编程语言。", "type": "TEXT"},
            {"name": "page_number", "value": 10, "type": "INT"},
            {"name": "create_time", "value": 1712908800000, "type": "LONG"}
        ]
        
        lucene.add_document(fields)
        lucene.commit()
        
        logger.info(f"文档添加完成，文档数: {lucene.get_doc_count()}")


def demo_natural_language_search():
    """演示自然语言查询"""
    logger.info("\n=== 自然语言查询示例 ===")
    
    jar_path = r"core\index\libs\Acaneko-Lucene9.12.3-v1.0.jar"
    
    if not os.path.exists(jar_path):
        logger.warning(f"JAR file not found: {jar_path}")
        return
    
    LuceneIndex.set_jar_path(jar_path)
    
    index_path = "./demo_lucene_index"
    
    with LuceneIndex(index_path, "zh") as lucene:
        result = lucene.search_natural(
            query_text="什么是全文检索？",
            fields=["content", "title"],
            top_n=5
        )
        
        logger.info(f"找到 {result['total_hits']} 条结果")
        for hit in result['hits']:
            logger.info(f"  ID: {hit['chunk_id']}, Score: {hit['score']:.4f}")
            logger.info(f"  Content: {hit['fields'].get('content', 'N/A')}")


def demo_json_search():
    """演示JSON查询"""
    logger.info("\n=== JSON查询示例 ===")
    
    jar_path = r"core\index\libs\Acaneko-Lucene9.12.3-v1.0.jar"
    
    if not os.path.exists(jar_path):
        logger.warning(f"JAR file not found: {jar_path}")
        return
    
    LuceneIndex.set_jar_path(jar_path)
    
    index_path = "./demo_lucene_index"
    
    with LuceneIndex(index_path, "zh") as lucene:
        json_query = """
        [
            {
                "type": "TEXT",
                "fields": ["content", "title"],
                "keywords": ["Lucene", "检索"],
                "occur": "SHOULD"
            }
        ]
        """
        
        result = lucene.search(json_query, 10)
        
        logger.info(f"找到 {result['total_hits']} 条结果")
        for hit in result['hits']:
            logger.info(f"  ID: {hit['chunk_id']}, Score: {hit['score']:.4f}")


def demo_composite_search():
    """演示组合查询"""
    logger.info("\n=== 组合查询示例 ===")
    
    jar_path = r"core\index\libs\Acaneko-Lucene9.12.3-v1.0.jar"
    
    if not os.path.exists(jar_path):
        logger.warning(f"JAR file not found: {jar_path}")
        return
    
    LuceneIndex.set_jar_path(jar_path)
    
    index_path = "./demo_lucene_index_list"
    
    with LuceneIndex(index_path, "zh") as lucene:
        conditions = [
            {
                "type": "TEXT",
                "fields": ["content", "title"],
                "keywords": ["编程", "语言"],
                "occur": "SHOULD"
            }
        ]
        
        result = lucene.search_composite(conditions, 10)
        
        logger.info(f"找到 {result['total_hits']} 条结果")
        for hit in result['hits']:
            logger.info(f"  ID: {hit['chunk_id']}, Score: {hit['score']:.4f}")


def demo_batch_operations():
    """演示批量操作"""
    logger.info("\n=== 批量操作示例 ===")
    
    jar_path = r"core\index\libs\Acaneko-Lucene9.12.3-v1.0.jar"
    
    if not os.path.exists(jar_path):
        logger.warning(f"JAR file not found: {jar_path}")
        return
    
    LuceneIndex.set_jar_path(jar_path)
    
    index_path = "./demo_lucene_index_batch"
    
    with LuceneIndex(index_path, "zh") as lucene:
        lucene.create_index_creator()
        
        documents = []
        for i in range(10):
            doc = {
                "chunk_id": {"value": f"batch_doc_{i:03d}", "type": "ID"},
                "title": {"value": f"文档标题 {i}", "type": "TEXT"},
                "content": {"value": f"这是第 {i} 个文档的内容，包含一些测试文本。", "type": "TEXT"}
            }
            documents.append(doc)
        
        lucene.add_documents_from_maps(documents)
        lucene.commit()
        
        logger.info(f"批量添加完成，文档数: {lucene.get_doc_count()}")
        logger.info(f"待提交文档数: {lucene.get_pending_doc_count()}")


def demo_field_types():
    """演示不同字段类型"""
    logger.info("\n=== 字段类型示例 ===")
    
    logger.info("支持的字段类型:")
    logger.info(f"  - ID: {FieldType.ID.value} - 不分词，精确匹配")
    logger.info(f"  - TEXT: {FieldType.TEXT.value} - 分词，全文检索")
    logger.info(f"  - STORED_ONLY: {FieldType.STORED_ONLY.value} - 仅存储，不索引")
    logger.info(f"  - LONG: {FieldType.LONG.value} - 长整型，支持范围查询")
    logger.info(f"  - INT: {FieldType.INT.value} - 整型，支持范围查询")


def main():
    """主函数"""
    logger.add("lucene_index_example.log", rotation="10 MB")
    
    logger.info("=== Lucene索引示例 ===")
    
    logger.info("\n注意：此示例需要JPype和Java环境")
    logger.info("请确保已安装:")
    logger.info("  1. Java 11或更高版本")
    logger.info("  2. pip install jpype1")
    logger.info("  3. JAR文件存在于libs目录")
    
    demo_field_types()
    
    demo_basic_usage()
    
    demo_add_document_list()
    
    demo_natural_language_search()
    
    demo_json_search()
    
    demo_composite_search()
    
    demo_batch_operations()
    
    logger.success("\n=== 示例完成 ===")


if __name__ == "__main__":
    main()
