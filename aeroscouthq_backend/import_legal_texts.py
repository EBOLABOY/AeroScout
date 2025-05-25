import asyncio
import os
from datetime import datetime

from app.database.connection import connect_db, disconnect_db
from app.database.crud import legal_crud

# 初始法律文本内容

# 通用免责声明内容
DISCLAIMER_CONTENT = """
<p>欢迎使用 AeroScout！在您继续之前，请仔细阅读以下重要声明。</p>
<p>本应用提供的所有信息，包括但不限于航班信息、价格、"多段组合推荐"及其他相关内容，均仅供一般参考之用，不构成任何形式的专业建议（例如旅行、财务或法律建议）。</p>
<p>所有信息均基于第三方数据源。我们尽力确保所提供信息的准确性和及时性，但不对其完整性、准确性、可靠性、适用性或可用性作任何明示或暗示的保证或陈述。</p>
<p>您理解并同意，您对本应用所提供信息的任何依赖和使用均由您自行承担风险。</p>
<p>在任何情况下，对于因使用或依赖本应用信息而直接或间接导致的任何性质的损失或损害（包括但不限于数据丢失或利润损失），AeroScout 及其关联方均不承担任何责任。我们强烈建议您在做出任何旅行决策或采取任何行动前，通过官方渠道（如航空公司、机场官方网站或授权代理）对所有信息进行独立核实。</p>
"""

# A-B模式风险确认文本
AB_RISK_CONTENT = """
<p>此优惠可能依赖于您在特定中转点放弃后续行程（俗称"跳机"），这可能违反航空公司的运输条款。</p>
<p>请注意以下法律风险：</p>
<ul>
  <li>航空公司可能取消您的回程或后续航段</li>
  <li>可能影响您的常旅客积分和会员状态</li>
  <li>在某些情况下，航空公司可能要求补缴票价差额</li>
  <li>可能违反航空公司运输条款，导致法律纠纷</li>
</ul>
<p>预订此航班即表示您已完全了解并自愿接受相关风险。AeroScout不对因"跳机"行为导致的任何损失负责。</p>
"""
# A-B-X模式风险确认文本
ABX_RISK_CONTENT = """
<p>此优惠使用了A-B-X模式，可能依赖于您在特定中转点放弃后续行程，并且可能涉及其他转机点，这可能违反航空公司的运输条款。</p>
<p>请注意以下法律风险：</p>
<ul>
  <li>航空公司可能取消您的回程或后续航段</li>
  <li>可能影响您的常旅客积分和会员状态</li>
  <li>在某些情况下，航空公司可能要求补缴票价差额</li>
  <li>可能违反航空公司运输条款，导致法律纠纷</li>
  <li>A-B-X模式复杂度更高，可能导致行程中的不确定性增加</li>
</ul>
<p>预订此航班即表示您已完全了解并自愿接受相关风险。AeroScout不对因使用此模式导致的任何损失负责。</p>
"""

# 隐私政策内容
PRIVACY_POLICY_CONTENT = """
<h2>1. 引言</h2>
<p>欢迎访问 AeroScout（以下简称"我们"或"本网站"）。我们致力于保护您的个人信息和隐私权。本隐私政策旨在向您说明，当您访问我们的网站或使用我们的服务时，我们如何收集、使用、披露和保护您的信息。请仔细阅读本隐私政策。如果您不同意本隐私政策的条款，请不要访问本网站。</p>

<h2>2. 我们收集的信息类型</h2>
<p>我们可能收集有关您的各种信息，包括：</p>
<ul>
  <li><strong>个人身份信息 (PII)：</strong>例如您的姓名、电子邮件地址、电话号码、邮寄地址等，这些信息是您在注册账户、订阅我们的通讯、参与调查或联系我们时自愿提供给我们的。</li>
  <li><strong>非个人身份信息：</strong>例如您的浏览器类型、操作系统、IP 地址、访问时间、引荐网站的 URL 以及您在本网站上查看的页面等。这些信息通常通过 Cookie 和其他跟踪技术自动收集。</li>
</ul>

<h2>3. 我们如何收集信息</h2>
<p>我们通过以下方式收集您的信息：</p>
<ul>
  <li><strong>用户提供：</strong>当您创建账户、填写表格、进行购买、与我们沟通或以其他方式直接向我们提供信息时。</li>
  <li><strong>自动收集：</strong>当您访问和浏览本网站时，我们可能会使用 Cookie、网络信标、跟踪像素和其他跟踪技术自动收集某些信息。</li>
</ul>
"""

