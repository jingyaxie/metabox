# MetaBox - 企业级智能知识库系统

一个基于 FastAPI + React + TypeScript 的现代化企业级智能知识库系统，支持多模态检索、智能问答、插件扩展和完整的权限管理。

## 🚀 核心特性

### 🧠 智能检索引擎
- **智能检索服务**：自动识别查询意图，智能选择最佳检索策略
- **多模态检索**：支持文本和图片的统一向量检索
- **增强检索流水线**：查询扩展、混合检索、重排序、元数据过滤
- **召回测试系统**：完整的检索效果评估和优化工具

### 💬 现代化聊天界面
- **ChatGPT风格界面**：对标ChatGPT的现代化设计
- **多会话管理**：新建、切换、重命名、删除会话
- **流式响应**：实时显示AI回复，支持中断
- **多模型支持**：动态切换不同AI模型
- **知识库集成**：灵活选择知识库进行问答

### 🏢 企业级管理功能
- **超级管理员系统**：模型供应商管理、系统配置、用户管理
- **API密钥管理**：完整的API访问控制和权限管理
- **外部API接口**：支持无上下文的外部智能检索
- **RBAC权限控制**：多用户多角色权限管理

### 🔌 插件与扩展
- **插件系统**：支持自定义插件开发和集成
- **Agent推理**：多步推理和智能任务执行
- **智能配置**：基于文档内容的智能分块配置

## 📋 功能模块总览

| 模块 | 功能描述 | 状态 |
|------|----------|------|
| **用户认证** | 用户注册、登录、JWT认证、权限控制 | ✅ 已完成 |
| **知识库管理** | 文档上传、图片上传、自动向量化、智能分块 | ✅ 已完成 |
| **智能聊天** | ChatGPT风格界面、多会话、流式响应、多模型 | ✅ 已完成 |
| **智能检索** | 意图识别、策略调度、多模态检索、召回测试 | ✅ 已完成 |
| **增强检索** | 查询扩展、混合检索、重排序、元数据过滤 | ✅ 已完成 |
| **超级管理员** | 模型供应商管理、系统配置、用户管理 | ✅ 已完成 |
| **API密钥管理** | API访问控制、权限管理、使用统计 | ✅ 已完成 |
| **外部API** | 无上下文外部检索、API密钥认证 | ✅ 已完成 |
| **插件系统** | 插件管理、Agent推理、扩展开发 | ✅ 已完成 |
| **智能配置** | 文档智能分块、配置模板、批量配置 | ✅ 已完成 |

## 🎨 用户界面特性

### ✨ 现代化设计
- **ChatGPT风格**：采用ChatGPT官方设计风格，界面简洁美观
- **响应式布局**：完美适配桌面、平板、手机等不同设备
- **流畅动画**：打字机效果、平滑滚动、优雅过渡

### 🔄 多会话管理
- **左侧会话栏**：新建、切换、重命名、删除会话
- **会话搜索**：快速查找历史会话
- **会话导出**：支持TXT、MD、JSON格式导出

### 🎯 智能配置
- **知识库选择**：下拉选择特定知识库或全部知识库
- **模型切换**：支持GPT-3.5、GPT-4、Claude、Qwen等多种模型
- **高级设置**：温度、最大长度、系统提示词等参数调节

### 💬 交互体验
- **快捷键支持**：Enter发送、Shift+Enter换行、Ctrl+K新建会话
- **文件上传**：拖拽或点击上传文档、图片
- **消息操作**：复制、重新生成、点赞/踩反馈
- **流式响应**：实时显示AI回复，支持中断

## 🏗️ 技术架构

```
┌─────────────────┐
│   React 前端    │ TypeScript + Tailwind + Zustand
│                 │ - 现代化UI组件库
│                 │ - 响应式设计
│                 │ - 状态管理
└─────────┬───────┘
          ↓
┌─────────────────┐
│   FastAPI 后端  │ Python + SQLAlchemy + Pydantic
│                 │ - RESTful API设计
│                 │ - 异步处理
│                 │ - 数据验证
└─────────┬───────┘
          ↓
┌─────────┬───────┬───────┐
│ Qdrant  │PostgreSQL│ Redis │ 数据存储
│ 向量库  │结构化数据│ 缓存  │
└─────────┴───────┴───────┘
```

