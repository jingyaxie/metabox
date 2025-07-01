#!/bin/bash

# MetaBox 项目自动测试与修复脚本
# 作者: AI Assistant
# 功能: 自动检测前后端服务状态，发现问题并自动修复

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

# 项目根目录
PROJECT_ROOT="/Users/xiejingya/ai/metabox"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

log_info "开始 MetaBox 项目自动测试与修复..."

# 1. 检查项目目录结构
log_info "检查项目目录结构..."
if [ ! -d "$PROJECT_ROOT" ]; then
    log_error "项目根目录不存在: $PROJECT_ROOT"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    log_error "前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
    log_error "后端目录不存在: $BACKEND_DIR"
    exit 1
fi

log_success "项目目录结构检查通过"

# 2. 检查前端依赖
log_info "检查前端依赖..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    log_warning "前端依赖未安装，正在安装..."
    npm install
    if [ $? -eq 0 ]; then
        log_success "前端依赖安装完成"
    else
        log_error "前端依赖安装失败"
        exit 1
    fi
else
    log_success "前端依赖已存在"
fi

# 检查关键依赖
if ! npm list vite > /dev/null 2>&1; then
    log_warning "Vite 依赖缺失，正在安装..."
    npm install vite
fi

if ! npm list react > /dev/null 2>&1; then
    log_warning "React 依赖缺失，正在安装..."
    npm install react react-dom
fi

# 3. 检查后端虚拟环境
log_info "检查后端虚拟环境..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    log_warning "后端虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        log_success "虚拟环境创建完成"
    else
        log_error "虚拟环境创建失败"
        exit 1
    fi
fi

# 激活虚拟环境
log_info "激活后端虚拟环境..."
source venv/bin/activate

# 检查 Python 版本
PYTHON_VERSION=$(python --version 2>&1)
log_info "Python 版本: $PYTHON_VERSION"

# 检查后端依赖
if [ ! -f "venv/lib/python*/site-packages/uvicorn" ] && [ ! -f "venv/lib/python*/site-packages/uvicorn.py" ]; then
    log_warning "后端依赖未安装，正在安装..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        log_success "后端依赖安装完成"
    else
        log_error "后端依赖安装失败"
        exit 1
    fi
else
    log_success "后端依赖已存在"
fi

# 4. 检查端口占用
log_info "检查端口占用情况..."

# 检查前端端口 3003
if lsof -i :3003 > /dev/null 2>&1; then
    log_warning "端口 3003 被占用，正在清理..."
    lsof -ti:3003 | xargs kill -9
    sleep 2
fi

# 检查后端端口 8000
if lsof -i :8000 > /dev/null 2>&1; then
    log_warning "端口 8000 被占用，正在清理..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

log_success "端口清理完成"

# 5. 启动后端服务
log_info "启动后端服务..."
cd "$BACKEND_DIR"
source venv/bin/activate

# 后台启动后端服务
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
log_info "等待后端服务启动..."
sleep 5

# 检查后端是否启动成功
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    log_success "后端服务启动成功 (PID: $BACKEND_PID)"
else
    log_error "后端服务启动失败，检查日志..."
    cat backend.log
    exit 1
fi

# 6. 启动前端服务
log_info "启动前端服务..."
cd "$FRONTEND_DIR"

# 后台启动前端服务
nohup npm run dev -- --host 0.0.0.0 --port 3003 > frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
log_info "等待前端服务启动..."
sleep 10

# 检查前端是否启动成功
if curl -s http://localhost:3003 > /dev/null 2>&1; then
    log_success "前端服务启动成功 (PID: $FRONTEND_PID)"
else
    log_error "前端服务启动失败，检查日志..."
    cat frontend.log
    exit 1
fi

# 7. 测试 API 接口
log_info "测试 API 接口..."

# 测试健康检查接口
if curl -s http://localhost:8000/health | grep -q "ok"; then
    log_success "健康检查接口正常"
else
    log_warning "健康检查接口异常"
fi

# 测试知识库接口
if curl -s http://localhost:8000/api/kb/ > /dev/null 2>&1; then
    log_success "知识库接口正常"
else
    log_warning "知识库接口异常"
fi

# 测试插件接口
if curl -s http://localhost:8000/api/plugins/ > /dev/null 2>&1; then
    log_success "插件接口正常"
else
    log_warning "插件接口异常"
fi

# 8. 测试前端页面
log_info "测试前端页面..."

# 测试前端主页
if curl -s http://localhost:3003 | grep -q "React\|Vite" > /dev/null 2>&1; then
    log_success "前端页面加载正常"
else
    log_warning "前端页面加载异常"
fi

# 9. 生成测试报告
log_info "生成测试报告..."

cat > test_report.txt << EOF
MetaBox 项目测试报告
====================
测试时间: $(date)
项目路径: $PROJECT_ROOT

服务状态:
- 后端服务: http://localhost:8000 (PID: $BACKEND_PID)
- 前端服务: http://localhost:3003 (PID: $FRONTEND_PID)

依赖检查:
- 前端依赖: $(if [ -d "$FRONTEND_DIR/node_modules" ]; then echo "已安装"; else echo "未安装"; fi)
- 后端依赖: $(if [ -d "$BACKEND_DIR/venv" ]; then echo "已安装"; else echo "未安装"; fi)

端口状态:
- 端口 3003: $(if lsof -i :3003 > /dev/null 2>&1; then echo "已占用"; else echo "空闲"; fi)
- 端口 8000: $(if lsof -i :8000 > /dev/null 2>&1; then echo "已占用"; else echo "空闲"; fi)

API 测试:
- 健康检查: $(if curl -s http://localhost:8000/health > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)
- 知识库接口: $(if curl -s http://localhost:8000/api/kb/ > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)
- 插件接口: $(if curl -s http://localhost:8000/api/plugins/ > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)

前端测试:
- 页面加载: $(if curl -s http://localhost:3003 > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)

日志文件:
- 后端日志: $BACKEND_DIR/backend.log
- 前端日志: $FRONTEND_DIR/frontend.log

使用说明:
1. 访问前端: http://localhost:3003
2. 访问后端API: http://localhost:8000
3. 查看API文档: http://localhost:8000/docs

停止服务:
- 停止后端: kill $BACKEND_PID
- 停止前端: kill $FRONTEND_PID
EOF

log_success "测试报告已生成: test_report.txt"

# 10. 显示服务状态
echo ""
log_success "🎉 MetaBox 项目启动完成！"
echo ""
echo "📊 服务状态:"
echo "  后端服务: http://localhost:8000 (PID: $BACKEND_PID)"
echo "  前端服务: http://localhost:3003 (PID: $FRONTEND_PID)"
echo ""
echo "📖 使用说明:"
echo "  1. 访问前端页面: http://localhost:3003"
echo "  2. 查看API文档: http://localhost:8000/docs"
echo "  3. 查看测试报告: test_report.txt"
echo ""
echo "🛑 停止服务:"
echo "  ./scripts/stop_services.sh"
echo ""

# 保存进程ID到文件
echo "$BACKEND_PID" > backend.pid
echo "$FRONTEND_PID" > frontend.pid

log_success "进程ID已保存到 backend.pid 和 frontend.pid" 