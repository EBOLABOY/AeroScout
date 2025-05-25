from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码与哈希密码是否匹配。

    Args:
        plain_password: 明文密码。
        hashed_password: 哈希后的密码。

    Returns:
        如果密码匹配则返回 True，否则返回 False。
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    对明文密码进行哈希处理。

    Args:
        password: 明文密码。

    Returns:
        哈希后的密码字符串。
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT 访问令牌。

    Args:
        data: 要编码到令牌中的数据字典。
        expires_delta: 令牌的有效期。如果未提供，则使用默认配置。

    Returns:
        生成的 JWT 令牌字符串。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT 访问令牌。

    Args:
        token: JWT 令牌字符串。

    Returns:
        解码后的令牌数据字典，如果令牌无效或过期则返回 None。
    """
    try:
        # Note: The 'jwt' library used here is python-jose's jwt, not PyJWT
        # python-jose handles expiration check automatically during decode
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        # Handle expired token specifically if needed, though decode raises JWTError for it too
        print("Token has expired")
        return None
    except JWTError as e:
        # Handle generic JWT errors (invalid signature, invalid format, etc.)
        print(f"JWT Error: {e}")
        return None