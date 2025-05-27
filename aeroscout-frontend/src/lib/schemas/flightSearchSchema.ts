/**
 * 航班搜索表单验证Schema
 */
import { z } from 'zod';

export const flightSearchSchema = z.object({
  originIata: z
    .string()
    .min(3, '出发地IATA代码必须为3位字符')
    .max(3, '出发地IATA代码必须为3位字符')
    .regex(/^[A-Z]{3}$/, '出发地IATA代码格式不正确'),
  
  destinationIata: z
    .string()
    .min(3, '目的地IATA代码必须为3位字符')
    .max(3, '目的地IATA代码必须为3位字符')
    .regex(/^[A-Z]{3}$/, '目的地IATA代码格式不正确'),
  
  departureDate: z
    .string()
    .min(1, '出发日期不能为空')
    .regex(/^\d{4}-\d{2}-\d{2}$/, '出发日期格式不正确'),
  
  returnDate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, '返程日期格式不正确')
    .optional()
    .or(z.literal('')),
  
  tripType: z.enum(['one-way', 'round-trip']),
  
  adults: z
    .number()
    .min(1, '至少需要1位成人乘客')
    .max(9, '最多支持9位成人乘客'),
  
  children: z
    .number()
    .min(0, '儿童数量不能为负数')
    .max(9, '最多支持9位儿童乘客')
    .default(0),
  
  infants: z
    .number()
    .min(0, '婴儿数量不能为负数')
    .max(9, '最多支持9位婴儿乘客')
    .default(0),
  
  cabinClass: z.enum(['ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']),
  
  directFlightsOnly: z.boolean().default(false),
  
  enableHubProbe: z.boolean().default(true),
  
}).refine((data) => {
  // 验证往返行程必须有返程日期
  if (data.tripType === 'round-trip') {
    return data.returnDate && data.returnDate.length > 0;
  }
  return true;
}, {
  message: '往返行程必须选择返程日期',
  path: ['returnDate'],
}).refine((data) => {
  // 验证返程日期不能早于出发日期
  if (data.tripType === 'round-trip' && data.returnDate && data.departureDate) {
    return new Date(data.returnDate) >= new Date(data.departureDate);
  }
  return true;
}, {
  message: '返程日期不能早于出发日期',
  path: ['returnDate'],
}).refine((data) => {
  // 验证出发地和目的地不能相同
  return data.originIata !== data.destinationIata;
}, {
  message: '出发地和目的地不能相同',
  path: ['destinationIata'],
});

export type FlightSearchFormData = z.infer<typeof flightSearchSchema>; 