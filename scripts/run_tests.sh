#!/bin/bash
set -e

echo "=== 运行测试 ==="
cd "$(dirname "$0")/.."

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "运行 pytest..."
pytest -v

echo ""
echo "=== 测试完成 ==="
