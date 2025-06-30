"""
混合分块服务
支持Parent-Child分块和结构化分块
"""
from typing import List, Dict, Any, Optional, Tuple
import re
import uuid
from dataclasses import dataclass
from enum import Enum
import logging

from app.services.text_splitter import TextSplitterFactory, TextChunk
from app.services.embedding_router import EmbeddingRouter, EmbeddingModel

logger = logging.getLogger(__name__)


class ChunkType(str, Enum):
    """分块类型"""
    PARENT = "parent"
    CHILD = "child"
    STANDALONE = "standalone"


@dataclass
class HybridChunk:
    """混合分块数据结构"""
    chunk_id: str
    content: str
    chunk_type: ChunkType
    parent_id: Optional[str] = None
    child_ids: List[str] = None
    metadata: Dict[str, Any] = None
    level: int = 0  # 层级深度
    
    def __post_init__(self):
        if self.child_ids is None:
            self.child_ids = []
        if self.metadata is None:
            self.metadata = {}


class HybridChunker:
    """混合分块器"""
    
    def __init__(self, embedding_router: Optional[EmbeddingRouter] = None):
        self.embedding_router = embedding_router or EmbeddingRouter()
        self.text_splitter_factory = TextSplitterFactory()
    
    async def create_hybrid_chunks(
        self,
        text: str,
        parent_chunk_size: int = 1024,
        child_chunk_size: int = 256,
        child_overlap: int = 32,
        use_semantic: bool = False,
        use_markdown_structure: bool = True
    ) -> List[HybridChunk]:
        """创建混合分块"""
        chunks = []
        
        # 检测是否为Markdown文档
        if use_markdown_structure and self._is_markdown_document(text):
            chunks = await self._create_markdown_hybrid_chunks(
                text, parent_chunk_size, child_chunk_size, child_overlap
            )
        else:
            chunks = await self._create_standard_hybrid_chunks(
                text, parent_chunk_size, child_chunk_size, child_overlap, use_semantic
            )
        
        return chunks
    
    def _is_markdown_document(self, text: str) -> bool:
        """检测是否为Markdown文档"""
        markdown_indicators = [
            r'^#\s+', r'^##\s+', r'^###\s+',  # 标题
            r'\*\*.*?\*\*', r'\*.*?\*',       # 粗体/斜体
            r'`.*?`', r'```[\w]*\n',          # 代码
            r'\[.*?\]\(.*?\)',                # 链接
            r'^\s*[-*+]\s+',                  # 列表
            r'^\s*\d+\.\s+'                   # 有序列表
        ]
        
        for pattern in markdown_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False
    
    async def _create_markdown_hybrid_chunks(
        self,
        text: str,
        parent_chunk_size: int,
        child_chunk_size: int,
        child_overlap: int
    ) -> List[HybridChunk]:
        """创建Markdown混合分块"""
        chunks = []
        
        # 使用Markdown标题分割器
        markdown_splitter = self.text_splitter_factory.create_splitter("markdown_header")
        header_chunks = markdown_splitter.split_text(text)
        
        for header_chunk in header_chunks:
            # 创建父块
            parent_id = str(uuid.uuid4())
            parent_chunk = HybridChunk(
                chunk_id=parent_id,
                content=header_chunk.content,
                chunk_type=ChunkType.PARENT,
                metadata={
                    "splitter": "markdown_header",
                    "header": header_chunk.metadata.get("header", ""),
                    "level": header_chunk.metadata.get("level", 0)
                },
                level=header_chunk.metadata.get("level", 0)
            )
            chunks.append(parent_chunk)
            
            # 如果父块内容较长，创建子块
            if len(header_chunk.content) > child_chunk_size:
                child_chunks = await self._create_child_chunks(
                    header_chunk.content, parent_id, child_chunk_size, child_overlap
                )
                chunks.extend(child_chunks)
                parent_chunk.child_ids = [chunk.chunk_id for chunk in child_chunks]
        
        return chunks
    
    async def _create_standard_hybrid_chunks(
        self,
        text: str,
        parent_chunk_size: int,
        child_chunk_size: int,
        child_overlap: int,
        use_semantic: bool
    ) -> List[HybridChunk]:
        """创建标准混合分块"""
        chunks = []
        
        # 选择分割器
        if use_semantic:
            splitter = self.text_splitter_factory.create_splitter("semantic")
        else:
            splitter = self.text_splitter_factory.create_splitter("recursive")
        
        # 创建父块
        parent_chunks = splitter.split_text(text)
        
        for i, parent_chunk in enumerate(parent_chunks):
            parent_id = str(uuid.uuid4())
            hybrid_parent = HybridChunk(
                chunk_id=parent_id,
                content=parent_chunk.content,
                chunk_type=ChunkType.PARENT,
                metadata={
                    "splitter": splitter.__class__.__name__,
                    "parent_index": i
                },
                level=0
            )
            chunks.append(hybrid_parent)
            
            # 创建子块
            child_chunks = await self._create_child_chunks(
                parent_chunk.content, parent_id, child_chunk_size, child_overlap
            )
            chunks.extend(child_chunks)
            hybrid_parent.child_ids = [chunk.chunk_id for chunk in child_chunks]
        
        return chunks
    
    async def _create_child_chunks(
        self,
        parent_content: str,
        parent_id: str,
        child_chunk_size: int,
        child_overlap: int
    ) -> List[HybridChunk]:
        """创建子块"""
        child_chunks = []
        
        # 使用递归分割器创建子块
        child_splitter = self.text_splitter_factory.create_splitter(
            "recursive",
            chunk_size=child_chunk_size,
            chunk_overlap=child_overlap
        )
        
        text_chunks = child_splitter.split_text(parent_content)
        
        for i, text_chunk in enumerate(text_chunks):
            child_id = str(uuid.uuid4())
            child_chunk = HybridChunk(
                chunk_id=child_id,
                content=text_chunk.content,
                chunk_type=ChunkType.CHILD,
                parent_id=parent_id,
                metadata={
                    "splitter": "recursive",
                    "child_index": i,
                    "parent_id": parent_id
                },
                level=1
            )
            child_chunks.append(child_chunk)
        
        return child_chunks
    
    async def create_semantic_chunks(
        self,
        text: str,
        chunk_size: int = 512,
        similarity_threshold: float = 0.8
    ) -> List[HybridChunk]:
        """创建语义分块"""
        chunks = []
        
        # 使用语义分割器
        semantic_splitter = self.text_splitter_factory.create_splitter("semantic")
        text_chunks = await semantic_splitter.split_text(text)
        
        for i, text_chunk in enumerate(text_chunks):
            chunk_id = str(uuid.uuid4())
            chunk = HybridChunk(
                chunk_id=chunk_id,
                content=text_chunk.content,
                chunk_type=ChunkType.STANDALONE,
                metadata={
                    "splitter": "semantic",
                    "chunk_index": i,
                    "similarity_threshold": similarity_threshold
                },
                level=0
            )
            chunks.append(chunk)
        
        return chunks
    
    def get_chunk_hierarchy(self, chunks: List[HybridChunk]) -> Dict[str, Any]:
        """获取分块层次结构"""
        hierarchy = {
            "parents": [],
            "children": [],
            "standalone": []
        }
        
        for chunk in chunks:
            if chunk.chunk_type == ChunkType.PARENT:
                hierarchy["parents"].append({
                    "id": chunk.chunk_id,
                    "content": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
                    "child_count": len(chunk.child_ids),
                    "level": chunk.level,
                    "metadata": chunk.metadata
                })
            elif chunk.chunk_type == ChunkType.CHILD:
                hierarchy["children"].append({
                    "id": chunk.chunk_id,
                    "parent_id": chunk.parent_id,
                    "content": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
                    "level": chunk.level,
                    "metadata": chunk.metadata
                })
            else:
                hierarchy["standalone"].append({
                    "id": chunk.chunk_id,
                    "content": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
                    "level": chunk.level,
                    "metadata": chunk.metadata
                })
        
        return hierarchy
    
    def get_chunk_statistics(self, chunks: List[HybridChunk]) -> Dict[str, Any]:
        """获取分块统计信息"""
        stats = {
            "total_chunks": len(chunks),
            "parent_chunks": len([c for c in chunks if c.chunk_type == ChunkType.PARENT]),
            "child_chunks": len([c for c in chunks if c.chunk_type == ChunkType.CHILD]),
            "standalone_chunks": len([c for c in chunks if c.chunk_type == ChunkType.STANDALONE]),
            "avg_parent_size": 0,
            "avg_child_size": 0,
            "max_level": 0
        }
        
        parent_sizes = [len(c.content) for c in chunks if c.chunk_type == ChunkType.PARENT]
        child_sizes = [len(c.content) for c in chunks if c.chunk_type == ChunkType.CHILD]
        
        if parent_sizes:
            stats["avg_parent_size"] = sum(parent_sizes) / len(parent_sizes)
        if child_sizes:
            stats["avg_child_size"] = sum(child_sizes) / len(child_sizes)
        
        if chunks:
            stats["max_level"] = max(c.level for c in chunks)
        
        return stats
    
    async def optimize_chunks(
        self,
        chunks: List[HybridChunk],
        target_chunk_size: int = 512,
        min_chunk_size: int = 100
    ) -> List[HybridChunk]:
        """优化分块大小"""
        optimized_chunks = []
        
        for chunk in chunks:
            if len(chunk.content) > target_chunk_size:
                # 分割过大的块
                sub_chunks = await self._split_large_chunk(
                    chunk, target_chunk_size, min_chunk_size
                )
                optimized_chunks.extend(sub_chunks)
            elif len(chunk.content) < min_chunk_size and chunk.chunk_type == ChunkType.STANDALONE:
                # 合并过小的独立块
                if optimized_chunks and optimized_chunks[-1].chunk_type == ChunkType.STANDALONE:
                    last_chunk = optimized_chunks[-1]
                    if len(last_chunk.content) + len(chunk.content) <= target_chunk_size:
                        last_chunk.content += "\n\n" + chunk.content
                        continue
                
                optimized_chunks.append(chunk)
            else:
                optimized_chunks.append(chunk)
        
        return optimized_chunks
    
    async def _split_large_chunk(
        self,
        chunk: HybridChunk,
        target_size: int,
        min_size: int
    ) -> List[HybridChunk]:
        """分割过大的块"""
        if chunk.chunk_type == ChunkType.PARENT:
            # 父块分割为多个子块
            sub_chunks = []
            content = chunk.content
            start = 0
            
            while start < len(content):
                end = start + target_size
                if end < len(content):
                    # 尝试在句子边界分割
                    sentence_end = content.rfind('.', start, end)
                    if sentence_end > start + min_size:
                        end = sentence_end + 1
                
                sub_content = content[start:end].strip()
                if sub_content:
                    sub_chunk = HybridChunk(
                        chunk_id=str(uuid.uuid4()),
                        content=sub_content,
                        chunk_type=ChunkType.CHILD,
                        parent_id=chunk.chunk_id,
                        metadata={
                            "splitter": "optimization",
                            "original_chunk_id": chunk.chunk_id,
                            "sub_index": len(sub_chunks)
                        },
                        level=chunk.level + 1
                    )
                    sub_chunks.append(sub_chunk)
                
                start = end
            
            return sub_chunks
        else:
            # 其他类型的块直接分割
            splitter = self.text_splitter_factory.create_splitter(
                "recursive",
                chunk_size=target_size,
                chunk_overlap=50
            )
            
            text_chunks = splitter.split_text(chunk.content)
            sub_chunks = []
            
            for i, text_chunk in enumerate(text_chunks):
                sub_chunk = HybridChunk(
                    chunk_id=str(uuid.uuid4()),
                    content=text_chunk.content,
                    chunk_type=chunk.chunk_type,
                    parent_id=chunk.parent_id,
                    metadata={
                        "splitter": "optimization",
                        "original_chunk_id": chunk.chunk_id,
                        "sub_index": i
                    },
                    level=chunk.level
                )
                sub_chunks.append(sub_chunk)
            
            return sub_chunks 