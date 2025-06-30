
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

---

## 二、系统架构总览

```text
┌─────────────────────────────┐
│         Web 前端 UI         │ React + Tailwind + Zustand │
└─────────────────────────────┘
            ↓
┌─────────────────────────────┐
│         后端 API 服务        │ FastAPI / NestJS            │
│ 用户系统 / RAG / 插件 / Agent│                            │
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

### 1️⃣ 知识库管理模块

- 创建、编辑、删除知识库
- 支持文本文件（PDF、Word、Markdown、TXT）上传
- 支持图片上传，自动向量化并绑定描述
- 文本自动切分并生成向量入库

### 2️⃣ Chat 对话模块（RAG）

- 支持文本问题的向量检索与上下文构建
- 支持图片问题，结合图像向量库进行检索
- 支持多模型接入（OpenAI、通义千问、Claude 等）

### 3️⃣ 插件系统与 Agent 推理

- 插件注册、管理与调用（搜索、翻译、天气等）
- Agent 多步骤推理流程，动态调用多个工具完成复杂任务

### 4️⃣ 多模态能力模块

- 文本 Embedding：支持 OpenAI、通义千问 Embedding API
- 图片向量化：支持 CLIP、Qwen-VL、BLIP-2 等模型
- 实现图文混合检索与多模态问答

### 5️⃣ 权限管理模块（RBAC）

- 用户注册、登录、JWT 鉴权
- 支持角色分级：超级管理员、管理员、普通用户、游客
- 绑定知识库访问权限，保护数据安全

### 6️⃣ 部署与运维

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

### 知识库表 `knowledge_bases`

| 字段           | 类型     | 描述              |
|----------------|----------|-------------------|
| id             | UUID     | 知识库唯一标识    |
| name           | TEXT     | 知识库名称        |
| type           | TEXT     | 类型（text/image） |
| owner_id       | UUID     | 所属用户          |

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
- 支持响应式设计，兼容移动端  
- 聊天窗口支持文本、图片、文件混排  
- 输入框支持多功能扩展（表情、上传、插件）  
- 支持暗黑模式和浅色模式切换  

### 2. 主要页面结构

```
┌─────────────────────────────────────────────┐
│                  顶部导航栏                  │
│ [LOGO]       [知识库管理] [聊天] [插件] [设置]│
└────────────┬─────────────────────────────┬───┘
             │                             │
             │                             │
     ┌───────┴────────────┐      ┌─────────┴──────────┐
     │  左侧知识库列表    │      │      右侧主内容区   │
     │ - 搜索知识库       │      │ - 选中知识库详情     │
     │ - 新建 / 导入知识库│      │ - 文档列表 / 图片列表 │
     │ - 状态指示         │      │ - 聊天界面           │
     └────────────────────┘      └──────────────────────┘
```

### 3. 主要界面模块说明

| 组件名              | 说明                              |
|---------------------|---------------------------------|
| `TopNav`            | 顶部导航，知识库、聊天、插件切换 |
| `Sidebar`           | 左侧知识库列表及操作              |
| `KnowledgeBaseView` | 知识库文件详情（文档/图片列表）  |
| `ChatWindow`        | 聊天主界面，支持图文混排         |
| `ChatInput`         | 多功能输入框，支持快捷发送及插件 |
| `PluginManager`     | 插件管理和调用界面                |
| `UserSettings`      | 用户信息和权限设置                |

### 4. 交互细节

- 文件支持拖拽上传  
- 聊天消息支持代码块、高亮、图片显示  
- 消息发送时显示加载状态  
- 历史聊天分页加载和搜索  
- 支持快捷键发送和消息清空  
- 移动端侧栏自动折叠  

### 5. 设计风格建议

- 参考 FastGPT，主色调蓝灰，简洁风  
- 使用 Tailwind CSS / Chakra UI 等快速构建  
- 字体大小适中，注重阅读体验和操作便利  

---

## 八、开发阶段规划

| 阶段 | 功能描述                          |
|-------|---------------------------------|
| V1    | 文本知识库上传、切分、向量化，基础聊天功能  |
| V2    | 图片上传、图像向量库、多模态问答         |
| V3    | 插件系统及 Agent 多步骤推理             |
| V4    | 用户注册、登录、多角色权限管理            |
| V5    | 部署优化、监控、模型热切换等              |

---

## 九、扩展建议（可选）

- 评分与用户反馈系统  
- Webhook 自动同步知识库数据  
- 多模型路由与 A/B 测试支持  
- 可视化知识图谱（如 Neo4j）  
- PWA 移动端支持  
- 多租户支持（SaaS）  

---

# 结束语

以上文档涵盖了系统架构、模块功能、数据库设计、API接口、Docker部署与详细界面架构，能完整指导你开发一个与 FastGPT 对标的本地智能知识库系统。

需要我帮你生成项目目录结构或示例代码，可以随时告诉我！
