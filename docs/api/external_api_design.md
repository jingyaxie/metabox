# MetaBox 外部API接口设计文档

## 📋 概述

MetaBox 对外提供完备的API接口，支持第三方系统调用知识库的检索和问答能力。本文档详细描述了API接口设计、认证授权、监控统计等方案。

## 🏗️ 架构设计

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   第三方应用     │    │   API Gateway   │    │   MetaBox Core  │
│                 │───▶│                 │───▶│                 │
│ - 业务系统      │    │ - 认证授权      │    │ - 知识库服务    │
│ - 移动应用      │    │ - 限流控制      │    │ - 向量检索      │
│ - Web应用       │    │ - 监控统计      │    │ - 问答服务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 核心组件
1. **API Gateway**: 统一入口，处理认证、限流、监控
2. **认证服务**: API密钥管理、权限验证
3. **限流服务**: 调用频率和配额控制
4. **监控服务**: 调用统计、性能监控
5. **计费服务**: 使用量统计、费用计算

## 🔐 认证授权方案

### 1. API密钥管理

#### 密钥生成
- 使用UUID v4生成32位随机密钥
- 支持密钥轮换和过期时间设置
- 密钥状态：active、inactive、expired

#### 密钥格式
```
格式: metabox_{app_id}_{random_string}
示例: metabox_app_123_abc123def456ghi789
```

#### 权限模型
```typescript
interface ApiKey {
  id: string
  app_id: string
  app_name: string
  key_hash: string          // 密钥哈希值
  permissions: {
    kb_ids: string[]        // 可访问的知识库ID列表
    operations: string[]    // 允许的操作类型
    rate_limit: number      // 每分钟调用限制
    quota_daily: number     // 每日配额
    quota_monthly: number   // 每月配额
  }
  status: 'active' | 'inactive' | 'expired'
  created_at: string
  expires_at?: string
  last_used_at?: string
}

interface ApiPermission {
  // 操作类型
  operations: {
    query: boolean          // 知识库问答
    search: boolean         // 向量检索
    hybrid: boolean         // 混合检索
    read: boolean           // 读取知识库信息
    write: boolean          // 写入知识库（预留）
  }
  
  // 资源访问
  resources: {
    kb_ids: string[]        // 可访问的知识库
    models: string[]        // 可使用的模型
  }
  
  // 限制配置
  limits: {
    rate_limit: number      // 每分钟调用限制
    quota_daily: number     // 每日配额
    quota_monthly: number   // 每月配额
    max_tokens: number      // 单次请求最大Token数
  }
}
```

#### 权限验证流程
1. 验证API密钥有效性
2. 检查密钥状态和过期时间
3. 验证操作权限
4. 检查资源访问权限
5. 验证调用限制和配额

### 2. 认证方式

#### HTTP Header认证
```http
Authorization: Bearer metabox_app_123_abc123def456ghi789
X-API-Key: metabox_app_123_abc123def456ghi789
```

#### 请求签名认证（可选）
```http
X-Timestamp: 1640995200
X-Signature: sha256(secret + timestamp + request_body)
```

## 📊 监控统计方案

### 1. 调用统计

#### 统计维度
- **应用维度**: 按API密钥统计
- **知识库维度**: 按知识库ID统计
- **接口维度**: 按API接口统计
- **时间维度**: 按分钟、小时、天、月统计

#### 统计指标
```typescript
interface ApiStats {
  // 调用量统计
  call_count: {
    total: number           // 总调用次数
    success: number         // 成功次数
    failed: number          // 失败次数
  }
  
  // 性能统计
  performance: {
    avg_response_time: number   // 平均响应时间
    max_response_time: number   // 最大响应时间
    min_response_time: number   // 最小响应时间
    p95_response_time: number   // 95%响应时间
  }
  
  // 资源消耗
  resource_usage: {
    total_tokens: number        // 总Token消耗
    total_requests: number      // 总请求数
    total_storage: number       // 存储使用量
  }
  
  // 错误统计
  errors: {
    rate_limit_exceeded: number // 限流错误
    quota_exceeded: number      // 配额超限
    auth_failed: number         // 认证失败
    validation_error: number    // 参数错误
    server_error: number        // 服务器错误
  }
}
```

### 2. 实时监控

#### 监控指标
- QPS (每秒查询数)
- 响应时间分布
- 错误率
- 资源使用率
- 并发用户数

#### 告警规则
- 错误率 > 5%
- 响应时间 > 5秒
- QPS > 1000
- 配额使用率 > 90%

### 3. 计费模型

#### 计费维度
1. **按调用次数计费**
   - 基础调用费：0.01元/次
   - 批量调用折扣

