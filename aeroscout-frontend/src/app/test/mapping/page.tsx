'use client';

import React, { useState } from 'react';
import { mockFlights } from '@/src/__mocks__/mockFlightData';
import { mapApiItineraryToStoreItinerary } from '@/store/flightResultsStore';
import FlightCard from '@/components/flight/FlightCard';
import { Card } from '@/components/common/Card';

/**
 * 测试页面：用于测试数据映射和FlightCard组件
 */
export default function MappingTestPage() {
  const [selectedMock, setSelectedMock] = useState('directFlight');
  
  // 获取选中的模拟数据
  const selectedMockData = mockFlights[selectedMock as keyof typeof mockFlights];
  
  // 映射数据
  const mappedData = mapApiItineraryToStoreItinerary(selectedMockData);
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">数据映射测试页面</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <Card className="p-4">
            <h2 className="text-xl font-semibold mb-4">选择模拟数据</h2>
            <div className="space-y-2">
              {Object.keys(mockFlights).map((mockKey) => (
                <div key={mockKey} className="flex items-center">
                  <input
                    type="radio"
                    id={mockKey}
                    name="mockData"
                    value={mockKey}
                    checked={selectedMock === mockKey}
                    onChange={() => setSelectedMock(mockKey)}
                    className="mr-2"
                  />
                  <label htmlFor={mockKey} className="cursor-pointer">
                    {mockKey}
                  </label>
                </div>
              ))}
            </div>
          </Card>
          
          <Card className="p-4 mt-4">
            <h2 className="text-xl font-semibold mb-4">API数据 (ApiFlightItinerary)</h2>
            <pre className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96 text-xs">
              {JSON.stringify(selectedMockData, null, 2)}
            </pre>
          </Card>
        </div>
        
        <div>
          <Card className="p-4">
            <h2 className="text-xl font-semibold mb-4">映射后数据 (FlightItinerary)</h2>
            <pre className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96 text-xs">
              {JSON.stringify(mappedData, null, 2)}
            </pre>
          </Card>
        </div>
      </div>
      
      <h2 className="text-xl font-semibold mb-4">FlightCard 渲染测试</h2>
      <div className="mb-8">
        <FlightCard 
          itinerary={mappedData} 
          isComboDeal={mappedData.numberOfStops && mappedData.numberOfStops > 0} 
        />
      </div>
      
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
        <h3 className="text-lg font-semibold text-yellow-800">测试说明</h3>
        <p className="text-yellow-800">
          此页面用于测试数据映射函数和FlightCard组件的渲染。您可以选择不同的模拟数据来查看映射结果和渲染效果。
        </p>
        <ul className="list-disc pl-5 mt-2 text-yellow-800">
          <li><strong>directFlight</strong>: 直飞航班</li>
          <li><strong>oneStopFlight</strong>: 一次中转航班</li>
          <li><strong>multiStopFlight</strong>: 多次中转航班（含换机场和行李重新托运）</li>
          <li><strong>hiddenCityFlight</strong>: 隐藏城市航班</li>
          <li><strong>probeSuggestionFlight</strong>: 探测特惠航班</li>
          <li><strong>multiAirlineFlight</strong>: 多航司航班</li>
        </ul>
      </div>
    </div>
  );
}
