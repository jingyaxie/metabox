#!/bin/bash

# MetaBox 项目停止服务脚本
# 作者: AI Assistant
# 功能: 停止前后端服务

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

# 项目根目录
PROJECT_ROOT="/Users/xiejingya/ai/metabox"

log_info "停止 MetaBox 项目服务..."

# 1. 停止后端服务
log_info "停止后端服务..."

# 检查是否有保存的PID文件
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        log_success "后端服务已停止 (PID: $BACKEND_PID)"
    else
        log_warning "后端服务进程不存在 (PID: $BACKEND_PID)"
    fi
    rm -f backend.pid
else
    log_warning "未找到后端PID文件"
fi

# 强制清理端口8000
if lsof -i :8000 > /dev/null 2>&1; then
    log_warning "强制清理端口8000..."
    lsof -ti:8000 | xargs kill -9
    log_success "端口8000已清理"
fi

# 2. 停止前端服务
log_info "停止前端服务..."

# 检查是否有保存的PID文件
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        log_success "前端服务已停止 (PID: $FRONTEND_PID)"
    else
        log_warning "前端服务进程不存在 (PID: $FRONTEND_PID)"
    fi
    rm -f frontend.pid
else
    log_warning "未找到前端PID文件"
fi

# 强制清理端口3003
if lsof -i :3003 > /dev/null 2>&1; then
    log_warning "强制清理端口3003..."
    lsof -ti:3003 | xargs kill -9
    log_success "端口3003已清理"
fi

# 3. 清理日志文件
log_info "清理日志文件..."
cd "$PROJECT_ROOT/backend"
if [ -f "backend.log" ]; then
    rm -f backend.log
    log_success "后端日志已清理"
fi

cd "$PROJECT_ROOT/frontend"
if [ -f "frontend.log" ]; then
    rm -f frontend.log
    log_success "前端日志已清理"
fi

# 4. 验证服务已停止
log_info "验证服务状态..."

if ! lsof -i :8000 > /dev/null 2>&1; then
    log_success "端口8000已释放"
else
    log_error "端口8000仍被占用"
fi

if ! lsof -i :3003 > /dev/null 2>&1; then
    log_success "端口3003已释放"
else
    log_error "端口3003仍被占用"
fi

echo ""
log_success "🎉 MetaBox 项目服务已全部停止！"
echo ""
echo "📊 服务状态:"
echo "  后端服务: 已停止"
echo "  前端服务: 已停止"
echo ""
echo "🚀 重新启动服务:"
echo "  ./scripts/test_and_fix.sh"
echo "" 