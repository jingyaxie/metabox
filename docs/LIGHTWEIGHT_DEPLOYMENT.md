# MetaBox 轻量级部署指南

## 概述

MetaBox 轻量级版本使用更轻量的技术栈，大幅降低硬件要求，同时保留核心功能包括图片向量化，适合资源受限的环境部署。

## 硬件要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM（支持图片处理）
- **存储**: 15GB 可用空间
- **网络**: 稳定的互联网连接（用于模型API调用）

### 推荐配置
- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 30GB 可用空间
- **网络**: 稳定的互联网连接

### 图片处理配置
- **GPU**: 可选，支持CUDA加速（推荐）
- **内存**: 额外2GB用于图片向量化
- **存储**: 额外10GB用于图片存储

## 技术栈对比

| 组件 | 原版本 | 轻量级版本 | 资源节省 |
|------|--------|------------|----------|
| 数据库 | PostgreSQL | SQLite | 90%+ |
| 向量数据库 | Qdrant | Chroma | 70%+ |
| 缓存 | Redis | 内存缓存 | 100% |
| 存储 | 云存储 | 本地文件 | 100% |
| 图片向量化 | 重型模型 | CLIP轻量模型 | 60%+ |
| 重排序 | 启用 | 关闭 | 80%+ |
| 混合搜索 | 启用 | 关闭 | 60%+ |

## 功能特性

### 保留的核心功能
- ✅ 知识库管理
- ✅ 文档上传和处理
- ✅ 聊天对话
- ✅ **图片向量化**（使用CLIP模型）
- ✅ 图片相似度搜索
- ✅ 流式响应
- ✅ 用户管理

### 关闭的优化功能
- ❌ 重排序（节省80%+资源）
- ❌ 混合搜索（节省60%+资源）
- ❌ 高级搜索
- ❌ 多模态对话（保留图片向量化）

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
# 安装轻量级依赖（包含图片处理）
pip install -r requirements_lightweight.txt

# 如果不需要图片处理，可以跳过以下包：
# pip install clip torch torchvision opencv-python-headless
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
MAX_FILE_SIZE=10485760  # 10MB，支持图片

# 模型配置
MODEL_TYPE=api
DEFAULT_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your_openai_api_key

# 图片处理配置
ENABLE_MULTIMODAL=true
ENABLE_IMAGE_VECTORIZATION=true
IMAGE_VECTOR_MODEL=clip
IMAGE_MAX_SIZE=1024
IMAGE_QUALITY=85

# 资源限制
MAX_CONCURRENT_REQUESTS=5
MAX_DOCUMENT_SIZE=5242880  # 5MB
MAX_MEMORY_USAGE=512  # 512MB

# 功能开关
ENABLE_RERANK=false
ENABLE_HYBRID_SEARCH=false
ENABLE_MULTIMODAL=true
ENABLE_IMAGE_VECTORIZATION=true
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

## 图片向量化功能

### 支持的图片格式
- JPEG/JPG
- PNG
- GIF
- BMP
- WebP

### 图片处理特性
- **自动尺寸调整**：大图片自动缩放到1024px
- **格式转换**：自动转换为RGB格式
- **向量化**：使用CLIP模型生成1536维向量
- **相似度搜索**：支持图片相似度检索
- **元数据提取**：自动提取图片信息

### 使用示例

```python
# 图片向量化
from app.services.lightweight_image_service import lightweight_image_service

# 向量化单张图片
image_path = "path/to/image.jpg"
with open(image_path, "rb") as f:
    image_data = f.read()

vector = await lightweight_image_service.vectorize_image(image_data)

# 批量向量化
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
vectors = await lightweight_image_service.vectorize_images_batch(image_paths)

# 图片相似度搜索
similar_images = await lightweight_image_service.search_similar_images(
    query_image=image_data,
    image_vectors=stored_vectors,
    top_k=5
)
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
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB，支持图片

# 图片处理配置
ENABLE_MULTIMODAL = True  # 启用多模态
ENABLE_IMAGE_VECTORIZATION = True  # 启用图片向量化
IMAGE_VECTOR_MODEL = "clip"  # 使用CLIP模型
IMAGE_MAX_SIZE = 1024  # 图片最大尺寸
IMAGE_QUALITY = 85  # 图片质量

# 资源限制
MAX_CONCURRENT_REQUESTS = 5  # 降低并发数
MAX_DOCUMENT_SIZE = 5 * 1024 * 1024  # 5MB文档限制
MAX_CHUNK_SIZE = 500  # 减小分块大小
MAX_CHUNKS_PER_DOC = 50  # 增加分块数量支持图片

# 内存优化
MAX_MEMORY_USAGE = 512  # 512MB内存限制
CLEANUP_INTERVAL = 300  # 5分钟清理间隔

# 功能开关
ENABLE_RERANK = False  # 关闭重排序
ENABLE_HYBRID_SEARCH = False  # 关闭混合搜索
ENABLE_MULTIMODAL = True  # 启用多模态
ENABLE_IMAGE_VECTORIZATION = True  # 启用图片向量化
```

