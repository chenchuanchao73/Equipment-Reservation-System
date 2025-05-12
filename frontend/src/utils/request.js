import axios from 'axios'
import store from '@/store'
import router from '@/router'
import { Message } from 'element-ui'

// 创建axios实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_URL || '',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('Response error:', error)

    if (error.response) {
      const { status, data } = error.response

      // 处理不同的错误状态码
      switch (status) {
        case 400:
          Message.error(data.detail || '请求参数错误')
          break
        case 401:
          Message.warning('您的会话已过期，请重新登录')
          store.dispatch('logout')
          router.push('/admin/login')
          break
        case 403:
          Message.error('没有权限访问该资源')
          break
        case 404:
          Message.error('请求的资源不存在')
          break
        case 500:
          Message.error('服务器内部错误')
          break
        default:
          Message.error(`请求失败: ${error.message}`)
      }
    } else {
      Message.error('网络错误，请检查您的网络连接')
    }

    return Promise.reject(error)
  }
)

export default service
