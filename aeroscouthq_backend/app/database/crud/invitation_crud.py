from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, insert

# Assuming 'database' is an instance of databases.Database configured elsewhere
from app.database.connection import database
from app.database.models import invitation_codes_table


async def get_invitation_code(code: str) -> Optional[dict]:
    """
    根据邀请码字符串查询有效（未使用）的邀请码。

    Args:
        code: 邀请码字符串。

    Returns:
        包含邀请码信息的字典，如果未找到或已使用则返回 None。
    """
    query = select(invitation_codes_table).where(
        invitation_codes_table.c.code == code,
        invitation_codes_table.c.is_used == False # Only fetch unused codes
    )
    result = await database.fetch_one(query)
    return result

async def mark_invitation_code_as_used(code_id: int, user_id: int):
    """
    将指定的邀请码标记为已使用。

    Args:
        code_id: 邀请码的 ID。
        user_id: 使用该邀请码注册的用户的 ID。
    """
    query = (
        update(invitation_codes_table)
        .where(invitation_codes_table.c.id == code_id)
        .values(
            is_used=True,
            used_by_user_id=user_id,
            used_at=datetime.now(timezone.utc) # Ensure timezone aware datetime
        )
    )
    await database.execute(query)

async def get_invitation_code_details(code: str) -> Optional[dict]:
    """
    获取邀请码的详细信息，无论其是否被使用。

    Args:
        code: 邀请码字符串。

    Returns:
        包含邀请码信息的字典，如果未找到则返回 None。
    """
    query = select(invitation_codes_table).where(invitation_codes_table.c.code == code)
    result = await database.fetch_one(query)
    return result
async def create_invitation_code(code: str, created_by: Optional[int] = None) -> int:
    """
    在数据库中创建新的邀请码。

    Args:
        code: 邀请码字符串。
        created_by: 创建该邀请码的用户 ID (可选)。

    Returns:
        新创建邀请码的 ID。
    """
    query = insert(invitation_codes_table).values(
        code=code,
        created_by_user_id=created_by,
        created_at=datetime.now(timezone.utc), # Ensure timezone aware datetime
        is_used=False # Default to not used
        # used_by_user_id and used_at are initially NULL
    )
    # The execute method for an insert typically returns the primary key of the new row
    last_record_id = await database.execute(query)
    if last_record_id is None:
         raise Exception("Failed to retrieve ID for newly created invitation code.")
    return last_record_id
async def ensure_invitation_code_is_usable(code: str, created_by: Optional[int] = None) -> dict:
    """
    Ensures an invitation code exists and is in a usable (not used) state.
    If it exists and is used, it will be reset.
    If it does not exist, it will be created.

    Args:
        code: The invitation code string.
        created_by: The user ID of the creator if the code needs to be created.

    Returns:
        The dictionary of the invitation code, ensured to be usable.
    """
    existing_code_details = await get_invitation_code_details(code)

    if existing_code_details:
        if existing_code_details["is_used"]:
            # Reset the code to be usable again
            reset_query = (
                update(invitation_codes_table)
                .where(invitation_codes_table.c.id == existing_code_details["id"])
                .values(
                    is_used=False,
                    used_by_user_id=None,
                    used_at=None
                )
            )
            await database.execute(reset_query)
            # Fetch the updated details
            return await get_invitation_code_details(code) # type: ignore
        return existing_code_details # Already exists and is usable
    else:
        # Create the code
        new_code_id = await create_invitation_code(code, created_by=created_by)
        # Fetch and return the newly created code details
        # It's guaranteed to be usable as create_invitation_code sets is_used=False
        return await get_invitation_code_details(code) # type: ignore

async def get_user_invitation_codes(user_id: int) -> list:
    """
    获取用户创建的所有邀请码。

    Args:
        user_id: 用户ID

    Returns:
        包含邀请码信息的字典列表
    """
    query = select(invitation_codes_table).where(
        invitation_codes_table.c.created_by_user_id == user_id
    )
    results = await database.fetch_all(query)
    return [dict(result) for result in results]