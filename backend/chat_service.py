"""
聊天服务模块
处理Query理解、检索召回、大模型回答等功能
"""

import logging
from typing import List, Dict, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务类"""
    
    def __init__(self, data_manager):
        """初始化聊天服务"""
        self.data_manager = data_manager
        
    def understand_query(self, query: str, config: dict) -> dict:
        """
        Query理解处理
        分析用户查询，提取关键词、槽位等信息
        
        Args:
            query: 用户查询文本
            config: 配置参数，包含高级Query理解选项
            
        Returns:
            Query理解结果字典
        """
        try:
            logger.info(f"Processing query understanding for: {query}")
            
            result = {
                "keywords": [],
                "slots": [],
                "rewritten_query": "",
                "hyde": ""
            }
            
            advanced_options = config.get("query_understanding_options", {})
            
            if advanced_options.get("keyword_extraction", False):
                result["keywords"] = self._extract_keywords(query)
            
            if advanced_options.get("slot_extraction", False):
                result["slots"] = self._extract_slots(query)
            
            if advanced_options.get("query_rewriting", False):
                result["rewritten_query"] = self._rewrite_query(query)
            
            if advanced_options.get("hyde", False):
                result["hyde"] = self._generate_hyde(query)
            
            logger.info(f"Query understanding completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Query understanding failed: {str(e)}")
            raise
    
    def _extract_keywords(self, query: str) -> List[str]:
        """提取关键词（模拟实现）"""
        import re
        
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = list(set(words))
        
        return keywords[:10]
    
    def _extract_slots(self, query: str) -> List[str]:
        """提取槽位（模拟实现）"""
        slots = []
        
        if "价格" in query:
            slots.append("价格")
        if "数量" in query:
            slots.append("数量")
        if "时间" in query:
            slots.append("时间")
        
        return slots
    
    def _rewrite_query(self, query: str) -> str:
        """重写查询（模拟实现）"""
        return f"请提供关于{query}的详细信息"
    
    def _generate_hyde(self, query: str) -> str:
        """生成假设性文档嵌入（模拟实现）"""
        return f"假设用户在寻找关于{query}的相关文档内容"
    
    def retrieve_documents(self, query: str, kb_id: str, config: dict) -> List[dict]:
        """
        检索召回文档
        基于相似度阈值从知识库中检索相关文档
        
        Args:
            query: 查询文本
            kb_id: 知识库ID
            config: 配置参数，包含相似度阈值、Rerank设置
            
        Returns:
            检索结果列表
        """
        try:
            logger.info(f"Retrieving documents for KB: {kb_id}, query: {query}")
            
            similarity_threshold = config.get("similarity_threshold", 0.65)
            rerank_enabled = config.get("rerank_enabled", False)
            rerank_model = config.get("rerank_model", "bge-reranker")
            rerank_threshold = config.get("rerank_threshold", 0.5)
            
            kb_path = Path("data") / kb_id / "Index"
            if not kb_path.exists():
                logger.warning(f"Knowledge base index not found: {kb_path}")
                return []
            
            results = self._load_index_documents(kb_path, query, similarity_threshold)
            
            if rerank_enabled:
                results = self._rerank_results(results, rerank_threshold)
            
            logger.info(f"Retrieved {len(results)} documents")
            return results
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}")
            raise
    
    def _load_index_documents(self, kb_path: Path, query: str, threshold: float) -> List[dict]:
        """加载索引文档（模拟实现）"""
        results = []
        
        for i in range(1, 6):
            similarity = max(0.5, 1.0 - (i * 0.1))
            if similarity >= threshold:
                results.append({
                    "id": str(i),
                    "content": f"这是检索到的文档片段内容{i}，与查询'{query}'相关...",
                    "similarity": similarity,
                    "rank_score": similarity * 0.95,
                    "file_name": f"文档{i}.pdf",
                    "metadata": {
                        "page": i,
                        "section": f"第{i}章"
                    }
                })
        
        return sorted(results, key=lambda x: x["similarity"], reverse=True)
    
    def _rerank_results(self, results: List[dict], threshold: float) -> List[dict]:
        """Rerank结果（模拟实现）"""
        reranked = []
        
        for result in results:
            rank_score = result["similarity"] * 0.9 + (hash(result["id"]) % 10) * 0.01
            result["rank_score"] = min(rank_score, 1.0)
            
            if result["rank_score"] >= threshold:
                reranked.append(result)
        
        return sorted(reranked, key=lambda x: x["rank_score"], reverse=True)
    
    def generate_response(self, query: str, context: str, config: dict) -> str:
        """
        生成大模型回答
        基于查询和检索上下文生成最终回答
        
        Args:
            query: 用户查询
            context: 检索到的文档上下文
            config: 配置参数，包含大模型选择
            
        Returns:
            生成的回答文本
        """
        try:
            logger.info(f"Generating response for query: {query}")
            
            llm_model = config.get("llm_model", "gpt-4")
            
            response = self._call_llm_api(query, context, llm_model)
            
            logger.info(f"Response generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise
    
    def _call_llm_api(self, query: str, context: str, model: str) -> str:
        """调用大模型API（模拟实现）"""
        
        response_templates = {
            "gpt-4": f"基于您的问题'{query}'，我为您找到了相关信息。{context}这些建议可以帮助您解决问题。如果您需要更多详细信息，请随时告诉我。",
            "gpt-3.5": f"根据您的查询'{query}'，我检索到了相关资料。{context}希望这些信息对您有帮助。",
            "claude-3": f"针对您的问题'{query}'，我分析了相关文档。{context}这些是主要发现。",
            "qwen-72b": f"关于'{query}'，我为您整理了以下信息。{context}如有其他问题，欢迎继续提问。"
        }
        
        base_response = response_templates.get(model, response_templates["gpt-4"])
        
        if context:
            return base_response.replace("{context}", "结合检索到的文档内容，")
        else:
            return base_response.replace("{context}", "")
    
    def process_chat_request(self, request: dict) -> dict:
        """
        处理完整的聊天请求
        整合Query理解、检索召回、大模型回答的完整流程
        
        Args:
            request: 聊天请求，包含查询和配置
            
        Returns:
            完整的聊天响应
        """
        try:
            query = request.get("query", "")
            config = request.get("config", {})
            
            logger.info(f"Processing chat request: {query}")
            
            query_understanding = None
            retrieval_results = []
            
            if config.get("advanced_query_enabled", False):
                query_understanding = self.understand_query(query, config)
            
            if config.get("knowledge_base_id"):
                retrieval_results = self.retrieve_documents(
                    query,
                    config["knowledge_base_id"],
                    config
                )
            
            context = self._build_context(retrieval_results)
            
            response = self.generate_response(query, context, config)
            
            result = {
                "message": response,
                "query_understanding": query_understanding,
                "retrieval_results": retrieval_results
            }
            
            logger.info(f"Chat request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Chat request processing failed: {str(e)}")
            raise
    
    def _build_context(self, retrieval_results: List[dict]) -> str:
        """构建上下文字符串"""
        if not retrieval_results:
            return ""
        
        contexts = []
        for result in retrieval_results[:3]:
            contexts.append(result["content"][:200])
        
        return " ".join(contexts)