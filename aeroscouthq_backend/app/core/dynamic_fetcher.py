import asyncio
import concurrent.futures
import json
import logging
import os
import platform
import time
import traceback
from typing import Optional, Dict, Any
from pathlib import Path
from functools import partial

from fastapi import HTTPException, status
import httpx

# HTTP-based fallback function for getting Trip.com headers
async def _fetch_trip_headers_http_fallback() -> Optional[Dict[str, str]]:
    """
    使用纯HTTP方法获取Trip.com的基础headers，不依赖浏览器自动化。
    这是一个简化的fallback方案。

    Returns:
        Dict[str, str]: 包含基础Trip.com headers的字典，如果失败则返回None
    """
    logger.info("开始使用HTTP方法获取Trip.com基础headers...")
    try:
        # 使用httpx发送请求获取基础cookies
        async with httpx.AsyncClient() as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            response = await client.get('https://hk.trip.com/flights/', headers=headers, timeout=30.0)

            if response.status_code == 200:
                # 构建基础headers
                cookies_str = "; ".join([f"{name}={value}" for name, value in response.cookies.items()])

                trip_headers = {
                    'cookie': cookies_str,
                    'user-agent': headers['User-Agent'],
                    'content-type': 'application/json',
                    'origin': 'https://hk.trip.com',
                    'referer': 'https://hk.trip.com/flights/',
                    'accept': '*/*',
                    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                    'sec-ch-ua': '"Chromium";v="125", "Microsoft Edge";v="125", "Not.A/Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'x-ibu-flt-currency': 'CNY',
                    'x-ibu-flt-language': 'hk',
                    'x-ibu-flt-locale': 'zh-HK'
                }

                logger.info("HTTP方法获取基础headers成功")
                return trip_headers
            else:
                logger.error(f"HTTP请求失败，状态码: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"HTTP方法获取headers失败: {e}", exc_info=True)
        return None

from app.core.config import settings
# Import Celery tasks moved into functions to avoid circular import

logger = logging.getLogger(__name__)
# --- Global State ---
TRIP_CURRENT_HEADERS: Optional[Dict[str, str]] = None
TRIP_LAST_FETCH_TIME: float = 0
TRIP_FETCH_LOCK = asyncio.Lock()

# Ensure the cache directory exists
Path(settings.TRIP_COOKIE_FILE).parent.mkdir(parents=True, exist_ok=True)

# Removed _fetch_new_trip_playwright_session_data as its logic is now in tasks.py

async def get_effective_trip_headers(force_refresh: bool = False) -> Dict[str, str]:
    """
    Gets effective Trip.com headers. Handles caching (memory-first, then file-first)
    and triggers background refresh via Celery only if both caches are invalid.

    Args:
        force_refresh: If True, bypasses cache checks and forces a background refresh task,
                       but still returns current cache if available.

    Returns:
        A dictionary containing Trip.com headers (potentially stale if refresh is in progress).

    Raises:
        HTTPException:
            - 503 Service Unavailable: If no headers are available (neither memory nor file cache is valid)
              and a background refresh has been triggered. Client should retry.
            - 500 Internal Server Error: For unexpected errors like failing to enqueue the task when needed.
    """
    global TRIP_CURRENT_HEADERS, TRIP_LAST_FETCH_TIME

    async with TRIP_FETCH_LOCK:
        now = time.time()
        headers_to_return: Optional[Dict[str, str]] = None
        memory_cache_valid = False
        file_cache_valid = False
        file_mod_time = 0
        expiry_seconds = settings.TRIP_COOKIE_EXPIRY_SECONDS
        cache_file_path = settings.TRIP_COOKIE_FILE

        # 1. Check in-memory cache (unless force_refresh)
        memory_expired = (now - TRIP_LAST_FETCH_TIME) > expiry_seconds
        if not force_refresh and TRIP_CURRENT_HEADERS and not memory_expired:
            memory_cache_valid = True
            headers_to_return = TRIP_CURRENT_HEADERS.copy()
            logger.info("Using valid in-memory Trip.com headers.")

        # 2. Check file cache if memory wasn't valid (unless force_refresh)
        if not headers_to_return and not force_refresh and os.path.exists(cache_file_path):
            try:
                file_mod_time = os.path.getmtime(cache_file_path)
                file_expired = (now - file_mod_time) > expiry_seconds
                if not file_expired:
                    with open(cache_file_path, 'r') as f:
                        cached_headers = json.load(f)
                        if isinstance(cached_headers, dict) and 'cookie' in cached_headers and 'user-agent' in cached_headers:
                            file_cache_valid = True
                            headers_to_return = cached_headers.copy() # Prepare to return file cache
                            logger.info(f"Found valid Trip.com headers in file cache: {cache_file_path}")
                        else:
                            logger.warning(f"Invalid format in Trip.com cookie cache file: {cache_file_path}.")
                else:
                    logger.info(f"Trip.com cookie cache file expired: {cache_file_path}")
            except Exception as e:
                logger.warning(f"Error reading Trip.com cookie cache file {cache_file_path}: {e}.")

        # 3. Determine if a background refresh task is needed
        # Needed if forced OR if neither memory nor file cache was valid.
        needs_background_refresh = force_refresh or not (memory_cache_valid or file_cache_valid)
        task_triggered = False

        # 4. Trigger task if needed
        if needs_background_refresh:
            logger.info(f"Triggering background fetch for Trip.com headers (Force: {force_refresh}, No Valid Cache: {not (memory_cache_valid or file_cache_valid)}).")
            task_triggered = False

            # Try to enqueue the async task
            try:
                from app.core.tasks import fetch_trip_session_task # Delayed import
                fetch_trip_session_task.delay()
                task_triggered = True
                logger.info("Successfully enqueued fetch_trip_session_task.")
            except Exception as e_async:
                logger.error(f"Failed to enqueue fetch_trip_session_task: {e_async}", exc_info=True)

                # If task enqueue fails AND we have no headers to return, try direct HTTP fetch
                if not headers_to_return:
                    logger.warning("No valid headers and task enqueue failed. Attempting direct HTTP fetch...")
                    try:
                        # 使用HTTP fallback方法
                        logger.info("尝试使用HTTP fallback方法...")
                        direct_headers = await _fetch_trip_headers_http_fallback()
                        if direct_headers and 'cookie' in direct_headers and 'user-agent' in direct_headers:
                            logger.info("HTTP fallback获取成功。使用这些headers。")
                            headers_to_return = direct_headers.copy()
                            TRIP_CURRENT_HEADERS = direct_headers.copy()
                            TRIP_LAST_FETCH_TIME = time.time()
                            task_triggered = True  # 防止503错误

                            # 保存到文件
                            try:
                                with open(settings.TRIP_COOKIE_FILE, 'w') as f:
                                    json.dump(direct_headers, f, indent=2)
                                logger.info(f"HTTP fallback结果保存到文件: {settings.TRIP_COOKIE_FILE}")
                            except Exception as e:
                                logger.error(f"保存到文件失败: {e}")
                        else:
                            logger.error("HTTP fallback failed to get valid headers.")
                            raise HTTPException(
                                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail="Trip.com session data is unavailable. HTTP fallback failed."
                            )
                    except Exception as e_direct:
                        logger.error(f"HTTP fallback failed: {e_direct}", exc_info=True)
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Trip.com session data is unavailable. All fetch methods failed."
                        )

        # 5. Decide what to return or raise
        if headers_to_return:
            # If we loaded from file, update memory cache now
            if file_cache_valid and not memory_cache_valid:
                TRIP_CURRENT_HEADERS = headers_to_return.copy() # Use the copy we made
                TRIP_LAST_FETCH_TIME = file_mod_time
                logger.info("Updated in-memory Trip.com cache from file.")

            if task_triggered: # Log if we are returning stale data while refresh runs
                 logger.warning("Returning potentially stale Trip.com headers while background refresh is running.")
            return headers_to_return
        else:
            # No valid cache found (memory or file).
            # Background task should have been triggered (or failed to trigger).
            logger.error("No valid Trip.com headers available. Background refresh initiated (or failed).")

            # Last resort - try HTTP fallback inline
            try:
                logger.warning("Attempting last-resort HTTP fallback for Trip.com headers...")
                direct_headers = await _fetch_trip_headers_http_fallback()
                if direct_headers and 'cookie' in direct_headers and 'user-agent' in direct_headers:
                    logger.info("HTTP fallback获取成功")
                    # 更新内存缓存
                    TRIP_CURRENT_HEADERS = direct_headers.copy()
                    TRIP_LAST_FETCH_TIME = time.time()

                    # 保存到文件
                    try:
                        with open(settings.TRIP_COOKIE_FILE, 'w') as f:
                            json.dump(direct_headers, f, indent=2)
                        logger.info(f"HTTP fallback结果保存到文件: {settings.TRIP_COOKIE_FILE}")
                    except Exception as e:
                        logger.error(f"保存到文件失败: {e}")

                    return direct_headers
                else:
                    logger.error("HTTP fallback failed to get valid headers")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Trip.com session data is unavailable or being refreshed. Please try again shortly."
                    )
            except Exception as e_last:
                logger.error(f"HTTP fallback failed: {e_last}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Trip.com session data is unavailable or being refreshed. Please try again shortly."
                )

