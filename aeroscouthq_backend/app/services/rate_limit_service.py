import datetime
import logging

from fastapi import HTTPException, status

# Assuming user_crud exists and has the update_api_call_count function
from app.database.crud import user_crud
from app.apis.v1.schemas import UserResponse # Assuming UserResponse schema includes id, api_call_count_today, last_api_call_date
from app.core.config import settings

logger = logging.getLogger(__name__)

async def check_and_update_limit(user: UserResponse, limit_type: str, max_calls: int):
    """
    Checks if the user has exceeded their daily API call limit for a specific type,
    using the provided max_calls, and updates the count if the limit is not reached.

    Args:
        user: The user object (schema) containing current limit info.
        limit_type: The type of limit being checked (e.g., "poi", "flight").
        max_calls: The maximum number of calls allowed for this limit_type.

    Returns:
        None. Raises HTTPException if the limit is exceeded.

    Raises:
        HTTPException: With status 429 if the limit is exceeded.

    Implementation Notes:
        - Current Approach: Relies on checking the date and updating the count in the database
          during each request. This is generally acceptable for SQLite and moderate concurrency.
        - Concurrency Issue (Race Condition): In high-concurrency scenarios, multiple requests
          might simultaneously read the *same* old count before any single request can write
          the updated count back to the database. This could lead to exceeding the intended limit.
          Example: Limit is 10, current count is 9. Two requests arrive almost simultaneously.
          Both read 9. Both increment to 10 and update. The user effectively made 11 calls.
        - Future Improvements (Higher Concurrency / PostgreSQL):
            - Atomic Updates: Use database features like `UPDATE ... SET count = count + 1 WHERE ...`
              or SELECT FOR UPDATE (row locking) if using PostgreSQL to ensure atomic operations.
            - Distributed Cache/Counter: Employ solutions like Redis with atomic increments (`INCR`)
              for highly scalable and performant rate limiting, decoupling it from the main DB.
        - Daily Reset Logic: The count reset currently happens *reactively* when a user makes
          their first request on a new day. If a user doesn't make any requests for several days,
          their count remains unchanged until their next interaction.
        - Proactive Daily Reset (Alternative): A more robust approach involves a scheduled task
          (e.g., using Celery Beat, APScheduler, or an external cron job) that runs daily at
          midnight (UTC or server time) to explicitly reset `api_call_count_today` to 0 and
          update `last_api_call_date` for all relevant users. This is outside the current scope.
    """
    today = datetime.date.today()
    user_last_call_date = user.last_api_call_date
    current_count = user.api_call_count_today

    # Reset count if the last call was not today
    if user_last_call_date != today:
        logger.info(f"User {user.id}: First API call ({limit_type}) today. Resetting count.")
        current_count = 0
    else:
        logger.debug(f"User {user.id}: API call count today ({limit_type}): {current_count}")


    # Check against the limit
    # Using >= because if count is already AT the limit, the *next* call is disallowed.
    if current_count >= max_calls:
        logger.warning(f"User {user.id}: API call limit ({max_calls}) exceeded for {limit_type}.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"API call limit exceeded for today for '{limit_type}'. Limit: {max_calls} calls."
        )

    # Limit not reached, update the count and date in the database
    new_count = current_count + 1
    try:
        # Ensure the CRUD function exists and accepts these parameters
        await user_crud.update_api_call_count(
            user_id=user.id,
            new_count=new_count,
            call_date=today
        )
        logger.info(f"User {user.id}: API call ({limit_type}) allowed. New count: {new_count}")
        # No return needed as the function now only raises exceptions on failure/limit exceeded
    except Exception as e:
        # Log the error and potentially re-raise or handle differently
        logger.error(f"User {user.id}: Failed to update API call count for {limit_type}: {e}")
        # Depending on policy, you might still allow the call but log the failure,
        # or deny the call by raising an exception. Raising 500 seems appropriate here.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update API usage count."
        )