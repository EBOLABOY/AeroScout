from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any

# --- User Schemas ---

class UserBase(BaseModel):
    """Base User Schema"""
    email: EmailStr = Field(..., json_schema_extra={"example": "user@example.com"})

class UserCreate(UserBase):
    """Schema for User Creation"""
    password: str = Field(..., min_length=8, json_schema_extra={"example": "strongpassword"})
    invitation_code: str = Field(..., json_schema_extra={"example": "VALID_INV_CODE_123"})

class UserResponse(UserBase):
    """Schema for User Response (excluding sensitive data)"""
    id: int = Field(..., json_schema_extra={"example": 1})
    is_admin: bool # Added is_admin field
    is_active: bool = Field(default=True, json_schema_extra={"example": True})
    created_at: datetime
    last_login_at: Optional[datetime] = None
    api_call_count_today: int = Field(default=0, json_schema_extra={"example": 10})
    last_api_call_date: Optional[datetime] = None # Store as datetime for ORM compatibility, handle date logic in service

    model_config = ConfigDict(from_attributes=True) # Replaces Config class in Pydantic v2

# --- Token Schemas ---

class Token(BaseModel):
    """JWT Token Schema"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Data contained within the JWT Token"""
    email: Optional[EmailStr] = None

# --- Invitation Code Schemas ---

class InvitationCodeBase(BaseModel):
    """Base Invitation Code Schema"""
    code: str = Field(..., json_schema_extra={"example": "UNIQUE_INV_CODE_XYZ"})

class InvitationCodeCreate(InvitationCodeBase):
    """Schema for Creating an Invitation Code (currently same as base)"""
    pass # No additional fields needed for creation via this schema for now

class InvitationCodeResponse(InvitationCodeBase):
    """Schema for Invitation Code Response"""
    id: int = Field(..., json_schema_extra={"example": 1})
    is_used: bool = Field(default=False, json_schema_extra={"example": False})
    created_by_user_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    used_by_user_id: Optional[int] = Field(None, json_schema_extra={"example": 2})
    created_at: datetime
    used_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) # Replaces Config class in Pydantic v2

# --- POI Schemas ---

class PoiSearchRequest(BaseModel):
    """Schema for POI Search Request"""
    query: str = Field(..., description="Search query for POI (e.g., airport name, city)", json_schema_extra={"example": "Beijing"})
    trip_type: str = Field(..., description="Type of trip context (e.g., 'flight', 'hotel')", json_schema_extra={"example": "flight"})
    mode: str = Field(..., description="Search mode (e.g., 'dep', 'arr')", json_schema_extra={"example": "dep"})

class AirportInfo(BaseModel):
    """标准化的机场信息模型"""
    code: str = Field(..., description="机场IATA代码", json_schema_extra={"example": "PEK"})
    name: str = Field(..., description="机场名称", json_schema_extra={"example": "北京首都国际机场"})
    city: str = Field(..., description="城市名称", json_schema_extra={"example": "北京"})
    country: str = Field(..., description="国家名称", json_schema_extra={"example": "中国"})
    type: str = Field(..., description="POI类型", json_schema_extra={"example": "AIRPORT"})

class PoiSearchResponse(BaseModel):
    """优化后的POI搜索响应"""
    success: bool = Field(..., description="请求是否成功")
    airports: List[AirportInfo] = Field(..., description="机场列表")
    total: int = Field(..., description="结果总数")
    query: str = Field(..., description="搜索关键词")

# --- Flight Schemas ---

