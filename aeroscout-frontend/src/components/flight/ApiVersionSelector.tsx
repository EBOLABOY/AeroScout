/**
 * API版本选择组件
 * 独立组件，避免修改主搜索表单的类型复杂性
 */
import React from 'react';

interface ApiVersionSelectorProps {
  value: 'v1' | 'v2';
  onChange: (version: 'v1' | 'v2') => void;
  showBadge?: boolean;
}

const ApiVersionSelector: React.FC<ApiVersionSelectorProps> = ({ 
  value, 
  onChange, 
  showBadge = true 
}) => {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-blue-900">
          搜索引擎版本
        </label>
        {showBadge && (
          <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">
            实验性功能
          </span>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* V1 选项 */}
        <div 
          className={`
            relative p-3 border-2 rounded-lg cursor-pointer transition-all
            ${value === 'v1' 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-200 bg-white hover:border-gray-300'
            }
          `}
          onClick={() => onChange('v1')}
        >
          <div className="flex items-start space-x-3">
            <input
              type="radio"
              value="v1"
              checked={value === 'v1'}
              onChange={() => onChange('v1')}
              className="mt-1 text-blue-600"
            />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900">
                标准搜索 (V1)
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                经典航班搜索，稳定快速
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                  直飞航班
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                  经典搜索
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* V2 选项 */}
        <div 
          className={`
            relative p-3 border-2 rounded-lg cursor-pointer transition-all
            ${value === 'v2' 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-200 bg-white hover:border-gray-300'
            }
          `}
          onClick={() => onChange('v2')}
        >
          <div className="flex items-start space-x-3">
            <input
              type="radio"
              value="v2"
              checked={value === 'v2'}
              onChange={() => onChange('v2')}
              className="mt-1 text-blue-600"
            />
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900">
                智能搜索 (V2)
                <span className="ml-2 text-xs text-blue-600 font-normal">推荐</span>
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                分阶段搜索，发现更多优惠
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                  甩尾票
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                  质量评分
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                  风险评估
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
                  枢纽探测
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 功能对比提示 */}
      <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
        💡 <strong>V2智能搜索特色：</strong>
        {value === 'v2' ? (
          <span className="ml-1">
            先搜索直飞和甩尾票，再探测枢纽城市，发现更多便宜的机票组合
          </span>
        ) : (
          <span className="ml-1">
            选择V2体验分阶段搜索、质量评分等智能功能
          </span>
        )}
      </div>
    </div>
  );
};

export default ApiVersionSelector; 