#!/bin/bash

# MetaBox 部署脚本
# 使用方法: ./scripts/deploy.sh [start|stop|restart|logs|clean]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

# 检查 Docker 和 Docker Compose
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "依赖检查通过"
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p "$PROJECT_ROOT/uploads"
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/nginx/conf.d"
    
    log_success "目录创建完成"
}

# 设置环境变量
setup_environment() {
    log_info "设置环境变量..."
    
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning "未找到 .env 文件，创建默认配置..."
        cat > "$PROJECT_ROOT/.env" << EOF
# MetaBox 环境配置
APP_NAME=MetaBox
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=postgresql://kb_user:kb_password@postgres:5432/metabox
QDRANT_URL=http://qdrant:6333

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件上传配置
MAX_FILE_SIZE=104857600
UPLOAD_DIR=uploads
ALLOWED_EXTENSIONS=["pdf","doc","docx","txt","md","jpg","jpeg","png","gif"]

# Redis 配置
REDIS_URL=redis://redis:6379
CACHE_TTL=3600

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/metabox.log

# CORS 配置
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
CORS_ALLOW_CREDENTIALS=true
EOF
        log_success "默认 .env 文件创建完成"
    else
        log_info ".env 文件已存在"
    fi
}

# 启动服务
start_services() {
    log_info "启动 MetaBox 服务..."
    
    cd "$PROJECT_ROOT"
    
    # 拉取最新镜像
    log_info "拉取 Docker 镜像..."
    docker-compose pull
    
    # 构建镜像
    log_info "构建服务镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log_info "启动所有服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services
    
    log_success "MetaBox 启动完成！"
    log_info "访问地址: http://localhost"
    log_info "API 文档: http://localhost/docs"
    log_info "默认管理员账户: admin / admin123"
}

# 停止服务
stop_services() {
    log_info "停止 MetaBox 服务..."
    
    cd "$PROJECT_ROOT"
    docker-compose down
    
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启 MetaBox 服务..."
    
    stop_services
    sleep 5
    start_services
}

# 查看日志
show_logs() {
    log_info "显示服务日志..."
    
    cd "$PROJECT_ROOT"
    docker-compose logs -f
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    cd "$PROJECT_ROOT"
    
    # 检查容器状态
    if docker-compose ps | grep -q "Up"; then
        log_success "所有服务运行正常"
        
        # 检查健康状态
        if curl -f http://localhost/health &> /dev/null; then
            log_success "健康检查通过"
        else
            log_warning "健康检查失败，服务可能还在启动中"
        fi
    else
        log_error "部分服务启动失败"
        docker-compose ps
        exit 1
    fi
}

# 清理资源
clean_resources() {
    log_warning "清理所有资源（包括数据）..."
    
    read -p "确定要删除所有数据吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$PROJECT_ROOT"
        
        # 停止并删除容器
        docker-compose down -v
        
        # 删除镜像
        docker-compose down --rmi all
        
        # 删除卷
        docker volume prune -f
        
        # 删除网络
        docker network prune -f
        
        log_success "资源清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    cd "$PROJECT_ROOT"
    
    # 创建备份目录
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    log_info "备份 PostgreSQL 数据库..."
    docker-compose exec -T postgres pg_dump -U kb_user metabox > "$BACKUP_DIR/database.sql"
    
    # 备份上传文件
    log_info "备份上传文件..."
    if [ -d "uploads" ]; then
        cp -r uploads "$BACKUP_DIR/"
    fi
    
    # 备份配置文件
    log_info "备份配置文件..."
    cp .env "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "数据备份完成: $BACKUP_DIR"
}

# 恢复数据
restore_data() {
    log_info "恢复数据..."
    
    if [ -z "$1" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    BACKUP_DIR="$1"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # 恢复数据库
    if [ -f "$BACKUP_DIR/database.sql" ]; then
        log_info "恢复 PostgreSQL 数据库..."
        docker-compose exec -T postgres psql -U kb_user -d metabox < "$BACKUP_DIR/database.sql"
    fi
    
    # 恢复上传文件
    if [ -d "$BACKUP_DIR/uploads" ]; then
        log_info "恢复上传文件..."
        rm -rf uploads
        cp -r "$BACKUP_DIR/uploads" .
    fi
    
    log_success "数据恢复完成"
}

# 显示帮助信息
show_help() {
    echo "MetaBox 部署脚本"
    echo ""
    echo "使用方法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动所有服务"
    echo "  stop      停止所有服务"
    echo "  restart   重启所有服务"
    echo "  logs      显示服务日志"
    echo "  status    检查服务状态"
    echo "  clean     清理所有资源（包括数据）"
    echo "  backup    备份数据"
    echo "  restore   恢复数据"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start"
    echo "  $0 logs"
    echo "  $0 backup"
    echo "  $0 restore backup_20231201_120000"
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            check_dependencies
            create_directories
            setup_environment
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        status)
            check_services
            ;;
        clean)
            clean_resources
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 执行主函数
main "$@" 