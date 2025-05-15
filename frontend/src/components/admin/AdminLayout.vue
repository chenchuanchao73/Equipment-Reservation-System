<template>
  <div class="admin-layout">
    <!-- 移动端菜单按钮，放在最外层，避免被父容器裁剪，仅在移动端显示 -->
    <div class="admin-mobile-nav-toggle" @click="toggleSidebar"></div>
    <el-container>
      <el-aside width="220px" class="admin-sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-header">
          <img src="@/assets/logo.png" alt="Logo" class="sidebar-logo" />
          <span class="sidebar-title">{{ $t('admin.adminPanel') }}</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/admin/dashboard">
            <i class="el-icon-s-home"></i>
            <span>{{ $t('admin.dashboard') }}</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/equipment">
            <i class="el-icon-s-grid"></i>
            <span>{{ $t('admin.equipment') }}</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/reservation">
            <i class="el-icon-s-order"></i>
            <span>{{ $t('admin.reservation') }}</span>
          </el-menu-item>
          
          <el-menu-item index="/admin/settings">
            <i class="el-icon-setting"></i>
            <span>{{ $t('admin.settings') }}</span>
          </el-menu-item>
        </el-menu>
        
        <div class="sidebar-footer">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              <i class="el-icon-user"></i>
              <span>{{ currentUser.name || currentUser.username }}</span>
              <i class="el-icon-arrow-down el-icon--right"></i>
            </span>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="home">
                <i class="el-icon-s-home"></i> {{ $t('nav.home') }}
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <i class="el-icon-switch-button"></i> {{ $t('nav.logout') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </el-dropdown>
        </div>
      </el-aside>
      
      <el-container>
        <el-header class="admin-header">
          <div class="header-left">
            <i
              class="el-icon-s-fold toggle-sidebar"
              @click="toggleSidebar"
            ></i>
            <slot name="header"></slot>
          </div>
          
          <div class="header-right">
            <el-dropdown trigger="click" @command="handleLanguageChange">
              <span class="language-dropdown">
                {{ currentLanguage === 'zh-CN' ? '中文' : 'English' }}
                <i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="zh-CN">中文</el-dropdown-item>
                <el-dropdown-item command="en">English</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </el-header>
        
        <el-main class="admin-main">
          <slot></slot>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'AdminLayout',
  
  data() {
    return {
      sidebarCollapsed: false
    }
  },
  
  computed: {
    ...mapGetters(['currentUser', 'getLanguage']),
    
    activeMenu() {
      return this.$route.path
    },
    
    currentLanguage() {
      return this.getLanguage
    }
  },
  
  methods: {
    ...mapActions(['logout', 'setLanguage']),
    
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    
    handleCommand(command) {
      if (command === 'logout') {
        this.handleLogout()
      } else if (command === 'home') {
        this.$router.push('/')
      }
    },
    
    handleLogout() {
      this.logout()
      this.$message.success(this.$t('admin.logoutSuccess'))
      this.$router.push('/admin/login')
    },
    
    handleLanguageChange(lang) {
      this.setLanguage(lang)
      this.$i18n.locale = lang
    }
  }
}
</script>

<style>
.admin-layout {
  height: 100vh;
  overflow: hidden;
}

.admin-sidebar {
  background-color: #304156;
  color: #bfcbd9;
  height: 100%;
  overflow-y: auto;
  transition: width 0.3s;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 15px;
  border-bottom: 1px solid #1f2d3d;
}

.sidebar-logo {
  height: 32px;
  margin-right: 10px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: bold;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #1f2d3d;
  position: absolute;
  bottom: 0;
  width: 100%;
  box-sizing: border-box;
}

.user-dropdown {
  display: flex;
  align-items: center;
  color: #bfcbd9;
  cursor: pointer;
}

.user-dropdown i {
  margin-right: 5px;
}

.admin-header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar {
  font-size: 20px;
  margin-right: 20px;
  cursor: pointer;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.language-dropdown {
  color: #606266;
  cursor: pointer;
}

.admin-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 64px !important;
  }
  
  .sidebar-title {
    display: none;
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
    z-index: 3000;
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
