# MetaBox - 本地智能知识库系统

> 对标 FastGPT 的本地私有化部署智能知识库系统

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

### 环境要求

- Docker & Docker Compose
- Node.js 18+ (开发环境)
- Python 3.9+ (开发环境)

### 一键部署

```bash
# 克隆项目
git clone https://github.com/your-repo/MetaBox.git
cd MetaBox

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的 API Key

# 启动服务
docker-compose up -d

# 访问系统
# 前端: http://localhost:3000
# 后端: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 开发环境

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

## 📚 文档

- [API 文档](./docs/api/) - 完整的 API 接口文档
- [部署指南](./docs/deployment/) - 详细部署说明
- [开发指南](./docs/development/) - 开发环境搭建

## 🧪 测试

```bash
# 前端测试
cd frontend && npm test

# 后端测试
cd backend && pytest

# 集成测试
npm run test:e2e
```

## 📦 项目结构

```
MetaBox/
├── frontend/          # React 前端应用
├── backend/           # FastAPI 后端应用
├── docker/            # Docker 配置文件
├── scripts/           # 部署和运维脚本
├── docs/              # 项目文档
├── tests/             # 集成测试
└── .cursorrules       # 开发规范
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持

- 📧 邮箱：support@metabox.com
- 💬 讨论：[GitHub Discussions](https://github.com/your-repo/MetaBox/discussions)
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/MetaBox/issues)

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！ 