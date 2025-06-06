import router from './index'
import store from '@/store'
import { Message } from 'element-ui'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 配置NProgress
NProgress.configure({ showSpinner: false })

// 白名单路由（不需要登录即可访问）
const whiteList = [
  '/',
  '/equipment',
  '/equipment/:id',
  '/reservation/query',
  '/reservation/:code',
  '/admin/login',
  '/404'
]

// 更新页面标题的函数
export const updatePageTitle = () => {
  // 获取当前路由
  const currentRoute = router.currentRoute
  if (!currentRoute) return

  let pageTitle = currentRoute.meta.title || ''
  let appName = 'HTNIA设备预定系统' // 默认值

  // 如果标题是i18n键值（包含点号），则使用i18n进行翻译
  if (pageTitle && pageTitle.includes('.')) {
    try {
      const i18nTitle = router.app.$i18n.t(pageTitle)
      if (i18nTitle !== pageTitle) { // 如果翻译成功（结果不等于原键值）
        pageTitle = i18nTitle
      }
    } catch (e) {
      console.error('Failed to translate page title:', e)
    }
  }

  // 尝试获取国际化的应用名称
  try {
    if (router.app && router.app.$i18n) {
      appName = router.app.$i18n.t('common.fullAppName')
    }
  } catch (e) {
    console.error('Failed to translate app name:', e)
  }

  document.title = pageTitle ? `${pageTitle} - ${appName}` : appName
}

// 路由前置守卫
router.beforeEach((to, from, next) => {
  // 开始进度条
  NProgress.start()

  // 获取用户登录状态
  const hasToken = store.getters.isLoggedIn

  // 判断是否需要登录权限
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  // 如果是登录页面且已登录，直接跳转到首页
  if (to.path === '/admin/login' && hasToken) {
    next('/admin/dashboard')
    NProgress.done()
    return
  }

  // 如果需要登录权限但未登录，跳转到登录页
  if (requiresAuth && !hasToken) {
    // 如果已经在登录页，直接放行，避免死循环
    if (to.path === '/admin/login') {
      next()
      NProgress.done()
      return
    }
    next(`/admin/login?redirect=${to.path}`)
    NProgress.done()
    return
  }

  // 其他情况直接放行
  next()
})

// 路由后置守卫
router.afterEach(() => {
  // 结束进度条
  NProgress.done()

  // 设置页面标题 - 在路由完成后设置，确保i18n已初始化
  setTimeout(() => {
    updatePageTitle()
  }, 0)
})

export default router
