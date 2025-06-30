"""
MultiQueryExpander 多查询扩展模块
支持LLM扩展、同义词扩展等多种策略
"""
from typing import List, Dict, Any, Optional
import asyncio
import re
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """查询类型"""
    FACTUAL = "factual"      # 事实性查询
    CONCEPTUAL = "conceptual"  # 概念性查询
    QUESTION = "question"    # 问题性查询
    INSTRUCTION = "instruction"  # 指令性查询


class ExpansionStrategy(str, Enum):
    """扩展策略"""
    SYNONYMS = "synonyms"           # 同义词扩展
    PARAPHRASE = "paraphrase"       # 句式变换
    CONCEPT = "concept"             # 概念扩展
    QUESTION = "question"           # 问题形式
    HYBRID = "hybrid"               # 混合策略


class MultiQueryExpander:
    """多查询扩展器"""
    
    def __init__(self, llm_client=None, expansion_count: int = 3):
        self.llm_client = llm_client
        self.expansion_count = expansion_count
        
        # 同义词词典（可扩展为加载外部词典）
        self.synonym_dict = {
            "python": ["python编程", "python开发", "python语言"],
            "机器学习": ["人工智能", "AI", "深度学习", "监督学习"],
            "安装": ["配置", "设置", "部署", "搭建"],
            "问题": ["错误", "异常", "故障", "bug"],
            "如何": ["怎么", "怎样", "方法", "步骤"],
            "为什么": ["原因", "理由", "优势", "好处"],
            "react": ["react框架", "react开发", "react.js"],
            "vue": ["vue框架", "vue开发", "vue.js"],
            "数据库": ["数据存储", "数据管理", "DB"],
            "API": ["接口", "服务", "端点", "endpoint"]
        }
    
    async def expand_query(self, query: str, context: str = None, 
                          strategy: ExpansionStrategy = ExpansionStrategy.HYBRID) -> List[str]:
        """扩展查询"""
        try:
            # 1. 查询分析
            query_type = self._analyze_query_type(query)
            
            # 2. 根据策略选择扩展方法
            if strategy == ExpansionStrategy.SYNONYMS:
                expansions = self._synonym_expansion(query)
            elif strategy == ExpansionStrategy.PARAPHRASE:
                expansions = await self._paraphrase_expansion(query, context)
            elif strategy == ExpansionStrategy.CONCEPT:
                expansions = self._concept_expansion(query)
            elif strategy == ExpansionStrategy.QUESTION:
                expansions = self._question_expansion(query)
            else:  # HYBRID
                expansions = await self._hybrid_expansion(query, context, query_type)
            
            # 3. 去重和过滤
            all_queries = [query] + expansions
            unique_queries = self._deduplicate_queries(all_queries)
            
            # 4. 限制数量
            return unique_queries[:self.expansion_count + 1]  # +1 for original query
            
        except Exception as e:
            logger.error(f"查询扩展失败: {e}")
            return [query]  # 降级返回原始查询
    
    def _analyze_query_type(self, query: str) -> QueryType:
        """分析查询类型"""
        query_lower = query.lower()
        
        # 问题性查询
        if any(word in query_lower for word in ["如何", "怎么", "怎样", "为什么", "什么", "哪里"]):
            return QueryType.QUESTION
        
        # 指令性查询
        if any(word in query_lower for word in ["安装", "配置", "设置", "部署", "运行", "启动"]):
            return QueryType.INSTRUCTION
        
        # 概念性查询
        if any(word in query_lower for word in ["是什么", "定义", "概念", "原理", "机制"]):
            return QueryType.CONCEPTUAL
        
        # 默认为事实性查询
        return QueryType.FACTUAL
    
    def _synonym_expansion(self, query: str) -> List[str]:
        """同义词扩展"""
        expansions = []
        query_lower = query.lower()
        
        for word, synonyms in self.synonym_dict.items():
            if word in query_lower:
                for synonym in synonyms:
                    expanded = query_lower.replace(word, synonym)
                    if expanded != query_lower:
                        expansions.append(expanded)
        
        return expansions[:self.expansion_count]
    
    async def _paraphrase_expansion(self, query: str, context: str = None) -> List[str]:
        """句式变换扩展"""
        if not self.llm_client:
            return self._fallback_paraphrase(query)
        
        try:
            prompt = self._generate_paraphrase_prompt(query, context)
            response = await self.llm_client.generate(prompt)
            expansions = self._parse_llm_response(response)
            return expansions[:self.expansion_count]
        except Exception as e:
            logger.error(f"LLM句式变换失败: {e}")
            return self._fallback_paraphrase(query)
    
    def _fallback_paraphrase(self, query: str) -> List[str]:
        """降级句式变换"""
        expansions = []
        
        # 简单的句式变换规则
        if "如何" in query:
            expansions.append(query.replace("如何", "怎么"))
            expansions.append(query.replace("如何", "怎样"))
        
        if "为什么" in query:
            expansions.append(query.replace("为什么", "原因"))
            expansions.append(query.replace("为什么", "优势"))
        
        if "是什么" in query:
            expansions.append(query.replace("是什么", "定义"))
            expansions.append(query.replace("是什么", "概念"))
        
        return expansions[:self.expansion_count]
    
    def _concept_expansion(self, query: str) -> List[str]:
        """概念扩展"""
        expansions = []
        query_lower = query.lower()
        
        # 概念映射
        concept_mapping = {
            "python": ["编程语言", "开发工具", "脚本语言"],
            "机器学习": ["人工智能", "数据科学", "算法"],
            "数据库": ["数据存储", "数据管理", "信息管理"],
            "web开发": ["前端开发", "后端开发", "全栈开发"],
            "API": ["接口", "服务", "数据交换"],
            "部署": ["发布", "上线", "运维", "配置"]
        }
        
        for concept, related_concepts in concept_mapping.items():
            if concept in query_lower:
                for related in related_concepts:
                    expanded = query_lower.replace(concept, related)
                    if expanded != query_lower:
                        expansions.append(expanded)
        
        return expansions[:self.expansion_count]
    
    def _question_expansion(self, query: str) -> List[str]:
        """问题形式扩展"""
        expansions = []
        
        # 将陈述句转换为疑问句
        if not any(word in query for word in ["如何", "怎么", "为什么", "什么", "哪里"]):
            if "安装" in query:
                expansions.append(f"如何{query}")
                expansions.append(f"怎么{query}")
            elif "配置" in query:
                expansions.append(f"如何{query}")
                expansions.append(f"怎么{query}")
            elif "使用" in query:
                expansions.append(f"如何{query}")
                expansions.append(f"怎么{query}")
        
        return expansions[:self.expansion_count]
    
    async def _hybrid_expansion(self, query: str, context: str, query_type: QueryType) -> List[str]:
        """混合扩展策略"""
        all_expansions = []
        
        # 根据查询类型选择扩展策略
        if query_type == QueryType.FACTUAL:
            all_expansions.extend(self._synonym_expansion(query))
            all_expansions.extend(self._concept_expansion(query))
        elif query_type == QueryType.CONCEPTUAL:
            all_expansions.extend(self._concept_expansion(query))
            all_expansions.extend(await self._paraphrase_expansion(query, context))
        elif query_type == QueryType.QUESTION:
            all_expansions.extend(await self._paraphrase_expansion(query, context))
            all_expansions.extend(self._synonym_expansion(query))
        elif query_type == QueryType.INSTRUCTION:
            all_expansions.extend(self._question_expansion(query))
            all_expansions.extend(self._synonym_expansion(query))
        
        return all_expansions[:self.expansion_count]
    
    def _generate_paraphrase_prompt(self, query: str, context: str = None) -> str:
        """生成句式变换提示"""
        prompt = f"""
请为以下查询生成{self.expansion_count}个不同的表达方式，保持语义相似但用词和句式不同：

原始查询：{query}

{f"上下文：{context}" if context else ""}

请生成{self.expansion_count}个扩展查询，每行一个：
"""
        return prompt.strip()
    
    def _parse_llm_response(self, response: str) -> List[str]:
        """解析LLM响应"""
        lines = response.strip().split('\n')
        expansions = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('原始查询'):
                # 清理行号等前缀
                line = re.sub(r'^\d+\.\s*', '', line)
                line = re.sub(r'^[-*]\s*', '', line)
                if line:
                    expansions.append(line)
        
        return expansions
    
    def _deduplicate_queries(self, queries: List[str]) -> List[str]:
        """去重查询"""
        seen = set()
        unique_queries = []
        
        for query in queries:
            query_normalized = query.lower().strip()
            if query_normalized not in seen:
                seen.add(query_normalized)
                unique_queries.append(query)
        
        return unique_queries
    
    def add_synonyms(self, word: str, synonyms: List[str]):
        """添加同义词"""
        if word not in self.synonym_dict:
            self.synonym_dict[word] = []
        self.synonym_dict[word].extend(synonyms)
    
    def get_expansion_stats(self, query: str) -> Dict[str, Any]:
        """获取扩展统计信息"""
        query_type = self._analyze_query_type(query)
        synonym_count = len(self._synonym_expansion(query))
        concept_count = len(self._concept_expansion(query))
        
        return {
            "query_type": query_type.value,
            "synonym_expansions": synonym_count,
            "concept_expansions": concept_count,
            "total_possible_expansions": synonym_count + concept_count
        } 