# 依赖安装阶段
FROM node:18-alpine AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# 复制package文件
COPY package.json package-lock.json* ./

# 安装依赖（包括devDependencies，构建时需要）
RUN npm ci

# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app

# 从deps阶段复制node_modules
COPY --from=deps /app/node_modules ./node_modules

# 复制源代码
COPY . .

# 设置环境变量
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# 构建应用
RUN npm run build

# 调试：检查构建产物结构
RUN echo "=== 检查构建后的目录结构 ===" && \
    ls -la /app && \
    echo "=== 检查 .next/standalone 目录 ===" && \
    ls -la /app/.next/standalone && \
    echo "=== 检查 .next/static 目录 ===" && \
    ls -la /app/.next/static

# 生产阶段
FROM node:18-alpine AS runner

WORKDIR /app

# 创建非root用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制构建产物 - standalone模式已包含public目录
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 设置权限
RUN chown -R nextjs:nodejs /app
USER nextjs

# 暴露端口
EXPOSE 3000

# 设置环境变量
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0

# 启动应用 - 使用 standalone 模式
CMD ["node", "server.js"]
