# AeroScout 数据库迁移指南

## 📊 数据库表结构总览

### 当前数据库包含以下8个表：

1. **users** - 用户表
   - 存储用户基本信息、认证信息
   - 包含 `is_admin` 字段标识管理员权限
   - 主键：id (自增)

2. **invitation_codes** - 邀请码表
   - 管理用户注册邀请码
   - 跟踪邀请码使用状态
   - 主键：id (自增)

3. **locations** - 位置表
   - 存储地理位置信息
   - 支持城市、机场等位置数据
   - 主键：id (自增)

4. **airports** - 机场表
   - 存储机场详细信息
   - IATA/ICAO代码、坐标等
   - 主键：id (自增)

5. **potential_hubs** - 潜在枢纽表
   - 存储可能的中转枢纽信息
   - 用于隐藏城市票务分析
   - 主键：id (自增)

6. **user_searches** - 用户搜索记录表
   - 记录用户的搜索历史
   - 用于分析和优化
   - 主键：id (自增)

7. **legal_texts** - 法律文本表
   - 存储隐私政策、服务条款等
   - 支持多语言和版本管理
   - 主键：id (自增)

8. **alembic_version** - Alembic版本表
   - 跟踪数据库迁移版本
   - 由Alembic自动管理

## 🔄 迁移链结构

当前迁移链按以下顺序执行：

```
None → 0001_create_initial_database_schema → 76db113d9a1e → c47909388e6b → create_default_admin → ad9f5c7e8b23
```

### 迁移文件详情：

1. **0001_create_initial_database_schema.py**
   - 创建所有基础表结构
   - 使用 metadata.create_all() 方法
   - 包含所有核心业务表

2. **76db113d9a1e_add_is_admin_to_users_table.py**
   - 为users表添加 is_admin 字段
   - 设置默认值为 False

3. **c47909388e6b_initial_schema.py**
   - 空迁移文件（占位符）
   - 用于维护迁移链完整性

4. **create_default_admin.py**
   - 创建默认管理员账户
   - 邮箱：1242772513@qq.com
   - 密码：1242772513
   - 自动设置管理员权限

5. **add_legal_texts_table.py**
   - 智能检查并创建legal_texts表
   - 如果表已存在则跳过创建
   - 创建相关索引

## 🚀 首次部署流程

### 1. 自动迁移（推荐）
```bash
cd aeroscouthq_backend
alembic upgrade head
```

### 2. 手动初始化管理员（可选）
```bash
python init_default_admin.py
```

### 3. 验证部署
```bash
python check_db.py
```

## ✅ 部署验证清单

### 数据库检查：
- [ ] 数据库文件已创建 (aeroscout.db)
- [ ] 所有8个表都已创建
- [ ] Alembic版本为最新 (ad9f5c7e8b23)
- [ ] 默认管理员账户已创建
- [ ] 管理员权限设置正确

### 功能测试：
- [ ] 用户注册功能正常
- [ ] 管理员登录正常
- [ ] API接口响应正常
- [ ] 数据库连接稳定

## 🔧 故障排除

### 常见问题：

1. **迁移失败：表已存在**
   - 原因：重复运行迁移
   - 解决：检查当前版本 `alembic current`
   - 如需重置：删除数据库文件重新迁移

2. **默认管理员创建失败**
   - 检查数据库连接
   - 确认users表已创建
   - 查看详细错误日志

3. **编码错误（Windows）**
   - 已修复：移除了Unicode emoji字符
   - 使用标准ASCII字符输出

### 测试脚本：

- **check_db.py** - 检查数据库表结构
- **test_fresh_deploy.py** - 测试全新部署流程
- **init_default_admin.py** - 初始化默认管理员

## 📝 注意事项

1. **生产环境部署**：
   - 建议在部署前备份现有数据
   - 在测试环境先验证迁移
   - 监控迁移过程的日志

2. **默认管理员安全**：
   - 首次登录后立即修改密码
   - 考虑创建专用管理员账户
   - 定期审查管理员权限

3. **数据库维护**：
   - 定期备份数据库文件
   - 监控数据库大小增长
   - 考虑数据清理策略

## 🎯 部署成功标志

当看到以下输出时，表示部署成功：

```
✅ Alembic迁移成功
✅ 数据库文件已创建
✅ 所有必要的表都已创建
✅ Alembic版本: ad9f5c7e8b23
✅ 默认管理员创建成功
✅ 默认管理员账户验证成功
🎉 全新部署测试成功！
```