# 服务条款内容
TERMS_OF_SERVICE_CONTENT = """
<h2>1. 接受条款</h2>
<p>欢迎使用 AeroScout（以下简称"本服务"）。访问或使用本服务即表示您同意遵守这些服务条款（以下简称"条款"）。如果您不同意这些条款的任何部分，则不得访问本服务。</p>

<h2>2. 服务描述</h2>
<p>AeroScout 提供航班信息查询和相关服务。本网站目前为演示项目，提供的航班信息、价格等仅供参考，不保证其绝对准确性、完整性或实时性。所有预订决策和行为均由用户自行负责。</p>

<h2>3. 用户责任与行为准则</h2>
<p>您同意对您在本服务上的所有活动负全部责任。您同意遵守所有适用的地方、州、国家和国际法律法规。您同意不：</p>
<ul>
  <li>以任何非法方式使用本服务；</li>
  <li>干扰或破坏本服务或与本服务连接的服务器或网络；</li>
  <li>试图未经授权访问本服务、其他帐户、计算机系统或连接到本服务的网络；</li>
  <li>收集或存储其他用户的个人数据。</li>
</ul>

<h2>4. 免责声明</h2>
<p>本服务按"原样"和"可用"的基础提供。AeroScout 不作任何明示或暗示的陈述或保证，包括但不限于对适销性、特定用途适用性和不侵权的暗示保证。AeroScout 不保证本服务将不间断、安全或无错误，也不保证缺陷将得到纠正。您明确同意自行承担使用本服务的风险。</p>
"""

# 初始化函数：将法律文本导入数据库
async def import_legal_texts():
    """
    导入初始法律文本到数据库
    """
    print("正在连接数据库...")
    await connect_db()
    
    try:
        print("开始导入法律文本...")
        
        # 导入通用免责声明
        print("导入通用免责声明...")
        await legal_crud.create_legal_text(
            text_type="disclaimer",
            content=DISCLAIMER_CONTENT,
            version="1.0",
            language="zh-CN",
            is_active=True
        )
        
        # 导入A-B模式风险确认文本
        print("导入A-B模式风险确认文本...")
        await legal_crud.create_legal_text(
            text_type="risk_confirmation",
            subtype="a-b",
            content=AB_RISK_CONTENT,
            version="1.0",
            language="zh-CN",
            is_active=True
        )
        
        # 导入A-B-X模式风险确认文本
        print("导入A-B-X模式风险确认文本...")
        await legal_crud.create_legal_text(
            text_type="risk_confirmation",
            subtype="a-b-x",
            content=ABX_RISK_CONTENT,
            version="1.0",
            language="zh-CN",
            is_active=True
        )
        
        # 导入隐私政策
        print("导入隐私政策...")
        await legal_crud.create_legal_text(
            text_type="privacy_policy",
            content=PRIVACY_POLICY_CONTENT,
            version="1.0",
            language="zh-CN",
            is_active=True
        )
        
        # 导入服务条款
        print("导入服务条款...")
        await legal_crud.create_legal_text(
            text_type="terms_of_service",
            content=TERMS_OF_SERVICE_CONTENT,
            version="1.0",
            language="zh-CN",
            is_active=True
        )
        
        print("法律文本导入完成！")
    
    except Exception as e:
        print(f"导入法律文本时出错: {e}")
    
    finally:
        print("断开数据库连接...")
        await disconnect_db()

# 入口点
if __name__ == "__main__":
    asyncio.run(import_legal_texts())