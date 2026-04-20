"""
示例：使用文本向量化
演示如何使用Embedding类进行文本向量化
"""

import numpy as np
from loguru import logger
from core.embedding.embedding import Embedding


def main():
    logger.add("embedding_example.log", rotation="10 MB")
    
    logger.info("=== 文本向量化示例 ===")
    
    logger.info("\n注意：此示例需要下载模型，首次运行可能需要较长时间")
    logger.info("如果不想下载模型，可以使用本地模型路径")
    
    model_name = r"models\google\embeddinggemma-300m"
    logger.info(f"\n加载模型: {model_name}")
    
    try:
        embedding = Embedding(model_name)
        logger.success(f"模型加载成功，向量维度: {embedding.get_embedding_dimension()}")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        logger.info("请确保已安装sentence-transformers库，并且网络连接正常")
        return
    
    logger.info("\n=== 单个文本向量化 ===")
    
    text = "这是一个测试文本，用于演示向量化功能。"
    logger.info(f"输入文本: {text}")
    
    vector = embedding.get_embedding(text, content_type="document")
    logger.success(f"向量化完成，形状: {vector.shape}")
    logger.info(f"向量类型: {type(vector)}")
    logger.info(f"向量前10个值: {vector[:10]}")
    
    logger.info("\n=== 批量文本向量化 ===")
    
    texts = [
        "机器学习是人工智能的一个分支",
        "深度学习使用神经网络进行学习",
        "自然语言处理是AI的重要应用"
    ]
    
    logger.info(f"输入 {len(texts)} 个文本:")
    for i, text in enumerate(texts, 1):
        logger.info(f"  {i}. {text}")
    
    vectors = embedding.get_embedding(texts, content_type="document")
    logger.success(f"批量向量化完成，形状: {vectors.shape}")
    
    logger.info("\n=== 相似度计算示例 ===")
    
    query = "什么是机器学习？"
    logger.info(f"查询文本: {query}")
    
    query_vector = embedding.get_embedding(query, content_type="query")
    
    cosine_similarities = np.dot(vectors, query_vector) / (
        np.linalg.norm(vectors, axis=1) * np.linalg.norm(query_vector)
    )
    
    logger.info("\n文档与查询的相似度:")
    sorted_indices = np.argsort(cosine_similarities)[::-1]
    for idx in sorted_indices:
        logger.info(
            f"  文档{idx+1}: {cosine_similarities[idx]:.4f} - {texts[idx]}"
        )
    
    logger.info("\n=== 模型信息 ===")
    
    info = embedding.get_model_info()
    logger.info("模型详细信息:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("\n=== 性能测试 ===")
    
    import time
    
    batch_sizes = [1, 10, 100]
    
    for batch_size in batch_sizes:
        test_texts = [f"测试文本 {i}" for i in range(batch_size)]
        
        start_time = time.time()
        _ = embedding.get_embedding(test_texts, content_type="document")
        elapsed_time = time.time() - start_time
        
        logger.info(
            f"批量大小 {batch_size:3d}: {elapsed_time:.4f} 秒 "
            f"({elapsed_time/batch_size*1000:.2f} 毫秒/文本)"
        )
    
    logger.info("\n=== prefix配置示例 ===")
    
    logger.info("如果模型目录下有 config_sentence_transformers.json 文件:")
    logger.info("  - query类型文本会自动添加 query_prefix")
    logger.info("  - document类型文本会自动添加 document_prefix")
    logger.info("\n示例配置文件内容:")
    logger.info('  {')
    logger.info('    "query_prefix": "query: ",')
    logger.info('    "document_prefix": "passage: "')
    logger.info('  }')
    
    logger.info("\n=== 实际应用场景 ===")
    
    logger.info("1. 文档检索：将文档和查询向量化后计算相似度")
    logger.info("2. 语义搜索：基于向量相似度的语义搜索")
    logger.info("3. 聚类分析：对文本向量进行聚类")
    logger.info("4. 推荐系统：基于向量相似度的内容推荐")
    
    logger.success("\n示例完成！")


if __name__ == "__main__":
    main()
