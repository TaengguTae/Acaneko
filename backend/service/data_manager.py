"""
数据存储管理
负责metadata.json的读写和文件操作
"""

import json
import os
import uuid
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from models import KnowledgeBase, DocumentInfo


class DataManager:
    """数据管理器"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.metadata_file = self.data_dir / "metadata.json"
        self._ensure_directories()

    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.metadata_file.exists():
            self._save_metadata({})

    def _load_metadata(self) -> Dict:
        """加载元数据"""
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_metadata(self, metadata: Dict):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def generate_id(self) -> str:
        """生成唯一ID"""
        return str(uuid.uuid4())

    def create_knowledge_base(self, request: dict) -> KnowledgeBase:
        """创建知识库"""
        kb_id = self.generate_id()
        kb_data = {
            "id": kb_id,
            "name": request["name"],
            "description": request["description"],
            "document_count": 0,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "chunk_size": request.get("chunk_size", 500),
            "overlap_size": request.get("overlap_size", 50),
            "vector_model": request.get("vector_model", "openai-3-small"),
            "language": request.get("language", "zh-CN")
        }

        metadata = self._load_metadata()
        metadata[kb_id] = kb_data
        self._save_metadata(metadata)

        kb_dir = self.data_dir / kb_id
        kb_dir.mkdir(exist_ok=True)
        (kb_dir / "Documents").mkdir(exist_ok=True)
        (kb_dir / "Index").mkdir(exist_ok=True)

        return KnowledgeBase(**kb_data)

    def get_knowledge_bases(self) -> List[KnowledgeBase]:
        """获取所有知识库"""
        metadata = self._load_metadata()
        return [KnowledgeBase(**kb_data) for kb_data in metadata.values()]

    def get_knowledge_base(self, kb_id: str) -> Optional[KnowledgeBase]:
        """获取单个知识库"""
        metadata = self._load_metadata()
        kb_data = metadata.get(kb_id)
        if kb_data:
            return KnowledgeBase(**kb_data)
        return None

    def update_knowledge_base(self, kb_id: str, updates: dict):
        """更新知识库"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        kb_data = metadata[kb_id]
        for key, value in updates.items():
            if value is not None:
                kb_data[key] = value

        self._save_metadata(metadata)

    def delete_knowledge_base(self, kb_id: str):
        """删除知识库"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        del metadata[kb_id]
        self._save_metadata(metadata)

        kb_dir = self.data_dir / kb_id
        if kb_dir.exists():
            import shutil
            shutil.rmtree(kb_dir)

    def upload_document(self, kb_id: str, filename: str, file_size: int) -> DocumentInfo:
        """上传文档"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        doc_id = self.generate_id()
        doc_data = {
            "id": doc_id,
            "name": filename,
            "size": file_size,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "chunks": 0
        }

        kb_data = metadata[kb_id]
        if "documents" not in kb_data:
            kb_data["documents"] = []

        kb_data["documents"].insert(0, doc_data)
        kb_data["document_count"] = len(kb_data["documents"])
        self._save_metadata(metadata)

        return DocumentInfo(**doc_data)

    def get_documents(self, kb_id: str) -> List[DocumentInfo]:
        """获取知识库文档列表"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        kb_data = metadata[kb_id]
        documents = kb_data.get("documents", [])
        return [DocumentInfo(**doc_data) for doc_data in documents]

    def delete_document(self, kb_id: str, doc_id: str):
        """删除文档"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        kb_data = metadata[kb_id]
        documents = kb_data.get("documents", [])

        doc_to_delete = None
        for doc in documents:
            if doc["id"] == doc_id:
                doc_to_delete = doc
                break

        if doc_to_delete:
            documents.remove(doc_to_delete)
            kb_data["document_count"] = len(documents)
            self._save_metadata(metadata)

            doc_path = self.data_dir / kb_id / "Documents" / doc_to_delete["name"]
            if doc_path.exists():
                doc_path.unlink()

    def batch_delete_documents(self, kb_id: str, doc_ids: List[str]):
        """批量删除文档"""
        for doc_id in doc_ids:
            self.delete_document(kb_id, doc_id)

    def update_document_status(self, kb_id: str, doc_id: str, status: str, chunks: int = 0):
        """更新文档解析状态"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        kb_data = metadata[kb_id]
        documents = kb_data.get("documents", [])

        for doc in documents:
            if doc["id"] == doc_id:
                doc["status"] = status
                doc["chunks"] = chunks
                break

        self._save_metadata(metadata)

    def reset_parse_status(self, kb_id: str):
        """重置解析状态"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        kb_data = metadata[kb_id]
        documents = kb_data.get("documents", [])

        for doc in documents:
            if doc["status"] == "failed":
                doc["status"] = "pending"
                doc["chunks"] = 0

        self._save_metadata(metadata)

    def get_parse_status(self, kb_id: str) -> dict:
        """获取解析状态"""
        metadata = self._load_metadata()
        if kb_id not in metadata:
            raise ValueError(f"Knowledge base {kb_id} not found")

        kb_data = metadata[kb_id]
        documents = kb_data.get("documents", [])

        total = len(documents)
        completed = sum(1 for doc in documents if doc["status"] == "completed")
        failed = sum(1 for doc in documents if doc["status"] == "failed")
        in_progress = sum(1 for doc in documents if doc["status"] == "parsing")

        percentage = (completed / total * 100) if total > 0 else 0

        return {
            "knowledge_base_id": kb_id,
            "total_documents": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "percentage": round(percentage, 2)
        }

    def save_document_file(self, kb_id: str, filename: str, file_content: bytes):
        """保存文档文件"""
        doc_dir = self.data_dir / kb_id / "Documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        file_path = doc_dir / filename
        with open(file_path, 'wb') as f:
            f.write(file_content)

        return file_path
