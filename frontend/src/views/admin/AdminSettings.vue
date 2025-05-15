<template>
  <div class="admin-settings">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基础设置" name="base">
        <p>（这里是原有系统设置内容）</p>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
export default {
  name: 'AdminSettings',
  data() {
    return {
      activeTab: 'base'
    }
  }
}
</script>

<style scoped>
.admin-settings {
  padding: 20px;
}
</style> 