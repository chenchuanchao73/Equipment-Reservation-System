<template>
  <div class="admin-layout">
    <!-- 移动端菜单按钮 -->
    <div class="admin-mobile-nav-toggle" @click="mobileMenuOpen = true"></div>
    <!-- 移动端抽屉菜单和遮罩层 -->
    <div v-if="mobileMenuOpen" class="admin-mobile-nav-overlay" @click="mobileMenuOpen = false"></div>
    <div v-if="mobileMenuOpen" class="admin-mobile-nav-drawer">
      <div class="admin-mobile-nav-header">
        <img src="@/assets/logo.png" alt="Logo" class="admin-mobile-nav-logo">
        <h3 class="admin-mobile-nav-title">管理控制台</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="admin-mobile-nav-list"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        @select="handleMobileMenuSelect"
      >
        <el-menu-item index="/admin/dashboard">
          <i class="el-icon-s-home"></i>
          <span>控制台</span>
        </el-menu-item>
        <el-submenu index="equipment">
          <template slot="title">
            <i class="el-icon-s-grid"></i>
            <span>设备管理</span>
          </template>
          <el-menu-item index="/admin/equipment">
            <i class="el-icon-s-management"></i>
            <span>设备列表</span>
          </el-menu-item>
          <el-menu-item index="/admin/category">
            <i class="el-icon-collection-tag"></i>
            <span>设备类别</span>
          </el-menu-item>
        </el-submenu>
        <el-menu-item index="/admin/reservation">
          <i class="el-icon-s-order"></i>
          <span>预定管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/announcement">
          <i class="el-icon-message-solid"></i>
          <span>公告管理</span>
        </el-menu-item>
        <el-submenu index="email-mobile">
          <template slot="title">
            <i class="el-icon-message"></i>
            <span>邮件管理</span>
          </template>
          <el-menu-item index="/admin/email/settings">
            <i class="el-icon-setting"></i>
            <span>邮件设置</span>
          </el-menu-item>
          <el-menu-item index="/admin/email/templates">
            <i class="el-icon-document"></i>
            <span>邮件模板</span>
          </el-menu-item>
          <el-menu-item index="/admin/email/logs">
            <i class="el-icon-tickets"></i>
            <span>邮件日志</span>
          </el-menu-item>
        </el-submenu>
        <el-menu-item index="/admin/db-viewer">
          <i class="el-icon-view"></i>
          <span>数据库表查看</span>
        </el-menu-item>
        <el-menu-item index="/admin/system-logs">
          <i class="el-icon-document"></i>
          <span>系统日志</span>
        </el-menu-item>
        <el-menu-item index="/admin/accounts">
          <i class="el-icon-user"></i>
          <span>账号管理</span>
        </el-menu-item>
      </el-menu>
      <div class="admin-mobile-nav-footer">
        <el-button type="primary" plain icon="el-icon-s-home" size="small" @click="handleCommand('home')">返回首页</el-button>
        <el-button type="danger" plain icon="el-icon-switch-button" size="small" @click="handleCommand('logout')">退出登录</el-button>
      </div>
    </div>
    <el-container class="admin-container">
      <el-header class="admin-header">
        <div class="header-left">
          <img src="@/assets/logo.png" alt="Logo" class="header-logo" />
          <span class="header-title">管理控制台</span>
        </div>

        <div class="header-menu">
          <el-menu
            :default-active="activeMenu"
            class="top-menu"
            mode="horizontal"
            background-color="#FFFFFF"
            text-color="#333333"
            active-text-color="#409EFF"
            router
          >
            <el-menu-item index="/admin/dashboard">
              <i class="el-icon-s-home"></i>
              <span>控制台</span>
            </el-menu-item>

            <el-submenu index="equipment">
              <template slot="title">
                <i class="el-icon-s-grid"></i>
                <span>设备管理</span>
              </template>
              <el-menu-item index="/admin/equipment">
                <i class="el-icon-s-management"></i>
                <span>设备列表</span>
              </el-menu-item>
              <el-menu-item index="/admin/category">
                <i class="el-icon-collection-tag"></i>
                <span>设备类别</span>
              </el-menu-item>
            </el-submenu>

            <el-menu-item index="/admin/reservation">
              <i class="el-icon-s-order"></i>
              <span>预定管理</span>
            </el-menu-item>

            <el-menu-item index="/admin/announcement">
              <i class="el-icon-message-solid"></i>
              <span>公告管理</span>
            </el-menu-item>

            <el-submenu index="email">
              <template slot="title">
                <i class="el-icon-message"></i>
                <span>邮件管理</span>
              </template>
              <el-menu-item index="/admin/email/settings">
                <i class="el-icon-setting"></i>
                <span>邮件设置</span>
              </el-menu-item>
              <el-menu-item index="/admin/email/templates">
                <i class="el-icon-document"></i>
                <span>邮件模板</span>
              </el-menu-item>
              <el-menu-item index="/admin/email/logs">
                <i class="el-icon-tickets"></i>
                <span>邮件日志</span>
              </el-menu-item>
            </el-submenu>

            <el-menu-item index="/admin/db-viewer">
              <i class="el-icon-view"></i>
              <span>数据库表查看</span>
            </el-menu-item>

            <el-menu-item index="/admin/system-logs">
              <i class="el-icon-document"></i>
              <span>系统日志</span>
            </el-menu-item>

            <el-menu-item index="/admin/accounts">
              <i class="el-icon-user"></i>
              <span>账号管理</span>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="header-right">
          <div class="user-info">
            <i class="el-icon-user"></i>
            <span>{{ displayUsername }}</span>
          </div>
          
          <el-button type="primary" plain icon="el-icon-s-home" size="small" @click="handleCommand('home')" class="home-btn">返回首页</el-button>
          <el-button type="danger" plain icon="el-icon-switch-button" size="small" @click="handleCommand('logout')" class="logout-btn">退出登录</el-button>
        </div>
      </el-header>

      <el-main class="admin-main">
        <keep-alive>
          <router-view></router-view>
        </keep-alive>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { updatePageTitle } from '@/router/permission'