async def load_initial_trip_cookies():
    """
    Attempts to load Trip.com cookies from the cache file into memory on application startup.
    Does not trigger a fetch if the file is invalid or expired.
    """
    global TRIP_CURRENT_HEADERS, TRIP_LAST_FETCH_TIME
    logger.info(f"Attempting to load initial Trip.com cookies from {settings.TRIP_COOKIE_FILE}...")
    if os.path.exists(settings.TRIP_COOKIE_FILE):
        try:
            now = time.time()
            file_mod_time = os.path.getmtime(settings.TRIP_COOKIE_FILE)
            if (now - file_mod_time) <= settings.TRIP_COOKIE_EXPIRY_SECONDS:
                with open(settings.TRIP_COOKIE_FILE, 'r') as f:
                    cached_headers = json.load(f)
                    if isinstance(cached_headers, dict) and 'cookie' in cached_headers and 'user-agent' in cached_headers:
                        # Only load if memory is empty or file is newer
                        if not TRIP_CURRENT_HEADERS or file_mod_time > TRIP_LAST_FETCH_TIME:
                            TRIP_CURRENT_HEADERS = cached_headers
                            TRIP_LAST_FETCH_TIME = file_mod_time
                            logger.info("Successfully loaded initial Trip.com headers from valid cache file into memory.")
                        else:
                            logger.info("In-memory Trip.com headers are already present and up-to-date.")
                    else:
                        logger.warning("Initial Trip.com cookie cache file has invalid format. Skipping load.")
            else:
                logger.info("Initial Trip.com cookie cache file found but expired. Skipping load.")
        except Exception as e:
            logger.warning(f"Error loading initial Trip.com cookie cache file: {e}. Skipping load.")
    else:
        logger.info("No initial Trip.com cookie cache file found. Headers will be fetched by the first request if needed.")

