# NCM to MP3 WebUI 编程任务说明文档

---

## 1. 📌 功能目标

### 核心目标
构建一个基于 Web 的可视化界面，将命令行工具 `ncmdump` 的功能封装为用户友好的图形化操作，实现 .ncm 格式音频文件到 MP3/FLAC 格式的在线转换。

### 用户价值
- **降低使用门槛**：无需掌握命令行知识，通过浏览器即可完成文件转换
- **远程访问**：支持通过网络远程上传和下载文件，不受本地环境限制
- **批量处理**：支持一次上传多个文件进行批量转换
- **即时反馈**：实时显示转换进度和状态

### 预期功能
| 功能 | 描述 |
|------|------|
| 文件上传 | 支持拖拽和点击选择 .ncm 文件 |
| 批量转换 | 后台异步执行 ncmdump 命令 |
| 状态查询 | 实时轮询转换任务状态 |
| 单文件下载 | 下载单个转换后的音频文件 |
| 批量下载 | 将多个文件打包为 ZIP 下载 |
| 容器化部署 | 支持 Docker 一键部署 |

---

## 2. 🔁 输入输出规范

### 2.1 文件上传接口

**接口**: `POST /api/upload`

| 项目 | 规范 |
|------|------|
| **输入类型** | `multipart/form-data` |
| **输入字段** | `files`: 多个 .ncm 文件 |
| **输入来源** | 用户浏览器（拖拽或文件选择器） |
| **输出类型** | `application/json` |
| **输出结构** | `{"task_id": "uuid", "message": "string"}` |
| **输出去向** | 前端 JavaScript 用于状态追踪 |

### 2.2 状态查询接口

**接口**: `GET /api/status/{task_id}`

| 项目 | 规范 |
|------|------|
| **输入类型** | URL 路径参数 |
| **输入字段** | `task_id`: UUID 字符串 |
| **输出类型** | `application/json` |
| **输出结构** | `{"task_id": "string", "status": "pending|processing|completed|failed", "message": "string", "files": ["string"]}` |

### 2.3 文件下载接口

**接口**: `GET /api/download/{task_id}/{filename}`

| 项目 | 规范 |
|------|------|
| **输入类型** | URL 路径参数 |
| **输入字段** | `task_id`: UUID, `filename`: 文件名 |
| **输出类型** | `application/octet-stream` |
| **输出去向** | 浏览器下载 |

### 2.4 批量下载接口

**接口**: `GET /api/download-all/{task_id}`

| 项目 | 规范 |
|------|------|
| **输入类型** | URL 路径参数 |
| **输出类型** | `application/zip` |
| **输出文件名** | `converted_files.zip` |

---

## 3. 🧱 数据结构设计

### 3.1 任务数据模型

```python
class ConversionTask:
    task_id: str      # UUID 唯一标识
    status: str       # pending | processing | completed | failed
    message: str      # 状态描述信息
    files: List[str]  # 转换成功的文件名列表
```

### 3.2 目录结构设计

```
项目根目录/
├── uploads/
│   └── {task_id}/           # 每个任务独立目录
│       ├── file1.ncm
│       └── file2.ncm
├── outputs/
│   └── {task_id}/           # 每个任务独立目录
│       ├── file1.mp3
│       └── file2.flac
│   └── {task_id}.zip        # 批量下载临时文件
```

### 3.3 内存数据结构

```python
# 任务状态存储（内存字典，生产环境建议使用 Redis）
tasks: dict[str, ConversionTask] = {}
```

---

## 4. 🧩 模块划分与系统结构

### 4.1 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Upload Zone │  │ Status Card │  │ Download Links  │  │
│  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
└─────────┼────────────────┼──────────────────┼───────────┘
          │                │                  │
          ▼                ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                 FastAPI Backend (API Layer)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ /upload  │  │ /status  │  │/download │  │ /health  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘ │
