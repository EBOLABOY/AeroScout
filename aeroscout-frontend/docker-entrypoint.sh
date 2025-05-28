#!/bin/sh

# 设置默认值
BACKEND_URL=${BACKEND_URL:-http://localhost:8000}

echo "🔧 配置nginx代理..."
echo "后端URL: $BACKEND_URL"

# 替换nginx配置中的环境变量
envsubst '${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "✅ nginx配置完成"
cat /etc/nginx/conf.d/default.conf

# 启动nginx
exec "$@"
