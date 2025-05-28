# AeroScout 部署配置指南

## 🔧 硬编码地址修复总结

### 已修复的硬编码地址：

1. **前端API服务文件**
   - `src/lib/apiService.ts` - 移除了硬编码的 `baseURL: 'http://localhost:8000/api'`
   - `src/lib/v2Adapter.ts` - 修复了硬编码的API URL，现在使用环境变量
   - `src/lib/v2AdapterFixed.ts` - 修复了硬编码的API URL，现在使用环境变量

2. **Docker配置文件**
   - `Dockerfile.static` - 使用构建参数传递API URL
   - `nginx.frontend.conf` - 使用环境变量替换后端代理地址
   - `docker-entrypoint.sh` - 新增启动脚本处理nginx配置

3. **Docker Compose文件**
   - `docker-compose.build.yml` - 使用环境变量配置API地址
   - `docker-compose.prebuilt.yml` - 使用环境变量配置API地址

4. **健康检查脚本**
   - `health-check.bat` - 改为使用localhost（适合本地开发）
   - `health-check-flexible.bat` - 新增支持环境变量的灵活版本

## 环境变量配置

### 前端环境变量

#### NEXT_PUBLIC_API_URL
- **描述**: 前端调用后端API的基础URL
- **默认值**: `http://localhost:8000`
- **生产环境示例**: `https://AeroScout.izlx.de`
- **注意**: 这个变量必须以 `NEXT_PUBLIC_` 开头才能在浏览器中使用

#### NEXT_PUBLIC_API_BASE_URL
- **描述**: API客户端的基础URL（包含API版本路径）
- **默认值**: `http://localhost:8000/api/v1`
- **生产环境示例**: `https://AeroScout.izlx.de/api/v1`

### 后端环境变量

#### BACKEND_URL (用于nginx代理)
- **描述**: nginx代理转发到后端的URL
- **默认值**: `http://localhost:8000`
- **Docker环境示例**: `http://backend:8000`

## 部署方式

### 1. 开发环境
```bash
# 设置环境变量
export NEXT_PUBLIC_API_URL=http://localhost:8000

# 启动服务
docker-compose up -d
```

### 2. 生产环境 (使用域名)
```bash
# 设置环境变量
export NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de
export BACKEND_URL=http://backend:8000

# 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 静态部署
```bash
# 构建时设置API URL
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de \
  -f aeroscout-frontend/Dockerfile.static \
  -t aeroscout-frontend:static \
  ./aeroscout-frontend

# 运行时设置后端URL
docker run -d \
  -p 80:80 \
  -e BACKEND_URL=http://your-backend:8000 \
  aeroscout-frontend:static
```

## 配置文件说明

### .env 文件示例
```env
# 前端API地址
NEXT_PUBLIC_API_URL=https://AeroScout.izlx.de

# 后端代理地址 (用于nginx)
BACKEND_URL=http://backend:8000

# 其他配置...
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=sqlite+aiosqlite:///./aeroscout.db
```

### Docker Compose 环境变量
所有Docker Compose文件现在都支持通过环境变量配置API地址：

```yaml
environment:
  - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000}
```

## 健康检查

### 使用灵活的健康检查脚本
```bash
# 设置自定义地址
set FRONTEND_URL=https://AeroScout.izlx.de
set BACKEND_URL=https://AeroScout.izlx.de

# 运行检查
health-check-flexible.bat
```

## 故障排除

### 1. API调用失败
- 检查 `NEXT_PUBLIC_API_URL` 是否正确设置
- 确认后端服务是否可访问
- 检查CORS配置

### 2. nginx代理错误
- 检查 `BACKEND_URL` 环境变量
- 确认nginx配置模板是否正确替换
- 查看nginx错误日志

### 3. 构建时错误
- 确保构建参数正确传递
- 检查Dockerfile中的ARG和ENV配置

## 注意事项

1. **NEXT_PUBLIC_** 前缀的环境变量会被打包到前端代码中，在浏览器中可见
2. 生产环境建议使用HTTPS
3. 确保所有服务之间的网络连通性
4. 定期检查和更新环境变量配置
