# 外部智能检索API使用示例

## 接口地址

- **智能检索**: `POST /api/v1/intelligent/search`
- **策略推荐**: `POST /api/v1/intelligent/recommend-strategy`
- **健康检查**: `GET /api/v1/intelligent/health`

## 认证方式

使用API密钥认证，在请求头中添加：
```
Authorization: Bearer your_api_key_here
```

## 使用示例

### 1. 智能检索

```bash
curl -X POST "http://localhost:8000/api/v1/intelligent/search" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是RESTful API?",
    "kb_ids": ["kb_001"],
    "top_k": 10,
    "similarity_threshold": 0.7
  }'
```

**响应示例**:
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
        "knowledge_base_id": "kb_001"
      }
    ],
    "strategy_used": {
      "service_type": "enhanced",
      "strategy_name": "增强检索流水线",
      "reasoning": "概念查询，使用增强流水线"
    },
    "intent_analysis": {
      "query_type": "conceptual",
      "confidence": 0.8
    },
    "total": 1,
    "query_time": 245
  },
  "message": "检索成功"
}
```

### 2. Python示例

```python
import requests

API_BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 智能检索
def intelligent_search(query, kb_ids=None):
    url = f"{API_BASE_URL}/api/v1/intelligent/search"
    
    payload = {
        "query": query,
        "kb_ids": kb_ids or [],
        "top_k": 10,
        "similarity_threshold": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# 使用示例
results = intelligent_search("什么是微服务架构?", ["kb_001"])
if results["success"]:
    print(f"检索到 {results['data']['total']} 个结果")
    for result in results["data"]["results"]:
        print(f"- {result['content'][:100]}...")
```

### 3. JavaScript示例

```javascript
const API_BASE_URL = 'http://localhost:8000';
const API_KEY = 'your_api_key_here';

const headers = {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
};

async function intelligentSearch(query, kbIds = []) {
    const url = `${API_BASE_URL}/api/v1/intelligent/search`;
    
    const payload = {
        query: query,
        kb_ids: kbIds,
        top_k: 10,
        similarity_threshold: 0.7
    };
    
    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// 使用示例
intelligentSearch("什么是微服务架构?", ["kb_001"])
    .then(results => {
        if (results.success) {
            console.log(`检索到 ${results.data.total} 个结果`);
            results.data.results.forEach(result => {
                console.log(`- ${result.content.substring(0, 100)}...`);
            });
        }
    });
```

## 主要特点

1. **无需对话上下文**: 直接传入查询即可
2. **自动意图识别**: 系统自动分析查询类型
3. **智能策略选择**: 根据意图选择最佳检索策略
4. **API密钥认证**: 支持外部系统集成
5. **权限控制**: 只能访问授权的知识库

## 参数说明

- `query`: 检索查询内容
- `kb_ids`: 知识库ID列表（可选）
- `top_k`: 返回结果数量（默认10）
- `similarity_threshold`: 相似度阈值（默认0.7）
- `force_strategy`: 强制使用指定策略（可选）
- `user_context`: 用户上下文信息（可选） 