## 性能优化建议

### 1. 系统级优化

```bash
# 增加文件描述符限制
ulimit -n 65536

# 调整内存管理
echo 'vm.swappiness=10' >> /etc/sysctl.conf
sysctl -p

# 如果有GPU，设置CUDA环境
export CUDA_VISIBLE_DEVICES=0
```

### 2. 应用级优化

```python
# 启用内存优化
ENABLE_MEMORY_OPTIMIZATION = True

# 定期清理缓存
CLEANUP_INTERVAL = 300

# 限制并发请求
MAX_CONCURRENT_REQUESTS = 5

# 图片处理优化
IMAGE_MAX_SIZE = 1024  # 限制图片尺寸
IMAGE_QUALITY = 85  # 压缩图片质量
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

# 监控GPU使用（如果有）
nvidia-smi

# 监控进程
ps aux | grep metabox
```

### 2. 日志监控

```bash
# 查看应用日志
tail -f logs/app.log

# 查看图片处理日志
grep "image" logs/app.log

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

# 获取图片服务状态
GET /api/v1/system/image/status
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

### 2. 图片处理失败

**症状**: 图片上传后无法向量化

**解决方案**:
```bash
# 检查CLIP模型是否正确加载
python -c "import clip; print('CLIP available')"

# 检查CUDA是否可用
python -c "import torch; print(torch.cuda.is_available())"

# 检查图片格式支持
python -c "from PIL import Image; print('Pillow available')"
```

### 3. 磁盘空间不足

**症状**: 文件上传失败或数据库错误

**解决方案**:
```bash
# 检查磁盘使用
df -h

# 清理临时文件
rm -rf /tmp/*

# 清理日志文件
find logs/ -name "*.log" -mtime +7 -delete

# 清理图片缓存
rm -rf uploads/temp/*
```

### 4. 数据库锁定

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

# 备份图片数据
cp -r uploads/images uploads/images.backup
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

### Q: 轻量级版本是否支持图片向量化？

A: **是的**！轻量级版本保留了图片向量化功能，使用CLIP模型进行图片向量化，支持图片相似度搜索。

### Q: 图片处理对硬件要求高吗？

A: 轻量级版本使用CLIP模型，相比重型模型大幅降低了硬件要求。CPU模式下需要4GB内存，GPU模式下需要6GB内存。

### Q: 如何从原版本迁移到轻量级版本？

A: 需要重新初始化数据库和向量数据库，因为使用了不同的技术栈。建议先备份数据，然后按照安装步骤重新部署。

### Q: 轻量级版本是否支持集群部署？

A: 轻量级版本主要针对单机部署优化，如需集群部署建议使用原版本。

### Q: 如何调整图片处理参数？

A: 可以通过修改 `.env` 文件中的配置参数来调整，如 `IMAGE_MAX_SIZE`、`IMAGE_QUALITY` 等。

### Q: 支持哪些图片格式？

A: 支持JPEG、PNG、GIF、BMP、WebP等常见格式，会自动转换为RGB格式进行处理。

## 技术支持

如遇到问题，请：

1. 查看日志文件 `logs/app.log`
2. 检查系统资源使用情况
3. 参考故障排除章节
4. 提交 Issue 到项目仓库

---

**注意**: 轻量级版本在保持核心功能的同时大幅降低了硬件要求，特别适合需要图片向量化功能的资源受限环境。 