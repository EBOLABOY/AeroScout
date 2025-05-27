# API调用限制配置

## 当前限制设置

### 普通用户
- **POI调用限制**: 每日10次
- **航班搜索限制**: 每日5次
- **总限制**: 每日15次

### 管理员用户
- **无限制**: 管理员用户不受任何API调用限制约束

## 配置文件

### 环境变量 (.env)
```
POI_DAILY_LIMIT=10
FLIGHT_DAILY_LIMIT=5
```

### 配置类 (config.py)
```python
POI_DAILY_LIMIT: int = 10
FLIGHT_DAILY_LIMIT: int = 5
```

## 实现细节

### 1. Rate Limiter
- 位置: `app/core/dependencies.py`
- 管理员用户会直接跳过限制检查
- 普通用户会根据配置的限制进行检查

### 2. API统计显示
- 位置: `app/apis/v1/endpoints/users.py`
- 管理员用户显示"无限制"
- 普通用户显示具体的限制数字

### 3. 前端显示
- 位置: `aeroscout-frontend/src/app/dashboard/page.tsx`
- 当限制值 >= 999999 时显示"无限制"
- 否则显示具体数字

## 测试

运行测试脚本验证配置:
```bash
cd aeroscouthq_backend
python test_limits.py
```

## 注意事项

1. 修改限制后需要重启后端服务器
2. 管理员权限通过 `user.is_admin` 字段判断
3. 当前实现使用统一计数器，未来可以实现分别计数
