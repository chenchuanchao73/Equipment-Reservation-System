<template>
  <div id="app">
    <announcement-bar v-if="announcements.length && !isAdminRoute" class="announcement-fixed" />
    <el-container>
      <el-header v-if="!isAdminRoute">
        <app-header />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
      <el-footer v-if="!isAdminRoute">
        <app-footer />
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AnnouncementBar from '@/components/common/AnnouncementBar.vue'
import { fetchAnnouncements } from '@/api/announcement'
import { mapGetters } from 'vuex'

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter,
    AnnouncementBar
  },
  data() {
    return {
      announcements: []
    }
  },
  computed: {
    ...mapGetters(['isDarkMode']),
    isAdminRoute() {
      return this.$route.path.startsWith('/admin')
    }
  },
  created() {
    this.loadAnnouncements()
    this.applyTheme()
  },
  methods: {
    async loadAnnouncements() {
      try {
        const res = await fetchAnnouncements()
        this.announcements = Array.isArray(res) ? res : []
        console.log('App组件加载到公告数据:', this.announcements)
      } catch (error) {
        console.error('加载公告失败:', error)
      }
    },
    applyTheme() {
      // 应用暗色主题
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark-mode')
      } else {
        document.documentElement.classList.remove('dark-mode')
      }
    }
  },
  watch: {
    isDarkMode: {
      handler(newValue) {
        // 当isDarkMode变化时重新应用主题
        if (newValue) {
          document.documentElement.classList.add('dark-mode')
        } else {
          document.documentElement.classList.remove('dark-mode')
        }
      },
      immediate: true
    }
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: hidden !important;
  min-height: 100vh;
}

html, body {
  margin: 0;
  padding: 0;
  height: 100vh;
  width: 100%;
  overflow-x: hidden;
  overflow-y: hidden;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100vh;
  width: 100vw;
  max-width: 100vw;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.el-container {
  height: 100vh;
  width: 100%;
  max-width: 100%;
  padding: 0;
  margin: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.el-header {
  padding: 0 !important;
  margin: 0 !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  width: 100vw !important;
  max-width: 100vw !important;
  overflow: hidden;
  background-color: #FFFFFF !important;
  border-bottom: 1px solid #EBEEF5;
  flex-shrink: 0;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  width: 100%;
  max-width: 100%;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.el-footer {
  padding: 20px;
  background-color: #f5f7fa;
  border-top: 1px solid #e6e6e6;
  flex-shrink: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .el-main {
    padding: 10px;
    overflow-y: auto;
    overflow-x: hidden;
    /* 在移动端，header高度为0，所以main区域需要为footer留出空间 */
    max-height: calc(100vh - 80px); /* 只减去footer的高度 */
    flex: 1;
  }

  .el-footer {
    padding: 10px;
    flex-shrink: 0;
    min-height: 60px; /* 确保footer有最小高度 */
    background-color: #f5f7fa;
    border-top: 1px solid #e6e6e6;
  }

  .el-header {
    height: 0 !important; /* 移动端header高度为0，但不完全隐藏，保留MobileNav */
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important; /* 允许MobileNav悬浮按钮显示 */
  }

  /* 确保移动端不能滚动超过footer */
  html, body {
    overflow: hidden;
    position: fixed;
    width: 100%;
    height: 100%;
  }

  #app {
    overflow: hidden;
    position: fixed;
    width: 100%;
    height: 100%;
  }

  .el-container {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
}

/* 通用样式 */
.page-title {
  margin-bottom: 20px;
  font-weight: bold;
  color: #303133;
}

.text-center {
  text-align: center;
}

.mb-20 {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}

/* 卡片样式 */
.custom-card {
  border-radius: 4px;
  border: 1px solid #ebeef5;
  background-color: #fff;
  overflow: hidden;
  color: #303133;
  transition: 0.3s;
  margin-bottom: 20px;
}

.custom-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.custom-card-header {
  padding: 18px 20px;
  border-bottom: 1px solid #ebeef5;
  box-sizing: border-box;
}

.custom-card-body {
  padding: 20px;
}

/* 表单样式 */
.form-container {
  max-width: 600px;
  margin: 0 auto;
}

/* 按钮样式 */
.action-button {
  margin-right: 10px;
}

/* 加载动画容器 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

/* 隐藏表格右侧的空单元格 */
.el-table__body tr td:last-child:empty,
.el-table__header tr th:last-child:empty,
.el-table__body tr td:empty,
.el-table__header tr th:empty {
  display: none !important;
}

/* 设置表格内容居中 */
.el-table th, .el-table td {
  text-align: center !important;
}

/* 表格标题行样式 */
.el-table th {
  background-color: #f2f2f2 !important;
  color: #333;
  font-weight: bold;
}

/* 表格隔行变色 */
.el-table--striped .el-table__body tr.el-table__row--striped td {
  background-color: #fafafa;
}

/* 表格内容居中显示 */
.el-table th.gutter,
.el-table colgroup col:last-child {
  display: none !important;
}

/* 隐藏表格右侧的空列 */
.el-table__body-wrapper .el-table__body td:last-child:empty {
  display: none !important;
}

/* 隐藏表格右侧的空列 */
.el-table__fixed-right-patch {
  display: none !important;
}

/* 固定公告栏在顶部 */
.announcement-fixed {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 2000;
}

/* 当公告栏显示时，给header添加上边距 */
.announcement-fixed + .el-container .el-header {
  margin-top: 40px;
}

/* 手机端适配 */
@media (max-width: 768px) {
  .announcement-fixed + .el-container .el-header {
    margin-top: 60px;
  }
}
</style>
