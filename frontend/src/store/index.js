import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

// 系统支持的语言列表
const SUPPORTED_LANGUAGES = ['zh-CN', 'en']

// 检测浏览器语言并匹配系统支持的语言
const detectBrowserLanguage = () => {
  // 获取浏览器语言
  let browserLang = navigator.language || navigator.userLanguage || 'zh-CN'
  console.log('Detected browser language:', browserLang)

  // 将浏览器语言转换为系统支持的语言格式
  // 例如：zh-CN, zh, en-US, en 等
  browserLang = browserLang.toLowerCase()

  // 精确匹配
  if (SUPPORTED_LANGUAGES.includes(browserLang)) {
    console.log('Exact language match found:', browserLang)
    return browserLang
  }

  // 部分匹配（例如：zh-TW -> zh-CN, en-GB -> en）
  const langPrefix = browserLang.split('-')[0]
  for (const lang of SUPPORTED_LANGUAGES) {
    if (lang.toLowerCase().startsWith(langPrefix)) {
      console.log('Partial language match found:', browserLang, '->', lang)
      return lang
    }
  }

  // 如果没有匹配，检查localStorage中是否有保存的语言设置
  const savedLanguage = localStorage.getItem('language')
  if (savedLanguage && SUPPORTED_LANGUAGES.includes(savedLanguage)) {
    console.log('Using saved language preference:', savedLanguage)
    return savedLanguage
  }

  // 默认返回中文
  console.log('No language match found, using default:', 'zh-CN')
  return 'zh-CN'
}

