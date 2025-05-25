# AeroScout 数据映射与集成指南

本文档提供了关于 AeroScout 前端与后端 API 数据映射和集成的最佳实践和指导。

## 目录

1. [数据流概述](#数据流概述)
2. [API 响应结构](#api-响应结构)
3. [数据映射函数](#数据映射函数)
4. [特殊字段处理](#特殊字段处理)
5. [测试与验证](#测试与验证)
6. [常见问题与解决方案](#常见问题与解决方案)

## 数据流概述

AeroScout 前端与后端的数据流如下：

1. 用户在前端发起航班搜索请求
2. 后端创建一个异步任务并返回 `task_id`
3. 前端使用 `task_id` 轮询任务结果
4. 后端返回任务结果，包含航班数据
5. 前端使用 `mapApiItineraryToStoreItinerary` 函数将 API 数据映射到前端状态
6. 前端使用映射后的数据渲染 UI 组件（如 `FlightCard`）

## API 响应结构

后端 API 返回的航班搜索结果结构如下：

```typescript
interface TaskResultResponse {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | string;
  result?: {
    search_id?: string;
    direct_flights?: ApiFlightItinerary[];
    combo_deals?: ApiFlightItinerary[];
    disclaimers?: string[];
    probe_details?: Record<string, unknown>;
  } | null;
  error?: string | null;
}
```

其中 `ApiFlightItinerary` 是航班行程数据，包含以下关键字段：

- `id`: 行程唯一标识符
- `priceEur`: 价格（欧元）
- `priceCurrency`: 货币代码（可选）
- `bookingToken`: 预订令牌
- `deepLink`: 预订链接
- `segments`: 航段数组
- `totalDurationMinutes`: 总行程时长（分钟）
- `isSelfTransfer`: 是否自行中转
- `isHiddenCity`: 是否隐藏城市票
- `isThrowawayDeal`: 是否为探测特惠
- `dataSource`: 数据来源
- `rawData`: 原始数据（可选）

## 数据映射函数

`mapApiItineraryToStoreItinerary` 函数负责将 API 返回的 `ApiFlightItinerary` 映射为前端状态使用的 `FlightItinerary`。

### 主要映射逻辑

1. **基本字段映射**：直接映射 id、价格、预订链接等基本字段
2. **计算派生字段**：
   - `totalTravelTime`: 格式化的总行程时间（如 "3h 45m"）
   - `isDirectFlight`: 根据 segments 长度或 API 提供的标志确定
   - `numberOfStops`: 计算中转次数
3. **特殊字段处理**：
   - `probeHub` 和 `probeDisclaimer`: 从 rawData 中提取
   - `transfers`: 根据相邻航段构建中转信息
   - `airlines`: 从所有航段中提取唯一航司信息

### 示例

```typescript
// API 数据
const apiItinerary = {
  id: "flight-123",
  priceEur: 450.75,
  segments: [/* 航段数据 */],
  totalDurationMinutes: 180,
  // ...其他字段
};

// 映射后的数据
const storeItinerary = mapApiItineraryToStoreItinerary(apiItinerary);
// 结果包含额外的派生字段如 totalTravelTime, transfers 等
```

## 特殊字段处理

### 中转信息 (transfers)

中转信息是根据相邻航段计算的，包括：

- 中转城市
- 中转时长
- 是否需要换机场
- 是否需要重新托运行李
- 是否更换航空公司

```typescript
// 中转信息示例
transfers: [
  {
    city: "Tokyo",
    durationMinutes: 120,
    isDifferentAirport: true,
    airportChangeDetail: {
      fromAirportCode: "NRT",
      toAirportCode: "HND"
    },
    layoverTime: "2h",
    isBaggageRecheck: true,
    isAirlineChange: true,
    fromAirline: { code: "MU", name: "China Eastern" },
    toAirline: { code: "JL", name: "Japan Airlines" }
  }
]
```

### 探测特惠 (isProbeSuggestion)

探测特惠是一种特殊的票价类型，通常涉及"跳机"行为。前端需要显示明确的风险提示。

- `isProbeSuggestion` 映射自 API 的 `isThrowawayDeal`
- `probeHub` 和 `probeDisclaimer` 从 `rawData` 中提取

### 航空公司信息 (airlines)

航空公司信息是从所有航段中提取的唯一航司列表：

```typescript
airlines: [
  { code: "MU", name: "China Eastern", logoUrl: "https://..." },
  { code: "JL", name: "Japan Airlines", logoUrl: "https://..." }
]
```

## 测试与验证

为确保数据映射的正确性，我们提供了以下测试工具：

1. **单元测试**：`flightResultsStore.test.ts` 包含对映射函数的测试
2. **模拟数据**：`mockFlightData.ts` 提供了各种场景的模拟数据
3. **测试页面**：`/test/mapping` 页面可用于可视化测试映射结果

## 常见问题与解决方案

### 1. 中转信息不完整

**问题**：中转信息（如城市、时长）显示不完整或不正确。

**解决方案**：
- 确保 API 返回的航段数据包含完整的出发/到达信息
- 检查时间格式是否一致，确保时区处理正确
- 验证相邻航段的到达/出发时间差计算是否正确

### 2. 探测特惠标识不正确

**问题**：探测特惠航班没有正确标识或显示风险提示。

**解决方案**：
- 确保 API 正确设置了 `isThrowawayDeal` 标志
- 检查 `rawData` 中是否包含 `probeHub` 和 `probeDisclaimer` 信息
- 验证 UI 组件是否正确处理 `isProbeSuggestion` 标志

### 3. 航空公司信息不完整

**问题**：航空公司信息（如名称、图标）显示不完整。

**解决方案**：
- 确保 API 返回的航段数据包含完整的航空公司信息
- 检查航空公司 Logo URL 构建逻辑
- 考虑使用本地缓存的航空公司信息作为备份

---

本指南将随着项目的发展不断更新。如有问题或建议，请联系开发团队。
