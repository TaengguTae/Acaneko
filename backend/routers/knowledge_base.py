"""
知识库管理路由
提供知识库CRUD、文档管理、文档解析等API端点
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import logging

from models import (
    KnowledgeBase,
    CreateKnowledgeBaseRequest,
    UpdateKnowledgeBaseRequest,
    DocumentInfo,
    BatchDeleteDocumentsRequest,
    ParseDocumentsRequest,
    ParseStatusResponse
)
from service import DataManager, ParseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge-bases", tags=["知识库管理"])


def init_router(data_manager: DataManager, parse_service: ParseService):
    """初始化路由，注入依赖"""
    
    @router.get("", response_model=List[KnowledgeBase])
    async def get_knowledge_bases():
        """获取所有知识库"""
        try:
            return data_manager.get_knowledge_bases()
        except Exception as e:
            logger.error(f"Failed to get knowledge bases: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{kb_id}", response_model=KnowledgeBase)
    async def get_knowledge_base(kb_id: str):
        """获取单个知识库"""
        try:
            kb = data_manager.get_knowledge_base(kb_id)
            if not kb:
                raise HTTPException(status_code=404, detail=f"Knowledge base {kb_id} not found")
            return kb
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get knowledge base {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("", response_model=KnowledgeBase)
    async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
        """创建知识库"""
        try:
            kb = data_manager.create_knowledge_base(request.dict())
            logger.info(f"Created knowledge base: {kb.id}")
            return kb
        except Exception as e:
            logger.error(f"Failed to create knowledge base: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.put("/{kb_id}", response_model=KnowledgeBase)
    async def update_knowledge_base(kb_id: str, request: UpdateKnowledgeBaseRequest):
        """更新知识库"""
        try:
            updates = {k: v for k, v in request.dict().items() if v is not None}
            data_manager.update_knowledge_base(kb_id, updates)
            kb = data_manager.get_knowledge_base(kb_id)
            logger.info(f"Updated knowledge base: {kb_id}")
            return kb
        except ValueError as e:
            logger.error(f"Knowledge base {kb_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to update knowledge base {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/{kb_id}")
    async def delete_knowledge_base(kb_id: str):
        """删除知识库"""
        try:
            data_manager.delete_knowledge_base(kb_id)
            logger.info(f"Deleted knowledge base: {kb_id}")
            return {"message": f"Knowledge base {kb_id} deleted successfully"}
        except ValueError as e:
            logger.error(f"Knowledge base {kb_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to delete knowledge base {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{kb_id}/documents", response_model=List[DocumentInfo])
    async def get_documents(kb_id: str):
        """获取知识库文档列表"""
        try:
            return data_manager.get_documents(kb_id)
        except ValueError as e:
            logger.error(f"Knowledge base {kb_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to get documents for {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{kb_id}/documents/upload")
    async def upload_document(kb_id: str, files: List[UploadFile] = File(...)):
        """上传文档"""
        try:
            uploaded_docs = []
            for file in files:
                file_content = await file.read()
                data_manager.save_document_file(kb_id, file.filename, file_content)
                
                doc = data_manager.upload_document(kb_id, file.filename, len(file_content))
                uploaded_docs.append(doc)
            
            logger.info(f"Uploaded {len(uploaded_docs)} documents to {kb_id}")
            return {
                "message": f"Successfully uploaded {len(uploaded_docs)} documents",
                "documents": uploaded_docs
            }
        except ValueError as e:
            logger.error(f"Knowledge base {kb_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to upload documents to {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/{kb_id}/documents/{doc_id}")
    async def delete_document(kb_id: str, doc_id: str):
        """删除文档"""
        try:
            data_manager.delete_document(kb_id, doc_id)
            logger.info(f"Deleted document {doc_id} from {kb_id}")
            return {"message": f"Document {doc_id} deleted successfully"}
        except ValueError as e:
            logger.error(f"Document {doc_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{kb_id}/documents/batch-delete")
    async def batch_delete_documents(kb_id: str, request: BatchDeleteDocumentsRequest):
        """批量删除文档"""
        try:
            data_manager.batch_delete_documents(kb_id, request.doc_ids)
            logger.info(f"Batch deleted {len(request.doc_ids)} documents from {kb_id}")
            return {"message": f"Successfully deleted {len(request.doc_ids)} documents"}
        except ValueError as e:
            logger.error(f"Failed to batch delete documents: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to batch delete documents: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/{kb_id}/parse", response_model=dict)
    async def parse_documents(kb_id: str, request: ParseDocumentsRequest):
        """开始解析文档"""
        try:
            result = await parse_service.parse_documents(
                kb_id,
                request.chunk_size,
                request.overlap_size,
                request.vector_model,
                request.language
            )
            logger.info(f"Started parsing documents for {kb_id}")
            return result
        except ValueError as e:
            logger.error(f"Knowledge base {kb_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to parse documents for {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/{kb_id}/parse-status", response_model=ParseStatusResponse)
    async def get_parse_status(kb_id: str):
        """获取解析状态"""
        try:
            status = await parse_service.check_parse_status(kb_id)
            return ParseStatusResponse(**status)
        except ValueError as e:
            logger.error(f"Knowledge base {kb_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to get parse status for {kb_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return router