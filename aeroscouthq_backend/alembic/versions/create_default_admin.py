"""create default admin user

Revision ID: create_default_admin
Revises: 0001_create_initial_database_schema
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'create_default_admin'
down_revision: Union[str, None] = 'c47909388e6b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 默认管理员信息
DEFAULT_ADMIN_EMAIL = "1242772513@qq.com"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD_HASH = "$2b$12$aASEXfmo0jISIXqWfYE1Reu6I6N9/bZJsVXx/jTa0Fc.tvQgVDxMu"  # 1242772513的bcrypt哈希
INVITATION_CODE = "ADMIN_INIT_CODE"

def upgrade() -> None:
    """创建默认管理员账户"""

    # 获取数据库连接
    connection = op.get_bind()

    try:
        # 1. 检查管理员是否已存在
        result = connection.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": DEFAULT_ADMIN_EMAIL}
        ).fetchone()

        if result:
            print(f"管理员账户 {DEFAULT_ADMIN_EMAIL} 已存在，跳过创建")
            return

        # 2. 创建邀请码（如果不存在）
        invitation_result = connection.execute(
            text("SELECT id FROM invitation_codes WHERE code = :code"),
            {"code": INVITATION_CODE}
        ).fetchone()

        invitation_id = None
        if not invitation_result:
            # 创建邀请码
            invitation_id = connection.execute(
                text("""
                    INSERT INTO invitation_codes (code, is_used, created_at)
                    VALUES (:code, :is_used, :created_at)
                """),
                {
                    "code": INVITATION_CODE,
                    "is_used": False,
                    "created_at": datetime.now(timezone.utc)
                }
            ).lastrowid
            print(f"创建邀请码: {INVITATION_CODE}")
        else:
            invitation_id = invitation_result[0]

        # 3. 创建管理员用户
        admin_id = connection.execute(
            text("""
                INSERT INTO users (
                    username, email, hashed_password, is_admin, is_active,
                    created_at, api_call_count_today
                ) VALUES (
                    :username, :email, :hashed_password, :is_admin, :is_active,
                    :created_at, :api_call_count_today
                )
            """),
            {
                "username": DEFAULT_ADMIN_USERNAME,
                "email": DEFAULT_ADMIN_EMAIL,
                "hashed_password": DEFAULT_ADMIN_PASSWORD_HASH,
                "is_admin": True,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "api_call_count_today": 0
            }
        ).lastrowid

        # 4. 标记邀请码为已使用
        if invitation_id and admin_id:
            connection.execute(
                text("""
                    UPDATE invitation_codes
                    SET is_used = :is_used, used_at = :used_at, used_by_user_id = :user_id
                    WHERE id = :invitation_id
                """),
                {
                    "is_used": True,
                    "used_at": datetime.now(timezone.utc),
                    "user_id": admin_id,
                    "invitation_id": invitation_id
                }
            )

        print(f"[SUCCESS] 默认管理员账户创建成功!")
        print(f"   邮箱: {DEFAULT_ADMIN_EMAIL}")
        print(f"   用户名: {DEFAULT_ADMIN_USERNAME}")
        print(f"   密码: 1242772513")
        print(f"   用户ID: {admin_id}")
        print(f"   管理员权限: 是")

    except Exception as e:
        print(f"[ERROR] 创建默认管理员账户失败: {e}")
        raise


def downgrade() -> None:
    """删除默认管理员账户"""

    connection = op.get_bind()

    try:
        # 删除管理员用户
        connection.execute(
            text("DELETE FROM users WHERE email = :email"),
            {"email": DEFAULT_ADMIN_EMAIL}
        )

        # 删除邀请码
        connection.execute(
            text("DELETE FROM invitation_codes WHERE code = :code"),
            {"code": INVITATION_CODE}
        )

        print(f"[SUCCESS] 默认管理员账户已删除: {DEFAULT_ADMIN_EMAIL}")

    except Exception as e:
        print(f"[ERROR] 删除默认管理员账户失败: {e}")
        raise
