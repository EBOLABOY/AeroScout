interface ApiError {
  response?: {
    status: number;
    data?: {
      detail?: string | { msg: string }[]; // FastAPI validation errors might be an array of objects
      message?: string; // General error message
    };
  };
  message?: string; // For network errors or other non-HTTP errors
  request?: unknown; // For errors where the request was made but no response was received
}

export const getFriendlyErrorMessage = (error: ApiError): string => {
  if (error.response) {
    const { status, data } = error.response;
    let detailMessage = '';

    if (data?.detail) {
      if (typeof data.detail === 'string') {
        detailMessage = data.detail;
      } else if (Array.isArray(data.detail) && data.detail.length > 0) {
        // Handle FastAPI validation errors which are often arrays of objects
        detailMessage = data.detail.map(d => d.msg || JSON.stringify(d)).join(', ');
      }
    } else if (data?.message) {
      detailMessage = data.message;
    }


    switch (status) {
      case 400:
        return `请求无效。${detailMessage ? `详情: ${detailMessage}` : '请检查您的输入。'}`;
      case 401:
        return '身份验证失败，请重新登录。';
      case 403:
        return '您没有权限执行此操作。';
      case 404:
        return `请求的资源未找到。${detailMessage ? `详情: ${detailMessage}` : ''}`;
      case 422:
        return `请求数据验证失败。${detailMessage ? `详情: ${detailMessage}` : '请检查您提交的内容。'}`;
      case 429:
        return '请求过于频繁，请稍后再试。';
      case 500:
      case 501:
      case 502:
      case 503:
      case 504:
        return `服务器发生错误，请稍后再试。(${status}${detailMessage ? ` - ${detailMessage}` : ''})`;
      default:
        return `发生未知错误 (HTTP ${status})。${detailMessage ? `详情: ${detailMessage}` : ''}`;
    }
  } else if (error.request) {
    // The request was made but no response was received
    return '无法连接到服务器，请检查您的网络连接。';
  } else if (error.message) {
    // Something happened in setting up the request that triggered an Error
    // or a generic JavaScript error
    if (error.message.toLowerCase().includes('network error') || error.message.toLowerCase().includes('failed to fetch')) {
      return '网络连接错误，请检查您的网络并重试。';
    }
    return `发生错误：${error.message}`;
  }
  return '发生未知错误，请稍后再试。';
};