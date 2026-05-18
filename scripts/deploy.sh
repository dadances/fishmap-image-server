#!/bin/bash
set -e

echo "=== 部署到服务器 ==="

REMOTE_USER="root"
REMOTE_HOST="your-server-ip"
REMOTE_PATH="/opt/fishmap-image-server"

echo "上传代码到服务器..."
rsync -avz --exclude 'venv' --exclude '.git' --exclude 'data' \
    "$(dirname "$0")/../" ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

echo "在服务器上部署..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
cd /opt/fishmap-image-server
docker-compose down || true
docker-compose up -d --build
echo "部署完成！"
ENDSSH

echo "访问地址: http://fishmap.top/admin"
