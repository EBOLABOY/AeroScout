'use client';

import React from 'react';
import Link from 'next/link';

export default function TermsPage() {
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
          <h1 className="text-xl font-bold text-white">服务条款</h1>
          <div className="w-20"></div>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 py-16">
        <div className="bg-white/95 backdrop-blur-3xl rounded-3xl shadow-2xl border border-white/20 p-8 sm:p-12">
          {/* 标题区域 */}
          <div className="text-center mb-12">
            <h1 className="text-[32px] font-bold text-gray-900 mb-4">服务条款</h1>
            <p className="text-[16px] text-gray-600">
              最后更新时间：{new Date().getFullYear()}年{new Date().getMonth() + 1}月{new Date().getDate()}日
            </p>
          </div>

          {/* 内容区域 */}
          <div className="space-y-8 text-gray-700">
            {/* 引言 */}
            <section>
              <p className="text-[16px] leading-relaxed">
                欢迎使用AeroScout航班搜索服务。本服务条款（"条款"）规定了您使用我们网站和服务的条件。使用我们的服务即表示您同意遵守这些条款。
              </p>
            </section>

            {/* 服务描述 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">1. 服务性质与范围</h2>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-6 mb-4">
                <h3 className="text-[18px] font-semibold text-blue-800 mb-3">核心服务定义</h3>
                <p className="text-[15px] text-blue-700 mb-4">
                  AeroScout是一个<strong>纯信息展示平台</strong>，我们的服务范围严格限定为：
                </p>
                <ul className="list-disc list-inside space-y-2 text-[15px] text-blue-700 ml-4">
                  <li><strong>信息聚合：</strong>从公开渠道收集和整理航班信息</li>
                  <li><strong>数据展示：</strong>以搜索结果形式展示航班信息</li>
                  <li><strong>比较工具：</strong>提供价格和时间的比较功能</li>
                  <li><strong>链接导航：</strong>引导用户到第三方网站查看详情</li>
                </ul>
              </div>

              <div className="bg-red-50 border-l-4 border-red-400 p-6 mb-4">
                <h3 className="text-[18px] font-semibold text-red-800 mb-3">明确服务边界</h3>
                <p className="text-[15px] text-red-700 mb-4">
                  <strong>我们明确声明，我们不是：</strong>
                </p>
                <ul className="list-disc list-inside space-y-2 text-[15px] text-red-700 ml-4">
                  <li>旅行社或票务代理</li>
                  <li>航空公司或其授权代理</li>
                  <li>机票销售商或预订服务商</li>
                  <li>旅行服务提供商</li>
                  <li>任何形式的交易中介</li>
                </ul>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
                <h3 className="text-[18px] font-semibold text-yellow-800 mb-3">用户行为独立性</h3>
                <p className="text-[15px] text-yellow-700">
                  <strong>重要声明：</strong>用户通过我们的平台获取信息后，其后续的所有预订、购买、旅行行为均为用户的独立决定和行为。我们对用户的任何旅行决策、预订方式、票务使用方法等不承担任何责任，也不提供任何建议或指导。
                </p>
              </div>
            </section>

            {/* 免责声明 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">2. 全面免责声明</h2>

              <div className="bg-red-50 border-l-4 border-red-400 p-6 mb-6">
                <h3 className="text-[18px] font-semibold text-red-800 mb-4">核心免责原则</h3>
                <div className="space-y-4 text-[15px] text-red-700">
                  <p><strong>2.1 纯信息服务：</strong>我们仅提供信息展示服务，不参与任何交易过程，不对用户基于信息做出的任何决定承担责任。</p>
                  <p><strong>2.2 用户自主决策：</strong>用户使用任何航班信息进行预订、旅行的行为完全基于个人判断，我们不承担任何相关责任。</p>
                  <p><strong>2.3 第三方关系：</strong>我们与任何航空公司、旅行社、票务代理均无合作关系，不对其服务、政策、条款承担任何责任。</p>
                </div>
              </div>

              <div className="bg-orange-50 border-l-4 border-orange-400 p-6 mb-6">
                <h3 className="text-[18px] font-semibold text-orange-800 mb-4">特殊旅行策略免责</h3>
                <div className="space-y-4 text-[15px] text-orange-700">
                  <p><strong>2.4 旅行方式选择：</strong>用户可能通过我们的信息了解到各种旅行路线和预订方式。我们明确声明：</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>我们不推荐、不建议、不指导任何特定的旅行方式</li>
                    <li>我们不对任何旅行策略的合规性、风险性进行评估</li>
                    <li>用户选择任何旅行方式的风险完全自负</li>
                    <li>我们不对因旅行方式选择导致的任何后果承担责任</li>
                  </ul>
                  <p><strong>2.5 航空公司政策：</strong>各航空公司有其独立的服务条款和政策，我们不对这些政策的解释、执行或变更承担任何责任。</p>
                </div>
              </div>

              <div className="bg-gray-50 border-l-4 border-gray-400 p-6 mb-6">
                <h3 className="text-[18px] font-semibold text-gray-800 mb-4">技术与信息免责</h3>
                <div className="space-y-3 text-[15px] text-gray-700">
                  <p><strong>2.6 信息准确性：</strong>航班信息来源于第三方，我们不保证信息的准确性、完整性、及时性或可靠性。</p>
                  <p><strong>2.7 技术故障：</strong>我们不对因技术故障、网络中断、系统维护、数据错误等导致的任何损失承担责任。</p>
                  <p><strong>2.8 外部链接：</strong>我们不对通过我们平台访问的第三方网站内容、服务或政策承担责任。</p>
                </div>
              </div>

              <div className="bg-purple-50 border-l-4 border-purple-400 p-6">
                <h3 className="text-[18px] font-semibold text-purple-800 mb-4">损失与责任限制</h3>
                <div className="space-y-3 text-[15px] text-purple-700">
                  <p><strong>2.9 损失免责：</strong>在任何情况下，我们均不对以下损失承担责任：</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>直接、间接、特殊、偶然或后果性损失</li>
                    <li>经济损失、利润损失、商业机会损失</li>
                    <li>旅行计划变更、行程延误、航班取消等损失</li>
                    <li>因使用我们服务而产生的任何法律纠纷</li>
                    <li>第三方对用户的任何索赔或诉讼</li>
                  </ul>
                  <p><strong>2.10 责任上限：</strong>即使在法律允许的最大范围内，我们的总责任也不超过零元人民币。</p>
                </div>
              </div>
            </section>

            {/* 特殊免责声明 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">3. 特殊旅行策略免责声明</h2>
              <div className="bg-red-100 border-2 border-red-400 p-8 mb-6">
                <h3 className="text-[20px] font-bold text-red-800 mb-4">⚠️ 重要法律声明</h3>
                <div className="space-y-4 text-[15px] text-red-700">
                  <p><strong>3.1 信息展示性质：</strong>我们的平台可能展示各种航班路线信息，包括但不限于直飞、中转、多段航班等。这些信息的展示纯属技术性数据聚合，不构成任何形式的建议、推荐或指导。</p>

                  <p><strong>3.2 用户决策独立性：</strong>用户基于我们平台信息做出的任何旅行决策，包括但不限于：</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>选择特定的航班路线</li>
                    <li>决定是否完成全程旅行</li>
                    <li>选择在中转城市停留或离开</li>
                    <li>任何形式的行程变更</li>
                  </ul>
                  <p>均为用户的完全自主行为，我们对此不承担任何责任。</p>

                  <p><strong>3.3 航空公司条款独立性：</strong>各航空公司拥有独立的运输条款、服务条件和政策规定。我们：</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>不是任何航空公司的代理或合作伙伴</li>
                    <li>不对航空公司的政策进行解释或建议</li>
                    <li>不对航空公司政策的执行承担任何责任</li>
                    <li>不对因航空公司政策变更导致的任何后果负责</li>
                  </ul>

                  <p><strong>3.4 法律风险自负：</strong>用户应当自行了解并遵守：</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>相关航空公司的完整服务条款</li>
                    <li>目的地国家/地区的入境要求</li>
                    <li>所有适用的法律法规</li>
                    <li>任何可能涉及的合同义务</li>
                  </ul>

                  <p><strong>3.5 绝对免责：</strong>我们对用户因任何旅行策略选择而可能面临的以下情况不承担任何责任：</p>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>航空公司的任何形式的处罚或限制</li>
                    <li>法律纠纷或诉讼</li>
                    <li>经济损失或额外费用</li>
                    <li>旅行计划的任何变更或取消</li>
                    <li>任何形式的声誉或信用影响</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* 用户责任 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">4. 用户责任与义务</h2>
              <div className="bg-blue-50 border border-blue-200 p-6 mb-4">
                <h3 className="text-[18px] font-semibold text-blue-800 mb-3">基本义务</h3>
                <p className="text-[15px] leading-relaxed mb-4">使用我们的服务时，您同意并承诺：</p>
                <ul className="list-disc list-inside space-y-2 text-[15px] text-blue-700 ml-4">
                  <li>仅将我们的服务用于合法目的</li>
                  <li>不干扰或破坏我们的服务</li>
                  <li>自行验证所有信息的准确性</li>
                  <li>自行承担所有旅行决策的风险和责任</li>
                  <li>遵守所有适用的法律法规</li>
                  <li>不将我们的服务用于任何商业目的</li>
                </ul>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 p-6">
                <h3 className="text-[18px] font-semibold text-yellow-800 mb-3">特别提醒</h3>
                <p className="text-[15px] text-yellow-700">
                  <strong>用户确认：</strong>您理解并同意，您通过我们的平台获取信息后的所有行为均为您的独立决定，您将自行承担所有相关风险和后果，包括但不限于与航空公司、旅行社或其他第三方可能产生的任何争议。
                </p>
              </div>
            </section>

            {/* 责任限制 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">4. 责任限制</h2>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                <div className="space-y-4 text-[15px]">
                  <p><strong>4.1 服务性质：</strong>我们的服务按"现状"提供，不提供任何明示或暗示的保证。</p>
                  <p><strong>4.2 损害赔偿上限：</strong>在任何情况下，我们的总责任不超过您在过去12个月内向我们支付的费用（如有）。</p>
                  <p><strong>4.3 不可抗力：</strong>我们不对因不可抗力事件（包括但不限于自然灾害、政府行为、网络攻击等）导致的损失承担责任。</p>
                  <p><strong>4.4 第三方链接：</strong>我们的网站可能包含第三方链接，我们不对这些第三方网站的内容或服务承担责任。</p>
                </div>
              </div>
            </section>

            {/* 知识产权 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">5. 知识产权</h2>
              <p className="text-[15px] leading-relaxed mb-4">
                我们的网站内容、设计、商标、标识等均受知识产权法保护。未经许可，您不得：
              </p>
              <ul className="list-disc list-inside space-y-2 text-[15px] ml-4">
                <li>复制、修改、分发我们的内容</li>
                <li>使用我们的商标或标识</li>
                <li>进行反向工程或数据抓取</li>
                <li>创建衍生作品</li>
              </ul>
            </section>

            {/* 隐私保护 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">6. 隐私保护</h2>
              <p className="text-[15px] leading-relaxed">
                您的隐私对我们很重要。我们的隐私政策详细说明了我们如何收集、使用和保护您的个人信息。使用我们的服务即表示您同意我们的隐私政策。
              </p>
            </section>

            {/* 服务变更 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">7. 服务变更和终止</h2>
              <div className="space-y-4 text-[15px]">
                <p><strong>7.1 服务变更：</strong>我们保留随时修改、暂停或终止服务的权利，恕不另行通知。</p>
                <p><strong>7.2 账户终止：</strong>我们可能因违反条款或其他原因终止您的账户。</p>
                <p><strong>7.3 数据保留：</strong>服务终止后，我们可能保留您的数据一段时间，具体见隐私政策。</p>
              </div>
            </section>

            {/* 争议解决 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">8. 争议解决</h2>
              <div className="space-y-4 text-[15px]">
                <p><strong>8.1 友好协商：</strong>如发生争议，双方应首先通过友好协商解决。</p>
                <p><strong>8.2 管辖法律：</strong>本条款受中华人民共和国法律管辖。</p>
                <p><strong>8.3 管辖法院：</strong>因本条款产生的争议应提交至我们所在地有管辖权的人民法院解决。</p>
              </div>
            </section>

            {/* 条款修改 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">9. 条款修改</h2>
              <p className="text-[15px] leading-relaxed">
                我们可能会不时更新这些条款。重大变更将通过网站通知。继续使用我们的服务即表示您接受修改后的条款。建议您定期查看本页面以了解最新条款。
              </p>
            </section>

            {/* 其他条款 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">10. 其他条款</h2>
              <div className="space-y-4 text-[15px]">
                <p><strong>10.1 完整协议：</strong>本条款构成您与我们之间的完整协议。</p>
                <p><strong>10.2 可分割性：</strong>如条款中任何部分被认定无效，其余部分仍然有效。</p>
                <p><strong>10.3 不弃权：</strong>我们未行使任何权利不构成对该权利的放弃。</p>
                <p><strong>10.4 语言版本：</strong>如有多语言版本，以中文版本为准。</p>
              </div>
            </section>

            {/* 联系方式 */}
            <section>
              <h2 className="text-[22px] font-semibold text-gray-900 mb-4">11. 联系我们</h2>
              <div className="bg-blue-50 rounded-2xl p-6">
                <p className="text-[15px] leading-relaxed mb-4">
                  如果您对本服务条款有任何疑问，请联系我们：
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
              <Link href="/privacy" className="text-blue-600 hover:text-blue-700 transition-colors">
                隐私政策
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
