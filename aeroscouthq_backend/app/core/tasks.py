import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple # Add List and Tuple
import httpx
from fastapi import HTTPException, status # For handling header fetch errors
from app.core import dynamic_fetcher
from app.apis.v1 import schemas # Import schemas for request/response types
from app.database.crud import hub_crud # Import hub_crud for probing
from typing import Optional, Dict, Any

from celery.exceptions import MaxRetriesExceededError, Retry

from app.celery_worker import celery_app
from app.core.config import settings
# Import flight service later when implementing find_flights_task
# from app.services import kiwi_flight_service

logger = logging.getLogger(__name__)


# --- HTTP-based Session Fetching Tasks ---

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def fetch_trip_session_task(self) -> Optional[Dict[str, str]]:
    """
    Celery task to fetch Trip.com session data (headers) using HTTP requests.
    Retries on failure.
    """
    # Run the async logic in a new event loop
    return asyncio.run(_fetch_trip_session_task_async(self))


async def _fetch_trip_session_task_async(self) -> Optional[Dict[str, str]]:
    """
    Async implementation of the Trip.com session fetch task using HTTP requests.
    """
    attempt_number = self.request.retries + 1
    logger.info(f"[Trip.com HTTP Task Attempt {attempt_number}/{self.max_retries + 1}] Starting fetch...")

    try:
        # Use httpx to fetch basic session data
        async with httpx.AsyncClient() as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            target_url = "https://hk.trip.com/flights/"
            logger.info(f"[Trip.com HTTP Task Attempt {attempt_number}] Requesting: {target_url}")

            response = await client.get(target_url, headers=headers, timeout=30.0)

            if response.status_code == 200:
                # Extract cookies from response
                cookies_str = "; ".join([f"{name}={value}" for name, value in response.cookies.items()])

                local_captured_headers = {
                    'accept': '*/*',
                    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                    'content-type': 'application/json',
                    'origin': 'https://hk.trip.com',
                    'referer': target_url,
                    'sec-ch-ua': '"Chromium";v="125", "Microsoft Edge";v="125", "Not.A/Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'x-ibu-flt-currency': 'CNY',
                    'x-ibu-flt-language': 'hk',
                    'x-ibu-flt-locale': 'zh-HK',
                    'cookie': cookies_str,
                    'user-agent': headers['User-Agent']
                }

                logger.info(f"[Trip.com HTTP Task Attempt {attempt_number}] HTTP fetch successful.")

                # Save to file cache
                try:
                    with open(settings.TRIP_COOKIE_FILE, 'w') as f:
                        json.dump(local_captured_headers, f, indent=2)
                    logger.info(f"Saved new Trip.com headers to cache file from task: {settings.TRIP_COOKIE_FILE}")
                except Exception as e:
                    logger.error(f"Failed to save Trip.com headers to cache file from task {settings.TRIP_COOKIE_FILE}: {e}")

                return local_captured_headers
            else:
                logger.error(f"[Trip.com HTTP Task Attempt {attempt_number}] HTTP request failed with status: {response.status_code}")
                raise Exception(f"HTTP request failed with status: {response.status_code}")

    except Exception as e:
        logger.error(f"[Trip.com HTTP Task Attempt {attempt_number}] Error: {e}", exc_info=True)
        try:
            raise self.retry(exc=e, countdown=60 * attempt_number)
        except MaxRetriesExceededError:
            logger.critical(f"[Trip.com HTTP Task] Max retries exceeded: {e}")
            return None
        except Retry:
            raise
        except Exception as e_retry:
            logger.error(f"[Trip.com HTTP Task] Unexpected error during retry logic: {e_retry}")
            return None


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, acks_late=True)
def fetch_kiwi_session_task(self) -> Optional[Dict[str, str]]:
    """
    Celery task to fetch Kiwi.com session data (headers) using fixed tokens.
    Retries on failure.
    """
    # Run the async logic in a new event loop
    return asyncio.run(_fetch_kiwi_session_task_async(self))


async def _fetch_kiwi_session_task_async(self) -> Optional[Dict[str, str]]:
    """
    Async implementation of the Kiwi.com session fetch task using fixed tokens.
    """
    attempt_number = self.request.retries + 1
    logger.info(f"[Kiwi.com Fixed Token Task Attempt {attempt_number}/{self.max_retries + 1}] Starting fetch...")

    try:
        # Use fixed token strategy
        captured_headers_dict = {
            'content-type': 'application/json',
            'kw-skypicker-visitor-uniqid': 'b500f05c-8234-4a94-82a7-fb5dc02340a9',
            'kw-umbrella-token': '0d23674b463dadee841cc65da51e34fe47bbbe895ae13b69d42ece267c7a2f51',
            'kw-x-rand-id': '07d338ea',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
            'origin': 'https://www.kiwi.com',
            'referer': 'https://www.kiwi.com/cn/search/tiles/--/--/anytime/anytime'
        }

        # Validate token by making a test request
        try:
            async with httpx.AsyncClient() as client:
                test_payload = {
                    "query": "query { __typename }",
                    "variables": {}
                }
                response = await client.post(
                    "https://api.skypicker.com/umbrella/v2/graphql",
                    headers=captured_headers_dict,
                    json=test_payload,
                    timeout=10.0
                )

                if response.status_code == 200:
                    logger.info(f"[Kiwi.com Fixed Token Task Attempt {attempt_number}] Token validation successful.")
                else:
                    logger.warning(f"[Kiwi.com Fixed Token Task Attempt {attempt_number}] Token validation failed with status: {response.status_code}")
                    raise Exception(f"Token validation failed with status: {response.status_code}")
        except Exception as e:
            logger.error(f"[Kiwi.com Fixed Token Task Attempt {attempt_number}] Token validation error: {e}")
            raise self.retry(exc=e, countdown=60 * attempt_number)

        logger.info(f"[Kiwi.com Fixed Token Task Attempt {attempt_number}] Kiwi fetch successful. Headers: {json.dumps(captured_headers_dict)}")

        # Save to file cache
        try:
            token_file = settings.KIWI_TOKEN_FILE
            with open(token_file, 'w') as f:
                json.dump(captured_headers_dict, f, indent=2)
            logger.info(f"Saved new Kiwi.com headers to cache file from task: {token_file}")
        except AttributeError:
            logger.error("settings.KIWI_TOKEN_FILE is not defined in config.py! Cannot save Kiwi token.")
        except Exception as e:
            logger.error(f"Failed to save Kiwi.com headers to cache file from task: {e}")

        return captured_headers_dict

    except Exception as e:
        logger.error(f"[Kiwi.com Fixed Token Task Attempt {attempt_number}] Error: {e}", exc_info=True)
        try:
            raise self.retry(exc=e, countdown=60 * attempt_number)
        except MaxRetriesExceededError:
            logger.critical(f"[Kiwi.com Fixed Token Task] Max retries exceeded: {e}")
            return None
        except Retry:
            raise
        except Exception as e_retry:
            logger.error(f"[Kiwi.com Fixed Token Task] Unexpected error during retry logic: {e_retry}")
            return None


# --- Kiwi API Configuration (Copied from service) ---
KIWI_GRAPHQL_ENDPOINT = "https://api.skypicker.com/umbrella/v2/graphql"
ONEWAY_QUERY_TEMPLATE = """
query SearchOneWayItinerariesQuery(
  $search: SearchOnewayInput
  $filter: ItinerariesFilterInput
  $options: ItinerariesOptionsInput
) {
  onewayItineraries(search: $search, filter: $filter, options: $options) {
    __typename
    ... on AppError { error: message }
    ... on Itineraries {
      server { requestId packageVersion serverToken }
      metadata { itinerariesCount hasMorePending }
      itineraries {
        __typename
        ... on ItineraryOneWay {
          id shareId
          price { amount priceBeforeDiscount } priceEur { amount }
          provider { name code } duration pnrCount
          travelHack { isTrueHiddenCity isVirtualInterlining isThrowawayTicket }
          bookingOptions {
            edges {
              node {
                token
                bookingUrl
                price { amount }
                priceEur { amount }
              }
            }
          }
          sector {
            duration
            sectorSegments {
              segment {
                source { localTime utcTimeIso station { name code city { name } } }
                destination { localTime utcTimeIso station { name code city { name } } }
                code duration carrier { name code } operatingCarrier { name code } cabinClass
              }
              layover { duration isBaggageRecheck }
            }
          }
        }
      }
    }
  }
}
"""
RETURN_QUERY_TEMPLATE = """
query SearchReturnItinerariesQuery(
  $search: SearchReturnInput
  $filter: ItinerariesFilterInput
  $options: ItinerariesOptionsInput
) {
  returnItineraries(search: $search, filter: $filter, options: $options) {
    __typename
    ... on AppError { error: message }
    ... on Itineraries {
      server { requestId packageVersion serverToken }
      metadata { itinerariesCount hasMorePending }
      itineraries {
        __typename
        ... on ItineraryReturn {
          id shareId
          price { amount priceBeforeDiscount } priceEur { amount }
          provider { name code } duration pnrCount
          travelHack { isTrueHiddenCity isVirtualInterlining isThrowawayTicket }
          bookingOptions {
            edges {
              node {
                token
                bookingUrl
                price { amount }
                priceEur { amount }
              }
            }
          }
          outbound {
            duration
            sectorSegments {
              segment {
                source { localTime utcTimeIso station { name code city { name } } }
                destination { localTime utcTimeIso station { name code city { name } } }
                code duration carrier { name code } operatingCarrier { name code } cabinClass
              }
              layover { duration isBaggageRecheck }
            }
          }
          inbound {
            duration
            sectorSegments {
              segment {
                source { localTime utcTimeIso station { name code city { name } } }
                destination { localTime utcTimeIso station { name code city { name } } }
                code duration carrier { name code } operatingCarrier { name code } cabinClass
              }
              layover { duration isBaggageRecheck }
            }
          }
        }
      }
    }
  }
}
"""

