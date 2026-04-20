"""
示例：使用向量索引
演示如何使用FaissIndex进行向量索引和检索
"""

import numpy as np
from loguru import logger
from core.index.vector_index import FaissIndex


def generate_sample_vectors(num_vectors: int, dimension: int):
    """生成示例向量"""
    np.random.seed(42)
    vectors = np.random.randn(num_vectors, dimension).astype('float32')
    return vectors


def main():
    logger.add("vector_index_example.log", rotation="10 MB")
    
    logger.info("=== 向量索引示例 ===")
    
    dimension = 128
    num_vectors = 1000
    
    logger.info(f"创建 {dimension} 维向量索引")
    index = FaissIndex(dimension)
    
    logger.info(f"生成 {num_vectors} 个示例向量")
    vectors = generate_sample_vectors(num_vectors, dimension)
    vector_ids = [f"doc_{i:04d}" for i in range(num_vectors)]
    
    logger.info("批量添加向量到索引...")
    index.add_vectors(vectors, vector_ids)
    
    logger.success(f"成功添加 {index.get_vector_count()} 个向量")
    
    logger.info("索引信息:")
    info = index.get_index_info()
    for key, value in info.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("\n=== 向量检索示例 ===")
    
    query_vector = vectors[0]
    logger.info("使用第一个向量作为查询向量")
    
    top_k = 5
    logger.info(f"查询最相似的 {top_k} 个向量...")
    results = index.search(query_vector, top_k=top_k)
    
    logger.success(f"查询完成，返回 {len(results)} 个结果:")
    for rank, (vector_id, score) in enumerate(results, 1):
        logger.info(f"  第{rank}名: ID={vector_id}, 相似度={score:.6f}")
    
    logger.info("\n=== 索引持久化示例 ===")
    
    save_path = "example_index"
    logger.info(f"保存索引到 {save_path}")
    index.save_index(save_path)
    logger.success("索引保存成功")
    
    logger.info(f"从 {save_path} 加载索引")
    loaded_index = FaissIndex.load_index(save_path)
    logger.success(f"索引加载成功，包含 {loaded_index.get_vector_count()} 个向量")
    
    logger.info("验证加载的索引...")
    results_loaded = loaded_index.search(query_vector, top_k=top_k)
    
    logger.info("比较原始索引和加载索引的查询结果:")
    for i, ((id1, score1), (id2, score2)) in enumerate(zip(results, results_loaded), 1):
        match = "✓" if id1 == id2 and abs(score1 - score2) < 1e-5 else "✗"
        logger.info(
            f"  结果{i}: {match} "
            f"原始(ID={id1}, 分数={score1:.6f}) vs "
            f"加载(ID={id2}, 分数={score2:.6f})"
        )
    
    logger.info("\n=== 其他功能示例 ===")
    
    logger.info("检查向量是否存在:")
    test_ids = ["doc_0000", "doc_0500", "doc_9999", "nonexistent"]
    for test_id in test_ids:
        exists = index.has_vector(test_id)
        logger.info(f"  {test_id}: {'存在' if exists else '不存在'}")
    
    logger.info("\n根据内部索引获取向量ID:")
    for internal_idx in [0, 100, 500, 999]:
        vector_id = index.get_vector_id(internal_idx)
        logger.info(f"  内部索引 {internal_idx} -> 向量ID: {vector_id}")
    
    logger.info("\n移除向量示例:")
    remove_id = "doc_0100"
    logger.info(f"移除向量: {remove_id}")
    success = index.remove_vector(remove_id)
    logger.info(f"移除结果: {'成功' if success else '失败'}")
    logger.info(f"向量是否存在: {'是' if index.has_vector(remove_id) else '否'}")
    
    logger.info("\n=== 批量查询示例 ===")
    
    num_queries = 5
    logger.info(f"使用前 {num_queries} 个向量进行批量查询")
    
    for i in range(num_queries):
        query = vectors[i]
        results = index.search(query, top_k=3)
        logger.info(f"\n查询 {i+1} (向量ID: doc_{i:04d}):")
        for rank, (vid, score) in enumerate(results, 1):
            logger.info(f"  第{rank}名: {vid} (相似度: {score:.6f})")
    
    logger.info("\n=== 清空索引示例 ===")
    logger.info(f"清空前向量数量: {index.get_vector_count()}")
    index.clear_index()
    logger.info(f"清空后向量数量: {index.get_vector_count()}")
    
    logger.success("\n示例完成！")


if __name__ == "__main__":
    main()
