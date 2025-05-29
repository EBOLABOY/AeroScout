/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    screens: {
      'xs': '375px',   // 小手机
      'sm': '640px',   // 大手机
      'md': '768px',   // 平板
      'lg': '1024px',  // 小桌面
      'xl': '1280px',  // 大桌面
      '2xl': '1536px', // 超大桌面
    },
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
      },
      fontSize: {
        'xs-mobile': ['10px', '14px'],
        'sm-mobile': ['12px', '16px'],
        'base-mobile': ['14px', '20px'],
        'lg-mobile': ['16px', '24px'],
        'xl-mobile': ['18px', '28px'],
        '2xl-mobile': ['20px', '28px'],
        '3xl-mobile': ['24px', '32px'],
        '4xl-mobile': ['28px', '36px'],
        '5xl-mobile': ['32px', '40px'],
      },
      minHeight: {
        'screen-safe': 'calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom))',
      },
      maxWidth: {
        'mobile': '375px',
        'mobile-lg': '414px',
      },
    },
  },
  plugins: [],
}
