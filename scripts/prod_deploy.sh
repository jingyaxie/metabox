#!/bin/bash

# MetaBox 生产环境 Docker 部署脚本
# 适用于生产环境部署，支持域名和SSL配置

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="metabox"
DOMAIN=""
SERVER_IP=""
SSL_EMAIL=""
ENVIRONMENT="production"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    echo "MetaBox 生产环境部署脚本"
    echo ""
    echo "用法: $0 [选项] [命令]"
    echo ""
    echo "选项:"
    echo "  -d, --domain DOMAIN      设置域名 (必需)"
    echo "  -i, --ip IP              设置服务器IP (必需)"
    echo "  -e, --email EMAIL        设置SSL证书邮箱 (必需)"
    echo "  -h, --help               显示帮助信息"
    echo ""
    echo "命令:"
    echo "  deploy      - 完整部署（推荐首次使用）"
    echo "  build       - 构建镜像"
    echo "  start       - 启动服务"
    echo "  stop        - 停止服务"
    echo "  restart     - 重启服务"
    echo "  status      - 检查服务状态"
    echo "  logs        - 查看服务日志"
    echo "  backup      - 备份数据"
    echo "  restore     - 恢复数据"
    echo "  update      - 更新部署"
    echo "  clean       - 清理环境"
    echo ""
    echo "示例:"
    echo "  $0 -d metabox.example.com -i 192.168.1.100 -e admin@example.com deploy"
    echo "  $0 -d metabox.example.com -i 192.168.1.100 -e admin@example.com start"
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -i|--ip)
                SERVER_IP="$2"
                shift 2
                ;;
            -e|--email)
                SSL_EMAIL="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                COMMAND="$1"
                shift
                ;;
        esac
    done
}

# 检查必需参数
check_required_params() {
    if [ -z "$DOMAIN" ]; then
        log_error "域名未设置，请使用 -d 参数指定域名"
        exit 1
    fi
    
    if [ -z "$SERVER_IP" ]; then
        log_error "服务器IP未设置，请使用 -i 参数指定IP地址"
        exit 1
    fi
    
    if [ -z "$SSL_EMAIL" ]; then
        log_error "SSL邮箱未设置，请使用 -e 参数指定邮箱"
        exit 1
    fi
}

