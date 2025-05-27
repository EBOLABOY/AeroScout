'use client';

import React from 'react';
import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#007AFF] via-[#5856D6] to-[#AF52DE]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-purple-300/5 rounded-full blur-3xl animate-float-delayed"></div>
      </div>

      {/* 顶部导航 */}
      <nav className="relative z-10 bg-white/8 backdrop-blur-3xl border-b border-white/15">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/search" className="flex items-center space-x-2 text-white hover:text-white/80 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="font-medium">返回首页</span>
          </Link>
          <h1 className="text-xl font-bold text-white">隐私政策</h1>
          <div className="w-20"></div>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 py-16">
        <div className="bg-white/95 backdrop-blur-3xl rounded-3xl shadow-2xl border border-white/20 p-8 sm:p-12">
          {/* 标题区域 */}
          <div className="text-center mb-12">
            <h1 className="text-[32px] font-bold text-gray-900 mb-4">隐私政策</h1>
            <p className="text-[16px] text-gray-600">
              最后更新时间：{new Date().getFullYear()}年{new Date().getMonth() + 1}月{new Date().getDate()}日
            </p>
          </div>

          {/* 内容区域 */}
          <div className="space-y-8 text-gray-700">
            {/* 引言 */}
            <section>
              <p className="text-[16px] leading-relaxed">
                AeroScout（"我们"、"我们的"或"本公司"）非常重视您的隐私保护。本隐私政策说明了我们如何收集、使用、存储和保护您的个人信息。使用我们的服务即表示您同意本隐私政策的条款。
              </p>
            </section>

            {/* 信息收集 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">1. 我们收集的信息</h2>
              <div className="space-y-4">
                <div>
                  <h3 className="text-[18px] font-semibold text-gray-800 mb-2">1.1 您主动提供的信息</h3>
                  <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                    <li>注册账户时提供的基本信息（邮箱、用户名等）</li>
                    <li>搜索航班时输入的出发地、目的地、日期等信息</li>
                    <li>联系我们时提供的信息</li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-[18px] font-semibold text-gray-800 mb-2">1.2 自动收集的信息</h3>
                  <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                    <li>设备信息（IP地址、浏览器类型、操作系统等）</li>
                    <li>使用数据（访问时间、页面浏览记录等）</li>
                    <li>Cookie和类似技术收集的信息</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 信息使用 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">2. 信息使用方式</h2>
              <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                <li>提供、维护和改进我们的服务</li>
                <li>处理您的搜索请求并显示相关结果</li>
                <li>发送服务相关的通知和更新</li>
                <li>分析用户行为以优化用户体验</li>
                <li>防止欺诈和确保服务安全</li>
                <li>遵守法律法规要求</li>
              </ul>
            </section>

            {/* 信息共享 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">3. 信息共享</h2>
              <p className="text-[15px] leading-relaxed mb-4">
                我们不会出售、租赁或以其他方式向第三方披露您的个人信息，除非：
              </p>
              <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                <li>获得您的明确同意</li>
                <li>与可信的服务提供商共享，以提供服务（如航空公司、支付处理商）</li>
                <li>法律要求或政府部门要求</li>
                <li>保护我们的权利、财产或安全</li>
                <li>业务转让或合并情况下</li>
              </ul>
            </section>

            {/* 数据安全 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">4. 数据安全</h2>
              <p className="text-[15px] leading-relaxed mb-4">
                我们采用行业标准的安全措施来保护您的个人信息：
              </p>
              <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                <li>使用SSL加密技术保护数据传输</li>
                <li>实施访问控制和身份验证机制</li>
                <li>定期进行安全审计和漏洞扫描</li>
                <li>员工隐私培训和保密协议</li>
                <li>数据备份和灾难恢复计划</li>
              </ul>
            </section>

            {/* Cookie政策 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">5. Cookie和跟踪技术</h2>
              <p className="text-[15px] leading-relaxed mb-4">
                我们使用Cookie和类似技术来：
              </p>
              <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                <li>记住您的偏好设置</li>
                <li>分析网站使用情况</li>
                <li>提供个性化内容</li>
                <li>改善网站性能</li>
              </ul>
              <p className="text-[15px] leading-relaxed mt-4">
                您可以通过浏览器设置管理Cookie偏好，但这可能影响某些功能的使用。
              </p>
            </section>

            {/* 您的权利 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">6. 您的权利</h2>
              <p className="text-[15px] leading-relaxed mb-4">
                您对自己的个人信息享有以下权利：
              </p>
              <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                <li>访问权：查看我们持有的您的个人信息</li>
                <li>更正权：要求更正不准确的信息</li>
                <li>删除权：要求删除您的个人信息</li>
                <li>限制处理权：限制我们处理您的信息</li>
                <li>数据可携权：获取您的数据副本</li>
                <li>反对权：反对我们处理您的信息</li>
              </ul>
              <p className="text-[15px] leading-relaxed mt-4">
                如需行使这些权利，请通过 1242772513@izlx.de 联系我们，或添加微信 Xinx--1996。
              </p>
            </section>

            {/* 数据保留 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">7. 数据保留</h2>
              <p className="text-[15px] leading-relaxed">
                我们仅在必要期间保留您的个人信息，具体保留期限取决于信息类型和使用目的。一般情况下，账户信息在账户删除后30天内删除，搜索记录保留12个月用于服务改进。
              </p>
            </section>

            {/* 儿童隐私 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">8. 儿童隐私保护</h2>
              <p className="text-[15px] leading-relaxed">
                我们的服务面向18岁以上用户。我们不会故意收集18岁以下儿童的个人信息。如果我们发现收集了儿童信息，将立即删除。
              </p>
            </section>

            {/* 政策更新 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">9. 隐私政策更新</h2>
              <p className="text-[15px] leading-relaxed">
                我们可能会不时更新本隐私政策。重大变更将通过网站通知或邮件形式告知您。继续使用我们的服务即表示您接受更新后的政策。
              </p>
            </section>

            {/* 联系方式 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">10. 联系我们</h2>
              <div className="bg-blue-50 rounded-2xl p-6">
                <p className="text-[15px] leading-relaxed mb-4">
                  如果您对本隐私政策有任何疑问或需要帮助，请通过以下方式联系我们：
                </p>
                <div className="space-y-2 text-[15px]">
                  <p><strong>邮箱：</strong> 1242772513@izlx.de</p>
                  <p><strong>微信：</strong> Xinx--1996</p>
                  <p><strong>客服时间：</strong> 周一至周日 9:00-21:00</p>
                </div>
              </div>
            </section>
          </div>

          {/* 底部导航 */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="flex flex-wrap justify-center gap-6 text-[14px]">
              <Link href="/about" className="text-blue-600 hover:text-blue-700 transition-colors">
                关于我们
              </Link>
              <Link href="/terms" className="text-blue-600 hover:text-blue-700 transition-colors">
                服务条款
              </Link>
              <Link href="/search" className="text-blue-600 hover:text-blue-700 transition-colors">
                返回搜索
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
