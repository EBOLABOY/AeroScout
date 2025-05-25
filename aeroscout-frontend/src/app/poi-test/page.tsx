'use client';

import React, { useState } from 'react';
import AirportSelector from '@/components/airport/AirportSelector';
import { AirportInfo } from '@/lib/apiService';

const PoiTestPage: React.FC = () => {
  const [departureAirport, setDepartureAirport] = useState<AirportInfo | null>(null);
  const [arrivalAirport, setArrivalAirport] = useState<AirportInfo | null>(null);

  const handleDepartureSelect = (airport: AirportInfo | null) => {
    console.log('Departure airport selected:', airport);
    setDepartureAirport(airport);
  };

  const handleArrivalSelect = (airport: AirportInfo | null) => {
    console.log('Arrival airport selected:', airport);
    setArrivalAirport(airport);
  };

  return (
    <div className="container mx-auto p-4 min-h-screen bg-[#F5F5F7]">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#1D1D1F] text-center">机场选择功能测试页</h1>
        <p className="text-center text-[#86868B] mt-2">测试全新设计的机场选择组件</p>
      </header>

      <div className="max-w-2xl mx-auto bg-white p-8 rounded-apple shadow-apple animate-scaleIn">
        <div className="space-y-8">
          <div>
            <h2 className="text-lg font-semibold text-[#1D1D1F] mb-4">机场选择测试</h2>
            <div className="space-y-6">
              <AirportSelector
                label="出发地"
                placeholder="搜索出发机场..."
                onAirportSelected={handleDepartureSelect}
                value={departureAirport}
              />
              <AirportSelector
                label="目的地"
                placeholder="搜索目的地机场..."
                onAirportSelected={handleArrivalSelect}
                value={arrivalAirport}
              />
            </div>
          </div>

          {(departureAirport || arrivalAirport) && (
            <div className="mt-8 p-6 border border-[#E8E8ED] rounded-apple bg-[#F5F5F7] animate-fadeIn">
              <h3 className="text-lg font-semibold text-[#1D1D1F] mb-4 flex items-center">
                <svg className="h-5 w-5 mr-2 text-[#34C759]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                  <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clipRule="evenodd" />
                </svg>
                当前选择
              </h3>
              <div className="space-y-4">
                {departureAirport && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-2 h-2 bg-[#007AFF] rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-[#86868B]">出发地</p>
                      <p className="text-base text-[#1D1D1F] font-medium">
                        {departureAirport.name} ({departureAirport.code})
                      </p>
                      <p className="text-xs text-[#86868B] mt-1">
                        {departureAirport.city}, {departureAirport.country}
                      </p>
                    </div>
                  </div>
                )}
                {arrivalAirport && (
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 w-2 h-2 bg-[#FF9500] rounded-full mt-2"></div>
                    <div>
                      <p className="text-sm font-medium text-[#86868B]">目的地</p>
                      <p className="text-base text-[#1D1D1F] font-medium">
                        {arrivalAirport.name} ({arrivalAirport.code})
                      </p>
                      <p className="text-xs text-[#86868B] mt-1">
                        {arrivalAirport.city}, {arrivalAirport.country}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <footer className="mt-12 text-center text-sm text-[#86868B]">
        <p>AeroScout POI Search Test Environment</p>
      </footer>
    </div>
  );
};

export default PoiTestPage;