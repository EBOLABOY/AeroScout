/**
 * 机场相关类型定义
 */

export interface Airport {
  code: string;
  name: string;
  city: string;
  country: string;
  type?: string;
  timezone?: string;
  coordinates?: {
    latitude: number;
    longitude: number;
  };
}

export interface AirportSearchResult {
  airports: Airport[];
  total: number;
  query: string;
}

export interface AirportSearchRequest {
  query: string;
  trip_type: 'flight' | 'train' | 'bus';
  mode: 'dep' | 'arr' | 'both';
  limit?: number;
} 