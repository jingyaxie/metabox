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

### Git 工作流

1. **分支命名**
   - 功能分支：`feature/功能名称`
   - 修复分支：`fix/问题描述`
   - 文档分支：`docs/文档内容`

2. **提交信息格式**
   ```
   type(scope): description
   
   feat(auth): 添加用户登录功能
   fix(chat): 修复消息发送失败问题
   docs(readme): 更新部署说明
   ```

3. **代码审查**
   - 所有 PR 必须通过代码审查
   - 确保测试通过
   - 检查代码覆盖率

### 测试规范

#### 前端测试

```typescript
// components/__tests__/ChatMessage.test.tsx
import { render, screen } from '@testing-library/react';
import ChatMessage from '../ChatMessage';

describe('ChatMessage', () => {
  it('应该正确显示消息内容', () => {
    const message = { id: '1', content: '测试消息', role: 'user' };
    render(<ChatMessage message={message} />);
    
    expect(screen.getByText('测试消息')).toBeInTheDocument();
  });
});
```

#### 后端测试

```python
# tests/test_chat.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.post("/api/chat", json={
        "message": "测试消息",
        "kb_ids": ["test-kb-id"]
    })
    
    assert response.status_code == 200
    assert "answer" in response.json()
```

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