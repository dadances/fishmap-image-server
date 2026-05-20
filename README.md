# 钓鱼地图图片存储服务器

纯血鸿蒙App"钓鱼地图"的图片存储服务器，支持用户上传头像、钓点照片、渔获照片。

## 技术栈

- **FastAPI** (Python 3.8+) - 异步高性能Web框架
- **SQLite** - 零配置数据库
- **Nginx** - 反向代理 + 静态文件服务
- **Docker Compose** - 一键部署

## 功能特性

- 图片上传（支持头像、钓点照片、渔获照片）
- 图片替换/删除（原图自动备份）
- 管理后台（图片列表、筛选、统计、设置）
- API密钥认证
- 局域网测试支持（自动获取本机IP）

## 快速开始

### 本地开发

```bash
# 1. 克隆项目
git clone https://github.com/YOUR_USERNAME/fishmap-image-server.git
cd fishmap-image-server

# 2. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# macOS 需要额外安装
pip install python-magic-bin  # 替代 python-magic

# 3. 启动服务（默认端口 2026）
uvicorn app.main:app --reload

# 4. 访问
# API: http://localhost:2026
# 管理后台: http://localhost:2026/admin
# API文档: http://localhost:2026/docs
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
uvicorn app.main:app --host 0.0.0.0 --port 2026

# 管理后台会显示本机IP，其他设备访问 http://<IP>:2026
# 例如: http://192.168.43.5:2026
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
- file: 图片文件（必填）
- uid: 用户ID（必填）
- type: avatar | fishing_spot | catch（必填）
- spot_id: 钓点ID（仅fishing_spot需要）

响应:
{
  "id": "a3f8b2c1",
  "url": "/images/a3f8b2c1.jpg",
  "status": "active"
}
```

### 管理后台API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/api/login` | POST | 管理员登录 |
| `/admin/api/images` | GET | 图片列表（支持分页/筛选） |
| `/admin/api/images/{id}/replace` | POST | 替换图片 |
| `/admin/api/images/{id}/delete` | DELETE | 删除图片 |
| `/admin/api/stats` | GET | 统计概览 |
| `/admin/api/info` | GET | 服务器信息（含本机IP） |
| `/admin/api/settings` | GET/POST | 系统设置 |

### 图片访问

```
GET /images/{uuid}.{ext}
```

## 管理后台

- 地址: `http://localhost:2026/admin`
- 默认账号: `admin` / `fishmap2024`

### 功能
- 图片列表（分页、按UID/钓点ID/类型/状态筛选）
- 图片预览
- 显示每张图片的完整URL，支持一键复制
- 替换图片（原图自动备份）
- 删除图片（原图自动备份）
- 统计概览
- 系统设置（存储路径、管理员账号密码、文件大小限制）

## 配置

### 环境变量

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `API_SECRET` | `fishmap` | API密钥 |
| `MAX_FILE_SIZE` | `20971520` | 最大文件大小(20MB) |
| `ADMIN_USER` | `admin` | 管理后台用户名 |
| `ADMIN_PASSWORD` | `fishmap2024` | 管理后台密码 |
| `IMAGE_DIR` | `./data/images` | 图片存储目录 |
| `DB_PATH` | `./data/db/images.db` | 数据库路径 |
| `PORT` | `2026` | 服务端口 |

### 系统设置（管理后台修改）

在管理后台"系统设置"页面可修改：
- 图片存储目录
- 数据库路径
- 管理员用户名
- 管理员密码
- 最大文件大小(MB)

设置会保存到 `data/config.json`，重启服务后生效。

## 目录结构

```
fishmap-image-server/
├── app/                    # 后端代码
│   ├── main.py            # FastAPI入口
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── schemas.py         # Pydantic数据模型
│   ├── routes/            # API路由
│   │   ├── upload.py      # 上传接口
│   │   └── admin.py       # 管理后台API
│   ├── services/          # 业务逻辑
│   │   └── image_service.py
│   └── utils/             # 工具函数
│       └── file_utils.py
├── admin/                  # 管理后台前端
│   └── index.html
├── tests/                  # 自动化测试
│   ├── conftest.py
│   ├── test_upload.py
│   ├── test_admin.py
│   └── test_auth.py
├── scripts/                # 脚本
│   ├── run_tests.sh
│   └── deploy.sh
├── data/                   # 数据目录（运行时创建）
│   ├── images/            # 图片存储
│   │   └── backup/        # 备份目录
│   └── db/                # 数据库
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## 测试覆盖

| 测试项 | 状态 |
|--------|------|
| 上传成功 | ✅ |
| 上传失败（secret错误） | ✅ |
| 上传失败（文件超20MB） | ✅ |
| 上传失败（非图片类型） | ✅ |
| 上传失败（缺少spot_id） | ✅ |
| 上传失败（空文件） | ✅ |
| 管理登录成功/失败 | ✅ |
| 图片列表/筛选 | ✅ |
| 统计接口 | ✅ |
| 服务器信息 | ✅ |
| 未授权访问拦截 | ✅ |

## 部署到阿里云

```bash
# 1. 修改 scripts/deploy.sh 中的服务器IP
# 2. 执行部署
bash scripts/deploy.sh

# 3. 配置HTTPS（可选）
certbot --nginx -d 121.43.194.67
```

## 鸿蒙端调用示例

```typescript
import request from '@ohos.request';

let uploadConfig = {
  url: 'https://fishmap.top/api/upload',
  header: {
    'X-API-Secret': 'fishmap'
  },
  method: 'POST',
  files: [
    { 
      filename: 'photo.jpg', 
      name: 'file',
      uri: 'internal://cache/photo.jpg', 
      type: 'jpg' 
    }
  ],
  data: [
    { name: 'uid', value: 'user123' },
    { name: 'type', value: 'fishing_spot' },
    { name: 'spot_id', value: 'spot888' }
  ]
}

request.uploadFile(context, uploadConfig)
  .then((uploadTask) => {
    uploadTask.on('complete', (taskStates) => {
      console.info('upload complete');
    });
  });
```
