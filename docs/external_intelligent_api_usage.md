# 外部智能检索API使用文档

## 概述

外部智能检索API提供了基于API密钥认证的智能检索服务，无需用户登录和对话上下文，支持自动意图识别和检索策略选择。

## 接口列表

### 1. 智能检索接口

**接口地址**: `POST /api/v1/intelligent/search`

**认证方式**: API密钥认证

**功能**: 根据查询内容自动识别意图，选择最合适的检索策略，返回相关文档

#### 请求参数

```json
{
  "query": "什么是RESTful API?",
  "kb_ids": ["kb_001", "kb_002"],
  "user_context": {
    "domain": "技术文档",
    "user_level": "中级",
    "preferences": {
      "response_speed": "balanced",
      "quality_priority": "high"
    }
  },
  "force_strategy": null,
  "enable_learning": true,
  "timeout_ms": 5000,
  "top_k": 10,
  "similarity_threshold": 0.7
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 检索查询内容 |
| kb_ids | array | 否 | 指定知识库ID列表，为空时检索所有有权限的知识库 |
| user_context | object | 否 | 用户上下文信息，用于意图识别和策略选择 |
| force_strategy | string | 否 | 强制使用指定检索策略（vector/hybrid/enhanced/keyword） |
| enable_learning | boolean | 否 | 是否启用学习功能，默认true |
| timeout_ms | integer | 否 | 超时时间（毫秒） |
| top_k | integer | 否 | 返回结果数量，默认10 |
| similarity_threshold | float | 否 | 相似度阈值，默认0.7 |

#### 响应格式

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "chunk_001",
        "content": "RESTful API是一种软件架构风格...",
        "score": 0.85,
        "source_file": "api_design.md",
        "knowledge_base_id": "kb_001",
        "metadata": {
          "chunk_index": 1,
          "file_type": "markdown"
        }
      }
    ],
    "strategy_used": {
      "service_type": "enhanced",
      "strategy_name": "增强检索流水线",
      "parameters": {
        "enable_expansion": true,
        "enable_rerank": true,
        "top_k": 10
      },
      "reasoning": "概念查询，使用增强流水线获得最佳效果"
    },
    "intent_analysis": {
      "query_type": "conceptual",
      "complexity": "simple",
      "confidence": 0.8,
      "features": {
        "query_length": 12,
        "word_count": 3,
        "has_question_mark": true,
        "query_type": "conceptual"
      }
    },
    "performance_metrics": {
      "response_time": 245,
      "strategy_used": "enhanced",
      "intent_confidence": 0.8,
      "results_count": 5
    },
    "total": 5,
    "query_time": 245,
    "api_key_id": "ak_001"
  },
  "message": "检索成功"
}
```

### 2. 策略推荐接口

**接口地址**: `POST /api/v1/intelligent/recommend-strategy`

**认证方式**: API密钥认证

**功能**: 根据查询内容推荐最适合的检索策略

#### 请求参数

```json
{
  "query": "如何安装Docker?",
  "user_context": {
    "domain": "技术教程",
    "user_level": "初级"
  }
}
```

#### 响应格式

```json
{
  "success": true,
  "data": [
    {
      "strategy": "keyword",
      "name": "关键词检索",
      "description": "适合程序查询和操作步骤",
      "confidence": 0.9
    },
    {
      "strategy": "hybrid",
      "name": "混合检索",
      "description": "平衡精度和召回率",
      "confidence": 0.8
    },
    {
      "strategy": "enhanced",
      "name": "增强检索",
      "description": "最高精度，适合复杂查询",
      "confidence": 0.7
    }
  ],
  "message": "策略推荐成功"
}
```

### 3. 健康检查接口

**接口地址**: `GET /api/v1/intelligent/health`

**认证方式**: 无需认证

**功能**: 检查智能检索服务状态

#### 响应格式

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "services": {
      "vector_service": true,
      "hybrid_retriever": true,
      "enhanced_pipeline": true,
      "intent_recognizer": true,
      "strategy_scheduler": true,
      "retrieval_executor": true
    },
    "total_queries": 1250,
    "avg_response_time": 234.5,
    "strategy_usage": {
      "vector": 450,
      "hybrid": 380,
      "enhanced": 320,
      "keyword": 100
    },
    "intent_distribution": {
      "factual": 300,
      "conceptual": 280,
      "procedural": 250,
      "comparative": 200,
      "troubleshooting": 220
    }
  },
  "message": "服务正常"
}
```

## 使用示例

### Python示例

```python
import requests
import json

# API配置
API_BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 1. 智能检索
def intelligent_search(query, kb_ids=None):
    url = f"{API_BASE_URL}/api/v1/intelligent/search"
    
    payload = {
        "query": query,
        "kb_ids": kb_ids or [],
        "user_context": {
            "domain": "技术文档",
            "user_level": "中级"
        },
        "top_k": 10,
        "similarity_threshold": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 2. 策略推荐
def recommend_strategy(query):
    url = f"{API_BASE_URL}/api/v1/intelligent/recommend-strategy"
    
    payload = {
        "query": query,
        "user_context": {
            "domain": "技术文档"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 3. 健康检查
def health_check():
    url = f"{API_BASE_URL}/api/v1/intelligent/health"
    response = requests.get(url)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 检查服务状态
    health = health_check()
    print("服务状态:", health["data"]["status"])
    
    # 获取策略推荐
    recommendations = recommend_strategy("什么是微服务架构?")
    print("推荐策略:", recommendations["data"])
    
    # 执行智能检索
    results = intelligent_search(
        query="什么是微服务架构?",
        kb_ids=["kb_001", "kb_002"]
    )
    
    if results["success"]:
        print(f"检索到 {results['data']['total']} 个结果")
        for result in results["data"]["results"]:
            print(f"- {result['content'][:100]}... (分数: {result['score']:.2f})")
        
        print(f"使用的策略: {results['data']['strategy_used']['strategy_name']}")
        print(f"意图分析: {results['data']['intent_analysis']['query_type']}")
    else:
        print("检索失败:", results["message"])
```

### JavaScript示例

```javascript
// API配置
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'your_api_key_here';

const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
};

// 1. 智能检索
async function intelligentSearch(query, kbIds = []) {
    const url = `${API_BASE_URL}/api/v1/intelligent/search`;
    
    const payload = {
        query: query,
        kb_ids: kbIds,
        user_context: {
            domain: '技术文档',
            user_level: '中级'
        },
        top_k: 10,
        similarity_threshold: 0.7
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    } catch (error) {
        console.error('检索失败:', error);
        throw error;
    }
}

// 2. 策略推荐
async function recommendStrategy(query) {
    const url = `${API_BASE_URL}/api/v1/intelligent/recommend-strategy`;
    
    const payload = {
        query: query,
        user_context: {
            domain: '技术文档'
        }
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(payload)
        });
        
        return await response.json();
    } catch (error) {
        console.error('策略推荐失败:', error);
        throw error;
    }
}

