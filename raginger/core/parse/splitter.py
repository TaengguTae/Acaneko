"""
文档切片器模块
用于RAG系统的文档预处理，支持按字符和按token两种切分模式
"""

from typing import List, Dict, Optional, Any, Callable
from functools import lru_cache
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter


class DocumentSplitter:
    """
    文档切片器类
    
    基于langchain-core和langchain-text-splitter库实现，
    支持按字符和按token两种切分模式，为RAG系统提供高质量的文档切片数据。
    
    Attributes:
        tokenizer: 分词器实例
        split_type: 切分类型（'character' 或 'token'）
        chunk_size: 切片大小
        chunk_overlap: 切片重叠大小
        additional_metadata_fields: 额外的元数据字段
        _splitter: langchain文本分割器实例
        _cache: 切片缓存字典
    """
    
    def __init__(
        self,
        tokenizer: Any,
        split_type: str = "character",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        additional_metadata_fields: Optional[Dict[str, Any]] = None
    ):
        """
        初始化文档切片器
        
        Args:
            tokenizer: 通过transforms库加载的分词器实例
            split_type: 切分类型，支持"character"（按字符）和"token"（按token）
            chunk_size: 切片大小（根据split_type分别表示字符数或token数）
            chunk_overlap: 切片重叠大小（根据split_type分别表示字符数或token数）
            additional_metadata_fields: 需要额外添加的元数据字段
            
        Raises:
            ValueError: 当参数不满足要求时抛出
        """
        self._validate_parameters(split_type, chunk_size, chunk_overlap)
        
        self.tokenizer = tokenizer
        self.split_type = split_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.additional_metadata_fields = additional_metadata_fields or {}
        
        self._splitter = self._create_splitter()
        self._cache: Dict[str, List[Dict]] = {}
        
        logger.info(
            f"DocumentSplitter initialized with split_type={split_type}, "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
    
    def _validate_parameters(
        self,
        split_type: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> None:
        """
        验证初始化参数
        
        Args:
            split_type: 切分类型
            chunk_size: 切片大小
            chunk_overlap: 切片重叠大小
            
        Raises:
            ValueError: 参数不满足要求时抛出
        """
        if split_type not in ["character", "token"]:
            raise ValueError(
                f"split_type must be 'character' or 'token', got '{split_type}'"
            )
        
        if chunk_size <= 0:
            raise ValueError(
                f"chunk_size must be greater than 0, got {chunk_size}"
            )
        
        if chunk_overlap < 0:
            raise ValueError(
                f"chunk_overlap must be non-negative, got {chunk_overlap}"
            )
        
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be less than "
                f"chunk_size ({chunk_size})"
            )
    
    def _create_splitter(self) -> TextSplitter:
        """
        创建langchain文本分割器实例
        
        Returns:
            TextSplitter: 配置好的文本分割器实例
        """

        # 定义通用的分隔符列表
        # 顺序极度重要：从大结构到小细节
        generic_separators = [
            "\n\n", 
            "\n", 
            r"(?<=[。！？；])", # 中文标点后切分
            r"(?<=[.!?;])",   # 英文标点后切分
            " ",
            ""
        ]
        if self.split_type == "character":
            return RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=generic_separators
            )
        else:
            return RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=self._token_length_function,
                separators=generic_separators
            )
    
    def _token_length_function(self, text: str) -> int:
        """
        计算文本的token数量
        
        Args:
            text: 输入文本
            
        Returns:
            int: token数量
        """
        try:
            return len(self.tokenizer.encode(text, add_special_tokens=False))
        except Exception as e:
            logger.warning(f"Failed to count tokens, using character count: {e}")
            return len(text)
    
    def _count_tokens(self, text: str) -> int:
        """
        计算文本的token数量（公共方法）
        
        Args:
            text: 输入文本
            
        Returns:
            int: token数量
        """
        return self._token_length_function(text)
    
    def _generate_cache_key(
        self,
        document: str,
        doc_id: str,
        doc_name: str
    ) -> str:
        """
        生成缓存键
        
        Args:
            document: 文档内容
            doc_id: 文档ID
            doc_name: 文档名称
            
        Returns:
            str: 缓存键
        """
        content_hash = hashlib.md5(document.encode()).hexdigest()
        return f"{doc_id}_{doc_name}_{content_hash}_{self.split_type}_{self.chunk_size}_{self.chunk_overlap}"
    
    def _get_chunk_length(self, content: str) -> int:
        """
        获取切片长度（根据split_type）
        
        Args:
            content: 切片内容
            
        Returns:
            int: 切片长度
        """
        if self.split_type == "character":
            return len(content)
        else:
            return self._count_tokens(content)
    
    def _find_chunk_indices(
        self,
        document: str,
        chunk_content: str,
        start_search_from: int = 0
    ) -> tuple[int, int]:
        """
        查找切片在原文档中的起始和结束索引
        
        Args:
            document: 原始文档
            chunk_content: 切片内容
            start_search_from: 开始搜索的位置
            
        Returns:
            tuple[int, int]: (起始索引, 结束索引)
        """
        start_index = document.find(chunk_content, start_search_from)
        if start_index == -1:
            start_index = start_search_from
        end_index = start_index + len(chunk_content)
        return start_index, end_index
    
    def split_single_document(
        self,
        document: str,
        doc_id: str,
        doc_name: str,
        metadata: dict = {}
    ) -> List[Dict]:
        """
        对单个文档进行切片处理
        
        Args:
            document: 文档内容字符串
            doc_id: 文档ID
            doc_name: 文档名称
            
        Returns:
            List[Dict]: 切片列表，每个切片包含chunk_id、content、doc_id等字段
            
        Raises:
            ValueError: 文档内容为空或无效时抛出
        """
        if not document or not isinstance(document, str):
            logger.warning(f"Empty or invalid document: doc_id={doc_id}")
            return []
        
        document = document.strip()
        if not document:
            logger.warning(f"Document is empty after stripping: doc_id={doc_id}")
            return []
        
        cache_key = self._generate_cache_key(document, doc_id, doc_name)
        if cache_key in self._cache:
            logger.debug(f"Using cached chunks for doc_id={doc_id}")
            return self._cache[cache_key]
        
        try:
            raw_chunks = self._splitter.split_text(document)
        except Exception as e:
            logger.error(f"Failed to split document {doc_id}: {e}")
            return []
        
        chunks = []
        search_position = 0
        
        for chunk_index, chunk_content in enumerate(raw_chunks):
            if not chunk_content.strip():
                continue
            
            start_index, end_index = self._find_chunk_indices(
                document, chunk_content, search_position
            )
            search_position = start_index + 1
            
            chunk_data = {
                "chunk_id": f"{doc_id}_{chunk_index}",
                "content": chunk_content,
                "doc_id": doc_id,
                "doc_name": doc_name,
                "chunk_length": self._get_chunk_length(chunk_content),
                "chunk_index": chunk_index,
                "token_count": self._count_tokens(chunk_content),
                "start_index": start_index,
                "end_index": end_index,
                "vector_id": f"v_v_{doc_id}_{chunk_index}"
            }
            
            chunk_data.update(metadata)
            
            chunks.append(chunk_data)
        
        self._cache[cache_key] = chunks
        logger.info(
            f"Split document {doc_id} into {len(chunks)} chunks "
            f"(split_type={self.split_type})"
        )
        
        return chunks
    
    def split_documents(
        self,
        documents: List[Dict[str, str]],
        max_workers: int = 4
    ) -> List[Dict]:
        """
        对一批文档进行批量切片处理
        
        Args:
            documents: 文档列表，每个文档应包含"content"、"doc_id"和"doc_name"字段
            max_workers: 并行处理的最大线程数
            
        Returns:
            List[Dict]: 所有文档的切片列表
            
        Raises:
            ValueError: 文档格式不正确时抛出
        """
        if not documents:
            logger.warning("Empty documents list provided")
            return []
        
        for idx, doc in enumerate(documents):
            if not isinstance(doc, dict):
                raise ValueError(f"Document at index {idx} is not a dictionary")
            if "content" not in doc or "doc_id" not in doc or "doc_name" not in doc:
                raise ValueError(
                    f"Document at index {idx} missing required fields "
                    f"(content, doc_id, doc_name)"
                )
        
        all_chunks = []
        
        if max_workers > 1 and len(documents) > 1:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_doc = {
                    executor.submit(
                        self.split_single_document,
                        doc["content"],
                        doc["doc_id"],
                        doc["doc_name"],
                        metadata=doc.get("metadata", {})
                    ): doc for doc in documents
                }
                
                for future in as_completed(future_to_doc):
                    doc = future_to_doc[future]
                    try:
                        chunks = future.result()
                        all_chunks.extend(chunks)
                    except Exception as e:
                        logger.error(
                            f"Failed to process document {doc['doc_id']}: {e}"
                        )
        else:
            for doc in documents:
                try:
                    chunks = self.split_single_document(
                        doc["content"],
                        doc["doc_id"],
                        doc["doc_name"],
                        metadata=doc.get("metadata", {})
                    )
                    all_chunks.extend(chunks)
                except Exception as e:
                    logger.error(
                        f"Failed to process document {doc['doc_id']}: {e}"
                    )
        
        logger.info(
            f"Split {len(documents)} documents into {len(all_chunks)} total chunks"
        )
        
        return all_chunks
    
    def clear_cache(self) -> None:
        """清空切片缓存"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_size(self) -> int:
        """
        获取缓存大小
        
        Returns:
            int: 缓存中的文档数量
        """
        return len(self._cache)
    
    def get_splitter_info(self) -> Dict[str, Any]:
        """
        获取切片器配置信息
        
        Returns:
            Dict[str, Any]: 切片器配置信息字典
        """
        return {
            "split_type": self.split_type,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "additional_metadata_fields": self.additional_metadata_fields,
            "cache_size": self.get_cache_size()
        }


if __name__ == '__main__':
    # 已检查, 正常
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("raginger/models/google/embeddinggemma-300m")
    text = """首先说句废话，ずっと真夜中でいいのに。这个组合的音乐特性是和acane息息相关的，也就是说“假设ztmy的主唱不是acane会怎么样”此类的问题是没有答案且（个人认为）没有意义的。先说studio的感受。acane最大的亮点（同时也是最可能不被喜欢的地方）就是她在处理一些音时表现出的爆发力。这点可以从第一首单曲“秒針を噛む”中副歌强有力的重音感受出来，在ztmy其他的歌曲中也或多或少地有体现（在『潜潜話』中尤其明显）。个人认为Vocal是服务于歌曲的，而在这些歌曲中Vocal和乐器的配合能够很好地表现整首曲子。例如“脳裏上のクラッカー”这种情感长时间地大量宣泄，没有一个穿透力强（当然有时候会被认为是吵闹）的Vocal是很难与伴奏中疯狂的Guitar、Bass和Drum平衡的。如果进入了整首歌的情绪，或许就会觉得acane的处理恰到好处，而非疯狂的嘶吼。而作为一个音乐风格多变且激进的组合，主唱对于不同曲子和情感的适应性和表现力是很重要的。从“Dear Mr「F」”的低吟浅唱到“あいつら全員同窓会”快速的歌词与节奏，从“過眠”这种类似清唱的歌曲再到“MILABO”这种伴奏火力全开的曲子，acane在契合伴奏旋律，展现歌曲的整体风格方面都能做的很好。当然，acane的唱法也有不让人满意的地方。在一些高音的处理上并不悦耳（比如Live中“秒針を噛む”经常出现的结尾低转高的长音），缺少必要的颤音，在层次性上缺少除力度变化外的表现手段等等。不得不承认，如果acane能解决这些问题，ztmy这个组合能创作出的音乐范围、表达出的情感会更加宽广与丰富。再说Live的感受。首先要强调一点，脱离歌曲的难度而去评判表现出的唱功是不合理的。像“マイノリティ脈絡”或者“あいつら全員同窓会”这种节奏快速、气口很短的歌曲的演唱难度是很大的，而acane在Live（CLEANING LABO)上的表现也是可圈可点的。此外，ztmy的很多歌曲音其实是比较高的（“脳裏上のクラッカー”、“マイノリティ脈絡”最高的是G#5而且是真声演唱），无论是真声演唱或者真假声转换都并不容易。而acane对于ztmy的歌曲的现场表现力也在逐渐提升。从一开始的“Midnight Forever”到“やきやきヤンキーツアー”再到“CLEANING LABO”，可以很明显地感觉到她水平的提高。尽管如此，依然存在楼主说的音准和音色的问题（音色薄可能是因为在studio里面有丰富的垫音与和声，而在Live里面较少），这是不可否认的。但是个人认为acane最需要的是在Live中表现出足以平衡ztmy丰富器乐的能力，作为Vocal同乐队一起完美演绎他们的歌曲，而在这点上她已经在一定程度上达到了要求。最后是对于音乐的一些看法。音乐打动人的地方有很多，不同的音乐作品给予人的感受、让人共鸣的点是不一样的。对于ずっと真夜中でいいのに。的歌曲，如果要讨论主唱的唱功，评判的标准应该是ta能否通过自己的演绎让他们的歌曲给予听众一定的感受。所以，如果主唱在一些音上跑调影响了这首歌的表现，那么可以说ta的唱功不足以胜任这首歌的Vocal。但是在听歌时除了关注一两句的几个音的细节，也需要从Vocal与乐器的配合、从整首歌的表现上评判一个Vocal。我想，在这点上，acane的唱功足以作为ずっと真夜中でいいのに。的主唱。PS：可以听听acane刚开始活动的时候的翻唱，大概就能知道她一贯的唱法以及这几年改变的地方。"""
    x = tokenizer.encode(text)
    print(x)
    splitter = DocumentSplitter(tokenizer=tokenizer, split_type="token", chunk_size=256, chunk_overlap=50)
    chunks = splitter.split_single_document(document=text, doc_id="test", doc_name="test")
    print()
    for i, ck in enumerate(chunks):
        print(f"第{i + 1}个chunk: ", f"token数: {len(tokenizer.encode(ck['content']))}, 内容: {ck['content']}")
        print('-----------------')