export default {
  name: 'AdminLayout',

  data() {
    return {
      mobileMenuOpen: false
    }
  },

  computed: {
    ...mapGetters(['currentUser', 'getLanguage']),

    activeMenu() {
      return this.$route.path
    },

    currentLanguage() {
      return this.getLanguage
    },

    displayUsername() {
      // 优先显示用户名，如果没有则显示'管理员'
      return this.currentUser && this.currentUser.username ? this.currentUser.username : '管理员'
    },

    isSuperAdmin() {
      return this.currentUser && this.currentUser.role === 'superadmin'
    }
  },

  methods: {
    ...mapActions(['logout', 'setLanguage']),

    handleCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
      } else if (command === 'home') {
        this.$router.push('/')
      }
    },

    handleLogout() {
      this.logout()
      this.$message.success('退出登录成功')
      this.$router.push('/admin/login')
    },

    handleLanguageChange(lang) {
      this.setLanguage(lang)
      this.$i18n.locale = lang

      // 更新页面标题
      setTimeout(() => {
        updatePageTitle()
      }, 0)
    },

    handleMobileMenuSelect(key) {
      this.$router.push(key)
      this.mobileMenuOpen = false
    },

    toggleMobileMenu() {
      // 这里可以实现折叠菜单的逻辑，或 emit 事件给父组件
      const menu = document.querySelector('.header-menu')
      if (menu) {
        menu.style.display = (menu.style.display === 'none') ? '' : 'none'
      }
    }
  }
}
</script>

<style>
.admin-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  display: flex;
  margin: 0;
  padding: 0;
  position: absolute;
  top: 0;
  left: 0;
  box-sizing: border-box;
}

