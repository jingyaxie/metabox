@echo off
REM MetaBox 本地开发环境一键部署脚本 (Windows版本)
REM 适用于 Windows 开发环境

setlocal enabledelayedexpansion

REM 设置编码为UTF-8
chcp 65001 >nul

REM 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 日志函数
:log_info
echo %BLUE%[INFO]%NC% %~1
goto :eof

:log_success
echo %GREEN%[SUCCESS]%NC% %~1
goto :eof

:log_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:log_error
echo %RED%[ERROR]%NC% %~1
goto :eof

REM 检查命令是否存在
:check_command
where %1 >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "%1 未安装，请先安装 %1"
    exit /b 1
)
goto :eof

REM 检查系统环境
:check_environment
call :log_info "检查系统环境..."

REM 检查必需命令
call :check_command python
call :check_command pip
call :check_command node
call :check_command npm
call :check_command docker
call :check_command git

call :log_success "环境检查完成"
goto :eof

REM 创建虚拟环境
:setup_python_env
call :log_info "设置 Python 虚拟环境..."

cd backend

if not exist "venv" (
    call :log_info "创建 Python 虚拟环境..."
    python -m venv venv
)

call :log_info "激活虚拟环境并安装依赖..."
call venv\Scripts\activate.bat

REM 升级 pip
python -m pip install --upgrade pip

REM 安装依赖
if exist "requirements.txt" (
    pip install -r requirements.txt
)

if exist "requirements-dev.txt" (
    pip install -r requirements-dev.txt
)

deactivate
cd ..

call :log_success "Python 环境设置完成"
goto :eof

REM 安装前端依赖
:setup_frontend
call :log_info "设置前端环境..."

cd frontend

REM 安装依赖
call :log_info "安装前端依赖..."
npm install

REM 检查是否有构建脚本
findstr /C:"\"build\"" package.json >nul 2>&1
if %errorlevel% equ 0 (
    call :log_info "构建前端项目..."
    npm run build
)

cd ..

call :log_success "前端环境设置完成"
goto :eof

REM 设置环境变量
:setup_env
call :log_info "设置环境变量..."

if not exist ".env" (
    call :log_info "创建 .env 文件..."
    copy env.example .env
    
    REM 生成随机密钥
    for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set SECRET_KEY=%%i
    powershell -Command "(Get-Content .env) -replace 'your-secret-key-here', '%SECRET_KEY%' | Set-Content .env"
    
    call :log_info "请编辑 .env 文件配置数据库连接等信息"
) else (
    call :log_info ".env 文件已存在"
)

call :log_success "环境变量设置完成"
goto :eof

REM 启动数据库服务
:start_database
call :log_info "启动数据库服务..."

REM 检查 Docker 是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker 未运行，请先启动 Docker"
    exit /b 1
)

REM 启动 PostgreSQL 和 Redis
docker-compose up -d postgres redis qdrant

REM 等待数据库启动
call :log_info "等待数据库启动..."
timeout /t 10 /nobreak >nul

call :log_success "数据库服务启动完成"
goto :eof

REM 初始化数据库
:init_database
call :log_info "初始化数据库..."

cd backend
call venv\Scripts\activate.bat

REM 运行数据库迁移
call :log_info "运行数据库迁移..."
python -m alembic upgrade head

REM 初始化基础数据
call :log_info "初始化基础数据..."
python -c "from app.core.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine); print('数据库表创建完成')"

deactivate
cd ..

call :log_success "数据库初始化完成"
goto :eof

REM 启动开发服务
:start_dev_services
call :log_info "启动开发服务..."

REM 启动后端服务
call :log_info "启动后端服务..."
cd backend
call venv\Scripts\activate.bat
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ..\logs\backend.log 2>&1
deactivate
cd ..

REM 等待后端启动
timeout /t 5 /nobreak >nul

REM 启动前端服务
call :log_info "启动前端服务..."
cd frontend
start /B npm run dev > ..\logs\frontend.log 2>&1
cd ..

call :log_success "开发服务启动完成"
goto :eof

REM 检查服务状态
:check_services
call :log_info "检查服务状态..."

REM 检查后端服务
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "后端服务运行正常"
) else (
    call :log_warning "后端服务可能未正常启动"
)

REM 检查前端服务
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "前端服务运行正常"
) else (
    call :log_warning "前端服务可能未正常启动"
)

REM 检查数据库
docker-compose ps postgres | findstr "Up" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "PostgreSQL 数据库运行正常"
) else (
    call :log_warning "PostgreSQL 数据库可能未正常启动"
)

docker-compose ps redis | findstr "Up" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Redis 缓存运行正常"
) else (
    call :log_warning "Redis 缓存可能未正常启动"
)

docker-compose ps qdrant | findstr "Up" >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Qdrant 向量数据库运行正常"
) else (
    call :log_warning "Qdrant 向量数据库可能未正常启动"
)
goto :eof

REM 停止服务
:stop_services
call :log_info "停止开发服务..."

REM 停止前端服务
taskkill /f /im node.exe >nul 2>&1

REM 停止后端服务
taskkill /f /im python.exe >nul 2>&1

REM 停止数据库服务
docker-compose down

call :log_success "所有服务已停止"
goto :eof

REM 清理环境
:cleanup
call :log_info "清理开发环境..."

REM 停止服务
call :stop_services

REM 清理日志
if exist "logs" (
    del /q logs\* >nul 2>&1
)

REM 清理 Docker 容器和镜像
docker-compose down -v
docker system prune -f

call :log_success "环境清理完成"
goto :eof

REM 显示帮助信息
:show_help
echo MetaBox 本地开发环境管理脚本
echo.
echo 用法: %0 [命令]
echo.
echo 命令:
echo   setup      - 完整环境设置（推荐首次使用）
echo   start      - 启动所有服务
echo   stop       - 停止所有服务
echo   restart    - 重启所有服务
echo   status     - 检查服务状态
echo   clean      - 清理环境
echo   help       - 显示帮助信息
echo.
echo 示例:
echo   %0 setup   # 首次设置环境
echo   %0 start   # 启动服务
echo   %0 status  # 检查状态
goto :eof

REM 主函数
:main
REM 创建日志目录
if not exist "logs" mkdir logs

if "%1"=="setup" (
    call :log_info "开始完整环境设置..."
    call :check_environment
    call :setup_python_env
    call :setup_frontend
    call :setup_env
    call :start_database
    call :init_database
    call :start_dev_services
    call :check_services
    call :log_success "环境设置完成！"
    call :log_info "访问地址:"
    call :log_info "  前端: http://localhost:3000"
    call :log_info "  后端: http://localhost:8000"
    call :log_info "  API文档: http://localhost:8000/docs"
) else if "%1"=="start" (
    call :start_database
    call :start_dev_services
    call :check_services
) else if "%1"=="stop" (
    call :stop_services
) else if "%1"=="restart" (
    call :stop_services
    timeout /t 2 /nobreak >nul
    call :start_database
    call :start_dev_services
    call :check_services
) else if "%1"=="status" (
    call :check_services
) else if "%1"=="clean" (
    call :cleanup
) else (
    call :show_help
)

goto :eof

REM 执行主函数
call :main %* 