## 🚀 快速开始

### 方式一：使用一键部署脚本（推荐）

#### 选项A：Docker版本（推荐）
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

#### 选项B：非Docker版本（本地服务）
```bash
# 给脚本添加执行权限
chmod +x scripts/dev_setup_no_docker.sh

# 首次完整环境设置（会自动安装PostgreSQL、Redis等）
./scripts/dev_setup_no_docker.sh setup

# 启动服务
./scripts/dev_setup_no_docker.sh start

# 检查服务状态
./scripts/dev_setup_no_docker.sh status

# 停止服务
./scripts/dev_setup_no_docker.sh stop

# 重启服务
./scripts/dev_setup_no_docker.sh restart

# 清理环境
./scripts/dev_setup_no_docker.sh clean
```

### 方式二：手动部署

#### 环境要求
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (Docker版本)
- PostgreSQL 14+ (非Docker版本)
- Redis 6+ (非Docker版本)
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

## 🔧 系统配置

### 超级管理员配置
1. 访问 `/admin/login` 进行管理员登录
2. 配置模型供应商（OpenAI、通义千问等）
3. 设置系统配置参数
4. 管理用户权限

### 知识库创建
1. 登录系统后进入知识库页面
2. 点击"创建知识库"
3. 选择模型配置
4. 上传文档和图片
5. 系统自动进行向量化处理

### API密钥管理
1. 在设置页面创建API密钥
2. 配置访问权限和限制
3. 获取API密钥用于外部调用

## 📚 使用指南

### 智能聊天
1. 进入聊天页面
2. 选择知识库和模型
3. 开始对话，系统会自动检索相关知识
4. 支持多会话管理和历史记录

### 智能检索
1. 进入增强检索页面
2. 配置检索参数
3. 输入查询内容
4. 查看检索结果和相关性评分

### 召回测试
1. 在知识库详情页面选择"召回测试"标签
2. 创建测试用例
3. 运行测试并查看结果
4. 优化检索参数

## 🔌 API接口

### 内部API
- 认证相关：`/auth/*`
- 用户管理：`/users/*`
- 知识库管理：`/kb/*`
- 聊天接口：`/chat/*`
- 智能检索：`/intelligent-retrieval/*`
- 增强检索：`/enhanced-retrieval/*`
- 插件管理：`/plugins/*`

### 外部API
- 智能检索：`/api/v1/external/intelligent-search`
- 知识库问答：`/api/v1/external/chat/query`
- 向量检索：`/api/v1/external/retrieval/search`

### 管理员API
- 模型供应商：`/api/v1/admin/model-providers/*`
- 模型配置：`/api/v1/admin/model-configs/*`
- 系统配置：`/api/v1/admin/system-configs/*`
- 用户管理：`/api/v1/admin/users/*`

## 🛠️ 开发指南

### 项目结构
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
├── docs/                     # 项目文档
└── tests/                    # 集成测试
```

### 代码规范
- 前端：TypeScript + ESLint + Prettier
- 后端：Python + Black + isort + flake8
- 提交规范：Conventional Commits
- 测试覆盖率：> 80%

## 📊 性能指标

### 系统性能
- 支持并发用户：1000+
- 响应时间：< 2秒
- 检索准确率：> 90%
- 系统可用性：99.9%

### 硬件要求
- **最低配置**：4核CPU、8GB内存、100GB存储
- **推荐配置**：8核CPU、16GB内存、500GB存储
- **生产环境**：16核CPU、32GB内存、1TB存储

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 支持与反馈

- 📧 邮箱：support@metabox.ai
- 💬 讨论区：[GitHub Discussions](https://github.com/your-repo/discussions)
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档：[项目文档](https://docs.metabox.ai)

## 🙏 致谢

感谢所有为MetaBox项目做出贡献的开发者和用户！

---

**MetaBox** - 让知识管理更智能，让AI应用更简单 🚀 