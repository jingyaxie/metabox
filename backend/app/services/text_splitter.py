"""
高级文本分割服务
基于Dify和LangChain技术点实现
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """文本块数据结构"""
    content: str
    metadata: Dict[str, Any]
    parent_id: Optional[str] = None
    chunk_id: Optional[str] = None


class RecursiveCharacterTextSplitter:
    """递归字符分割器"""
    
    def __init__(
        self, 
        chunk_size: int = 512, 
        chunk_overlap: int = 64, 
        separators: Optional[List[str]] = None,
        keep_separator: bool = True
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.keep_separator = keep_separator
        
        # 默认分隔符优先级
        self.separators = separators or [
            "\n\n",  # 段落分隔
            "\n",    # 换行
            "。",     # 中文句号
            "！",     # 中文感叹号
            "？",     # 中文问号
            "；",     # 中文分号
            "：",     # 中文冒号
            "，",     # 中文逗号
            ". ",    # 英文句号
            "! ",    # 英文感叹号
            "? ",    # 英文问号
            "; ",    # 英文分号
            ": ",    # 英文冒号
            ", ",    # 英文逗号
            " ",     # 空格
            ""       # 字符级别
        ]
    
    def split_text(self, text: str) -> List[TextChunk]:
        """递归分割文本"""
        if not text.strip():
            return []
        
        # 尝试按不同分隔符分割
        for separator in self.separators:
            if separator in text:
                splits = self._split_text_with_separator(text, separator)
                if len(splits) > 1:
                    return self._merge_splits(splits)
        
        # 如果没有找到合适的分隔符，按字符分割
        return self._split_text_by_characters(text)
    
    def _split_text_with_separator(self, text: str, separator: str) -> List[str]:
        """使用指定分隔符分割文本"""
        if separator == "":
            return list(text)
        
        splits = text.split(separator)
        if self.keep_separator and separator != "":
            return [s + separator for s in splits[:-1]] + [splits[-1]]
        return splits
    
    def _merge_splits(self, splits: List[str]) -> List[TextChunk]:
        """合并分割结果，确保块大小合适"""
        merged_splits = []
        current_chunk = ""
        
        for split in splits:
            # 如果当前块加上新分割超过限制
            if len(current_chunk) + len(split) > self.chunk_size and current_chunk:
                # 保存当前块
                merged_splits.append(TextChunk(
                    content=current_chunk.strip(),
                    metadata={"splitter": "recursive_character"}
                ))
                
                # 开始新块，包含重叠部分
                if self.chunk_overlap > 0:
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + split
                else:
                    current_chunk = split
            else:
                current_chunk += split
        
        # 添加最后一个块
        if current_chunk.strip():
            merged_splits.append(TextChunk(
                content=current_chunk.strip(),
                metadata={"splitter": "recursive_character"}
            ))
        
        return merged_splits
    
    def _split_text_by_characters(self, text: str) -> List[TextChunk]:
        """按字符分割文本"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(TextChunk(
                    content=chunk.strip(),
                    metadata={"splitter": "recursive_character"}
                ))
        return chunks


class MarkdownHeaderTextSplitter:
    """Markdown标题分割器"""
    
    def __init__(self, headers_to_split_on: Optional[List[Tuple[str, str]]] = None):
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "标题1"),
            ("##", "标题2"),
            ("###", "标题3"),
            ("####", "标题4"),
            ("#####", "标题5"),
            ("######", "标题6"),
        ]
        
        # 构建正则表达式模式
        self.header_patterns = []
        for header, name in self.headers_to_split_on:
            pattern = rf"^{re.escape(header)}\s+(.+)$"
            self.header_patterns.append((pattern, name, len(header)))
    
    def split_text(self, text: str) -> List[TextChunk]:
        """按Markdown标题分割文本"""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        current_header = ""
        current_level = 0
        
        for line in lines:
            # 检查是否是标题行
            header_info = self._is_header_line(line)
            
            if header_info:
                # 保存当前块
                if current_chunk.strip():
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        metadata={
                            "splitter": "markdown_header",
                            "header": current_header,
                            "level": current_level
                        }
                    ))
                
                # 开始新块
                current_header = header_info["title"]
                current_level = header_info["level"]
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        
        # 添加最后一个块
        if current_chunk.strip():
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                metadata={
                    "splitter": "markdown_header",
                    "header": current_header,
                    "level": current_level
                }
            ))
        
        return chunks
    
    def _is_header_line(self, line: str) -> Optional[Dict[str, Any]]:
        """检查是否是标题行"""
        for pattern, name, level in self.header_patterns:
            match = re.match(pattern, line.strip())
            if match:
                return {
                    "title": match.group(1).strip(),
                    "level": level,
                    "name": name
                }
        return None