export default new Vuex.Store({
  state: {
    // 用户状态
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || '{}'),

    // 设备数据
    equipments: [],
    equipmentTotal: 0,
    equipmentCategories: [],

    // 预定数据
    reservations: [],
    reservationTotal: 0,

    // 系统设置
    settings: {},

    // 加载状态
    loading: false,

    // 语言设置
    language: detectBrowserLanguage(),

    // 主题设置
    darkMode: localStorage.getItem('darkMode') === 'true' || false
  },

  getters: {
    // 用户状态
    isLoggedIn: state => !!state.token,
    currentUser: state => state.user,
    isAdmin: state => state.user && state.user.role === 'admin',
    isSuperAdmin: state => state.user && state.user.role === 'superadmin',

    // 设备数据
    getEquipments: state => state.equipments,
    getEquipmentTotal: state => state.equipmentTotal,
    getEquipmentCategories: state => state.equipmentCategories,

    // 预定数据
    getReservations: state => state.reservations,
    getReservationTotal: state => state.reservationTotal,

    // 系统设置
    getSettings: state => state.settings,

    // 加载状态
    isLoading: state => state.loading,

    // 语言设置
    getLanguage: state => state.language,

    // 主题设置
    isDarkMode: state => state.darkMode
  },

  mutations: {
    // 用户状态
    SET_TOKEN(state, token) {
      state.token = token
    },
    SET_USER(state, user) {
      state.user = user
    },
    CLEAR_AUTH(state) {
      state.token = ''
      state.user = {}
    },

    // 设备数据
    SET_EQUIPMENTS(state, { items, total }) {
      state.equipments = items
      state.equipmentTotal = total
    },
    SET_EQUIPMENT_CATEGORIES(state, categories) {
      state.equipmentCategories = categories
    },

    // 预定数据
    SET_RESERVATIONS(state, { items, total }) {
      state.reservations = items
      state.reservationTotal = total
    },

    // 系统设置
    SET_SETTINGS(state, settings) {
      state.settings = settings
    },

    // 加载状态
    SET_LOADING(state, isLoading) {
      state.loading = isLoading
    },

    // 语言设置
    SET_LANGUAGE(state, language) {
      state.language = language
      localStorage.setItem('language', language)
    },

    // 主题设置
    SET_DARK_MODE(state, darkMode) {
      state.darkMode = darkMode
    }
  },

  actions: {
    // 用户登录
    async login({ commit }, credentials) {
      try {
        commit('SET_LOADING', true)

        // 创建表单数据 - 使用URLSearchParams格式，这是OAuth2PasswordRequestForm所需的格式
        const formData = new URLSearchParams()
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)

        // 添加调试日志
        console.log('Sending login request to:', axios.defaults.baseURL + '/api/admin/login')
        console.log('Login credentials:', { username: credentials.username, password: '******' })

        // 发送登录请求，并指定更长的超时时间
        const response = await axios.post('/api/admin/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          timeout: 30000 // 30秒超时
        })

        // 保存令牌和用户信息
        const token = response.data.access_token
        const user = {
          id: response.data.admin_id,
          username: response.data.username,
          name: response.data.name,
          role: response.data.role
        }

        // 更新状态
        commit('SET_TOKEN', token)
        commit('SET_USER', user)

        // 保存到本地存储
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        return true
      } catch (error) {
        console.error('Login error:', error)

        // 详细的错误日志
        if (error.response) {
          // 服务器响应了，但状态码表示错误
          console.error('Error response:', {
            status: error.response.status,
            data: error.response.data,
            headers: error.response.headers
          })
        } else if (error.request) {
          // 请求已发送，但没有收到响应
          console.error('No response received:', error.request)
          console.log('Is backend server running at', axios.defaults.baseURL, '?')
        } else {
          // 设置请求时发生错误
          console.error('Request error:', error.message)
        }

        return false
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 用户登出
    logout({ commit }) {
      // 清除状态
      commit('CLEAR_AUTH')

      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    // 获取设备列表
    async fetchEquipments({ commit }, { page = 1, limit = 10, category = null, status = null, search = null }) {
      try {
        commit('SET_LOADING', true)

        // 构建查询参数
        const params = {
          skip: (page - 1) * limit,
          limit,
          category,
          status,
          search
        }

        // 发送请求
        const response = await axios.get('/api/equipment', { params })

        // 更新状态
        commit('SET_EQUIPMENTS', response.data)

        return response.data
      } catch (error) {
        console.error('Fetch equipments error:', error)
        return { items: [], total: 0 }
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 获取设备类别
    async fetchEquipmentCategories({ commit }) {
      try {
        commit('SET_LOADING', true)

        // 发送请求
        const response = await axios.get('/api/equipment/categories')

        // 更新状态
        commit('SET_EQUIPMENT_CATEGORIES', response.data.categories)

        return response.data.categories
      } catch (error) {
        console.error('Fetch equipment categories error:', error)
        return []
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 获取预定列表
    async fetchReservations({ commit }, { page = 1, limit = 10, equipmentId = null, userName = null, status = null, fromDate = null, toDate = null }) {
      try {
        commit('SET_LOADING', true)

        // 构建查询参数
        const params = {
          skip: (page - 1) * limit,
          limit,
          equipment_id: equipmentId,
          user_name: userName,
          status,
          from_date: fromDate,
          to_date: toDate
        }

        // 发送请求
        const response = await axios.get('/api/reservation', { params })

        // 更新状态
        commit('SET_RESERVATIONS', response.data)

        return response.data
      } catch (error) {
        console.error('Fetch reservations error:', error)
        return { items: [], total: 0 }
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 获取系统设置
    async fetchSettings({ commit }) {
      try {
        commit('SET_LOADING', true)

        // 发送请求
        const response = await axios.get('/api/admin/settings')

        // 更新状态
        commit('SET_SETTINGS', response.data)

        return response.data
      } catch (error) {
        console.error('Fetch settings error:', error)
        return {}
      } finally {
        commit('SET_LOADING', false)
      }
    },

    // 设置语言
    setLanguage({ commit }, language) {
      console.log('Setting language to:', language)
      commit('SET_LANGUAGE', language)
    },

    // 切换暗色/亮色主题
    toggleDarkMode({ commit, state }) {
      const newDarkMode = !state.darkMode
      commit('SET_DARK_MODE', newDarkMode)
      localStorage.setItem('darkMode', newDarkMode)
      return newDarkMode
    }
  },

  modules: {
    // 可以在这里添加模块
  }
})
