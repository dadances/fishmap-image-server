# 钓鱼地图图片存储服务器

纯血鸿蒙 App "钓鱼地图" 的图片存储服务器，支持头像、钓点照片、渔获照片的上传、存储和管理。

## 技术栈

- **FastAPI** (Python 3.8+) — 异步高性能 Web 框架
- **SQLite** — 零配置数据库
- **Docker Compose** — 一键部署

## 服务器地址

| 项目 | 地址 |
|------|------|
| 管理后台 | http://121.43.194.67:2000/admin |
| 上传接口 | http://121.43.194.67:2000/api/upload |
| API 文档 | http://121.43.194.67:2000/docs |
| 健康检查 | http://121.43.194.67:2000/health |

> 本地开发时端口为 2026，地址为 `http://localhost:2026`。

## 快速测试（3 种方式）

### 方式 1：管理后台可视化

打开 http://121.43.194.67:2000/admin ，登录后点击「＋ 上传图片」按钮即可上传测试。

- 默认账号：`admin`
- 默认密码：`fishmap2024`

### 方式 2：curl 命令行

```bash
# 上传头像
curl -X POST http://121.43.194.67:2000/api/upload \
  -H "X-API-Secret: fishmap" \
  -F "file=@photo.jpg" \
  -F "uid=user_001" \
  -F "type=avatar"

# 上传钓点照片
curl -X POST http://121.43.194.67:2000/api/upload \
  -H "X-API-Secret: fishmap" \
  -F "file=@spot.jpg" \
  -F "uid=user_001" \
  -F "type=fishing_spot" \
  -F "spot_id=spot_101"

# 上传渔获照片
curl -X POST http://121.43.194.67:2000/api/upload \
  -H "X-API-Secret: fishmap" \
  -F "file=@catch.jpg" \
  -F "uid=user_001" \
  -F "type=catch"
```

响应示例：
```json
{
  "id": "a3f8b2c1",
  "url": "http://121.43.194.67:2000/images/a3f8b2c1.jpg",
  "status": "active"
}
```

### 方式 3：Python 脚本

```python
import requests

url = "http://121.43.194.67:2000/api/upload"
headers = {"X-API-Secret": "fishmap"}

with open("photo.jpg", "rb") as f:
    res = requests.post(url, headers=headers,
        data={"uid": "user_001", "type": "avatar"},
        files={"file": f})

print(res.json())
# {'id': 'a3f8b2c1', 'url': 'http://121.43.194.67:2000/images/a3f8b2c1.jpg', 'status': 'active'}
```

---

## 接入指南

### 鸿蒙 HarmonyOS 端

```typescript
import request from '@ohos.request';

let uploadConfig = {
  url: 'http://121.43.194.67:2000/api/upload',
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
    { name: 'uid', value: 'user_001' },
    { name: 'type', value: 'fishing_spot' },
    { name: 'spot_id', value: 'spot_101' }  // 钓点类型必填
  ]
}

request.uploadFile(context, uploadConfig)
  .then((uploadTask) => {
    uploadTask.on('complete', (taskStates) => {
      console.info('upload complete');
    });
  });
```

### Android / Java

```java
OkHttpClient client = new OkHttpClient();
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

client.newCall(request).enqueue(callback);
```

### iOS / Swift

```swift
let url = URL(string: "http://121.43.194.67:2000/api/upload")!
let boundary = UUID().uuidString
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("fishmap", forHTTPHeaderField: "X-API-Secret")
request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

var body = Data()
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"uid\"\r\n\r\n".data(using: .utf8)!)
body.append("user_001\r\n".data(using: .utf8)!)
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"type\"\r\n\r\n".data(using: .utf8)!)
body.append("avatar\r\n".data(using: .utf8)!)
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"file\"; filename=\"photo.jpg\"\r\n".data(using: .utf8)!)
body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
body.append(imageData)
body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
request.httpBody = body

URLSession.shared.dataTask(with: request) { data, response, error in
    // handle response
}.resume()
```

---

## API 完整参考

### 图片上传

```
POST /api/upload
```

| 请求头 | 值 | 必填 |
|--------|------|------|
| X-API-Secret | fishmap | 是 |