# --- Application Startup Integration ---
# Ensure load_initial_trip_cookies and load_initial_kiwi_token are called
# during application startup (e.g., in main.py lifespan).
# Example (in main.py):
# from contextlib import asynccontextmanager
# from app.core.dynamic_fetcher import load_initial_trip_cookies, load_initial_kiwi_token
#
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Connect to DB, etc.
#     await load_initial_trip_cookies()
#     await load_initial_kiwi_token()
#     yield
#     # Disconnect DB, etc.
#
# app = FastAPI(lifespan=lifespan)
# --- Global State for Kiwi.com ---
KIWI_CURRENT_HEADERS: Optional[Dict[str, str]] = None
KIWI_LAST_FETCH_TIME: float = 0
KIWI_FETCH_LOCK = asyncio.Lock()

# Ensure the Kiwi cache directory exists (assuming settings.KIWI_TOKEN_FILE is defined)
# This should ideally be done once, maybe near the Trip.com check or in startup
try:
    Path(settings.KIWI_TOKEN_FILE).parent.mkdir(parents=True, exist_ok=True)
except AttributeError:
    logger.error("settings.KIWI_TOKEN_FILE is not defined in config.py!")
except Exception as e:
    logger.error(f"Error creating directory for KIWI_TOKEN_FILE: {e}")


