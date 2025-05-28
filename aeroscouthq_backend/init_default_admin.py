#!/usr/bin/env python3
"""
初始化默认管理员账户脚本
在首次部署后运行，创建默认的管理员账户
"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import get_password_hash
from app.database.connection import database
from app.database.models import users_table
from app.database.crud import user_crud, invitation_crud
from sqlalchemy import select, insert

# 默认管理员账户信息
DEFAULT_ADMIN_EMAIL = "1242772513@qq.com"
DEFAULT_ADMIN_PASSWORD = "1242772513"
DEFAULT_ADMIN_USERNAME = "admin"

async def create_default_admin():
    """创建默认管理员账户"""
    try:
        # 连接数据库
        await database.connect()
        print("[SUCCESS] 数据库连接成功")

        # 检查管理员账户是否已存在
        existing_admin = await user_crud.get_user_by_email(DEFAULT_ADMIN_EMAIL)
        if existing_admin:
            print(f"[WARNING] 管理员账户 {DEFAULT_ADMIN_EMAIL} 已存在，跳过创建")
            return

        # 创建默认邀请码（如果需要）
        invitation_code = "ADMIN_INIT_CODE"
        existing_invitation = await invitation_crud.get_invitation_code(invitation_code)
        if not existing_invitation:
            await invitation_crud.create_invitation_code(invitation_code)
            print(f"[SUCCESS] 创建默认邀请码: {invitation_code}")

        # 哈希密码
        hashed_password = get_password_hash(DEFAULT_ADMIN_PASSWORD)

        # 创建管理员用户
        admin_data = {
            "username": DEFAULT_ADMIN_USERNAME,
            "email": DEFAULT_ADMIN_EMAIL,
            "hashed_password": hashed_password,
            "is_admin": True,  # 设置为管理员
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "api_call_count_today": 0
        }

        # 直接插入数据库（绕过邀请码验证）
        query = insert(users_table).values(**admin_data)
        admin_id = await database.execute(query)

        if admin_id:
            print(f"[SUCCESS] 默认管理员账户创建成功!")
            print(f"   邮箱: {DEFAULT_ADMIN_EMAIL}")
            print(f"   密码: {DEFAULT_ADMIN_PASSWORD}")
            print(f"   用户ID: {admin_id}")
            print(f"   管理员权限: 是")

            # 标记邀请码为已使用
            if existing_invitation:
                await invitation_crud.mark_invitation_code_as_used(existing_invitation["id"], admin_id)
                print(f"[SUCCESS] 邀请码已标记为已使用")
        else:
            print("[ERROR] 创建管理员账户失败")

    except Exception as e:
        print(f"[ERROR] 创建默认管理员账户时出错: {e}")
        raise
    finally:
        # 断开数据库连接
        await database.disconnect()
        print("[SUCCESS] 数据库连接已断开")

async def check_admin_exists():
    """检查管理员账户是否存在"""
    try:
        await database.connect()
        existing_admin = await user_crud.get_user_by_email(DEFAULT_ADMIN_EMAIL)
        await database.disconnect()
        return existing_admin is not None
    except Exception as e:
        print(f"[ERROR] 检查管理员账户时出错: {e}")
        return False

def main():
    """主函数"""
    print("[INFO] 开始初始化默认管理员账户...")
    print(f"   目标邮箱: {DEFAULT_ADMIN_EMAIL}")
    print(f"   用户名: {DEFAULT_ADMIN_USERNAME}")
    print("=" * 50)

    try:
        # 运行异步函数
        asyncio.run(create_default_admin())
        print("=" * 50)
        print("[SUCCESS] 默认管理员账户初始化完成!")

    except Exception as e:
        print("=" * 50)
        print(f"[ERROR] 初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