# --- Custom Exception (Copied from service) ---
class KiwiTokenError(Exception):
    """Custom exception for Kiwi API token-related errors."""
    pass


# --- Helper Functions for Flight Search Task ---

import logging
from datetime import datetime, timedelta, timezone # Import timezone
from typing import Optional, List, Dict, Any

from app.apis.v1 import schemas

logger = logging.getLogger(__name__)

def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Safely parse ISO 8601 datetime strings."""
    if not dt_str:
        return None
    try:
        # Handle potential 'Z' for UTC
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1] + '+00:00'
        # Pydantic v2 handles timezone-aware strings automatically if the model field is datetime
        dt = datetime.fromisoformat(dt_str)
        return dt
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse datetime string '{dt_str}': {e}")
        return None

def _parse_duration_minutes(duration_seconds: Optional[int]) -> Optional[int]:
    """Convert duration from seconds to minutes."""
    if duration_seconds is None:
        return None
    try:
        # Use floor division or round as appropriate, floor seems more common for duration
        return duration_seconds // 60
    except TypeError:
        logger.warning(f"Invalid type for duration_seconds: {type(duration_seconds)}")
        return None

def _parse_segment(raw_segment_data: dict) -> Optional[schemas.FlightSegment]:
    """Parses a single raw segment from Kiwi API into our FlightSegment schema."""
    try:
        segment = raw_segment_data.get('segment')
        if not segment:
            logger.warning("Segment data missing in raw_segment_data")
            return None

        source = segment.get('source', {})
        destination = segment.get('destination', {})
        source_station = source.get('station', {})
        dest_station = destination.get('station', {})
        carrier = segment.get('carrier', {})
        op_carrier_data = segment.get('operatingCarrier') # Can be null
        op_carrier = op_carrier_data if op_carrier_data else carrier # Fallback to carrier

        # Check essential nested structures exist
        if not all([source_station, dest_station, carrier, op_carrier]):
             logger.warning("Missing critical segment sub-dictionaries (station, carrier, op_carrier)")
             return None

        # Check essential codes exist
        dep_code = source_station.get('code')
        arr_code = dest_station.get('code')
        carrier_code = carrier.get('code')
        op_carrier_code = op_carrier.get('code')
        if not all([dep_code, arr_code, carrier_code, op_carrier_code]):
             logger.warning("Missing critical segment codes (departure, arrival, carrier, operating carrier)")
             return None

        # --- Flight Number Logic ---
        # Priority: 1. segment.code (from GraphQL), 2. segment.flightNumber (legacy/alternative), 3. Constructed placeholder
        flight_number = segment.get('code') # Priority 1: segment.code from GraphQL
        if not flight_number:
            flight_number_raw = segment.get('flightNumber') # Priority 2: Check legacy/alternative field
            if flight_number_raw:
                 flight_number = f"{carrier_code}-{flight_number_raw}" # Construct if available
            else:
                 flight_number = f"{carrier_code}-?" # Priority 3: Fallback placeholder

        # --- Time Parsing ---
        departure_time_local = _parse_datetime(source.get('localTime'))
        arrival_time_local = _parse_datetime(destination.get('localTime'))
        departure_time_utc = _parse_datetime(source.get('utcTimeIso')) # Added UTC time parsing
        arrival_time_utc = _parse_datetime(destination.get('utcTimeIso')) # Added UTC time parsing

        # --- Duration Parsing ---
        duration_minutes = _parse_duration_minutes(segment.get('duration'))

        # --- Validation of Parsed Values ---
        # Check local times and duration as they were checked before. UTC times are good to have but maybe not critical for skipping.
        if not all([departure_time_local, arrival_time_local, duration_minutes is not None]):
            logger.warning(f"Missing critical parsed segment data (local times, duration) for segment {flight_number} from {dep_code} @ {source.get('localTime')}")
            return None

        # --- Schema Instantiation ---
        # 使用与base_schemas.py中FlightSegment类匹配的字段名称
        return schemas.FlightSegment(
            departure_airport=dep_code,
            arrival_airport=arr_code,
            departure_airport_name=source_station.get('name'),
            arrival_airport_name=dest_station.get('name'),
            departure_city=source_station.get('city', {}).get('name'),
            arrival_city=dest_station.get('city', {}).get('name'),
            departure_time=departure_time_local,
            arrival_time=arrival_time_local,
            departure_time_utc=departure_time_utc,
            arrival_time_utc=arrival_time_utc,
            duration_minutes=duration_minutes,
            carrier_code=carrier_code,
            carrier_name=carrier.get('name'),
            operating_carrier_code=op_carrier_code,
            operating_carrier_name=op_carrier.get('name'),
            flight_number=flight_number,
            cabin_class=segment.get('cabinClass'),
            aircraft=None
        )
    except (KeyError, TypeError, AttributeError) as e:
        logger.error(f"Error parsing flight segment: {e}. Data: {str(raw_segment_data)[:200]}", exc_info=True)
        return None

async def _task_parse_kiwi_itinerary(raw_itinerary_data: dict, is_one_way: bool, requested_currency: str = "EUR") -> Optional[schemas.FlightItinerary]:
    """Parses a single raw itinerary from Kiwi API into our FlightItinerary schema."""
    if not raw_itinerary_data or not isinstance(raw_itinerary_data, dict):
        logger.warning("Received empty or invalid raw_itinerary_data")
        return None

    try:
        itinerary_id = raw_itinerary_data.get('id')
        share_id = raw_itinerary_data.get('shareId') # For deep link construction

        # 解析价格信息 - 添加调试日志
        price_eur_data = raw_itinerary_data.get('priceEur')
        price_eur = price_eur_data.get('amount') if price_eur_data else None

        # 获取主货币价格（根据API请求中的currency参数返回）
        price_main_data = raw_itinerary_data.get('price')
        price_main = price_main_data.get('amount') if price_main_data else None

        # 调试：打印价格信息
        logger.info(f"价格解析调试 - itinerary_id: {itinerary_id}")
        logger.info(f"  - 请求货币: {requested_currency}")
        logger.info(f"  - priceEur数据: {price_eur_data}")
        logger.info(f"  - price数据: {price_main_data}")
        logger.info(f"  - price_eur值: {price_eur}")
        logger.info(f"  - price_main值: {price_main}")

        # 直接使用Kiwi返回的CNY价格，不进行汇率转换
        final_price_cny = None
        if requested_currency.upper() == "CNY" and price_main is not None:
            # 当请求CNY时，price字段就是CNY价格，直接使用
            final_price_cny = float(price_main)
            logger.info(f"  - 直接使用Kiwi返回的CNY价格: {final_price_cny}")
        else:
            # 如果请求的不是CNY或者没有price_main，跳过此航班
            logger.warning(f"  - 未请求CNY货币或无CNY价格数据，跳过航班 - itinerary_id: {itinerary_id}")
            logger.warning(f"  - requested_currency: {requested_currency}, price_main: {price_main}")
            return None

        total_duration_seconds = raw_itinerary_data.get('duration')
        travel_hack_data = raw_itinerary_data.get('travelHack', {}) # Default to empty dict
        is_hidden_city = travel_hack_data.get('isTrueHiddenCity', False) # Default to False
        is_throwaway_ticket = travel_hack_data.get('isThrowawayTicket', False) # Check for throwaway ticket
        pnr_count = raw_itinerary_data.get('pnrCount', 1) # Get PNR count for self-transfer check

        # 🔍 甩尾票字段诊断日志
        logger.info(f"🔍 甩尾票字段诊断 - itinerary_id: {itinerary_id}")
        logger.info(f"  - travelHack数据: {travel_hack_data}")
        logger.info(f"  - isTrueHiddenCity: {is_hidden_city}")
        logger.info(f"  - isThrowawayTicket: {is_throwaway_ticket}")

        # 检查 hiddenDestination 和 throwawayDestination 字段
        hidden_destinations_found = []
        throwaway_destinations_found = []

        # 检查单程航班的 sector
        if 'sector' in raw_itinerary_data:
            sector = raw_itinerary_data['sector']
            if 'sectorSegments' in sector:
                for i, segment_data in enumerate(sector['sectorSegments']):
                    segment = segment_data.get('segment', {})
                    hidden_dest = segment.get('hiddenDestination')
                    throwaway_dest = segment.get('throwawayDestination')
                    if hidden_dest:
                        hidden_destinations_found.append(f"航段{i}: {hidden_dest}")
                        logger.info(f"  - 发现 hiddenDestination 航段{i}: {hidden_dest}")
                    if throwaway_dest:
                        throwaway_destinations_found.append(f"航段{i}: {throwaway_dest}")
                        logger.info(f"  - 发现 throwawayDestination 航段{i}: {throwaway_dest}")

        # 检查往返航班的 outbound/inbound
        for leg_name in ['outbound', 'inbound']:
            if leg_name in raw_itinerary_data:
                leg_data = raw_itinerary_data[leg_name]
                if 'sectorSegments' in leg_data:
                    for i, segment_data in enumerate(leg_data['sectorSegments']):
                        segment = segment_data.get('segment', {})
                        hidden_dest = segment.get('hiddenDestination')
                        throwaway_dest = segment.get('throwawayDestination')
                        if hidden_dest:
                            hidden_destinations_found.append(f"{leg_name}航段{i}: {hidden_dest}")
                            logger.info(f"  - 发现 hiddenDestination {leg_name}航段{i}: {hidden_dest}")
                        if throwaway_dest:
                            throwaway_destinations_found.append(f"{leg_name}航段{i}: {throwaway_dest}")
                            logger.info(f"  - 发现 throwawayDestination {leg_name}航段{i}: {throwaway_dest}")

        # 汇总诊断结果
        if hidden_destinations_found or throwaway_destinations_found:
            logger.info(f"  - ✅ 发现甩尾票字段: hidden={len(hidden_destinations_found)}, throwaway={len(throwaway_destinations_found)}")
        else:
            logger.info(f"  - ❌ 未发现任何甩尾票字段")
        provider_data = raw_itinerary_data.get('provider', {}) # Extract provider info
        provider_code = provider_data.get('code') # Added
        provider_name = provider_data.get('name') # Added

        # Extract booking token from bookingOptions
        booking_token = None
        booking_url = None
        booking_options = raw_itinerary_data.get('bookingOptions', {})
        if booking_options and 'edges' in booking_options:
            edges = booking_options['edges']
            if edges and len(edges) > 0:
                first_option = edges[0].get('node', {})
                booking_token = first_option.get('token')
                booking_url = first_option.get('bookingUrl')

        # Basic validation - 确保至少有EUR价格
        if not all([itinerary_id, final_price_cny is not None, total_duration_seconds is not None]):
             logger.warning(f"Missing critical itinerary fields (id, final_price_cny, duration) for itinerary data: {str(raw_itinerary_data)[:200]}")
             return None

        total_duration_minutes = _parse_duration_minutes(total_duration_seconds)
        if total_duration_minutes is None:
             logger.warning(f"Could not parse total duration for itinerary ID {itinerary_id}")
             return None

        outbound_segments_list: List[schemas.FlightSegment] = []
        inbound_segments_list: List[schemas.FlightSegment] = []
        # Determine self-transfer based on PNR count OR baggage recheck flag
        overall_self_transfer = (pnr_count > 1)

        # --- Parse Segments ---
        legs_to_parse = []
        if is_one_way:
            sector = raw_itinerary_data.get('sector')
            if sector and 'sectorSegments' in sector:
                legs_to_parse.append({'leg_data': sector, 'target_list': outbound_segments_list, 'name': 'oneway'})
            else:
                logger.warning(f"One-way itinerary {itinerary_id} missing 'sector' or 'sector.sectorSegments' structure.")
                return None # Missing structure is an error
        else: # Round trip
            outbound_leg = raw_itinerary_data.get('outbound')
            inbound_leg = raw_itinerary_data.get('inbound')

            if outbound_leg and 'sectorSegments' in outbound_leg:
                 legs_to_parse.append({'leg_data': outbound_leg, 'target_list': outbound_segments_list, 'name': 'outbound'})
            else:
                 logger.warning(f"Return itinerary {itinerary_id} missing 'outbound' or 'outbound.sectorSegments' structure.")
                 return None # Missing outbound is critical

            # Inbound is optional in terms of having segments, but the structure should ideally be there if 'inbound' key exists
            if inbound_leg and 'sectorSegments' in inbound_leg:
                 legs_to_parse.append({'leg_data': inbound_leg, 'target_list': inbound_segments_list, 'name': 'inbound'})
            elif inbound_leg: # 'inbound' key exists but no 'sectorSegments' or it's empty/null
                 logger.info(f"Return itinerary {itinerary_id} has 'inbound' leg structure but no segments found within.")
                 # This is acceptable, inbound_segments_list will remain empty.
            # If 'inbound' key doesn't exist at all, that's also fine (e.g., API error, or truly one-way data in return structure?)


        # Process the legs
        for leg_info in legs_to_parse:
            leg_data = leg_info['leg_data']
            target_list = leg_info['target_list']
            leg_name = leg_info['name']
            segment_count = 0
            for segment_data in leg_data.get('sectorSegments', []):
                parsed_segment = _parse_segment(segment_data)
                if parsed_segment:
                    target_list.append(parsed_segment)
                    segment_count += 1
                # Check for self-transfer *within* the leg via layover flag
                # This adds to the pnr_count check
                layover = segment_data.get('layover')
                if layover and layover.get('isBaggageRecheck'):
                    overall_self_transfer = True # Set flag if any segment requires recheck
            if segment_count == 0 and leg_data.get('sectorSegments'):
                 # Log if the list existed but we parsed nothing from it
                 logger.warning(f"Parsed 0 valid segments from {leg_name} leg of itinerary {itinerary_id}, although sectorSegments list was present.")
                 # Decide if this is fatal. If outbound fails, it's fatal. If inbound fails, maybe okay?
                 if leg_name == 'outbound' or leg_name == 'oneway':
                     return None # Cannot proceed without outbound/oneway segments if they were expected

        # --- Final Checks and Object Creation ---
        if not outbound_segments_list:
             # This should only happen if the initial structure check failed or parsing failed for outbound/oneway
             logger.error(f"Critical error: No outbound segments parsed for itinerary {itinerary_id}. Returning None.")
             return None

        # Construct deep link with priority: booking_url > booking_token > shareId > fallback
        if booking_url:
            deep_link = booking_url
        elif booking_token:
            deep_link = f"https://www.kiwi.com/en/booking?token={booking_token}"
        elif share_id:
            deep_link = f"https://www.kiwi.com/deep?shareId={share_id}"
        else:
            deep_link = f"https://www.kiwi.com/search?id={itinerary_id}"

        # 使用与base_schemas.py中FlightItinerary类匹配的字段名称
        # 添加最终价格验证调试
        logger.info(f"🎯 最终价格验证 - itinerary_id: {itinerary_id}")
        logger.info(f"  - final_price_cny: {final_price_cny} (类型: {type(final_price_cny)})")

        # 确保价格是有效的正数
        if final_price_cny is None or final_price_cny <= 0:
            logger.error(f"❌ 最终价格无效，跳过此航班 - itinerary_id: {itinerary_id}, price: {final_price_cny}")
            return None

        # 🔍 最终甩尾票标记确认
        logger.info(f"🔍 最终甩尾票标记确认 - itinerary_id: {itinerary_id}")
        logger.info(f"  - is_hidden_city: {is_hidden_city}")
        logger.info(f"  - is_throwaway_ticket: {is_throwaway_ticket}")
        logger.info(f"  - hidden_destinations_found: {len(hidden_destinations_found)}")
        logger.info(f"  - throwaway_destinations_found: {len(throwaway_destinations_found)}")

        # 如果发现了 hiddenDestination 但 is_hidden_city 为 False，强制设置为 True
        if hidden_destinations_found and not is_hidden_city:
            logger.warning(f"  - ⚠️ 发现 hiddenDestination 但 isTrueHiddenCity=False，强制标记为甩尾票")
            is_hidden_city = True

        return schemas.FlightItinerary(
            id=itinerary_id,
            price=final_price_cny,  # 直接使用CNY价格
            currency="CNY",  # 始终返回CNY
            booking_token=booking_token,
            deep_link=deep_link,
            outbound_segments=outbound_segments_list, # 已检查非空
            inbound_segments=inbound_segments_list if inbound_segments_list else None, # 如果为空则设为None
            segments=outbound_segments_list + (inbound_segments_list if inbound_segments_list else []), # 同时设置segments字段以兼容
            total_duration_minutes=total_duration_minutes,
            is_self_transfer=overall_self_transfer,
            is_hidden_city=is_hidden_city,
            is_throwaway_deal=is_throwaway_ticket,  # 🔧 修复: 传递甩尾票标识
            data_source="kiwi",
            raw_data=None # 保持响应简洁，除非调试需要
        )

    except (KeyError, TypeError, ValueError, AttributeError) as e:
        # Log the specific itinerary ID if available
        it_id = raw_itinerary_data.get('id', 'UNKNOWN_ID') if isinstance(raw_itinerary_data, dict) else 'INVALID_DATA'
        logger.error(f"Failed to parse Kiwi itinerary {it_id}: {e}. Raw data snippet: {str(raw_itinerary_data)[:500]}", exc_info=True)
        return None

async def _task_fetch_kiwi_itineraries_page(
    variables: dict,
    kiwi_headers: dict,
    server_token: Optional[str],
    is_one_way: bool,
    attempt_prefix: str,
    page_num: int
) -> Tuple[List[dict], Optional[str], bool]:
    """Fetches a single page of itineraries from Kiwi GraphQL API."""
    if is_one_way:
        query_template = ONEWAY_QUERY_TEMPLATE
        feature_name = "SearchOneWayItinerariesQuery"
        itineraries_key = "onewayItineraries"
    else:
        query_template = RETURN_QUERY_TEMPLATE
        feature_name = "SearchReturnItinerariesQuery"
        itineraries_key = "returnItineraries"

    current_variables = json.loads(json.dumps(variables))
    current_variables["options"]["serverToken"] = server_token

    payload = {
        "query": query_template,
        "variables": current_variables
    }

    api_url = f"{KIWI_GRAPHQL_ENDPOINT}?featureName={feature_name}"
    request_timeout = 45.0

    async with httpx.AsyncClient(timeout=request_timeout) as client:
        try:
            logger.debug(f"[{attempt_prefix}-P{page_num}] Sending request to {api_url} with token: {str(server_token)[:10]}...")
            response = await client.post(api_url, headers=kiwi_headers, json=payload)

            if response.status_code != 200:
                logger.error(f"[{attempt_prefix}-P{page_num}] Kiwi API HTTP Error: {response.status_code} - {response.text[:500]}")
                if response.status_code in [401, 403]:
                     logger.warning(f"[{attempt_prefix}-P{page_num}] Received HTTP {response.status_code}, potentially a token issue.")
                     raise KiwiTokenError(f"Kiwi API returned HTTP {response.status_code}, likely token-related.")
                return [], None, False

            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.error(f"[{attempt_prefix}-P{page_num}] Failed to decode JSON response: {response.text[:500]}")
                return [], None, False

            if 'errors' in data and data['errors']:
                error_message = json.dumps(data['errors'])
                logger.error(f"[{attempt_prefix}-P{page_num}] Kiwi GraphQL API Error: {error_message}")
                if "token" in error_message.lower() or "authorization" in error_message.lower() or "session" in error_message.lower():
                     logger.warning(f"[{attempt_prefix}-P{page_num}] GraphQL error suggests a token issue: {error_message}")
                     raise KiwiTokenError(f"Kiwi GraphQL error indicates potential token issue: {error_message}")
                return [], None, False

            if 'data' not in data or not data['data'] or itineraries_key not in data['data']:
                 logger.error(f"[{attempt_prefix}-P{page_num}] Invalid response structure. Missing '{itineraries_key}'. Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                 return [], None, False

            results_container = data['data'][itineraries_key]
            if results_container is None:
                logger.warning(f"[{attempt_prefix}-P{page_num}] '{itineraries_key}' field is null in response.")
                return [], None, False

            if results_container.get('__typename') == 'AppError':
                error_message = results_container.get('error', 'Unknown AppError')
                logger.error(f"[{attempt_prefix}-P{page_num}] Kiwi API returned AppError: {error_message}")
                if "token" in error_message.lower() or "session" in error_message.lower() or "invalid parameters" in error_message.lower():
                     logger.warning(f"[{attempt_prefix}-P{page_num}] AppError suggests a token issue: {error_message}")
                     raise KiwiTokenError(f"Kiwi AppError indicates potential token issue: {error_message}")
                return [], None, False

            raw_itineraries = results_container.get('itineraries', [])
            new_token = results_container.get('server', {}).get('serverToken')
            has_more = results_container.get('metadata', {}).get('hasMorePending', False)

            logger.info(f"[{attempt_prefix}-P{page_num}] Fetched {len(raw_itineraries)} itineraries. HasMore: {has_more}. NewToken: {str(new_token)[:10]}...")

            if has_more and not new_token and server_token:
                 logger.warning(f"[{attempt_prefix}-P{page_num}] hasMorePending is True, but no new serverToken received.")

            return raw_itineraries, new_token, has_more

        except httpx.TimeoutException:
            logger.error(f"[{attempt_prefix}-P{page_num}] Request to Kiwi API timed out after {request_timeout}s.")
            raise KiwiTokenError(f"Kiwi API request timed out (possible token/session issue).")
        except httpx.RequestError as e:
            logger.error(f"[{attempt_prefix}-P{page_num}] httpx RequestError contacting Kiwi API: {e}")
            return [], None, False
        except KiwiTokenError:
             raise
        except Exception as e:
            logger.error(f"[{attempt_prefix}-P{page_num}] Unexpected error during Kiwi API fetch: {e}", exc_info=True)
            return [], None, False


async def _task_perform_kiwi_search_session(
    base_variables: dict,
    kiwi_headers: dict,
    is_one_way: bool,
    max_pages: int,
    attempt_prefix: str
) -> List[dict]:
    """Performs a full paginated search session with Kiwi API."""
    all_raw_itineraries = []
    current_token = None
    page = 1
    has_more = True

    while has_more and page <= max_pages:
        try:
            logger.info(f"[{attempt_prefix}] Requesting page {page}...")
            raw_itineraries, new_token, has_more_pending = await _task_fetch_kiwi_itineraries_page(
                variables=base_variables,
                kiwi_headers=kiwi_headers,
                server_token=current_token,
                is_one_way=is_one_way,
                attempt_prefix=attempt_prefix,
                page_num=page
            )

            if raw_itineraries:
                all_raw_itineraries.extend(raw_itineraries)
                logger.info(f"[{attempt_prefix}-P{page}] Added {len(raw_itineraries)} itineraries. Total: {len(all_raw_itineraries)}")

            current_token = new_token
            has_more = has_more_pending

            if not has_more_pending:
                logger.info(f"[{attempt_prefix}-P{page}] No more pending results indicated by API.")
                break

            page += 1
            await asyncio.sleep(0.5)

        except KiwiTokenError:
            logger.error(f"[{attempt_prefix}] KiwiTokenError encountered during page {page} fetch. Aborting session.")
            raise
        except Exception as e:
            logger.error(f"[{attempt_prefix}] Unexpected error during page {page} fetch in session: {e}", exc_info=True)
            break

    if page > max_pages and has_more:
         logger.warning(f"[{attempt_prefix}] Reached max_pages limit ({max_pages}) but API indicated more results might exist.")

    logger.info(f"[{attempt_prefix}] Search session finished. Fetched {len(all_raw_itineraries)} itineraries in {page-1} pages.")
    return all_raw_itineraries


def _task_build_kiwi_variables(params: schemas.FlightSearchRequest, is_one_way: bool, **overrides) -> dict:
    """Builds the variables dictionary for Kiwi GraphQL API calls based on FlightSearchRequest."""
    logger.debug(f"Building Kiwi variables for {'one-way' if is_one_way else 'return'} search. Params: {params}, Overrides: {overrides}")

    # --- Itinerary Dates and Locations ---
    dep_date_start_obj = datetime.strptime(params.departure_date_from, "%Y-%m-%d")
    dep_date_end_obj = datetime.strptime(params.departure_date_to, "%Y-%m-%d") if params.departure_date_to else dep_date_start_obj

    itinerary_params = {
        "source": {"ids": [f"Station:airport:{params.origin_iata.upper()}"]},
        "destination": {"ids": [f"Station:airport:{params.destination_iata.upper()}"]},
        "outboundDepartureDate": {
            "start": dep_date_start_obj.strftime("%Y-%m-%dT00:00:00"),
            "end": dep_date_end_obj.strftime("%Y-%m-%dT23:59:59")
        }
    }
    if not is_one_way and params.return_date_from:
        ret_date_start_obj = datetime.strptime(params.return_date_from, "%Y-%m-%d")
        ret_date_end_obj = datetime.strptime(params.return_date_to, "%Y-%m-%d") if params.return_date_to else ret_date_start_obj
        itinerary_params["inboundDepartureDate"] = {
            "start": ret_date_start_obj.strftime("%Y-%m-%dT00:00:00"),
            "end": ret_date_end_obj.strftime("%Y-%m-%dT23:59:59")
        }

    # Apply overrides directly to itinerary (primarily for hub probing)
    if "source" in overrides:
        itinerary_params["source"] = overrides["source"]
    if "destination" in overrides:
        # Ensure destination override is in correct format
        dest_override = overrides["destination"]
        if isinstance(dest_override, str):
            # Convert string format to proper object format
            itinerary_params["destination"] = {"ids": [dest_override]}
        else:
            itinerary_params["destination"] = dest_override

    # --- Passengers and Bags ---
    passenger_params = {
        "adults": params.adults,
        # Add children/infants here if they are added to FlightSearchRequest
        # "children": getattr(params, 'children', 0),
        # "infants": getattr(params, 'infants', 0),
    }
    # Only add bag keys if they have valid values (not None and not empty list)
    if hasattr(params, 'adult_hold_bags') and params.adult_hold_bags:
        passenger_params["adultsHoldBags"] = params.adult_hold_bags
    if hasattr(params, 'adult_hand_bags') and params.adult_hand_bags:
        passenger_params["adultsHandBags"] = params.adult_hand_bags

    # --- Cabin Class ---
    cabin_map = {
        "ECONOMY": "ECONOMY",
        "PREMIUM_ECONOMY": "PREMIUM_ECONOMY",
        "BUSINESS": "BUSINESS",
        "FIRST": "FIRST",
    }
    # Use upper() for case-insensitivity and provide a default 'ECONOMY'
    mapped_cabin_class = cabin_map.get(getattr(params, 'cabin_class', 'ECONOMY').upper(), "ECONOMY")
    cabin_class_params = {"cabinClass": mapped_cabin_class, "applyMixedClasses": False} # Assuming applyMixedClasses=False is desired

    # --- Search Structure ---
    search_params = {
        "itinerary": itinerary_params,
        "passengers": passenger_params,
        "cabinClass": cabin_class_params,
        # Remove market field as it's not supported in SearchOnewayInput
    }

    # --- Filter Structure ---
    filter_params = {
        "allowDifferentStationConnection": True,
        "enableSelfTransfer": True,
        "enableThrowAwayTicketing": True,
        "enableTrueHiddenCity": True,
        "transportTypes": ["FLIGHT"],
        "contentProviders": ["KIWI"],
        "limit": params.max_results_per_type,
    }

    # Apply direct flight filter only to the main search, not probes
    is_probe = "source" in overrides or "destination" in overrides
    if params.direct_flights_only_for_primary and not is_probe:
        filter_params["maxStopsCount"] = 0

    if not is_one_way:
        filter_params["allowReturnFromDifferentCity"] = True
        filter_params["allowChangeInboundDestination"] = True
        filter_params["allowChangeInboundSource"] = True

    # Apply filter overrides (for maxStopsCount, etc.)
    if "maxStopsCount" in overrides:
        filter_params["maxStopsCount"] = overrides["maxStopsCount"]

    # --- Options Structure (based on real Kiwi query) ---
    options_params = {
        "sortBy": "QUALITY",  # Use QUALITY as in real query
        "partner": "skypicker",
        "currency": params.preferred_currency.lower() if params.preferred_currency else "cny",  # 默认使用CNY，小写
        "locale": "cn",  # 根据真实负载设置为cn
        "market": "us",  # 根据真实负载设置为us
        "partnerMarket": "cn",  # 设置为中国伙伴市场
        "serverToken": None,  # This will be filled in dynamically later
    }


    # --- Final Variables ---
    variables = {
        "search": search_params,
        "filter": filter_params,
        "options": options_params,
    }
    logger.debug(f"Constructed Kiwi variables: {json.dumps(variables, indent=2)}") # Use json.dumps for pretty print
    return variables


async def _task_run_search_with_retry(
    self, # Added self for retry mechanism
    variables: dict,
    attempt_desc: str,
    request_params: schemas.FlightSearchRequest, # Pass original request for max_pages
    force_one_way: bool = False
) -> List[dict]:
    """Runs a search session with token refresh retry logic within a Celery task."""
    kiwi_headers = {} # Initialize headers dict
    search_is_one_way = force_one_way or request_params.return_date_from is None
    search_id = variables.get("search_id", "unknown") # Get search_id if passed

    try:
        # Attempt 1: Get headers and run search
        try:
            kiwi_headers = await dynamic_fetcher.get_effective_kiwi_headers()
        except HTTPException as e:
             if e.status_code == 503:
                 logger.warning(f"[{search_id}-{attempt_desc}] Initial Kiwi headers fetch returned 503. Retrying task in 30s...")
                 logger.info(f"[{search_id}-{attempt_desc}] 503 error details: {e.detail}")
                 raise self.retry(exc=e, countdown=30) # Increased from 15s to 30s
             else:
                 logger.error(f"[{search_id}-{attempt_desc}] Failed to get initial Kiwi headers: {e.detail}")
                 raise # Re-raise other HTTP errors
        except Exception as e:
             logger.error(f"[{search_id}-{attempt_desc}] Unexpected error getting initial Kiwi headers: {e}", exc_info=True)
             raise # Re-raise unexpected errors

        return await _task_perform_kiwi_search_session(
            base_variables=variables,
            kiwi_headers=kiwi_headers,
            is_one_way=search_is_one_way,
            max_pages=request_params.max_pages_per_search,
            attempt_prefix=f"{search_id}-{attempt_desc}"
        )
    except KiwiTokenError:
        # Attempt 2: Refresh headers and retry search
        logger.warning(f"[{search_id}-{attempt_desc}] KiwiTokenError detected. Forcing header refresh and retrying search...")
        try:
            # Force refresh headers
            kiwi_headers = await dynamic_fetcher.get_effective_kiwi_headers(force_refresh=True)
            logger.info(f"[{search_id}-{attempt_desc}] Retrying search with refreshed headers.")
            # Retry the search session
            return await _task_perform_kiwi_search_session(
                base_variables=variables,
                kiwi_headers=kiwi_headers,
                is_one_way=search_is_one_way,
                max_pages=request_params.max_pages_per_search,
                attempt_prefix=f"{search_id}-{attempt_desc}-retry"
            )
        except KiwiTokenError as retry_e:
            logger.error(f"[{search_id}-{attempt_desc}] KiwiTokenError persisted after retry: {retry_e}")
            # Decide task outcome: fail or return empty? Let's return empty list after failed retry.
            return []
        except HTTPException as e:
             # Handle potential 503 on forced refresh
             if e.status_code == 503:
                 logger.error(f"[{search_id}-{attempt_desc}] Kiwi headers fetch returned 503 even on forced refresh. Retrying task in 45s...")
                 logger.info(f"[{search_id}-{attempt_desc}] Forced refresh 503 error details: {e.detail}")
                 raise self.retry(exc=e, countdown=45) # Increased from 30s to 45s for forced refresh
             else:
                 logger.error(f"[{search_id}-{attempt_desc}] Failed to get refreshed Kiwi headers: {e.detail}")
                 return [] # Return empty list if header refresh fails definitively
        except Exception as e:
             logger.error(f"[{search_id}-{attempt_desc}] Unexpected error during search retry: {e}", exc_info=True)
             return [] # Return empty list on unexpected retry error


# --- Flight Search Task ---

@celery_app.task(bind=True, max_retries=2, default_retry_delay=30, acks_late=True)
def find_flights_task(self, search_params_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to find flights based on search parameters, handling direct flights,
    hub probing, and result combination. Returns a dictionary representation
    of FlightSearchResponse.
    """
    # Run the async logic in a new event loop
    return asyncio.run(_find_flights_task_async(self, search_params_dict))