# --- Kiwi.com Functions ---

# Removed _fetch_new_kiwi_playwright_session_data as its logic is now in tasks.py

async def get_effective_kiwi_headers(force_refresh: bool = False) -> Dict[str, str]:
    """
    获取有效的 Kiwi.com headers

    新的简化策略：
    1. 优先使用预获取的缓存（内存或文件）
    2. 只在缓存完全无效时才触发立即获取
    3. 依赖 token 调度器进行定期刷新，避免请求时延迟

    Args:
        force_refresh: 如果为 True，强制立即获取新 token

    Returns:
        包含 Kiwi.com headers 的字典

    Raises:
        HTTPException: 如果无法获取有效 headers
    """
    global KIWI_CURRENT_HEADERS, KIWI_LAST_FETCH_TIME

    # 检查配置
    try:
        expiry_seconds = settings.KIWI_COOKIE_EXPIRY_SECONDS
        cache_file_path = settings.KIWI_TOKEN_FILE
    except AttributeError as e:
        logger.critical(f"Missing required Kiwi settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {e}"
        )

    async with KIWI_FETCH_LOCK:
        now = time.time()

        # 1. 检查内存缓存（最快）
        memory_expired = (now - KIWI_LAST_FETCH_TIME) > expiry_seconds
        if not force_refresh and KIWI_CURRENT_HEADERS and not memory_expired:
            logger.info("使用有效的内存 Kiwi headers")
            return KIWI_CURRENT_HEADERS.copy()

        # 2. 检查文件缓存
        if not force_refresh and os.path.exists(cache_file_path):
            try:
                file_mod_time = os.path.getmtime(cache_file_path)
                file_expired = (now - file_mod_time) > expiry_seconds
                if not file_expired:
                    with open(cache_file_path, 'r') as f:
                        cached_headers = json.load(f)
                        if isinstance(cached_headers, dict) and 'kw-umbrella-token' in cached_headers:
                            # 更新内存缓存
                            KIWI_CURRENT_HEADERS = cached_headers.copy()
                            KIWI_LAST_FETCH_TIME = file_mod_time
                            logger.info("从文件缓存加载有效的 Kiwi headers")
                            return cached_headers.copy()
            except Exception as e:
                logger.warning(f"读取 Kiwi 缓存文件失败: {e}")

        # 3. 缓存无效或强制刷新，立即获取
        logger.warning("Kiwi 缓存无效或被强制刷新，开始立即获取...")
        try:
            fresh_headers = await _get_fresh_kiwi_headers_sync()
            if fresh_headers and 'kw-umbrella-token' in fresh_headers:
                # 更新内存缓存
                KIWI_CURRENT_HEADERS = fresh_headers.copy()
                KIWI_LAST_FETCH_TIME = time.time()

                # 保存到文件缓存
                try:
                    with open(cache_file_path, 'w') as f:
                        json.dump(fresh_headers, f, indent=2)
                    logger.info("立即获取 Kiwi headers 成功，已更新缓存")
                except Exception as e:
                    logger.warning(f"保存 Kiwi 缓存失败: {e}")

                return fresh_headers
            else:
                logger.error("立即获取 Kiwi headers 失败")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Unable to obtain fresh Kiwi.com session data"
                )
        except Exception as e:
            logger.error(f"立即获取 Kiwi headers 异常: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Kiwi.com session data temporarily unavailable"
            )

