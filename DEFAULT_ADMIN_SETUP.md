# 默认管理员账户设置说明

## 📋 概述

AeroScout 在首次部署时会自动创建一个默认管理员账户，方便初始化和管理系统。

## 👤 默认账户信息

- **邮箱**: 1242772513@qq.com
- **密码**: 1242772513
- **用户名**: admin
- **权限**: 管理员
- **状态**: 激活

## 🔧 自动创建机制

### 1. Alembic 迁移
系统使用 Alembic 数据库迁移在首次部署时自动创建默认管理员账户：

- 迁移文件: `aeroscouthq_backend/alembic/versions/create_default_admin.py`
- 执行时机: 数据库初始化时
- 检查机制: 如果账户已存在则跳过创建

### 2. Docker 启动脚本
Docker 容器启动时会运行初始化脚本：

- 启动脚本: `aeroscouthq_backend/docker-entrypoint.sh`
- 初始化脚本: `aeroscouthq_backend/init_default_admin.py`
- 执行顺序: 数据库迁移 → 创建默认管理员 → 启动应用

### 3. 首次部署脚本
提供了专门的首次部署脚本：

- Windows: `first-time-deploy.bat`
- Linux/macOS: `first-time-deploy.sh`

## 🛡️ 安全考虑

### ⚠️ 重要提醒

1. **立即修改密码**: 首次登录后请立即修改默认密码
2. **强密码策略**: 使用包含大小写字母、数字和特殊字符的强密码
3. **定期更新**: 定期更新管理员密码
4. **访问控制**: 限制管理员账户的访问来源

### 🔒 密码修改步骤

1. 使用默认账户登录系统
2. 进入用户设置或个人资料页面
3. 修改密码为强密码
4. 确认保存并重新登录验证

## 🔄 重置默认管理员

如果需要重置默认管理员账户，可以：

### 方法1: 重新运行初始化脚本
```bash
cd aeroscouthq_backend
python init_default_admin.py
```

### 方法2: 手动数据库操作
```sql
-- 删除现有管理员
DELETE FROM users WHERE email = '1242772513@qq.com';

-- 重新运行迁移
alembic upgrade head
```

### 方法3: 重新部署
```bash
# 完全重新部署
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build
```

## 📝 自定义默认管理员

如果需要修改默认管理员信息，可以编辑以下文件：

### 1. 修改迁移文件
编辑 `aeroscouthq_backend/alembic/versions/create_default_admin.py`:

```python
# 修改这些常量
DEFAULT_ADMIN_EMAIL = "your-email@example.com"
DEFAULT_ADMIN_USERNAME = "your-username"
# 需要重新生成密码哈希
DEFAULT_ADMIN_PASSWORD_HASH = "your-bcrypt-hash"
```

### 2. 修改初始化脚本
编辑 `aeroscouthq_backend/init_default_admin.py`:

```python
# 修改这些常量
DEFAULT_ADMIN_EMAIL = "your-email@example.com"
DEFAULT_ADMIN_PASSWORD = "your-password"
DEFAULT_ADMIN_USERNAME = "your-username"
```

### 3. 生成密码哈希
使用 Python 生成新的密码哈希：

```python
from app.core.security import get_password_hash
password_hash = get_password_hash("your-new-password")
print(password_hash)
```

## 🚀 部署后验证

部署完成后，验证默认管理员账户：

1. **访问前端**: http://your-domain:3000
2. **登录页面**: 点击登录
3. **使用默认账户**: 
   - 邮箱: 1242772513@qq.com
   - 密码: 1242772513
4. **验证权限**: 确认可以访问管理员功能

## 📞 故障排除

### 问题1: 默认管理员未创建
**解决方案**:
1. 检查数据库迁移是否成功执行
2. 查看容器日志: `docker logs aeroscout-backend`
3. 手动运行初始化脚本

### 问题2: 无法登录默认账户
**解决方案**:
1. 确认邮箱和密码输入正确
2. 检查数据库中用户表是否存在该记录
3. 验证密码哈希是否正确

### 问题3: 权限不足
**解决方案**:
1. 确认用户的 `is_admin` 字段为 `true`
2. 检查用户的 `is_active` 字段为 `true`
3. 重新创建管理员账户

## 📚 相关文件

- `aeroscouthq_backend/alembic/versions/create_default_admin.py` - 数据库迁移
- `aeroscouthq_backend/init_default_admin.py` - 初始化脚本
- `aeroscouthq_backend/docker-entrypoint.sh` - Docker 启动脚本
- `first-time-deploy.bat` / `first-time-deploy.sh` - 首次部署脚本
- `DEPLOYMENT.md` - 部署文档