// 3. 健康检查
async function healthCheck() {
    const url = `${API_BASE_URL}/api/v1/intelligent/health`;
    
    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error('健康检查失败:', error);
        throw error;
    }
}

// 使用示例
async function main() {
    try {
        // 检查服务状态
        const health = await healthCheck();
        console.log('服务状态:', health.data.status);
        
        // 获取策略推荐
        const recommendations = await recommendStrategy('什么是微服务架构?');
        console.log('推荐策略:', recommendations.data);
        
        // 执行智能检索
        const results = await intelligentSearch(
            '什么是微服务架构?',
            ['kb_001', 'kb_002']
        );
        
        if (results.success) {
            console.log(`检索到 ${results.data.total} 个结果`);
            results.data.results.forEach(result => {
                console.log(`- ${result.content.substring(0, 100)}... (分数: ${result.score.toFixed(2)})`);
            });
            
            console.log(`使用的策略: ${results.data.strategy_used.strategy_name}`);
            console.log(`意图分析: ${results.data.intent_analysis.query_type}`);
        } else {
            console.log('检索失败:', results.message);
        }
    } catch (error) {
        console.error('操作失败:', error);
    }
}

// 运行示例
main();
```

### cURL示例

```bash
# 1. 智能检索
curl -X POST "http://localhost:8000/api/v1/intelligent/search" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RESTful API?",
    "kb_ids": ["kb_001", "kb_002"],
    "user_context": {
      "domain": "技术文档",
      "user_level": "中级"
    },
    "top_k": 10,
    "similarity_threshold": 0.7
  }'

# 2. 策略推荐
curl -X POST "http://localhost:8000/api/v1/intelligent/recommend-strategy" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何安装Docker?",
    "user_context": {
      "domain": "技术教程"
    }
  }'

# 3. 健康检查
curl -X GET "http://localhost:8000/api/v1/intelligent/health"
```

## 最佳实践

### 1. 查询优化

- **明确查询**: 使用具体、明确的查询词
- **避免模糊**: 避免过于宽泛的查询
- **使用关键词**: 包含重要的技术术语和概念

```python
# 好的查询
"如何配置Nginx反向代理?"

# 不好的查询
"怎么弄?"
```

### 2. 上下文利用

- **提供领域信息**: 在user_context中指定domain
- **用户级别**: 指定user_level（初级/中级/高级）
- **偏好设置**: 设置response_speed和quality_priority

```python
user_context = {
    "domain": "技术文档",
    "user_level": "中级",
    "preferences": {
        "response_speed": "balanced",  # fast/balanced/quality
        "quality_priority": "high"     # speed/balanced/high
    }
}
```

### 3. 策略选择

- **自动选择**: 让系统自动选择策略（推荐）
- **强制策略**: 仅在特殊需求时使用force_strategy
- **策略推荐**: 使用recommend-strategy接口了解推荐策略

### 4. 结果处理

- **相似度过滤**: 使用similarity_threshold过滤低质量结果
- **数量控制**: 使用top_k控制返回结果数量
- **结果分析**: 查看strategy_used和intent_analysis了解检索过程

### 5. 错误处理

```python
try:
    results = intelligent_search(query, kb_ids)
    if results["success"]:
        # 处理成功结果
        process_results(results["data"]["results"])
    else:
        # 处理业务错误
        handle_business_error(results["message"])
except requests.exceptions.RequestException as e:
    # 处理网络错误
    handle_network_error(e)
except Exception as e:
    # 处理其他错误
    handle_unknown_error(e)
```

### 6. 性能优化

- **批量查询**: 避免频繁的单次查询
- **缓存结果**: 对相同查询进行缓存
- **超时设置**: 设置合理的timeout_ms
- **异步处理**: 使用异步方式处理大量查询

## 错误码说明

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| KB_ACCESS_DENIED | 没有访问知识库的权限 | 检查API密钥权限配置 |
| INTERNAL_ERROR | 内部服务错误 | 联系技术支持 |
| INVALID_REQUEST | 请求参数错误 | 检查请求参数格式 |
| TIMEOUT_ERROR | 请求超时 | 增加timeout_ms或简化查询 |
| RATE_LIMIT_EXCEEDED | 请求频率超限 | 降低请求频率 |

## 限制说明

- **API密钥权限**: 需要search权限
- **知识库访问**: 只能访问API密钥授权的知识库
- **请求频率**: 受API密钥限流配置限制
- **响应时间**: 复杂查询可能需要较长时间
- **结果数量**: 单次查询最多返回100个结果 