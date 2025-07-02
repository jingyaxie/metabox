# MetaBox 部署指南

本文档将指导您完成 MetaBox 智能知识库系统的部署，包括开发环境、测试环境和生产环境的配置。

## 🚀 快速部署

### 方式一：一键部署脚本（推荐）

#### Docker 版本
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

#### 非 Docker 版本
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

## 🐳 Docker 部署

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 20GB 可用磁盘空间

### 部署步骤

#### 1. 克隆项目
```bash
git clone https://github.com/your-repo/metabox.git
cd metabox
```

#### 2. 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量
vim .env
```

主要配置项：
```bash
# 数据库配置
POSTGRES_DB=metabox
POSTGRES_USER=metabox
POSTGRES_PASSWORD=your_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 应用配置
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# AI模型配置
OPENAI_API_KEY=your_openai_key
QIANWEN_API_KEY=your_qianwen_key
```

#### 3. 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 初始化数据库
```bash
# 进入后端容器
docker-compose exec backend bash

# 执行数据库迁移
python -m alembic upgrade head

# 创建超级管理员
python scripts/create_super_admin.py
```

#### 5. 访问系统
- 前端界面：http://localhost:3004
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 🖥️ 本地部署

### 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 14+
- Redis 6+
- Git

### 部署步骤

#### 1. 安装系统依赖

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm postgresql redis-server
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip nodejs npm postgresql redis
```

**macOS:**
```bash
brew install python3 node postgresql redis
```

#### 2. 配置数据库
```bash
# 启动PostgreSQL服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE metabox;
CREATE USER metabox WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE metabox TO metabox;
\q
```

#### 3. 配置Redis
```bash
# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis

# 配置Redis密码（可选）
sudo vim /etc/redis/redis.conf
# 添加：requirepass your_redis_password
```

#### 4. 部署后端
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate.bat  # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置环境变量
cp ../env.example ../.env
vim ../.env

# 初始化数据库
python -m alembic upgrade head

# 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 5. 部署前端
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 或构建生产版本
npm run build
npm run preview
```

## ☁️ 生产环境部署

### 服务器要求
- **CPU**: 8核心以上
- **内存**: 16GB以上
- **存储**: 500GB以上SSD
- **网络**: 100Mbps以上带宽
- **操作系统**: Ubuntu 20.04+ / CentOS 8+

### 部署架构
```
┌─────────────────┐
│   Nginx         │ 反向代理和负载均衡
└─────────┬───────┘
          ↓
┌─────────────────┐
│   React 前端    │ 静态文件服务
└─────────┬───────┘
          ↓
┌─────────────────┐
│   FastAPI 后端  │ 应用服务
└─────────┬───────┘
          ↓
┌─────────┬───────┬───────┐
│ Qdrant  │PostgreSQL│ Redis │ 数据存储
│ 向量库  │结构化数据│ 缓存  │
└─────────┴───────┴───────┘
```

### 部署步骤

#### 1. 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y curl wget git nginx postgresql redis-server

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. 配置防火墙
```bash
# 配置UFW防火墙
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

#### 3. 配置Nginx
```bash
# 创建Nginx配置
sudo vim /etc/nginx/sites-available/metabox

server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/metabox/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持
    location /chat/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/metabox /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. 配置SSL证书
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

#### 5. 部署应用
```bash
# 克隆项目
git clone https://github.com/your-repo/metabox.git
cd metabox

# 配置环境变量
cp env.example .env
vim .env

# 使用Docker Compose部署
docker-compose -f docker-compose.prod.yml up -d

# 初始化数据库
docker-compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
```

#### 6. 配置监控
```bash
# 安装Prometheus和Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# 配置日志收集
sudo vim /etc/logrotate.d/metabox
```

## 🔧 配置说明

### 环境变量配置

#### 基础配置
```bash
# 应用配置
DEBUG=False
SECRET_KEY=your_secret_key
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# 数据库配置
DATABASE_URL=postgresql://metabox:password@localhost:5432/metabox
REDIS_URL=redis://:password@localhost:6379/0

# 向量数据库配置
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=your_qdrant_key
```

#### AI模型配置
```bash
# OpenAI配置
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 通义千问配置
QIANWEN_API_KEY=your_qianwen_key
QIANWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1

# 文心一言配置
WENXIN_API_KEY=your_wenxin_key
WENXIN_SECRET_KEY=your_wenxin_secret
```

#### 文件存储配置
```bash
# 本地存储
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600  # 100MB

# 云存储（可选）
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=your_bucket_name
```

### 性能优化

#### 数据库优化
```sql
-- PostgreSQL优化
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

#### Redis优化
```bash
# Redis配置优化
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 应用优化
```python
# FastAPI优化配置
app = FastAPI(
    title="MetaBox API",
    description="智能知识库系统API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔒 安全配置

### 网络安全
```bash
# 配置防火墙规则
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 应用安全
```python
# 安全中间件配置
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["your-domain.com", "localhost", "127.0.0.1"]
)

# 速率限制
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### 数据安全
```bash
# 数据库加密
sudo -u postgres psql
ALTER USER metabox PASSWORD 'strong_password';
\q

# 备份策略
#!/bin/bash
# 数据库备份脚本
pg_dump -h localhost -U metabox metabox > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 📊 监控和日志

### 系统监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs

# 配置系统监控
sudo vim /etc/systemd/system/metabox-monitor.service
```

### 应用日志
```python
# 日志配置
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/metabox.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 性能监控
```python
# 性能监控中间件
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🔄 更新和维护

### 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 重启服务
docker-compose -f docker-compose.prod.yml up -d

# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
```

### 数据备份
```bash
#!/bin/bash
# 备份脚本
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/metabox"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -h localhost -U metabox metabox > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 系统维护
```bash
# 定期维护脚本
#!/bin/bash

# 清理日志文件
find /var/log -name "*.log" -mtime +30 -delete

# 清理临时文件
rm -rf /tmp/*

# 更新系统包
apt update && apt upgrade -y

# 重启服务
systemctl restart metabox
```

## 🆘 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql

# 检查数据库连接
psql -h localhost -U metabox -d metabox

# 查看数据库日志
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### 2. Redis连接失败
```bash
# 检查Redis服务状态
sudo systemctl status redis

# 测试Redis连接
redis-cli ping

# 查看Redis日志
sudo tail -f /var/log/redis/redis-server.log
```

#### 3. 应用启动失败
```bash
# 查看应用日志
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep :8000

# 检查环境变量
docker-compose exec backend env
```

#### 4. 前端访问失败
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 查看Nginx日志
sudo tail -f /var/log/nginx/error.log

# 检查防火墙设置
sudo ufw status
```

### 性能问题排查
```bash
# 查看系统资源使用
htop
iotop
nethogs

# 查看数据库性能
sudo -u postgres psql
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;
```

## 📞 技术支持

如果您在部署过程中遇到问题，可以通过以下方式获取帮助：

- 📧 邮箱：deploy@metabox.ai
- 💬 部署群：扫描二维码加入
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/metabox/issues)
- 📖 文档：[部署文档](https://docs.metabox.ai/deployment)

---

**部署指南版本**: v1.0.0  
**最后更新**: 2024年12月 