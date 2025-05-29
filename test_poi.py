#!/usr/bin/env python3
"""
本地测试POI搜索API的脚本
"""

import asyncio
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'aeroscouthq_backend'))

from app.services.trip_poi_service import get_poi_data

async def test_poi_search():
    """测试POI搜索功能"""
    
    # 测试查询
    queries = ["Shanghai", "Beijing", "New York", "London"]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"测试查询: {query}")
        print(f"{'='*50}")
        
        try:
            # 调用POI搜索
            result = await get_poi_data(
                query=query,
                trip_type="flight", 
                mode="dep",
                user_email="test@example.com"
            )
            
            print(f"结果类型: {type(result)}")
            if result:
                print(f"结果内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print("结果为空")
                
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 设置环境变量
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    os.environ.setdefault("SECRET_KEY", "test_secret")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # 运行测试
    asyncio.run(test_poi_search())
