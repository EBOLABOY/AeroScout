from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Dict # Import Dict for response model if not using PoiSearchResponse
import logging

from app.core.dependencies import get_current_active_user, RateLimiter # Import new RateLimiter
from app.services import trip_poi_service
from app.apis.v1.schemas import UserResponse, PoiSearchRequest, PoiSearchResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/search",
    response_model=PoiSearchResponse, # Or Dict if returning raw data directly
    summary="Search for Point of Interest (POI)",
    description="Searches for POIs (like airports, cities) using the Trip.com API, subject to rate limiting.",
    dependencies=[Depends(RateLimiter(limit_type="poi"))] # Apply POI-specific rate limiting
)
async def search_poi(
    request_body: PoiSearchRequest = Body(...),
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Handles POI search requests.

    - **query**: The search term (e.g., "Shanghai", "PVG").
    - **trip_type**: Context for the search (e.g., "flight").
    - **mode**: Search mode (e.g., "dep" for departure, "arr" for arrival).
    """
    try:
        logger.debug(f"POI搜索: {request_body.query}")

        # 获取处理后的POI数据
        poi_data = await trip_poi_service.get_poi_data(
            query=request_body.query,
            trip_type=request_body.trip_type,
            mode=request_body.mode,
            current_user=current_user # Pass user for potential checks/logging in service
        )

        # 如果服务层返回None，说明处理过程中出现了错误
        if poi_data is None:
            logger.error(f"POI搜索失败: 服务层返回了None值")
            raise HTTPException(status_code=404, detail="POI data not found or error occurred.")

        # 检查数据格式并处理兼容性
        if "airports" in poi_data:
            # 新格式数据
            airport_count = poi_data.get("total", 0)
            logger.info(f"返回POI搜索结果: 找到{airport_count}个机场")

            if airport_count > 0:
                sample_airports = poi_data["airports"][:min(3, airport_count)]
                logger.debug(f"样本机场: {sample_airports}")

            return PoiSearchResponse(
                success=poi_data["success"],
                airports=poi_data["airports"],
                total=poi_data["total"],
                query=poi_data["query"]
            )
        else:
            # 旧格式数据，需要转换
            logger.warning("检测到旧格式的缓存数据，正在转换为新格式")

            # 从旧格式提取数据
            data_list = poi_data.get("dataList", [])
            airports = []

            for item in data_list:
                if item.get("code") and item.get("name"):
                    airport = {
                        "code": item["code"],
                        "name": item["name"],
                        "city": item.get("city_name", ""),
                        "country": item.get("country_name", ""),
                        "type": item.get("type", "AIRPORT")
                    }
                    airports.append(airport)

            logger.info(f"转换后返回POI搜索结果: 找到{len(airports)}个机场")

            return PoiSearchResponse(
                success=True,
                airports=airports,
                total=len(airports),
                query=request_body.query
            )
        # Alternatively, if you want to return the raw dict directly:
        # return poi_data
    except HTTPException as e:
        # Re-raise HTTPExceptions raised by the service layer or dependencies
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        # Log the error e
        print(f"Unexpected error during POI search: {e}") # Basic logging
        raise HTTPException(status_code=500, detail="Internal server error during POI search.")