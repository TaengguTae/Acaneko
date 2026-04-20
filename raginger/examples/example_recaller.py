"""
示例：使用召回模块
演示如何使用Recaller进行向量召回、BM25召回和混合召回
"""

import numpy as np
from loguru import logger
from raginger.core.index.vector_index import FaissIndex
from raginger.core.index.lucene_index import LuceneIndex
from raginger.core.embedding.embedding import Embedding
from raginger.core.recall.recaller import Recaller
import json
import os


def build_sample_indices():
    """构建示例FAISS索引和Lucene索引"""
    logger.info("=== 构建示例索引 ===")
    
    dimension = 128
    num_docs = 10
    
    os.makedirs("data", exist_ok=True)
    
    logger.info(f"创建 {dimension} 维FAISS向量索引")
    faiss_index = FaissIndex(dimension)
    
    logger.info(f"生成 {num_docs} 个示例文档向量")
    np.random.seed(42)
    vectors = np.random.randn(num_docs, dimension).astype('float32')
    doc_ids = [f"doc_{i:03d}" for i in range(num_docs)]
    
    logger.info("添加向量到FAISS索引")
    faiss_index.add_vectors(vectors, doc_ids)
    
    logger.info("保存FAISS索引到 data/sample_faiss_index")
    faiss_index.save_index("data/sample_faiss_index")
    
    logger.success("FAISS索引构建完成")
    
    logger.info("\n构建Lucene索引...")
    logger.info("注意：Lucene索引需要JVM环境")
    logger.info("示例代码：")
    logger.info("""
    from raginger.core.index.lucene_index import LuceneIndex, FieldType
    
    # 设置JAR包路径（如果不在默认位置）
    LuceneIndex.set_jar_path("path/to/Acaneko-Lucene9.12.3-v1.0.jar")
    
    # 创建索引
    lucene_index = LuceneIndex("data/sample_lucene_index", language="zh")
    
    # 定义字段配置
    field_configs = [
        {"name": "chunk_id", "type": FieldType.ID},
        {"name": "title", "type": FieldType.TEXT},
        {"name": "content", "type": FieldType.TEXT},
        {"name": "category", "type": FieldType.STORED_ONLY},
    ]
    
    # 创建索引
    lucene_index.create_index(field_configs)
    
    # 添加文档
    docs = [
        {
            "chunk_id": "doc_000",
            "title": "机器学习简介",
            "content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习。",
            "category": "AI"
        },
        # ... 更多文档
    ]
    lucene_index.add_documents(docs)
    
    # 提交索引
    lucene_index.commit()
    """)
    
    logger.success("示例索引构建完成")
    
    return "data/sample_faiss_index", "data/sample_lucene_index"


def demo_vector_recall():
    """演示向量召回功能"""
    logger.info("\n=== 向量召回功能演示 ===")
    
    logger.info("向量召回使用FAISS索引进行相似度检索")
    logger.info("特点：基于语义相似度，能找到语义相近的文档")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 初始化Recaller
    recaller = Recaller(
        faiss_index_path="data/sample_faiss_index",
        lucene_index_path="data/sample_lucene_index",
        embedding=embedding
    )
    
    # 向量召回
    results = recaller.recall_vector(
        query="什么是机器学习？",
        topk=5,
        threshold=0.0
    )
    
    # 查看结果
    for result in results:
        print(f"文档ID: {result['chunk_id']}, 相似度: {result['score']:.4f}")
    
    # 关闭资源
    recaller.close()
    """)
    
    logger.info("\n参数说明：")
    logger.info("  - query: 查询文本")
    logger.info("  - topk: 返回结果数量（默认10）")
    logger.info("  - threshold: 相似度阈值，过滤低于此值的结果（默认0.0）")
    
    logger.success("\n向量召回演示完成")


def demo_bm25_natural_recall():
    """演示BM25自然语言召回功能"""
    logger.info("\n=== BM25自然语言召回功能演示 ===")
    
    logger.info("BM25召回使用Lucene索引进行关键词检索")
    logger.info("特点：基于关键词匹配，适合精确检索场景")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 初始化Recaller
    recaller = Recaller(
        faiss_index_path="data/sample_faiss_index",
        lucene_index_path="data/sample_lucene_index",
        embedding=embedding
    )
    
    # BM25自然语言召回
    results = recaller.recall_bm25_natural(
        query="机器学习 人工智能",
        topk=10,
        fields=["content", "title"]
    )
    
    # 查看结果
    for result in results:
        print(f"文档ID: {result['chunk_id']}, BM25分数: {result['score']:.4f}")
        print(f"存储字段: {result['fields']}")
    
    # 关闭资源
    recaller.close()
    """)
    
    logger.info("\n参数说明：")
    logger.info("  - query: 自然语言查询文本")
    logger.info("  - topk: 返回结果数量（默认10）")
    logger.info("  - fields: 搜索字段列表（默认['content', 'title']）")
    
    logger.success("\nBM25自然语言召回演示完成")


