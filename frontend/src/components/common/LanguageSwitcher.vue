<template>
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
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { updatePageTitle } from '@/router/permission'

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

      // 更新页面标题
      setTimeout(() => {
        updatePageTitle()
      }, 0)
    }
  }
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  align-items: center;
}

.lang-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px 8px;
  color: #fff;
  font-size: 14px;
}

.lang-btn.active {
  font-weight: bold;
}

.divider {
  color: #fff;
  margin: 0 5px;
  opacity: 0.7;
}
</style>
