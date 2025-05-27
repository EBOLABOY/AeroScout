from typing import Optional
import logging

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt # Assuming jwt is needed for decode

from app.core.security import decode_access_token # Assuming this handles decoding
from app.database.crud import user_crud
from app.apis.v1.schemas import UserResponse, TokenData
from app.core.config import settings # Import settings
from app.services import rate_limit_service
# Define the OAuth2 scheme, pointing to the login endpoint
# Ensure the tokenUrl matches your actual login route
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
# 获取一个 logger 实例
logger = logging.getLogger(__name__)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Decodes the JWT token, validates it, and retrieves the user from the database.
    Returns the user data as a dictionary or None if validation fails.
    """
    try:
        # 解码访问令牌
        payload: Optional[dict] = decode_access_token(token)

        if payload is None:
            logger.error(
                "decode_access_token returned None. Token might be invalid, expired, missing, or malformed."
            )
            raise credentials_exception

        # 从 payload 中获取用户邮箱
        email: str = payload.get("sub")
        if email is None:
            logger.error("Email ('sub') not found in token payload.")
            raise credentials_exception

        # 创建 token_data 对象
        token_data = TokenData(email=email)

    except JWTError:
        logger.error("JWTError occurred during token decoding.", exc_info=True)
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}", exc_info=True)
        raise credentials_exception

    # 从数据库获取用户信息
    user = await user_crud.get_user_by_email(email=token_data.email)
    if user is None:
        logger.error(f"User not found in database: {token_data.email}")
        raise credentials_exception

    # 将用户信息转换为字典格式
    return dict(user)


async def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    可选的用户认证函数，如果没有token或token无效，返回None而不是抛出异常
    """
    if not authorization:
        return None

    # 提取Bearer token
    if not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")
    if not token:
        return None

    try:
        # 解码访问令牌
        payload: Optional[dict] = decode_access_token(token)

        if payload is None:
            logger.warning("decode_access_token returned None for optional auth")
            return None

        # 从 payload 中获取用户邮箱
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Email ('sub') not found in token payload for optional auth")
            return None

        # 创建 token_data 对象
        token_data = TokenData(email=email)

        # 从数据库获取用户信息
        user = await user_crud.get_user_by_email(email=token_data.email)
        if user is None:
            logger.warning(f"User not found in database for optional auth: {token_data.email}")
            return None

        # 将用户信息转换为字典格式
        return dict(user)

    except JWTError:
        logger.warning("JWTError occurred during optional token decoding")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error during optional token validation: {e}")
        return None


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Checks if the user retrieved by get_current_user is active.
    Raises an exception if the user is inactive.
    Returns the user data as a UserResponse Pydantic model.
    """
    # The Depends(get_current_user) already handles the case where the user
    # couldn't be authenticated (it would raise credentials_exception).
    # So, current_user here should be a valid user dict.
    if not current_user: # Defensive check, though Depends should handle it
         raise credentials_exception # Or perhaps a different error?

    # Check if the user is active
    # Ensure the key 'is_active' exists in the dict returned by get_current_user
    if not current_user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Convert the dictionary to the UserResponse Pydantic model
    # This assumes the dictionary structure matches the UserResponse fields
    return UserResponse.model_validate(current_user)

async def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """
    Checks if the user retrieved by get_current_user is an admin.
    Raises an exception if the user is not an admin.
    Returns the user data as a UserResponse Pydantic model.
    """
    if not current_user: # Defensive check
        raise credentials_exception

    # Check if the user is active first (optional, but good practice)
    if not current_user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Check if the user is an admin
    # Ensure the key 'is_admin' exists in the dict returned by get_current_user
    if not current_user.get("is_admin"): # Assuming 'is_admin' is the field name
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have admin privileges"
        )

    return UserResponse.model_validate(current_user)

class RateLimiter:
    """
    Dependency class to enforce API rate limiting based on daily call counts.
    Fetches the limit from settings based on limit_type and uses rate_limit_service.
    """
    def __init__(self, limit_type: str):
        self.limit_type = limit_type
        # Dynamically get the limit from settings based on limit_type
        # Example: if limit_type is 'poi', it looks for settings.POI_DAILY_LIMIT
        # Falls back to a default if the specific limit isn't defined (optional, adjust as needed)
        default_limit = getattr(settings, "DEFAULT_API_CALL_LIMIT", 15) # Provide a fallback default
        self.daily_limit = getattr(settings, f"{limit_type.upper()}_DAILY_LIMIT", default_limit)

    async def __call__(self, current_user: UserResponse = Depends(get_current_active_user)):
        """
        Checks the user's API call count against the specific limit using rate_limit_service.
        管理员用户不受限制。

        Args:
            current_user: The currently authenticated and active user.

        Raises:
            HTTPException(429): If the rate limit is exceeded.
        """
        # 管理员用户不受API调用限制
        if current_user.is_admin:
            return

        # Call the rate limit service, passing the dynamically determined limit
        await rate_limit_service.check_and_update_limit(
            user=current_user,
            limit_type=self.limit_type,
            max_calls=self.daily_limit # Pass the limit fetched during initialization
        )
        # The service itself will raise HTTPException(429) if the limit is exceeded.
        # No need to check 'allowed' or raise exception here.