'use client';

import React, { useState, useEffect } from 'react';
import Button from './Button';
import { legalService, ProbeStrategySubtype } from '../../services/legalService';

interface RiskConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  itineraryId: string;
  probeHub?: string;
  probeDisclaimer?: string;
  probeStrategy?: string; // 探测策略：'a-b' 或 'a-b-x'
}

const RiskConfirmationModal: React.FC<RiskConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  itineraryId,
  probeHub,
  probeDisclaimer,
  probeStrategy
}) => {
  const [isAcknowledged, setIsAcknowledged] = useState(false);
  const [riskText, setRiskText] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  
  // 根据探测策略获取风险确认文本
  useEffect(() => {
    const fetchRiskText = async () => {
      if (!isOpen) return;
      
      try {
        setIsLoading(true);
        
        // 如果已有probeDisclaimer，直接使用
        if (probeDisclaimer) {
          setRiskText(probeDisclaimer);
          return;
        }
        
        // 否则，根据探测策略获取对应的风险确认文本
        if (probeStrategy) {
          const strategy = probeStrategy.toLowerCase() === 'a-b-x'
            ? ProbeStrategySubtype.A_B_X
            : ProbeStrategySubtype.A_B;
            
          const text = await legalService.getRiskConfirmationText(strategy);
          setRiskText(text);
        } else {
          // 默认使用A-B策略
          const text = await legalService.getRiskConfirmationText(ProbeStrategySubtype.A_B);
          setRiskText(text);
        }
      } catch (error) {
        console.error('获取风险确认文本失败:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRiskText();
  }, [isOpen, probeDisclaimer, probeStrategy]);
  
  // Reset acknowledgment when modal opens
  useEffect(() => {
    if (isOpen) {
      setIsAcknowledged(false);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    if (isAcknowledged) {
      onConfirm();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 animate-fadeIn">
      <div className="bg-white rounded-apple max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-apple">
        <div className="p-6">
          <div className="flex items-start">
            <div className="h-12 w-12 bg-[#FF3B30] rounded-full flex items-center justify-center flex-shrink-0 mr-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-[#1D1D1F] mb-2">重要法律风险警告</h2>
              <p className="text-[#86868B]">请在继续前仔细阅读以下风险提示</p>
            </div>
          </div>

          {isLoading ? (
            <div className="mt-6 p-4 bg-[#F5F5F7] rounded-apple flex justify-center">
              <p className="text-md text-[#86868B]">加载中...</p>
            </div>
          ) : (
            <div className="mt-6">
              <div
                className="p-4 bg-[#FFF1F0] border-2 border-[#FF3B30] rounded-apple"
                dangerouslySetInnerHTML={{ __html: riskText }}
              />
            </div>
          )}

          {probeHub && (
            <div className="mt-6 p-4 bg-[#FFF8E6] border-2 border-[#FF9500] rounded-apple flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-[#FF9500] mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-md font-bold text-[#FF9500]">探测枢纽: <strong>{probeHub}</strong></span>
            </div>
          )}

          <div className="mt-6 p-4 bg-[#FFFBEB] border border-[#F59E0B] rounded-apple">
            <p className="text-md font-medium text-[#B45309]">
              预订此航班即表示您已完全了解并自愿接受相关风险。AeroScout不对因&quot;跳机&quot;行为导致的任何损失负责。
            </p>
          </div>

          <div className="mt-6 flex items-center">
            <input 
              type="checkbox" 
              id={`risk-modal-acknowledge-${itineraryId}`} 
              checked={isAcknowledged}
              onChange={(e) => setIsAcknowledged(e.target.checked)}
              className="h-5 w-5 text-[#FF3B30] border-[#FF3B30] rounded focus:ring-[#FF3B30]" 
            />
            <label htmlFor={`risk-modal-acknowledge-${itineraryId}`} className="ml-3 block text-md text-[#1D1D1F] font-medium">
              我已阅读并理解上述风险警告，并自愿承担相关风险
            </label>
          </div>
        </div>

        <div className="border-t border-[#E8E8ED] p-4 flex flex-col sm:flex-row-reverse gap-3">
          <Button
            onClick={handleConfirm}
            disabled={!isAcknowledged}
            variant="danger"
            size="lg"
            className="w-full sm:w-auto"
          >
            我已了解风险，继续预订
          </Button>
          <Button
            onClick={onClose}
            variant="tertiary"
            size="lg"
            className="w-full sm:w-auto"
          >
            取消
          </Button>
        </div>
      </div>
    </div>
  );
};

export default RiskConfirmationModal;