└───────┼─────────────┼─────────────┼─────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────┐
│                  Service Layer (Business Logic)          │
│  ┌───────────────────┐  ┌────────────────────────────┐  │
│  │ File Management   │  │ Conversion Task Executor   │  │
│  │ - Save uploads    │  │ - Async subprocess call    │  │
│  │ - Serve downloads │  │ - Status management        │  │
│  └───────────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
        │                           │
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  File System  │           │   ncmdump     │
│  uploads/     │           │   (CLI Tool)  │
│  outputs/     │           │               │
└───────────────┘           └───────────────┘
```

### 4.2 模块职责

| 模块 | 职责 | 文件位置 |
|------|------|----------|
| **前端界面** | 用户交互、文件选择、状态展示、下载触发 | `templates/index.html` |
| **API 路由层** | HTTP 请求处理、参数校验、响应格式化 | `app/main.py` |
| **文件管理** | 上传文件保存、输出文件读取、临时文件清理 | `app/main.py` |
| **任务执行器** | 异步调用 ncmdump、状态更新 | `app/main.py` |
| **静态资源** | CSS/JS 等静态文件托管 | `static/` |

### 4.3 数据流

```
用户上传文件
    │
    ▼
保存到 uploads/{task_id}/
    │
    ▼
创建 ConversionTask (status=pending)
    │
    ▼
BackgroundTask 启动异步转换
    │
    ▼
执行: ncmdump {file} -o outputs/{task_id}/
    │
    ├─成功─▶ status=completed, files=[...]
    │
    └─失败─▶ status=failed, message=error
    │
    ▼
前端轮询 /api/status/{task_id}
    │
    ▼
用户下载文件
```

### 4.4 可扩展性考虑

- **任务队列**: 当前使用 FastAPI BackgroundTasks，可替换为 Celery + Redis
- **存储后端**: 当前使用本地文件系统，可替换为 S3/MinIO
- **状态存储**: 当前使用内存字典，可替换为 Redis
- **水平扩展**: 通过 Nginx 负载均衡 + 共享存储实现

---

## 5. 🪜 实现步骤与开发规划

### 阶段1：环境准备

**任务清单：**
- [x] 创建项目目录结构
  ```
  mkdir -p app static templates uploads outputs
  ```
- [x] 创建 `requirements.txt` 依赖文件
  ```
  fastapi==0.109.0
  uvicorn[standard]==0.27.0
  python-multipart==0.0.6
  aiofiles==23.2.1
  ```
- [x] 创建 `.gitignore` 和 `.dockerignore`

### 阶段2：基础功能开发

**2.1 后端 API 开发 (`app/main.py`)**

| 函数 | 逻辑说明 | 测试方法 |
|------|----------|----------|
| `index()` | 返回 HTML 模板 | `curl http://localhost:8000/` |
| `upload_files()` | 保存文件、创建任务、启动后台转换 | 使用 Postman 上传 .ncm 文件 |
| `run_ncmdump()` | 异步执行 ncmdump 命令、更新状态 | 检查 outputs 目录生成文件 |
| `get_status()` | 返回任务状态 | `curl http://localhost:8000/api/status/{id}` |
| `download_file()` | 返回单个文件流 | 浏览器下载测试 |
| `download_all()` | 打包 ZIP 并返回 | 浏览器下载测试 |

**2.2 前端界面开发 (`templates/index.html`)**

| 组件 | 功能 |
|------|------|
| Upload Zone | 拖拽区域、文件选择器、dragover 样式 |
| File List | 显示已选文件名和大小 |
| Convert Button | 触发上传和转换 |
| Status Card | 显示任务状态、进度条 |
| Result Files | 显示下载链接 |

### 阶段3：整合与联调

**联调检查点：**
- [ ] 上传 .ncm 文件 → 返回 task_id
- [ ] 轮询状态 → 从 pending → processing → completed
- [ ] 下载单个文件 → 文件正确
- [ ] 下载 ZIP → 包含所有文件
- [ ] 上传非 .ncm 文件 → 返回 400 错误
- [ ] 查询不存在的 task_id → 返回 404

