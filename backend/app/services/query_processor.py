"""
QueryProcessor 查询预处理模块
"""
from typing import List
from enum import Enum
import re

class QueryType(Enum):
    """查询类型枚举"""
    QUESTION = "question"      # 问题性查询
    INSTRUCTION = "instruction"  # 指令性查询
    CONCEPTUAL = "conceptual"    # 概念性查询
    FACTUAL = "factual"         # 事实性查询

class QueryProcessor:
    """查询预处理与清洗"""
    def __init__(self):
        pass

    async def process(self, query: str) -> str:
        """主入口：标准化、去噪、分词等"""
        query = self._normalize(query)
        query = self._remove_noise(query)
        query = self._strip(query)
        return query

    async def preprocess_query(self, query: str) -> str:
        """预处理查询"""
        return await self.process(query)

    def analyze_query_type(self, query: str) -> QueryType:
        """分析查询类型"""
        query_lower = query.lower()
        
        # 概念性查询（优先检查）
        if any(word in query_lower for word in ["什么是", "定义", "概念", "原理", "机制", "架构", "介绍"]):
            return QueryType.CONCEPTUAL
        
        # 问题性查询
        if any(word in query_lower for word in ["如何", "为什么", "怎么", "哪个", "哪里", "何时", "谁"]):
            return QueryType.QUESTION
        
        # 指令性查询
        if any(word in query_lower for word in ["安装", "配置", "设置", "运行", "启动", "停止", "重启"]):
            return QueryType.INSTRUCTION
        
        # 默认为事实性查询
        return QueryType.FACTUAL

    def _normalize(self, query: str) -> str:
        """全角转半角，统一大小写，去除特殊符号"""
        query = query.lower()
        query = re.sub(r'[，。！？、；：]', ' ', query)
        query = re.sub(r'\s+', ' ', query)
        return query

    def _remove_noise(self, query: str) -> str:
        """去除无意义词、停用词等（可扩展）"""
        # 简单实现，可扩展为加载停用词表
        noise_words = ["请问", "帮我", "一下", "能否", "如何", "怎么", "请", "帮忙"]
        for word in noise_words:
            query = query.replace(word, "")
        return query

    def _strip(self, query: str) -> str:
        return query.strip() 