async def _find_flights_task_async(self, search_params_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Async implementation of the flight search task.
    """
    # Reconstruct Pydantic model from dict
    try:
        request_params = schemas.FlightSearchRequest(**search_params_dict)
    except Exception as e:
        logger.error(f"Failed to parse search_params_dict into FlightSearchRequest: {e}", exc_info=True)
        # Return an error structure or raise an exception? Let's return error dict.
        return {"search_id": "parsing-error", "flights": [], "disclaimers": ["Error parsing search parameters."], "probe_log": None}

    search_id = str(uuid.uuid4())
    task_id = self.request.id
    logger.info(f"[{search_id} / Task {task_id}] Starting flight search task ({request_params.origin_iata} -> {request_params.destination_iata})")

    is_one_way = request_params.return_date_from is None
    disclaimers = []
    probe_log = {} if request_params.enable_hub_probe else None # Initialize probe log if enabled
    parsed_main_flights: List[schemas.FlightItinerary] = [] # Stores all parsed flights from the main A->B search
    parsed_throwaway_deals: List[schemas.FlightItinerary] = [] # Stores validated and marked throwaway deals (A->X via B)
    main_search_raw: List[dict] = []

    # --- 1. Perform Main Search (A -> B) ---
    logger.info(f"[{search_id} / Task {task_id}] Performing main search ({request_params.origin_iata} -> {request_params.destination_iata})...")
    main_vars = _task_build_kiwi_variables(request_params, is_one_way)
    main_vars["search_id"] = search_id # Pass search_id for logging within helpers
    if request_params.direct_flights_only_for_primary:
        main_vars["filter"]["maxStopsCount"] = 0 # Filter for direct flights in primary search
        disclaimers.append("Primary search limited to direct flights.")

    try:
        main_search_raw = await _task_run_search_with_retry(
            self=self, # Pass self for retry mechanism
            variables=main_vars,
            attempt_desc="main",
            request_params=request_params
        )
    except MaxRetriesExceededError:
         logger.error(f"[{search_id} / Task {task_id}] Max retries exceeded during main search header fetch. Failing task.")
         # Return error dict
         return {"search_id": search_id, "flights": [], "disclaimers": ["Failed to fetch flight data after multiple retries."], "probe_log": probe_log}
    except Exception as e:
         logger.error(f"[{search_id} / Task {task_id}] Unhandled exception during main search: {e}", exc_info=True)
         return {"search_id": search_id, "flights": [], "disclaimers": ["An unexpected error occurred during the flight search."], "probe_log": probe_log}


    # --- 2. Parse Main Search Results (A -> B) ---
    logger.info(f"[{search_id} / Task {task_id}] Parsing {len(main_search_raw)} main search results...")
    min_direct_price_cny = float('inf')
    requested_currency = request_params.preferred_currency or "CNY"  # 获取请求的货币
    for raw_itinerary in main_search_raw:
        try:
            parsed = await _task_parse_kiwi_itinerary(raw_itinerary, is_one_way, requested_currency)
            if parsed:  # 添加None检查
                parsed_main_flights.append(parsed)
                # Check if it's a direct flight and update min price
                # Note: Kiwi's `sector` (one-way) vs `outbound`/`inbound` (return) structure needs careful handling for segment count.
                # Let's assume `len(parsed.segments)` works for both after parsing.
                # A more robust check might involve `raw_itinerary.get("sector", {}).get("sectorSegments", [])` length for one-way.
                if len(parsed.segments) == 1:
                     min_direct_price_cny = min(min_direct_price_cny, parsed.price)
                elif not is_one_way and len(parsed.segments) == 2: # Basic check for direct round trip
                     # This check is simplistic. A true direct round trip has one outbound and one inbound segment.
                     # Parsing logic in _task_parse_kiwi_itinerary combines segments, so this check might be inaccurate.
                     # We rely on the price comparison later.
                     min_direct_price_cny = min(min_direct_price_cny, parsed.price)
            else:
                logger.warning(f"[{search_id} / Task {task_id}] Parsed main flight to None - {raw_itinerary.get('id', 'UNKNOWN_ID')}")

        except ValueError as e:
            logger.warning(f"[{search_id} / Task {task_id}] Failed to parse main itinerary {raw_itinerary.get('id', 'N/A')}: {e}")
        except Exception as e:
             logger.error(f"[{search_id} / Task {task_id}] Unexpected error parsing main itinerary {raw_itinerary.get('id', 'N/A')}: {e}", exc_info=True)

    if min_direct_price_cny == float('inf'):
        logger.info(f"[{search_id} / Task {task_id}] No direct flights found in main search results for price comparison.")
        min_direct_price_cny = None
    else:
        logger.info(f"[{search_id} / Task {task_id}] Minimum direct flight price (A->B): {min_direct_price_cny} CNY")


    # --- 3. Perform Throwaway Ticketing Probe (Search A -> X, check for intermediate stop B) ---
    # This logic attempts to find "throwaway" or "hidden city" deals where a flight
    # from the origin (A) to a sacrifice destination (X) stops at the user's desired
    # destination (B), and the A->X ticket is cheaper than the direct A->B ticket.
    # The user would discard the final leg (B->X). This carries risks (e.g., checked bags, airline penalties).
    if request_params.enable_hub_probe:
        logger.info(f"[{search_id} / Task {task_id}] Starting Throwaway Ticketing Probe (Searching A->X via B)...")
        # Use configured list of sacrifice destinations (X)
        sacrifice_destinations = settings.CHINA_HUB_CITIES_FOR_PROBE # Example: ['HKG', 'MFM', 'TPE']
        probe_log["status"] = "started"
        probe_log["sacrifice_destinations_queried"] = []
        probe_log["probe_raw_results_count"] = 0 # Total raw itineraries returned by A->X searches
        probe_log["potential_deals_via_b_count"] = 0 # Itineraries A->X that were found to stop at B
        probe_log["throwaway_deals_marked_count"] = 0 # Itineraries marked as throwaway deals after price check
        probe_log["errors"] = []
        throwaway_tasks = []
        all_potential_throwaway_deals_via_b: List[schemas.FlightItinerary] = [] # Store parsed A->X itineraries that stop at B

        if not sacrifice_destinations:
            logger.warning(f"[{search_id} / Task {task_id}] Throwaway probe enabled but sacrifice destinations list (CHINA_HUB_CITIES_FOR_PROBE) is empty.")
            probe_log["status"] = "skipped_no_destinations"
            disclaimers.append("Throwaway probe skipped: No sacrifice destinations configured.")
        else:
            destination_b_iata = request_params.destination_iata.upper()

            for dest_x_iata in sacrifice_destinations:
                dest_x_iata = dest_x_iata.upper()
                if dest_x_iata == request_params.origin_iata.upper() or dest_x_iata == destination_b_iata:
                    logger.debug(f"[{search_id} / Task {task_id}] Skipping probe destination {dest_x_iata} as it matches origin or main destination.")
                    continue # Skip if X is A or B

                probe_log["sacrifice_destinations_queried"].append(dest_x_iata)

                # Build variables for A -> X search
                # Use the original is_one_way setting for the A->X search
                probe_vars = _task_build_kiwi_variables(request_params, is_one_way, destination=f"Station:airport:{dest_x_iata}")
                probe_vars["search_id"] = search_id

                async def run_throwaway_probe(dest_x, variables):
                    potential_deals_for_x: List[schemas.FlightItinerary] = []
                    try:
                        logger.info(f"[{search_id} / Task {task_id}] Probing A -> {dest_x}...")
                        probe_raw_results = await _task_run_search_with_retry(
                            self=self,
                            variables=variables,
                            attempt_desc=f"throwaway-{dest_x}",
                            request_params=request_params,
                            force_one_way=is_one_way # Ensure probe matches main search type
                        )
                        probe_log["probe_raw_results_count"] += len(probe_raw_results)

                        # Filter results: Find itineraries A-...-B-...-X
                        for raw_itinerary in probe_raw_results:
                            try:
                                parsed_itinerary = await _task_parse_kiwi_itinerary(raw_itinerary, is_one_way, requested_currency)
                                if not parsed_itinerary or not parsed_itinerary.segments: continue

                                for i, segment in enumerate(parsed_itinerary.segments):
                                    # Check if segment destination is B and it's not the last segment
                                    # Check if a segment's destination is the user's target (B)
                                    # AND it's not the *very last* segment of the A->X journey.
                                    if segment.arrival_airport.upper() == destination_b_iata and i < len(parsed_itinerary.segments) - 1:
                                        # Found a potential A-...-B-...-X itinerary. Add it for later price comparison.
                                        potential_deals_for_x.append(parsed_itinerary)
                                        logger.debug(f"[{search_id} / Task {task_id}] Potential throwaway candidate found: A -> {dest_x} via B (ID: {parsed_itinerary.id}, Price: {parsed_itinerary.price} CNY)")
                                        # Don't break yet, maybe multiple stops at B? (Unlikely but possible)
                                        # Let's break for simplicity now, assuming first B stop is the relevant one.
                                        break # Move to the next itinerary

                            except ValueError as e:
                                logger.warning(f"[{search_id} / Task {task_id}] Failed to parse potential throwaway deal for A->{dest_x} (ID: {raw_itinerary.get('id', 'N/A')}): {e}")
                            except Exception as e:
                                logger.error(f"[{search_id} / Task {task_id}] Unexpected error parsing potential throwaway deal for A->{dest_x} (ID: {raw_itinerary.get('id', 'N/A')}): {e}", exc_info=True)

                        logger.info(f"[{search_id} / Task {task_id}] Probe A -> {dest_x} found {len(potential_deals_for_x)} potential candidate itineraries stopping at B.")
                        return potential_deals_for_x
                    except MaxRetriesExceededError:
                         logger.error(f"[{search_id} / Task {task_id}] Max retries exceeded during probe A -> {dest_x}. Skipping destination.")
                         probe_log["errors"].append(f"Probe A -> {dest_x} failed after retries.")
                         return []
                    except Exception as e:
                        logger.error(f"[{search_id} / Task {task_id}] Error probing A -> {dest_x}: {e}", exc_info=True)
                        probe_log["errors"].append(f"Probe A -> {dest_x} failed: {str(e)}")
                        return []

                throwaway_tasks.append(run_throwaway_probe(dest_x_iata, probe_vars))

            # Gather results from all throwaway probes
            try:
                probe_results_lists = await asyncio.gather(*throwaway_tasks) # Collect results from all A->X searches
                all_potential_throwaway_deals_via_b = [item for sublist in probe_results_lists for item in sublist]
                probe_log["potential_deals_via_b_count"] = len(all_potential_throwaway_deals_via_b)
                logger.info(f"[{search_id} / Task {task_id}] Throwaway probe completed. Found {len(all_potential_throwaway_deals_via_b)} total candidate itineraries (A->X stopping at B).")

                # Price Comparison: Check if the A->X itinerary (stopping at B) is cheaper than the cheapest direct A->B flight.
                # Note: This compares the *full* A->X price against the A->B price.
                # A more ideal comparison would use the price specifically for the A->B portion
                # of the A->X itinerary, but this data is often unavailable or hard to extract reliably.
                # This simplification might miss some deals or include deals where only the full A->X is cheaper.
                if min_direct_price_cny is not None:
                    # Define a threshold (e.g., must be cheaper, or significantly cheaper)
                    # Let's require it to be strictly cheaper for now.
                    # price_threshold_factor = 0.9 # Example: Must be at least 10% cheaper
                    for deal_candidate in all_potential_throwaway_deals_via_b:
                        # Compare A->X price with the minimum direct A->B price found earlier
                        if deal_candidate.price < min_direct_price_cny: # Use '<' for strictly cheaper
                            # Mark this itinerary as a throwaway deal
                            deal_candidate.is_throwaway_deal = True
                            parsed_throwaway_deals.append(deal_candidate)
                            logger.debug(f"[{search_id} / Task {task_id}] Marked throwaway deal: ID {deal_candidate.id}, Price {deal_candidate.price} CNY (Direct A->B min: {min_direct_price_cny} CNY)")

                    probe_log["throwaway_deals_marked_count"] = len(parsed_throwaway_deals)
                    logger.info(f"[{search_id} / Task {task_id}] Marked {len(parsed_throwaway_deals)} throwaway deals as cheaper than direct A->B price ({min_direct_price_cny} CNY).")
                    if parsed_throwaway_deals:
                         disclaimers.append(
                             f"Found {len(parsed_throwaway_deals)} potential throwaway deals (flying A-X, exiting at B). "
                             "These require buying the full A-X ticket and abandoning the final leg(s). "
                             "This may violate airline rules and cause issues with checked bags or return flights. Verify risks before booking."
                         )
                else:
                    logger.info(f"[{search_id} / Task {task_id}] Skipping price comparison for throwaway deals as no direct A->B price was found for reference.")
                    # Do not mark any deals if no reference price exists.
                    probe_log["throwaway_deals_marked_count"] = 0


                probe_log["status"] = "completed"

            except Exception as e:
                 logger.error(f"[{search_id} / Task {task_id}] Error during asyncio.gather for throwaway probes: {e}", exc_info=True)
                 probe_log["status"] = "error_gathering_results"
                 probe_log["errors"].append(f"Error gathering throwaway probe results: {str(e)}")


    # --- 4. Combine and Filter Final Results ---
    # Separate direct flights and combo deals
    direct_flights = []
    combo_deals = []

    # Combine main search results and valid throwaway deals
    combined_flights = parsed_main_flights + parsed_throwaway_deals

    # Remove duplicates based on 'id'
    unique_flights_dict: Dict[str, schemas.FlightItinerary] = {}
    for flight in combined_flights:
        if flight:  # 添加None检查
            # Prioritize non-throwaway deals if IDs collide? Or let the cheaper one win?
            # Current logic: last one seen wins if ID is the same. Sorting later handles price.
            unique_flights_dict[flight.id] = flight
    final_flights = list(unique_flights_dict.values())

    # Separate direct flights from combo deals
    for flight in final_flights:
        # Determine if it's a direct flight based on segment count
        if is_one_way:
            # For one-way trips, direct flights have exactly 1 segment
            if len(flight.segments) == 1:
                direct_flights.append(flight)
            else:
                combo_deals.append(flight)
        else:
            # For round trips, direct flights have exactly 2 segments (1 outbound + 1 inbound)
            # This is a simplified check - in reality we should check outbound_segments and inbound_segments
            if len(flight.segments) == 2:
                direct_flights.append(flight)
            else:
                combo_deals.append(flight)

    # Sort by price
    direct_flights.sort(key=lambda f: f.price)
    combo_deals.sort(key=lambda f: f.price)

    logger.info(f"[{search_id} / Task {task_id}] Search task finished. Returning {len(direct_flights)} direct flights and {len(combo_deals)} combo deals (including {len(parsed_throwaway_deals)} throwaway deals).")

    # --- 5. Construct and Return Response ---
    response_data = schemas.FlightSearchResponse(
        search_id=search_id,
        direct_flights=direct_flights,
        combo_deals=combo_deals,
        disclaimers=list(set(disclaimers)), # Ensure unique disclaimers
        probe_details=probe_log # Use 'probe_details' to match schema definition if needed, or keep 'probe_log'
    )

    # Celery tasks should return JSON-serializable data
    # Use mode='json' to ensure datetime objects are properly serialized
    return response_data.model_dump(mode='json')


async def find_flights_sync_async(search_params_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    同步版本的航班搜索函数，不依赖Celery的self参数。
    专门用于同步接口调用。

    Args:
        search_params_dict: 搜索参数字典

    Returns:
        FlightSearchResponse的字典表示
    """
    # 创建一个模拟的self对象用于内部调用
    class MockSelf:
        def __init__(self):
            self.request = type('MockRequest', (), {'id': 'sync-call'})()

    mock_self = MockSelf()

    # 调用原有的异步函数
    return await _find_flights_task_async(mock_self, search_params_dict)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30, acks_late=True)
