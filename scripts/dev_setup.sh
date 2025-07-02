#!/bin/bash

# MetaBox 本地开发环境一键部署脚本
# 适用于 macOS/Linux 开发环境

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查系统环境
check_environment() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "检测到 macOS 系统"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "检测到 Linux 系统"
    else
        log_warning "未知操作系统: $OSTYPE"
    fi
    
    # 检查必需命令
    check_command "python3"
    check_command "pip3"
    check_command "node"
    check_command "npm"
    check_command "docker"
    check_command "docker-compose"
    check_command "git"
    
    log_success "环境检查完成"
}

# 创建虚拟环境
setup_python_env() {
    log_info "设置 Python 虚拟环境..."
    
    cd backend
    
    if [ ! -d "venv" ]; then
        log_info "创建 Python 虚拟环境..."
        python3 -m venv venv
    fi
    
    log_info "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi
    
    deactivate
    cd ..
    
    log_success "Python 环境设置完成"
}

# 安装前端依赖
setup_frontend() {
    log_info "设置前端环境..."
    
    cd frontend
    
    # 安装依赖
    log_info "安装前端依赖..."
    npm install
    
    # 检查是否有构建脚本
    if [ -f "package.json" ] && grep -q "\"build\"" package.json; then
        log_info "构建前端项目..."
        npm run build
    fi
    
    cd ..
    
    log_success "前端环境设置完成"
}

# 设置环境变量
setup_env() {
    log_info "设置环境变量..."
    
    if [ ! -f ".env" ]; then
        log_info "创建 .env 文件..."
        cp env.example .env
        
        # 生成随机密钥
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        sed -i.bak "s/your-secret-key-here/$SECRET_KEY/" .env
        
        log_info "请编辑 .env 文件配置数据库连接等信息"
    else
        log_info ".env 文件已存在"
    fi
    
    log_success "环境变量设置完成"
}

# 启动数据库服务
start_database() {
    log_info "启动数据库服务..."
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        log_error "Docker 未运行，请先启动 Docker"
        exit 1
    fi
    
    # 启动本地服务（SQLite + Chroma）
    docker-compose up -d
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 10
    
    log_success "数据库服务启动完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    cd backend
    source venv/bin/activate
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    python -m alembic upgrade head
    
    # 初始化基础数据
    log_info "初始化基础数据..."
    python -c "
from app.core.database import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('数据库表创建完成')
"
    
    deactivate
    cd ..
    
    log_success "数据库初始化完成"
}

# 启动开发服务
start_dev_services() {
    log_info "启动开发服务..."
    
    # 启动后端服务
    log_info "启动后端服务..."
    cd backend
    source venv/bin/activate
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    deactivate
    cd ..
    
    # 等待后端启动
    sleep 5
    
    # 启动前端服务
    log_info "启动前端服务..."
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    cd ..
    
    log_success "开发服务启动完成"
    log_info "后端服务 PID: $BACKEND_PID"
    log_info "前端服务 PID: $FRONTEND_PID"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查后端服务
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "后端服务运行正常"
    else
        log_warning "后端服务可能未正常启动"
    fi
    
    # 检查前端服务
    if curl -s http://localhost:3000 > /dev/null; then
        log_success "前端服务运行正常"
    else
        log_warning "前端服务可能未正常启动"
    fi
    
    # 检查数据库
    if docker-compose ps postgres | grep -q "Up"; then
        log_success "PostgreSQL 数据库运行正常"
    else
        log_warning "PostgreSQL 数据库可能未正常启动"
    fi
    
    if docker-compose ps redis | grep -q "Up"; then
        log_success "Redis 缓存运行正常"
    else
        log_warning "Redis 缓存可能未正常启动"
    fi
    
    if docker-compose ps qdrant | grep -q "Up"; then
        log_success "Qdrant 向量数据库运行正常"
    else
        log_warning "Qdrant 向量数据库可能未正常启动"
    fi
}

# 停止服务
stop_services() {
    log_info "停止开发服务..."
    
    # 停止前端服务
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_info "前端服务已停止"
        fi
        rm -f logs/frontend.pid
    fi
    
    # 停止后端服务
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_info "后端服务已停止"
        fi
        rm -f logs/backend.pid
    fi
    
    # 停止数据库服务
    docker-compose down
    
    log_success "所有服务已停止"
}

# 清理环境
cleanup() {
    log_info "清理开发环境..."
    
    # 停止服务
    stop_services
    
    # 清理日志
    rm -rf logs/*
    
    # 清理 Docker 容器和镜像
    docker-compose down -v
    docker system prune -f
    
    log_success "环境清理完成"
}

# 显示帮助信息
show_help() {
    echo "MetaBox 本地开发环境管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  setup      - 完整环境设置（推荐首次使用）"
    echo "  start      - 启动所有服务"
    echo "  stop       - 停止所有服务"
    echo "  restart    - 重启所有服务"
    echo "  status     - 检查服务状态"
    echo "  clean      - 清理环境"
    echo "  help       - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 setup   # 首次设置环境"
    echo "  $0 start   # 启动服务"
    echo "  $0 status  # 检查状态"
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p logs
    
    case "${1:-help}" in
        "setup")
            log_info "开始完整环境设置..."
            check_environment
            setup_python_env
            setup_frontend
            setup_env
            start_database
            init_database
            start_dev_services
            check_services
            log_success "环境设置完成！"
            log_info "访问地址:"
            log_info "  前端: http://localhost:3000"
            log_info "  后端: http://localhost:8000"
            log_info "  API文档: http://localhost:8000/docs"
            ;;
        "start")
            start_database
            start_dev_services
            check_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_database
            start_dev_services
            check_services
            ;;
        "status")
            check_services
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