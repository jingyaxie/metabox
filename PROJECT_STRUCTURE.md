# MetaBox 项目结构说明

## 📁 目录结构总览

```
MetaBox/
├── 📄 .cursorrules              # 开发规范配置
├── 📄 README.md                 # 项目主文档
├── 📄 CHANGELOG.md              # 版本更新日志
├── 📄 env.example               # 环境变量示例
├── 📄 PROJECT_STRUCTURE.md      # 项目结构说明（本文件）
├── 📄 local_kb_system_spec_full.md  # 系统技术规格文档
│
├── 🎨 frontend/                 # React 前端应用
│   ├── 📄 package.json          # 前端依赖配置
│   ├── 📁 src/                  # 源代码目录
│   │   ├── 📁 components/       # 可复用组件
│   │   ├── 📁 pages/           # 页面组件
│   │   ├── 📁 hooks/           # 自定义 Hooks
│   │   ├── 📁 stores/          # Zustand 状态管理
│   │   ├── 📁 services/        # API 服务
│   │   ├── 📁 utils/           # 工具函数
│   │   └── 📁 types/           # TypeScript 类型定义
│   ├── 📁 tests/               # 前端测试
│   └── 📁 public/              # 静态资源
│
├── ⚙️ backend/                  # FastAPI 后端应用
│   ├── 📄 requirements.txt      # Python 依赖
│   ├── 📁 app/                 # 应用代码目录
│   │   ├── 📁 api/             # API 路由
│   │   ├── 📁 core/            # 核心配置
│   │   ├── 📁 models/          # 数据模型
│   │   ├── 📁 services/        # 业务逻辑
│   │   └── 📁 utils/           # 工具函数
│   ├── 📁 tests/               # 后端测试
│   └── 📁 alembic/             # 数据库迁移
│
├── 🐳 docker/                   # Docker 配置
│   ├── 📄 docker-compose.yml   # 容器编排配置
│   ├── 📁 frontend/            # 前端 Docker 配置
│   └── 📁 backend/             # 后端 Docker 配置
│
├── 🔧 scripts/                  # 部署和运维脚本
│   ├── 📄 deploy.sh            # 一键部署脚本
│   ├── 📄 backup.sh            # 数据备份脚本
│   └── 📄 monitor.sh           # 监控脚本
│
├── 📚 docs/                     # 项目文档
│   ├── 📁 api/                 # API 文档
│   ├── 📁 deployment/          # 部署文档
│   └── 📁 development/         # 开发文档
│
└── 🧪 tests/                    # 集成测试
    ├── 📁 e2e/                 # 端到端测试
    └── 📁 performance/         # 性能测试
```

## 🎯 各模块详细说明

### 🎨 前端模块 (`frontend/`)

**技术栈：** React + TypeScript + Tailwind CSS + Zustand

**核心功能：**
- 知识库管理界面
- 聊天对话界面
- 插件管理界面
- 用户权限管理界面

**目录说明：**
- `components/`: 可复用的 UI 组件
- `pages/`: 页面级组件
- `hooks/`: 自定义 React Hooks
- `stores/`: Zustand 状态管理
- `services/`: API 调用服务
- `utils/`: 工具函数
- `types/`: TypeScript 类型定义

### ⚙️ 后端模块 (`backend/`)

**技术栈：** FastAPI + SQLAlchemy + Pydantic

**核心功能：**
- RESTful API 服务
- 用户认证与权限管理
- RAG 检索与问答
- 文件上传与处理
- 插件系统管理

**目录说明：**
- `api/`: API 路由定义
- `core/`: 核心配置和中间件
- `models/`: 数据库模型
- `services/`: 业务逻辑服务
- `utils/`: 工具函数

### 🐳 Docker 配置 (`docker/`)

**服务组件：**
- `frontend`: React 前端容器
- `backend`: FastAPI 后端容器
- `postgres`: PostgreSQL 数据库
- `qdrant`: Qdrant 向量数据库
- `redis`: Redis 缓存服务
- `nginx`: 反向代理（可选）

### 🔧 脚本工具 (`scripts/`)

**部署脚本：**
- `deploy.sh`: 一键部署脚本
- `backup.sh`: 数据备份脚本
- `monitor.sh`: 系统监控脚本

### 📚 文档目录 (`docs/`)

**文档分类：**
- `api/`: API 接口文档
- `deployment/`: 部署指南
- `development/`: 开发指南

## 🚀 开发流程

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd MetaBox

# 配置环境变量
cp env.example .env
# 编辑 .env 文件
```

### 2. 开发模式
```bash
# 前端开发
cd frontend
npm install
npm run dev

# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. 生产部署
```bash
# 一键部署
./scripts/deploy.sh prod

# 查看服务状态
docker-compose ps
```

## 📋 开发规范

### 代码规范
- 前端：ESLint + Prettier
- 后端：Black + isort + flake8
- 提交信息：遵循 Conventional Commits

### 测试要求
- 前端：Jest + React Testing Library
- 后端：Pytest + FastAPI TestClient
- 覆盖率：> 80%

### 文档要求
- API 文档：自动生成
- 代码注释：中文注释
- 提交信息：中文描述

## 🔍 快速导航

| 功能 | 文件路径 | 说明 |
|------|----------|------|
| 项目配置 | `.cursorrules` | 开发规范配置 |
| 环境变量 | `env.example` | 环境变量模板 |
| 部署配置 | `docker/docker-compose.yml` | Docker 编排 |
| 部署脚本 | `scripts/deploy.sh` | 一键部署 |
| 前端入口 | `frontend/src/` | React 应用 |
| 后端入口 | `backend/app/` | FastAPI 应用 |
| API 文档 | `docs/api/` | 接口文档 |
| 部署文档 | `docs/deployment/` | 部署指南 |

## 🆘 常见问题

### Q: 如何添加新的 API 接口？
A: 在 `backend/app/api/` 下创建新的路由文件，在 `backend/app/services/` 下实现业务逻辑。

### Q: 如何添加新的前端页面？
A: 在 `frontend/src/pages/` 下创建页面组件，在 `frontend/src/components/` 下创建可复用组件。

### Q: 如何修改数据库结构？
A: 修改 `backend/app/models/` 下的模型文件，使用 Alembic 生成迁移文件。

### Q: 如何添加新的插件？
A: 在 `backend/app/plugins/` 下创建插件文件，在前端 `frontend/src/components/` 下创建插件界面。

---

📧 如有问题，请联系：support@metabox.com 