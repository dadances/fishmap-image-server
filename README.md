# 钓鱼地图图片存储服务器

纯血鸿蒙 App "钓鱼地图" 的图片存储服务器，支持头像、钓点照片、渔获照片的上传、存储和管理。

## 特性

- 图片上传（头像 / 钓点 / 渔获，最大 20MB）
- 密钥认证（X-API-Secret）
- 用户自主删除（uid 权限校验）
- 回收站（7 天保留，支持还原、一键清空、过期自动清理）
- 管理后台（列表、筛选、替换、删除、上传、系统设置）
- 原图备份（替换/删除时自动备份原文件）
- 缓存穿透防护（URL 版本号 + no-cache 响应头）
- 自动化测试（19 个用例全部通过）

## 技术栈

- **FastAPI** (Python 3.8+) — 异步高性能 Web 框架
- **SQLite** — 零配置数据库
- **Docker Compose** — 一键部署

## 服务器地址

| 项目 | 地址 |
|------|------|
| 管理后台 | http://121.43.194.67:2000/admin |
| 上传接口 | http://121.43.194.67:2000/api/upload |
| 公开删除 | http://121.43.194.67:2000/api/images/{id} |
| API 文档 | http://121.43.194.67:2000/docs |
| 健康检查 | http://121.43.194.67:2000/health |

> 本地开发端口为 2026。

---

## 快速测试

### 方式 1：管理后台

打开 http://121.43.194.67:2000/admin，登录后点击「＋ 上传图片」即可。

- 账号：`admin` / `fishmap2024`

### 方式 2：curl

```bash
# 上传
curl -X POST http://121.43.194.67:2000/api/upload \
  -H "X-API-Secret: fishmap" \
  -F "file=@photo.jpg" \
  -F "uid=user_001" \
  -F "type=avatar"

# 响应
# {"id":"a3f8b2c1","url":"http://121.43.194.67:2000/images/a3f8b2c1.jpg","status":"active"}

# 用户自行删除
curl -X DELETE http://121.43.194.67:2000/api/images/a3f8b2c1 \
  -H "X-API-Secret: fishmap" \
  -F "uid=user_001"

# 响应
# {"success":true,"message":"Image deleted"}
```

### 方式 3：Python

```python
import requests

BASE = "http://121.43.194.67:2000"
HEADERS = {"X-API-Secret": "fishmap"}

# 上传
with open("photo.jpg", "rb") as f:
    r = requests.post(f"{BASE}/api/upload", headers=HEADERS,
        data={"uid": "user_001", "type": "avatar"},
        files={"file": f})
    print(r.json())

# 删除
r = requests.delete(f"{BASE}/api/images/a3f8b2c1",
    headers=HEADERS, data={"uid": "user_001"})
print(r.json())
```

---

## 接入指南

### 鸿蒙 (HarmonyOS)

```typescript
import request from '@ohos.request';

let uploadConfig = {
  url: 'http://121.43.194.67:2000/api/upload',
  header: { 'X-API-Secret': 'fishmap' },
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
    { name: 'uid', value: 'user_001' },
    { name: 'type', value: 'fishing_spot' },
    { name: 'spot_id', value: 'spot_101' }
  ]
};

request.uploadFile(context, uploadConfig)
  .then((uploadTask) => {
    uploadTask.on('complete', (taskStates) => {
      console.info('upload complete');
    });
  });
```

### Android (Java / OkHttp)

```java
RequestBody body = new MultipartBody.Builder()
    .setType(MultipartBody.FORM)
    .addFormDataPart("file", "photo.jpg",
        RequestBody.create(MediaType.parse("image/jpeg"), imageFile))
    .addFormDataPart("uid", "user_001")
    .addFormDataPart("type", "avatar")
    .build();

Request request = new Request.Builder()
    .url("http://121.43.194.67:2000/api/upload")
    .header("X-API-Secret", "fishmap")
    .post(body)
    .build();
```

### iOS (Swift / URLSession)

```swift
var request = URLRequest(url: URL(string: "http://121.43.194.67:2000/api/upload")!)
request.httpMethod = "POST"
request.setValue("fishmap", forHTTPHeaderField: "X-API-Secret")

let boundary = UUID().uuidString
request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
// ... construct multipart body with file, uid, type fields ...
URLSession.shared.dataTask(with: request) { data, _, _ in }.resume()
```

---

## API 完整参考

### 上传图片

