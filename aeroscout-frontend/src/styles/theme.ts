// Apple设计风格的主题系统
// 基于苹果的设计语言，提供清晰、简洁、优雅的视觉体验

// 颜色系统
export const colors = {
  // 基础颜色 - 精确匹配苹果设计语言
  base: {
    background: '#ffffff',
    foreground: '#1D1D1F'
  },

  // 主色调 - 苹果官方蓝色
  primary: {
    light: '#E9F0FC',
    main: '#0071E3',
    dark: '#0051A2',
    contrast: '#FFFFFF'
  },

  // 中性色调 - 苹果风格灰度
  neutral: {
    50: '#F5F5F7',
    100: '#E8E8ED',
    200: '#D2D2D7',
    300: '#AEAEB2',
    400: '#8E8E93',
    500: '#636366',
    600: '#48484A',
    700: '#3A3A3C',
    800: '#2C2C2E',
    900: '#1C1C1E'
  },

  // 语义色彩 - 精确匹配苹果系统颜色
  semantic: {
    success: '#34C759', // 绿色
    warning: '#FF9500', // 橙色
    error: '#FF3B30',   // 红色
    info: '#007AFF',    // 蓝色
    purple: '#AF52DE'   // 紫色
  },

  // 苹果设计特有颜色
  teal: '#5AC8FA',    // 浅蓝
  indigo: '#5856D6',  // 靛蓝
  pink: '#FF2D55',    // 粉色

  // 背景色
  background: {
    primary: '#FFFFFF',
    secondary: '#F5F5F7',
    tertiary: '#FAFAFA'
  }
};

// 暗色模式颜色
export const darkColors = {
  // 暗色模式基础颜色
  base: {
    background: '#000000',
    foreground: '#F5F5F7'
  },

  // 暗色模式主色调
  primary: {
    light: '#0A84FF33',
    main: '#0A84FF',
    dark: '#0077ED',
    contrast: '#FFFFFF'
  },

  // 暗色模式中性色调 - 苹果风格
  neutral: {
    50: '#1C1C1E',
    100: '#2C2C2E',
    200: '#3A3A3C',
    300: '#48484A',
    400: '#636366',
    500: '#8E8E93',
    600: '#AEAEB2',
    700: '#C7C7CC',
    800: '#E5E5EA',
    900: '#F2F2F7'
  },

  // 暗色模式语义色彩 - 苹果系统颜色
  semantic: {
    success: '#30D158', // 暗色模式绿色
    warning: '#FF9F0A', // 暗色模式橙色
    error: '#FF453A',   // 暗色模式红色
    info: '#0A84FF',    // 暗色模式蓝色
    purple: '#BF5AF2'   // 暗色模式紫色
  },

  // 暗色模式苹果特有颜色
  teal: '#64D2FF',    // 暗色模式浅蓝
  indigo: '#5E5CE6',  // 暗色模式靛蓝
  pink: '#FF375F'     // 暗色模式粉色
};

// 排版系统
export const typography = {
  fontFamily: {
    base: 'SF Pro Text, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    display: 'SF Pro Display, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    mono: 'SF Mono, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace'
  },
  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  },
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem'      // 48px
  },
  lineHeight: {
    none: 1,
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75
  }
};

// 间距和圆角
export const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
  20: '5rem',    // 80px
  24: '6rem'     // 96px
};

export const borderRadius = {
  none: '0',
  sm: '0.25rem',    // 4px
  md: '0.5rem',     // 8px
  lg: '0.75rem',    // 12px
  xl: '1rem',       // 16px
  '2xl': '1.5rem',  // 24px
  full: '9999px'
};

// 阴影
export const shadows = {
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
  none: 'none'
};

// 动画
export const animations = {
  transition: {
    fast: 'all 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    medium: 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    slow: 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    bounce: 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
  }
};

// 导出完整主题
const theme = {
  colors,
  darkColors,
  typography,
  spacing,
  borderRadius,
  shadows,
  animations
};

export default theme;
