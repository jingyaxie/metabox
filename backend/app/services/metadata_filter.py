"""
MetadataFilter 元数据过滤模块
支持多种过滤条件和动态过滤规则
"""
from typing import List, Dict, Any, Optional, Union, Callable
import asyncio
import logging
from enum import Enum
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class FilterOperator(str, Enum):
    """过滤操作符"""
    EQUALS = "equals"           # 等于
    NOT_EQUALS = "not_equals"   # 不等于
    CONTAINS = "contains"       # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    GREATER_THAN = "gt"         # 大于
    LESS_THAN = "lt"            # 小于
    GREATER_EQUAL = "gte"       # 大于等于
    LESS_EQUAL = "lte"          # 小于等于
    IN = "in"                   # 在列表中
    NOT_IN = "not_in"           # 不在列表中
    EXISTS = "exists"           # 存在
    NOT_EXISTS = "not_exists"   # 不存在
    REGEX = "regex"             # 正则匹配
    DATE_RANGE = "date_range"   # 日期范围


class FilterCondition:
    """过滤条件"""
    
    def __init__(self, field: str, operator: FilterOperator, value: Any):
        self.field = field
        self.operator = operator
        self.value = value
    
    def __str__(self):
        return f"{self.field} {self.operator.value} {self.value}"


