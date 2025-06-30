#!/bin/bash

# MetaBox 部署脚本
# 使用方法: ./scripts/deploy.sh [dev|prod]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查 .env 文件
    if [ ! -f ".env" ]; then
        log_warn ".env 文件不存在，正在创建..."
        cp .env.example .env
        log_warn "请编辑 .env 文件配置必要的环境变量"
        exit 1
    fi
    
    log_info "环境检查通过"
}

# 备份数据
backup_data() {
    if [ "$1" = "prod" ]; then
        log_info "备份现有数据..."
        timestamp=$(date +%Y%m%d_%H%M%S)
        backup_dir="backup_${timestamp}"
        
        mkdir -p "$backup_dir"
        
        # 备份数据库
        docker-compose exec -T postgres pg_dump -U kb_user metabox > "$backup_dir/database.sql"
        
        # 备份向量数据
        docker cp metabox-qdrant-1:/qdrant/storage "$backup_dir/qdrant_data"
        
        log_info "数据备份完成: $backup_dir"
    fi
}

# 停止服务
stop_services() {
    log_info "停止现有服务..."
    docker-compose down
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    docker-compose build --no-cache
}

# 启动服务
start_services() {
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    check_services
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    services=("frontend" "backend" "postgres" "qdrant")
    
    for service in "${services[@]}"; do
        if docker-compose ps | grep -q "$service.*Up"; then
            log_info "$service 服务运行正常"
        else
            log_error "$service 服务启动失败"
            docker-compose logs "$service"
            exit 1
        fi
    done
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 等待数据库启动
    sleep 10
    
    # 运行数据库迁移
    docker-compose exec backend alembic upgrade head
    
    log_info "数据库初始化完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查前端
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_info "前端服务正常"
    else
        log_error "前端服务异常"
        return 1
    fi
    
    # 检查后端
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_info "后端服务正常"
    else
        log_error "后端服务异常"
        return 1
    fi
    
    # 检查数据库
    if docker-compose exec postgres pg_isready -U kb_user > /dev/null 2>&1; then
        log_info "数据库服务正常"
    else
        log_error "数据库服务异常"
        return 1
    fi
    
    log_info "所有服务健康检查通过"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署完成！"
    echo ""
    echo "访问地址:"
    echo "  前端界面: http://localhost:3000"
    echo "  后端 API: http://localhost:8000"
    echo "  API 文档: http://localhost:8000/docs"
    echo "  管理界面: http://localhost:8000/admin"
    echo ""
    echo "查看日志:"
    echo "  docker-compose logs -f"
    echo ""
    echo "停止服务:"
    echo "  docker-compose down"
}

# 主函数
main() {
    local environment=${1:-dev}
    
    log_info "开始部署 MetaBox ($environment 环境)"
    
    # 切换到项目根目录
    cd "$(dirname "$0")/.."
    
    check_environment
    backup_data "$environment"
    stop_services
    build_images
    start_services
    init_database
    health_check
    show_deployment_info
    
    log_info "部署完成！"
}

# 脚本入口
main "$@" 