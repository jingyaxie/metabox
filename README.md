# MetaBox - 本地智能知识库系统

一个基于 FastAPI + React + TypeScript 的现代化智能知识库系统，支持文档管理、智能检索、多模态处理和插件扩展。

## 🚀 项目特性

- 🧠 **RAG + 多模态检索**：支持文本和图片的智能检索与问答
- 🖼️ **统一向量库**：文本和图片向量库，实现多模态搜索
- 🧩 **插件系统**：支持插件扩展和 Agent 多步推理
- 🧑‍💼 **权限管理**：多用户多角色 RBAC 权限控制
- 🐳 **一键部署**：Docker Compose 本地私有化部署
- ⚙️ **模块化架构**：清晰的分层架构，易于扩展维护

## 📋 功能模块

| 模块 | 功能描述 |
|------|----------|
| 知识库管理 | 文档上传、图片上传、自动向量化 |
| Chat 对话 | RAG 检索、多模态问答、历史记录 |
| 插件系统 | 插件注册、管理、Agent 推理 |
| 权限管理 | 用户注册、登录、角色权限控制 |
| 多模态支持 | 文本/图片向量化、混合检索 |

## 🏗️ 技术架构

```
┌─────────────────┐
│   React 前端    │ TypeScript + Tailwind + Zustand
└─────────┬───────┘
          ↓
┌─────────────────┐
│   FastAPI 后端  │ Python + SQLAlchemy + Pydantic
└─────────┬───────┘
          ↓
┌─────────┬───────┐
│ Qdrant  │PostgreSQL│ 向量库 + 结构化数据
└─────────┴───────┘
```

## 🚀 快速开始

### 方式一：使用一键部署脚本（推荐）

#### macOS/Linux 用户
```bash
# 给脚本添加执行权限
chmod +x scripts/dev_setup.sh

# 首次完整环境设置
./scripts/dev_setup.sh setup

# 启动服务
./scripts/dev_setup.sh start

# 检查服务状态
./scripts/dev_setup.sh status

# 停止服务
./scripts/dev_setup.sh stop

# 重启服务
./scripts/dev_setup.sh restart

# 清理环境
./scripts/dev_setup.sh clean
```

#### Windows 用户
```cmd
# 首次完整环境设置
scripts\dev_setup.bat setup

# 启动服务
scripts\dev_setup.bat start

# 检查服务状态
scripts\dev_setup.bat status

# 停止服务
scripts\dev_setup.bat stop

# 重启服务
scripts\dev_setup.bat restart

# 清理环境
scripts\dev_setup.bat clean
```

### 方式二：手动部署

#### 环境要求
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose
- Git

#### 后端部署
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate.bat  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 设置环境变量
cp ../env.example ../.env
# 编辑 .env 文件配置数据库连接等信息

# 启动数据库服务
cd ..
docker-compose up -d postgres redis qdrant

# 初始化数据库
cd backend
python -m alembic upgrade head

# 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端部署
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 📁 项目结构

```
MetaBox/
├── frontend/                 # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   ├── pages/           # 页面组件
│   │   ├── hooks/           # 自定义 Hooks
│   │   ├── stores/          # Zustand 状态管理
│   │   ├── services/        # API 服务
│   │   ├── utils/           # 工具函数
│   │   └── types/           # TypeScript 类型
│   ├── tests/               # Jest + RTL 测试
│   └── package.json
├── backend/                  # FastAPI + Python
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── tests/               # Pytest 测试
│   └── requirements.txt
├── docker/                   # Docker 配置
├── scripts/                  # 部署脚本
│   ├── dev_setup.sh         # macOS/Linux 开发脚本
│   └── dev_setup.bat        # Windows 开发脚本
├── docs/                     # 项目文档
└── tests/                    # 集成测试
```

## 🔧 核心功能

### 知识库管理
- 📚 多知识库支持
- 📄 文档上传与解析
- 🖼️ 图片处理与向量化
- 🔍 智能检索与召回测试

### 智能对话
- 💬 多轮对话支持
- 🧠 RAG 检索增强生成
- 🔄 流式响应
- 📊 会话管理

### 插件系统
- 🔌 插件开发框架
- 🤖 Agent 多步推理
- ⚙️ 插件管理界面
- 🧪 插件测试工具

### 高级 RAG 优化
- 📝 智能文本分割
- 🔗 父子块分割策略
- 🎯 多模型 Embedding 路由
- 🔄 混合检索引擎
- 📊 重排序优化

## 🌐 访问地址

启动成功后，可通过以下地址访问：

- **前端界面**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **数据库管理**: http://localhost:5432 (PostgreSQL)

## 📚 开发文档

- [API 文档](docs/api/)
- [部署指南](docs/deployment/)
- [开发指南](docs/development/)
- [RAG 优化技术](docs/rag_optimization_tech.md)

## 🧪 测试

### 后端测试
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### 前端测试
```bash
cd frontend
npm test
```

### 集成测试
```bash
pytest tests/integration/ -v
```

## 🚀 生产部署

### Docker Compose 部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 环境变量配置
复制 `env.example` 为 `.env` 并配置：
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/metabox
REDIS_URL=redis://localhost:6379

# 向量数据库配置
QDRANT_URL=http://localhost:6333

# API 密钥
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key

# 其他配置
DEBUG=false
LOG_LEVEL=INFO
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 常见问题

### Q: 脚本执行权限问题
```bash
chmod +x scripts/dev_setup.sh
```

### Q: Docker 服务未启动
确保 Docker Desktop 已启动并运行。

### Q: 端口被占用
修改 `docker-compose.yml` 中的端口映射，或停止占用端口的服务。

### Q: 数据库连接失败
检查 `.env` 文件中的数据库配置，确保 PostgreSQL 容器正常运行。

## 📞 支持

如有问题，请：
1. 查看 [常见问题](#常见问题) 部分
2. 检查 [开发文档](docs/development/)
3. 提交 [Issue](../../issues)

---

**MetaBox** - 让知识管理更智能 🚀 