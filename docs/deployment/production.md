# MetaBox 生产环境部署指南

## 📋 部署概述

本文档详细说明 MetaBox 智能知识库系统的生产环境部署流程，包括环境准备、配置管理、服务部署和运维监控。

## 🎯 系统要求

### 硬件要求
- **CPU**: 4核心以上
- **内存**: 8GB以上
- **存储**: 100GB以上可用空间
- **网络**: 稳定的网络连接

### 软件要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / macOS 12+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.30+

## 🚀 快速部署

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-repo/MetaBox.git
cd MetaBox

# 配置环境变量
cp env.example .env
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# 基础配置
DOMAIN=your-domain.com
SECRET_KEY=your-secret-key-here
DEBUG=false
LOG_LEVEL=INFO

# 数据库配置
DATABASE_URL=postgresql://metabox:password@postgres:5432/metabox
REDIS_URL=redis://redis:6379

# 向量数据库配置
QDRANT_URL=http://qdrant:6333

# API 密钥
OPENAI_API_KEY=your-openai-api-key
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=your-azure-endpoint

# 文件存储配置
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=104857600

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# 监控配置
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### 3. 一键部署

```bash
# 给脚本添加执行权限
chmod +x scripts/deploy.sh

# 完整部署
./scripts/deploy.sh deploy
```

## 🔧 详细部署流程

### 阶段一：环境检查

```bash
# 检查 Docker 环境
docker --version
docker-compose --version

# 检查系统资源
df -h
free -h
nproc
```

### 阶段二：构建镜像

```bash
# 构建所有镜像
./scripts/deploy.sh build

# 或手动构建
docker-compose build --no-cache
```

### 阶段三：启动服务

```bash
# 启动数据库服务
docker-compose up -d postgres redis qdrant

# 等待数据库启动
sleep 15

# 运行数据库迁移
docker-compose run --rm backend python -m alembic upgrade head

# 启动应用服务
docker-compose up -d backend frontend nginx
```

### 阶段四：验证部署

```bash
# 检查服务状态
./scripts/deploy.sh status

# 检查健康状态
curl -s https://your-domain.com/health

# 检查前端访问
curl -s https://your-domain.com
```

## 📊 服务架构

```
Internet
    ↓
Nginx (反向代理 + SSL)
    ↓
Frontend (React) ←→ Backend (FastAPI)
    ↓
PostgreSQL (主数据库)
    ↓
Redis (缓存)
    ↓
Qdrant (向量数据库)
```

## 🔒 安全配置

### SSL/TLS 配置

```nginx
# nginx/conf.d/default.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 反向代理配置
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 防火墙配置

```bash
# Ubuntu/Debian
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

## 📈 监控与日志

### 日志管理

```bash
# 查看所有服务日志
./scripts/deploy.sh logs

# 查看特定服务日志
./scripts/deploy.sh logs backend
./scripts/deploy.sh logs frontend
./scripts/deploy.sh logs nginx
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看系统资源
htop
iotop
```

### 健康检查

```bash
# 自动健康检查脚本
#!/bin/bash
while true; do
    if ! curl -s https://your-domain.com/health > /dev/null; then
        echo "$(date): 服务异常，尝试重启..."
        ./scripts/deploy.sh restart
    fi
    sleep 60
done
```

## 🔄 备份与恢复

### 数据备份

```bash
# 自动备份
./scripts/deploy.sh backup

# 手动备份数据库
docker-compose exec postgres pg_dump -U metabox metabox > backup_$(date +%Y%m%d).sql

# 备份上传文件
tar -czf uploads_$(date +%Y%m%d).tar.gz uploads/
```

### 数据恢复

```bash
# 恢复数据
./scripts/deploy.sh restore backup_20231201_143000/

# 手动恢复数据库
docker-compose exec -T postgres psql -U metabox metabox < backup_20231201.sql
```

## 🚨 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查日志
docker-compose logs backend

# 检查端口占用
netstat -tlnp | grep :8000

# 重启服务
./scripts/deploy.sh restart
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose ps postgres

# 检查数据库日志
docker-compose logs postgres

# 重新初始化数据库
docker-compose run --rm backend python -m alembic upgrade head
```

#### 3. 内存不足
```bash
# 检查内存使用
free -h

# 清理 Docker 资源
docker system prune -f

# 增加 swap 空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 性能优化

#### 1. 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_documents_kb_id ON documents(knowledge_base_id);
CREATE INDEX idx_chunks_doc_id ON chunks(document_id);

-- 分析表
ANALYZE documents;
ANALYZE chunks;
```

#### 2. Redis 优化
```bash
# 配置 Redis 内存限制
echo "maxmemory 1gb" >> redis.conf
echo "maxmemory-policy allkeys-lru" >> redis.conf
```

#### 3. Nginx 优化
```nginx
# 启用 gzip 压缩
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 配置缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔄 更新部署

### 自动更新

```bash
# 更新代码并重新部署
./scripts/deploy.sh update
```

### 手动更新

```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose restart
```

## 📞 运维支持

### 监控告警

- **服务状态监控**: 每5分钟检查一次
- **资源使用监控**: CPU、内存、磁盘使用率
- **错误日志监控**: 实时监控错误日志
- **性能指标监控**: 响应时间、吞吐量

### 联系支持

- **技术文档**: [项目文档](docs/)
- **问题反馈**: [GitHub Issues](../../issues)
- **紧急联系**: support@metabox.com

---

*本文档将随着系统更新持续维护* 