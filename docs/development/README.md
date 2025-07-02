# MetaBox 开发指南

欢迎来到 MetaBox 开发指南！本文档将帮助您快速搭建开发环境，了解项目架构，并开始开发工作。

## 🚀 快速开始

### 环境要求
- **Python**: 3.8+
- **Node.js**: 16+
- **Git**: 最新版本
- **Docker**: 20.10+ (可选)
- **Docker Compose**: 2.0+ (可选)

### 开发环境搭建

#### 1. 克隆项目
```bash
git clone https://github.com/your-repo/metabox.git
cd metabox
```

#### 2. 后端环境配置
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
```

#### 3. 前端环境配置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 4. 数据库服务
```bash
# 启动数据库服务
docker-compose up -d postgres redis qdrant

# 初始化数据库
cd backend
python -m alembic upgrade head
```

#### 5. 启动后端服务
```bash
# 在backend目录下
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🏗️ 项目架构

### 整体架构
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

### 前端架构
```
frontend/
├── src/
│   ├── components/       # 可复用组件
│   │   ├── chat/        # 聊天相关组件
│   │   ├── ui/          # 基础UI组件
│   │   └── common/      # 通用组件
│   ├── pages/           # 页面组件
│   │   ├── Home.tsx     # 首页
│   │   ├── Chat.tsx     # 聊天页面
│   │   ├── KnowledgeBase.tsx # 知识库页面
│   │   ├── AdminDashboard.tsx # 管理员仪表板
│   │   └── Settings.tsx # 设置页面
│   ├── hooks/           # 自定义 Hooks
│   │   ├── useAuth.ts   # 认证相关
│   │   ├── useChat.ts   # 聊天相关
│   │   └── useKB.ts     # 知识库相关
│   ├── stores/          # Zustand 状态管理
│   │   ├── authStore.ts # 认证状态
│   │   ├── chatStore.ts # 聊天状态
│   │   └── kbStore.ts   # 知识库状态
│   ├── services/        # API 服务
│   │   ├── api.ts       # API 客户端
│   │   ├── auth.ts      # 认证 API
│   │   ├── chat.ts      # 聊天 API
│   │   └── kb.ts        # 知识库 API
│   ├── utils/           # 工具函数
│   │   ├── constants.ts # 常量定义
│   │   ├── helpers.ts   # 辅助函数
│   │   └── validators.ts # 验证函数
│   └── types/           # TypeScript 类型
│       ├── api.ts       # API 类型
│       ├── chat.ts      # 聊天类型
│       └── kb.ts        # 知识库类型
├── tests/               # 测试文件
├── public/              # 静态资源
└── package.json
```

### 后端架构
```
backend/
├── app/
│   ├── api/             # API 路由
│   │   ├── __init__.py  # 路由注册
│   │   ├── auth.py      # 认证相关 API
│   │   ├── chat.py      # 聊天相关 API
│   │   ├── knowledge_base.py # 知识库相关 API
│   │   ├── plugins.py   # 插件相关 API
│   │   ├── smart_config.py # 智能配置 API
│   │   ├── enhanced_retrieval.py # 增强检索 API
│   │   ├── intelligent_retrieval.py # 智能检索 API
│   │   └── v1/          # v1版本API
│   │       ├── admin.py # 管理员API
│   │       ├── api_keys.py # API密钥管理
│   │       ├── external.py # 外部API
│   │       └── external_intelligent.py # 外部智能检索
│   ├── core/            # 核心配置
│   │   ├── config.py    # 配置管理
│   │   ├── database.py  # 数据库配置
│   │   ├── auth.py      # 认证中间件
│   │   └── deps.py      # 依赖注入
│   ├── models/          # 数据模型
│   │   ├── user.py      # 用户模型
│   │   ├── knowledge_base.py # 知识库模型
│   │   ├── chat.py      # 聊天模型
│   │   ├── api_key.py   # API密钥模型
│   │   ├── admin.py     # 管理员模型
│   │   └── plugin.py    # 插件模型
│   ├── services/        # 业务逻辑
│   │   ├── auth_service.py # 认证服务
│   │   ├── chat_service.py # 聊天服务
│   │   ├── knowledge_base_service.py # 知识库服务
│   │   ├── vector_service.py # 向量服务
│   │   ├── admin_service.py # 管理员服务
│   │   ├── api_key_service.py # API密钥服务
│   │   ├── intelligent_retrieval_service.py # 智能检索服务
│   │   ├── enhanced_retrieval_pipeline.py # 增强检索流水线
│   │   ├── intent_recognizer.py # 意图识别器
│   │   ├── strategy_scheduler.py # 策略调度器
│   │   ├── multi_query_expander.py # 多查询扩展器
│   │   ├── hybrid_retriever.py # 混合检索器
│   │   ├── reranker.py  # 重排序器
│   │   ├── metadata_filter.py # 元数据过滤器
│   │   └── smart_config.py # 智能配置服务
│   ├── schemas/         # 数据验证
│   │   ├── user.py      # 用户模式
│   │   ├── knowledge_base.py # 知识库模式
│   │   ├── chat.py      # 聊天模式
│   │   ├── admin.py     # 管理员模式
│   │   └── api_key.py   # API密钥模式
│   ├── utils/           # 工具函数
│   │   ├── security.py  # 安全工具
│   │   ├── file.py      # 文件处理
│   │   └── helpers.py   # 辅助函数
│   └── plugins/         # 插件系统
│       ├── __init__.py  # 插件管理器
│       └── base.py      # 插件基类
├── alembic/             # 数据库迁移
├── tests/               # 测试文件
├── logs/                # 日志文件
├── uploads/             # 上传文件
└── requirements.txt     # 依赖文件
```

