import json # Added for parsing settings
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status

from app.services import invitation_service, trip_poi_service # Added trip_poi_service
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.apis.v1.schemas import UserResponse # InvitationCodeResponse might be needed later
from app.core.config import settings # Added settings
from app.database.crud import hub_crud # Added hub_crud

router = APIRouter()

@router.post("/invitations", response_model=Dict[str, str], status_code=status.HTTP_201_CREATED)
async def create_invitation(
    current_user: UserResponse = Depends(get_current_admin_user) # 修复：使用管理员权限验证
):
    """
    Create a new invitation code (Admin access only).
    """
    new_code = await invitation_service.create_new_invitation_code(
        created_by_user_id=current_user.id
    )
    if not new_code:
        # This case might indicate an issue with DB or logic, though the service handles uniqueness.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create invitation code."
        )
    return {"invitation_code": new_code}


@router.post(
    "/populate-hubs",
    response_model=Dict[str, str],
    summary="Populate China Hub Cities from Config",
    description="Fetches POI data for hub cities defined in settings and attempts to add them to the database.",
)
async def populate_hubs(
    current_user: UserResponse = Depends(get_current_active_user) # Basic auth check
):
    """
    Populates the potential hubs table with data for Chinese hub cities
    specified in the application settings.
    """
    try:
        # 🔧 诊断日志：检查配置值的类型和内容
        print(f"🔍 诊断 - CHINA_HUB_CITIES_FOR_PROBE 类型: {type(settings.CHINA_HUB_CITIES_FOR_PROBE)}")
        print(f"🔍 诊断 - CHINA_HUB_CITIES_FOR_PROBE 值: {settings.CHINA_HUB_CITIES_FOR_PROBE}")
        
        # 检查类型，如果已经是list则直接使用，否则尝试解析
        if isinstance(settings.CHINA_HUB_CITIES_FOR_PROBE, list):
            hub_iata_codes = settings.CHINA_HUB_CITIES_FOR_PROBE
            print(f"🔍 诊断 - 直接使用list类型配置，长度: {len(hub_iata_codes)}")
        else:
            # 如果是字符串，尝试JSON解析
            print(f"🔍 诊断 - 尝试解析字符串类型配置")
            hub_iata_codes = json.loads(settings.CHINA_HUB_CITIES_FOR_PROBE)
            print(f"🔍 诊断 - JSON解析成功，结果: {hub_iata_codes}")
        
        if not isinstance(hub_iata_codes, list):
            raise ValueError("CHINA_HUB_CITIES_FOR_PROBE is not a valid list")
            
        print(f"🔍 诊断 - 最终使用的hub_iata_codes: {hub_iata_codes}")
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"🔍 诊断 - 解析失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse CHINA_HUB_CITIES_FOR_PROBE setting: {e}"
        )

    added_count = 0
    failed_count = 0
    # Use 'flight' and 'dep' as reasonable defaults for airport POI lookup
    trip_type = 'flight'
    mode = 'dep'

    for iata_code in hub_iata_codes:
        try:
            print(f"Attempting to fetch POI data for hub: {iata_code}") # Logging
            # Call the POI service - this will use cache and rate limiting
            poi_data = await trip_poi_service.get_poi_data(
                query=iata_code,
                trip_type=trip_type,
                mode=mode,
                current_user=current_user # Pass user, though not strictly needed for this internal task
            )

            # Assuming poi_data corresponds to the 'poiSearch' object in the response
            if poi_data and isinstance(poi_data, dict) and 'results' in poi_data:
                hub_found_and_added = False
                iata_code_upper = iata_code.upper() # Target IATA code from settings

                for result_item in poi_data.get('results', []):
                    if not isinstance(result_item, dict): continue # Skip invalid items

                    for child in result_item.get('childResults', []):
                        if not isinstance(child, dict): continue # Skip invalid child items

                        # Check if it's an airport (dataType 5) and has an airportCode
                        if child.get('dataType') == 5 and child.get('airportCode'):
                            child_airport_code = child.get('airportCode', '').upper()

                            # Check if this child airport matches the target IATA code
                            if child_airport_code == iata_code_upper:
                                # Extract details from the child (airport) dictionary
                                name = child.get('name') or child.get('airportShortName') # Prefer 'name', fallback to 'airportShortName'
                                city = child.get('cityName')
                                country = child.get('countryName')
                                longitude = child.get('longitude')
                                latitude = child.get('latitude')

                                if name: # Need at least a name and the matched IATA code
                                    hub_info = {
                                        "iata_code": iata_code_upper, # Use the matched code from settings
                                        "name": name,
                                        "city": city,
                                        "country": country,
                                        "longitude": longitude, # Add geo data if available
                                        "latitude": latitude,   # Add geo data if available
                                        "source": "trip.com"
                                    }
                                    try:
                                        print(f"Found matching airport for {iata_code}. Adding potential hub: {hub_info}") # Logging
                                        await hub_crud.add_potential_hub(hub_data=hub_info)
                                        added_count += 1
                                        hub_found_and_added = True
                                        break # Stop searching children once the target IATA is found and added
                                    except Exception as db_err:
                                        print(f"Error adding hub {iata_code} ({name}) to DB: {db_err}")
                                        # Don't increment failed_count here, let the outer check handle it if never added
                                else:
                                    print(f"Warning: Found matching airport {iata_code} but missing 'name' in child data: {child}")
                        # End of check for matching airport child
                    # End of loop through childResults
                    if hub_found_and_added:
                        break # Stop searching parent results once the target IATA is found and added
                # End of loop through results

                if not hub_found_and_added:
                    print(f"Failed to find or add a matching airport entry for IATA code {iata_code} in the received POI data.")
                    failed_count += 1
            else:
                # Handle case where poi_data is missing, not a dict, or has no 'results'
                print(f"Invalid or empty POI data structure received from service for {iata_code}.")
                failed_count += 1

        except HTTPException as http_err:
            # Catch specific HTTP errors from the service (e.g., rate limit, API errors)
            print(f"HTTP error fetching POI for {iata_code}: {http_err.detail}")
            failed_count += 1
        except Exception as e:
            # Catch any other unexpected errors during the process for a specific IATA code
            print(f"Unexpected error processing {iata_code}: {e}", exc_info=True) # Add exc_info for better debugging
            failed_count += 1

    return {"message": f"Hub population attempted. Added: {added_count}, Failed: {failed_count}"}