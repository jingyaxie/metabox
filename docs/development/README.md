# MetaBox 开发指南

## 🛠️ 开发环境搭建

### 前置要求

- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- Git

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/MetaBox.git
cd MetaBox
```

### 2. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 3. 前端开发环境

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm test

# 代码检查
npm run lint
```

### 4. 后端开发环境

> **强制要求：所有后端依赖必须安装在 backend/venv 虚拟环境目录下，严禁污染系统环境。**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖（推荐开发用 requirements-dev.txt）
pip install -r requirements-dev.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 代码格式化
black .
isort .
```

### 5. 数据库设置

```bash
# 启动数据库服务
docker-compose up postgres qdrant -d

# 运行数据库迁移
cd backend
alembic upgrade head
```

## 📁 项目结构说明

### 前端结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── ui/             # 基础 UI 组件
│   │   ├── chat/           # 聊天相关组件
│   │   │   ├── ChatSidebar.tsx      # 左侧会话列表
│   │   │   ├── ChatMessageList.tsx  # 消息列表
│   │   │   ├── ChatMessage.tsx      # 单条消息气泡
│   │   │   ├── ChatInputBar.tsx     # 底部输入区
│   │   │   ├── ModelSelector.tsx    # 模型选择器
│   │   │   ├── KnowledgeBaseSelector.tsx # 知识库选择器
│   │   │   └── ChatHeader.tsx       # 聊天头部
│   │   ├── kb/             # 知识库相关组件
│   │   └── common/         # 通用组件
│   ├── pages/              # 页面组件
│   │   ├── Home.tsx        # 首页
│   │   ├── Chat.tsx        # 聊天页面
│   │   ├── KnowledgeBase.tsx # 知识库页面
│   │   └── Settings.tsx    # 设置页面
│   ├── hooks/              # 自定义 Hooks
│   │   ├── useAuth.ts      # 认证相关
│   │   ├── useChat.ts      # 聊天相关
│   │   └── useKB.ts        # 知识库相关
│   ├── stores/             # Zustand 状态管理
│   │   ├── authStore.ts    # 认证状态
│   │   ├── chatStore.ts    # 聊天状态
│   │   └── kbStore.ts      # 知识库状态
│   ├── services/           # API 服务
│   │   ├── api.ts          # API 客户端
│   │   ├── auth.ts         # 认证 API
│   │   ├── chat.ts         # 聊天 API
│   │   └── kb.ts           # 知识库 API
│   ├── utils/              # 工具函数
│   │   ├── constants.ts    # 常量定义
│   │   ├── helpers.ts      # 辅助函数
│   │   └── validators.ts   # 验证函数
│   └── types/              # TypeScript 类型
│       ├── api.ts          # API 类型
│       ├── chat.ts         # 聊天类型
│       └── kb.ts           # 知识库类型
├── tests/                  # 测试文件
├── public/                 # 静态资源
└── package.json
```

### 后端结构

```
backend/
├── app/
│   ├── api/                # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证相关 API
│   │   ├── chat.py         # 聊天相关 API
│   │   ├── kb.py           # 知识库相关 API
│   │   └── plugins.py      # 插件相关 API
│   ├── core/               # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库配置
│   │   ├── security.py     # 安全相关
│   │   └── dependencies.py # 依赖注入
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模型
│   │   ├── kb.py           # 知识库模型
│   │   └── chat.py         # 聊天模型
│   ├── services/           # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auth_service.py # 认证服务
│   │   ├── chat_service.py # 聊天服务
│   │   ├── kb_service.py   # 知识库服务
│   │   ├── rag_service.py  # RAG 服务
│   │   └── vector_service.py # 向量服务
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py   # 文件处理
│   │   ├── text_utils.py   # 文本处理
│   │   └── image_utils.py  # 图像处理
│   └── main.py             # 应用入口
├── tests/                  # 测试文件
├── alembic/                # 数据库迁移
└── requirements.txt
```

## 🔧 开发规范

### 代码风格

#### 前端 (TypeScript/React)

- 使用函数组件 + Hooks
- 组件名使用 PascalCase
- 文件名使用 PascalCase (组件) 或 camelCase (工具)
- 使用 TypeScript 严格模式
- 必须为组件定义 Props 接口

```typescript
// ✅ 正确示例
interface ChatMessageProps {
  message: Message;
  onDelete?: (id: string) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onDelete }) => {
  return <div>{message.content}</div>;
};
```

#### 后端 (Python/FastAPI)

- 使用类型注解
- 遵循 PEP 8 规范
- 使用 Pydantic 进行数据验证
- 异步函数使用 async/await

```python
# ✅ 正确示例
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    kb_ids: List[str]
    history: Optional[List[dict]] = None

async def chat_endpoint(request: ChatRequest) -> dict:
    result = await chat_service.process(request)
    return {"answer": result}
```

## 💬 Chat 界面设计规范

### 设计目标
对标 ChatGPT 的现代化对话体验，支持知识库和大模型灵活切换，界面美观、交互流畅，提升专业感和易用性。

