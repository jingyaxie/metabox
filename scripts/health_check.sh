#!/bin/bash

# MetaBox 项目健康检查脚本
# 作者: AI Assistant
# 功能: 检查前后端服务健康状态

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

log_info "开始 MetaBox 项目健康检查..."

# 1. 检查端口占用
log_info "检查端口占用情况..."

# 检查后端端口
if lsof -i :8000 > /dev/null 2>&1; then
    BACKEND_PID=$(lsof -ti:8000 | head -1)
    log_success "后端服务运行中 (PID: $BACKEND_PID)"
else
    log_error "后端服务未运行"
fi

# 检查前端端口
if lsof -i :3003 > /dev/null 2>&1; then
    FRONTEND_PID=$(lsof -ti:3003 | head -1)
    log_success "前端服务运行中 (PID: $FRONTEND_PID)"
else
    log_error "前端服务未运行"
fi

# 2. 检查后端API健康状态
log_info "检查后端API健康状态..."

# 健康检查接口
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
        log_success "健康检查接口正常"
    else
        log_warning "健康检查接口响应异常: $HEALTH_RESPONSE"
    fi
else
    log_error "健康检查接口无法访问"
fi

# 知识库接口
if curl -s http://localhost:8000/api/kb/ > /dev/null 2>&1; then
    log_success "知识库接口正常"
else
    log_error "知识库接口无法访问"
fi

# 插件接口
if curl -s http://localhost:8000/api/plugins/ > /dev/null 2>&1; then
    log_success "插件接口正常"
else
    log_error "插件接口无法访问"
fi

# 聊天接口
if curl -s http://localhost:8000/api/chat/sessions > /dev/null 2>&1; then
    log_success "聊天接口正常"
else
    log_error "聊天接口无法访问"
fi

# 3. 检查前端页面
log_info "检查前端页面..."

if curl -s http://localhost:3003 > /dev/null 2>&1; then
    FRONTEND_RESPONSE=$(curl -s http://localhost:3003 | head -20)
    if echo "$FRONTEND_RESPONSE" | grep -q "React\|Vite\|html"; then
        log_success "前端页面加载正常"
    else
        log_warning "前端页面响应异常"
    fi
else
    log_error "前端页面无法访问"
fi

# 4. 检查日志文件
log_info "检查日志文件..."

# 后端日志
if [ -f "$PROJECT_ROOT/backend/backend.log" ]; then
    BACKEND_LOG_SIZE=$(du -h "$PROJECT_ROOT/backend/backend.log" | cut -f1)
    log_info "后端日志文件存在 (大小: $BACKEND_LOG_SIZE)"
    
    # 检查最近的错误
    RECENT_ERRORS=$(tail -50 "$PROJECT_ROOT/backend/backend.log" | grep -i "error\|exception\|traceback" | wc -l)
    if [ $RECENT_ERRORS -gt 0 ]; then
        log_warning "后端日志中发现 $RECENT_ERRORS 个错误"
    else
        log_success "后端日志无错误"
    fi
else
    log_warning "后端日志文件不存在"
fi

# 前端日志
if [ -f "$PROJECT_ROOT/frontend/frontend.log" ]; then
    FRONTEND_LOG_SIZE=$(du -h "$PROJECT_ROOT/frontend/frontend.log" | cut -f1)
    log_info "前端日志文件存在 (大小: $FRONTEND_LOG_SIZE)"
    
    # 检查最近的错误
    RECENT_ERRORS=$(tail -50 "$PROJECT_ROOT/frontend/frontend.log" | grep -i "error\|exception\|failed" | wc -l)
    if [ $RECENT_ERRORS -gt 0 ]; then
        log_warning "前端日志中发现 $RECENT_ERRORS 个错误"
    else
        log_success "前端日志无错误"
    fi
else
    log_warning "前端日志文件不存在"
fi

# 5. 检查系统资源
log_info "检查系统资源..."

# CPU使用率
CPU_USAGE=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
log_info "CPU使用率: ${CPU_USAGE}%"

# 内存使用率
MEMORY_USAGE=$(top -l 1 | grep "PhysMem" | awk '{print $2}' | sed 's/[^0-9]//g')
log_info "内存使用: ${MEMORY_USAGE}MB"

# 磁盘使用率
DISK_USAGE=$(df -h "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//')
log_info "磁盘使用率: ${DISK_USAGE}%"

# 6. 生成健康报告
log_info "生成健康检查报告..."

cat > health_report.txt << EOF
MetaBox 项目健康检查报告
========================
检查时间: $(date)
项目路径: $PROJECT_ROOT

服务状态:
- 后端服务: $(if lsof -i :8000 > /dev/null 2>&1; then echo "运行中 (PID: $(lsof -ti:8000 | head -1))"; else echo "未运行"; fi)
- 前端服务: $(if lsof -i :3003 > /dev/null 2>&1; then echo "运行中 (PID: $(lsof -ti:3003 | head -1))"; else echo "未运行"; fi)

API 健康状态:
- 健康检查: $(if curl -s http://localhost:8000/health > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)
- 知识库接口: $(if curl -s http://localhost:8000/api/kb/ > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)
- 插件接口: $(if curl -s http://localhost:8000/api/plugins/ > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)
- 聊天接口: $(if curl -s http://localhost:8000/api/chat/sessions > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)

前端状态:
- 页面加载: $(if curl -s http://localhost:3003 > /dev/null 2>&1; then echo "正常"; else echo "异常"; fi)

系统资源:
- CPU使用率: ${CPU_USAGE}%
- 内存使用: ${MEMORY_USAGE}MB
- 磁盘使用率: ${DISK_USAGE}%

日志状态:
- 后端日志: $(if [ -f "$PROJECT_ROOT/backend/backend.log" ]; then echo "存在"; else echo "不存在"; fi)
- 前端日志: $(if [ -f "$PROJECT_ROOT/frontend/frontend.log" ]; then echo "存在"; else echo "不存在"; fi)

访问地址:
- 前端页面: http://localhost:3003
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

建议操作:
$(if ! lsof -i :8000 > /dev/null 2>&1; then echo "- 启动后端服务: cd $PROJECT_ROOT/backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"; fi)
$(if ! lsof -i :3003 > /dev/null 2>&1; then echo "- 启动前端服务: cd $PROJECT_ROOT/frontend && npm run dev -- --host 0.0.0.0 --port 3003"; fi)
EOF

log_success "健康检查报告已生成: health_report.txt"

# 7. 显示总结
echo ""
log_info "📊 健康检查总结:"

# 计算正常服务数量
HEALTHY_SERVICES=0
TOTAL_SERVICES=2

if lsof -i :8000 > /dev/null 2>&1; then
    HEALTHY_SERVICES=$((HEALTHY_SERVICES + 1))
fi

if lsof -i :3003 > /dev/null 2>&1; then
    HEALTHY_SERVICES=$((HEALTHY_SERVICES + 1))
fi

if [ $HEALTHY_SERVICES -eq $TOTAL_SERVICES ]; then
    log_success "🎉 所有服务运行正常！"
elif [ $HEALTHY_SERVICES -gt 0 ]; then
    log_warning "⚠️  部分服务运行正常 ($HEALTHY_SERVICES/$TOTAL_SERVICES)"
else
    log_error "❌ 所有服务都未运行"
fi

echo ""
echo "📖 查看详细报告:"
echo "  cat health_report.txt"
echo ""
echo "🚀 重新启动服务:"
echo "  ./scripts/test_and_fix.sh"
echo "" 