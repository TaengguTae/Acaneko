import sqlite3
from core.recall.recaller import Recaller
from core.embedding.embedding import Embedding
from core.rerank.qwen3_reranker import Qwen3Reranker

class SearchPipe:
    """
    搜索管道
    """

    def __init__(self, kb_name: str):
        self.kb_name = kb_name
        self.recaller = Recaller(
            faiss_index_path=f"../storage/kb/{kb_name}/index/faiss",
            lucene_index_path=f"../storage/kb/{kb_name}/index/lucene",
            embedding=Embedding("models/google/embeddinggemma-300m"),
            language="zh"
        )
        # 建立数据库连接
        self.db = sqlite3.connect(f"../storage/kb/{kb_name}/database.db")
        self.cursor = self.db.cursor()
        self.reranker = Qwen3Reranker(
            model_path=f"models/Qwen/Qwen3-Reranker-0.6B"
        )

    def run(self, query: str):
        vector_res = self.recaller.recall_vector(query)
        for r in vector_res:
            print(r["chunk_id"], r["score"])
        lucene_res = self.recaller.recall_bm25_natural(query)
        for r in lucene_res:
            print(r["chunk_id"], r["score"])
        recall_chunk_ids = [str(r["chunk_id"][4:]) for r in vector_res] + [str(r["chunk_id"]) for r in lucene_res]
        print(recall_chunk_ids)
        
        # 去重
        unique_chunk_ids = list(set(recall_chunk_ids))
        print(f"去重后chunk_ids: {unique_chunk_ids}")
        placeholders = ','.join(['?' for _ in unique_chunk_ids])
        query_sql = f"SELECT content FROM chunks WHERE chunk_id IN ({placeholders});"
        self.cursor.execute(query_sql, unique_chunk_ids)
        rows = self.cursor.fetchall()
        recall_content = [row[0] for row in rows]
        self.db.close()

        rank_scores = self.reranker.rerank(query, recall_content)
        for r in rank_scores:
            print(r)
            print("="*50)









if __name__ == "__main__":
    search_pipe = SearchPipe("ztmy")
    search_pipe.run("真夜中2026年的演唱会叫什么名字")