def demo_bm25_composite_recall():
    """演示BM25组合召回功能"""
    logger.info("\n=== BM25组合召回功能演示 ===")
    
    logger.info("BM25组合召回支持复杂的查询条件组合")
    logger.info("特点：支持TEXT、FILTER、RANGE等多种条件类型")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 初始化Recaller
    recaller = Recaller(
        faiss_index_path="data/sample_faiss_index",
        lucene_index_path="data/sample_lucene_index",
        embedding=embedding
    )
    
    # 构建查询条件
    conditions = [
        {
            "type": "TEXT",
            "fields": ["content", "title"],
            "keywords": ["机器学习", "深度学习"],
            "occur": "SHOULD"
        },
        {
            "type": "FILTER",
            "field": "category",
            "value": "AI",
            "occur": "MUST"
        }
    ]
    
    # BM25组合召回
    results = recaller.recall_bm25_composite(
        conditions=conditions,
        topk=10
    )
    
    # 查看结果
    for result in results:
        print(f"文档ID: {result['chunk_id']}, BM25分数: {result['score']:.4f}")
    
    # 关闭资源
    recaller.close()
    """)
    
    logger.info("\n条件类型说明：")
    logger.info("  - TEXT: 文本搜索条件")
    logger.info("    - fields: 搜索字段列表")
    logger.info("    - keywords: 关键词列表")
    logger.info("    - occur: MUST(必须匹配) / SHOULD(应该匹配) / MUST_NOT(必须不匹配)")
    
    logger.info("\n  - FILTER: 精确过滤条件")
    logger.info("    - field: 过滤字段")
    logger.info("    - value: 过滤值")
    logger.info("    - occur: 同上")
    
    logger.info("\n  - RANGE: 范围条件")
    logger.info("    - field: 范围字段")
    logger.info("    - min_value: 最小值")
    logger.info("    - max_value: 最大值")
    logger.info("    - occur: 同上")
    
    logger.success("\nBM25组合召回演示完成")


def demo_hybrid_recall():
    """演示混合召回功能"""
    logger.info("\n=== 混合召回功能演示 ===")
    
    logger.info("混合召回同时使用向量召回和BM25召回")
    logger.info("特点：结合语义相似度和关键词匹配，召回效果更好")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 初始化Recaller
    recaller = Recaller(
        faiss_index_path="data/sample_faiss_index",
        lucene_index_path="data/sample_lucene_index",
        embedding=embedding
    )
    
    # 混合召回
    results = recaller.recall_hybrid(
        query="什么是机器学习？",
        topk=5,
        vector_threshold=0.0,
        bm25_fields=["content", "title"]
    )
    
    # 查看向量召回结果
    print("向量召回结果：")
    for result in results["vector"]:
        print(f"  文档ID: {result['chunk_id']}, 相似度: {result['score']:.4f}")
    
    # 查看BM25召回结果
    print("\\nBM25召回结果：")
    for result in results["bm25"]:
        print(f"  文档ID: {result['chunk_id']}, BM25分数: {result['score']:.4f}")
    
    # 关闭资源
    recaller.close()
    """)
    
    logger.info("\n参数说明：")
    logger.info("  - query: 查询文本")
    logger.info("  - topk: 每种召回方式返回的结果数量（默认10）")
    logger.info("  - vector_threshold: 向量召回的相似度阈值（默认0.0）")
    logger.info("  - bm25_fields: BM25搜索字段列表（默认['content', 'title']）")
    
    logger.info("\n返回结果说明：")
    logger.info("  返回一个字典，包含两个键：")
    logger.info("  - vector: 向量召回结果列表")
    logger.info("  - bm25: BM25召回结果列表")
    
    logger.success("\n混合召回演示完成")


