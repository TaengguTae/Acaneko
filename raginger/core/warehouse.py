import json
from pathlib import Path
import uuid

from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer

from core.parse.splitter import DocumentSplitter
from core.parse.database_storage import DatabaseStorage
from core.embedding.embedding import Embedding
from core.index.lucene_index import LuceneIndex
from core.index.vector_index import FaissIndex


class Warehouse:
    """
    数据入库。
    """
    def __init__(
        self,
        
        # 知识库
        knowledge_base_name: str,
        
        # 切片
        chunk_size: int,
        chunk_overlap: int,
        split_type: str,

        # 嵌入模型
        embedding_model: str,

        # 语言
        language: str,
    ):
        self.knowledge_base_name = knowledge_base_name
        self.embedding_model = Path(f"models/{embedding_model}")
        self.language = language
        self.embedding = Embedding(str(self.embedding_model))
        
        self.tmp_file_path = Path(f"../storage/kb/{knowledge_base_name}/tmp_file_content")
        self.db_path = Path(f"../storage/kb/{knowledge_base_name}/database.db")
        self.lucene_index_path = Path(f"../storage/kb/{knowledge_base_name}/index/lucene")
        self.vector_index_path = Path(f"../storage/kb/{knowledge_base_name}/index/faiss")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lucene_index_path.mkdir(parents=True, exist_ok=True)
        self.vector_index_path.mkdir(parents=True, exist_ok=True)

        self.splitter = DocumentSplitter(
            AutoTokenizer.from_pretrained(str(self.embedding_model)), 
            split_type, chunk_size, chunk_overlap
        )
        self.db = DatabaseStorage(str(self.db_path))
        self.lucene_index = LuceneIndex(str(self.lucene_index_path), self.language)
        self.lucene_index.create_index_creator()
        self.vector_index = FaissIndex(self.embedding.get_embedding_dimension())
        
    
    def run(self):
        # TODO: 解析 
        # 假设已经做完
        import random
        documents = []
        for txt_file in Path("../data/ztmy").glob("*.txt"):
            with open(txt_file, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "doc_id": str(uuid.uuid4()),
                    "doc_name": txt_file.name,
                    "content": content,
                    "metadata": {
                        "timestamp": random.randint(10000000, 99999999),
                        "file_src": "ztmy",
                        "file_type": "txt"
                    }
                })

        # 遍历tmp_file_content中的json文件
        # documents = []
        # for json_file in self.tmp_file_path.glob("*.json"):
        #     with open(json_file, "r", encoding="utf-8") as f:
        #         data = json.load(f)
        #         documents.append({
        #             "doc_id": str(uuid.uuid4()),
        #             "doc_name": data.get("file_name", ""),
        #             "content": data.get("content", ""),
        #             "metadata": {
        #                 "timestamp": data.get("timestamp", ""),
        #                 "file_src": data.get("source", ""),
        #                 "file_type": data.get("file_type", "")
        #             }
        #         })
        
        chunks = self.splitter.split_documents(documents)
        with open("temp.json", "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)
        get_type = lambda k: {"content": "TEXT", "doc_name": "TEXT", "timestamp": "LONG"}.get(k, "ID")
        chunks_for_lucene = [{k: {"value": v, "type": get_type(k)} for k, v in chunk.items()} for chunk in chunks]
        
        # 写入lucene
        self.lucene_index.add_documents_from_maps(chunks_for_lucene)
        self.lucene_index.commit()
        self.lucene_index.close()

        # 写入faiss
        for i in range(0, len(chunks), interval:=15):
            batch = chunks[i:i+interval]
            texts = [chunk["content"] for chunk in batch]
            vector_ids = [chunk["vector_id"] for chunk in batch]
            vector = self.embedding.get_embedding(texts, content_type="document")
            self.vector_index.add_vectors(vector, vector_ids)
        self.vector_index.save_index(str(self.vector_index_path))

        # 写入数据库
        for chunk in chunks:
            chunk_data = {
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "vector_id": chunk["vector_id"],
                "chunk_position": chunk.get("chunk_index", 0),
                "title": chunk.get("doc_name", ""),
                "content": chunk["content"],
                "file_type": chunk.get("file_type", ""),
                "file_src": chunk.get("file_src", ""),
                "vertical": "file",
                "timestamp": chunk.get("timestamp", 0)
            }
            self.db.insert_chunk(chunk_data)
        self.db.close()


if __name__ == '__main__':
    warehouse = Warehouse(
        knowledge_base_name="ztmy",
        chunk_size=256,
        chunk_overlap=40,
        split_type="token",
        embedding_model="google/embeddinggemma-300m",
        language="zh"
    )
    warehouse.run()
