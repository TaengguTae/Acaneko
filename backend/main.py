"""
FastAPI主应用
提供知识库管理的所有API端点
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import uvicorn
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import (
    KnowledgeBase, CreateKnowledgeBaseRequest, UpdateKnowledgeBaseRequest,
    ParseDocumentsRequest, ParseStatusResponse, DocumentInfo, BatchDeleteDocumentsRequest
)
from backend.data_manager import DataManager
from backend.config import ConfigManager
from backend.parse_service import ParseService


app = FastAPI(
    title="RAG知识库管理API",
    description="提供知识库创建、文件管理、文档解析等功能",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

data_manager = DataManager()
config_manager = ConfigManager()
parse_service = ParseService(data_manager)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RAG知识库管理API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/vector-models", response_model=List)
async def get_vector_models():
    """获取向量模型列表"""
    try:
        return config_manager.get_vector_models()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/languages", response_model=List)
async def get_languages():
    """获取语言列表"""
    try:
        return config_manager.get_languages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases", response_model=List[KnowledgeBase])
async def get_knowledge_bases():
    """获取所有知识库"""
    try:
        return data_manager.get_knowledge_bases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases/{kb_id}", response_model=KnowledgeBase)
async def get_knowledge_base(kb_id: str):
    """获取单个知识库"""
    try:
        kb = data_manager.get_knowledge_base(kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail=f"Knowledge base {kb_id} not found")
        return kb
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases", response_model=KnowledgeBase)
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    """创建知识库"""
    try:
        kb = data_manager.create_knowledge_base(request.dict())
        return kb
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/knowledge-bases/{kb_id}", response_model=KnowledgeBase)
async def update_knowledge_base(kb_id: str, request: UpdateKnowledgeBaseRequest):
    """更新知识库"""
    try:
        updates = {k: v for k, v in request.dict().items() if v is not None}
        data_manager.update_knowledge_base(kb_id, updates)
        kb = data_manager.get_knowledge_base(kb_id)
        return kb
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge-bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    try:
        data_manager.delete_knowledge_base(kb_id)
        return {"message": f"Knowledge base {kb_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases/{kb_id}/documents", response_model=List[DocumentInfo])
async def get_documents(kb_id: str):
    """获取知识库文档列表"""
    try:
        return data_manager.get_documents(kb_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases/{kb_id}/documents/upload")
async def upload_document(kb_id: str, files: List[UploadFile] = File(...)):
    """上传文档"""
    try:
        uploaded_docs = []
        for file in files:
            file_content = await file.read()
            data_manager.save_document_file(kb_id, file.filename, file_content)
            
            doc = data_manager.upload_document(kb_id, file.filename, len(file_content))
            uploaded_docs.append(doc)
        
        return {
            "message": f"Successfully uploaded {len(uploaded_docs)} documents",
            "documents": uploaded_docs
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/knowledge-bases/{kb_id}/documents/{doc_id}")
async def delete_document(kb_id: str, doc_id: str):
    """删除文档"""
    try:
        data_manager.delete_document(kb_id, doc_id)
        return {"message": f"Document {doc_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases/{kb_id}/documents/batch-delete")
async def batch_delete_documents(kb_id: str, request: BatchDeleteDocumentsRequest):
    """批量删除文档"""
    try:
        data_manager.batch_delete_documents(kb_id, request.doc_ids)
        return {"message": f"Successfully deleted {len(request.doc_ids)} documents"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/knowledge-bases/{kb_id}/parse", response_model=dict)
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
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-bases/{kb_id}/parse-status", response_model=ParseStatusResponse)
async def get_parse_status(kb_id: str):
    """获取解析状态"""
    try:
        status = await parse_service.check_parse_status(kb_id)
        return ParseStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
