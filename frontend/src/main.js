import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import VueI18n from 'vue-i18n'
import axios from 'axios'
import enLocale from 'element-ui/lib/locale/lang/en'
import zhLocale from 'element-ui/lib/locale/lang/zh-CN'


// 导入权限控制
import './router/permission'

// 导入富文本编辑器
// 暂时注释掉富文本编辑器相关代码
// import VueQuillEditor from 'vue-quill-editor'
// import 'quill/dist/quill.core.css'
// import 'quill/dist/quill.snow.css'
// import 'quill/dist/quill.bubble.css'

// 导入语言包
import zhCN from './locales/zh-CN'
import en from './locales/en'

// 使用插件
Vue.use(VueI18n)
// Vue.use(VueQuillEditor) // 暂时注释掉

// 配置axios
axios.defaults.baseURL = process.env.VUE_APP_API_URL || 'http://localhost:8000'
// 增加超时时间到 30 秒
axios.defaults.timeout = 30000
// 添加调试日志
console.log('API Base URL:', axios.defaults.baseURL)
axios.interceptors.request.use(config => {
  // 从localStorage获取token
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

axios.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response) {
    // 处理401错误（会话过期）
    if (error.response.status === 401) {
      // 显示友好的提示信息
      Vue.prototype.$message({
        message: '您的会话已过期，请重新登录',
        type: 'warning',
        duration: 3000
      })

      store.dispatch('logout')
      // 避免重复导航到登录页
      if (router.currentRoute.path !== '/admin/login') {
        router.push('/admin/login')
      }
    }
  }
  return Promise.reject(error)
})

Vue.prototype.$http = axios

// 配置i18n
const i18n = new VueI18n({
  locale: store.state.language || 'zh-CN',
  messages: {
    'zh-CN': {
      ...zhCN,
      el: zhLocale.el
    },
    'en': {
      ...en,
      el: enLocale.el
    }
  },
  silentTranslationWarn: true
})

// 同步语言设置
store.watch(
  state => state.language,
  (newLang) => {
    i18n.locale = newLang
    document.querySelector('html').setAttribute('lang', newLang)
    console.log('Language changed to:', newLang)
  }
)

// 使用Element UI
Vue.use(ElementUI, {
  i18n: (key, value) => i18n.t(key, value)
})

// 导入日期工具函数
import { formatDate, convertToBeijingTime } from './utils/date'

// 全局过滤器
Vue.filter('dateFormat', function(value, format = 'YYYY-MM-DD HH:mm') {
  if (!value) return ''

  // 使用日期工具函数，自动转换为北京时间
  return formatDate(value, format, true)
})

Vue.config.productionTip = false

new Vue({
  router,
  store,
  i18n,
  render: h => h(App)
}).$mount('#app')