def demo_context_manager():
    """演示上下文管理器使用"""
    logger.info("\n=== 上下文管理器使用演示 ===")
    
    logger.info("使用with语句自动管理资源")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 使用上下文管理器
    with Recaller(
        faiss_index_path="data/sample_faiss_index",
        lucene_index_path="data/sample_lucene_index",
        embedding=embedding
    ) as recaller:
        # 向量召回
        vector_results = recaller.recall_vector("查询文本", topk=5)
        
        # BM25召回
        bm25_results = recaller.recall_bm25_natural("查询文本", topk=5)
        
        # 混合召回
        hybrid_results = recaller.recall_hybrid("查询文本", topk=5)
        
        # 获取索引信息
        info = recaller.get_index_info()
        print(f"索引信息: {info}")
    
    # 自动调用close()方法释放资源
    """)
    
    logger.success("\n上下文管理器演示完成")


def demo_get_index_info():
    """演示获取索引信息"""
    logger.info("\n=== 获取索引信息演示 ===")
    
    logger.info("获取当前索引的详细信息")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 初始化Recaller
    recaller = Recaller(
        faiss_index_path="data/sample_faiss_index",
        lucene_index_path="data/sample_lucene_index",
        embedding=embedding
    )
    
    # 获取索引信息
    info = recaller.get_index_info()
    
    print(f"FAISS索引路径: {info['faiss_index_path']}")
    print(f"Lucene索引路径: {info['lucene_index_path']}")
    print(f"Lucene语言: {info['lucene_language']}")
    print(f"向量维度: {info['embedding_dimension']}")
    print(f"FAISS向量数量: {info['faiss_vector_count']}")
    print(f"Lucene文档数量: {info['lucene_doc_count']}")
    
    # 关闭资源
    recaller.close()
    """)
    
    logger.info("\n返回信息说明：")
    logger.info("  - faiss_index_path: FAISS索引路径")
    logger.info("  - lucene_index_path: Lucene索引路径")
    logger.info("  - lucene_language: Lucene索引语言")
    logger.info("  - embedding_dimension: 向量维度")
    logger.info("  - faiss_vector_count: FAISS索引中的向量数量")
    logger.info("  - lucene_doc_count: Lucene索引中的文档数量")
    
    logger.success("\n获取索引信息演示完成")


def demo_performance_tips():
    """演示性能优化建议"""
    logger.info("\n=== 性能优化建议 ===")
    
    logger.info("1. 向量召回优化：")
    logger.info("   - 使用合适的向量维度（384或768）")
    logger.info("   - 对于大规模数据，使用IVF或HNSW索引")
    logger.info("   - 合理设置threshold过滤低相似度结果")
    
    logger.info("\n2. BM25召回优化：")
    logger.info("   - 选择合适的搜索字段")
    logger.info("   - 使用组合查询时合理设置occur条件")
    logger.info("   - 避免过于复杂的查询条件")
    
    logger.info("\n3. 混合召回优化：")
    logger.info("   - 根据场景调整topk值")
    logger.info("   - 可以对两种召回结果进行融合排序")
    logger.info("   - 考虑使用RRF(Reciprocal Rank Fusion)算法")
    
    logger.info("\n4. 资源管理：")
    logger.info("   - 使用上下文管理器自动释放资源")
    logger.info("   - 避免频繁创建和销毁Recaller实例")
    logger.info("   - 对于高并发场景，考虑使用连接池")
    
    logger.success("\n性能优化建议演示完成")


