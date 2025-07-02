#!/bin/bash

# MetaBox 本地开发环境一键部署脚本 (非Docker版本)
# 适用于 macOS/Linux 开发环境，使用轻量级配置

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
    check_command "git"
    
    log_success "环境检查完成"
}

# 安装系统依赖 (macOS)
install_system_deps_macos() {
    log_info "安装系统依赖 (macOS)..."
    
    # 检查 Homebrew
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew 未安装，请先安装 Homebrew: https://brew.sh/"
        exit 1
    fi
    
    # SQLite 通常已预装，无需额外安装
    log_info "SQLite 已预装，无需额外安装"
    
    # 使用内存缓存，无需额外安装
    log_info "使用内存缓存，无需额外安装"
    
    # Chroma 通过 Python 包安装，无需额外检查
    log_info "Chroma 向量数据库将通过 Python 包安装"
    
    log_success "系统依赖安装完成"
}

# 安装系统依赖 (Linux)
install_system_deps_linux() {
    log_info "安装系统依赖 (Linux)..."
    
    # SQLite 通常已预装
    log_info "SQLite 已预装，无需额外安装"
    
    # 使用内存缓存，无需额外安装
    log_info "使用内存缓存，无需额外安装"
    
    # Chroma 通过 Python 包安装，无需额外检查
    log_info "Chroma 向量数据库将通过 Python 包安装"
    
    log_success "系统依赖安装完成"
}

# 安装系统依赖
install_system_deps() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_system_deps_macos
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        install_system_deps_linux
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    # 创建数据目录
    mkdir -p data
    mkdir -p chroma_db
    mkdir -p uploads
    mkdir -p logs
    
    log_info "使用 SQLite 数据库，无需额外配置"
    log_success "数据库配置完成"
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
        log_info "安装依赖..."
        pip install -r requirements.txt
    fi
    
    if [ -f "requirements-dev.txt" ]; then
        log_info "安装开发依赖..."
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
        sed -i.bak "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
        
        log_info "请编辑 .env 文件配置 API Key 等信息"
    else
        log_info ".env 文件已存在"
    fi
    
    log_success "环境变量设置完成"
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
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    
    # 停止后端服务
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            log_info "后端服务已停止"
        fi
        rm -f logs/backend.pid
    fi
    
    # 停止前端服务
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            log_info "前端服务已停止"
        fi
        rm -f logs/frontend.pid
    fi
    
    log_success "服务已停止"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查后端服务
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            log_success "后端服务运行中 (PID: $BACKEND_PID)"
        else
            log_warning "后端服务未运行"
        fi
    else
        log_warning "后端服务未启动"
    fi
    
    # 检查前端服务
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            log_success "前端服务运行中 (PID: $FRONTEND_PID)"
        else
            log_warning "前端服务未运行"
        fi
    else
        log_warning "前端服务未启动"
    fi
    
    # 检查端口
    if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
        log_success "后端端口 8000 已监听"
    else
        log_warning "后端端口 8000 未监听"
    fi
    
    if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
        log_success "前端端口 3000 已监听"
    else
        log_warning "前端端口 3000 未监听"
    fi
}

# 显示日志
show_logs() {
    local service=${1:-"all"}
    
    case $service in
        "backend")
            if [ -f "logs/backend.log" ]; then
                tail -f logs/backend.log
            else
                log_error "后端日志文件不存在"
            fi
            ;;
        "frontend")
            if [ -f "logs/frontend.log" ]; then
                tail -f logs/frontend.log
            else
                log_error "前端日志文件不存在"
            fi
            ;;
        "all")
            if [ -f "logs/backend.log" ] && [ -f "logs/frontend.log" ]; then
                tail -f logs/backend.log logs/frontend.log
            else
                log_error "日志文件不存在"
            fi
            ;;
        *)
            log_error "未知服务: $service"
            ;;
    esac
}

# 清理环境
cleanup() {
    log_info "清理环境..."
    
    # 停止服务
    stop_services
    
    # 清理日志
    rm -rf logs/*
    
    # 清理缓存
    rm -rf frontend/node_modules/.cache
    rm -rf backend/__pycache__
    rm -rf backend/app/__pycache__
    
    log_success "环境清理完成"
}

# 显示帮助信息
show_help() {
    echo "MetaBox 本地开发环境设置脚本 (非Docker版本)"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  setup     - 完整环境设置（推荐首次使用）"
    echo "  start     - 启动开发服务"
    echo "  stop      - 停止开发服务"
    echo "  restart   - 重启开发服务"
    echo "  status    - 检查服务状态"
    echo "  logs      - 查看服务日志 [backend|frontend|all]"
    echo "  clean     - 清理环境"
    echo "  help      - 显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 setup"
    echo "  $0 start"
    echo "  $0 logs backend"
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost:3000"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p logs
    
    case "${1:-help}" in
        "setup")
            log_info "开始完整环境设置..."
            check_environment
            install_system_deps
            setup_python_env
            setup_frontend
            setup_env
            setup_database
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
            start_dev_services
            check_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_dev_services
            check_services
            ;;
        "status")
            check_services
            ;;
        "logs")
            show_logs $2
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