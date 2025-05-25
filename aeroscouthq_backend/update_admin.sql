-- 更新用户为管理员并设置密码
-- 密码哈希值对应 "Admin123!"

-- 更新已存在的用户
UPDATE users 
SET 
    is_admin = 1, 
    hashed_password = '$2b$12$1iRejnR9jZdQz.WvxW8YYeNhCXXD1CgEzjDcvmxZdgKR0jXEJhJwS'
WHERE 
    email = 'admin@aeroscout.com';

-- 如果用户不存在，则创建新用户
INSERT OR IGNORE INTO users 
(
    email, 
    hashed_password, 
    is_admin, 
    is_active, 
    created_at
) 
VALUES 
(
    'admin@aeroscout.com', 
    '$2b$12$1iRejnR9jZdQz.WvxW8YYeNhCXXD1CgEzjDcvmxZdgKR0jXEJhJwS', 
    1, 
    1, 
    CURRENT_TIMESTAMP
);

-- 显示更新后的用户信息
SELECT id, email, is_admin FROM users WHERE email = 'admin@aeroscout.com';