def demo_rag_integration():
    """演示与RAG系统集成"""
    logger.info("\n=== RAG系统集成示例 ===")
    
    logger.info("RAG系统工作流程：")
    logger.info("  1. 用户提出查询")
    logger.info("  2. 使用Recaller检索相关文档")
    logger.info("  3. 构建上下文（context）")
    logger.info("  4. 调用LLM生成答案")
    logger.info("  5. 返回答案和来源文档")
    
    logger.info("\n示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    from raginger.core.parse.database_storage import DatabaseStorage
    
    # 初始化组件
    embedding = Embedding("models/embedding")
    db_storage = DatabaseStorage("data/chunks.db")
    
    # 初始化Recaller
    recaller = Recaller(
        faiss_index_path="data/faiss_index",
        lucene_index_path="data/lucene_index",
        embedding=embedding
    )
    
    # 混合召回
    query = "什么是机器学习？"
    results = recaller.recall_hybrid(query, topk=5)
    
    # 获取文档内容
    context_docs = []
    for result in results["vector"]:
        chunk = db_storage.get_chunk_by_id(result["chunk_id"])
        if chunk:
            context_docs.append(chunk["content"])
    
    # 构建上下文
    context = "\\n".join(context_docs)
    
    # 调用LLM生成答案
    # answer = llm.generate(query, context)
    
    # 关闭资源
    recaller.close()
    """)
    
    logger.success("\nRAG集成演示完成")


def main():
    logger.add("recall_example.log", rotation="10 MB")
    
    logger.info("=== 召回模块使用示例 ===")
    logger.info("Recaller类支持向量召回、BM25召回和混合召回")
    
    build_sample_indices()
    demo_vector_recall()
    demo_bm25_natural_recall()
    demo_bm25_composite_recall()
    demo_hybrid_recall()
    demo_context_manager()
    demo_get_index_info()
    demo_performance_tips()
    demo_rag_integration()
    
    logger.info("\n=== 实际使用说明 ===")
    logger.info("要实际运行召回功能，需要：")
    logger.info("  1. 准备FAISS索引文件（使用FaissIndex创建）")
    logger.info("  2. 准备Lucene索引目录（使用LuceneIndex创建）")
    logger.info("  3. 准备Embedding模型（使用Embedding类加载）")
    logger.info("  4. 初始化Recaller并调用相应的召回方法")
    
    logger.info("\n完整示例代码：")
    logger.info("""
    from raginger.core.recall.recaller import Recaller
    from raginger.core.embedding.embedding import Embedding
    
    # 加载Embedding模型
    embedding = Embedding("models/embedding")
    
    # 初始化Recaller
    with Recaller(
        faiss_index_path="data/faiss_index",
        lucene_index_path="data/lucene_index",
        embedding=embedding
    ) as recaller:
        # 向量召回
        vector_results = recaller.recall_vector("查询文本", topk=5, threshold=0.7)
        
        # BM25自然语言召回
        bm25_results = recaller.recall_bm25_natural("查询文本", topk=5)
        
        # BM25组合召回
        conditions = [{"type": "TEXT", "fields": ["content"], "keywords": ["关键词"], "occur": "SHOULD"}]
        composite_results = recaller.recall_bm25_composite(conditions, topk=5)
        
        # 混合召回
        hybrid_results = recaller.recall_hybrid("查询文本", topk=5)
    """)
    
    logger.success("\n示例完成！")


if __name__ == "__main__":
    main()