class ParentChildTextSplitter:
    """父子块分割器"""
    
    def __init__(
        self, 
        parent_chunk_size: int = 1024, 
        child_chunk_size: int = 256,
        child_overlap: int = 32
    ):
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=64
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_overlap
        )
    
    def split_text(self, text: str) -> List[TextChunk]:
        """生成父子块结构"""
        # 首先生成父块
        parent_chunks = self.recursive_splitter.split_text(text)
        
        all_chunks = []
        chunk_id_counter = 0
        
        for parent_chunk in parent_chunks:
            parent_id = f"parent_{chunk_id_counter}"
            chunk_id_counter += 1
            
            # 添加父块
            parent_chunk.chunk_id = parent_id
            parent_chunk.metadata.update({
                "splitter": "parent_child",
                "chunk_type": "parent",
                "parent_id": None
            })
            all_chunks.append(parent_chunk)
            
            # 生成子块
            child_chunks = self.child_splitter.split_text(parent_chunk.content)
            
            for i, child_chunk in enumerate(child_chunks):
                child_id = f"child_{chunk_id_counter}_{i}"
                child_chunk.chunk_id = child_id
                child_chunk.parent_id = parent_id
                child_chunk.metadata.update({
                    "splitter": "parent_child",
                    "chunk_type": "child",
                    "parent_id": parent_id,
                    "child_index": i
                })
                all_chunks.append(child_chunk)
        
        return all_chunks


class SemanticTextSplitter:
    """语义聚类分割器"""
    
    def __init__(
        self, 
        chunk_size: int = 512,
        embedding_model: Optional[str] = None,
        similarity_threshold: float = 0.8
    ):
        self.chunk_size = chunk_size
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
    
    async def split_text(self, text: str) -> List[TextChunk]:
        """基于语义相似度的文本分割"""
        # 首先按句子分割
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            return [TextChunk(
                content=text,
                metadata={"splitter": "semantic"}
            )]
        
        # 计算句子嵌入（这里简化处理，实际需要调用embedding服务）
        # sentence_embeddings = await self._get_embeddings(sentences)
        
        # 基于相似度聚类
        chunks = self._cluster_sentences(sentences)
        
        return [TextChunk(
            content=chunk,
            metadata={"splitter": "semantic"}
        ) for chunk in chunks]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 简单的句子分割，实际可以使用更复杂的NLP工具
        sentence_endings = r'[。！？.!?]'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _cluster_sentences(self, sentences: List[str]) -> List[str]:
        """基于相似度聚类句子"""
        # 简化实现：按长度聚类
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks


class TextSplitterFactory:
    """文本分割器工厂"""
    
    @staticmethod
    def create_splitter(
        splitter_type: str,
        **kwargs
    ) -> Any:
        """创建指定类型的分割器"""
        if splitter_type == "recursive":
            return RecursiveCharacterTextSplitter(**kwargs)
        elif splitter_type == "markdown":
            return MarkdownHeaderTextSplitter(**kwargs)
        elif splitter_type == "parent_child":
            return ParentChildTextSplitter(**kwargs)
        elif splitter_type == "semantic":
            return SemanticTextSplitter(**kwargs)
        else:
            raise ValueError(f"Unknown splitter type: {splitter_type}")
    
    @staticmethod
    def get_optimal_splitter(text: str, **kwargs) -> Any:
        """根据文本特征选择最优分割器"""
        # 检测文本类型
        if text.startswith('#') or '##' in text:
            # Markdown文档
            return MarkdownHeaderTextSplitter(**kwargs)
        elif len(text) > 10000:
            # 长文档，使用父子块分割
            return ParentChildTextSplitter(**kwargs)
        else:
            # 普通文档，使用递归分割
            return RecursiveCharacterTextSplitter(**kwargs) 