**常见问题排查：**
| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 转换失败 | ncmdump 未安装 | 检查 PATH 或 Docker 镜像 |
| 文件下载 404 | 输出路径错误 | 检查 OUTPUT_DIR 配置 |
| CORS 错误 | 跨域未配置 | 确认 CORSMiddleware 生效 |

### 阶段4：容器化部署

**4.1 Dockerfile 构建**
```dockerfile
FROM python:3.11-slim
# 安装 ncmdump
# 安装 Python 依赖
# 复制代码
# 启动 uvicorn
```

**4.2 docker-compose.yml**
```yaml
services:
  ncm-converter:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
```

**4.3 部署命令**
```bash
docker compose up -d --build
```

---

## 6. 🧯 辅助说明与注意事项

### 6.1 异常处理策略

| 场景 | 处理方式 |
|------|----------|
| 上传空文件列表 | 返回 400 Bad Request |
| 上传非 .ncm 文件 | 过滤忽略，仅处理有效文件 |
| ncmdump 执行失败 | 捕获 stderr，记录到 task.message |
| 任务不存在 | 返回 404 Not Found |
| 文件不存在 | 返回 404 Not Found |

### 6.2 边界条件处理

```python
# 文件大小限制（建议在 Nginx 层配置）
client_max_body_size 500M;

# 文件名安全处理
filename = secure_filename(file.filename)

# 路径穿越防护
if ".." in filename:
    raise HTTPException(400, "Invalid filename")
```

### 6.3 资源清理策略

```python
def cleanup_old_files(directory: Path, max_age_hours: int = 24):
    """定期清理超过 24 小时的临时文件"""
    current_time = time.time()
    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_hours * 3600:
                file_path.unlink()
```

### 6.4 幂等性保证

- 每次上传生成唯一 `task_id` (UUID)
- 相同文件重复上传会创建新任务
- 状态查询为只读操作，天然幂等

### 6.5 安全注意事项

| 风险 | 缓解措施 |
|------|----------|
| 命令注入 | 使用 subprocess 的 shell=False 模式或参数化命令 |
| 路径穿越 | 校验文件名，禁止 `..` |
| DoS 攻击 | 限制上传文件大小和并发数 |
| 敏感信息泄露 | 错误信息不暴露系统路径 |

---

## 7. ⚙️ 推荐技术栈与工具

### 7.1 编程语言与框架

| 层级 | 技术选型 | 选择理由 |
|------|----------|----------|
| 后端 | Python 3.11 + FastAPI | 高性能异步框架，自动生成 OpenAPI 文档 |
| 前端 | 原生 HTML/CSS/JS | 简单场景无需框架，减少依赖 |
| 容器 | Docker + docker-compose | 标准化部署，环境一致性 |

### 7.2 第三方库

| 库 | 用途 |
|----|------|
| `uvicorn[standard]` | ASGI 服务器，支持 HTTP/2 |
| `python-multipart` | 解析 multipart/form-data |
| `aiofiles` | 异步文件操作 |

### 7.3 外部工具

| 工具 | 用途 |
|------|------|
| `ncmdump` | 核心转换引擎 (来自 taurusxin/ncmdump) |
| Docker | 容器化运行环境 |
| Nginx (可选) | 反向代理、SSL 终止、静态资源缓存 |

### 7.4 调试与测试工具

| 工具 | 用途 |
|------|------|
| `curl` | API 接口测试 |
| Postman | 可视化 API 调试 |
| `pytest` + `httpx` | 自动化测试 |
| Docker logs | 容器日志查看 |

### 7.5 生产环境增强建议

| 组件 | 推荐方案 |
|------|----------|
| 任务队列 | Celery + Redis |
| 状态存储 | Redis |
| 对象存储 | MinIO / AWS S3 |
| 监控 | Prometheus + Grafana |
| 日志 | ELK Stack / Loki |

---

## 附录：快速启动命令

```bash
# 开发环境
cd /storage/Project/Vibe_Coding/ncm_to_mp3
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境 (Docker)
docker compose up -d --build

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```
