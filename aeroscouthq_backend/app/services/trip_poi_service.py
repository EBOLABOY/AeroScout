import json
import logging
from typing import Optional, Dict, Any

import httpx
from fastapi import HTTPException, status

from app.core import dynamic_fetcher
from app.core.config import settings
from app.database.crud import poi_crud
from app.apis.v1.schemas import UserResponse # Assuming POI schemas might be needed later



logger = logging.getLogger(__name__)

# Constants from 机场信息查询.py (adapted for async context)
POI_SEARCH_OPERATION_NAME = "poiSearch"
POI_SEARCH_SHA256HASH = "f02b0e5250b9089a56498b8a3e4332b9962c9d65c2364e0ee4cf28dcff38cc8b"
TRIP_POI_API_URL = "https://hk.trip.com/flights/graphql/poiSearch"

# Special value to indicate header refresh needed
HEADER_REFRESH_REQUIRED = object()

async def _call_trip_poi_api(search_key: str, trip_type: str, mode: str, headers: dict) -> Optional[Dict[str, Any]] | object:
    """
    Calls the Trip.com POI Search GraphQL API asynchronously.

    Args:
        search_key: The search term for the POI.
        trip_type: Trip type (e.g., "RT", "OW").
        mode: Search mode (e.g., "0").
        headers: The request headers obtained from dynamic_fetcher.

    Returns:
        The parsed JSON response data (poiSearch part) on success.
        HEADER_REFRESH_REQUIRED if an authentication error (401/403) occurs.
        None if the request fails for other reasons or the response is invalid.
    """
    # 确保 mode 值为 API 期望的值
    if mode == "dep":
        logger.info("将 mode 从 'dep' 转换为 '0'，以匹配 Trip.com API 的要求")
        mode = "0"
    elif mode == "arr":
        logger.info("将 mode 从 'arr' 转换为 '1'，以匹配 Trip.com API 的要求")
        mode = "1"
    elif mode not in ["0", "1"]:
        logger.warning(f"未知的 mode 值: {mode}，默认使用 '0'")
        mode = "0"

    # 确保 trip_type 值为 API 期望的值
    if trip_type == "flight":
        logger.info("将 trip_type 从 'flight' 转换为 'RT'，以匹配 Trip.com API 的要求")
        trip_type = "RT"
    elif trip_type == "oneway":
        logger.info("将 trip_type 从 'oneway' 转换为 'OW'，以匹配 Trip.com API 的要求")
        trip_type = "OW"
    elif trip_type not in ["RT", "OW"]:
        logger.warning(f"未知的 trip_type 值: {trip_type}，默认使用 'RT'")
        trip_type = "RT"

    # 使用正确的 GraphQL 格式和参数值 - 恢复为与原始代码一致的格式
    payload = {
        "operationName": POI_SEARCH_OPERATION_NAME,
        "variables": {
            "key": search_key,
            "mode": mode,           # 现在使用正确的 mode 值
            "tripType": trip_type,  # 现在使用正确的 trip_type 值
            "Head": {}              # 恢复为空对象，与原始实现一致
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": POI_SEARCH_SHA256HASH
            }
        }
    }

    # 添加详细的调试日志
    logger.debug(f"构造的 Trip.com GraphQL 请求: {json.dumps(payload)}")
    logger.debug(f"使用的请求头: {json.dumps({k: v for k, v in headers.items() if k != 'cookie'})}")
    logger.debug(f"Cookie长度: {len(headers.get('cookie', ''))}")

    # 配置代理
    proxies = {}
    if settings.HTTP_PROXY:
        proxies["http://"] = settings.HTTP_PROXY
    if settings.HTTPS_PROXY:
        proxies["https://"] = settings.HTTPS_PROXY

    client_kwargs = {"timeout": 20.0}
    if proxies:
        client_kwargs["proxies"] = proxies
        logger.info(f"Using proxy for Trip.com API: {proxies}")

    async with httpx.AsyncClient(**client_kwargs) as client:
        try:
            logger.debug(f"Calling Trip.com POI API: URL={TRIP_POI_API_URL}, Payload={json.dumps(payload)}")
            response = await client.post(TRIP_POI_API_URL, headers=headers, json=payload)
            logger.debug(f"Trip.com POI API响应状态码: {response.status_code}")

            # Check for authentication errors first
            if response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]:
                logger.warning(f"Trip.com API returned {response.status_code}. Headers might be invalid. Signaling refresh.")
                return HEADER_REFRESH_REQUIRED # Signal to refresh headers

            response.raise_for_status() # Raise exception for other bad status codes

            data = response.json()
            logger.debug(f"Trip.com POI API Raw Response: {json.dumps(data)}")

            # Check GraphQL level errors
            if "errors" in data and data["errors"]:
                logger.error(f"Trip.com GraphQL API returned errors: {data['errors']}")
                return None

            # Check for successful data structure
            if ("data" in data and
                "poiSearch" in data["data"] and
                data["data"]["poiSearch"] and
                isinstance(data["data"]["poiSearch"], dict) and
                data["data"]["poiSearch"].get("ResponseStatus", {}).get("Ack") == "Success"):
                logger.info(f"Successfully retrieved POI data for key '{search_key}'.")
                return data["data"]["poiSearch"] # Return the relevant part
            else:
                logger.warning(f"Trip.com POI search response format invalid or not successful for key '{search_key}'. Response: {json.dumps(data)}")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Trip.com POI API: {e.response.status_code} - {e.response.text[:500]}...")
            # 添加更详细的错误日志
            logger.error(f"请求URL: {TRIP_POI_API_URL}")
            logger.error(f"请求头: {json.dumps({k: v for k, v in headers.items() if k != 'cookie'})}")
            logger.error(f"请求负载: {json.dumps(payload)}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error calling Trip.com POI API: {e}")
            return None
        except json.JSONDecodeError:
            # Check if response object exists before accessing .text
            resp_text = response.text[:500] if 'response' in locals() and hasattr(response, 'text') else "N/A"
            logger.error(f"Failed to decode JSON response from Trip.com POI API. Response text: {resp_text}...")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error calling Trip.com POI API: {e}", exc_info=True)
            return None


