import json
from typing import List, Optional, Union # Use list directly in Python 3.9+
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    # Configure Pydantic settings behavior
    model_config = SettingsConfigDict(
        env_file='.env',              # Specify the .env file to load
        env_file_encoding='utf-8',    # Specify encoding for the .env file
        extra='ignore'                # Ignore extra fields loaded from the environment
    )

    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./aeroscout.db"

    # JWT Configuration
    SECRET_KEY: str = "your_secret_key_here_please_change_me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API Usage Limits - Specific limits per type
    POI_DAILY_LIMIT: int = 10 # Default daily limit for POI endpoints
    FLIGHT_DAILY_LIMIT: int = 5 # Default daily limit for flight search endpoints

    # Dynamic Fetcher Cache File Paths
    TRIP_COOKIE_FILE: str = "trip_cookies.json"
    KIWI_TOKEN_FILE: str = "kiwi_token.json"

    # Celery Configuration
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Redis Configuration for Search Sessions
    REDIS_URL: str = "redis://localhost:6379/2"  # 使用数据库2存储搜索会话
    REDIS_SESSION_TTL: int = 3600  # 搜索会话过期时间（秒），默认1小时

    # Hub Probing Configuration
    # Default value is an empty list if the env var is not set or empty
    CHINA_HUB_CITIES_FOR_PROBE: List[str] = []

    # 甩尾票探测目的地列表 - 默认包含一些亚洲主要城市
    THROWAWAY_DESTINATIONS: List[str] = ["HKG", "TPE", "ICN", "NRT", "MNL", "SIN", "BKK", "KUL"]

    # 代理配置 - 用于绕过反爬虫限制
    HTTP_PROXY: Optional[str] = None  # 例如: "http://proxy.example.com:8080"
    HTTPS_PROXY: Optional[str] = None  # 例如: "http://proxy.example.com:8080"

    # User-Agent轮换池 - 用于请求头伪装
    USER_AGENT_POOL: List[str] = [
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",

        # Chrome macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",

        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",

        # Firefox Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",

        # Safari macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ]

    @field_validator('CHINA_HUB_CITIES_FOR_PROBE', 'THROWAWAY_DESTINATIONS', mode='before')
    @classmethod
    def parse_json_string_list(cls, value: Optional[Union[str, List[str]]], info) -> List[str]:
        """Parses a JSON string list from env var into a Python list."""
        field_name = info.field_name
        if isinstance(value, list):
            return value # Already a list (e.g., when set directly in code)
        if not value: # Handles None or empty string from env var
            return []
        try:
            parsed_list = json.loads(value)
            if not isinstance(parsed_list, list):
                raise ValueError(f"{field_name} must be a JSON list string")
            # Ensure all elements are strings, though Pydantic would likely validate this later too
            if not all(isinstance(item, str) for item in parsed_list):
                raise ValueError(f"All items in {field_name} list must be strings")
            return parsed_list
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON string provided for {field_name}")
        except Exception as e:
            # Catch potential issues during validation or type checking
            raise ValueError(f"Error parsing {field_name}: {e}")

    # Cookie Expiry Configuration
    TRIP_COOKIE_EXPIRY_SECONDS: int = 3600 # Default 1 hour
    KIWI_COOKIE_EXPIRY_SECONDS: int = 3600 # Default 1 hour

    # Kiwi 任务状态管理配置
    KIWI_TASK_STATUS_FILE: str = "cache/.kiwi_task_status.json"  # 任务状态文件路径
    KIWI_TASK_WAIT_TIMEOUT: int = 45  # 智能等待的最大超时时间（秒）
    KIWI_TASK_CHECK_INTERVAL: int = 2  # 状态检查间隔（秒）
    KIWI_TASK_STATUS_EXPIRY: int = 300  # 状态文件过期时间（秒）

    # Testing Flag
    # Controls specific behaviors during testing, e.g., database transactions
    TESTING: bool = False

    # 日志配置
    LOG_LEVEL: str = "WARNING"  # 默认日志级别，可选: DEBUG, INFO, WARNING, ERROR, CRITICAL
    ENABLE_SEARCH_DEBUG_LOGS: bool = False  # 是否启用搜索过程的详细调试日志

# Create a single, reusable instance of the Settings class
settings = Settings()

# Example usage (can be removed or kept for debugging):
# if __name__ == "__main__":
#     print("Loaded Settings:")
#     print(f"  Database URL: {settings.DATABASE_URL}")
#     print(f"  Secret Key: {'*' * 8}") # Avoid printing sensitive keys
#     print(f"  Hub Cities: {settings.CHINA_HUB_CITIES_FOR_PROBE}")
#     print(f"  Testing Mode: {settings.TESTING}")