class MetadataFilter:
    """元数据过滤器"""
    
    def __init__(self):
        # 预定义的过滤规则
        self.predefined_filters = {
            "recent_docs": self._filter_recent_documents,
            "high_quality": self._filter_high_quality,
            "official_sources": self._filter_official_sources,
            "code_docs": self._filter_code_documents,
            "tutorial_docs": self._filter_tutorial_documents,
            "exclude_archived": self._filter_exclude_archived,
            "include_images": self._filter_include_images,
            "exclude_images": self._filter_exclude_images
        }
        
        # 字段类型映射
        self.field_types = {
            "created_at": "datetime",
            "updated_at": "datetime",
            "file_size": "number",
            "word_count": "number",
            "quality_score": "number",
            "source_type": "string",
            "file_type": "string",
            "language": "string",
            "tags": "list",
            "categories": "list",
            "is_archived": "boolean",
            "has_images": "boolean"
        }
    
    async def filter_documents(self, documents: List[Dict], 
                             conditions: List[FilterCondition] = None,
                             predefined_filters: List[str] = None) -> List[Dict]:
        """过滤文档"""
        try:
            filtered_docs = documents.copy()
            
            # 应用预定义过滤器
            if predefined_filters:
                for filter_name in predefined_filters:
                    if filter_name in self.predefined_filters:
                        filtered_docs = self.predefined_filters[filter_name](filtered_docs)
                    else:
                        logger.warning(f"未知的预定义过滤器: {filter_name}")
            
            # 应用自定义条件
            if conditions:
                for condition in conditions:
                    filtered_docs = self._apply_condition(filtered_docs, condition)
            
            return filtered_docs
            
        except Exception as e:
            logger.error(f"文档过滤失败: {e}")
            return documents  # 降级返回原始文档
    
    def _apply_condition(self, documents: List[Dict], condition: FilterCondition) -> List[Dict]:
        """应用单个过滤条件"""
        filtered_docs = []
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            field_value = self._get_nested_field(metadata, condition.field)
            
            if self._evaluate_condition(field_value, condition):
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _evaluate_condition(self, field_value: Any, condition: FilterCondition) -> bool:
        """评估过滤条件"""
        try:
            if condition.operator == FilterOperator.EQUALS:
                return field_value == condition.value
            
            elif condition.operator == FilterOperator.NOT_EQUALS:
                return field_value != condition.value
            
            elif condition.operator == FilterOperator.CONTAINS:
                if isinstance(field_value, str) and isinstance(condition.value, str):
                    return condition.value.lower() in field_value.lower()
                elif isinstance(field_value, list):
                    return condition.value in field_value
                return False
            
            elif condition.operator == FilterOperator.NOT_CONTAINS:
                if isinstance(field_value, str) and isinstance(condition.value, str):
                    return condition.value.lower() not in field_value.lower()
                elif isinstance(field_value, list):
                    return condition.value not in field_value
                return True
            
            elif condition.operator == FilterOperator.GREATER_THAN:
                return self._compare_values(field_value, condition.value, "gt")
            
            elif condition.operator == FilterOperator.LESS_THAN:
                return self._compare_values(field_value, condition.value, "lt")
            
            elif condition.operator == FilterOperator.GREATER_EQUAL:
                return self._compare_values(field_value, condition.value, "gte")
            
            elif condition.operator == FilterOperator.LESS_EQUAL:
                return self._compare_values(field_value, condition.value, "lte")
            
            elif condition.operator == FilterOperator.IN:
                if isinstance(condition.value, list):
                    return field_value in condition.value
                return False
            
            elif condition.operator == FilterOperator.NOT_IN:
                if isinstance(condition.value, list):
                    return field_value not in condition.value
                return True
            
            elif condition.operator == FilterOperator.EXISTS:
                return field_value is not None
            
            elif condition.operator == FilterOperator.NOT_EXISTS:
                return field_value is None
            
            elif condition.operator == FilterOperator.REGEX:
                if isinstance(field_value, str) and isinstance(condition.value, str):
                    return bool(re.search(condition.value, field_value, re.IGNORECASE))
                return False
            
            elif condition.operator == FilterOperator.DATE_RANGE:
                return self._evaluate_date_range(field_value, condition.value)
            
            else:
                logger.warning(f"未知的过滤操作符: {condition.operator}")
                return True
                
        except Exception as e:
            logger.error(f"条件评估失败: {e}")
            return True  # 出错时不过滤
    
    def _compare_values(self, field_value: Any, condition_value: Any, operator: str) -> bool:
        """比较数值"""
        try:
            # 尝试转换为数值进行比较
            if isinstance(field_value, str):
                field_value = float(field_value)
            if isinstance(condition_value, str):
                condition_value = float(condition_value)
            
            if operator == "gt":
                return field_value > condition_value
            elif operator == "lt":
                return field_value < condition_value
            elif operator == "gte":
                return field_value >= condition_value
            elif operator == "lte":
                return field_value <= condition_value
            
        except (ValueError, TypeError):
            logger.warning(f"无法比较值: {field_value} {operator} {condition_value}")
            return False
        
        return False
    
    def _evaluate_date_range(self, field_value: Any, date_range: Dict[str, Any]) -> bool:
        """评估日期范围"""
        try:
            if not field_value:
                return False
            
            # 解析日期值
            if isinstance(field_value, str):
                field_date = datetime.fromisoformat(field_value.replace('Z', '+00:00'))
            elif isinstance(field_value, datetime):
                field_date = field_value
            else:
                return False
            
            # 检查开始日期
            if "start" in date_range:
                start_date = datetime.fromisoformat(date_range["start"].replace('Z', '+00:00'))
                if field_date < start_date:
                    return False
            
            # 检查结束日期
            if "end" in date_range:
                end_date = datetime.fromisoformat(date_range["end"].replace('Z', '+00:00'))
                if field_date > end_date:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"日期范围评估失败: {e}")
            return False
    
    def _get_nested_field(self, metadata: Dict[str, Any], field_path: str) -> Any:
        """获取嵌套字段值"""
        try:
            keys = field_path.split('.')
            value = metadata
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception as e:
            logger.error(f"获取嵌套字段失败: {e}")
            return None
    
    # 预定义过滤器方法
    def _filter_recent_documents(self, documents: List[Dict]) -> List[Dict]:
        """过滤最近30天的文档"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        filtered_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            created_at = metadata.get("created_at")
            
            if created_at:
                try:
                    if isinstance(created_at, str):
                        doc_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        doc_date = created_at
                    
                    if doc_date >= cutoff_date:
                        filtered_docs.append(doc)
                except:
                    # 如果日期解析失败，保留文档
                    filtered_docs.append(doc)
            else:
                # 如果没有创建时间，保留文档
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _filter_high_quality(self, documents: List[Dict]) -> List[Dict]:
        """过滤高质量文档（质量分数>=0.7）"""
        filtered_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            quality_score = metadata.get("quality_score", 0.5)
            
            if quality_score >= 0.7:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _filter_official_sources(self, documents: List[Dict]) -> List[Dict]:
        """过滤官方来源文档"""
        official_types = ["official_doc", "documentation", "api_doc"]
        
        filtered_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            source_type = metadata.get("source_type", "")
            
            if source_type in official_types:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _filter_code_documents(self, documents: List[Dict]) -> List[Dict]:
        """过滤包含代码的文档"""
        filtered_docs = []
        for doc in documents:
            content = doc.get("content", "")
            # 检查是否包含代码块
            if "```" in content or "<code>" in content:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _filter_tutorial_documents(self, documents: List[Dict]) -> List[Dict]:
        """过滤教程类文档"""
        tutorial_keywords = ["教程", "tutorial", "guide", "how to", "步骤", "步骤"]
        
        filtered_docs = []
        for doc in documents:
            content = doc.get("content", "")
            title = doc.get("title", "")
            
            # 检查标题和内容中是否包含教程关键词
            for keyword in tutorial_keywords:
                if keyword.lower() in title.lower() or keyword.lower() in content.lower():
                    filtered_docs.append(doc)
                    break
        
        return filtered_docs
    
    def _filter_exclude_archived(self, documents: List[Dict]) -> List[Dict]:
        """排除已归档的文档"""
        filtered_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            is_archived = metadata.get("is_archived", False)
            
            if not is_archived:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _filter_include_images(self, documents: List[Dict]) -> List[Dict]:
        """包含图片的文档"""
        filtered_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            has_images = metadata.get("has_images", False)
            
            if has_images:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def _filter_exclude_images(self, documents: List[Dict]) -> List[Dict]:
        """排除包含图片的文档"""
        filtered_docs = []
        for doc in documents:
            metadata = doc.get("metadata", {})
            has_images = metadata.get("has_images", False)
            
            if not has_images:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def create_condition(self, field: str, operator: FilterOperator, value: Any) -> FilterCondition:
        """创建过滤条件"""
        return FilterCondition(field, operator, value)
    
    def create_date_range_condition(self, field: str, start_date: str = None, end_date: str = None) -> FilterCondition:
        """创建日期范围条件"""
        date_range = {}
        if start_date:
            date_range["start"] = start_date
        if end_date:
            date_range["end"] = end_date
        
        return FilterCondition(field, FilterOperator.DATE_RANGE, date_range)
    
    def get_filter_stats(self, original_count: int, filtered_count: int) -> Dict[str, Any]:
        """获取过滤统计信息"""
        return {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "filtered_out_count": original_count - filtered_count,
            "filter_ratio": (original_count - filtered_count) / original_count if original_count > 0 else 0
        }
    
    def add_predefined_filter(self, name: str, filter_func: Callable):
        """添加预定义过滤器"""
        self.predefined_filters[name] = filter_func
    
    def get_available_filters(self) -> List[str]:
        """获取可用的预定义过滤器"""
        return list(self.predefined_filters.keys()) 