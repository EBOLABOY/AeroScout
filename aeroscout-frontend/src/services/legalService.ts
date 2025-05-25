import apiClient from '../lib/apiService';

// 定义法律文本类型
export enum LegalTextType {
  DISCLAIMER = 'disclaimer',
  RISK_CONFIRMATION = 'risk_confirmation',
  PRIVACY_POLICY = 'privacy_policy',
  TERMS_OF_SERVICE = 'terms_of_service'
}

// 定义探测策略子类型
export enum ProbeStrategySubtype {
  A_B = 'a-b',
  A_B_X = 'a-b-x'
}

// 法律文本接口
export interface LegalText {
  id: number;
  type: string;
  subtype: string | null;
  content: string | null;
  version: string;
  is_active: boolean;
  language: string;
  content_path: string | null;
  created_at: string;
  updated_at: string;
}

// 缓存接口
interface LegalTextCache {
  [key: string]: {
    text: LegalText;
    timestamp: number;
  };
}

/**
 * 法律文本服务类
 * 负责从API获取法律文本，管理缓存，根据探测策略获取对应的风险确认文本
 */
export class LegalService {
  private static instance: LegalService;
  private cache: LegalTextCache = {};
  private readonly CACHE_EXPIRATION = 24 * 60 * 60 * 1000; // 24小时缓存有效期（毫秒）
  private readonly DEFAULT_LANGUAGE = 'zh-CN';
  
  // 备用文本，当API请求失败时使用
  private fallbackTexts = {
    [LegalTextType.DISCLAIMER]: `
      <p>欢迎使用 AeroScout！在您继续之前，请仔细阅读以下重要声明。</p>
      <p>本应用提供的所有信息，包括但不限于航班信息、价格、"多段组合推荐"及其他相关内容，均仅供一般参考之用，不构成任何形式的专业建议（例如旅行、财务或法律建议）。</p>
      <p>所有信息均基于第三方数据源。我们尽力确保所提供信息的准确性和及时性，但不对其完整性、准确性、可靠性、适用性或可用性作任何明示或暗示的保证或陈述。</p>
      <p>您理解并同意，您对本应用所提供信息的任何依赖和使用均由您自行承担风险。</p>
      <p>在任何情况下，对于因使用或依赖本应用信息而直接或间接导致的任何性质的损失或损害（包括但不限于数据丢失或利润损失），AeroScout 及其关联方均不承担任何责任。我们强烈建议您在做出任何旅行决策或采取任何行动前，通过官方渠道（如航空公司、机场官方网站或授权代理）对所有信息进行独立核实。</p>
    `,
    [LegalTextType.RISK_CONFIRMATION + "_" + ProbeStrategySubtype.A_B]: `
      <p>此优惠可能依赖于您在特定中转点放弃后续行程（俗称"跳机"），这可能违反航空公司的运输条款。</p>
      <p>请注意以下法律风险：</p>
      <ul>
        <li>航空公司可能取消您的回程或后续航段</li>
        <li>可能影响您的常旅客积分和会员状态</li>
        <li>在某些情况下，航空公司可能要求补缴票价差额</li>
        <li>可能违反航空公司运输条款，导致法律纠纷</li>
      </ul>
      <p>预订此航班即表示您已完全了解并自愿接受相关风险。AeroScout不对因"跳机"行为导致的任何损失负责。</p>
    `,
    [LegalTextType.RISK_CONFIRMATION + "_" + ProbeStrategySubtype.A_B_X]: `
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
    `
  };

  private constructor() {}

  /**
   * 获取LegalService单例
   */
  public static getInstance(): LegalService {
    if (!LegalService.instance) {
      LegalService.instance = new LegalService();
    }
    return LegalService.instance;
  }