```
POST /api/upload
X-API-Secret: fishmap
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 图片文件（jpg/png/webp/gif，≤20MB） |
| uid | string | 是 | 用户 ID |
| type | string | 是 | `avatar` / `fishing_spot` / `catch` |
| spot_id | string | 条件 | 仅 `fishing_spot` 类型必填 |

成功 `200`：

```json
{
  "id": "a3f8b2c1",
  "url": "http://121.43.194.67:2000/images/a3f8b2c1.jpg",
  "status": "active"
}
```

错误码：

| 状态 | 说明 |
|------|------|
| 400 | 参数错误 / 文件类型不符 |
| 401 | X-API-Secret 错误 |
| 413 | 文件超过 20MB |

### 删除图片（用户自主）

```
DELETE /api/images/{image_id}
X-API-Secret: fishmap
Content-Type: multipart/form-data
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| uid | string | 是 | 必须与上传者 uid 一致 |

成功 `200`：

```json
{"success": true, "message": "Image deleted"}
```

错误码：

| 状态 | 说明 |
|------|------|
| 401 | X-API-Secret 错误 |
| 403 | uid 不匹配，图片不属于该用户 |
| 404 | 图片不存在 |
| 400 | 图片已在回收站 |

### 图片访问

```
GET /images/{id}.{ext}
```

上传返回的 `url` 字段即直接可用地址。

### 管理后台 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/api/login` | POST | 管理员登录 |
| `/admin/api/images` | GET | 图片列表（筛选：uid/spot_id/type/status） |
| `/admin/api/images/{id}/replace` | POST | 替换图片 |
| `/admin/api/images/{id}/recycle` | POST | 移入回收站 |
| `/admin/api/recycle` | GET | 回收站列表（含剩余天数） |
| `/admin/api/recycle/{id}/restore` | POST | 还原图片 |
| `/admin/api/recycle/{id}/permanent` | DELETE | 永久删除 |
| `/admin/api/recycle/cleanup` | POST | 清理过期（>7 天） |
| `/admin/api/recycle/clear-all` | POST | 一键清空回收站 |
| `/admin/api/stats` | GET | 统计概览 |
| `/admin/api/info` | GET | 服务器信息 |
| `/admin/api/settings` | GET/POST | 系统设置 |
| `/admin/api/restart` | POST | 重启服务 |
| `/admin/api/cleanup` | POST | 清理孤儿文件 |

---

## 管理后台

http://121.43.194.67:2000/admin · `admin` / `fishmap2024`

| 页面 | 功能 |
|------|------|
| **图片管理** | 列表/筛选/预览/复制链接/替换/删除/上传 |
| **回收站** | 显示剩余天数、还原、永久删除、清理过期、一键清空 |
| **系统设置** | 存储路径、数据库路径、账号密码、文件大小限制、重启服务、清理残留 |

### 删除与回收站逻辑

```
用户/管理员删除 → 文件 → recycle/ 目录
                  → DB 记录标记 recycled，记录 deleted_at
                  → 回收站保留 7 天
                  → 7 天后自动永久删除（文件 + DB 记录）
                  → 或手动: 还原 / 永久删除 / 一键清空
```

---

## 本地开发

```bash
git clone https://github.com/dadances/fishmap-image-server.git
cd fishmap-image-server

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install python-magic-bin  # macOS 额外安装

# 启动
uvicorn app.main:app --reload

# 测试
pytest -v   # 19 passed
```

---

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `API_SECRET` | `fishmap` | 上传/删除认证密钥 |
| `MAX_FILE_SIZE` | `20971520` | 最大文件大小（20MB） |
| `ADMIN_USER` | `admin` | 管理后台账号 |
| `ADMIN_PASSWORD` | `fishmap2024` | 管理后台密码 |
| `IMAGE_DIR` | `./data/images` | 图片存储目录 |
| `DB_PATH` | `./data/db/images.db` | 数据库路径 |
| `DOMAIN` | `121.43.194.67:2000` | 返回 URL 域名 |
| `PORT` | `2026` | 服务端口 |

---

## 目录结构

```
fishmap-image-server/
├── app/
│   ├── main.py            # FastAPI 入口
│   ├── config.py           # 配置
│   ├── database.py         # SQLite
│   ├── schemas.py          # 数据模型
│   ├── routes/
│   │   ├── upload.py       # 上传 + 公开删除
│   │   └── admin.py        # 管理后台 API
│   ├── services/
│   │   └── image_service.py
│   └── utils/
│       └── file_utils.py
├── admin/
│   └── index.html          # 管理后台（Alpine.js）
├── tests/                  # 19 个测试用例
├── scripts/
│   ├── run_tests.sh
│   └── deploy.sh
├── data/                   # 运行时
│   ├── images/
│   │   ├── backup/         # 替换/删除原图备份
│   │   └── recycle/        # 回收站
│   └── db/
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── requirements.txt
└── README.md
```