# 检查系统环境
check_environment() {
    log_info "检查生产环境..."
    
    # 检查必需命令
    local required_commands=("docker" "docker-compose" "git" "curl" "openssl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 未安装，请先安装 $cmd"
            exit 1
        fi
    done
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请先启动 Docker"
        exit 1
    fi
    
    # 检查端口是否被占用
    local ports=(80 443 8000 3000 5432 6379 6333)
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            log_warning "端口 $port 已被占用"
        fi
    done
    
    log_success "环境检查完成"
}

# 创建生产环境配置
create_prod_config() {
    log_info "创建生产环境配置..."
    
    # 创建生产环境目录
    mkdir -p production/{config,data,logs,ssl}
    
    # 创建生产环境 docker-compose 文件
    cat > production/docker-compose.prod.yml << EOF
version: '3.8'

services:
  # SQLite 数据库（本地文件）
  postgres:
    image: postgres:14-alpine
    container_name: ${PROJECT_NAME}_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: metabox
      POSTGRES_USER: metabox
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./config/postgres:/etc/postgresql
    ports:
      - "5432:5432"
    networks:
      - metabox_network

  # 本地缓存（内存）
  redis:
    image: redis:7-alpine
    container_name: ${PROJECT_NAME}_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    networks:
      - metabox_network

  # Chroma 向量数据库（本地文件）
  qdrant:
    image: qdrant/qdrant:latest
    container_name: ${PROJECT_NAME}_qdrant
    restart: unless-stopped
    volumes:
      - ./data/qdrant:/qdrant/storage
    ports:
      - "6333:6333"
    networks:
      - metabox_network

  # 后端服务
  backend:
    build:
      context: ../backend
      dockerfile: ../docker/backend/Dockerfile
    container_name: ${PROJECT_NAME}_backend
    restart: unless-stopped
    environment:
      - DATABASE_URL=postgresql://metabox:\${POSTGRES_PASSWORD}@postgres:5432/metabox
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - SECRET_KEY=\${SECRET_KEY}
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./data/uploads:/app/uploads
      - ./logs/backend:/app/logs
    depends_on:
      - postgres
      - redis
      - qdrant
    networks:
      - metabox_network

  # 前端服务
  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/frontend/Dockerfile
    container_name: ${PROJECT_NAME}_frontend
    restart: unless-stopped
    environment:
      - REACT_APP_API_URL=https://${DOMAIN}/api
      - REACT_APP_ENVIRONMENT=production
    volumes:
      - ./logs/frontend:/app/logs
    depends_on:
      - backend
    networks:
      - metabox_network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: ${PROJECT_NAME}_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./config/nginx/conf.d:/etc/nginx/conf.d
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend
    networks:
      - metabox_network

  # Certbot SSL 证书
  certbot:
    image: certbot/certbot
    container_name: ${PROJECT_NAME}_certbot
    volumes:
      - ./ssl:/etc/letsencrypt
      - ./config/nginx/conf.d:/etc/nginx/conf.d
    command: certonly --webroot --webroot-path=/var/www/html --email ${SSL_EMAIL} --agree-tos --no-eff-email -d ${DOMAIN}
    depends_on:
      - nginx
    networks:
      - metabox_network

networks:
  metabox_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
EOF

    # 创建 Nginx 配置
    mkdir -p production/config/nginx/conf.d
    cat > production/config/nginx/conf.d/default.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    # 重定向到 HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};
    
    # SSL 配置
    ssl_certificate /etc/nginx/ssl/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/live/${DOMAIN}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 前端静态文件
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 后端 API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 支持 WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 文件上传
    location /uploads/ {
        proxy_pass http://backend:8000/uploads/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 大文件上传支持
        client_max_body_size 100M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # 健康检查
    location /health {
        proxy_pass http://backend:8000/health;
        access_log off;
    }
}
EOF

    # 创建环境变量文件
    cat > production/.env << EOF
# 数据库配置
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# 应用配置
SECRET_KEY=$(openssl rand -base64 64)
OPENAI_API_KEY=your-openai-api-key-here

# 域名配置
DOMAIN=${DOMAIN}
SERVER_IP=${SERVER_IP}

# 环境配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
EOF

    log_success "生产环境配置创建完成"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    cd production
    
    # 构建后端镜像
    log_info "构建后端镜像..."
    docker build -t ${PROJECT_NAME}/backend:latest -f ../docker/backend/Dockerfile ../backend
    
    # 构建前端镜像
    log_info "构建前端镜像..."
    docker build -t ${PROJECT_NAME}/frontend:latest -f ../docker/frontend/Dockerfile ../frontend
    
    cd ..
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动生产服务..."
    
    cd production
    
    # 启动基础服务
    docker-compose -f docker-compose.prod.yml up -d postgres redis qdrant
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 30
    
    # 初始化数据库
    log_info "初始化数据库..."
    docker-compose -f docker-compose.prod.yml exec -T postgres psql -U metabox -d metabox -c "SELECT 1;" || {
        log_info "创建数据库用户和数据库..."
        docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres -c "CREATE USER metabox WITH PASSWORD '\${POSTGRES_PASSWORD}';"
        docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres -c "CREATE DATABASE metabox OWNER metabox;"
    }
    
    # 启动应用服务
    docker-compose -f docker-compose.prod.yml up -d backend frontend
    
    # 启动 Nginx
    docker-compose -f docker-compose.prod.yml up -d nginx
    
    cd ..
    
    log_success "服务启动完成"
}

# 配置 SSL 证书
setup_ssl() {
    log_info "配置 SSL 证书..."
    
    cd production
    
    # 创建临时 Nginx 配置用于证书验证
    cat > config/nginx/conf.d/temp.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    # 重启 Nginx
    docker-compose -f docker-compose.prod.yml restart nginx
    
    # 申请 SSL 证书
    log_info "申请 Let's Encrypt SSL 证书..."
    docker-compose -f docker-compose.prod.yml run --rm certbot
    
    # 恢复正式 Nginx 配置
    rm config/nginx/conf.d/temp.conf
    docker-compose -f docker-compose.prod.yml restart nginx
    
    cd ..
    
    log_success "SSL 证书配置完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    cd production
    
    # 检查容器状态
    docker-compose -f docker-compose.prod.yml ps
    
    # 检查服务健康状态
    if curl -s https://${DOMAIN}/health > /dev/null; then
        log_success "后端服务运行正常"
    else
        log_warning "后端服务可能未正常启动"
    fi
    
    if curl -s https://${DOMAIN} > /dev/null; then
        log_success "前端服务运行正常"
    else
        log_warning "前端服务可能未正常启动"
    fi
    
    # 检查 SSL 证书
    if openssl s_client -connect ${DOMAIN}:443 -servername ${DOMAIN} < /dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
        log_success "SSL 证书配置正常"
    else
        log_warning "SSL 证书可能有问题"
    fi
    
    cd ..
}

# 查看服务日志
show_logs() {
    log_info "查看服务日志..."
    
    cd production
    
    if [ -n "$1" ]; then
        docker-compose -f docker-compose.prod.yml logs -f $1
    else
        docker-compose -f docker-compose.prod.yml logs -f
    fi
    
    cd ..
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    cd production
    
    # 创建备份目录
    mkdir -p ../backups/$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="../backups/$(date +%Y%m%d_%H%M%S)"
    
    # 备份 PostgreSQL 数据
    log_info "备份 PostgreSQL 数据..."
    docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U metabox metabox > ${BACKUP_DIR}/database.sql
    
    # 备份 Redis 数据
    log_info "备份 Redis 数据..."
    docker-compose -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE
    cp data/redis/dump.rdb ${BACKUP_DIR}/redis.rdb
    
    # 备份 Qdrant 数据
    log_info "备份 Qdrant 数据..."
    tar -czf ${BACKUP_DIR}/qdrant.tar.gz data/qdrant/
    
    # 备份上传文件
    log_info "备份上传文件..."
    tar -czf ${BACKUP_DIR}/uploads.tar.gz data/uploads/
    
    # 备份 SSL 证书
    log_info "备份 SSL 证书..."
    tar -czf ${BACKUP_DIR}/ssl.tar.gz ssl/
    
    cd ..
    
    log_success "数据备份完成: ${BACKUP_DIR}"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    log_info "恢复数据..."
    
    cd production
    
    BACKUP_DIR="../backups/$1"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi
    
    # 停止服务
    docker-compose -f docker-compose.prod.yml down
    
    # 恢复 PostgreSQL 数据
    log_info "恢复 PostgreSQL 数据..."
    docker-compose -f docker-compose.prod.yml up -d postgres
    sleep 10
    docker-compose -f docker-compose.prod.yml exec -T postgres psql -U metabox -d metabox < ${BACKUP_DIR}/database.sql
    
    # 恢复其他数据
    log_info "恢复其他数据..."
    tar -xzf ${BACKUP_DIR}/qdrant.tar.gz -C ./
    tar -xzf ${BACKUP_DIR}/uploads.tar.gz -C ./
    tar -xzf ${BACKUP_DIR}/ssl.tar.gz -C ./
    
    # 重启服务
    docker-compose -f docker-compose.prod.yml up -d
    
    cd ..
    
    log_success "数据恢复完成"
}

# 更新部署
update_deployment() {
    log_info "更新部署..."
    
    # 备份当前数据
    backup_data
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建镜像
    build_images
    
    # 重启服务
    cd production
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d
    cd ..
    
    log_success "部署更新完成"
}

# 停止服务
stop_services() {
    log_info "停止生产服务..."
    
    cd production
    docker-compose -f docker-compose.prod.yml down
    cd ..
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启生产服务..."
    
    cd production
    docker-compose -f docker-compose.prod.yml restart
    cd ..
    
    log_success "服务已重启"
}

# 清理环境
cleanup() {
    log_info "清理生产环境..."
    
    cd production
    
    # 停止并删除容器
    docker-compose -f docker-compose.prod.yml down -v
    
    # 删除镜像
    docker rmi ${PROJECT_NAME}/backend:latest ${PROJECT_NAME}/frontend:latest 2>/dev/null || true
    
    # 清理日志
    rm -rf logs/*
    
    cd ..
    
    log_success "环境清理完成"
}

# 完整部署
full_deploy() {
    log_info "开始完整部署..."
    
    check_required_params
    check_environment
    create_prod_config
    build_images
    start_services
    setup_ssl
    check_services
    
    log_success "部署完成！"
    log_info "访问地址:"
    log_info "  前端: https://${DOMAIN}"
    log_info "  后端: https://${DOMAIN}/api"
    log_info "  健康检查: https://${DOMAIN}/health"
}

# 主函数
main() {
    case "${COMMAND:-help}" in
        "deploy")
            full_deploy
            ;;
        "build")
            check_required_params
            build_images
            ;;
        "start")
            check_required_params
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            check_required_params
            check_services
            ;;
        "logs")
            show_logs $2
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data $2
            ;;
        "update")
            update_deployment
            ;;
        "clean")
            cleanup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# 解析参数并执行
parse_args "$@"
main 