  /**
   * 从API获取法律文本
   * @param type 文本类型
   * @param subtype 子类型(可选)
   * @param version 版本号(可选)
   * @param language 语言代码(可选)
   * @returns 法律文本
   */
  public async getLegalText(
    type: LegalTextType,
    subtype?: string,
    version?: string,
    language: string = this.DEFAULT_LANGUAGE
  ): Promise<string> {
    try {
      // 构建缓存键
      const cacheKey = this.buildCacheKey(type, subtype, version, language);
      
      // 检查缓存
      const cachedText = this.getFromCache(cacheKey);
      if (cachedText) {
        return cachedText.content || this.getFallbackText(type, subtype);
      }
      
      // 构建API请求参数
      const params: Record<string, string> = {
        type,
        language
      };
      
      if (subtype) params.subtype = subtype;
      if (version) params.version = version;
      
      // 发送API请求
      const response = await apiClient.get<LegalText>('/legal/content', { params });
      
      // 将结果存入缓存
      this.saveToCache(cacheKey, response.data);
      
      return response.data.content || this.getFallbackText(type, subtype);
    } catch (error) {
      console.error(`获取法律文本失败: ${error}`);
      // 返回后备文本
      return this.getFallbackText(type, subtype);
    }
  }

  /**
   * 根据探测策略获取风险确认文本
   * @param probeStrategy 探测策略子类型 ('a-b' | 'a-b-x')
   * @param language 语言代码(可选)
   * @returns 风险确认文本
   */
  public async getRiskConfirmationText(
    probeStrategy: ProbeStrategySubtype,
    language: string = this.DEFAULT_LANGUAGE
  ): Promise<string> {
    return this.getLegalText(LegalTextType.RISK_CONFIRMATION, probeStrategy, undefined, language);
  }
  
  /**
   * 获取免责声明文本
   * @param language 语言代码(可选)
   * @returns 免责声明文本
   */
  public async getDisclaimerText(language: string = this.DEFAULT_LANGUAGE): Promise<string> {
    return this.getLegalText(LegalTextType.DISCLAIMER, undefined, undefined, language);
  }
  
  /**
   * 获取隐私政策文本
   * @param language 语言代码(可选)
   * @returns 隐私政策文本
   */
  public async getPrivacyPolicyText(language: string = this.DEFAULT_LANGUAGE): Promise<string> {
    return this.getLegalText(LegalTextType.PRIVACY_POLICY, undefined, undefined, language);
  }
  
  /**
   * 获取服务条款文本
   * @param language 语言代码(可选)
   * @returns 服务条款文本
   */
  public async getTermsOfServiceText(language: string = this.DEFAULT_LANGUAGE): Promise<string> {
    return this.getLegalText(LegalTextType.TERMS_OF_SERVICE, undefined, undefined, language);
  }
  
  /**
   * 清除缓存
   */
  public clearCache(): void {
    this.cache = {};
  }

  /**
   * 从缓存中获取文本
   * @param cacheKey 缓存键
   * @returns 法律文本或null
   */
  private getFromCache(cacheKey: string): LegalText | null {
    const now = Date.now();
    const cachedItem = this.cache[cacheKey];
    
    if (cachedItem && now - cachedItem.timestamp < this.CACHE_EXPIRATION) {
      return cachedItem.text;
    }
    
    // 如果缓存过期，删除缓存项
    if (cachedItem) {
      delete this.cache[cacheKey];
    }
    
    return null;
  }

  /**
   * 将文本保存到缓存
   * @param cacheKey 缓存键
   * @param text 法律文本
   */
  private saveToCache(cacheKey: string, text: LegalText): void {
    this.cache[cacheKey] = {
      text,
      timestamp: Date.now()
    };
  }

  /**
   * 构建缓存键
   * @param type 文本类型
   * @param subtype 子类型(可选)
   * @param version 版本号(可选)
   * @param language 语言代码
   * @returns 缓存键
   */
  private buildCacheKey(
    type: string,
    subtype?: string,
    version?: string,
    language: string = this.DEFAULT_LANGUAGE
  ): string {
    let key = `${type}_${language}`;
    if (subtype) key += `_${subtype}`;
    if (version) key += `_${version}`;
    return key;
  }

  /**
   * 获取后备文本
   * @param type 文本类型
   * @param subtype 子类型(可选)
   * @returns 后备文本
   */
  private getFallbackText(type: string, subtype?: string): string {
    if (type === LegalTextType.RISK_CONFIRMATION && subtype) {
      return this.fallbackTexts[`${type}_${subtype}`] || '';
    }
    return this.fallbackTexts[type] || '';
  }
}

// 导出单例实例
export const legalService = LegalService.getInstance();