async def load_initial_kiwi_token():
    """
    Attempts to load Kiwi.com token/headers from the cache file into memory on application startup.
    Does not trigger a fetch if the file is invalid or expired.
    """
    global KIWI_CURRENT_HEADERS, KIWI_LAST_FETCH_TIME
    logger.info(f"Attempting to load initial Kiwi.com token from settings.KIWI_TOKEN_FILE...")

    try:
        token_file = settings.KIWI_TOKEN_FILE
        expiry_seconds = settings.KIWI_COOKIE_EXPIRY_SECONDS
    except AttributeError as e:
        logger.error(f"Missing required Kiwi settings for initial load: {e}. Cannot load initial token.")
        return # Cannot proceed without settings

    if os.path.exists(token_file):
        try:
            now = time.time()
            file_mod_time = os.path.getmtime(token_file)
            if (now - file_mod_time) <= expiry_seconds:
                with open(token_file, 'r') as f:
                    cached_headers = json.load(f)
                    if isinstance(cached_headers, dict) and 'kw-umbrella-token' in cached_headers:
                         # Only load if memory is empty or file is newer
                        if not KIWI_CURRENT_HEADERS or file_mod_time > KIWI_LAST_FETCH_TIME:
                            KIWI_CURRENT_HEADERS = cached_headers
                            KIWI_LAST_FETCH_TIME = file_mod_time
                            logger.info("Successfully loaded initial Kiwi.com headers from valid cache file into memory.")
                        else:
                            logger.info("In-memory Kiwi.com headers are already present and up-to-date.")
                    else:
                        logger.warning("Initial Kiwi.com token cache file has invalid format. Skipping load.")
            else:
                logger.info("Initial Kiwi.com token cache file found but expired. Skipping load.")
        except Exception as e:
            logger.warning(f"Error loading initial Kiwi.com token cache file: {e}. Skipping load.")
    else:
        logger.info("No initial Kiwi.com token cache file found. Headers will be fetched by the first request if needed.")

# --- 同步 Kiwi Token 获取（基于工作代码的降级方案）---

async def _get_fresh_kiwi_headers_sync() -> Optional[Dict[str, str]]:
    """
    获取新鲜的 Kiwi headers，使用固定token策略
    """
    logger.info("开始获取 Kiwi headers（固定token策略）...")

    # 使用固定token策略
    logger.info("使用固定token策略...")
    try:
        # 提供一个固定的fallback headers
        fallback_headers = {
            'content-type': 'application/json',
            'kw-skypicker-visitor-uniqid': 'b500f05c-8234-4a94-82a7-fb5dc02340a9',
            'kw-umbrella-token': '0d23674b463dadee841cc65da51e34fe47bbbe895ae13b69d42ece267c7a2f51',
            'kw-x-rand-id': '07d338ea',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
            'origin': 'https://www.kiwi.com',
            'referer': 'https://www.kiwi.com/cn/search/tiles/--/--/anytime/anytime'
        }

        # 简单验证token是否有效（通过发送测试请求）
        try:
            async with httpx.AsyncClient() as client:
                test_payload = {
                    "query": "query { __typename }",
                    "variables": {}
                }
                response = await client.post(
                    "https://api.skypicker.com/umbrella/v2/graphql",
                    headers=fallback_headers,
                    json=test_payload,
                    timeout=10.0
                )

                if response.status_code == 200:
                    logger.info("固定token验证有效")
                    return fallback_headers
                else:
                    logger.warning(f"固定token验证失败，状态码: {response.status_code}")
        except Exception as e:
            logger.warning(f"固定token验证请求失败: {e}")

    except Exception as e:
        logger.warning(f"固定token验证失败: {e}")

    logger.error("Kiwi token获取失败")
    return None