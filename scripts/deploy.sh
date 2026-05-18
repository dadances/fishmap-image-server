#!/bin/bash
set -e

echo "=== 部署到服务器 ==="

REMOTE_USER="root"
REMOTE_HOST="your-server-ip"
REMOTE_PATH="/opt/fishmap-image-server"

echo "上传代码到服务器..."
rsync -avz --exclude 'venv' --exclude '.git' --exclude 'data' --exclude '__pycache__' \
    --exclude '.pytest_cache' --exclude '*.pyc' \
    "$(dirname "$0")/../" ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

echo "在服务器上安装依赖并启动..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
cd /opt/fishmap-image-server

# Aliyun Linux / CentOS 系统依赖
if command -v yum &> /dev/null; then
    yum install -y file-devel libjpeg-turbo-devel zlib-devel python3-pip
elif command -v apt &> /dev/null; then
    apt update && apt install -y libmagic1 libjpeg-dev zlib1g-dev python3-pip
fi

# 安装 Python 依赖
pip3 install -r requirements.txt

# Docker 部署
if command -v docker-compose &> /dev/null || command -v docker &> /dev/null; then
    docker-compose down || true
    docker-compose up -d --build
else
    echo "未检测到 Docker，使用直接启动"
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 2026 > /tmp/fishmap.log 2>&1 &
fi

echo "部署完成！"
ENDSSH

echo "管理后台: http://fishmap.top/admin"