async def get_poi_data(query: str, trip_type: str, mode: str, current_user: UserResponse) -> Dict[str, Any]:
    """
    Retrieves POI data, checking cache first, then calling the Trip.com API.
    Handles API authentication errors by refreshing headers and retrying once.

    Args:
        query: The search query string.
        trip_type: Trip type (e.g., "RT", "OW").
        mode: Search mode (e.g., "0").
        current_user: The currently authenticated user.

    Returns:
        The raw POI data dictionary from the API or cache.

    Raises:
        HTTPException: If data cannot be retrieved after retry (503 Service Unavailable).
    """
    logger.info(f"User '{current_user.email}' searching POI: query='{query}', type='{trip_type}', mode='{mode}'")

    # 1. Check cache
    cached_result = await poi_crud.get_cached_location(query, trip_type, mode)
    if cached_result:
        logger.info(f"Cache hit for POI query: '{query}', type='{trip_type}', mode='{mode}'")
        if 'raw_data' in cached_result and isinstance(cached_result['raw_data'], str):
            try:
                parsed_data = json.loads(cached_result['raw_data'])
                logger.debug("Successfully parsed cached raw_data. Processing it now to ensure new format.")
                return process_poi_results(parsed_data, query) # Process and return in new format
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse cached JSON data for POI query '{query}'. Proceeding to API call.")
        else:
            # Log if raw_data is missing or not a string
            data_type = type(cached_result.get('raw_data')).__name__ if 'raw_data' in cached_result else 'missing'
            logger.warning(f"Cache data for POI query '{query}' is malformed (expected string, got {data_type}). Proceeding to API call.")

    logger.info(f"Cache miss for POI query: '{query}', type='{trip_type}', mode='{mode}'. Calling API.")

    # 2. Cache miss - Call API (first attempt)
    headers = await dynamic_fetcher.get_effective_trip_headers()
    if not headers:
         logger.error("Failed to get initial effective Trip.com headers.")
         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not prepare request to external service (headers).")

    api_result = await _call_trip_poi_api(query, trip_type, mode, headers)

    # 3. Handle API result: Check for refresh signal
    if api_result is HEADER_REFRESH_REQUIRED:
        logger.warning("Trip.com API call indicated header refresh needed. Attempting refresh and retry.")
        headers = await dynamic_fetcher.get_effective_trip_headers(force_refresh=True)
        if not headers:
            logger.error("Failed to get refreshed Trip.com headers after initial auth failure.")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to refresh external service credentials.")

        # Retry API call
        api_result = await _call_trip_poi_api(query, trip_type, mode, headers)

    # 4. Handle final API result (after potential retry)
    if api_result is None or api_result is HEADER_REFRESH_REQUIRED:
        logger.error(f"Failed to retrieve data from Trip.com for query '{query}' after potential retry.")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to retrieve data from Trip.com after retry")

    # 5. Success - Process data, save to cache and return
    if isinstance(api_result, dict):
        logger.info(f"Successfully retrieved data from Trip.com API for query '{query}'. Processing results.")

        # 处理数据，转换为前端期望的格式
        processed_data = process_poi_results(api_result, query)

        try:
            # 将处理后的数据转为JSON字符串并保存到缓存
            raw_json_str = json.dumps(api_result)  # 仍保存原始数据到缓存
            await poi_crud.save_location_result(query, trip_type, mode, raw_json_str)
        except Exception as e:
            logger.exception(f"Failed to save POI result to cache for query '{query}': {e}", exc_info=True)

        return processed_data  # 返回处理后的数据而不是原始数据
    else:
        logger.error(f"API call for query '{query}' returned unexpected type: {type(api_result)}. Raising internal error.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error processing external API response.")