class FlightSearchRequest(BaseModel):
    """Schema for Flight Search Request"""
    origin_iata: str = Field(..., description="Origin airport IATA code", json_schema_extra={"example": "PVG"})
    destination_iata: str = Field(..., description="Destination airport IATA code", json_schema_extra={"example": "SFO"})
    departure_date_from: str = Field(..., description="Departure date start (YYYY-MM-DD)", json_schema_extra={"example": "2024-10-26"})
    departure_date_to: str = Field(..., description="Departure date end (YYYY-MM-DD)", json_schema_extra={"example": "2024-10-28"})
    return_date_from: Optional[str] = Field(None, description="Return date start (YYYY-MM-DD, for round trips)", json_schema_extra={"example": "2024-11-10"})
    return_date_to: Optional[str] = Field(None, description="Return date end (YYYY-MM-DD, for round trips)", json_schema_extra={"example": "2024-11-12"})
    cabin_class: str = Field("ECONOMY", description="Cabin class (e.g., ECONOMY, BUSINESS)", json_schema_extra={"example": "ECONOMY"})
    adults: int = Field(1, description="Number of adult passengers", json_schema_extra={"example": 1}, ge=1)
    direct_flights_only_for_primary: bool = Field(False, description="Search only direct flights for the primary origin-destination pair")
    enable_hub_probe: bool = Field(True, description="Enable probing via Chinese hubs for potentially cheaper fares")
    max_probe_hubs: int = Field(5, description="Maximum number of Chinese hubs to probe", json_schema_extra={"example": 5}, ge=0)
    max_results_per_type: int = Field(20, description="Maximum results to return per type (direct, combo)", json_schema_extra={"example": 20}, ge=1)
    max_pages_per_search: int = Field(5, description="Maximum Kiwi search result pages to fetch per search leg", json_schema_extra={"example": 5}, ge=1)
    adult_hold_bags: Optional[List[int]] = Field(None, description="Number of hold bags per adult (e.g., [1, 0] for 1 bag for first adult, 0 for second)", json_schema_extra={"example": [1]})
    adult_hand_bags: Optional[List[int]] = Field(None, description="Number of hand bags per adult (e.g., [1, 1])", json_schema_extra={"example": [1]})
    preferred_currency: Optional[str] = Field(None, description="Preferred currency for prices (e.g., 'USD', 'EUR')", json_schema_extra={"example": "EUR"})
    preferred_locale: Optional[str] = Field(None, description="Preferred locale for results (e.g., 'en', 'zh')", json_schema_extra={"example": "en"})
    market: Optional[str] = Field("cn", description="Market code for the search (e.g., 'us', 'cn')", json_schema_extra={"example": "cn"})

# --- Flight Segment and Itinerary Schemas ---

class FlightSegment(BaseModel):
    """Schema representing a single flight segment."""
    segment_id: Optional[str] = Field(None, description="Kiwi segment ID", json_schema_extra={"example": "segment_abc_123"})
    departure_airport: str = Field(..., json_schema_extra={"example": "PVG"})
    departure_airport_name: Optional[str] = Field(None, json_schema_extra={"example": "Shanghai Pudong International Airport"})
    departure_city: Optional[str] = Field(None, json_schema_extra={"example": "Shanghai"})
    arrival_airport: str = Field(..., json_schema_extra={"example": "SFO"})
    arrival_airport_name: Optional[str] = Field(None, json_schema_extra={"example": "San Francisco International Airport"})
    arrival_city: Optional[str] = Field(None, json_schema_extra={"example": "San Francisco"})
    departure_time: datetime = Field(..., description="Local departure time", json_schema_extra={"example": "2024-10-26T10:00:00"})
    arrival_time: datetime = Field(..., description="Local arrival time", json_schema_extra={"example": "2024-10-26T08:30:00"}) # Example: Crossing date line
    departure_time_utc: Optional[datetime] = Field(None, description="UTC departure time", json_schema_extra={"example": "2024-10-26T02:00:00Z"})
    arrival_time_utc: Optional[datetime] = Field(None, description="UTC arrival time", json_schema_extra={"example": "2024-10-26T15:30:00Z"})
    duration_minutes: int = Field(..., json_schema_extra={"example": 750})
    carrier_code: str = Field(..., json_schema_extra={"example": "MU"})
    carrier_name: Optional[str] = Field(None, json_schema_extra={"example": "China Eastern Airlines"})
    operating_carrier_code: Optional[str] = Field(None, json_schema_extra={"example": "MU"})
    operating_carrier_name: Optional[str] = Field(None, json_schema_extra={"example": "China Eastern Airlines"})
    flight_number: str = Field(..., json_schema_extra={"example": "587"})
    cabin_class: Optional[str] = Field(None, description="Cabin class (e.g., ECONOMY, BUSINESS)", json_schema_extra={"example": "BUSINESS"})
    aircraft: Optional[str] = Field(None, json_schema_extra={"example": "Boeing 777"}) # Note: Kiwi API example doesn't seem to provide this directly per segment
    layover_duration_minutes: Optional[int] = Field(None, description="Duration of layover AFTER this segment in minutes", json_schema_extra={"example": 120})
    is_baggage_recheck: Optional[bool] = Field(None, description="Indicates if baggage recheck is needed during layover AFTER this segment", json_schema_extra={"example": True})
    departure_terminal: Optional[str] = Field(None, description="Departure terminal", json_schema_extra={"example": "T2"})
    arrival_terminal: Optional[str] = Field(None, description="Arrival terminal", json_schema_extra={"example": "T1"})
    next_segment_requires_airport_change: Optional[bool] = Field(None, description="Indicates if the next segment after this one requires an airport change", json_schema_extra={"example": False})
    hidden_destination: Optional[Dict[str, Any]] = Field(None, description="Hidden destination info for this segment", json_schema_extra={"example": {"code": "XMN", "name": "厦门高崎国际机场", "city_name": "厦门"}})


