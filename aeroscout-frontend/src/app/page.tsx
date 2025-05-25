'use client';

import FlightSearchForm from '@/components/flight/FlightSearchForm';
import Button from '@/components/common/Button';
import Earth3D from '@/components/Earth3D';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* 顶部导航 - 苹果官网风格 */}
      <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-[#E5E5EA]">
        <div className="max-w-[980px] mx-auto px-5 py-3 flex justify-between items-center">
          <div>
            <Link href="/" className="text-[21px] font-medium text-[#1D1D1F] bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] bg-clip-text text-transparent transition-apple hover:opacity-80">AeroScout</Link>
          </div>

          {/* 移动端菜单按钮 */}
          <div className="md:hidden">
            <button className="p-2 rounded-full hover:bg-[#F5F5F7] transition-apple">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#1D1D1F]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* 桌面端导航 */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/auth/login"
              className="text-[14px] font-medium text-[#1D1D1F] hover:text-[#0071E3] px-3 py-1.5 rounded-full transition-apple"
            >
              登录
            </Link>
            <Link
              href="/auth/register"
              className="text-[14px] font-medium text-white bg-[#0071E3] hover:bg-[#0077ED] px-4 py-1.5 rounded-full shadow-apple-sm transition-apple"
            >
              注册
            </Link>
          </div>
        </div>
      </nav>

      {/* 主标题区 - 活力旅行风格 */}
      <section className="bg-white pt-8 pb-16 mb-8">
        <div className="max-w-[980px] mx-auto px-5">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="text-left mb-8 md:mb-0 md:max-w-md">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 rounded-full bg-[#FF9500] flex items-center justify-center mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
                <span className="text-[16px] font-medium text-[#FF9500]">旅行从未如此简单</span>
              </div>
              <h1 className="text-[44px] font-bold text-[#1D1D1F] tracking-tight leading-tight mb-4">发现您的<br/><span className="text-[#FF9500]">下一站</span>精彩</h1>
              <p className="text-[18px] text-[#86868B] mb-6">智能搜索全球航班，为您找到最优惠的价格和最佳的旅行组合</p>
              <div className="flex items-center">
                <div className="flex -space-x-2 mr-4">
                  <div className="w-8 h-8 rounded-full bg-[#0066CC] flex items-center justify-center border-2 border-white">
                    <span className="text-[10px] text-white font-bold">500+</span>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-[#34C759] flex items-center justify-center border-2 border-white">
                    <span className="text-[10px] text-white font-bold">30%</span>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-[#FF9500] flex items-center justify-center border-2 border-white">
                    <span className="text-[10px] text-white font-bold">24/7</span>
                  </div>
                </div>
                <span className="text-[14px] text-[#86868B]">已为超过100万用户提供服务</span>
              </div>
            </div>
            <div className="relative -mt-16">
              {/* 3D地球组件 */}
              <div className="w-96 h-96 relative">
                {/* 3D地球组件 */}
                <Earth3D />

                {/* 轨道环 - 装饰效果 */}
                <div className="absolute inset-[-15px] border-2 border-white/10 rounded-full pointer-events-none"></div>
                <div className="absolute inset-[-30px] border border-white/5 rounded-full pointer-events-none"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 搜索表单区域 - 苹果风格 */}
      <section className="max-w-[980px] mx-auto px-5 -mt-28 mb-8 relative z-10">
        <FlightSearchForm />
      </section>

      {/* 特性介绍 - 苹果风格标题 */}
      <section className="max-w-[980px] mx-auto px-5 py-16 text-center">
        <h2 className="text-[32px] font-semibold text-[#1D1D1F] mb-2">智能航班搜索</h2>
        <p className="text-[19px] text-[#86868B] max-w-2xl mx-auto mb-16">
          我们的算法可以发现传统搜索引擎无法找到的航班组合，平均为您节省 30% 的旅行成本。
        </p>

        {/* 特性卡片 - 苹果风格网格 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-b from-[#E6F2FF] to-white rounded-2xl p-8 shadow-md flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] rounded-full flex items-center justify-center mb-6 shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">多航司组合</h3>
            <p className="text-[15px] text-[#86868B] mb-6">
              智能组合不同航空公司的航班，发现隐藏的价格优势。
            </p>
            <Button variant="link" size="sm" className="mt-auto text-[#0066CC]">查看示例</Button>
          </div>

          <div className="bg-gradient-to-b from-[#E6FFF2] to-white rounded-2xl p-8 shadow-md flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-[#34C759] to-[#30D158] rounded-full flex items-center justify-center mb-6 shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">价格保障</h3>
            <p className="text-[15px] text-[#86868B] mb-6">
              透明定价，显示所有税费和附加费用，无隐藏收费。
            </p>
            <Button variant="link" size="sm" className="mt-auto text-[#34C759]">了解详情</Button>
          </div>

          <div className="bg-gradient-to-b from-[#FFF8E6] to-white rounded-2xl p-8 shadow-md flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-[#FF9500] to-[#FFCC00] rounded-full flex items-center justify-center mb-6 shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">价格追踪</h3>
            <p className="text-[15px] text-[#86868B] mb-6">
              设置价格提醒，当您关注的航线价格下降时获得通知。
            </p>
            <Button variant="link" size="sm" className="mt-auto text-[#FF9500]">开始追踪</Button>
          </div>
        </div>
      </section>

      {/* 会员服务 - 渐变背景 */}
      <section className="bg-gradient-to-r from-[#000428] to-[#004e92] py-20 my-16 rounded-3xl mx-5 overflow-hidden relative">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxkZWZzPjxwYXR0ZXJuIGlkPSJwYXR0ZXJuIiB4PSIwIiB5PSIwIiB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHBhdHRlcm5UcmFuc2Zvcm09InJvdGF0ZSgzMCkiPjxyZWN0IHg9IjAiIHk9IjAiIHdpZHRoPSIyIiBoZWlnaHQ9IjIiIGZpbGw9IiNmZmZmZmYiIG9wYWNpdHk9IjAuMDUiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjcGF0dGVybikiLz48L3N2Zz4=')] opacity-50"></div>
        <div className="max-w-[980px] mx-auto px-5 text-center relative z-10">
          <div className="inline-block mb-6 bg-white/10 backdrop-blur-md px-6 py-2 rounded-full">
            <span className="text-[15px] font-medium text-white">全新上线</span>
          </div>
          <h2 className="text-[40px] font-semibold text-white mb-4">AeroScout+</h2>
          <p className="text-[21px] text-white/80 max-w-2xl mx-auto mb-10">
            订阅会员服务，享受独家优惠和高级功能。
          </p>
          <Button variant="primary" size="lg" className="bg-gradient-to-r from-[#5AC8FA] to-[#0066CC] text-white hover:opacity-90 px-8 py-3 rounded-full shadow-lg font-medium">了解更多</Button>
        </div>
      </section>

      {/* 全球覆盖 - 现代卡片设计 */}
      <section className="py-16 my-12">
        <div className="max-w-[980px] mx-auto px-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-[32px] font-semibold text-[#1D1D1F] mb-4">全球覆盖</h2>
              <p className="text-[17px] text-[#86868B] mb-8">
                搜索全球数百家航空公司，覆盖所有主要航线。无论您想去哪里，我们都能帮您找到最佳航班。
              </p>
              <ul className="space-y-5">
                <li className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[#0066CC]/10 to-[#5AC8FA]/10 flex items-center justify-center mr-4">
                    <svg className="w-5 h-5 text-[#0066CC]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-[16px] text-[#1D1D1F]">覆盖全球 200+ 个国家和地区</span>
                </li>
                <li className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[#0066CC]/10 to-[#5AC8FA]/10 flex items-center justify-center mr-4">
                    <svg className="w-5 h-5 text-[#0066CC]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-[16px] text-[#1D1D1F]">支持 500+ 家航空公司搜索</span>
                </li>
                <li className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-[#0066CC]/10 to-[#5AC8FA]/10 flex items-center justify-center mr-4">
                    <svg className="w-5 h-5 text-[#0066CC]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-[16px] text-[#1D1D1F]">每月为超过 100 万用户提供服务</span>
                </li>
              </ul>
            </div>
            <div className="bg-gradient-to-br from-[#E6F2FF] to-white rounded-2xl p-10 shadow-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-[64px] font-bold bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] bg-clip-text text-transparent">30%</div>
                <p className="text-[19px] text-[#1D1D1F] mt-2">平均节省的旅行成本</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 页脚 - 现代简约风格 */}
      <footer className="border-t border-[#E5E5EA] py-16">
        <div className="max-w-[980px] mx-auto px-5">
          <div className="flex flex-col md:flex-row justify-between mb-12">
            <div className="mb-8 md:mb-0">
              <span className="text-[24px] font-medium bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] bg-clip-text text-transparent">AeroScout</span>
              <p className="text-[14px] text-[#86868B] mt-3 max-w-xs">
                智能航班搜索，发现最佳组合，节省您的旅行成本。
              </p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
              <div>
                <h4 className="text-[14px] font-semibold text-[#1D1D1F] mb-4">关于我们</h4>
                <ul className="space-y-3">
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">公司介绍</a></li>
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">新闻中心</a></li>
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">联系我们</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-[14px] font-semibold text-[#1D1D1F] mb-4">服务支持</h4>
                <ul className="space-y-3">
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">帮助中心</a></li>
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">联系客服</a></li>
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">常见问题</a></li>
                </ul>
              </div>
              <div>
                <h4 className="text-[14px] font-semibold text-[#1D1D1F] mb-4">法律信息</h4>
                <ul className="space-y-3">
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">隐私政策</a></li>
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">使用条款</a></li>
                  <li><a href="#" className="text-[14px] text-[#86868B] hover:text-[#0066CC] transition-colors">销售政策</a></li>
                </ul>
              </div>
            </div>
          </div>

          <div className="border-t border-[#E5E5EA] pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-[14px] text-[#86868B] mb-4 md:mb-0">
              &copy; {new Date().getFullYear()} AeroScout. 保留所有权利.
            </p>
            <div className="flex space-x-6">
              <a href="#" className="text-[#86868B] hover:text-[#0066CC]">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M16 8.049c0-4.446-3.582-8.05-8-8.05C3.58 0-.002 3.603-.002 8.05c0 4.017 2.926 7.347 6.75 7.951v-5.625h-2.03V8.05H6.75V6.275c0-2.017 1.195-3.131 3.022-3.131.876 0 1.791.157 1.791.157v1.98h-1.009c-.993 0-1.303.621-1.303 1.258v1.51h2.218l-.354 2.326H9.25V16c3.824-.604 6.75-3.934 6.75-7.951z"/>
                </svg>
              </a>
              <a href="#" className="text-[#86868B] hover:text-[#0066CC]">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334 0-.14 0-.282-.006-.422A6.685 6.685 0 0 0 16 3.542a6.658 6.658 0 0 1-1.889.518 3.301 3.301 0 0 0 1.447-1.817 6.533 6.533 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.325 9.325 0 0 1-6.767-3.429 3.289 3.289 0 0 0 1.018 4.382A3.323 3.323 0 0 1 .64 6.575v.045a3.288 3.288 0 0 0 2.632 3.218 3.203 3.203 0 0 1-.865.115 3.23 3.23 0 0 1-.614-.057 3.283 3.283 0 0 0 3.067 2.277A6.588 6.588 0 0 1 .78 13.58a6.32 6.32 0 0 1-.78-.045A9.344 9.344 0 0 0 5.026 15z"/>
                </svg>
              </a>
              <a href="#" className="text-[#86868B] hover:text-[#0066CC]">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 0C5.829 0 5.556.01 4.703.048 3.85.088 3.269.222 2.76.42a3.917 3.917 0 0 0-1.417.923A3.927 3.927 0 0 0 .42 2.76C.222 3.268.087 3.85.048 4.7.01 5.555 0 5.827 0 8.001c0 2.172.01 2.444.048 3.297.04.852.174 1.433.372 1.942.205.526.478.972.923 1.417.444.445.89.719 1.416.923.51.198 1.09.333 1.942.372C5.555 15.99 5.827 16 8 16s2.444-.01 3.298-.048c.851-.04 1.434-.174 1.943-.372a3.916 3.916 0 0 0 1.416-.923c.445-.445.718-.891.923-1.417.197-.509.332-1.09.372-1.942C15.99 10.445 16 10.173 16 8s-.01-2.445-.048-3.299c-.04-.851-.175-1.433-.372-1.941a3.926 3.926 0 0 0-.923-1.417A3.911 3.911 0 0 0 13.24.42c-.51-.198-1.092-.333-1.943-.372C10.443.01 10.172 0 7.998 0h.003zm-.717 1.442h.718c2.136 0 2.389.007 3.232.046.78.035 1.204.166 1.486.275.373.145.64.319.92.599.28.28.453.546.598.92.11.281.24.705.275 1.485.039.843.047 1.096.047 3.231s-.008 2.389-.047 3.232c-.035.78-.166 1.203-.275 1.485a2.47 2.47 0 0 1-.599.919c-.28.28-.546.453-.92.598-.28.11-.704.24-1.485.276-.843.038-1.096.047-3.232.047s-2.39-.009-3.233-.047c-.78-.036-1.203-.166-1.485-.276a2.478 2.478 0 0 1-.92-.598 2.48 2.48 0 0 1-.6-.92c-.109-.281-.24-.705-.275-1.485-.038-.843-.046-1.096-.046-3.233 0-2.136.008-2.388.046-3.231.036-.78.166-1.204.276-1.486.145-.373.319-.64.599-.92.28-.28.546-.453.92-.598.282-.11.705-.24 1.485-.276.738-.034 1.024-.044 2.515-.045v.002zm4.988 1.328a.96.96 0 1 0 0 1.92.96.96 0 0 0 0-1.92zm-4.27 1.122a4.109 4.109 0 1 0 0 8.217 4.109 4.109 0 0 0 0-8.217zm0 1.441a2.667 2.667 0 1 1 0 5.334 2.667 2.667 0 0 1 0-5.334z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