2. **按Token消耗计费**
   - 输入Token：0.0001元/Token
   - 输出Token：0.0002元/Token

3. **按知识库大小计费**
   - 存储费：0.1元/GB/月
   - 向量化费：0.01元/文档

#### 计费规则
```typescript
interface BillingRule {
  // 基础费用
  base_fee: {
    per_call: number        // 每次调用基础费用
    per_token_input: number // 输入Token费用
    per_token_output: number // 输出Token费用
    per_gb_storage: number  // 存储费用
  }
  
  // 阶梯定价
  tier_pricing: {
    monthly_calls: {
      '0-1000': number      // 0-1000次/月
      '1001-10000': number  // 1001-10000次/月
      '10001+': number      // 10001+次/月
    }
  }
  
  // 免费额度
  free_tier: {
    daily_calls: number     // 每日免费调用次数
    monthly_storage: number // 每月免费存储量
  }
}
```

## 🔌 API接口设计

### 1. 知识库问答接口

#### 接口信息
```
POST /api/v1/chat/query
Content-Type: application/json
Authorization: Bearer {api_key}
```

#### 请求参数
```typescript
interface QueryRequest {
  // 必填参数
  message: string           // 用户问题
  
  // 可选参数
  kb_ids?: string[]        // 指定知识库ID列表
  model_id?: string        // 指定模型ID
  session_id?: string      // 会话ID（用于上下文）
  
  // 高级参数
  options?: {
    temperature?: number    // 温度参数 0-1
    max_tokens?: number     // 最大Token数
    top_k?: number         // 检索文档数量
    similarity_threshold?: number // 相似度阈值
  }
  
  // 流式响应
  stream?: boolean         // 是否启用流式响应
}
```

#### 响应格式
```typescript
interface QueryResponse {
  success: boolean
  data: {
    answer: string         // AI回答内容
    sources: Array<{       // 参考来源
      kb_id: string
      chunk_id: string
      content: string
      similarity: number
    }>
    usage: {
      prompt_tokens: number
      completion_tokens: number
      total_tokens: number
    }
    session_id?: string    // 会话ID
  }
  error?: {
    code: string
    message: string
  }
}
```

### 2. 向量检索接口

#### 接口信息
```
POST /api/v1/retrieval/search
Content-Type: application/json
Authorization: Bearer {api_key}
```

#### 请求参数
```typescript
interface SearchRequest {
  // 必填参数
  query: string            // 检索查询
  
  // 可选参数
  kb_ids?: string[]       // 指定知识库ID列表
  top_k?: number          // 返回结果数量
  similarity_threshold?: number // 相似度阈值
  
  // 过滤条件
  filters?: {
    metadata?: Record<string, any> // 元数据过滤
    date_range?: {
      start: string
      end: string
    }
  }
}
```

#### 响应格式
```typescript
interface SearchResponse {
  success: boolean
  data: {
    results: Array<{
      chunk_id: string
      content: string
      similarity: number
      metadata: Record<string, any>
      kb_id: string
    }>
    total: number
    query_time: number
  }
}
```

### 3. 混合检索接口

#### 接口信息
```
POST /api/v1/retrieval/hybrid
Content-Type: application/json
Authorization: Bearer {api_key}
```

#### 请求参数
```typescript
interface HybridRequest {
  // 必填参数
  query: string            // 检索查询
  
  // 检索配置
  search_config: {
    vector_weight: number  // 向量检索权重 0-1
    keyword_weight: number // 关键词检索权重 0-1
    top_k: number         // 返回结果数量
  }
  
  // 其他参数同SearchRequest
}
```

### 4. 知识库管理接口

#### 获取知识库列表
```
GET /api/v1/kb/list
Authorization: Bearer {api_key}
```

#### 获取知识库信息
```
GET /api/v1/kb/{kb_id}/info
Authorization: Bearer {api_key}
```

## 📈 限流控制

### 1. 限流策略

#### 多级限流
1. **应用级限流**: 基于API密钥的全局限制
2. **接口级限流**: 基于具体接口的限制
3. **用户级限流**: 基于用户ID的限制
4. **IP级限流**: 基于IP地址的限制

#### 限流算法
- **令牌桶算法**: 适用于突发流量
- **滑动窗口**: 精确控制时间窗口
- **漏桶算法**: 平滑流量

### 2. 限流配置

```typescript
interface RateLimitConfig {
  // 应用级限制
  app_level: {
    requests_per_minute: number
    requests_per_hour: number
    requests_per_day: number
  }
  
  // 接口级限制
  endpoint_level: {
    '/api/v1/chat/query': {
      requests_per_minute: number
      burst_size: number
    }
  }
  
  // 用户级限制
  user_level: {
    requests_per_minute: number
    concurrent_requests: number
  }
}
```

