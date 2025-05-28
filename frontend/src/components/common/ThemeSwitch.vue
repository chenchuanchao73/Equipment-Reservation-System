<template>
  <div class="theme-switch">
    <el-tooltip :content="$t('common.toggleTheme')" placement="bottom">
      <el-button 
        :class="['theme-switch-btn', isDarkMode ? 'is-dark' : 'is-light']" 
        circle 
        @click="toggleTheme"
      >
        <i :class="isDarkMode ? 'el-icon-moon' : 'el-icon-sunny'"></i>
      </el-button>
    </el-tooltip>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'ThemeSwitch',
  computed: {
    ...mapGetters(['isDarkMode'])
  },
  methods: {
    ...mapActions(['toggleDarkMode']),
    async toggleTheme() {
      const isDark = await this.toggleDarkMode()
      this.applyDarkMode(isDark)
    },
    applyDarkMode(isDark) {
      // 应用或删除暗色主题样式类
      if (isDark) {
        document.documentElement.classList.add('dark-mode')
      } else {
        document.documentElement.classList.remove('dark-mode')
      }
    }
  },
  mounted() {
    // 初始化时应用主题设置
    this.applyDarkMode(this.isDarkMode)
  }
}
</script>

<style scoped>
.theme-switch {
  display: flex;
  align-items: center;
}

.theme-switch-btn {
  transition: background-color 0.3s, color 0.3s;
}

.theme-switch-btn.is-light {
  background-color: #ffffff;
  color: #409eff;
}

.theme-switch-btn.is-dark {
  background-color: #181a1b;
  color: #f0c78a;
}

.el-icon-sunny, .el-icon-moon {
  font-size: 16px;
}
</style> 