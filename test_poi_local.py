#!/usr/bin/env python3
"""
本地测试POI搜索API的脚本
"""

import requests
import json

def test_poi_api():
    """测试POI搜索API"""

    base_url = "http://localhost:8000"

    # 0. 先检查后端健康状态
    print("🏥 检查后端健康状态...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ 后端健康检查: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"   响应: {health_response.json()}")
    except Exception as e:
        print(f"❌ 后端健康检查失败: {e}")
        return

    # 1. 先登录获取token
    print("\n🔐 正在登录...")
    try:
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data="username=1242772513@qq.com&password=1242772513",
            timeout=10
        )
        print(f"📊 登录响应状态码: {login_response.status_code}")
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return

    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        print(f"响应: {login_response.text}")
        return

    token_data = login_response.json()
    access_token = token_data.get("access_token")
    print(f"✅ 登录成功，获取到token: {access_token[:20]}...")

    # 2. 测试POI搜索
    test_queries = ["Shanghai", "Beijing", "New York", "London", "Tokyo"]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🔍 测试查询: {query}")
        print(f"{'='*60}")

        # 发送POI搜索请求
        try:
            poi_response = requests.post(
                f"{base_url}/api/v1/poi/search",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                json={
                    "query": query,
                    "trip_type": "flight",
                    "mode": "dep"
                },
                timeout=30  # 增加超时时间，因为可能需要调用外部API
            )
        except Exception as e:
            print(f"❌ POI搜索请求失败: {e}")
            continue

        print(f"📊 状态码: {poi_response.status_code}")

        if poi_response.status_code == 200:
            result = poi_response.json()
            print(f"✅ 成功获取结果:")
            print(f"   - 成功: {result.get('success')}")
            print(f"   - 机场数量: {result.get('total', 0)}")
            print(f"   - 查询: {result.get('query')}")

            airports = result.get('airports', [])
            if airports:
                print(f"   - 机场列表:")
                for i, airport in enumerate(airports[:3]):  # 只显示前3个
                    print(f"     {i+1}. {airport.get('name')} ({airport.get('code')})")
                if len(airports) > 3:
                    print(f"     ... 还有 {len(airports) - 3} 个机场")
            else:
                print(f"   - ⚠️ 没有找到机场")
        else:
            print(f"❌ 请求失败: {poi_response.text}")

if __name__ == "__main__":
    print("🚀 开始测试POI搜索API")
    print("📍 后端地址: http://localhost:8000")

    try:
        test_poi_api()
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n🏁 测试完成")
