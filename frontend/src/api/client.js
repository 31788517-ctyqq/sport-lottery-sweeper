import axios from 'axios'
import apiClient from './index'

// 创建多个axios实例用于不同场景
const publicClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const uploadClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 60000,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

const downloadClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 60000,
  responseType: 'blob'
})

// 默认客户端（已配置拦截器）
const defaultClient = apiClient

// 导出所有客户端
export {
  defaultClient as default,
  publicClient,
  uploadClient,
  downloadClient
}

// 请求方法封装
export const request = {
  // GET请求
  get(url, config = {}) {
    return defaultClient.get(url, config)
  },
  
  // POST请求
  post(url, data, config = {}) {
    return defaultClient.post(url, data, config)
  },
  
  // PUT请求
  put(url, data, config = {}) {
    return defaultClient.put(url, data, config)
  },
  
  // PATCH请求
  patch(url, data, config = {}) {
    return defaultClient.patch(url, data, config)
  },
  
  // DELETE请求
  delete(url, config = {}) {
    return defaultClient.delete(url, config)
  },
  
  // 上传文件
  upload(url, file, config = {}) {
    const formData = new FormData()
    formData.append('file', file)
    
    return uploadClient.post(url, formData, {
      ...config,
      headers: {
        ...config.headers,
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 批量上传
  uploadMultiple(url, files, fieldName = 'files', config = {}) {
    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append(`${fieldName}[${index}]`, file)
    })
    
    return uploadClient.post(url, formData, {
      ...config,
      headers: {
        ...config.headers,
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 下载文件
  download(url, config = {}) {
    return downloadClient.get(url, config)
  },
  
  // 并发请求
  all(requests) {
    return axios.all(requests)
  },
  
  // 取消请求
  createCancelToken() {
    return axios.CancelToken.source()
  }
}

// 导出工具函数
export const createApiUrl = (endpoint, params = {}) => {
  let url = endpoint
  
  // 替换路径参数
  Object.keys(params).forEach(key => {
    if (url.includes(`:${key}`)) {
      url = url.replace(`:${key}`, params[key])
      delete params[key]
    }
  })
  
  // 添加查询参数
  const queryParams = new URLSearchParams()
  Object.keys(params).forEach(key => {
    if (params[key] !== undefined && params[key] !== null) {
      queryParams.append(key, params[key])
    }
  })
  
  const queryString = queryParams.toString()
  if (queryString) {
    url += `?${queryString}`
  }
  
  return url
}

// 请求状态管理
export const createRequestState = () => {
  return {
    loading: false,
    error: null,
    data: null
  }
}

// 请求状态更新器
export const updateRequestState = (state, promise) => {
  state.loading = true
  state.error = null
  
  return promise
    .then(response => {
      state.data = response
      state.loading = false
      return response
    })
    .catch(error => {
      state.error = error
      state.loading = false
      throw error
    })
}