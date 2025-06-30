#!/bin/bash

# MetaBox 生产环境部署脚本
# 支持 Docker Compose 一键部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查必需参数
check_required_params() {
    if [ -z "$DOMAIN" ]; then
        log_error "请设置 DOMAIN 环境变量"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        log_error "请设置 SECRET_KEY 环境变量"
        exit 1
    fi
}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
    # 检查 Docker
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! docker-compose version &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        log_error ".env 文件不存在，请先配置环境变量"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动数据库服务
    docker-compose up -d postgres redis qdrant
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 15
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    docker-compose run --rm backend python -m alembic upgrade head
    
    # 启动应用服务
    docker-compose up -d backend frontend nginx
    
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启服务..."
    docker-compose restart
    log_success "服务重启完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查容器状态
    docker-compose ps
    
    # 检查健康状态
    if curl -s https://${DOMAIN}/health > /dev/null; then
        log_success "后端服务健康检查通过"
    else
        log_warning "后端服务健康检查失败"
    fi
    
    if curl -s https://${DOMAIN} > /dev/null; then
        log_success "前端服务访问正常"
    else
        log_warning "前端服务访问失败"
    fi
}

# 显示日志
show_logs() {
    local service=${1:-"all"}
    
    if [ "$service" = "all" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $service
    fi
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    # 创建备份目录
    mkdir -p backups/$(date +%Y%m%d_%H%M%S)
    
    # 备份数据库
    docker-compose exec postgres pg_dump -U metabox metabox > backups/$(date +%Y%m%d_%H%M%S)/database.sql
    
    # 备份上传文件
    tar -czf backups/$(date +%Y%m%d_%H%M%S)/uploads.tar.gz uploads/
    
    log_success "数据备份完成"
}

# 恢复数据
restore_data() {
    local backup_dir=$1
    
    if [ -z "$backup_dir" ]; then
        log_error "请指定备份目录"
        exit 1
    fi
    
    log_info "恢复数据..."
    
    # 恢复数据库
    docker-compose exec -T postgres psql -U metabox metabox < $backup_dir/database.sql
    
    # 恢复上传文件
    tar -xzf $backup_dir/uploads.tar.gz -C ./
    
    log_success "数据恢复完成"
}

# 更新部署
update_deployment() {
    log_info "更新部署..."
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建镜像
    build_images
    
    # 重启服务
    restart_services
    
    log_success "部署更新完成"
}

# 清理环境
cleanup() {
    log_info "清理环境..."
    
    # 停止服务
    stop_services
    
    # 清理镜像
    docker system prune -f
    
    # 清理日志
    rm -rf logs/*
    
    log_success "环境清理完成"
}

# 完整部署
full_deploy() {
    log_info "开始完整部署..."
    
    check_required_params
    check_environment
    build_images
    start_services
    
    # 等待服务启动
    sleep 10
    
    check_services
    
    log_success "部署完成！"
    log_info "访问地址:"
    log_info "  前端: https://${DOMAIN}"
    log_info "  后端API: https://${DOMAIN}/api"
    log_info "  API文档: https://${DOMAIN}/docs"
    log_info "  健康检查: https://${DOMAIN}/health"
}

# 显示帮助
show_help() {
    echo "MetaBox 生产环境部署脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy    - 完整部署"
    echo "  build     - 构建镜像"
    echo "  start     - 启动服务"
    echo "  stop      - 停止服务"
    echo "  restart   - 重启服务"
    echo "  status    - 检查状态"
    echo "  logs      - 查看日志 [服务名]"
    echo "  backup    - 备份数据"
    echo "  restore   - 恢复数据 <备份目录>"
    echo "  update    - 更新部署"
    echo "  clean     - 清理环境"
    echo "  help      - 显示帮助"
    echo ""
    echo "环境变量:"
    echo "  DOMAIN    - 域名"
    echo "  SECRET_KEY - 密钥"
    echo ""
    echo "示例:"
    echo "  $0 deploy"
    echo "  $0 status"
    echo "  $0 logs backend"
}

# 主函数
main() {
    case "${1:-help}" in
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

# 执行主函数
main "$@" 