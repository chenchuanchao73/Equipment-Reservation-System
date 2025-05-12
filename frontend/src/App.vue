<template>
  <div id="app">
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

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter
  },
  computed: {
    isAdminRoute() {
      return this.$route.path.startsWith('/admin')
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
}

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

#app {
  height: 100%;
  width: 100vw;
  max-width: 100vw;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.el-container {
  height: 100%;
  width: 100%;
  max-width: 100%;
  padding: 0;
  margin: 0;
  overflow-x: hidden;
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
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  width: 100%;
  max-width: 100%;
}

.el-footer {
  padding: 20px;
  background-color: #f5f7fa;
  border-top: 1px solid #e6e6e6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .el-main {
    padding: 10px;
  }

  .el-footer {
    padding: 10px;
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
</style>
