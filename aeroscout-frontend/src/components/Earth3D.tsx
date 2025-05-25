'use client';

import React, { useRef, useEffect, useState } from 'react';
import dynamic from 'next/dynamic';

// 动态导入Globe组件，避免SSR问题
const Globe = dynamic(() => import('react-globe.gl'), {
  ssr: false,
  loading: () => (
    <div className="w-96 h-96 rounded-full bg-[#1A4275] flex items-center justify-center">
      <div className="text-white">加载中...</div>
    </div>
  )
});

// 主要航空枢纽城市坐标 - 用于生成更真实的航线
const MAJOR_AIRPORTS = [
  { name: 'Beijing', lat: 40.0799, lng: 116.6031 },
  { name: 'Shanghai', lat: 31.1443, lng: 121.8083 },
  { name: 'Tokyo', lat: 35.6895, lng: 139.6917 },
  { name: 'Seoul', lat: 37.5665, lng: 126.9780 },
  { name: 'Singapore', lat: 1.3521, lng: 103.8198 },
  { name: 'Dubai', lat: 25.2532, lng: 55.3657 },
  { name: 'London', lat: 51.5074, lng: -0.1278 },
  { name: 'Paris', lat: 48.8566, lng: 2.3522 },
  { name: 'Frankfurt', lat: 50.1109, lng: 8.6821 },
  { name: 'New York', lat: 40.7128, lng: -74.0060 },
  { name: 'Los Angeles', lat: 34.0522, lng: -118.2437 },
  { name: 'Sydney', lat: -33.8688, lng: 151.2093 },
  { name: 'Bangkok', lat: 13.7563, lng: 100.5018 },
  { name: 'Hong Kong', lat: 22.3193, lng: 114.1694 },
  { name: 'Istanbul', lat: 41.0082, lng: 28.9784 },
  { name: 'Delhi', lat: 28.6139, lng: 77.2090 },
  { name: 'Moscow', lat: 55.7558, lng: 37.6173 },
  { name: 'Amsterdam', lat: 52.3676, lng: 4.9041 },
  { name: 'Toronto', lat: 43.6532, lng: -79.3832 },
  { name: 'Sao Paulo', lat: -23.5505, lng: -46.6333 }
];

const Earth3D = () => {
  const globeEl = useRef<any>();
  const [arcsData, setArcsData] = useState<any[]>([]);

  // 生成更真实的航线数据（基于主要航空枢纽）
  useEffect(() => {
    // 生成30条航线，从主要枢纽出发或到达
    const N = 30;
    const newArcsData = [...Array(N).keys()].map(() => {
      // 随机选择起点和终点
      const useHubAsStart = Math.random() > 0.5;
      const hubIndex = Math.floor(Math.random() * MAJOR_AIRPORTS.length);
      const hub = MAJOR_AIRPORTS[hubIndex];

      // 为非枢纽端生成随机坐标，但确保在陆地附近（避免海洋中间的点）
      const randomLat = (Math.random() * 140 - 70) * 0.9; // 避免极地区域
      const randomLng = Math.random() * 360 - 180;

      // 确定航线颜色 - 使用更多样化的颜色
      const colors = [
        'rgba(255,255,255,0.6)', // 白色
        'rgba(255,165,0,0.6)',   // 橙色
        'rgba(135,206,250,0.6)', // 天蓝色
        'rgba(152,251,152,0.5)'  // 淡绿色
      ];
      const color = colors[Math.floor(Math.random() * colors.length)];

      // 创建航线数据
      return {
        startLat: useHubAsStart ? hub.lat : randomLat,
        startLng: useHubAsStart ? hub.lng : randomLng,
        endLat: useHubAsStart ? randomLat : hub.lat,
        endLng: useHubAsStart ? randomLng : hub.lng,
        color,
        // 添加动画时间变化，使航线动画不同步
        animateTime: 1000 + Math.random() * 2000
      };
    });

    setArcsData(newArcsData);
  }, []);

  // 设置地球自转
  useEffect(() => {
    // 确保组件已挂载且globeEl.current已存在
    if (!globeEl.current) return;

    // 启用自动旋转
    const controls = globeEl.current.controls();
    controls.autoRotate = true;

    // 设置旋转轴为Y轴（水平旋转）- 调整速度更慢一些，更自然
    controls.autoRotateSpeed = -0.6; // 负值使其按照我们期望的方向旋转（从西向东）

    // 禁用缩放和平移，保持地球在固定位置
    controls.enableZoom = false;
    controls.enablePan = false;

    // 调整初始视角 - 略微倾斜以展示更多北半球（大多数航线）
    globeEl.current.pointOfView({
      lat: 25,
      lng: 10,
      altitude: 1.8  // 调整高度，使地球看起来更大但不会太大
    });

    // 确保控制器更新
    const animate = () => {
      controls.update();
      requestAnimationFrame(animate);
    };

    const frameId = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(frameId);
    };
  }, []);

  return (
    <div className="w-96 h-96 relative">
      <Globe
        ref={globeEl}
        // 使用更高质量的地球贴图，包含真实的海洋、陆地、森林和云层
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-blue-marble.jpg"
        // 使用更详细的地形图
        bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
        // 添加云层
        cloudsImageUrl="//unpkg.com/three-globe/example/img/earth-clouds.png"
        // 调整大气层 - 更亮、更蓝的色调
        atmosphereColor="rgba(65,145,255,0.3)"
        atmosphereAltitude={0.18}
        // 航线设置
        arcsData={arcsData}
        arcColor={'color'}
        arcDashLength={0.4}
        arcDashGap={0.2}
        arcDashAnimateTime={d => d.animateTime}
        arcStroke={0.5} // 更细的航线
        arcAltitude={0.2} // 航线高度
        // 背景透明
        backgroundColor="rgba(0,0,0,0)"
        // 调整尺寸
        width={380}
        height={380}
        // 增加地球比例
        globeScale={1.8}
      />
    </div>
  );
};

export default Earth3D;
