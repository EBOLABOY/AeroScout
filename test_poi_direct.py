#!/usr/bin/env python3
"""
直接测试POI服务的脚本（不通过HTTP API）
"""

import asyncio
import json
import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'aeroscouthq_backend'))

async def test_poi_direct():
    """直接测试POI服务"""

    try:
        # 导入POI服务
        from app.services.trip_poi_service import _call_trip_poi_api

        print("🔍 直接测试Trip.com POI API调用")
        print("="*50)

        # 测试查询
        queries = ["Shanghai", "Beijing"]

        for query in queries:
            print(f"\n📍 测试查询: {query}")
            print("-" * 30)

            try:
                # 准备基本的headers
                headers = {
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    'content-type': 'application/json',
                    'origin': 'https://hk.trip.com',
                    'referer': 'https://hk.trip.com/flights/',
                    'accept': '*/*',
                    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
                    'x-ctx-country': 'HK',
                    'x-ctx-currency': 'CNY',
                    'x-ctx-locale': 'zh-HK',
                    'currency': 'CNY',
                    'locale': 'zh-HK',
                    'cookieorigin': 'https://hk.trip.com'
                }

                # 直接调用API
                result = await _call_trip_poi_api(
                    search_key=query,
                    mode="0",  # 0 for departure
                    trip_type="RT",  # Round trip
                    headers=headers
                )

                print(f"✅ API调用成功")
                print(f"📊 结果类型: {type(result)}")

                if result:
                    # 显示结果的基本信息
                    if isinstance(result, dict):
                        print(f"🔑 响应键: {list(result.keys())}")

                        # 检查ResponseStatus
                        if "ResponseStatus" in result:
                            status = result["ResponseStatus"]
                            print(f"📈 状态: {status.get('Ack', 'Unknown')}")

                        # 检查results
                        if "results" in result:
                            results = result["results"]
                            print(f"📋 结果数量: {len(results) if isinstance(results, list) else 'Not a list'}")

                            if isinstance(results, list) and len(results) > 0:
                                first_result = results[0]
                                print(f"🏷️ 第一个结果: {first_result.get('name', 'No name')}")
                                if "childResults" in first_result:
                                    child_count = len(first_result["childResults"])
                                    print(f"✈️ 子机场数量: {child_count}")

                        # 显示原始响应的前500字符
                        print(f"📄 原始响应 (前500字符):")
                        print(json.dumps(result, ensure_ascii=False)[:500] + "...")
                    else:
                        print(f"⚠️ 结果不是字典类型: {result}")
                else:
                    print("❌ 结果为空")

            except Exception as e:
                print(f"❌ API调用失败: {e}")
                import traceback
                traceback.print_exc()

    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保后端代码路径正确")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 开始直接测试POI服务")

    # 设置基本环境变量
    os.environ.setdefault("LOG_LEVEL", "INFO")

    # 运行测试
    asyncio.run(test_poi_direct())

    print("\n🏁 测试完成")
