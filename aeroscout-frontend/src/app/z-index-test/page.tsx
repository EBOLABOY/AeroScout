'use client';

import React, { useState } from 'react';
import AirportSelector from '@/components/airport/AirportSelector';
import { AirportInfo } from '@/lib/apiService';

const ZIndexTestPage: React.FC = () => {
  const [airport1, setAirport1] = useState<AirportInfo | null>(null);
  const [airport2, setAirport2] = useState<AirportInfo | null>(null);

  return (
    <div className="min-h-screen bg-[#F5F5F7] p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-[#1D1D1F] mb-8 text-center">
          Z-Index 层级测试页面
        </h1>
        
        <div className="space-y-8">
          {/* 测试场景1: 普通容器 */}
          <div className="bg-white p-6 rounded-apple shadow-apple">
            <h2 className="text-xl font-semibold text-[#1D1D1F] mb-4">
              测试场景1: 普通容器
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AirportSelector
                label="出发地"
                placeholder="搜索出发机场..."
                onAirportSelected={setAirport1}
                value={airport1}
              />
              <AirportSelector
                label="目的地"
                placeholder="搜索目的地机场..."
                onAirportSelected={setAirport2}
                value={airport2}
              />
            </div>
          </div>

          {/* 测试场景2: 高z-index容器 */}
          <div className="bg-white p-6 rounded-apple shadow-apple relative z-50">
            <h2 className="text-xl font-semibold text-[#1D1D1F] mb-4">
              测试场景2: 高z-index容器 (z-50)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AirportSelector
                label="出发地"
                placeholder="搜索出发机场..."
                onAirportSelected={setAirport1}
                value={airport1}
              />
              <AirportSelector
                label="目的地"
                placeholder="搜索目的地机场..."
                onAirportSelected={setAirport2}
                value={airport2}
              />
            </div>
          </div>

          {/* 测试场景3: 重叠容器 */}
          <div className="relative">
            <div className="bg-white p-6 rounded-apple shadow-apple">
              <h2 className="text-xl font-semibold text-[#1D1D1F] mb-4">
                测试场景3: 重叠容器
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AirportSelector
                  label="出发地"
                  placeholder="搜索出发机场..."
                  onAirportSelected={setAirport1}
                  value={airport1}
                />
                <AirportSelector
                  label="目的地"
                  placeholder="搜索目的地机场..."
                  onAirportSelected={setAirport2}
                  value={airport2}
                />
              </div>
            </div>
            
            {/* 重叠的遮挡元素 */}
            <div className="absolute top-20 left-4 right-4 h-32 bg-gradient-to-r from-[#FF9500]/20 to-[#0071E3]/20 rounded-apple border border-[#E5E5EA] flex items-center justify-center z-10">
              <span className="text-[#86868B] font-medium">
                重叠遮挡元素 (z-10) - 下拉菜单应该显示在此元素之上
              </span>
            </div>
          </div>

          {/* 测试场景4: Flex容器 */}
          <div className="bg-white p-6 rounded-apple shadow-apple">
            <h2 className="text-xl font-semibold text-[#1D1D1F] mb-4">
              测试场景4: Flex容器
            </h2>
            <div className="flex flex-col md:flex-row md:items-end md:space-x-4">
              <div className="flex-1 mb-4 md:mb-0">
                <AirportSelector
                  label="出发地"
                  placeholder="搜索出发机场..."
                  onAirportSelected={setAirport1}
                  value={airport1}
                />
              </div>
              <div className="flex-1 mb-4 md:mb-0">
                <AirportSelector
                  label="目的地"
                  placeholder="搜索目的地机场..."
                  onAirportSelected={setAirport2}
                  value={airport2}
                />
              </div>
            </div>
          </div>

          {/* 测试场景5: 模拟FlightSearchForm布局 */}
          <div className="bg-white rounded-apple shadow-apple overflow-visible">
            <div className="bg-gradient-to-r from-[#FF9500]/10 to-white px-4 py-3">
              <h2 className="text-xl font-semibold text-[#1D1D1F]">
                测试场景5: 模拟FlightSearchForm布局
              </h2>
            </div>
            <div className="p-6 overflow-visible">
              <div className="flex flex-col md:flex-row md:items-end md:space-x-4 overflow-visible">
                <div className="flex-1 mb-4 md:mb-0 overflow-visible">
                  <AirportSelector
                    label="出发地"
                    placeholder="搜索出发机场..."
                    onAirportSelected={setAirport1}
                    value={airport1}
                  />
                </div>
                <div className="flex-1 mb-4 md:mb-0 overflow-visible">
                  <AirportSelector
                    label="目的地"
                    placeholder="搜索目的地机场..."
                    onAirportSelected={setAirport2}
                    value={airport2}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* 选择结果显示 */}
          {(airport1 || airport2) && (
            <div className="bg-[#E9F0FC] p-6 rounded-apple border border-[#0071E3]/20">
              <h3 className="text-lg font-semibold text-[#1D1D1F] mb-4">当前选择</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {airport1 && (
                  <div>
                    <p className="text-sm font-medium text-[#86868B]">出发地</p>
                    <p className="text-base text-[#1D1D1F] font-medium">
                      {airport1.name} ({airport1.code})
                    </p>
                    <p className="text-xs text-[#86868B]">
                      {airport1.city}, {airport1.country}
                    </p>
                  </div>
                )}
                {airport2 && (
                  <div>
                    <p className="text-sm font-medium text-[#86868B]">目的地</p>
                    <p className="text-base text-[#1D1D1F] font-medium">
                      {airport2.name} ({airport2.code})
                    </p>
                    <p className="text-xs text-[#86868B]">
                      {airport2.city}, {airport2.country}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-[#86868B]">
            测试说明：在每个场景中输入机场名称（如"北京"、"上海"），检查下拉菜单是否正确显示在所有元素之上
          </p>
        </div>
      </div>
    </div>
  );
};

export default ZIndexTestPage;