## 🔧 开发规范

### 代码规范

#### 前端规范
- 使用 TypeScript，严格类型检查
- 组件使用函数式 + Hooks
- 状态管理使用 Zustand
- 样式使用 Tailwind CSS
- 文件命名：组件 PascalCase，工具 camelCase
- 必须写单元测试，覆盖率 > 80%

#### 后端规范
- 使用 FastAPI + SQLAlchemy
- 遵循 RESTful API 设计
- 使用 Pydantic 进行数据验证
- 异步处理，使用 async/await
- 完整的错误处理和日志记录
- 必须写单元测试，覆盖率 > 80%

### Git 规范

#### 分支管理
- `main`: 主分支，用于生产环境
- `develop`: 开发分支，用于集成测试
- `feature/*`: 功能分支，用于新功能开发
- `hotfix/*`: 热修复分支，用于紧急修复

#### 提交规范
```
<type>(<scope>): <subject>

<body>

<footer>
```

类型说明：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 数据库规范

#### 命名规范
- 表名：小写，下划线分隔
- 字段名：小写，下划线分隔
- 索引名：`idx_表名_字段名`
- 外键名：`fk_表名_字段名`

#### 迁移规范
- 每次数据库变更都要创建迁移文件
- 迁移文件要有明确的描述
- 生产环境谨慎执行迁移

## 🧪 测试指南

### 前端测试
```bash
# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行E2E测试
npm run test:e2e
```

### 后端测试
```bash
# 运行单元测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app

# 运行特定测试文件
pytest tests/test_auth.py
```

### 集成测试
```bash
# 运行API集成测试
pytest tests/integration/

# 运行数据库集成测试
pytest tests/integration/test_database.py
```

## 🔍 调试指南

### 前端调试
```bash
# 启动开发服务器
npm run dev

# 打开浏览器开发者工具
# 使用 React Developer Tools 插件
```

### 后端调试
```bash
# 启动调试模式
python -m uvicorn app.main:app --reload --log-level debug

# 使用 VS Code 调试
# 配置 launch.json 文件
```

### 数据库调试
```bash
# 连接数据库
psql -h localhost -U metabox -d metabox

# 查看表结构
\d table_name

# 查看数据
SELECT * FROM table_name LIMIT 10;
```

## 📦 部署指南

### 开发环境部署
```bash
# 使用一键部署脚本
./scripts/dev_setup.sh setup
./scripts/dev_setup.sh start
```

### 生产环境部署
```bash
# 构建Docker镜像
docker-compose -f docker-compose.prod.yml build

# 启动生产服务
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 安全指南

### 开发安全
- 所有用户输入都要验证
- 使用参数化查询防止SQL注入
- 实现适当的权限控制
- 敏感信息使用环境变量

### 生产安全
- 使用HTTPS
- 配置防火墙
- 定期更新依赖
- 监控系统日志

## 📚 学习资源

### 技术栈
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Tailwind CSS 官方文档](https://tailwindcss.com/)

### 最佳实践
- [RESTful API 设计指南](https://restfulapi.net/)
- [Python 代码规范](https://www.python.org/dev/peps/pep-0008/)
- [JavaScript 代码规范](https://github.com/airbnb/javascript)

## 🤝 贡献指南

### 贡献流程
1. Fork 项目仓库
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

### 代码审查
- 所有代码变更都需要通过审查
- 确保测试覆盖率不降低
- 遵循项目代码规范
- 更新相关文档

## 📞 技术支持

如果您在开发过程中遇到问题，可以通过以下方式获取帮助：

- 📧 邮箱：dev@metabox.ai
- 💬 开发者群：扫描二维码加入
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/metabox/issues)
- 📖 文档：[项目文档](https://docs.metabox.ai)

---

**开发指南版本**: v1.0.0  
**最后更新**: 2024年12月 