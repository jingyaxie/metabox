# MetaBox 轻量级部署指南

## 概述

MetaBox 轻量级版本使用更轻量的技术栈，大幅降低硬件要求，适合资源受限的环境部署。

## 硬件要求

### 最低配置
- **CPU**: 2核心
- **内存**: 2GB RAM
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接（用于模型API调用）

### 推荐配置
- **CPU**: 4核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **网络**: 稳定的互联网连接

## 技术栈对比

| 组件 | 原版本 | 轻量级版本 | 资源节省 |
|------|--------|------------|----------|
| 数据库 | PostgreSQL | SQLite | 90%+ |
| 向量数据库 | Qdrant | Chroma | 70%+ |
| 缓存 | Redis | 内存缓存 | 100% |
| 存储 | 云存储 | 本地文件 | 100% |
| 重排序 | 启用 | 关闭 | 80%+ |
| 混合搜索 | 启用 | 关闭 | 60%+ |

## 安装步骤

### 1. 环境准备

```bash
# 创建项目目录
mkdir metabox-lightweight
cd metabox-lightweight

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
# 安装轻量级依赖
pip install -r requirements_lightweight.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=sqlite:///./metabox.db

# 向量数据库配置
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIR=./chroma_db

# 存储配置
STORAGE_TYPE=local
UPLOAD_DIR=./uploads

# 模型配置
MODEL_TYPE=api
DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your_openai_api_key

# 资源限制
MAX_CONCURRENT_REQUESTS=5
MAX_DOCUMENT_SIZE=2097152
MAX_MEMORY_USAGE=256

# 功能开关
ENABLE_RERANK=false
ENABLE_HYBRID_SEARCH=false
ENABLE_MULTIMODAL=false
```

### 4. 初始化数据库

```bash
# 创建数据库迁移
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端服务（在另一个终端）
cd frontend
npm install
npm start
```

## 配置说明

### 轻量级配置参数

```python
# 数据库配置
DATABASE_URL = "sqlite:///./metabox.db"  # 使用SQLite
DB_POOL_SIZE = 5  # 降低连接池大小

# 向量数据库配置
VECTOR_DB_TYPE = "chroma"  # 使用Chroma
CHROMA_PERSIST_DIR = "./chroma_db"  # 本地持久化

# 存储配置
STORAGE_TYPE = "local"  # 本地文件存储
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB文件限制

# 资源限制
MAX_CONCURRENT_REQUESTS = 5  # 降低并发数
MAX_DOCUMENT_SIZE = 2 * 1024 * 1024  # 2MB文档限制
MAX_CHUNK_SIZE = 500  # 减小分块大小
MAX_CHUNKS_PER_DOC = 30  # 限制分块数量

# 内存优化
MAX_MEMORY_USAGE = 256  # 256MB内存限制
CLEANUP_INTERVAL = 300  # 5分钟清理间隔

# 功能开关
ENABLE_RERANK = False  # 关闭重排序
ENABLE_HYBRID_SEARCH = False  # 关闭混合搜索
ENABLE_MULTIMODAL = False  # 关闭多模态
```

## 性能优化建议

### 1. 系统级优化

```bash
# 增加文件描述符限制
ulimit -n 65536

# 调整内存管理
echo 'vm.swappiness=10' >> /etc/sysctl.conf
sysctl -p
```

### 2. 应用级优化

```python
# 启用内存优化
ENABLE_MEMORY_OPTIMIZATION = True

# 定期清理缓存
CLEANUP_INTERVAL = 300

# 限制并发请求
MAX_CONCURRENT_REQUESTS = 5
```

### 3. 数据库优化

```sql
-- SQLite优化
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;
```

## 监控和维护

### 1. 系统监控

```bash
# 监控内存使用
watch -n 1 'free -h'

# 监控磁盘使用
df -h

# 监控进程
ps aux | grep metabox
```

### 2. 日志监控

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

### 3. 性能监控

```python
# 获取服务状态
GET /api/v1/system/status

# 获取缓存统计
GET /api/v1/system/cache/stats

# 获取内存使用
GET /api/v1/system/memory
```

## 故障排除

### 1. 内存不足

**症状**: 服务启动失败或运行缓慢

**解决方案**:
```bash
# 检查内存使用
free -h

# 清理系统缓存
sync && echo 3 > /proc/sys/vm/drop_caches

# 重启服务
systemctl restart metabox
```

### 2. 磁盘空间不足

**症状**: 文件上传失败或数据库错误

**解决方案**:
```bash
# 检查磁盘使用
df -h

# 清理临时文件
rm -rf /tmp/*

# 清理日志文件
find logs/ -name "*.log" -mtime +7 -delete
```

### 3. 数据库锁定

**症状**: 数据库操作失败

**解决方案**:
```bash
# 检查SQLite锁
ls -la metabox.db*

# 删除锁文件
rm -f metabox.db-wal metabox.db-shm

# 重启服务
systemctl restart metabox
```

## 升级指南

### 1. 备份数据

```bash
# 备份数据库
cp metabox.db metabox.db.backup

# 备份向量数据库
cp -r chroma_db chroma_db.backup

# 备份上传文件
cp -r uploads uploads.backup
```

### 2. 升级步骤

```bash
# 停止服务
systemctl stop metabox

# 更新代码
git pull origin main

# 更新依赖
pip install -r requirements_lightweight.txt

# 执行数据库迁移
alembic upgrade head

# 启动服务
systemctl start metabox
```

## 常见问题

### Q: 轻量级版本功能是否完整？

A: 轻量级版本保留了核心功能，包括知识库管理、文档上传、聊天对话等。关闭了一些重型功能如重排序、混合搜索、多模态处理等。

### Q: 如何从原版本迁移到轻量级版本？

A: 需要重新初始化数据库和向量数据库，因为使用了不同的技术栈。建议先备份数据，然后按照安装步骤重新部署。

### Q: 轻量级版本是否支持集群部署？

A: 轻量级版本主要针对单机部署优化，如需集群部署建议使用原版本。

### Q: 如何调整资源限制？

A: 可以通过修改 `.env` 文件中的配置参数来调整资源限制，如 `MAX_CONCURRENT_REQUESTS`、`MAX_MEMORY_USAGE` 等。

## 技术支持

如遇到问题，请：

1. 查看日志文件 `logs/app.log`
2. 检查系统资源使用情况
3. 参考故障排除章节
4. 提交 Issue 到项目仓库

---

**注意**: 轻量级版本适合资源受限的环境，如需完整功能请使用原版本。 