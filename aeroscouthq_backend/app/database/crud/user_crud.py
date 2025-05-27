from datetime import datetime, date, timezone, timedelta
from typing import Optional

from sqlalchemy import select, update, insert

# Assuming 'database' is an instance of databases.Database configured elsewhere
from app.database.connection import database
from app.database.models import users_table
# Import UserCreate for type hinting, actual creation logic might be in service layer
from app.apis.v1.schemas import UserCreate


async def get_user_by_email(email: str) -> Optional[dict]:
    """
    根据电子邮件地址查询用户。

    Args:
        email: 用户电子邮件地址。

    Returns:
        包含用户信息的字典，如果未找到则返回 None。
        注意：返回的是数据库行对象，可以像字典一样访问。
    """
    query = select(users_table).where(users_table.c.email == email)
    result = await database.fetch_one(query)
    return result

async def get_user_by_id(user_id: int) -> Optional[dict]:
    """
    根据用户 ID 查询用户。

    Args:
        user_id: 用户 ID。

    Returns:
        包含用户信息的字典，如果未找到则返回 None。
    """
    query = select(users_table).where(users_table.c.id == user_id)
    result = await database.fetch_one(query)
    return result

async def create_user(user_data: dict) -> int:
    """
    在数据库中创建新用户。

    Args:
        user_data: 包含用户信息的字典，至少需要 'username', 'email' 和 'hashed_password'。

    Returns:
        新创建用户的 ID。
    """
    query = insert(users_table).values(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=user_data["hashed_password"],
        created_at=datetime.now(timezone.utc), # Ensure timezone aware datetime
        is_active=True, # Default to active upon creation
        is_admin=False, # Default to non-admin user
        api_call_count_today=0,
        # last_login_at and last_api_call_date are initially NULL
    )
    print(f"插入用户数据: {query}")  # 添加日志以验证插入的数据
    # The execute method for an insert typically returns the primary key of the new row
    last_record_id = await database.execute(query)
    if last_record_id is None:
         # This case might happen if the DB driver doesn't support returning the ID directly
         # Or if the insert failed silently (less likely with proper error handling)
         # A fallback might be needed, e.g., query the user by email again, but that's less ideal.
         raise Exception("Failed to retrieve ID for newly created user.")
    return last_record_id


async def update_last_login(user_id: int):
    """
    更新用户的最后登录时间。

    Args:
        user_id: 用户 ID。
    """
    query = (
        update(users_table)
        .where(users_table.c.id == user_id)
        .values(last_login_at=datetime.now(timezone.utc)) # Ensure timezone aware datetime
    )
    await database.execute(query)

async def update_api_call_count(user_id: int, new_count: int, call_date: date):
    """
    更新用户的当日 API 调用次数和最后调用日期。

    Args:
        user_id: 用户 ID。
        new_count: 新的调用次数。
        call_date: API 调用的日期 (date object)。
    """
    # Convert date object to datetime object at the beginning of the day for storage
    # Assuming the database column `last_api_call_date` is a DATE or DATETIME type.
    # If it's DATE, the time component might be ignored by the DB.
    # If it's DATETIME/TIMESTAMP, storing just the date part might require care.
    # Storing as datetime at midnight UTC for consistency.
    call_datetime = datetime.combine(call_date, datetime.min.time(), tzinfo=timezone.utc)

    query = (
        update(users_table)
        .where(users_table.c.id == user_id)
        .values(
            api_call_count_today=new_count,
            last_api_call_date=call_datetime # Store the datetime representation
        )
    )
    await database.execute(query)
async def check_and_increment_api_call_count(user_id: int, max_calls: int) -> bool:
    """
    检查用户的 API 调用次数是否达到限制，如果未达到则增加计数。
    包含每日自动重置逻辑。

    Args:
        user_id: 用户 ID。
        max_calls: 用户每日允许的最大 API 调用次数。

    Returns:
        True 如果调用被允许且计数已增加，False 如果达到限制。

    Raises:
        Exception: 如果找不到用户。
    """
    async with database.transaction():
        # 1. 获取当前用户状态 (在一个事务中读取)
        query = select(
            users_table.c.api_call_count_today,
            users_table.c.last_api_call_date
        ).where(users_table.c.id == user_id)
        # Use `for_update=True` if the database backend and `databases` library support it
        # for stronger locking. Check `databases` documentation for specific backend support.
        # query = query.with_for_update() # Example if supported

        user_status = await database.fetch_one(query)

        if user_status is None:
            # 或者可以根据业务逻辑返回 False 或其他处理
            raise Exception(f"User with id {user_id} not found.")

        current_count = user_status["api_call_count_today"]
        last_call_date_stored = user_status["last_api_call_date"]

        # 2. 获取当前 UTC 日期
        # We only care about the date part for daily reset logic
        today_utc = datetime.now(timezone.utc).date()

        # 3. 检查是否需要重置计数
        reset_count = False
        if last_call_date_stored:
            # Ensure comparison is between date objects
            # If last_api_call_date is stored as DATETIME, convert it to date
            if isinstance(last_call_date_stored, datetime):
                last_call_date = last_call_date_stored.date()
            else: # Assuming it's already a date object
                last_call_date = last_call_date_stored

            if last_call_date < today_utc:
                current_count = 0 # 重置计数
                reset_count = True
        else:
            # 如果 last_api_call_date 为 NULL (例如新用户或首次调用)
            current_count = 0
            reset_count = True # Treat as needing reset/initialization

        # 4. 检查是否达到限额
        if current_count < max_calls:
            # 5. 如果未达到，增加计数并更新日期 (在一个事务中写入)
            new_count = current_count + 1
            # Store today's date (as datetime at midnight UTC for consistency if column is DATETIME)
            update_datetime = datetime.combine(today_utc, datetime.min.time(), tzinfo=timezone.utc)

            update_query = (
                update(users_table)
                .where(users_table.c.id == user_id)
                .values(
                    api_call_count_today=new_count,
                    last_api_call_date=update_datetime
                )
            )
            await database.execute(update_query)
            return True
        else:
            # 6. 如果已达到限额，不更新，返回 False
            # 如果是因为跨天重置而达到限额 (虽然不太可能，除非 max_calls=0)，
            # 确保日期仍然更新，以反映今天的检查。
            # 但当前逻辑是先检查后更新，所以如果 count >= max_calls，不会执行更新。
            # 如果需要即使超限也更新日期，需要调整逻辑。
            # 目前按需求：超限则不增加计数，也不（需要）更新日期。
            return False