"""
甩尾航班（隐藏城市票）搜索策略
"""

import time
from typing import List, Dict, Any

from .base import SearchStrategy, SearchContext, SearchResult, SearchResultStatus
from app.apis.v1.schemas.flights_v2 import EnhancedFlightItinerary, SearchPhase
from app.apis.v1.schemas import FlightItinerary

# 导入现有的任务函数
from app.core.tasks import (
    _task_build_kiwi_variables,
    _task_run_search_with_retry,
    _task_parse_kiwi_itinerary
)

class HiddenCityStrategy(SearchStrategy):
    """甩尾航班（隐藏城市票）搜索策略"""

    def __init__(self):
        super().__init__("hidden_city")
        # 常用的甩尾目的地城市（基于用户目的地选择合适的甩尾城市）
        self.default_throwaway_destinations = {
            # 亚洲主要甩尾目的地
            'asia': ['HKG', 'TPE', 'NRT', 'ICN', 'SIN', 'BKK', 'KUL', 'MNL'],
            # 欧洲主要甩尾目的地
            'europe': ['FRA', 'AMS', 'CDG', 'LHR', 'FCO', 'VIE', 'ZUR'],
            # 北美主要甩尾目的地
            'north_america': ['LAX', 'SFO', 'JFK', 'ORD', 'DFW', 'YVR', 'YYZ'],
            # 中国国内主要甩尾目的地（扩展版，按重要性排序）
            'china': [
                'PEK', 'PKX',  # 北京（首都机场、大兴机场）
                'PVG', 'SHA',  # 上海（浦东、虹桥）
                'CAN',         # 广州
                'SZX',         # 深圳
                'CTU',         # 成都
                'CKG',         # 重庆
                'XIY',         # 西安
                'KMG',         # 昆明
                'WUH',         # 武汉
                'CSX',         # 长沙
                'NKG',         # 南京
                'HGH',         # 杭州
                'XMN',         # 厦门
                'TSN',         # 天津
                'TAO',         # 青岛
                'DLC',         # 大连
                'SHE'          # 沈阳
            ]
        }

        # 机场信息映射（用于生成隐藏目的地信息）
        self.airport_info_map = {
            # 中国机场
            'PEK': {'name': '北京首都国际机场', 'city': '北京', 'country': '中国'},
            'PKX': {'name': '北京大兴国际机场', 'city': '北京', 'country': '中国'},
            'SHA': {'name': '上海虹桥国际机场', 'city': '上海', 'country': '中国'},
            'PVG': {'name': '上海浦东国际机场', 'city': '上海', 'country': '中国'},
            'CAN': {'name': '广州白云国际机场', 'city': '广州', 'country': '中国'},
            'SZX': {'name': '深圳宝安国际机场', 'city': '深圳', 'country': '中国'},
            'CTU': {'name': '成都双流国际机场', 'city': '成都', 'country': '中国'},
            'WUH': {'name': '武汉天河国际机场', 'city': '武汉', 'country': '中国'},
            'XMN': {'name': '厦门高崎国际机场', 'city': '厦门', 'country': '中国'},
            'CSX': {'name': '长沙黄花国际机场', 'city': '长沙', 'country': '中国'},
            'TAO': {'name': '青岛流亭国际机场', 'city': '青岛', 'country': '中国'},
            'NKG': {'name': '南京禄口国际机场', 'city': '南京', 'country': '中国'},
            'HGH': {'name': '杭州萧山国际机场', 'city': '杭州', 'country': '中国'},
            'TSN': {'name': '天津滨海国际机场', 'city': '天津', 'country': '中国'},
            'DLC': {'name': '大连周水子国际机场', 'city': '大连', 'country': '中国'},
            'SYX': {'name': '三亚凤凰国际机场', 'city': '三亚', 'country': '中国'},
            'KMG': {'name': '昆明长水国际机场', 'city': '昆明', 'country': '中国'},

            # 亚洲其他机场
            'HKG': {'name': '香港国际机场', 'city': '香港', 'country': '中国香港'},
            'TPE': {'name': '台湾桃园国际机场', 'city': '台北', 'country': '中国台湾'},
            'NRT': {'name': '成田国际机场', 'city': '东京', 'country': '日本'},
            'HND': {'name': '羽田机场', 'city': '东京', 'country': '日本'},
            'ICN': {'name': '仁川国际机场', 'city': '首尔', 'country': '韩国'},
            'SIN': {'name': '新加坡樟宜机场', 'city': '新加坡', 'country': '新加坡'},
            'BKK': {'name': '素万那普机场', 'city': '曼谷', 'country': '泰国'},
            'KUL': {'name': '吉隆坡国际机场', 'city': '吉隆坡', 'country': '马来西亚'},
            'MNL': {'name': '尼诺伊·阿基诺国际机场', 'city': '马尼拉', 'country': '菲律宾'},
            'CGK': {'name': '苏加诺-哈达国际机场', 'city': '雅加达', 'country': '印度尼西亚'},
            'DEL': {'name': '英迪拉·甘地国际机场', 'city': '新德里', 'country': '印度'},
            'BOM': {'name': '贾特拉帕蒂·希瓦吉国际机场', 'city': '孟买', 'country': '印度'},
            'DXB': {'name': '迪拜国际机场', 'city': '迪拜', 'country': '阿联酋'},
            'DOH': {'name': '哈马德国际机场', 'city': '多哈', 'country': '卡塔尔'},

            # 欧洲机场
            'LHR': {'name': '希思罗机场', 'city': '伦敦', 'country': '英国'},
            'CDG': {'name': '戴高乐机场', 'city': '巴黎', 'country': '法国'},
            'FRA': {'name': '法兰克福机场', 'city': '法兰克福', 'country': '德国'},
            'AMS': {'name': '史基浦机场', 'city': '阿姆斯特丹', 'country': '荷兰'},
            'FCO': {'name': '菲乌米奇诺机场', 'city': '罗马', 'country': '意大利'},
            'MAD': {'name': '巴拉哈斯机场', 'city': '马德里', 'country': '西班牙'},
            'BCN': {'name': '巴塞罗那机场', 'city': '巴塞罗那', 'country': '西班牙'},
            'VIE': {'name': '维也纳国际机场', 'city': '维也纳', 'country': '奥地利'},
            'ZUR': {'name': '苏黎世机场', 'city': '苏黎世', 'country': '瑞士'},
            'MUC': {'name': '慕尼黑机场', 'city': '慕尼黑', 'country': '德国'},
            'CPH': {'name': '哥本哈根机场', 'city': '哥本哈根', 'country': '丹麦'},
            'ARN': {'name': '阿兰达机场', 'city': '斯德哥尔摩', 'country': '瑞典'},
            'HEL': {'name': '赫尔辛基机场', 'city': '赫尔辛基', 'country': '芬兰'},

            # 北美机场
            'LAX': {'name': '洛杉矶国际机场', 'city': '洛杉矶', 'country': '美国'},
            'SFO': {'name': '旧金山国际机场', 'city': '旧金山', 'country': '美国'},
            'JFK': {'name': '肯尼迪国际机场', 'city': '纽约', 'country': '美国'},
            'LGA': {'name': '拉瓜迪亚机场', 'city': '纽约', 'country': '美国'},
            'ORD': {'name': '奥黑尔国际机场', 'city': '芝加哥', 'country': '美国'},
            'DFW': {'name': '达拉斯沃斯堡国际机场', 'city': '达拉斯', 'country': '美国'},
            'ATL': {'name': '哈茨菲尔德-杰克逊国际机场', 'city': '亚特兰大', 'country': '美国'},
            'SEA': {'name': '西雅图-塔科马国际机场', 'city': '西雅图', 'country': '美国'},
            'YVR': {'name': '温哥华国际机场', 'city': '温哥华', 'country': '加拿大'},
            'YYZ': {'name': '皮尔逊国际机场', 'city': '多伦多', 'country': '加拿大'},
            'DEN': {'name': '丹佛国际机场', 'city': '丹佛', 'country': '美国'},
            'LAS': {'name': '麦卡伦国际机场', 'city': '拉斯维加斯', 'country': '美国'},
            'MIA': {'name': '迈阿密国际机场', 'city': '迈阿密', 'country': '美国'}
        }

    def _is_domestic_cn_airport(self, airport_code: str) -> bool:
        """
        判断机场代码是否为中国大陆国内机场
        """
        # 处理可能的格式：Station:airport:PEK 或直接 PEK
        code_to_check = airport_code.upper()
        if code_to_check.startswith("STATION:AIRPORT:"):
            code_to_check = code_to_check.split(':')[-1]

        # 中国大陆主要机场代码集合（扩展版）
        domestic_cn_airports = {
            # 一线城市主要机场
            "PEK", "PKX",  # 北京
            "PVG", "SHA",  # 上海
            "CAN",         # 广州
            "SZX",         # 深圳

            # 主要枢纽城市
            "CTU",         # 成都
            "CKG",         # 重庆
            "XIY",         # 西安
            "KMG",         # 昆明
            "WUH",         # 武汉
            "CSX",         # 长沙
            "NKG",         # 南京
            "HGH",         # 杭州
            "XMN",         # 厦门
            "FOC",         # 福州

            # 其他重要城市
            "TSN",         # 天津
            "SHE",         # 沈阳
            "HRB",         # 哈尔滨
            "DLC",         # 大连
            "TAO",         # 青岛
            "CGO",         # 郑州
            "HFE",         # 合肥
            "TYN",         # 太原
            "KWE",         # 贵阳
            "NNG",         # 南宁
            "URC",         # 乌鲁木齐
            "SYX",         # 三亚
            "HAK",         # 海口
            "JJN",         # 晋江
            "WNZ",         # 温州
            "NTG",         # 南通
            "YNT",         # 烟台
        }

        return code_to_check in domestic_cn_airports

    def can_execute(self, context: SearchContext) -> bool:
        """检查是否可以执行甩尾搜索"""
        # 只在第一阶段执行甩尾搜索
        return context.phase == SearchPhase.PHASE_ONE

    async def execute(self, context: SearchContext) -> SearchResult:
        """执行甩尾航班搜索"""
        start_time = time.time()
        await self._log_execution_start(context)

        # 验证请求参数
        if not await self._validate_request(context):
            return SearchResult(
                status=SearchResultStatus.FAILED,
                flights=[],
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message="请求参数验证失败"
            )

        try:
            # 获取甩尾目的地列表
            throwaway_destinations = self._get_throwaway_destinations(context)
            if not throwaway_destinations:
                return SearchResult(
                    status=SearchResultStatus.SUCCESS,
                    flights=[],
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"message": "未找到合适的甩尾目的地"},
                    disclaimers=["当前路线暂无甩尾票优惠"]
                )

            is_one_way = context.request.return_date_from is None
            all_hidden_city_flights = []
            search_summary = {
                "destinations_searched": [],
                "total_raw_results": 0,
                "valid_hidden_city_flights": 0
            }

            # 对每个甩尾目的地进行搜索
            for dest_code in throwaway_destinations:
                try:
                    self.logger.info(f"[{context.search_id}] 搜索甩尾路线: {context.request.origin_iata} -> {dest_code}")

                    # 构建查询变量（搜索 A -> X）
                    variables = self._build_throwaway_variables(context, dest_code, is_one_way)

                    # 执行搜索
                    context.increment_api_calls()
                    raw_results = await self._perform_search(context, variables, is_one_way)
                    search_summary["total_raw_results"] += len(raw_results)
                    search_summary["destinations_searched"].append(dest_code)

                    # 解析结果并筛选出经过目标城市的航班
                    hidden_flights = await self._extract_hidden_city_flights(
                        context, raw_results, dest_code, is_one_way
                    )

                    all_hidden_city_flights.extend(hidden_flights)
                    search_summary["valid_hidden_city_flights"] += len(hidden_flights)

                    self.logger.info(f"[{context.search_id}] 目的地 {dest_code} 找到 {len(hidden_flights)} 个甩尾航班")

                except Exception as e:
                    self.logger.warning(f"[{context.search_id}] 搜索甩尾目的地 {dest_code} 失败: {e}")
                    continue

            # 去重和排序
            unique_flights = self._deduplicate_flights(all_hidden_city_flights)

            # 增强航班信息
            enhanced_flights = []
            for flight in unique_flights:
                enhanced_flight = self._convert_to_enhanced_flight(flight, context)
                enhanced_flights.append(enhanced_flight)

            # 🔍 甩尾票搜索统计日志
            self.logger.info(f"🔍 甩尾票搜索统计 - search_id: {context.search_id}")
            self.logger.info(f"  - 搜索的甩尾目的地: {throwaway_destinations}")
            self.logger.info(f"  - 原始结果总数: {search_summary['total_raw_results']}")
            self.logger.info(f"  - 有效甩尾票数: {search_summary['valid_hidden_city_flights']}")
            self.logger.info(f"  - 去重后航班数: {len(unique_flights)}")
            self.logger.info(f"  - 最终增强航班数: {len(enhanced_flights)}")

            # 简化增强航班日志
            self.logger.debug(f"[{context.search_id}] 甩尾票搜索完成: {len(enhanced_flights)} 个有效航班")

            execution_time = int((time.time() - start_time) * 1000)

            result = SearchResult(
                status=SearchResultStatus.SUCCESS,
                flights=enhanced_flights,
                execution_time_ms=execution_time,
                metadata={
                    **search_summary,
                    "enhanced_flights": len(enhanced_flights),
                    "is_one_way": is_one_way
                },
                disclaimers=self._get_disclaimers()
            )

            await self._log_execution_end(context, result)
            return result

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"[{context.search_id}] 甩尾搜索执行失败: {e}", exc_info=True)

            return SearchResult(
                status=SearchResultStatus.FAILED,
                flights=[],
                execution_time_ms=execution_time,
                error_message=f"甩尾搜索执行失败: {str(e)}"
            )

    def _get_throwaway_destinations(self, context: SearchContext) -> List[str]:
        """获取适合的甩尾目的地列表"""
        origin = context.request.origin_iata.upper()
        destination = context.request.destination_iata.upper()

        # 🔍 诊断日志：记录甩尾目的地选择过程
        self.logger.info(f"🎯 甩尾目的地选择诊断 - search_id: {context.search_id}")
        self.logger.info(f"  - 起始地: {origin}")
        self.logger.info(f"  - 目的地: {destination}")

        # 判断目的地是否为国内
        is_destination_domestic = self._is_domestic_cn_airport(destination)
        self.logger.info(f"  - 目的地是否为国内: {is_destination_domestic}")

        # 基于目的地地理位置选择合适的甩尾城市
        throwaway_list = []

        # 中国境内目的地（扩展列表）
        china_airports = {
            'PEK', 'PKX', 'SHA', 'PVG', 'CAN', 'SZX', 'CTU', 'WUH', 'XMN',
            'CSX', 'TAO', 'NKG', 'HGH', 'TSN', 'DLC', 'SYX', 'KMG', 'CKG',
            'XIY', 'FOC', 'CGO', 'HFE', 'TYN', 'KWE', 'NNG', 'URC'
        }

        # 亚洲目的地
        asia_airports = {
            'HKG', 'TPE', 'NRT', 'HND', 'ICN', 'SIN', 'BKK', 'KUL',
            'MNL', 'CGK', 'DEL', 'BOM', 'DXB', 'DOH'
        }

        # 欧洲目的地
        europe_airports = {
            'LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'MAD', 'BCN', 'VIE',
            'ZUR', 'MUC', 'CPH', 'ARN', 'HEL'
        }

        # 北美目的地
        north_america_airports = {
            'LAX', 'SFO', 'JFK', 'LGA', 'ORD', 'DFW', 'ATL', 'SEA',
            'YVR', 'YYZ', 'DEN', 'LAS', 'MIA'
        }

        if destination in china_airports:
            # 🎯 国内目的地：优先使用国内其他枢纽作为甩尾目的地
            self.logger.info(f"  - 策略: 国内目的地，优先使用国内枢纽")
            throwaway_list.extend(self.default_throwaway_destinations['china'])
            # 只添加少量亚洲城市作为备选
            throwaway_list.extend(self.default_throwaway_destinations['asia'][:3])
        elif destination in asia_airports:
            # 亚洲目的地，尝试其他亚洲城市
            self.logger.info(f"  - 策略: 亚洲目的地，使用亚洲枢纽")
            throwaway_list.extend(self.default_throwaway_destinations['asia'])
        elif destination in europe_airports:
            # 欧洲目的地，尝试其他欧洲城市
            self.logger.info(f"  - 策略: 欧洲目的地，使用欧洲枢纽")
            throwaway_list.extend(self.default_throwaway_destinations['europe'])
        elif destination in north_america_airports:
            # 北美目的地，尝试其他北美城市
            self.logger.info(f"  - 策略: 北美目的地，使用北美枢纽")
            throwaway_list.extend(self.default_throwaway_destinations['north_america'])
        else:
            # 其他目的地，尝试各区域主要城市
            self.logger.info(f"  - 策略: 其他目的地，使用混合枢纽")
            throwaway_list.extend(self.default_throwaway_destinations['asia'][:3])
            throwaway_list.extend(self.default_throwaway_destinations['europe'][:3])
            throwaway_list.extend(self.default_throwaway_destinations['north_america'][:3])

        # 过滤掉起始地和目的地
        filtered_list = [dest for dest in throwaway_list
                        if dest != origin and dest != destination]

        # 限制搜索数量以控制API调用
        final_list = filtered_list[:8]  # 最多搜索8个甩尾目的地

        self.logger.info(f"  - 候选甩尾目的地: {throwaway_list}")
        self.logger.info(f"  - 过滤后列表: {filtered_list}")
        self.logger.info(f"  - 最终选择: {final_list}")

        return final_list

    def _build_throwaway_variables(self, context: SearchContext, throwaway_dest: str, is_one_way: bool) -> Dict[str, Any]:
        """构建甩尾搜索变量"""
        from app.apis.v1.schemas import FlightSearchRequest

        # 创建临时请求对象，目的地设为甩尾城市
        temp_request = FlightSearchRequest(
            origin_iata=context.request.origin_iata,
            destination_iata=throwaway_dest,  # 使用甩尾目的地
            departure_date_from=context.request.departure_date_from,
            departure_date_to=context.request.departure_date_to,
            return_date_from=context.request.return_date_from,
            return_date_to=context.request.return_date_to,
            cabin_class=context.request.cabin_class,
            adults=context.request.adults,
            preferred_currency=context.request.preferred_currency,
            market=context.request.market
        )

        # 使用现有函数构建基础变量
        variables = _task_build_kiwi_variables(temp_request, is_one_way)

        # 允许最多3次中转（增加找到甩尾票的机会）
        variables["filter"]["maxStopsCount"] = 3

        # 添加搜索ID
        variables["search_id"] = f"{context.search_id}_throwaway_{throwaway_dest}"

        return variables

    async def _perform_search(self, context: SearchContext, variables: Dict[str, Any], is_one_way: bool) -> List[Dict[str, Any]]:
        """执行Kiwi API搜索"""
        try:
            # 创建模拟的self对象
            class MockSelf:
                def __init__(self):
                    self.request = type('MockRequest', (), {'id': context.search_id})()

            mock_self = MockSelf()

            # 创建临时请求对象
            from app.apis.v1.schemas import FlightSearchRequest
            temp_request = FlightSearchRequest(
                origin_iata=context.request.origin_iata,
                destination_iata=context.request.destination_iata,
                departure_date_from=context.request.departure_date_from,
                departure_date_to=context.request.departure_date_to,
                return_date_from=context.request.return_date_from,
                return_date_to=context.request.return_date_to,
                cabin_class=context.request.cabin_class,
                adults=context.request.adults
            )

            # 使用现有的搜索函数
            raw_results = await _task_run_search_with_retry(
                self=mock_self,
                variables=variables,
                attempt_desc="hidden_city",
                request_params=temp_request,
                force_one_way=is_one_way
            )

            return raw_results

        except Exception as e:
            self.logger.error(f"[{context.search_id}] 甩尾搜索API调用失败: {e}", exc_info=True)
            raise

    async def _extract_hidden_city_flights(
        self,
        context: SearchContext,
        raw_results: List[Dict[str, Any]],
        throwaway_dest: str,
        is_one_way: bool
    ) -> List[FlightItinerary]:
        """从搜索结果中提取经过目标城市的甩尾航班"""
        hidden_flights = []
        target_destination = context.request.destination_iata.upper()
        requested_currency = context.request.preferred_currency or "CNY"

        for raw_itinerary in raw_results:
            try:
                parsed = await _task_parse_kiwi_itinerary(raw_itinerary, is_one_way, requested_currency)
                if not parsed or not parsed.segments:
                    continue

                # 检查航班路径是否经过目标城市（但不是最终目的地）
                if self._is_valid_hidden_city_flight(parsed, target_destination, throwaway_dest):
                    # 标记为甩尾航班
                    parsed.is_hidden_city = True
                    parsed.is_throwaway_deal = True

                    # 设置隐藏目的地信息（用户实际要去的地方）
                    airport_info = self.airport_info_map.get(target_destination.upper(), {
                        'name': f'{target_destination}机场',
                        'city': target_destination,
                        'country': '未知'
                    })

                    parsed.hidden_destination = {
                        'code': target_destination.upper(),
                        'name': airport_info['name'],
                        'city': airport_info['city'],
                        'country': airport_info['country']
                    }

                    hidden_flights.append(parsed)

                    self.logger.debug(
                        f"[{context.search_id}] 发现甩尾航班: {parsed.id} "
                        f"路径经过目标城市 {target_destination}"
                    )

            except Exception as e:
                self.logger.warning(f"[{context.search_id}] 解析甩尾航班时出错: {e}")
                continue

        return hidden_flights

    def _is_valid_hidden_city_flight(self, flight: FlightItinerary, target_city: str, final_dest: str) -> bool:
        """验证是否为有效的甩尾航班"""
        self.logger.info(f"🔍 甩尾票验证 - flight_id: {flight.id}")
        self.logger.info(f"  - 目标城市: {target_city}, 最终目的地: {final_dest}")
        self.logger.info(f"  - is_hidden_city: {flight.is_hidden_city}")
        self.logger.info(f"  - is_throwaway_deal: {getattr(flight, 'is_throwaway_deal', False)}")

        if not flight.segments:
            self.logger.info(f"  - ❌ 无航段信息")
            return False

        # 打印所有航段路径
        route = " -> ".join([seg.departure_airport for seg in flight.segments] + [flight.segments[-1].arrival_airport])
        self.logger.info(f"  - 航班路径: {route}")

        # 如果航班已经被标记为甩尾票，直接返回 True
        # 注意：优先使用 is_hidden_city (来自 isTrueHiddenCity)，isThrowawayTicket 字段不可靠
        if flight.is_hidden_city:
            self.logger.info(f"  - ✅ 航班已标记为甩尾票(isTrueHiddenCity=True)，直接通过验证")
            return True

        # 备用检查：如果有 is_throwaway_deal 标记也接受
        if getattr(flight, 'is_throwaway_deal', False):
            self.logger.info(f"  - ✅ 航班标记为甩尾优惠，通过验证")
            return True

        # 检查所有航段，寻找经过目标城市但不是最终目的地的情况
        for i, segment in enumerate(flight.segments):
            self.logger.info(f"  - 检查航段{i}: {segment.departure_airport} -> {segment.arrival_airport}")
            # 如果某个航段的到达地是目标城市，且不是最后一个航段
            if (segment.arrival_airport.upper() == target_city and
                i < len(flight.segments) - 1):

                # 确保最终目的地是我们设定的甩尾目的地
                final_segment = flight.segments[-1]
                if final_segment.arrival_airport.upper() == final_dest.upper():
                    self.logger.info(f"  - ✅ 发现有效甩尾路径: 在航段{i}经过目标城市{target_city}")
                    return True
                else:
                    self.logger.info(f"  - ❌ 最终目的地不匹配: 期望{final_dest}, 实际{final_segment.arrival_airport}")

        self.logger.info(f"  - ❌ 未找到有效的甩尾路径")
        return False

    def _deduplicate_flights(self, flights: List[FlightItinerary]) -> List[FlightItinerary]:
        """去除重复的航班"""
        seen_ids = set()
        unique_flights = []

        for flight in flights:
            if flight.id not in seen_ids:
                seen_ids.add(flight.id)
                unique_flights.append(flight)

        # 按价格排序
        unique_flights.sort(key=lambda x: x.price)
        return unique_flights

    def _convert_to_enhanced_flight(self, flight: FlightItinerary, context: SearchContext) -> EnhancedFlightItinerary:
        """将FlightItinerary转换为EnhancedFlightItinerary"""

        enhanced_flight = EnhancedFlightItinerary(
            # 复制基础字段
            id=flight.id,
            price=flight.price,
            currency=flight.currency,
            booking_token=flight.booking_token,
            deep_link=flight.deep_link,
            outbound_segments=flight.outbound_segments,
            inbound_segments=flight.inbound_segments,
            segments=flight.segments,
            total_duration_minutes=flight.total_duration_minutes,
            is_self_transfer=flight.is_self_transfer,
            is_hidden_city=flight.is_hidden_city,
            hidden_destination=flight.hidden_destination,  # 传递隐藏目的地
            data_source=flight.data_source,
            is_throwaway_deal=flight.is_throwaway_deal,
            isProbeSuggestion=flight.isProbeSuggestion,
            probeHub=flight.probeHub,
            probeDisclaimer=flight.probeDisclaimer,
            raw_data=flight.raw_data,

            # 新增字段
            search_phase=SearchPhase.PHASE_ONE,
            quality_score=None,
            hub_info=None,
            risk_factors=[
                "甩尾票风险：需要在中转站下机，不能完成全程",
                "行李风险：托运行李可能被送到最终目的地",
                "航空公司政策风险：可能违反运输条款"
            ],
            recommendation_reason=None
        )

        # 计算质量评分（甩尾票有额外风险，分数会较低）
        base_score = self._calculate_quality_score(enhanced_flight)
        enhanced_flight.quality_score = max(0.0, base_score - 20)  # 甩尾票扣20分

        # 设置推荐理由
        enhanced_flight.recommendation_reason = f"甩尾票优惠，价格较低但存在风险"

        # 添加策略相关元数据
        self._enhance_flight_with_metadata(enhanced_flight, context, {
            "is_hidden_city_flight": True,
            "has_risks": True,
            "segment_count": len(enhanced_flight.segments or [])
        })

        return enhanced_flight

    def _get_disclaimers(self) -> List[str]:
        """获取甩尾搜索的免责声明"""
        return [
            "甩尾票（隐藏城市票）存在风险：您需要在中转站下机，不能完成全程航段",
            "风险警告：托运行李将被送到票面最终目的地，建议仅携带手提行李",
            "政策风险：甩尾票可能违反航空公司运输条款，可能导致常旅客账户被处罚",
            "不适用于往返票：使用甩尾票后，后续航段将被自动取消",
            "请在充分了解风险后谨慎选择甩尾票"
        ]

    def _test_domestic_strategy(self, test_destinations: List[str]) -> Dict[str, Any]:
        """
        测试函数：验证国内甩尾策略的诊断
        """
        test_results = {
            "domestic_airports": [],
            "international_airports": [],
            "strategy_mapping": {}
        }

        for dest in test_destinations:
            is_domestic = self._is_domestic_cn_airport(dest)
            if is_domestic:
                test_results["domestic_airports"].append(dest)
                # 模拟获取国内甩尾目的地
                throwaway_list = self.default_throwaway_destinations['china'][:5]
                test_results["strategy_mapping"][dest] = {
                    "type": "domestic",
                    "throwaway_destinations": throwaway_list
                }
            else:
                test_results["international_airports"].append(dest)
                # 模拟获取国际甩尾目的地
                throwaway_list = self.default_throwaway_destinations['asia'][:5]
                test_results["strategy_mapping"][dest] = {
                    "type": "international",
                    "throwaway_destinations": throwaway_list
                }

        self.logger.info(f"🧪 甩尾策略测试结果:")
        self.logger.info(f"  - 国内机场: {test_results['domestic_airports']}")
        self.logger.info(f"  - 国际机场: {test_results['international_airports']}")
        for dest, strategy in test_results["strategy_mapping"].items():
            self.logger.info(f"  - {dest} ({strategy['type']}): {strategy['throwaway_destinations']}")

        return test_results