# 钓鱼地图图片存储服务器

纯血鸿蒙App"钓鱼地图"的图片存储服务器，支持用户上传头像、钓点照片、渔获照片。

## 技术栈

- FastAPI (Python)
- SQLite
- Nginx
- Docker Compose

## 快速开始

### 本地开发

```bash
# 1. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# macOS 需要额外安装
pip install python-magic-bin  # 替代 python-magic

# 2. 启动服务
uvicorn app.main:app --reload

# 3. 访问
# API: http://localhost:8000
# 管理后台: http://localhost:8000/admin
# API文档: http://localhost:8000/docs
```

### 运行测试

```bash
# 方式1: 使用脚本
bash scripts/run_tests.sh

# 方式2: 直接运行
pytest -v

# 测试结果: 19 passed ✅
```

### 局域网测试

```bash
# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 管理后台会显示本机IP，其他设备访问 http://<IP>:8000
# 例如: http://192.168.43.5:8000
```

### Docker部署

```bash
docker-compose up -d
```

## API接口

### App上传接口

```
POST /api/upload
X-API-Secret: fishmap
Content-Type: multipart/form-data

参数:
- file: 图片文件
- uid: 用户ID
- type: avatar | fishing_spot | catch
- spot_id: 钓点ID（仅fishing_spot需要）

响应:
{
  "id": "a3f8b2c1",
  "url": "/images/a3f8b2c1.jpg",
  "status": "active"
}
```

### 管理后台

- 登录: `http://localhost:8000/admin`
- 默认账号: `admin` / `fishmap2024`

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| API_SECRET | fishmap | API密钥 |
| MAX_FILE_SIZE | 20971520 | 最大文件大小(20MB) |
| ADMIN_USER | admin | 管理后台用户名 |
| ADMIN_PASSWORD | fishmap2024 | 管理后台密码 |
| IMAGE_DIR | ./data/images | 图片存储目录 |
| DB_PATH | ./data/db/images.db | 数据库路径 |

## 目录结构

```
fishmap-image-server/
├── app/                    # 后端代码
│   ├── main.py            # FastAPI入口
│   ├── config.py          # 配置
│   ├── database.py        # 数据库
│   ├── schemas.py         # 数据模型
│   ├── routes/            # 路由
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── admin/                  # 管理后台前端
├── tests/                  # 测试
├── scripts/                # 脚本
├── docker-compose.yml
├── Dockerfile
└── nginx.conf
```

## 测试覆盖

| 测试项 | 状态 |
|--------|------|
| 上传成功 | ✅ |
| 上传失败（secret错误） | ✅ |
| 上传失败（文件超20MB） | ✅ |
| 上传失败（非图片类型） | ✅ |
| 上传失败（缺少spot_id） | ✅ |
| 管理登录 | ✅ |
| 图片列表/筛选 | ✅ |
| 统计接口 | ✅ |
| 服务器信息 | ✅ |
| 未授权访问拦截 | ✅ |
