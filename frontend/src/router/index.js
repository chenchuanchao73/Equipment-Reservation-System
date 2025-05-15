import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'

// 导入视图组件
import Home from '@/views/Home.vue'
import EquipmentList from '@/views/equipment/EquipmentList.vue'
import EquipmentDetail from '@/views/equipment/EquipmentDetail.vue'
import ReservationForm from '@/views/reservation/ReservationForm.vue'
import RecurringReservationForm from '@/views/reservation/RecurringReservationForm.vue'
import ReservationQuery from '@/views/reservation/ReservationQuery.vue'
import ReservationDetail from '@/views/reservation/ReservationDetail.vue'
import RecurringReservationDetail from '@/views/reservation/RecurringReservationDetail.vue'
import AdminLogin from '@/views/admin/AdminLogin.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import AdminEquipment from '@/views/admin/AdminEquipment.vue'
import AdminCategory from '@/views/admin/AdminCategory.vue'
import AdminReservation from '@/views/admin/AdminReservation.vue'
import AdminReservationDetail from '@/views/admin/AdminReservationDetail.vue'
import NotFound from '@/views/NotFound.vue'
import AnnouncementManage from '@/views/admin/AnnouncementManage.vue'
import AdminSettings from '@/views/admin/AdminSettings.vue'

Vue.use(VueRouter)

// 路由配置
const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: { title: '首页' }
  },
  {
    path: '/calendar',
    name: 'calendar',
    component: () => import('@/views/calendar/CalendarView.vue'),
    meta: { title: 'calendar.title' }
  },
  {
    path: '/equipment',
    name: 'equipment-list',
    component: EquipmentList,
    meta: { title: '设备列表' }
  },
  {
    path: '/equipment/:id',
    name: 'equipment-detail',
    component: EquipmentDetail,
    meta: { title: '设备详情' }
  },
  {
    path: '/equipment/:id/reserve',
    name: 'reservation-form',
    component: ReservationForm,
    meta: { title: '预定设备' }
  },
  {
    path: '/equipment/:id/recurring-reserve',
    name: 'recurring-reservation-form',
    component: RecurringReservationForm,
    meta: { title: '循环预约设备' }
  },
  {
    path: '/reservation/query',
    name: 'reservation-query',
    component: ReservationQuery,
    meta: { title: '查询预定' }
  },
  {
    path: '/reservation/number/:number',
    name: 'reservation-detail-by-number',
    component: ReservationDetail,
    meta: { title: '预定详情' }
  },
  {
    path: '/reservation/:code',
    name: 'reservation-detail',
    component: ReservationDetail,
    meta: { title: '预定详情' }
  },
  {
    path: '/recurring-reservation/:id',
    name: 'recurring-reservation-detail',
    component: RecurringReservationDetail,
    meta: { title: '循环预约详情' },
    // 添加props选项，确保组件能够接收到路由参数
    props: true
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: AdminLogin,
    meta: { title: '管理员登录' }
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { title: '管理控制台', requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: AdminDashboard,
        meta: { title: '控制台', requiresAuth: true }
      },
      {
        path: 'equipment',
        name: 'admin-equipment',
        component: AdminEquipment,
        meta: { title: '设备管理', requiresAuth: true }
      },
      {
        path: 'category',
        name: 'admin-category',
        component: AdminCategory,
        meta: { title: '设备类别管理', requiresAuth: true }
      },
      {
        path: 'reservation',
        name: 'admin-reservation',
        component: AdminReservation,
        meta: { title: '预定管理', requiresAuth: true }
      },
      {
        path: 'reservation/:code',
        name: 'admin-reservation-detail',
        component: AdminReservationDetail,
        meta: { title: '预定详情', requiresAuth: true }
      },
      {
        path: 'settings',
        name: 'admin-settings',
        component: AdminSettings,
        meta: { title: '系统管理', requiresAuth: true }
      },
      {
        path: 'announcement',
        name: 'admin-announcement',
        component: AnnouncementManage,
        meta: { title: '公告管理', requiresAuth: true }
      },
      {
        path: 'email',
        name: 'admin-email',
        component: () => import('@/views/admin/EmailLayout.vue'),
        meta: { title: '邮件管理', requiresAuth: true },
        children: [
          {
            path: '',
            redirect: 'settings'
          },
          {
            path: 'settings',
            name: 'admin-email-settings',
            component: () => import('@/views/admin/EmailSettings.vue'),
            meta: { title: '邮件设置', requiresAuth: true }
          },
          {
            path: 'templates',
            name: 'admin-email-templates',
            component: () => import('@/views/admin/EmailTemplates.vue'),
            meta: { title: '邮件模板', requiresAuth: true }
          },
          {
            path: 'logs',
            name: 'admin-email-logs',
            component: () => import('@/views/admin/EmailLogs.vue'),
            meta: { title: '邮件日志', requiresAuth: true }
          }
        ]
      },
      {
        path: 'db-viewer',
        name: 'admin-db-viewer',
        component: () => import('@/views/admin/DatabaseViewer.vue'),
        meta: { title: '数据库表查看', requiresAuth: true }
      }
    ]
  },
  {
    path: '*',
    name: 'not-found',
    component: NotFound,
    meta: { title: '页面未找到' }
  }
]

const router = new VueRouter({
  mode: 'hash',
  base: process.env.BASE_URL,
  routes
})

// 添加路由解析规则，确保循环预约详情页面能够正确显示
router.beforeEach((to, from, next) => {
  // 如果是循环预约详情页面，但路由名称不是recurring-reservation-detail
  if (to.path.startsWith('/recurring-reservation/') && to.name !== 'recurring-reservation-detail') {
    // 获取循环预约ID
    const id = to.path.split('/').pop()
    // 重定向到循环预约详情页面
    next({ name: 'recurring-reservation-detail', params: { id } })
  } else {
    next()
  }
})

// 注意: 路由守卫已移至 permission.js

export default router