def probe_china_hubs_task(
    self,
    origin_iata: str,
    destination_iata: str,
    search_id: str,
    min_direct_price_eur: float,
    request_params_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Celery任务，执行中国中转城市探测逻辑。

    Args:
        origin_iata: 起始机场IATA代码
        destination_iata: 目的地机场IATA代码
        search_id: 搜索ID
        min_direct_price_eur: 最低直飞价格（欧元）
        request_params_dict: 搜索参数字典

    Returns:
        包含探测结果的字典
    """
    # Run the async logic in a new event loop
    return asyncio.run(_probe_china_hubs_task_async(
        self, origin_iata, destination_iata, search_id, min_direct_price_eur, request_params_dict
    ))


async def _probe_china_hubs_task_async(
    self,
    origin_iata: str,
    destination_iata: str,
    search_id: str,
    min_direct_price_eur: float,
    request_params_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Async implementation of the China hubs probing task.
    """
    task_id = self.request.id
    logger.info(f"[{search_id} / Task {task_id}] 开始中国中转城市探测任务: {origin_iata} -> {destination_iata}")

    try:
        # 重构请求参数
        request_params = schemas.FlightSearchRequest(**request_params_dict)
        requested_currency = request_params.preferred_currency or "CNY"  # 获取请求的货币

        # 获取中国主要枢纽机场
        china_hubs = await hub_crud.get_active_china_hubs()
        hubs_to_probe = china_hubs[:request_params.max_probe_hubs]

        # 初始化结果变量
        probe_log = {hub['iata_code']: {'status': 'pending', 'results': 0, 'a_b_deals': 0, 'a_b_x_deals': 0} for hub in hubs_to_probe}
        parsed_probe_deals = []
        disclaimers = []

        # 获取Kiwi API请求头
        try:
            kiwi_headers = await dynamic_fetcher.get_effective_kiwi_headers()
        except Exception as e:
            logger.error(f"[{search_id} / Task {task_id}] Failed to get Kiwi headers: {e}", exc_info=True)
            return {
                "probe_log": {"status": "failed", "error": "无法获取Kiwi API请求头"},
                "parsed_deals": [],
                "disclaimers": ["中国中转城市探测失败: 无法连接航班数据源"]
            }

        logger.info(f"[{search_id} / Task {task_id}] 将探测 {len(hubs_to_probe)} 个中国枢纽: {[h['iata_code'] for h in hubs_to_probe]}")

        # 定义目的地C和起点A
        origin_a_iata = origin_iata.upper()
        destination_c_iata = destination_iata.upper()

        for hub in hubs_to_probe:
            hub_iata = hub['iata_code']
            logger.info(f"[{search_id} / Task {task_id}] 正在探测经由枢纽: {hub_iata}")
            probe_log[hub_iata]['status'] = 'running'
            hub_results_count = 0
            a_b_deals_count = 0
            a_b_x_deals_count = 0

            # --- 策略1: A-B探测 (B为中国枢纽) ---
            try:
                logger.info(f"[{search_id} / Task {task_id}] 策略1: A-B探测 (A:{origin_a_iata} -> B:{hub_iata})...")

                # 构建A->B的搜索变量
                a_b_vars = _task_build_kiwi_variables(
                    request_params,
                    True,  # 强制单程
                    destination=f"Station:airport:{hub_iata}",  # 目的地设为枢纽B
                    maxStopsCount=3  # 最多3次中转，增加找到优惠的机会
                )
                a_b_vars["search_id"] = search_id

                # 执行A->B搜索
                a_b_raw = await _task_run_search_with_retry(
                    self=self,
                    variables=a_b_vars,
                    attempt_desc=f"probe-a-b-{hub_iata}",
                    request_params=request_params,
                    force_one_way=True
                )
                logger.info(f"[{search_id} / Task {task_id}] 找到 {len(a_b_raw)} 个从A到B的航班。")

                # 解析A->B结果并与A->C价格比较
                for it_raw in a_b_raw:
                    try:
                        parsed_itinerary = await _task_parse_kiwi_itinerary(it_raw, True, requested_currency)

                        # 价格比较: 如果A->B价格低于A->C最低直飞价格
                        if min_direct_price_eur != float('inf') and parsed_itinerary.price_eur < min_direct_price_eur * 0.9:  # 至少便宜10%
                            # 标记为探测建议
                            parsed_itinerary.isProbeSuggestion = True
                            parsed_itinerary.probeHub = hub_iata
                            parsed_itinerary.probeDisclaimer = f"此为探测特惠: 从{origin_a_iata}到{hub_iata}的票价低于直飞{destination_c_iata}，您可以考虑先飞到{hub_iata}，再另行安排前往{destination_c_iata}的交通。"

                            # 添加到探测结果
                            parsed_probe_deals.append(parsed_itinerary)
                            hub_results_count += 1
                            a_b_deals_count += 1

                            if "探测特惠机票可能提供更低价格" not in disclaimers:
                                disclaimers.append("探测特惠机票可能提供更低价格，但可能需要您自行安排后续交通。")

                    except ValueError as e:
                        logger.warning(f"[{search_id} / Task {task_id}] 解析A->B航班时出错 {it_raw.get('id')}: {e}")
                    except Exception as e:
                        logger.error(f"[{search_id} / Task {task_id}] 解析A->B航班时发生意外错误 {it_raw.get('id')}: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"[{search_id} / Task {task_id}] A-B探测过程中发生错误: {e}", exc_info=True)

            # --- 策略2: A-B-X探测 (B为中转，X为甩尾目的地) ---
            try:
                logger.info(f"[{search_id} / Task {task_id}] 策略2: A-B-X探测 (A:{origin_a_iata} -> X via B:{hub_iata})...")

                # 定义潜在的甩尾目的地X列表 (可以是其他中国城市或亚洲主要城市)
                sacrifice_destinations = [
                    d for d in settings.THROWAWAY_DESTINATIONS
                    if d != origin_a_iata and d != destination_c_iata and d != hub_iata
                ][:3]  # 限制为3个目的地以减少API调用

                for dest_x in sacrifice_destinations:
                    try:
                        logger.info(f"[{search_id} / Task {task_id}] 探测 A->{dest_x} 经由 {hub_iata}...")

                        # 构建A->X via B的搜索变量
                        a_b_x_vars = _task_build_kiwi_variables(
                            request_params,
                            True,  # 强制单程
                            destination=f"Station:airport:{dest_x}",  # 目的地设为X
                            stopovers=[{"locations": [f"Station:airport:{hub_iata}"], "nightsFrom": 0, "nightsTo": 0}]  # 必须经过B
                        )
                        a_b_x_vars["search_id"] = search_id

                        # 执行A->X via B搜索
                        a_b_x_raw = await _task_run_search_with_retry(
                            self=self,
                            variables=a_b_x_vars,
                            attempt_desc=f"probe-a-b-x-{hub_iata}-{dest_x}",
                            request_params=request_params,
                            force_one_way=True
                        )
                        logger.info(f"[{search_id} / Task {task_id}] 找到 {len(a_b_x_raw)} 个从A到X经由B的航班。")

                        # 解析A->X via B结果
                        for it_raw in a_b_x_raw:
                            try:
                                parsed_itinerary = await _task_parse_kiwi_itinerary(it_raw, True, requested_currency)

                                # 验证行程确实经过枢纽B
                                segment_through_hub = None
                                for i, segment in enumerate(parsed_itinerary.segments):
                                    if segment.arrival_airport == hub_iata and i < len(parsed_itinerary.segments) - 1:
                                        segment_through_hub = segment
                                        break

                                # 如果确实经过B，且价格低于A->C最低直飞价格
                                if segment_through_hub and min_direct_price_eur != float('inf') and parsed_itinerary.price_eur < min_direct_price_eur:
                                    # 标记为探测建议
                                    parsed_itinerary.isProbeSuggestion = True
                                    parsed_itinerary.probeHub = hub_iata
                                    parsed_itinerary.probeDisclaimer = (
                                        f"此为隐藏城市票价: 购买从{origin_a_iata}经{hub_iata}到{dest_x}的机票，但在{hub_iata}下机。"
                                        f"这可能违反航空公司运输条款，可能导致后续航段被取消，且托运行李可能会被送到最终目的地{dest_x}。"
                                    )

                                    # 添加到探测结果
                                    parsed_itinerary.is_hidden_city = True  # 标记为隐藏城市票
                                    parsed_probe_deals.append(parsed_itinerary)
                                    hub_results_count += 1
                                    a_b_x_deals_count += 1

                                    if "隐藏城市票价可能提供更低价格" not in disclaimers:
                                        disclaimers.append("隐藏城市票价可能提供更低价格，但存在法律风险，请谨慎考虑。")

                            except ValueError as e:
                                logger.warning(f"[{search_id} / Task {task_id}] 解析A->X via B航班时出错 {it_raw.get('id')}: {e}")
                            except Exception as e:
                                logger.error(f"[{search_id} / Task {task_id}] 解析A->X via B航班时发生意外错误 {it_raw.get('id')}: {e}", exc_info=True)

                    except Exception as e:
                        logger.error(f"[{search_id} / Task {task_id}] 探测A->{dest_x}经由{hub_iata}时发生错误: {e}", exc_info=True)

            except Exception as e:
                logger.error(f"[{search_id} / Task {task_id}] A-B-X探测过程中发生错误: {e}", exc_info=True)

            # 更新探测日志
            probe_log[hub_iata]['status'] = 'completed'
            probe_log[hub_iata]['results'] = hub_results_count
            probe_log[hub_iata]['a_b_deals'] = a_b_deals_count
            probe_log[hub_iata]['a_b_x_deals'] = a_b_x_deals_count
            logger.debug(f"[{search_id} / Task {task_id}] 完成枢纽探测: {hub_iata} - {hub_results_count} 个航班")
            await asyncio.sleep(1.0)  # 探测间隔

        logger.debug(f"[{search_id} / Task {task_id}] 中转城市探测完成: {len(parsed_probe_deals)} 个特惠")

        # 按价格排序
        parsed_probe_deals.sort(key=lambda f: f.price_eur)

        # 构建返回结果
        return {
            "probe_log": probe_log,
            "parsed_deals": [deal.model_dump(mode='json') for deal in parsed_probe_deals],  # 使用 mode='json' 确保 datetime 正确序列化
            "disclaimers": disclaimers
        }

    except Exception as e:
        logger.error(f"[{search_id} / Task {task_id}] 中国中转城市探测任务执行过程中发生意外错误: {e}", exc_info=True)
        return {
            "probe_log": {"status": "error", "error": str(e)},
            "parsed_deals": [],
            "disclaimers": ["中国中转城市探测过程中发生错误"]
        }