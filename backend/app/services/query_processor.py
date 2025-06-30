"""
QueryProcessor 查询预处理模块
"""
from typing import List
import re

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