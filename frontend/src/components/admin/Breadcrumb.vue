<template>
  <el-breadcrumb class="app-breadcrumb" separator="/">
    <transition-group name="breadcrumb">
      <el-breadcrumb-item v-for="(item, index) in levelList" :key="item.path">
        <span 
          v-if="index === levelList.length - 1 || item.redirect === 'noRedirect'"
          class="no-redirect"
        >
          {{ generateTitle(item.meta.title) }}
        </span>
        <a v-else @click.prevent="handleLink(item)">
          {{ generateTitle(item.meta.title) }}
        </a>
      </el-breadcrumb-item>
    </transition-group>
  </el-breadcrumb>
</template>

<script>
export default {
  name: 'Breadcrumb',
  
  data() {
    return {
      levelList: []
    }
  },
  
  watch: {
    $route: {
      handler(route) {
        this.getBreadcrumb()
      },
      immediate: true
    }
  },
  
  methods: {
    generateTitle(title) {
      // 如果是i18n的key，则翻译，否则直接返回
      if (title.startsWith('route.')) {
        return this.$t(title)
      }
      return title
    },
    
    getBreadcrumb() {
      // 面包屑仅显示有meta.title的路由
      let matched = this.$route.matched.filter(item => item.meta && item.meta.title)
      
      // 如果不是Dashboard路由，添加Dashboard作为第一个面包屑
      const first = matched[0]
      if (first && first.path !== '/admin/dashboard') {
        matched = [
          {
            path: '/admin/dashboard',
            meta: { title: this.$t('admin.dashboard') }
          }
        ].concat(matched)
      }
      
      this.levelList = matched
    },
    
    handleLink(item) {
      const { path, redirect } = item
      if (redirect) {
        this.$router.push(redirect)
        return
      }
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
.app-breadcrumb {
  display: inline-block;
  font-size: 14px;
  line-height: 60px;
  margin-left: 8px;
}

.app-breadcrumb .no-redirect {
  color: #97a8be;
  cursor: text;
}

.breadcrumb-enter-active,
.breadcrumb-leave-active {
  transition: all 0.5s;
}

.breadcrumb-enter,
.breadcrumb-leave-active {
  opacity: 0;
  transform: translateX(20px);
}

.breadcrumb-move {
  transition: all 0.5s;
}

.breadcrumb-leave-active {
  position: absolute;
}
</style>
