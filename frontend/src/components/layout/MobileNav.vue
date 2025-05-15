<template>
  <div class="mobile-nav">
    <div class="mobile-nav-overlay" v-if="isOpen" @click="closeMenu"></div>

    <div class="mobile-nav-toggle" @click="toggleMenu">
      <i :class="isOpen ? 'el-icon-close' : 'el-icon-menu'"></i>
    </div>

    <div class="mobile-nav-menu" :class="{ 'mobile-nav-menu-open': isOpen }">
      <div class="mobile-nav-header">
        <img src="@/assets/images/logo.svg" alt="Logo" class="mobile-nav-logo">
        <h3 class="mobile-nav-title">{{ $t('common.appName') }}</h3>
      </div>

      <el-menu
        :default-active="activeRoute"
        class="mobile-nav-list"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        @select="handleSelect"
      >
        <el-menu-item index="/">
          <i class="el-icon-s-home"></i>
          <span>{{ $t('nav.home') }}</span>
        </el-menu-item>

        <el-menu-item index="/equipment">
          <i class="el-icon-s-grid"></i>
          <span>{{ $t('nav.equipment') }}</span>
        </el-menu-item>

        <el-menu-item index="/reservation/query">
          <i class="el-icon-s-order"></i>
          <span>{{ $t('nav.reservation') }}</span>
        </el-menu-item>

        <el-menu-item index="/calendar">
          <i class="el-icon-date"></i>
          <span>{{ $t('nav.calendar') }}</span>
        </el-menu-item>

        <el-menu-item index="/admin/login">
          <i class="el-icon-s-custom"></i>
          <span>{{ $t('nav.admin') }}</span>
        </el-menu-item>
      </el-menu>

      <div class="mobile-nav-footer">
        <language-switcher />
      </div>
    </div>
  </div>
</template>

<script>
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue'

export default {
  name: 'MobileNav',

  components: {
    LanguageSwitcher
  },

  data() {
    return {
      isOpen: false
    }
  },

  computed: {
    activeRoute() {
      return this.$route.path
    }
  },

  methods: {
    toggleMenu() {
      this.isOpen = !this.isOpen

      // 禁用/启用body滚动
      if (this.isOpen) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    },

    closeMenu() {
      this.isOpen = false
      document.body.style.overflow = ''
    },

    handleSelect(key) {
      this.$router.push(key)
      this.closeMenu()
    }
  },

  // 路由变化时关闭菜单
  watch: {
    '$route'() {
      this.closeMenu()
    }
  },

  // 组件销毁时恢复body滚动
  beforeDestroy() {
    document.body.style.overflow = ''
  }
}
</script>

<style scoped>
.mobile-nav {
  display: none;
}

.mobile-nav-toggle {
  position: fixed;
  top: 15px;
  right: 15px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #409EFF;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  z-index: 1001;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.mobile-nav-toggle i {
  font-size: 24px;
}

.mobile-nav-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.mobile-nav-menu {
  position: fixed;
  top: 0;
  right: -280px;
  width: 280px;
  height: 100%;
  background-color: #304156;
  z-index: 1000;
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.mobile-nav-menu-open {
  right: 0;
}

.mobile-nav-header {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #263445;
}

.mobile-nav-logo {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.mobile-nav-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.mobile-nav-list {
  flex: 1;
  border-right: none;
}

.mobile-nav-footer {
  padding: 15px 20px;
  background-color: #263445;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .mobile-nav {
    display: block;
  }
  .mobile-nav-toggle {
    top: 50%;
    right: 0;
    left: auto;
    transform: translateY(-50%);
    margin-right: 8px;
  }
}
</style>
