# API 端点调用指南

本文档提供了 AeroScout 后端 API 端点的详细调用指南，旨在帮助前端开发人员理解和使用这些 API。

## 认证

大多数 API 端点需要认证。认证通过在请求的 `Authorization` Header 中提供 Bearer Token 来完成。

`Authorization: Bearer <YOUR_ACCESS_TOKEN>`

通过 `/api/v1/auth/login` 端点成功登录后，可以获取到 `access_token`。

---

## Admin API (`/api/v1/admin`)

### 1. 创建邀请码

*   **端点名称/描述**: 创建一个新的邀请码。此端点意图供管理员使用。
*   **HTTP 方法**: `POST`
*   **完整路径**: `/api/v1/admin/invitations`
*   **认证要求**: 需要用户认证令牌 (Bearer Token)。*注意: 目前实现中未进行严格的管理员角色检查，未来应加入。*
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**: 无
*   **成功响应**:
    *   状态码: `201 Created`
    *   Content-Type: `application/json`
    *   响应体字段:
        *   `invitation_code` (string): 生成的邀请码。
    *   响应体示例:
        ```json
        {
          "invitation_code": "SOME_UNIQUE_CODE_123"
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 用户未认证。
        ```json
        {
          "detail": "Not authenticated"
        }
        ```
    *   `500 Internal Server Error`: 创建邀请码失败。
        ```json
        {
          "detail": "Could not create invitation code."
        }
        ```

### 2. 从配置填充中国枢纽城市

*   **端点名称/描述**: 从应用程序配置中获取中国枢纽城市的 POI 数据，并尝试将它们添加到数据库。
*   **HTTP 方法**: `POST`
*   **完整路径**: `/api/v1/admin/populate-hubs`
*   **认证要求**: 需要用户认证令牌 (Bearer Token)。
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**: 无
*   **成功响应**:
    *   状态码: `200 OK` (根据代码，实际返回的可能是 `200 OK`，尽管装饰器指定 `response_model=Dict[str, str]`)
    *   Content-Type: `application/json`
    *   响应体字段:
        *   `message` (string): 描述操作结果的消息，例如 "Hub population attempted. Added: X, Failed: Y"。
    *   响应体示例:
        ```json
        {
          "message": "Hub population attempted. Added: 5, Failed: 0"
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 用户未认证。
        ```json
        {
          "detail": "Not authenticated"
        }
        ```
    *   `500 Internal Server Error`: 解析配置 `CHINA_HUB_CITIES_FOR_PROBE` 失败，或在处理过程中发生其他内部错误。
        ```json
        {
          "detail": "Failed to parse CHINA_HUB_CITIES_FOR_PROBE setting: <error_details>"
        }
        ```
        或者
        ```json
        {
          "detail": "Internal server error during hub population." // 假设的通用错误
        }
        ```

---

## Auth API (`/api/v1/auth`)

### 1. 注册新用户

*   **端点名称/描述**: 注册一个新用户。
*   **HTTP 方法**: `POST`
*   **完整路径**: `/api/v1/auth/register`
*   **认证要求**: 无
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**:
    *   Content-Type: `application/json`
    *   字段:
        *   `email` (string,必需): 用户的电子邮件地址。示例: `"user@example.com"`
        *   `password` (string, 必需, min_length=8): 用户的密码。示例: `"strongpassword"`
        *   `invitation_code` (string, 必需):有效的邀请码。示例: `"VALID_INV_CODE_123"`
    *   请求体示例:
        ```json
        {
          "email": "newuser@example.com",
          "password": "password123",
          "invitation_code": "VALID_INV_CODE_123"
        }
        ```
*   **成功响应**:
    *   状态码: `201 Created`
    *   Content-Type: `application/json`
    *   响应体字段 (参考 `UserResponse` schema):
        *   `id` (integer): 用户 ID。
        *   `email` (string): 用户邮箱。
        *   `is_active` (boolean): 用户是否激活。
        *   `created_at` (datetime): 用户创建时间。
        *   `last_login_at` (datetime, optional): 用户上次登录时间。
        *   `api_call_count_today` (integer): 当日 API 调用次数。
        *   `last_api_call_date` (datetime, optional): 上次 API 调用日期。
    *   响应体示例:
        ```json
        {
          "id": 1,
          "email": "newuser@example.com",
          "is_active": true,
          "created_at": "2023-10-27T10:00:00Z",
          "last_login_at": null,
          "api_call_count_today": 0,
          "last_api_call_date": null
        }
        ```
*   **错误响应**:
    *   `400 Bad Request`: 邀请码无效或已被使用，或邮箱已被注册。
        ```json
        {
          "detail": "Invalid or used invitation code."
        }
        ```
        或者
        ```json
        {
          "detail": "Email already registered."
        }
        ```
    *   `422 Unprocessable Entity`: 请求体验证失败 (例如，密码太短)。
        ```json
        {
          "detail": [
            {
              "loc": [
                "body",
                "password"
              ],
              "msg": "ensure this value has at least 8 characters",
              "type": "value_error.any_str.min_length",
              "ctx": {
                "limit_value": 8
              }
            }
          ]
        }
        ```

### 2. 用户登录获取令牌

*   **端点名称/描述**: 认证用户并返回访问令牌。
*   **HTTP 方法**: `POST`
*   **完整路径**: `/api/v1/auth/login`
*   **认证要求**: 无
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**:
    *   Content-Type: `application/x-www-form-urlencoded` (FastAPI 的 `OAuth2PasswordRequestForm` 期望这种格式)
    *   字段:
        *   `username` (string, 必需): 用户的电子邮件地址。
        *   `password` (string, 必需): 用户的密码。
    *   请求体示例 (form-data):
        ```
        username=user@example.com&password=strongpassword
        ```
*   **成功响应**:
    *   状态码: `200 OK`
    *   Content-Type: `application/json`
    *   响应体字段 (参考 `Token` schema):
        *   `access_token` (string): JWT 访问令牌。
        *   `token_type` (string): 令牌类型，通常为 "bearer"。
    *   响应体示例:
        ```json
        {
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "bearer"
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 邮箱或密码不正确。
        ```json
        {
          "detail": "Incorrect email or password"
        }
        ```
    *   `422 Unprocessable Entity`: 请求体验证失败 (例如，缺少字段)。

---

## Flights API (`/api/v1/flights`)

### 1. 异步搜索航班

*   **端点名称/描述**: 提交一个航班搜索任务到后台队列。需要认证并进行速率限制。返回一个任务 ID 用于稍后轮询结果。
*   **HTTP 方法**: `POST`
*   **完整路径**: `/api/v1/flights/search`
*   **认证要求**: 需要用户认证令牌 (Bearer Token)。
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**:
    *   Content-Type: `application/json`
    *   字段 (参考 `FlightSearchRequest` schema):
        *   `origin_iata` (string, 必需): 出发机场 IATA 代码。示例: `"PVG"`
        *   `destination_iata` (string, 必需): 到达机场 IATA 代码。示例: `"SFO"`
        *   `departure_date_from` (string, 必需, YYYY-MM-DD): 出发日期开始。示例: `"2024-10-26"`
        *   `departure_date_to` (string, 必需, YYYY-MM-DD): 出发日期结束。示例: `"2024-10-28"`
        *   `return_date_from` (string, 可选, YYYY-MM-DD): 返程日期开始 (往返行程)。示例: `"2024-11-10"`
        *   `return_date_to` (string, 可选, YYYY-MM-DD): 返程日期结束 (往返行程)。示例: `"2024-11-12"`
        *   `cabin_class` (string, 默认: "ECONOMY"): 舱位等级 (例如, "ECONOMY", "BUSINESS")。示例: `"ECONOMY"`
        *   `adults` (integer, 默认: 1, ge=1): 成人乘客数量。示例: `1`
        *   `direct_flights_only_for_primary` (boolean, 默认: false): 是否仅搜索主要始发地-目的地对的直飞航班。
        *   `enable_hub_probe` (boolean, 默认: true): 是否启用通过中国枢纽进行探测以获取可能更便宜的票价。
        *   `max_probe_hubs` (integer, 默认: 5, ge=0): 要探测的最大中国枢纽数量。示例: `5`
        *   `max_results_per_type` (integer, 默认: 20, ge=1): 每种类型（直飞、组合）返回的最大结果数。示例: `20`
        *   `max_pages_per_search` (integer, 默认: 5, ge=1): 每次搜索航段获取的最大 Kiwi 搜索结果页数。示例: `5`
        *   `adult_hold_bags` (array of integers, 可选): 每位成人的托运行李数量。示例: `[1]`
        *   `adult_hand_bags` (array of integers, 可选): 每位成人的手提行李数量。示例: `[1]`
        *   `preferred_currency` (string, 可选): 价格的首选货币 (例如, 'USD', 'EUR')。示例: `"EUR"`
        *   `preferred_locale` (string, 可选): 结果的首选区域设置 (例如, 'en', 'zh')。示例: `"en"`
        *   `market` (string, 默认: "cn"): 搜索的市场代码 (例如, 'us', 'cn')。示例: `"cn"`
    *   请求体示例:
        ```json
        {
          "origin_iata": "PVG",
          "destination_iata": "SFO",
          "departure_date_from": "2024-12-01",
          "departure_date_to": "2024-12-03",
          "adults": 1,
          "enable_hub_probe": true
        }
        ```
*   **成功响应**:
    *   状态码: `202 Accepted`
    *   Content-Type: `application/json`
    *   响应体字段 (参考 `AsyncTaskResponse` schema):
        *   `task_id` (string): Celery 任务的 ID。
        *   `status` (string): 任务提交状态，通常为 "Task submitted successfully."。
    *   响应体示例:
        ```json
        {
          "task_id": "some-celery-task-uuid",
          "status": "Task submitted successfully."
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 用户未认证。
    *   `422 Unprocessable Entity`: 请求体验证失败。
    *   `429 Too Many Requests`: 超出速率限制。
        ```json
        {
            "detail": "Rate limit exceeded for flight searches."
        }
        ```
    *   `500 Internal Server Error`: 提交航班搜索任务失败。
        ```json
        {
          "detail": "Failed to submit flight search task."
        }
        ```

---

## POI API (`/api/v1/poi`)

### 1. 搜索兴趣点 (POI)

*   **端点名称/描述**: 使用 Trip.com API 搜索 POI (例如机场、城市)，受速率限制。
*   **HTTP 方法**: `POST`
*   **完整路径**: `/api/v1/poi/search`
*   **认证要求**: 需要用户认证令牌 (Bearer Token)。
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**:
    *   Content-Type: `application/json`
    *   字段 (参考 `PoiSearchRequest` schema):
        *   `query` (string, 必需): POI 的搜索查询 (例如，机场名称、城市)。示例: `"Beijing"`
        *   `trip_type` (string, 必需): 行程上下文类型 (例如, 'flight', 'hotel')。示例: `"flight"`
        *   `mode` (string, 必需): 搜索模式 (例如, 'dep', 'arr')。示例: `"dep"`
    *   请求体示例:
        ```json
        {
          "query": "Shanghai",
          "trip_type": "flight",
          "mode": "dep"
        }
        ```
*   **成功响应**:
    *   状态码: `200 OK`
    *   Content-Type: `application/json`
    *   响应体字段 (参考 `PoiSearchResponse` schema):
        *   `success` (boolean): 指示请求是否成功。
        *   `data` (object): 从 Trip.com API 直接返回的原始字典数据。结构可能因查询而异。
    *   响应体示例 (结构可能变化):
        ```json
        {
          "success": true,
          "data": {
            // ... Trip.com API 返回的 POI 数据 ...
            "keyword": "Shanghai",
            "results": [
                // ... 搜索结果 ...
            ]
          }
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 用户未认证。
    *   `404 Not Found`: 未找到 POI 数据或发生错误。
        ```json
        {
          "detail": "POI data not found or error occurred."
        }
        ```
    *   `422 Unprocessable Entity`: 请求体验证失败。
    *   `429 Too Many Requests`: 超出速率限制。
        ```json
        {
            "detail": "Rate limit exceeded for POI searches."
        }
        ```
    *   `500 Internal Server Error`: POI 搜索期间发生内部服务器错误。
        ```json
        {
          "detail": "Internal server error during POI search."
        }
        ```

---

## Tasks API (`/api/v1/tasks`)

### 1. 获取 Celery 任务状态和结果

*   **端点名称/描述**: 检索 Celery 任务的状态和结果。需要认证。
*   **HTTP 方法**: `GET`
*   **完整路径**: `/api/v1/tasks/results/{task_id}`
*   **认证要求**: 需要用户认证令牌 (Bearer Token)。
*   **路径参数**:
    *   `task_id` (string, 必需): 要检索的 Celery 任务的 ID。
*   **查询参数**: 无
*   **请求体**: 无
*   **成功响应**:
    *   状态码: `200 OK`
    *   Content-Type: `application/json`
    *   响应体字段 (根据任务状态变化):
        *   `task_id` (string): 任务 ID。
        *   `status` (string): 任务状态 (例如, "PENDING", "STARTED", "SUCCESS", "RETRY")。
        *   `message` (string, 可选): 描述任务状态的消息。
        *   `result` (any, 可选): 如果任务成功，则为任务结果。对于航班搜索，这应该是 `FlightSearchResponse` schema 的结构。
        *   `meta` (object, 可选): 任务的元数据 (例如，在 "STARTED" 或 "RETRY" 状态下)。
    *   响应体示例 (任务成功 - 航班搜索):
        ```json
        {
          "task_id": "some-celery-task-uuid",
          "status": "SUCCESS",
          "result": {
            "search_id": "search_uuid_12345",
            "direct_flights": [
              // ... FlightItinerary 对象列表 ...
            ],
            "combo_deals": [
              // ... FlightItinerary 对象列表 ...
            ],
            "disclaimers": ["Self-transfer itineraries require separate check-ins."],
            "probe_details": { /* ... */ }
          }
        }

        #### `FlightItinerary` 对象详细定义

        `/api/v1/tasks/results/{task_id}` 接口返回的 `result` 对象中，`direct_flights` 和 `combo_deals` 数组的每个元素都是一个 `FlightItinerary` 对象。其结构定义如下：

        | 字段名                     | Python 数据类型             | 可选性   | 描述                                                     |
        | -------------------------- | --------------------------- | -------- | -------------------------------------------------------- |
        | `id`                       | `str`                       | 必需     | Kiwi 行程 ID                                             |
        | `price_eur`                | `float`                     | 必需     | 总价 (EUR)                                               |
        | `booking_token`            | `str`                       | 必需     | Kiwi 预订令牌                                            |
        | `deep_link`                | `str`                       | 必需     | Kiwi 预订深度链接                                        |
        | `outbound_segments`        | `Optional[List[FlightSegment]]` | 可选     | 出发航班航段列表                                         |
        | `inbound_segments`         | `Optional[List[FlightSegment]]` | 可选     | 返程航班航段列表 (往返行程)                                |
        | `segments`                 | `Optional[List[FlightSegment]]` | 可选     | 原始航段列表 (为清晰起见，请使用 outbound/inbound)         |
        | `total_duration_minutes`   | `int`                       | 必需     | 总时长 (包括中转，单位：分钟)                             |
        | `is_self_transfer`         | `bool`                      | 必需     | 是否涉及自我中转                                         |
        | `is_hidden_city`           | `bool`                      | 必需     | 是否为潜在的隐藏城市票务结果                             |
        | `data_source`              | `str`                       | 必需     | 航班数据来源 (默认为 "kiwi")                             |
        | `is_throwaway_deal`        | `Optional[bool]`            | 可选     | 是否为潜在的“抛弃型”机票 (枢纽探测)                      |
        | `raw_data`                 | `Optional[Dict[str, Any]]`  | 可选     | 来自源 API 的可选原始数据                                  |

        #### `FlightSegment` 对象详细定义

        在 `FlightItinerary` 对象中，`outbound_segments`、`inbound_segments` 和 `segments` 数组包含 `FlightSegment` 对象列表。每个 `FlightSegment` 对象的结构定义如下：

        | 字段名                               | Python 数据类型        | 可选性   | 描述                                                       |
        | ------------------------------------ | ---------------------- | -------- | ---------------------------------------------------------- |
        | `segment_id`                         | `Optional[str]`        | 可选     | Kiwi 航段 ID                                               |
        | `departure_airport`                  | `str`                  | 必需     | 出发机场 IATA 代码                                         |
        | `departure_airport_name`             | `Optional[str]`        | 可选     | 出发机场名称                                               |
        | `departure_city`                     | `Optional[str]`        | 可选     | 出发城市名称                                               |
        | `arrival_airport`                    | `str`                  | 必需     | 到达机场 IATA 代码                                         |
        | `arrival_airport_name`               | `Optional[str]`        | 可选     | 到达机场名称                                               |
        | `arrival_city`                       | `Optional[str]`        | 可选     | 到达城市名称                                               |
        | `departure_time`                     | `datetime`             | 必需     | 本地出发时间                                               |
        | `arrival_time`                       | `datetime`             | 必需     | 本地到达时间                                               |
        | `departure_time_utc`                 | `Optional[datetime]`   | 可选     | UTC 出发时间                                               |
        | `arrival_time_utc`                   | `Optional[datetime]`   | 可选     | UTC 到达时间                                               |
        | `duration_minutes`                   | `int`                  | 必需     | 航段时长 (分钟)                                            |
        | `carrier_code`                       | `str`                  | 必需     | 承运航空公司 IATA 代码                                     |
        | `carrier_name`                       | `Optional[str]`        | 可选     | 承运航空公司名称                                           |
        | `operating_carrier_code`             | `Optional[str]`        | 可选     | 实际承运航空公司 IATA 代码 (如果不同)                      |
        | `operating_carrier_name`             | `Optional[str]`        | 可选     | 实际承运航空公司名称 (如果不同)                            |
        | `flight_number`                      | `str`                  | 必需     | 航班号                                                     |
        | `cabin_class`                        | `Optional[str]`        | 可选     | 舱位等级 (例如, ECONOMY, BUSINESS)                         |
        | `aircraft`                           | `Optional[str]`        | 可选     | 飞机型号                                                   |
        | `layover_duration_minutes`           | `Optional[int]`        | 可选     | 此航段后的中转时长 (分钟)                                  |
        | `is_baggage_recheck`                 | `Optional[bool]`       | 可选     | 此航段后的中转期间是否需要重新托运行李                     |
        | `departure_terminal`                 | `Optional[str]`        | 可选     | 出发航站楼                                                 |
        | `arrival_terminal`                   | `Optional[str]`        | 可选     | 到达航站楼                                                 |
        | `next_segment_requires_airport_change` | `Optional[bool]`       | 可选     | 此航段后的下一航段是否需要更换机场                         |
        ```
    *   响应体示例 (任务进行中):
        ```json
        {
          "task_id": "some-celery-task-uuid",
          "status": "STARTED",
          "message": "Task has started processing.",
          "meta": {}
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 用户未认证。
    *   `404 Not Found`: 如果 `task_id` 无效或任务不存在 (尽管当前实现可能返回特定状态而不是 404)。
    *   `500 Internal Server Error`: 任务执行失败。
        ```json
        {
          "detail": {
            "task_id": "some-celery-task-uuid",
            "status": "FAILURE",
            "error": {
              "type": "SpecificExceptionName",
              "message": "Task execution failed."
            },
            "message": "Task encountered an error."
          }
        }
        ```

---

## Users API (`/api/v1/users`)

### 1. 获取当前登录用户信息

*   **端点名称/描述**: 获取当前已登录用户的信息。
*   **HTTP 方法**: `GET`
*   **完整路径**: `/api/v1/users/me`
*   **认证要求**: 需要用户认证令牌 (Bearer Token)。
*   **路径参数**: 无
*   **查询参数**: 无
*   **请求体**: 无
*   **成功响应**:
    *   状态码: `200 OK`
    *   Content-Type: `application/json`
    *   响应体字段 (参考 `UserResponse` schema):
        *   `id` (integer): 用户 ID。
        *   `email` (string): 用户邮箱。
        *   `is_active` (boolean): 用户是否激活。
        *   `created_at` (datetime): 用户创建时间。
        *   `last_login_at` (datetime, optional): 用户上次登录时间。
        *   `api_call_count_today` (integer): 当日 API 调用次数。
        *   `last_api_call_date` (datetime, optional): 上次 API 调用日期。
    *   响应体示例:
        ```json
        {
          "id": 1,
          "email": "user@example.com",
          "is_active": true,
          "created_at": "2023-10-27T10:00:00Z",
          "last_login_at": "2023-10-28T12:00:00Z",
          "api_call_count_today": 5,
          "last_api_call_date": "2023-10-28T00:00:00Z"
        }
        ```
*   **错误响应**:
    *   `401 Unauthorized`: 用户未认证或令牌无效/过期。
        ```json
        {
          "detail": "Not authenticated"
        }
        ```
        或者
        ```json
        {
          "detail": "Could not validate credentials"
        }
        ```

---