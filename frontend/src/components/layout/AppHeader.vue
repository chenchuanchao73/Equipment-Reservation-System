<template>
  <div>
    <!-- 桌面端导航 -->
    <div class="app-header desktop-nav">
      <el-menu
        :default-active="activeIndex"
        class="el-menu-demo"
        mode="horizontal"
        router
        background-color="#FFFFFF"
        text-color="#333333"
        active-text-color="#409EFF"
      >
        <!-- 移除Logo和标题 -->

        <el-menu-item index="/">
          <i class="el-icon-s-home"></i>
          <span>{{ $t('nav.home') }}</span>
        </el-menu-item>
        <el-menu-item index="/calendar">
          <i class="el-icon-date"></i>
          <span>{{ $t('nav.calendar') }}</span>
        </el-menu-item>
        <el-menu-item index="/equipment">
          <i class="el-icon-s-grid"></i>
          <span>{{ $t('nav.equipment') }}</span>
        </el-menu-item>
        <el-menu-item index="/reservation/query">
          <i class="el-icon-s-order"></i>
          <span>{{ $t('nav.reservation') }}</span>
        </el-menu-item>

        <div class="right-menu">
          <!-- 添加主题切换按钮 -->
          <theme-switch class="theme-switch-container" />

          <div class="language-switcher">
            <button
              class="lang-btn"
              :class="{ active: currentLanguage === 'zh-CN' }"
              @click="handleLanguageChange('zh-CN')"
            >
              中文
            </button>
            <span class="divider">|</span>
            <button
              class="lang-btn"
              :class="{ active: currentLanguage === 'en' }"
              @click="handleLanguageChange('en')"
            >
              English
            </button>
          </div>

        <el-button
          v-if="isLoggedIn"
          type="primary"
          plain
          size="small"
          class="admin-button"
          @click="goToAdmin"
          style="min-width: 100px;"
        >
          <i class="el-icon-s-tools"></i> {{ $t('nav.admin') }}
        </el-button>
        <el-button
          v-else
          type="text"
          class="login-button"
          @click="goToLogin"
          style="min-width: 100px;"
        >
          <i class="el-icon-s-custom"></i> {{ $t('nav.login') }}
        </el-button>
      </div>
    </el-menu>
    </div>

    <!-- 移动端导航 -->
    <mobile-nav class="mobile-nav" />
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import MobileNav from './MobileNav.vue'
import ThemeSwitch from '@/components/common/ThemeSwitch.vue'
import { updatePageTitle } from '@/router/permission'

export default {
  name: 'AppHeader',

  components: {
    MobileNav,
    ThemeSwitch
  },

  computed: {
    ...mapGetters(['isLoggedIn', 'getLanguage']),

    activeIndex() {
      return this.$route.path
    },

    currentLanguage() {
      return this.getLanguage
    }
  },

  methods: {
    ...mapActions(['setLanguage']),

    goToAdmin() {
      this.$router.push('/admin/dashboard')
    },

    goToLogin() {
      this.$router.push('/admin/login')
    },

    handleLanguageChange(lang) {
      this.setLanguage(lang)
      this.$i18n.locale = lang

      // 更新页面标题
      setTimeout(() => {
        updatePageTitle()
      }, 0)
    }
  }
}
</script>

<style scoped>
.app-header {
  width: 100vw !important;
  margin: 0 !important;
  padding: 0 !important;
}

.el-menu {
  display: flex;
  align-items: center;
  padding: 0 !important;
  width: 100vw !important;
  margin: 0 !important;
  border-radius: 0 !important;
  border: none !important;
}

.logo-container {
  margin-right: 20px;
  margin-left: 0;
  padding-left: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #409EFF;
}

.logo-image {
  height: 40px;
  margin-right: 10px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
}

.right-menu {
  margin-left: auto;
  margin-right: 0;
  padding-right: 0;
  display: flex;
  align-items: center;
}

.language-switcher {
  display: flex;
  align-items: center;
  margin-right: 20px;
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

.admin-button {
  color: #409EFF;
  margin-left: 10px;
}

.login-button {
  color: #606266;
  margin-left: 10px;
}

.theme-switch-container {
  margin-right: 15px;
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
}
</style>
