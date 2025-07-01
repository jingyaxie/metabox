# 本地智能知识库系统技术文档（对标 FastGPT）

---

## 一、项目目标

构建一个本地私有化部署的智能知识库系统，具备以下核心能力：

- 🧠 支持 RAG + 多模态（文本 + 图像）检索与问答
- 🖼️ 支持文本和图片向量库，统一多模态搜索
- 🧩 支持插件系统和 Agent 多步推理能力
- 🧑‍💼 多用户多角色权限管理（RBAC）
- 🐳 支持 Docker 一键本地私有化部署
- ⚙️ 系统架构模块清晰，易扩展、易维护
- 🔐 超级管理员系统配置与大模型供应商管理

---

## 二、系统架构总览

```text
┌─────────────────────────────┐
│         Web 前端 UI         │ React + Tailwind + Zustand │
│   ┌─────────────────────┐   │
│   │   超级管理员入口     │   │ 系统配置 / 模型管理
│   └─────────────────────┘   │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│         后端 API 服务        │ FastAPI / NestJS            │
│ 用户系统 / RAG / 插件 / Agent│                            │
│ 大模型配置 / 系统管理        │                            │
└────────────┬────────────────┘
             ↓
 ┌────────────┬────────────┐
 │ 向量数据库 │ 结构数据库 │
 │  Qdrant    │ PostgreSQL │
 └────┬───────┴───────┬────┘
      ↓               ↓
 [ 文本向量库 ]   [ 图片向量库 ]
```

---

## 三、功能模块说明

### 1️⃣ 超级管理员系统

#### 1.1 管理员登录入口
- 独立的管理员登录页面，与普通用户登录分离
- 支持超级管理员账号创建和权限验证
- 登录后进入系统管理控制台

#### 1.2 大模型供应商配置
- **支持的供应商**：
  - OpenAI (GPT-3.5/4, DALL-E, CLIP)
  - 阿里云通义千问 (Qwen, Qwen-VL)
  - 百度文心一言 (ERNIE, ERNIE-VL)
  - 智谱AI (ChatGLM, GLM-4V)
  - 讯飞星火 (SparkDesk)
  - 本地模型 (Ollama, vLLM)

- **配置项**：
  - API Key / Secret Key
  - 模型端点地址
  - 请求超时时间
  - 并发限制
  - 成本控制设置

#### 1.3 模型类型管理
- **文本理解模型**：用于文档内容理解和问答
- **图片理解模型**：用于图片描述生成和视觉问答
- **嵌入模型**：用于文本向量化
- **图片嵌入模型**：用于图片向量化

### 2️⃣ 知识库管理模块

- 创建、编辑、删除知识库
- 支持文本文件（PDF、Word、Markdown、TXT）上传
- 支持图片上传，自动向量化并绑定描述
- 文本自动切分并生成向量入库
- **新增**：创建知识库时可选择文本理解模型和图片理解模型

### 3️⃣ Chat 对话模块（RAG）

- 支持文本问题的向量检索与上下文构建
- 支持图片问题，结合图像向量库进行检索
- 支持多模型接入（OpenAI、通义千问、Claude 等）

### 4️⃣ 插件系统与 Agent 推理

- 插件注册、管理与调用（搜索、翻译、天气等）
- Agent 多步骤推理流程，动态调用多个工具完成复杂任务

### 5️⃣ 多模态能力模块

- 文本 Embedding：支持 OpenAI、通义千问 Embedding API
- 图片向量化：支持 CLIP、Qwen-VL、BLIP-2 等模型
- 实现图文混合检索与多模态问答

### 6️⃣ 权限管理模块（RBAC）

- 用户注册、登录、JWT 鉴权
- 支持角色分级：超级管理员、管理员、普通用户、游客
- 绑定知识库访问权限，保护数据安全

### 7️⃣ 部署与运维

- 使用 Docker Compose 一键部署所有服务
- 支持 GPU 容器，运行本地模型推理（可选）

---

## 四、数据库设计（简化版）

### 用户表 `users`

| 字段           | 类型     | 描述              |
|----------------|----------|-------------------|
| id             | UUID     | 用户唯一标识      |
| username       | TEXT     | 用户名            |
| password_hash  | TEXT     | 哈希密码          |
| role           | TEXT     | 用户角色          |
| is_super_admin | BOOLEAN  | 是否超级管理员    |

### 大模型供应商配置表 `model_providers`

| 字段           | 类型     | 描述              |
|----------------|----------|-------------------|
| id             | UUID     | 配置唯一标识      |
| provider_name  | TEXT     | 供应商名称        |
| provider_type  | TEXT     | 供应商类型        |
| api_key        | TEXT     | API密钥           |
| api_secret     | TEXT     | API密钥（可选）   |
| base_url       | TEXT     | API基础地址       |
| models         | JSONB    | 支持的模型列表    |
| config         | JSONB    | 其他配置参数      |
| is_active      | BOOLEAN  | 是否启用          |
| created_at     | TIMESTAMP| 创建时间          |
| updated_at     | TIMESTAMP| 更新时间          |

### 知识库表 `knowledge_bases`

| 字段                    | 类型     | 描述              |
|-------------------------|----------|-------------------|
| id                      | UUID     | 知识库唯一标识    |
| name                    | TEXT     | 知识库名称        |
| type                    | TEXT     | 类型（text/image） |
| owner_id                | UUID     | 所属用户          |
| text_model_id           | UUID     | 文本理解模型ID    |
| image_model_id          | UUID     | 图片理解模型ID    |
| embedding_model_id      | UUID     | 嵌入模型ID        |
| image_embedding_model_id| UUID     | 图片嵌入模型ID    |