class FlightItinerary(BaseModel):
    """Schema representing a complete flight itinerary (potentially multi-segment)."""
    id: str = Field(..., description="Kiwi itinerary ID", json_schema_extra={"example": "kiwi_itinerary_123abc"})
    price: float = Field(..., description="Total price in CNY", json_schema_extra={"example": 3850.25})
    currency: str = Field("CNY", description="Currency of the price (always CNY)", json_schema_extra={"example": "CNY"})
    booking_token: str = Field(..., description="Kiwi booking token", json_schema_extra={"example": "long_booking_token_xyz"})
    deep_link: str = Field(..., description="Kiwi deep link for booking", json_schema_extra={"example": "https://kiwi.com/..."})
    outbound_segments: Optional[List[FlightSegment]] = Field(None, description="List of outbound flight segments")
    inbound_segments: Optional[List[FlightSegment]] = Field(None, description="List of inbound flight segments (for round trips)")
    segments: Optional[List[FlightSegment]] = Field(None, description="Original list of segments (use outbound/inbound for clarity)") # Keep for potential backward compatibility or specific use cases, but prefer new fields
    total_duration_minutes: int = Field(..., description="Total duration including layovers", json_schema_extra={"example": 900})
    is_self_transfer: bool = Field(..., description="Indicates if the itinerary involves self-transfer", json_schema_extra={"example": False})
    is_hidden_city: bool = Field(..., description="Indicates if this is a potential hidden-city ticketing result", json_schema_extra={"example": False})
    hidden_destination: Optional[Dict[str, str]] = Field(None, description="Hidden destination info for throwaway tickets", json_schema_extra={"example": {"code": "XMN", "name": "厦门高崎国际机场", "city": "厦门", "country": "中国"}})
    data_source: str = Field("kiwi", description="Source of the flight data", json_schema_extra={"example": "kiwi"})
    is_throwaway_deal: Optional[bool] = Field(False, description="Indicates if this itinerary is a potential throwaway deal found via hub probing", json_schema_extra={"example": False})
    # 中国中转城市探测相关字段
    isProbeSuggestion: Optional[bool] = Field(False, description="Indicates if this itinerary is a probe suggestion (special deal via Chinese hub)", json_schema_extra={"example": False})
    probeHub: Optional[str] = Field(None, description="IATA code of the Chinese hub used for probing", json_schema_extra={"example": "PEK"})
    probeDisclaimer: Optional[str] = Field(None, description="Risk disclaimer for probe suggestion", json_schema_extra={"example": "此优惠可能依赖于您在特定中转点放弃后续行程（俗称\"跳机\"），这可能违反航空公司的运输条款。"})
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Optional raw data from the source API")

    model_config = ConfigDict(from_attributes=True) # Add model_config

class FlightSearchResponse(BaseModel):
    """Schema for Flight Search Response"""
    search_id: str = Field(..., description="Unique identifier for this search request", json_schema_extra={"example": "search_uuid_12345"})
    direct_flights: List[FlightItinerary] = Field(..., description="List of direct flight itineraries found")
    combo_deals: List[FlightItinerary] = Field(..., description="List of combined deals (non-direct and probed hub itineraries)")
    disclaimers: List[str] = Field([], description="List of disclaimers (e.g., self-transfer risks, hidden city warnings)", json_schema_extra={"example": ["Self-transfer itineraries require separate check-ins."]})
    probe_details: Optional[dict] = Field(None, description="Optional details about the hub probing process for debugging")

    model_config = ConfigDict(from_attributes=True) # Add model_config

# --- Task Schemas ---

class AsyncTaskResponse(BaseModel):
    """Standard response model for endpoints that trigger async tasks."""
    task_id: str
    status: str = "Task submitted successfully."