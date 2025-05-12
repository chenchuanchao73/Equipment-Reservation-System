<template>
  <el-dropdown trigger="click" @command="handleLanguageChange">
    <span class="el-dropdown-link">
      {{ currentLanguage === 'zh-CN' ? '中文' : 'English' }}
      <i class="el-icon-arrow-down el-icon--right"></i>
    </span>
    <el-dropdown-menu slot="dropdown">
      <el-dropdown-item command="zh-CN">中文</el-dropdown-item>
      <el-dropdown-item command="en">English</el-dropdown-item>
    </el-dropdown-menu>
  </el-dropdown>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'LanguageSwitcher',
  
  computed: {
    ...mapGetters(['getLanguage']),
    
    currentLanguage() {
      return this.getLanguage
    }
  },
  
  methods: {
    ...mapActions(['setLanguage']),
    
    handleLanguageChange(lang) {
      this.setLanguage(lang)
      this.$i18n.locale = lang
    }
  }
}
</script>

<style scoped>
.el-dropdown-link {
  color: #fff;
  cursor: pointer;
}
</style>