### 3. 限流响应

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995260
Retry-After: 60

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求频率超限，请稍后重试",
    "retry_after": 60
  }
}
```

## 🔧 SDK设计

### 1. Python SDK

```python
from metabox import MetaBoxClient

# 初始化客户端
client = MetaBoxClient(
    api_key="metabox_app_123_abc123def456ghi789",
    base_url="https://api.metabox.com"
)

# 知识库问答
response = client.chat.query(
    message="什么是人工智能？",
    kb_ids=["kb_123", "kb_456"],
    model_id="gpt-3.5-turbo"
)

# 向量检索
results = client.retrieval.search(
    query="机器学习算法",
    top_k=10,
    similarity_threshold=0.7
)
```

### 2. JavaScript SDK

```javascript
import { MetaBoxClient } from '@metabox/sdk';

// 初始化客户端
const client = new MetaBoxClient({
  apiKey: 'metabox_app_123_abc123def456ghi789',
  baseUrl: 'https://api.metabox.com'
});

// 知识库问答
const response = await client.chat.query({
  message: '什么是人工智能？',
  kbIds: ['kb_123', 'kb_456'],
  modelId: 'gpt-3.5-turbo'
});

// 向量检索
const results = await client.retrieval.search({
  query: '机器学习算法',
  topK: 10,
  similarityThreshold: 0.7
});
```

### 3. Java SDK

```java
import com.metabox.MetaBoxClient;

// 初始化客户端
MetaBoxClient client = new MetaBoxClient.Builder()
    .apiKey("metabox_app_123_abc123def456ghi789")
    .baseUrl("https://api.metabox.com")
    .build();

// 知识库问答
QueryRequest request = QueryRequest.builder()
    .message("什么是人工智能？")
    .kbIds(Arrays.asList("kb_123", "kb_456"))
    .modelId("gpt-3.5-turbo")
    .build();

QueryResponse response = client.chat().query(request);
```

## 📚 API文档

### 1. 文档生成
- 使用OpenAPI 3.0规范
- 自动生成Swagger UI文档
- 提供Postman集合
- 支持多语言文档

### 2. 文档内容
- 接口详细说明
- 请求/响应示例
- 错误码说明
- 最佳实践指南
- SDK使用示例

## 🚀 部署方案

### 1. 环境配置
- 生产环境：高可用集群部署
- 测试环境：单机部署
- 开发环境：本地部署

### 2. 监控告警
- 使用Prometheus + Grafana监控
- 配置告警规则
- 日志收集和分析

### 3. 安全措施
- HTTPS加密传输
- API密钥加密存储
- 请求签名验证
- IP白名单控制

## 📋 实施计划

### 第一阶段：基础功能
1. API密钥管理
2. 基础认证授权
3. 核心API接口
4. 简单限流控制

### 第二阶段：完善功能
1. 详细权限控制
2. 监控统计系统
3. 计费系统
4. SDK开发

### 第三阶段：优化升级
1. 性能优化
2. 安全加固
3. 文档完善
4. 运维自动化

## 🧩 前端/Node.js SDK 使用说明

### 安装与引入

```bash
# 直接复制 frontend/src/sdk 目录到你的项目
# 或后续发布 npm 包
```

```typescript
import { MetaBoxClient } from './sdk/metabox';

const client = new MetaBoxClient({
  apiKey: 'your_api_key',
  baseUrl: '/api/v1' // 或完整后端地址
});

// 问答
const res = await client.query({ message: '什么是人工智能？', kb_ids: ['kb_123'] });
console.log(res);

// 检索
const searchRes = await client.search({ query: '机器学习', kb_ids: ['kb_123'] });
console.log(searchRes);

// 流式问答
client.streamQuery(
  { message: '流式测试', kb_ids: ['kb_123'], stream: true },
  (msg) => console.log('流式消息:', msg),
  (err) => console.error('流式错误:', err)
);
```

### Python 调用示例
```python
import requests
headers = {"Authorization": "Bearer <your_api_key>"}
data = {"message": "什么是人工智能？", "kb_ids": ["kb_123"]}
resp = requests.post("https://yourdomain.com/api/v1/chat/query", json=data, headers=headers)
print(resp.json())
```

### curl 调用示例
```bash
curl -X POST https://yourdomain.com/api/v1/chat/query \
  -H "Authorization: Bearer <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{"message":"什么是人工智能？","kb_ids":["kb_123"]}'
```

---

如需更多语言SDK或高级用法，请参考 [API文档](/docs/api/external_api_design.md) 或联系技术支持。 