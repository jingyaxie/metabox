# MetaBox 部署指南

## 🚀 快速部署

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 内存
- 至少 10GB 磁盘空间

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/MetaBox.git
cd MetaBox

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的 API Key

# 3. 启动服务
./scripts/deploy.sh

# 4. 访问系统
# 前端: http://localhost:3000
# 后端: http://localhost:8000
```

## ⚙️ 环境配置

### 必需的环境变量

```bash
# .env 文件示例
# 数据库配置
DATABASE_URL=postgresql://kb_user:kb_password@postgres:5432/metabox
QDRANT_URL=http://qdrant:6333

# AI 模型 API Key
OPENAI_API_KEY=your_openai_api_key
QWEN_API_KEY=your_qwen_api_key

# JWT 密钥
JWT_SECRET_KEY=your_jwt_secret_key

# 文件上传配置
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=./uploads
```

### 可选配置

```bash
# Redis 缓存
REDIS_URL=redis://redis:6379

# 日志级别
LOG_LEVEL=INFO

# 跨域配置
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 服务说明

| 服务名 | 端口 | 说明 |
|--------|------|------|
| frontend | 3000 | React 前端应用 |
| backend | 8000 | FastAPI 后端服务 |
| postgres | 5432 | PostgreSQL 数据库 |
| qdrant | 6333 | Qdrant 向量数据库 |
| redis | 6379 | Redis 缓存服务 |

## 🔧 生产环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 项目部署

```bash
# 克隆项目
git clone https://github.com/your-repo/MetaBox.git
cd MetaBox

# 配置生产环境
cp .env.example .env.prod
# 编辑 .env.prod 文件

# 生产环境部署
./scripts/deploy.sh prod
```

### 3. Nginx 配置

```nginx
# /etc/nginx/sites-available/metabox
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 文件上传
    location /uploads {
        proxy_pass http://localhost:8000;
        client_max_body_size 100M;
    }
}
```

### 4. SSL 证书配置

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 监控和维护

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8000/health

# 检查数据库连接
docker-compose exec postgres pg_isready -U kb_user

# 检查向量数据库
curl http://localhost:6333/collections
```

### 日志管理

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend

# 日志轮转配置
sudo nano /etc/logrotate.d/metabox
```

### 数据备份

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U kb_user metabox > backup_$(date +%Y%m%d).sql

# 备份向量数据
docker cp metabox-qdrant-1:/qdrant/storage ./backup_qdrant_$(date +%Y%m%d)

# 自动备份脚本
./scripts/backup.sh
```

## 🔒 安全配置

### 防火墙设置

```bash
# 只开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 环境变量安全

```bash
# 使用强密码
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 定期轮换密钥
# 建议每月更换一次 JWT_SECRET_KEY
```

### 文件权限

```bash
# 设置正确的文件权限
sudo chown -R www-data:www-data /path/to/metabox
sudo chmod -R 755 /path/to/metabox
sudo chmod 600 /path/to/metabox/.env
```

## 🚨 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查端口占用
   sudo netstat -tulpn | grep :3000
   
   # 重启服务
   docker-compose restart
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker-compose exec postgres pg_isready -U kb_user
   
   # 重新初始化数据库
   docker-compose exec backend alembic upgrade head
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   
   # 增加 swap 空间
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### 性能优化

1. **数据库优化**
   ```sql
   -- 创建索引
   CREATE INDEX idx_text_chunks_kb_id ON text_chunks(kb_id);
   CREATE INDEX idx_image_vectors_kb_id ON image_vectors(kb_id);
   ```

2. **缓存配置**
   ```bash
   # 启用 Redis 缓存
   # 在 .env 中配置 REDIS_URL
   ```

3. **资源限制**
   ```yaml
   # docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 2G
             cpus: '1.0'
   ```

## 📞 技术支持

- 📧 邮箱：support@metabox.com
- 💬 讨论：[GitHub Discussions](https://github.com/your-repo/MetaBox/discussions)
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/MetaBox/issues) 