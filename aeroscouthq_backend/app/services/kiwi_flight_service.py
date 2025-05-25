import asyncio
import json
import logging
import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

import httpx
from fastapi import HTTPException, status

from app.core import dynamic_fetcher
from app.database.crud import hub_crud
from app.apis.v1 import schemas
from app.core.config import settings # 假设 settings 里可能有 KIWI_MAX_PAGES 等配置
from app.core.tasks import probe_china_hubs_task

logger = logging.getLogger(__name__)

# --- Kiwi API Configuration ---
KIWI_GRAPHQL_ENDPOINT = "https://api.skypicker.com/umbrella/v2/graphql"

# 注意：根据任务要求，已在原始模板基础上补充 bookingToken, databaseId, travelHack 相关字段
ONEWAY_QUERY_TEMPLATE = """
query SearchOneWayItinerariesQuery(
  $search: SearchOnewayInput
  $filter: ItinerariesFilterInput
  $options: ItinerariesOptionsInput
  $conditions: Boolean! # Keep if ItineraryDebug is used, otherwise can be removed if no @include uses it
) {
  onewayItineraries(search: $search, filter: $filter, options: $options) {
    __typename
    ... on AppError {
      error: message
    }
    ... on Itineraries {
      server { # Basic server info might be useful for debugging
        requestId
        packageVersion
        serverToken # May be needed for subsequent requests or pagination
      }
      metadata {
        itinerariesCount # Useful
        hasMorePending   # Useful for async loading display
        # REMOVED: eligibilityInformation (can be very large, add back specific parts if needed)
        # REMOVED: carriers (and AirlinesFilter_data fragment) - Add back if you need a carrier filter
        # REMOVED: stopoverCountries (and CountriesFilter_data fragment) - Add back for stopover country filter
        # REMOVED: travelTips (and TravelTip_data fragment) - Add back if you want to display these
        # REMOVED: topResults (and Sorting_data, useSortingModes_data fragments) - Add back if you need pre-sorted top results
        # REMOVED: priceAlertExists, existingPriceAlert (and PriceAlert_data fragment) - Add back for price alert features
        # REMOVED: missingProviders
        # searchFingerprint # Keep if needed for price alerts or re-querying
        # REMOVED: statusPerProvider
        # REMOVED: extendedTrackingMetadata (VERY LARGE - major reduction)
        # REMOVED: kayakEligibilityTest
        # hasTier1MarketItineraries # Usually internal logic, can remove
      }
      # sharedItinerary might be useful if you implement sharing features,
      # but for basic display, the main 'itineraries' list is key.
      # If keeping sharedItinerary, ensure its fragments are also kept/adjusted.
      # For now, let's assume we focus on the main itineraries list.
      # REMOVED: sharedItinerary (to simplify, can be added back if needed)

      itineraries {
        __typename
        id
        shareId # Useful for sharing or deep linking specific itineraries
        price {
          amount
          priceBeforeDiscount
        }
        priceEur {
          amount
        }
        provider {
          name
          code
          hasHighProbabilityOfPriceChange # Useful info for user
          # REMOVED: contentProvider, id (unless specifically needed for linking)
        }
        bagsInfo { # Important for user
          includedCheckedBags
          includedHandBags
          hasNoBaggageSupported
          hasNoCheckedBaggage
          # You might want to keep checkedBagTiers/handBagTiers if you display detailed baggage options/pricing
          # For simplification, I'm removing them, but they are often very useful.
          # checkedBagTiers { tierPrice { amount } bags { weight { value } } }
          # handBagTiers { tierPrice { amount } bags { weight { value } } }
          includedPersonalItem
          # personalItemTiers { ... } # Similar to above, useful but can be large
        }
        bookingOptions { # Essential for booking
          edges {
            node {
              token # Often needed for booking
              bookingUrl # Essential
              # trackingPixel # Usually for analytics, can remove
              itineraryProvider {
                code
                name
                # subprovider # Optional detail
                hasHighProbabilityOfPriceChange
                # contentProvider # Optional detail
                # providerCategory # Optional detail
                # id # Optional detail
              }
              price { amount } # Price for this specific booking option
              priceEur { amount }
              # priceLocks { ... } # Optional, if you use price lock features
              # kiwiProduct # Optional detail
              # disruptionTreatment # Optional detail
              # usRulesApply # Optional detail
            }
          }
        }
        travelHack { # Your requested fields
          isTrueHiddenCity
          isVirtualInterlining
          isThrowawayTicket
        }
        duration # Total duration
        pnrCount # Number of PNRs (tickets)

        ... on ItineraryOneWay { # Assuming you are focusing on OneWay
          legacyId # If used by your system
          sector {
            id
            duration # Duration of this sector
            sectorSegments {
              guarantee # Useful if you highlight transfer guarantees
              segment {
                id
                source {
                  localTime
                  utcTimeIso # Often useful for unambiguous time
                  station {
                    name
                    code
                    type # Useful to distinguish airport, bus station etc.
                    # gps { lat lng } # For map display
                    city { name # legacyId, id optional
                    }
                    # country { code id } # Optional detail
                  }
                }
                destination {
                  localTime
                  utcTimeIso
                  station {
                    name
                    code
                    type
                    # gps { lat lng }
                    city { name }
                    # country { code id }
                  }
                }
                duration # Segment duration
                type # Segment type (flight, train, etc.)
                code # Flight number or segment code
                carrier { name code # id optional
                }
                operatingCarrier { name code # id optional
                }
                cabinClass
                # hiddenDestination { ... } # If you need more details than travelHack.isTrueHiddenCity
                # throwawayDestination { ... } # If you need more details
              }
              layover { # Important for multi-segment itineraries
                duration
                isBaggageRecheck # Very important for self-transfers
                # isWalkingDistance # Optional detail
                # transferDuration # Optional detail
                # id # Optional detail
              }
            }
          }
          lastAvailable { seatsLeft } # Useful urgency indicator
          # isRyanair # Optional, if you need specific logic for Ryanair
          # benefitsData { ... } # Can be large, add back if you want to show these benefits
          # isAirBaggageBundleEligible # Optional
          # testEligibilityInformation # Usually internal, remove
        }
        # ...ItineraryDebug @include(if: $conditions) # Keep if $conditions can be true and you need debug data
      }
    }
  }
}

# --- REMOVED/COMMENTED OUT FRAGMENTS (adjust based on what you kept in the query) ---
# If you removed all references to a fragment in the main query,
# you MUST also remove its definition below.

# fragment AirlinesFilter_data on ItinerariesMetadata { ... } # Removed from query
# fragment CountriesFilter_data on ItinerariesMetadata { ... } # Removed from query
# fragment TravelTip_data on ItinerariesMetadata { ... } # Removed from query
# fragment Sorting_data on ItinerariesMetadata { ... } # Removed from query
# fragment useSortingModes_data on ItinerariesMetadata { ... } # (Likely linked to Sorting_data)
# fragment PriceAlert_data on ItinerariesMetadata { ... } # Removed from query

# Keep fragments that are still referenced or contain essential common fields
# For example, TripInfo is usually a good candidate to keep if it groups common itinerary fields.
# PrebookingStation might also be useful.
# ItineraryDebug is conditional.

fragment ItineraryDebug on Itinerary { # Keep if @include(if: $conditions) is used and $conditions can be true
  __isItinerary: __typename
  itineraryDebugData {
    debug
  }
}

fragment PrebookingStation on Station { # Used by TripInfo if kept, or directly if TripInfo is removed
  code
  type
  city {
    name
    # id # Optional
  }
}

# TripInfo is often a good way to group common fields across ItineraryOneWay, ItineraryReturn etc.
# If you *only* ever query ItineraryOneWay and don't use ...TripInfo, you could inline its fields.
# But keeping it is often cleaner if the API defines it and uses it broadly.
# Assuming TripInfo is still useful or was part of your original working query:
fragment TripInfo on Itinerary {
  __isItinerary: __typename # Often used by Apollo Client or similar
  ... on ItineraryOneWay {
    sector {
      id # Example, ensure TripInfo contains fields you want from all itinerary types
      sectorSegments {
        segment {
          id # Example
          source { station { ...PrebookingStation id }
          localTime
        }
        destination {
          station { ...PrebookingStation id }
          # localTime # Destination localTime might be in main segment, not always TripInfo
        }
      }
    }
  }
  # ... on ItineraryReturn { ... } # If you ever handle return trips
  # ... on ItineraryMulticity { ... } # If you ever handle multicity trips
}

# fragment WeekDaysFilter_data on ItinerariesMetadata { ... } # If you use weekday filters

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
          id shareId databaseId bookingToken # Added databaseId, bookingToken
          price { amount priceBeforeDiscount } priceEur { amount }
          provider { name code } duration pnrCount
          travelHack { isTrueHiddenCity isThrowawayTicket } # Fixed field name: isThrowAwayTicketing -> isThrowawayTicket
          outbound {
            duration
            sectorSegments {
              segment {
                source { localTime station { name code city { name } terminal } }
                destination { localTime station { name code city { name } terminal } }
                hiddenDestination { code name city { name id } country { name id } id } # Added hiddenDestination field
                duration carrier { name code } operatingCarrier { name code } cabinClass vehicle { type }
              }
              layover { duration isBaggageRecheck }
            }
          }
          inbound {
            duration
            sectorSegments {
              segment {
                source { localTime station { name code city { name } terminal } }
                destination { localTime station { name code city { name } terminal } }
                hiddenDestination { code name city { name id } country { name id } id } # Added hiddenDestination field
                duration carrier { name code } operatingCarrier { name code } cabinClass vehicle { type }
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

# --- Custom Exception ---
class KiwiTokenError(Exception):
    """Custom exception for Kiwi API token-related errors."""
    pass

# --- Helper Functions (Placeholders) ---

def _parse_segment_list(raw_segments_list: List[dict], itinerary_id: str) -> Tuple[List[schemas.FlightSegment], bool]:
    """Parses a list of raw segment data into FlightSegment objects and detects baggage recheck."""
    parsed_segments = []
    found_baggage_recheck = False
    for seg_detail in raw_segments_list:
        segment_data = seg_detail.get("segment")
        layover_data = seg_detail.get("layover")

        if not segment_data:
            logger.warning(f"Skipping segment due to missing segment data in itinerary {itinerary_id}")
            continue

        # Check for self-transfer based on baggage recheck flag in layover
        if layover_data and layover_data.get("isBaggageRecheck"):
            found_baggage_recheck = True

        # Parse segment details
        try:
            # Use .get with default None for potentially missing nested keys
            source_station = segment_data.get("source", {}).get("station", {})
            dest_station = segment_data.get("destination", {}).get("station", {})
            hidden_destination = segment_data.get("hiddenDestination", {})
            carrier = segment_data.get("carrier", {})
            operating_carrier = segment_data.get("operatingCarrier", {})

            departure_dt_str = segment_data.get("source", {}).get("localTime")
            arrival_dt_str = segment_data.get("destination", {}).get("localTime")

            departure_dt = datetime.fromisoformat(departure_dt_str) if departure_dt_str else None
            arrival_dt = datetime.fromisoformat(arrival_dt_str) if arrival_dt_str else None

            # Basic validation
            if not source_station.get("code") or not dest_station.get("code") or not carrier.get("code"):
                 logger.warning(f"Skipping segment due to missing essential codes (origin/dest/carrier) in itinerary {itinerary_id}")
                 continue

            # Process hidden destination information
            hidden_destination_info = None
            if hidden_destination and hidden_destination.get("code"):
                hidden_destination_info = {
                    "code": hidden_destination.get("code"),
                    "name": hidden_destination.get("name"),
                    "city_name": hidden_destination.get("city", {}).get("name"),
                    "city_id": hidden_destination.get("city", {}).get("id"),
                    "country_name": hidden_destination.get("country", {}).get("name"),
                    "country_id": hidden_destination.get("country", {}).get("id"),
                    "id": hidden_destination.get("id")
                }
                logger.debug(f"Found hidden destination for segment in itinerary {itinerary_id}: {hidden_destination_info}")

            segment = schemas.FlightSegment(
                # 使用与base_schemas.py中FlightSegment类匹配的字段名称
                departure_airport=source_station.get("code"),
                arrival_airport=dest_station.get("code"),
                departure_airport_name=source_station.get("name"),
                arrival_airport_name=dest_station.get("name"),
                departure_city=source_station.get("city", {}).get("name"),
                arrival_city=dest_station.get("city", {}).get("name"),
                departure_time=departure_dt,
                arrival_time=arrival_dt,
                duration_minutes=int(segment_data.get("duration", 0) / 60),
                carrier_code=carrier.get("code"),
                carrier_name=carrier.get("name"),
                operating_carrier_code=operating_carrier.get("code", carrier.get("code")),
                operating_carrier_name=operating_carrier.get("name", carrier.get("name")),
                flight_number=str(segment_data.get("flightNumber", "")),
                cabin_class=segment_data.get("cabinClass", "ECONOMY"),
                aircraft=segment_data.get("vehicle", {}).get("type"),
                departure_terminal=source_station.get("terminal"),
                arrival_terminal=dest_station.get("terminal"),
                layover_duration_minutes=int(layover_data.get("duration", 0) / 60) if layover_data else None,
                is_baggage_recheck=layover_data.get("isBaggageRecheck", False) if layover_data else None,
                hidden_destination=hidden_destination_info  # Add hidden destination info
            )
            parsed_segments.append(segment)
        except KeyError as e:
            logger.warning(f"KeyError parsing segment detail in itinerary {itinerary_id}: {e}. Skipping segment.")
            continue
        except ValueError as e: # Catches potential datetime parsing errors
             logger.warning(f"ValueError parsing segment detail (e.g., datetime) in itinerary {itinerary_id}: {e}. Skipping segment.")
             continue
        except Exception as e:
             logger.warning(f"Unexpected error parsing segment detail in itinerary {itinerary_id}: {e}. Skipping segment.", exc_info=True)
             continue

    return parsed_segments, found_baggage_recheck


async def _parse_kiwi_itinerary(raw_itinerary_data: dict, is_one_way: bool) -> Optional[schemas.FlightItinerary]:
    """Parses a single raw itinerary from Kiwi API into our schema. Returns None if parsing fails critically."""
    itinerary_id = raw_itinerary_data.get("id", "UNKNOWN_ID")
    try:
        outbound_segments: Optional[List[schemas.FlightSegment]] = None
        inbound_segments: Optional[List[schemas.FlightSegment]] = None
        found_outbound_recheck = False
        found_inbound_recheck = False

        total_duration = timedelta(seconds=raw_itinerary_data.get("duration", 0))
        is_hidden_city = raw_itinerary_data.get("travelHack", {}).get("isTrueHiddenCity", False)
        is_throwaway_ticket = raw_itinerary_data.get("travelHack", {}).get("isThrowawayTicket", False)
        pnr_count = raw_itinerary_data.get("pnrCount", 1)
        is_self_transfer_base = pnr_count > 1 # Base check on PNR count

        if is_one_way:
            sector = raw_itinerary_data.get("sector", {})
            raw_segments = sector.get("sectorSegments", [])
            outbound_segments, found_outbound_recheck = _parse_segment_list(raw_segments, itinerary_id)
        else: # Return flight
            outbound_raw = raw_itinerary_data.get("outbound", {}).get("sectorSegments", [])
            inbound_raw = raw_itinerary_data.get("inbound", {}).get("sectorSegments", [])
            outbound_segments, found_outbound_recheck = _parse_segment_list(outbound_raw, itinerary_id)
            inbound_segments, found_inbound_recheck = _parse_segment_list(inbound_raw, itinerary_id)

        # Final self-transfer check
        is_self_transfer = is_self_transfer_base or found_outbound_recheck or found_inbound_recheck

        # Validation: Ensure we have at least outbound segments
        if not outbound_segments:
             logger.error(f"Failed to parse any valid outbound segments for itinerary {itinerary_id}")
             return None # Return None instead of raising error to allow processing other itineraries
        else:
            # Calculate next_segment_requires_airport_change for outbound segments
            for i in range(len(outbound_segments) - 1):
                current_seg = outbound_segments[i]
                next_seg = outbound_segments[i+1]
                current_seg.next_segment_requires_airport_change = current_seg.arrival_airport != next_seg.departure_airport
            if outbound_segments: # Last segment has no next segment
                outbound_segments[-1].next_segment_requires_airport_change = False


        # Validation: For round trips, ensure we also have inbound segments
        if not is_one_way:
            if not inbound_segments:
                 logger.error(f"Failed to parse any valid inbound segments for round-trip itinerary {itinerary_id}")
                 return None # Return None for incomplete round trips
            else:
                # Calculate next_segment_requires_airport_change for inbound segments
                for i in range(len(inbound_segments) - 1):
                    current_seg = inbound_segments[i]
                    next_seg = inbound_segments[i+1]
                    current_seg.next_segment_requires_airport_change = current_seg.arrival_airport != next_seg.departure_airport
                if inbound_segments: # Last segment has no next segment
                    inbound_segments[-1].next_segment_requires_airport_change = False


        itinerary = schemas.FlightItinerary(
            id=itinerary_id,
            price=raw_itinerary_data["priceEur"]["amount"],
            booking_token=raw_itinerary_data.get("bookingToken"),
            deep_link=f"https://www.kiwi.com/en/booking?token={raw_itinerary_data.get('bookingToken')}",
            outbound_segments=outbound_segments,
            inbound_segments=inbound_segments,
            segments=outbound_segments + (inbound_segments if inbound_segments else []),
            total_duration_minutes=int(total_duration.total_seconds() / 60),
            is_self_transfer=is_self_transfer,
            is_hidden_city=is_hidden_city,
            is_throwaway_deal=is_throwaway_ticket,  # Add throwaway ticket flag
            data_source="kiwi",
            raw_data=None
        )
        return itinerary

    except KeyError as e:
        logger.error(f"KeyError while parsing itinerary {itinerary_id}: Missing key {e}")
        return None # Return None on critical parsing error
    except Exception as e:
        logger.error(f"Unexpected error parsing itinerary {itinerary_id}: {e}", exc_info=True)
        return None # Return None on critical parsing error


async def _fetch_kiwi_itineraries_page(
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
    
        # Deep copy variables to avoid modifying the original dict
        current_variables = json.loads(json.dumps(variables))
        current_variables["options"]["serverToken"] = server_token
    
        payload = {
            "query": query_template,
            "variables": current_variables
        }
    
        api_url = f"{KIWI_GRAPHQL_ENDPOINT}?featureName={feature_name}"
        request_timeout = 45.0 # seconds
    
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            try:
                logger.debug(f"[{attempt_prefix}-P{page_num}] Sending request to {api_url} with token: {str(server_token)[:10]}...")
                response = await client.post(api_url, headers=kiwi_headers, json=payload)
    
                # Check for HTTP errors first
                if response.status_code != 200:
                    logger.error(f"[{attempt_prefix}-P{page_num}] Kiwi API HTTP Error: {response.status_code} - {response.text[:500]}")
                    # Consider specific status codes that might indicate token issues
                    if response.status_code in [401, 403]:
                         logger.warning(f"[{attempt_prefix}-P{page_num}] Received HTTP {response.status_code}, potentially a token issue.")
                         raise KiwiTokenError(f"Kiwi API returned HTTP {response.status_code}, likely token-related.")
                    # For other errors, return empty results but don't raise KiwiTokenError unless sure
                    return [], None, False
    
                # Parse JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    logger.error(f"[{attempt_prefix}-P{page_num}] Failed to decode JSON response: {response.text[:500]}")
                    return [], None, False
    
                # Check for GraphQL level errors (within the JSON response)
                if 'errors' in data and data['errors']:
                    error_message = json.dumps(data['errors'])
                    logger.error(f"[{attempt_prefix}-P{page_num}] Kiwi GraphQL API Error: {error_message}")
                    # Check if the error message indicates a token problem (heuristic)
                    if "token" in error_message.lower() or "authorization" in error_message.lower() or "session" in error_message.lower():
                         logger.warning(f"[{attempt_prefix}-P{page_num}] GraphQL error suggests a token issue: {error_message}")
                         raise KiwiTokenError(f"Kiwi GraphQL error indicates potential token issue: {error_message}")
                    return [], None, False # Return empty for other GraphQL errors
    
                # Check for AppError within the data structure
                if 'data' not in data or not data['data'] or itineraries_key not in data['data']:
                     logger.error(f"[{attempt_prefix}-P{page_num}] Invalid response structure. Missing '{itineraries_key}'. Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                     return [], None, False
    
                results_container = data['data'][itineraries_key]
                if results_container is None:
                    logger.warning(f"[{attempt_prefix}-P{page_num}] '{itineraries_key}' field is null in response.")
                    # This might happen at the end of results, treat as no more data
                    return [], None, False
    
                if results_container.get('__typename') == 'AppError':
                    error_message = results_container.get('error', 'Unknown AppError')
                    logger.error(f"[{attempt_prefix}-P{page_num}] Kiwi API returned AppError: {error_message}")
                     # Check if AppError indicates a token problem (heuristic)
                    if "token" in error_message.lower() or "session" in error_message.lower() or "invalid parameters" in error_message.lower(): # "invalid parameters" sometimes relates to expired tokens
                         logger.warning(f"[{attempt_prefix}-P{page_num}] AppError suggests a token issue: {error_message}")
                         raise KiwiTokenError(f"Kiwi AppError indicates potential token issue: {error_message}")
                    return [], None, False # Return empty for other AppErrors
    
                # Extract data if successful
                raw_itineraries = results_container.get('itineraries', [])
                new_token = results_container.get('server', {}).get('serverToken')
                has_more = results_container.get('metadata', {}).get('hasMorePending', False)
    
                logger.info(f"[{attempt_prefix}-P{page_num}] Fetched {len(raw_itineraries)} itineraries. HasMore: {has_more}. NewToken: {str(new_token)[:10]}...")
    
                # Sanity check: if has_more is True, we should ideally get a new token
                if has_more and not new_token and server_token: # Only warn if we had a token before
                     logger.warning(f"[{attempt_prefix}-P{page_num}] hasMorePending is True, but no new serverToken received.")
                     # Don't stop pagination here, let the calling function decide based on max_pages
    
                return raw_itineraries, new_token, has_more
    
            except httpx.TimeoutException:
                logger.error(f"[{attempt_prefix}-P{page_num}] Request to Kiwi API timed out after {request_timeout}s.")
                # Timeout might indicate network issues or potentially an expired session/token causing delays
                # Let's raise KiwiTokenError cautiously here, as retrying with a fresh token might help.
                raise KiwiTokenError(f"Kiwi API request timed out (possible token/session issue).")
            except httpx.RequestError as e:
                logger.error(f"[{attempt_prefix}-P{page_num}] httpx RequestError contacting Kiwi API: {e}")
                # Treat generic request errors as potentially recoverable without token refresh for now
                return [], None, False
            except KiwiTokenError: # Re-raise KiwiTokenError if caught
                 raise
            except Exception as e:
                logger.error(f"[{attempt_prefix}-P{page_num}] Unexpected error during Kiwi API fetch: {e}", exc_info=True)
                return [], None, False
    
    
async def _perform_kiwi_search_session(
    base_variables: dict,         # Indented parameter
    kiwi_headers: dict,           # Indented parameter
    is_one_way: bool,             # Indented parameter
    max_pages: int,               # Indented parameter
    attempt_prefix: str           # Indented parameter
) -> List[dict]:                  # Indented return type
    """Performs a full paginated search session with Kiwi API."""
    all_raw_itineraries = []
    current_token = None
    page = 1
    has_more = True # Start assuming there might be data

    while has_more and page <= max_pages:
        try:
            logger.info(f"[{attempt_prefix}] Requesting page {page}...")
            raw_itineraries, new_token, has_more_pending = await _fetch_kiwi_itineraries_page(
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

            # Update token and has_more status for the next iteration
            current_token = new_token
            has_more = has_more_pending

            if not has_more_pending:
                logger.info(f"[{attempt_prefix}-P{page}] No more pending results indicated by API.")
                break # Exit loop if API says no more data

            page += 1

            # Optional delay to avoid overwhelming the API
            await asyncio.sleep(0.5) # 500ms delay between page requests

        except KiwiTokenError:
            logger.error(f"[{attempt_prefix}] KiwiTokenError encountered during page {page} fetch. Aborting session.")
            raise # Re-raise the error to be handled by the caller
        except Exception as e:
            logger.error(f"[{attempt_prefix}] Unexpected error during page {page} fetch in session: {e}", exc_info=True)
            # Decide whether to break or continue? Let's break for safety.
            break

    if page > max_pages and has_more:
         logger.warning(f"[{attempt_prefix}] Reached max_pages limit ({max_pages}) but API indicated more results might exist.")

    logger.info(f"[{attempt_prefix}] Search session finished. Fetched {len(all_raw_itineraries)} itineraries in {page-1} pages.")
    return all_raw_itineraries


# --- Helper Function for Variable Construction ---

def _build_kiwi_variables(params: schemas.FlightSearchRequest, is_one_way: bool, **overrides) -> dict:
    """Builds the base variables dictionary for Kiwi API calls, applying overrides."""
    dep_date_obj = datetime.strptime(params.departure_date_from, "%Y-%m-%d")
    itinerary_params = {
        "source": {"ids": [f"Station:airport:{params.origin_iata.upper()}"]},
        "destination": {"ids": [f"Station:airport:{params.destination_iata.upper()}"]},
        "outboundDepartureDate": {
            "start": dep_date_obj.strftime("%Y-%m-%dT00:00:00"),
            "end": dep_date_obj.strftime("%Y-%m-%dT23:59:59")
        }
    }
    if not is_one_way and params.return_date_from:
        ret_date_obj = datetime.strptime(params.return_date_from, "%Y-%m-%d")
        itinerary_params["inboundDepartureDate"] = {
            "start": ret_date_obj.strftime("%Y-%m-%dT00:00:00"),
            "end": ret_date_obj.strftime("%Y-%m-%dT23:59:59")
        }

    base_vars = {
        "search": {
            "itinerary": itinerary_params,
            "passengers": { # Assuming 1 adult for now, can be parameterized later
                "adults": 1, "children": 0, "infants": 0,
                "adultsHoldBags": params.adult_hold_bags if params.adult_hold_bags is not None else [0],
                "adultsHandBags": params.adult_hand_bags if params.adult_hand_bags is not None else [1] # Default to 1 hand bag
            },
            "cabinClass": {"cabinClass": params.cabin_class.upper(), "applyMixedClasses": False}
        },
        "filter": {
            "allowDifferentStationConnection": True,
            "enableSelfTransfer": True, # Default to true for main search
            "enableThrowAwayTicketing": True,
            "enableTrueHiddenCity": True,
            "transportTypes": ["FLIGHT"],
            "contentProviders": ["KIWI"], # Or make configurable if needed
            "limit": 30 # Standard page size for Kiwi
        },
        "options": {
            "sortBy": "PRICE", # Or make configurable
            # Use preferred currency/locale from request, fallback to defaults
            "currency": params.preferred_currency.lower() if params.preferred_currency else "eur",
            "locale": params.preferred_locale.lower() if params.preferred_locale else "en",
            "partner": "skypicker", # Standard value
            "partnerMarket": params.market.lower() if params.market else "cn", # Use market from request or default
            "storeSearch": False,
            "serverToken": None, # Will be set during pagination
             # Add abTestInput based on previous script if needed, keeping minimal for now
        }
    }

    if not is_one_way:
        base_vars["filter"]["allowReturnFromDifferentCity"] = True
        base_vars["filter"]["allowChangeInboundDestination"] = True
        base_vars["filter"]["allowChangeInboundSource"] = True

    # Apply overrides
    for key, value in overrides.items():
        if key in base_vars["filter"]:
            base_vars["filter"][key] = value
        elif key in base_vars["search"]: # Allow overriding search params if needed
             base_vars["search"][key] = value
        # Add more override locations if necessary

    return base_vars


# --- Main Service Function ---

async def find_flights(
    request_params: schemas.FlightSearchRequest,
    current_user: schemas.UserResponse # Assuming UserResponse is the correct schema
) -> schemas.FlightSearchResponse:
    """
    Finds flights based on search parameters, handling direct flights,
    hub probing, and result combination.
    """
    search_id = str(uuid.uuid4())
    logger.info(f"[{search_id}] Starting flight search for user '{current_user.username}' ({request_params.origin_iata} -> {request_params.destination_iata})")

    is_one_way = request_params.return_date_from is None
    disclaimers = []
    probe_log = {} if request_params.enable_hub_probe else None
    parsed_direct_flights: List[schemas.FlightItinerary] = []
    parsed_probed_deals: List[schemas.FlightItinerary] = []
    main_search_raw: List[dict] = []
    direct_flights_raw: List[dict] = [] # Only used if direct_flights_only_for_primary is True

    # --- 1. Get Kiwi Headers (with initial fetch) ---
    try:
        kiwi_headers = await dynamic_fetcher.get_effective_kiwi_headers()
    except Exception as e:
        logger.error(f"[{search_id}] Failed to get initial Kiwi headers: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to authenticate with flight provider.")

    # --- Helper for Search Session with Retry ---
    async def _run_search_with_retry(variables: dict, attempt_desc: str, force_one_way: bool = False) -> List[dict]:
        """Runs a search session with token refresh retry logic."""
        nonlocal kiwi_headers # Allow modification of headers on retry
        search_is_one_way = force_one_way or is_one_way # Use forced value or original request type

        try:
            return await _perform_kiwi_search_session(
                base_variables=variables,
                kiwi_headers=kiwi_headers,
                is_one_way=search_is_one_way, # Use determined one-way status
                max_pages=request_params.max_pages_per_search,
                attempt_prefix=f"{search_id}-{attempt_desc}"
            )
        except KiwiTokenError:
            logger.warning(f"[{search_id}-{attempt_desc}] KiwiTokenError detected. Forcing header refresh and retrying...")
            try:
                kiwi_headers = await dynamic_fetcher.get_effective_kiwi_headers(force_refresh=True)
                logger.info(f"[{search_id}-{attempt_desc}] Retrying search with refreshed headers.")
                return await _perform_kiwi_search_session(
                    base_variables=variables,
                    kiwi_headers=kiwi_headers,
                    is_one_way=search_is_one_way, # Use determined one-way status on retry
                    max_pages=request_params.max_pages_per_search,
                    attempt_prefix=f"{search_id}-{attempt_desc}-retry"
                )
            except KiwiTokenError as retry_e:
                logger.error(f"[{search_id}-{attempt_desc}] KiwiTokenError persisted after retry: {retry_e}")
                raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kiwi API authentication failed after retry.")
            except Exception as retry_e:
                 logger.error(f"[{search_id}-{attempt_desc}] Unexpected error during search retry: {retry_e}", exc_info=True)
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during flight search retry.")
        except Exception as e:
             logger.error(f"[{search_id}-{attempt_desc}] Unexpected error during initial search: {e}", exc_info=True)
             # Don't raise HTTPException here, allow process to continue if possible, maybe return empty list?
             # Let's return empty list for unexpected errors during search session
             return []


    # --- 2. Main Search (A-C, allowing stops and self-transfer) ---
    logger.info(f"[{search_id}] Performing main search...")
    main_search_vars = _build_kiwi_variables(request_params, is_one_way, enableSelfTransfer=True) # Explicitly enable self-transfer
    main_search_raw = await _run_search_with_retry(main_search_vars, "main")
    logger.info(f"[{search_id}] Main search completed. Found {len(main_search_raw)} raw itineraries.")

    # --- 3. Direct Flight Extraction & Parsing ---
    logger.info(f"[{search_id}] Extracting direct flights...")
    if request_params.direct_flights_only_for_primary:
        logger.info(f"[{search_id}] Performing dedicated direct flight search (maxStopsCount=0)...")
        direct_flight_vars = _build_kiwi_variables(request_params, is_one_way, maxStopsCount=0, enableSelfTransfer=False)
        direct_flights_raw = await _run_search_with_retry(direct_flight_vars, "direct")
        logger.info(f"[{search_id}] Dedicated direct search completed. Found {len(direct_flights_raw)} raw itineraries.")
        for it_raw in direct_flights_raw:
            try:
                parsed = await _parse_kiwi_itinerary(it_raw, is_one_way)
                # Double check it's actually direct (API might sometimes err)
                if len(parsed.segments) == (1 if is_one_way else 2): # 1 segment for one-way, 2 for return (outbound+inbound)
                    parsed_direct_flights.append(parsed)
                else:
                     logger.warning(f"[{search_id}] Itinerary {parsed.id} from direct search has {len(parsed.segments)} segments, expected {1 if is_one_way else 2}. Skipping.")
            except ValueError as e:
                logger.warning(f"[{search_id}] Failed to parse direct itinerary {it_raw.get('id')}: {e}")
            except Exception as e:
                 logger.error(f"[{search_id}] Unexpected error parsing direct itinerary {it_raw.get('id')}: {e}", exc_info=True)
    else:
        logger.info(f"[{search_id}] Filtering direct flights from main search results...")
        for it_raw in main_search_raw:
            try:
                # Determine expected segment count for direct flight
                expected_segments = 1 if is_one_way else 2 # Outbound + Inbound

                # Check segment count directly from raw data if possible (more efficient)
                segment_count = 0
                if is_one_way:
                    segment_count = len(it_raw.get("sector", {}).get("sectorSegments", []))
                else:
                    segment_count = len(it_raw.get("outbound", {}).get("sectorSegments", [])) + \
                                    len(it_raw.get("inbound", {}).get("sectorSegments", []))

                if segment_count == expected_segments:
                    parsed = await _parse_kiwi_itinerary(it_raw, is_one_way)
                    parsed_direct_flights.append(parsed)

            except ValueError as e:
                # This might happen if parsing fails even for potentially direct ones
                logger.warning(f"[{search_id}] Failed to parse potential direct itinerary {it_raw.get('id')} from main results: {e}")
            except Exception as e:
                 logger.error(f"[{search_id}] Unexpected error parsing potential direct itinerary {it_raw.get('id')} from main results: {e}", exc_info=True)

    logger.info(f"[{search_id}] Found {len(parsed_direct_flights)} direct itineraries.")
    if any(f.is_self_transfer for f in parsed_direct_flights):
         disclaimers.append("Some direct flight options may involve self-transfer (check details).") # Should not happen often for directs, but good check


    # --- 4. China Hub Probe ---
    if request_params.enable_hub_probe:
        logger.info(f"[{search_id}] Starting China Hub Probe using async task...")
        try:
            # 获取直飞航班的最低价格作为比较基准
            min_direct_price = float('inf')
            for flight in parsed_direct_flights:
                if flight.price < min_direct_price:
                    min_direct_price = flight.price
            
            logger.info(f"[{search_id}] Minimum direct flight price (A->C): {min_direct_price if min_direct_price != float('inf') else 'Not found'} EUR")
            
            # 启动异步Celery任务执行中国中转城市探测
            
            # 准备任务参数
            task_result = await probe_china_hubs_task.delay(
                origin_iata=request_params.origin_iata.upper(),
                destination_iata=request_params.destination_iata.upper(),
                search_id=search_id,
                min_direct_price=min_direct_price,
                request_params_dict=request_params.model_dump()
            )
            
            # 获取任务结果（这里会阻塞等待任务完成，但任务本身是在后台执行的）
            task_result_data = await task_result.get(timeout=60)  # 设置合理的超时时间
            
            # 处理任务结果
            if task_result_data:
                # 更新探测日志
                probe_log = task_result_data.get("probe_log", {})
                
                # 添加探测结果到parsed_probed_deals
                for deal_dict in task_result_data.get("parsed_deals", []):
                    # 将字典转换回FlightItinerary对象
                    deal = schemas.FlightItinerary(**deal_dict)
                    parsed_probed_deals.append(deal)
                
                # 添加免责声明
                for disclaimer in task_result_data.get("disclaimers", []):
                    if disclaimer not in disclaimers:
                        disclaimers.append(disclaimer)
                
                logger.info(f"[{search_id}] China Hub Probe task completed. Found {len(parsed_probed_deals)} probe deals.")
            else:
                logger.warning(f"[{search_id}] China Hub Probe task returned no results.")
                probe_log = {"status": "completed_no_results"}
                
        except Exception as e:
            logger.error(f"[{search_id}] Error during hub probe task execution: {e}", exc_info=True)
            probe_log = {"status": "error", "error": str(e)}
            # 记录错误但继续处理其他结果

    # --- 5. Combine & Deduplicate Combo Deals ---
    logger.info(f"[{search_id}] Combining and deduplicating combo deals...")
    parsed_combo_deals_from_main: List[schemas.FlightItinerary] = []
    direct_ids = {f.id for f in parsed_direct_flights}

    # Parse non-direct flights from main search
    for it_raw in main_search_raw:
        if it_raw.get('id') not in direct_ids:
            try:
                 # Check segment count again to be sure it's not direct
                 expected_segments = 1 if is_one_way else 2
                 segment_count = 0
                 if is_one_way:
                     segment_count = len(it_raw.get("sector", {}).get("sectorSegments", []))
                 else:
                     segment_count = len(it_raw.get("outbound", {}).get("sectorSegments", [])) + \
                                     len(it_raw.get("inbound", {}).get("sectorSegments", []))

                 if segment_count > expected_segments:
                     parsed = await _parse_kiwi_itinerary(it_raw, is_one_way)
                     parsed_combo_deals_from_main.append(parsed)
                     if parsed.is_self_transfer and "Self-transfer options included" not in disclaimers:
                         disclaimers.append("Self-transfer options included (may require re-checkin).")
                     if parsed.is_hidden_city and "Hidden city deals may be available" not in disclaimers:
                          disclaimers.append("Hidden city deals may be available (require careful booking).")
                     if parsed.is_throwaway_deal and "Throwaway ticket deals may be available" not in disclaimers:
                          disclaimers.append("Throwaway ticket deals may be available (require careful booking and may violate airline terms).")

            except ValueError as e:
                logger.warning(f"[{search_id}] Failed to parse combo itinerary {it_raw.get('id')} from main results: {e}")
            except Exception as e:
                 logger.error(f"[{search_id}] Unexpected error parsing combo itinerary {it_raw.get('id')} from main results: {e}", exc_info=True)


    # Combine main combo deals and probed deals
    combined_deals = parsed_combo_deals_from_main + parsed_probed_deals
    logger.info(f"[{search_id}] Combined deals before deduplication: {len(combined_deals)} (Main: {len(parsed_combo_deals_from_main)}, Probed: {len(parsed_probed_deals)})")

    # Deduplicate based on ID, keeping the "better" one (hidden city > lower price)
    final_combo_deals_dict: Dict[str, schemas.FlightItinerary] = {}
    for deal in combined_deals:
        existing = final_combo_deals_dict.get(deal.id)
        if not existing:
            final_combo_deals_dict[deal.id] = deal
        else:
            # Prioritize hidden city, then lower price
            if deal.is_hidden_city and not existing.is_hidden_city:
                final_combo_deals_dict[deal.id] = deal
            elif not deal.is_hidden_city and existing.is_hidden_city:
                continue # Keep existing hidden city deal
            elif deal.price < existing.price:
                final_combo_deals_dict[deal.id] = deal
            # else: keep existing (either same price or existing is cheaper)

    final_combo_deals = list(final_combo_deals_dict.values())
    logger.info(f"[{search_id}] Combined deals after deduplication: {len(final_combo_deals)}")


    # --- 6. Sort & Limit ---
    logger.info(f"[{search_id}] Sorting and limiting results...")
    # Sort by price ascending
    parsed_direct_flights.sort(key=lambda f: f.price)
    final_combo_deals.sort(key=lambda f: f.price)

    # Limit results
    final_direct = parsed_direct_flights[:request_params.max_results_per_type]
    final_combo = final_combo_deals[:request_params.max_results_per_type]
    logger.info(f"[{search_id}] Final results - Direct: {len(final_direct)}, Combo: {len(final_combo)}")


    # --- 7. Build Response ---
    logger.info(f"[{search_id}] Building final response.")
    return schemas.FlightSearchResponse(
        search_id=search_id,
        direct_flights=final_direct,
        combo_deals=final_combo,
        disclaimers=disclaimers,
        probe_details=probe_log # Include probe log if probing was enabled
    )