### 文本向量表 `text_chunks`

| 字段           | 类型      | 描述              |
|----------------|-----------|-------------------|
| id             | UUID      | 文本分块唯一ID    |
| kb_id          | UUID      | 关联知识库ID      |
| content        | TEXT      | 原始文本          |
| vector         | VECTOR    | 向量值            |
| created_at     | TIMESTAMP | 创建时间          |

### 图片向量表 `image_vectors`

| 字段           | 类型      | 描述              |
|----------------|-----------|-------------------|
| id             | UUID      | 图片向量唯一ID    |
| kb_id          | UUID      | 关联知识库ID      |
| filename       | TEXT      | 图片文件名        |
| description    | TEXT      | 图片描述          |
| vector         | VECTOR    | 图片向量          |
| created_at     | TIMESTAMP | 创建时间          |

---

## 五、API 接口设计示例

### 超级管理员登录

```
POST /api/admin/login
Body: { username: string, password: string }
Response: { success: bool, token: string, user: object }
```

### 大模型供应商管理

```
GET    /api/admin/model-providers          # 获取所有供应商
POST   /api/admin/model-providers          # 添加供应商
PUT    /api/admin/model-providers/{id}     # 更新供应商
DELETE /api/admin/model-providers/{id}     # 删除供应商
POST   /api/admin/model-providers/{id}/test # 测试连接
```

### 上传文档

```
POST /api/kb/upload-doc
Body: form-data { file, kb_id }
Response: { success: bool, message: string }
```

### 上传图片

```
POST /api/kb/upload-image
Body: form-data { file, description, kb_id }
Response: { success: bool, message: string }
```

### 聊天接口

```
POST /api/chat
Body: {
  message: string,
  kb_ids: [UUID],
  history: [{role: string, content: string}],
  user_id: UUID
}
Response: {
  answer: string
}
```

### 插件管理

```
POST /api/plugins/register
POST /api/plugins/execute
```

---

## 六、Docker Compose 示例

```yaml
version: '3.9'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  backend:
    build: ./backend
    environment:
      - OPENAI_API_KEY=your_key_here
      - QWEN_API_KEY=your_key_here
      - ERNIE_API_KEY=your_key_here
    ports:
      - "8000:8000"
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
  postgres:
    image: postgres
    environment:
      POSTGRES_USER: kb
      POSTGRES_PASSWORD: kb_pass
    ports:
      - "5432:5432"
```

---

## 七、界面架构设计（对标 FastGPT）

### 1. 总体设计原则

- 简洁直观，功能模块分明  
- 侧边栏快速切换知识库、聊天、插件、设置  
- 超级管理员独立入口，系统配置集中管理

### 2. 超级管理员界面

#### 2.1 管理员登录页
- 独立的管理员登录入口
- 科技感设计，与普通登录页区分
- 支持记住登录状态

#### 2.2 系统管理控制台
- **仪表板**：系统概览、使用统计、模型状态
- **模型管理**：大模型供应商配置、模型测试、成本监控
- **用户管理**：用户列表、权限分配、角色管理
- **系统设置**：系统参数、安全配置、备份恢复

#### 2.3 大模型配置界面
- 供应商列表展示（卡片式布局）
- 添加/编辑供应商配置表单
- 模型连接测试功能
- 成本和使用量统计图表

### 3. 知识库创建增强

#### 3.1 模型选择界面
- 文本理解模型选择（支持预览和测试）
- 图片理解模型选择
- 嵌入模型配置
- 模型性能对比和推荐

#### 3.2 高级配置
- 文档分割参数优化
- 向量维度设置
- 相似度阈值调整
- 检索策略配置

---

## 八、技术实现要点

### 1. 大模型供应商抽象层
- 统一的模型接口定义
- 支持不同供应商的API差异
- 错误处理和重试机制
- 成本控制和限流

### 2. 模型配置管理
- 配置验证和测试
- 模型能力检测
- 动态模型切换
- 配置版本管理

### 3. 安全性考虑
- API密钥加密存储
- 访问权限控制
- 操作日志记录
- 敏感信息脱敏

### 4. 性能优化
- 模型响应缓存
- 并发请求控制
- 异步处理机制
- 资源使用监控

---

## 九、开发计划

### 第一阶段：基础架构
- [x] 项目基础架构搭建
- [x] 用户认证系统
- [x] 知识库管理基础功能
- [x] Chat对话功能
- [x] 插件系统
- [ ] 超级管理员登录入口
- [ ] 大模型供应商配置系统

### 第二阶段：模型集成
- [ ] OpenAI集成
- [ ] 通义千问集成
- [ ] 文心一言集成
- [ ] 智谱AI集成
- [ ] 本地模型支持

### 第三阶段：高级功能
- [ ] 多模态能力完善
- [ ] Agent推理增强
- [ ] 性能优化
- [ ] 监控告警
- [ ] 部署自动化

---

## 十、总结

本系统通过超级管理员入口和大模型供应商配置功能，实现了：

1. **统一管理**：集中管理所有大模型供应商配置
2. **灵活选择**：知识库创建时可灵活选择不同的理解模型
3. **成本控制**：通过配置管理实现成本监控和控制
4. **安全可靠**：API密钥安全存储，权限严格控制
5. **易于扩展**：支持新的大模型供应商快速接入

这样的设计使得系统既具备了强大的AI能力，又保持了良好的可管理性和安全性。

---

# 结束语

以上文档涵盖了系统架构、模块功能、数据库设计、API接口、Docker部署与详细界面架构，能完整指导你开发一个与 FastGPT 对标的本地智能知识库系统。

需要我帮你生成项目目录结构或示例代码，可以随时告诉我！