def process_poi_results(poi_data: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    处理Trip.com API返回的POI数据，将其转换为新的标准化格式。

    Args:
        poi_data: Trip.com API返回的原始POI数据
        query: 搜索关键词

    Returns:
        标准化的机场搜索响应
    """
    try:
        airports = []

        # 检查原始数据中是否有results数组
        results = poi_data.get("results", [])
        if not results:
            logger.warning("No 'results' array found in Trip.com API response")
            return {
                "success": True,
                "airports": [],
                "total": 0,
                "query": query
            }

        if not isinstance(results, list):
            logger.warning(f"'results' is not a list, got {type(results)}")
            return {
                "success": True,
                "airports": [],
                "total": 0,
                "query": query
            }

        logger.info(f"Processing {len(results)} POI results from Trip.com API")

        # 处理每个POI项目，提取并转换字段
        for item in results:
            if not isinstance(item, dict):
                logger.warning(f"Skipping non-dict item in results: {type(item)}")
                continue

            # 从原始数据中提取需要的字段
            airport_code = item.get("airportCode", "")
            airport_name = item.get("airportShortName", "") or item.get("name", "")
            city_name = item.get("cityName", "") or item.get("cityEName", "")
            country_name = item.get("countryName", "")

            # 只处理有机场代码的项目（真正的机场）
            if airport_code and airport_name:
                airport_info = {
                    "code": airport_code,
                    "name": airport_name,
                    "city": city_name,
                    "country": country_name,
                    "type": "AIRPORT"
                }
                airports.append(airport_info)

            # 处理子结果（城市下的机场）
            child_results = item.get("childResults")
            if child_results and isinstance(child_results, list):
                for child in child_results:
                    if not isinstance(child, dict):
                        logger.warning(f"Skipping non-dict child item: {type(child)}")
                        continue

                    child_airport_code = child.get("airportCode", "")
                    child_airport_name = child.get("airportShortName", "") or child.get("name", "")
                    child_city_name = child.get("cityName", "") or city_name  # 使用父级城市名
                    child_country_name = child.get("countryName", "") or country_name  # 使用父级国家名

                    if child_airport_code and child_airport_name:
                        airport_info = {
                            "code": child_airport_code,
                            "name": child_airport_name,
                            "city": child_city_name,
                            "country": child_country_name,
                            "type": "AIRPORT"
                        }
                        airports.append(airport_info)

        # 去重处理（基于机场代码）
        unique_airports = []
        seen_codes = set()
        for airport in airports:
            if airport["code"] not in seen_codes:
                unique_airports.append(airport)
                seen_codes.add(airport["code"])

        logger.info(f"Processed {len(unique_airports)} unique airports from {len(results)} POI results")

        return {
            "success": True,
            "airports": unique_airports,
            "total": len(unique_airports),
            "query": query
        }
    except Exception as e:
        logger.exception(f"Error processing POI results for query '{query}': {e}")
        return {
            "success": True,
            "airports": [],
            "total": 0,
            "query": query
        }