| 表单参数 | 类型 | 必填 | 说明 |
|----------|------|------|------|
| file | file | 是 | 图片文件（jpg/png/webp/gif，最大 20MB） |
| uid | string | 是 | 用户唯一 ID |
| type | string | 是 | `avatar` / `fishing_spot` / `catch` |
| spot_id | string | 条件 | 仅 type=fishing_spot 时必填 |

**响应** `200`：
```json
{
  "id": "a3f8b2c1",
  "url": "http://121.43.194.67:2000/images/a3f8b2c1.jpg",
  "status": "active"
}
```

**错误**：
| 状态码 | 说明 |
|--------|------|
| 400 | 参数错误（文件类型不符、缺少 spot_id） |
| 401 | X-API-Secret 错误 |
| 413 | 文件超过 20MB |

### 图片访问

```
GET /images/{id}.{ext}
```

示例：`http://121.43.194.67:2000/images/a3f8b2c1.jpg`

上传成功后返回的 `url` 字段即为该地址。

---

## 管理后台

**地址**：http://121.43.194.67:2000/admin  
**账号**：`admin` / `fishmap2024`

### 功能

| 页面 | 功能 |
|------|------|
| 图片管理 | 列表查看、筛选（UID/类型/状态）、预览、复制链接、替换、删除 |
| 回收站 | 已删除图片保留 7 天，支持还原和永久删除 |
| 系统设置 | 修改存储路径、数据库路径、管理员账号密码、文件大小限制 |
| 重启服务 | 修改配置后一键重启 |
| 清理残留 | 清除未被数据库引用的孤儿文件 |

---

## 本地开发

```bash
# 克隆
git clone https://github.com/dadances/fishmap-image-server.git
cd fishmap-image-server

# 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# macOS 额外安装
pip install python-magic-bin

# 启动（默认端口 2026）
uvicorn app.main:app --reload

# 运行测试
pytest -v          # 19 passed ✅

# 局域网测试（其他设备可访问）
uvicorn app.main:app --host 0.0.0.0 --port 2026
```

---

## 配置

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| API_SECRET | `fishmap` | 上传接口认证密钥 |
| MAX_FILE_SIZE | `20971520` | 最大文件大小（20MB） |
| ADMIN_USER | `admin` | 管理后台用户名 |
| ADMIN_PASSWORD | `fishmap2024` | 管理后台密码 |
| IMAGE_DIR | `./data/images` | 图片存储目录 |
| DB_PATH | `./data/db/images.db` | 数据库路径 |
| DOMAIN | `121.43.194.67:2000` | 返回 URL 使用的域名地址 |
| PORT | `2026` | 服务端口 |

---

## 目录结构

```
fishmap-image-server/
├── app/                    # 后端代码
│   ├── main.py            # FastAPI 入口
│   ├── config.py          # 配置管理
│   ├── database.py        # SQLite 数据库
│   ├── schemas.py         # Pydantic 数据模型
│   ├── routes/
│   │   ├── upload.py      # 上传接口
│   │   └── admin.py       # 管理后台 API
│   ├── services/
│   │   └── image_service.py
│   └── utils/
│       └── file_utils.py  # 文件类型验证
├── admin/
│   └── index.html         # 管理后台前端（Alpine.js）
├── tests/                 # 自动化测试（19 个用例）
├── scripts/
│   ├── run_tests.sh
│   └── deploy.sh
├── data/                  # 运行时创建
│   ├── images/            # 图片存储
│   │   ├── backup/        # 替换/删除备份
│   │   └── recycle/       # 回收站
│   └── db/                # SQLite 数据库
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 测试覆盖

| 测试项 | 状态 |
|--------|------|
| 上传成功 | ✅ |
| X-API-Secret 错误 | ✅ |
| 文件超 20MB | ✅ |
| 非图片类型 | ✅ |
| 钓点缺少 spot_id | ✅ |
| 空文件 | ✅ |
| 管理登录 | ✅ |
| 图片列表/筛选 | ✅ |
| 统计接口 | ✅ |
| 服务器信息 | ✅ |
| 未授权拦截 | ✅ |
