# 此文件使当前目录成为一个Python包
# Python将能够正确导入此包中的模块，例如legal_schemas

# 直接从base_schemas模块导入模式类，解决循环导入问题
from app.apis.v1.base_schemas import (
    UserBase, UserCreate, UserResponse,
    Token, TokenData,
    InvitationCodeBase, InvitationCodeCreate, InvitationCodeResponse,
    PoiSearchRequest, AirportInfo, PoiSearchResponse,
    FlightSegment, FlightItinerary,
    FlightSearchRequest, FlightSearchResponse,
    AsyncTaskResponse
)

# 导入仪表盘相关的模式
from app.apis.v1.schemas.dashboard_schemas import (
    RecentSearch, RecentSearchesResponse,
    ApiUsageStat, ApiUsageResponse,
    InvitationCodeDetail, InvitationCodesResponse
)

# 导入法律文本相关的模式
from app.apis.v1.schemas.legal_schemas import (
    LegalTextBase, LegalTextCreate, LegalTextUpdate,
    LegalTextResponse
)

# 这些类现在可以从app.apis.v1.schemas包直接导入