.admin-container {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.admin-header,
.el-header {
  background-color: #FFFFFF !important;
  color: #333333 !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  height: 60px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #EBEEF5;
}

.header-left {
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-logo {
  height: 32px;
  margin-right: 10px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
  white-space: nowrap;
}

.header-menu {
  flex: 1;
  display: flex;
  justify-content: center;
}

.top-menu {
  background-color: #FFFFFF !important;
  border-bottom: none;
}

.top-menu .el-menu-item {
  height: 60px;
  line-height: 60px;
}

.top-menu .el-submenu__title {
  height: 60px;
  line-height: 60px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 0 20px;
}

.language-switcher {
  display: flex;
  align-items: center;
  margin-right: 15px;
}

.lang-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px 8px;
  color: #606266;
  font-size: 14px;
}

.lang-btn.active {
  color: #409EFF;
  font-weight: bold;
}

.divider {
  color: #DCDFE6;
  margin: 0 5px;
  opacity: 0.7;
}

.user-info {
  display: flex;
  align-items: center;
  color: #606266;
  margin-right: 15px;
  background-color: #F5F7FA;
  padding: 5px 12px;
  border-radius: 4px;
  font-size: 14px;
  border: 1px solid #DCDFE6;
}

.user-info i {
  margin-right: 5px;
}

.header-right .el-button {
  margin-left: 0;
  white-space: nowrap;
}

.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
  width: 100%;
  max-width: 100%;
}

@media (max-width: 768px) {
  .header-title {
    display: none;
  }

  .header-menu {
    display: none; /* 完全隐藏菜单栏，因为已经集成到侧边悬浮按钮中 */
  }

  .header-right {
    flex: 1;
    justify-content: flex-end;
    padding-right: 10px; /* 减少右侧内边距，让按钮更靠左 */
  }

  .user-info {
    margin-right: 8px; /* 减少用户信息右侧间距 */
  }

  /* 移动端按钮样式优化 */
  .home-btn, .logout-btn {
    padding: 7px 10px;
    font-size: 12px;
  }

  .home-btn {
    margin-right: 5px;
  }

  .logout-btn {
    margin-right: 5px; /* 确保退出按钮不会超出屏幕 */
  }

  .admin-mobile-nav-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0,0,0,0.5);
    z-index: 2999;
  }
  .admin-mobile-nav-drawer {
    position: fixed;
    top: 0;
    right: 0;
    width: 260px;
    height: 100vh;
    background: #304156;
    z-index: 3000;
    display: flex;
    flex-direction: column;
    transition: right 0.3s ease;
    box-shadow: -2px 0 8px rgba(0,0,0,0.1);
  }
  .admin-mobile-nav-header {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background-color: #263445;
  }
  .admin-mobile-nav-logo {
    width: 32px;
    height: 32px;
    margin-right: 10px;
  }
  .admin-mobile-nav-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #fff;
  }
  .admin-mobile-nav-list {
    flex: 1;
    border-right: none;
    background: #304156;
  }
  .admin-mobile-nav-footer {
    padding: 15px 20px;
    background-color: #263445;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .mobile-language-buttons {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
  }

  .mobile-lang-btn {
    flex: 1;
    background: #304156;
    border: 1px solid #1f2d3d;
    color: #bfcbd9;
    padding: 8px 0;
    cursor: pointer;
    font-size: 14px;
  }

  .mobile-lang-btn.active {
    background: #1f2d3d;
    color: #409EFF;
    font-weight: bold;
  }
  .admin-mobile-nav-toggle {
    position: fixed;
    top: 50%;
    right: 0;
    left: auto;
    transform: translateY(-50%);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #409EFF;
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    z-index: 3001;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
  .admin-mobile-nav-toggle:before {
    content: '';
    display: block;
    width: 24px;
    height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg fill="white" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg"><path d="M160 512a32 32 0 0 1 32-32h640a32 32 0 0 1 0 64H192a32 32 0 0 1-32-32zm0-192a32 32 0 0 1 32-32h640a32 32 0 0 1 0 64H192a32 32 0 0 1-32-32zm32 288a32 32 0 0 0 0 64h640a32 32 0 0 0 0-64H192z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
    margin: auto;
  }
}
</style>