### 页面布局结构

#### 1. 整体布局
```
┌─────────────────────────────────────────────────────────────┐
│                   顶部导航栏 (Layout)                        │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│   左侧栏    │                主对话区                        │
│  (Sidebar)  │                                               │
│             │  ┌─────────────────────────────────────────┐  │
│             │  │           聊天头部 (Header)              │  │
│             │  └─────────────────────────────────────────┘  │
│             │                                               │
│             │  ┌─────────────────────────────────────────┐  │
│             │  │          消息列表 (MessageList)          │  │
│             │  │                                           │  │
│             │  │  ┌─────────────────────────────────────┐  │
│             │  │  │        用户消息气泡                  │  │
│             │  │  └─────────────────────────────────────┘  │
│             │  │                                           │  │
│             │  │  ┌─────────────────────────────────────┐  │
│             │  │  │        AI 消息气泡                   │  │
│             │  │  └─────────────────────────────────────┘  │
│             │  └─────────────────────────────────────────┘  │
│             │                                               │
│             │  ┌─────────────────────────────────────────┐  │
│             │  │          输入区域 (InputBar)             │  │
│             │  │  ┌─────────────────────────────────────┐  │
│             │  │  │  知识库选择 │ 模型选择 │ 发送按钮    │  │
│             │  │  └─────────────────────────────────────┘  │
│             │  │  ┌─────────────────────────────────────┐  │
│             │  │  │           多行输入框                 │  │
│             │  │  └─────────────────────────────────────┘  │
│             │  └─────────────────────────────────────────┘  │
└─────────────┴───────────────────────────────────────────────┘
```

#### 2. 左侧栏 (ChatSidebar)
- **功能**：会话列表管理
- **组件**：
  - 新建会话按钮
  - 会话列表（支持搜索、重命名、删除）
  - 会话分组（最近、收藏等）
- **交互**：
  - 点击切换会话
  - 右键菜单（重命名、删除、导出）
  - 拖拽排序

#### 3. 聊天头部 (ChatHeader)
- **功能**：当前会话信息与操作
- **组件**：
  - 会话标题（可编辑）
  - 操作按钮（清空、导出、设置）
  - 当前模型/知识库状态
- **交互**：
  - 点击标题编辑
  - 悬停显示操作按钮

#### 4. 消息列表 (ChatMessageList)
- **功能**：消息流展示
- **组件**：
  - 消息气泡（用户/AI）
  - 消息状态（发送中、成功、失败）
  - 消息操作（复制、重新生成、反馈）
- **交互**：
  - 自动滚动到底部
  - 流式响应动画
  - 消息引用与追溯

#### 5. 输入区域 (ChatInputBar)
- **功能**：消息输入与发送
- **组件**：
  - 知识库选择下拉框
  - 模型选择下拉框
  - 多行输入框
  - 发送按钮
  - 文件上传按钮
  - 高级设置折叠面板
- **交互**：
  - Enter 发送，Shift+Enter 换行
  - 拖拽上传文件
  - 输入框自适应高度

### 组件设计规范

#### 1. ChatSidebar 组件
```typescript
interface ChatSidebarProps {
  sessions: Session[];
  currentSessionId: string;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
  onSessionDelete: (sessionId: string) => void;
  onSessionRename: (sessionId: string, name: string) => void;
}
```

#### 2. ChatMessage 组件
```typescript
interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
  onCopy?: (content: string) => void;
  onRegenerate?: () => void;
  onFeedback?: (type: 'like' | 'dislike') => void;
}
```

#### 3. ChatInputBar 组件
```typescript
interface ChatInputBarProps {
  onSend: (message: string, options: SendOptions) => void;
  onFileUpload: (files: File[]) => void;
  knowledgeBases: KnowledgeBase[];
  models: Model[];
  selectedKnowledgeBase: string;
  selectedModel: string;
  onKnowledgeBaseChange: (kbId: string) => void;
  onModelChange: (modelId: string) => void;
}
```

### 状态管理设计

#### 1. Chat Store (Zustand)
```typescript
interface ChatStore {
  // 会话管理
  sessions: Session[];
  currentSessionId: string;
  
  // 消息管理
  messages: Record<string, Message[]>;
  streamingMessageId: string | null;
  
  // 配置管理
  selectedKnowledgeBase: string;
  selectedModel: string;
  chatSettings: ChatSettings;
  
  // 操作
  createSession: () => void;
  switchSession: (sessionId: string) => void;
  sendMessage: (content: string) => Promise<void>;
  updateSettings: (settings: Partial<ChatSettings>) => void;
}
```

### 交互规范

#### 1. 快捷键
- `Enter`: 发送消息
- `Shift + Enter`: 换行
- `Ctrl/Cmd + K`: 新建会话
- `Ctrl/Cmd + L`: 清空当前会话
- `Ctrl/Cmd + S`: 导出会话

