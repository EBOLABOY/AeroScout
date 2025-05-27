#!/bin/bash
set -e

echo "🚀 AeroScout Backend 启动脚本"
echo "================================"

# 确保数据目录存在
echo "📁 检查数据目录..."
mkdir -p /app/data
chmod 755 /app/data

# 等待数据库准备就绪（如果使用外部数据库）
echo "📊 检查数据库连接..."

# 运行数据库迁移
echo "🔄 运行数据库迁移..."
alembic upgrade head

# 检查迁移是否成功
if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移完成"
else
    echo "❌ 数据库迁移失败"
    exit 1
fi

# 创建默认管理员账户（如果不存在）
echo "👤 检查默认管理员账户..."
python init_default_admin.py

# 启动应用
echo "🌟 启动 FastAPI 应用..."
echo "================================"

# 使用uvicorn启动应用
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
