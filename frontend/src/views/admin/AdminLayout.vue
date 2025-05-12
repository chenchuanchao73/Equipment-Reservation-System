<template>
  <div class="admin-layout">
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

            <el-menu-item index="/admin/settings">
              <i class="el-icon-setting"></i>
              <span>系统设置</span>
            </el-menu-item>
          </el-menu>
        </div>

        <div class="header-right">
          <div class="user-info">
            <i class="el-icon-user"></i>
            <span>{{ displayUsername }}</span>
          </div>
          <el-button type="primary" plain icon="el-icon-s-home" size="small" @click="handleCommand('home')">返回首页</el-button>
          <el-button type="danger" plain icon="el-icon-switch-button" size="small" @click="handleCommand('logout')">退出登录</el-button>
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

export default {
  name: 'AdminLayout',

  data() {
    return {}
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
    justify-content: flex-start;
  }

  .top-menu .el-menu-item span,
  .top-menu .el-submenu__title span {
    display: none;
  }

  .user-info span {
    display: none;
  }
}
</style>
