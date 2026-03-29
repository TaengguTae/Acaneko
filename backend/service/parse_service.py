"""
文档解析服务
负责文档解析、向量化和索引生成
"""

import asyncio
import aiohttp
from typing import Dict, Optional
from .data_manager import DataManager


class ParseService:
    """解析服务"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.parse_tasks: Dict[str, asyncio.Task] = {}

    async def parse_documents(self, kb_id: str, chunk_size: int, overlap_size: int, 
                          vector_model: str, language: str):
        """解析文档"""
        self.data_manager.reset_parse_status(kb_id)

        documents = self.data_manager.get_documents(kb_id)
        pending_docs = [doc for doc in documents if doc.status == "pending"]

        if not pending_docs:
            return {"message": "No pending documents to parse"}

        for doc in pending_docs:
            self.data_manager.update_document_status(kb_id, doc.id, "parsing")

        try:
            await self._call_parse_api(kb_id, chunk_size, overlap_size, vector_model, language)

            for doc in pending_docs:
                chunks = self._estimate_chunks(doc.size, chunk_size, overlap_size)
                self.data_manager.update_document_status(kb_id, doc.id, "completed", chunks)

            return {"message": f"Successfully parsed {len(pending_docs)} documents"}
        except Exception as e:
            for doc in pending_docs:
                self.data_manager.update_document_status(kb_id, doc.id, "failed")
            raise Exception(f"Parse failed: {str(e)}")

    async def _call_parse_api(self, kb_id: str, chunk_size: int, overlap_size: int,
                              vector_model: str, language: str):
        """调用远程解析API"""
        api_url = "http://localhost:8001/api/parse"

        payload = {
            "knowledge_base_id": kb_id,
            "chunk_size": chunk_size,
            "overlap_size": overlap_size,
            "vector_model": vector_model,
            "language": language
        }

        timeout = aiohttp.ClientTimeout(total=300)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(api_url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Parse API error: {response.status} - {error_text}")

                result = await response.json()
                return result

    def _estimate_chunks(self, file_size: int, chunk_size: int, overlap_size: int) -> int:
        """估算分块数量"""
        if overlap_size >= chunk_size:
            return 1

        effective_chunk = chunk_size - overlap_size
        if effective_chunk <= 0:
            return 1

        return max(1, (file_size // effective_chunk) + 1)

    async def check_parse_status(self, kb_id: str) -> Dict:
        """检查解析状态"""
        return self.data_manager.get_parse_status(kb_id)
