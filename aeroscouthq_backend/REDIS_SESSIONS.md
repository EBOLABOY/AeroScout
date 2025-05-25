# Redis搜索会话存储

本文档介绍AeroScout项目中Redis搜索会话存储功能的实现和使用。

## 功能概述

Redis搜索会话存储提供了以下功能：

- **多用户并发支持**: 支持多个用户同时进行航班搜索
- **会话持久化**: 搜索会话数据存储在Redis中，服务重启后不会丢失
- **自动过期**: 搜索会话自动过期，避免内存泄漏
- **高性能**: 基于Redis的高性能键值存储
- **故障回退**: Redis不可用时自动回退到内存存储

## 架构设计

### 核心组件

1. **RedisManager** (`app/core/redis_manager.py`)
   - 管理Redis连接池
   - 提供Redis客户端实例
   - 处理连接初始化和关闭

2. **SearchSessionStorage** (`app/core/search_session_storage.py`)
   - 抽象存储接口
   - Redis存储实现
   - 内存存储实现（备选方案）

3. **SearchSessionManager** (`app/core/search_session_manager.py`)
   - 统一的会话管理接口
   - 自动选择存储后端
   - 提供高级会话操作

### 存储策略

- **Redis键格式**: `search_session:{search_id}`
- **数据序列化**: JSON格式，支持datetime自动转换
- **TTL管理**: 默认1小时过期时间，可配置
- **数据库分离**: 使用Redis数据库2，避免与Celery冲突

## 配置说明

### 环境变量

```bash
# Redis连接配置
REDIS_URL=redis://localhost:6379/2

# 搜索会话TTL（秒）
REDIS_SESSION_TTL=3600
```

### 配置文件

在 `.env` 文件中添加：

```env
# Redis Configuration for Search Sessions
REDIS_URL=redis://localhost:6379/2
REDIS_SESSION_TTL=3600
```

## 使用方法

### 启动服务

1. **使用新的启动脚本**:
   ```bash
   start_with_redis.bat
   ```

2. **手动启动Redis**:
   ```bash
   # 使用Docker
   docker run -d -p 6379:6379 redis:latest
   
   # 或安装本地Redis服务
   redis-server
   ```

### API端点

#### 健康检查
```http
GET /api/v2/flights/health
```

响应示例：
```json
{
  "status": "healthy",
  "version": "v2",
  "message": "V2 API is running",
  "timestamp": "2024-01-01T12:00:00",
  "search_session_storage": {
    "status": "healthy",
    "storage_type": "redis",
    "redis_available": true
  }
}
```

#### 列出搜索会话
```http
GET /api/v2/flights/sessions?pattern=*
```

#### 获取会话详细信息
```http
GET /api/v2/flights/sessions/{search_id}/info
```

#### 搜索状态查询
```http
GET /api/v2/flights/search/status/{search_id}
```

#### 清理搜索会话
```http
DELETE /api/v2/flights/search/{search_id}
```

## 测试

### 运行测试脚本

```bash
python test_redis_sessions.py
```

测试内容包括：
- Redis连接测试
- 基本CRUD操作
- 并发会话处理
- TTL功能验证
- 故障回退测试

### 手动测试

1. **创建搜索会话**:
   ```bash
   curl -X POST "http://localhost:8000/api/v2/flights/search/phase-one" \
        -H "Content-Type: application/json" \
        -d '{
          "origin_iata": "PEK",
          "destination_iata": "LAX",
          "departure_date_from": "2024-03-01"
        }'
   ```

2. **查询会话状态**:
   ```bash
   curl "http://localhost:8000/api/v2/flights/search/status/{search_id}"
   ```

## 性能优化

### Redis配置优化

```redis
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### 连接池配置

```python
# 在redis_manager.py中调整
max_connections=20      # 最大连接数
socket_timeout=5        # 读写超时
health_check_interval=30 # 健康检查间隔
```

## 监控和日志

### 日志级别

- `INFO`: 连接状态、会话创建/删除
- `DEBUG`: 详细的操作日志
- `ERROR`: 连接失败、操作错误

### 监控指标

- Redis连接状态
- 会话创建/删除速率
- TTL过期统计
- 存储类型切换事件

## 故障排除

### 常见问题

1. **Redis连接失败**
   - 检查Redis服务是否运行
   - 验证连接配置
   - 查看防火墙设置

2. **会话数据丢失**
   - 检查TTL配置
   - 验证Redis持久化设置
   - 查看Redis内存使用情况

3. **性能问题**
   - 监控Redis内存使用
   - 检查连接池配置
   - 优化序列化性能

### 调试命令

```bash
# 检查Redis连接
redis-cli ping

# 查看搜索会话键
redis-cli keys "search_session:*"

# 查看特定会话
redis-cli get "search_session:your_search_id"

# 监控Redis操作
redis-cli monitor
```

## 部署建议

### 生产环境

1. **Redis集群**: 使用Redis Cluster或Sentinel
2. **持久化**: 启用RDB和AOF持久化
3. **监控**: 集成Redis监控工具
4. **备份**: 定期备份Redis数据

### 开发环境

1. **单实例Redis**: 使用Docker容器
2. **内存存储备选**: 确保故障回退正常工作
3. **调试日志**: 启用详细日志记录

## 更新日志

- **v1.0.0**: 初始实现Redis搜索会话存储
- **v1.1.0**: 添加并发支持和故障回退
- **v1.2.0**: 优化性能和添加监控功能