#### 2. 消息反馈
- 每条 AI 消息下方显示 👍/👎 按钮
- 点击后记录反馈，可撤销
- 反馈数据用于模型优化

#### 3. 文件上传
- 支持拖拽到输入框
- 支持点击上传按钮
- 支持图片预览
- 文件大小限制：10MB

#### 4. 流式响应
- 实时显示 AI 回复
- 打字机效果
- 支持中断响应
- 响应完成后显示操作按钮

### 视觉设计规范

#### 1. 配色方案
- **主色调**: #10a37f (ChatGPT 绿)
- **背景色**: #ffffff (主背景), #f7f7f8 (侧边栏)
- **文字色**: #374151 (主要文字), #6b7280 (次要文字)
- **边框色**: #e5e7eb
- **强调色**: #3b82f6 (链接), #ef4444 (错误)

#### 2. 字体规范
- **主字体**: Inter, -apple-system, BlinkMacSystemFont
- **代码字体**: 'Fira Code', 'Monaco', 'Consolas'
- **字号**: 14px (正文), 16px (标题), 12px (辅助文字)

#### 3. 间距规范
- **组件间距**: 16px, 24px, 32px
- **内边距**: 12px, 16px, 20px
- **圆角**: 8px (卡片), 6px (按钮), 4px (输入框)

#### 4. 阴影规范
- **卡片阴影**: 0 1px 3px 0 rgba(0, 0, 0, 0.1)
- **悬浮阴影**: 0 4px 6px -1px rgba(0, 0, 0, 0.1)
- **输入框阴影**: 0 0 0 3px rgba(16, 163, 127, 0.1)

### 响应式设计

#### 1. 断点设置
- **移动端**: < 768px
- **平板**: 768px - 1024px
- **桌面**: > 1024px

#### 2. 移动端适配
- 侧边栏可折叠
- 输入框固定在底部
- 消息气泡全宽显示
- 触摸友好的按钮尺寸

### 性能优化

#### 1. 消息渲染
- 虚拟滚动（大量消息时）
- 消息懒加载
- 图片懒加载

#### 2. 状态管理
- 消息分页加载
- 会话列表缓存
- 防抖搜索

#### 3. 网络优化
- 流式响应
- 请求取消
- 错误重试
- 离线支持

### 测试规范

#### 1. 单元测试
- 组件渲染测试
- 用户交互测试
- 状态管理测试

#### 2. 集成测试
- 消息发送流程
- 会话管理流程
- 文件上传流程

#### 3. E2E 测试
- 完整对话流程
- 多会话切换
- 响应式布局

## 🚀 部署流程

### 开发环境部署

```bash
# 使用 Docker Compose
docker-compose up -d

# 或使用部署脚本
./scripts/deploy.sh dev
```

### 生产环境部署

```bash
# 生产环境部署
./scripts/deploy.sh prod
```

## 📚 常用命令

### 前端

```bash
# 开发
npm run dev

# 构建
npm run build

# 测试
npm test
npm run test:coverage

# 代码检查
npm run lint
npm run lint:fix
```

### 后端

```bash
# 开发
uvicorn app.main:app --reload

# 测试
pytest
pytest --cov=app

# 代码格式化
black .
isort .

# 类型检查
mypy app/
```

### 数据库

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🐛 常见问题

### 1. 前端构建失败

```bash
# 清理缓存
rm -rf node_modules package-lock.json
npm install
```

### 2. 后端依赖冲突

```bash
# 重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 数据库连接失败

```bash
# 检查数据库服务状态
docker-compose ps

# 重启数据库服务
docker-compose restart postgres
```

## 📞 技术支持

- 📧 邮箱：dev@metabox.com
- 💬 讨论：[GitHub Discussions](https://github.com/your-repo/MetaBox/discussions)
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/MetaBox/issues) 

## 智能配置与前后端联调说明

### 1. 智能配置API对接
- 路径：`POST /kb/smart-config`
- 参数：content（文档内容），user_preferences（可选，用户自定义参数）
- 返回：推荐参数、类型、置信度、验证结果

### 2. 前端参数映射
- 推荐参数与前端表单字段一一对应
- 支持高级参数（分隔符、header层级、语义阈值等）
- 参数变更后可实时请求API校验与预览

### 3. 配置预览与性能评估
- 路径：`POST /kb/smart-config/preview`
- 返回：分块预览、性能指标、质量评分
- 前端展示：分块内容、分块数、平均大小、处理时间、内存、存储、评分

### 4. 配置模板管理
- 支持保存、应用、更新、删除配置模板
- 路径：`/kb/smart-config/template`（POST/GET/PUT/DELETE）
- 批量应用：`/kb/smart-config/batch`

### 5. Embedding路由与混合分块
- embedding_model参数可选，支持多模型
- use_parent_child/parent_chunk_size/child_chunk_size参数支持混合分块
- 前端可视化父子结构

---

如需联调或扩展新功能，请参考docs/rag_optimization_tech.md技术方案。 