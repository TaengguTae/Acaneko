"""
Qwen3 Reranker模块
使用Qwen3-Reranker模型进行文档重排序
"""

from typing import List, Optional, Tuple, Dict, Any

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from loguru import logger

from core.rerank.base import BaseReranker


class Qwen3Reranker(BaseReranker):
    """
    Qwen3 Reranker类
    
    使用Qwen3-Reranker模型对文档进行相关性打分和重排序。
    
    Attributes:
        model_path: 模型路径
        max_length: 最大序列长度
        instruction: 任务指令
        device: 运行设备
    """
    
    DEFAULT_INSTRUCTION = "Given a web search query, retrieve relevant passages that answer the query"
    DEFAULT_MAX_LENGTH = 8192
    
    def __init__(
        self,
        model_path: str,
        max_length: int = 8192,
        instruction: Optional[str] = None,
        device: Optional[str] = None,
        use_flash_attention: bool = False,
        torch_dtype: Optional[torch.dtype] = None
    ):
        """
        初始化Qwen3Reranker
        
        Args:
            model_path: 模型路径
            max_length: 最大序列长度（默认8192）
            instruction: 任务指令（默认使用通用检索指令）
            device: 运行设备（默认自动选择）
            use_flash_attention: 是否使用flash_attention_2加速
            torch_dtype: 模型数据类型（默认自动选择）
            
        Raises:
            ValueError: 当参数无效时抛出
            FileNotFoundError: 当模型文件不存在时抛出
        """
        if not model_path or not isinstance(model_path, str):
            raise ValueError(
                f"model_path must be a non-empty string, got {model_path}"
            )
        
        self.model_path = model_path
        self.max_length = max_length
        self.instruction = instruction or self.DEFAULT_INSTRUCTION
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Initializing Qwen3Reranker from: {model_path}")
        logger.info(f"Device: {self.device}, max_length: {max_length}")
        
        self._init_model(use_flash_attention, torch_dtype)
        self._init_tokens()
        
        logger.success("Qwen3Reranker initialized successfully")
    
    def _init_model(
        self,
        use_flash_attention: bool,
        torch_dtype: Optional[torch.dtype]
    ) -> None:
        """
        初始化模型和分词器
        
        Args:
            use_flash_attention: 是否使用flash_attention_2
            torch_dtype: 模型数据类型
        """
        model_kwargs = {}
        
        if use_flash_attention:
            model_kwargs["attn_implementation"] = "flash_attention_2"
        
        if torch_dtype is not None:
            model_kwargs["torch_dtype"] = torch_dtype
        elif self.device == "cuda":
            model_kwargs["torch_dtype"] = torch.float16
        
        logger.info("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            padding_side='left'
        )
        
        logger.info("Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            **model_kwargs
        )
        self.model.eval()
        
        if self.device == "cuda":
            self.model = self.model.cuda()
        
        logger.success("Model loaded successfully")
    
    def _init_tokens(self) -> None:
        """
        初始化特殊token和前后缀
        """
        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")
        
        prefix = (
            "<|im_start|>system\n"
            "Judge whether the Document meets the requirements based on the Query and the Instruct provided. "
            "Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n"
            "<|im_start|>user\n"
        )
        suffix = "<|im_end|>\n<|im_start|>assistant\n\n\n\n\n\n"
        
        self.prefix_tokens = self.tokenizer.encode(prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(suffix, add_special_tokens=False)
    
    def _format_instruction(self, query: str, doc: str) -> str:
        """
        格式化输入指令
        
        Args:
            query: 查询文本
            doc: 文档文本
            
        Returns:
            str: 格式化后的输入文本
        """
        return (
            f"<Instruct>: {self.instruction}\n"
            f"<Query>: {query}\n"
            f"<Document>: {doc}"
        )
    
    def _process_inputs(self, pairs: List[str]) -> dict:
        """
        处理输入文本对
        
        Args:
            pairs: 格式化后的文本对列表
            
        Returns:
            dict: 模型输入张量
        """
        max_content_length = self.max_length - len(self.prefix_tokens) - len(self.suffix_tokens)
        
        inputs = self.tokenizer(
            pairs,
            padding=False,
            truncation='longest_first',
            return_attention_mask=False,
            max_length=max_content_length
        )
        
        for i, ele in enumerate(inputs['input_ids']):
            inputs['input_ids'][i] = self.prefix_tokens + ele + self.suffix_tokens
        
        inputs = self.tokenizer.pad(
            inputs,
            padding=True,
            return_tensors="pt",
            max_length=self.max_length
        )
        
        for key in inputs:
            inputs[key] = inputs[key].to(self.model.device)
        
        return inputs
    
    @torch.no_grad()
    def _compute_logits(self, inputs: dict) -> List[float]:
        """
        计算相关性分数
        
        Args:
            inputs: 模型输入张量
            
        Returns:
            List[float]: 相关性分数列表
        """
        batch_scores = self.model(**inputs).logits[:, -1, :]
        true_vector = batch_scores[:, self.token_true_id]
        false_vector = batch_scores[:, self.token_false_id]
        batch_scores = torch.stack([false_vector, true_vector], dim=1)
        batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
        scores = batch_scores[:, 1].exp().tolist()
        
        return scores
    
    def compute_rank_score(
        self,
        query: str,
        documents: List[str],
        batch_size: int = 8
    ) -> List[Tuple[int, float]]:
        """
        计算文档相关性分数
        
        Args:
            query: 查询文本
            documents: 文档列表
            batch_size: 批处理大小（默认8）
            
        Returns:
            List[Tuple[int, float]]: 排序后的结果列表，每个元素为(文档索引, 分数)
            
        Raises:
            ValueError: 当参数无效时抛出
        """
        if not query or not isinstance(query, str):
            raise ValueError(
                f"query must be a non-empty string, got {query}"
            )
        
        if not documents or not isinstance(documents, list):
            raise ValueError(
                f"documents must be a non-empty list, got {documents}"
            )
        
        if batch_size <= 0:
            raise ValueError(
                f"batch_size must be positive, got {batch_size}"
            )
        
        logger.info(
            f"Computing rank scores for query: '{query[:50]}...' "
            f"with {len(documents)} documents"
        )
        
        all_scores = []
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            pairs = [
                self._format_instruction(query, doc)
                for doc in batch_docs
            ]
            
            inputs = self._process_inputs(pairs)
            scores = self._compute_logits(inputs)
            all_scores.extend(scores)
            
            logger.debug(
                f"Processed batch {i // batch_size + 1}: "
                f"{len(batch_docs)} documents"
            )
        
        results = list(enumerate(all_scores))
        results.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(
            f"Ranking completed, top score: {results[0][1]:.4f} "
            f"(doc index: {results[0][0]})"
        )
        
        return results
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: Optional[int] = None,
        batch_size: int = 8
    ) -> List[Tuple[int, float, str]]:
        """
        对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回前k个结果（默认返回全部）
            batch_size: 批处理大小
            
        Returns:
            List[Tuple[int, float, str]]: 重排序后的结果列表，
                每个元素为(文档索引, 分数, 文档内容)
        """
        ranked_results = self.compute_rank_score(query, documents, batch_size)
        
        if top_k is not None and top_k > 0:
            ranked_results = ranked_results[:top_k]
        
        results_with_docs = [
            (idx, score, documents[idx])
            for idx, score in ranked_results
        ]
        
        return results_with_docs
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            Dict[str, Any]: 模型配置信息
        """
        return {
            "model_path": self.model_path,
            "max_length": self.max_length,
            "instruction": self.instruction,
            "device": self.device,
            "model_dtype": str(self.model.dtype)
        }


if __name__ == "__main__":
    logger.add("qwen3_reranker.log", rotation="10 MB")
    
    model_path = r"models/Qwen/Qwen3-Reranker-0.6B"
    
    reranker = Qwen3Reranker(model_path)
    
    query = "What is the capital of China?"
    documents = [
        "The capital of China is Beijing.",
        "Gravity is a force that attracts two bodies towards each other.",
        "Beijing is the political and cultural center of China.",
        "Python is a popular programming language.",
    ]
    
    print("\n=== compute_rank_score 示例 ===")
    results = reranker.compute_rank_score(query, documents)
    for idx, score in results:
        print(f"文档 {idx}: 分数={score:.4f}, 内容={documents[idx][:50]}...")
    
    print("\n=== rerank 示例 (top_k=2) ===")
    top_results = reranker.rerank(query, documents, top_k=2)
    for idx, score, doc in top_results:
        print(f"文档 {idx}: 分数={score:.4f}")
        print(f"  内容: {doc}")
