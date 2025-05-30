<template>
  <div class="email-layout">
    <div class="email-submenu">
      <el-menu
        :default-active="activeSubmenu"
        class="email-menu"
        mode="horizontal"
        router
      >
        <el-menu-item index="/admin/email/settings">
          <i class="el-icon-setting"></i>
          <span>邮件设置</span>
        </el-menu-item>
        <el-menu-item index="/admin/email/templates">
          <i class="el-icon-document"></i>
          <span>邮件模板</span>
        </el-menu-item>
        <el-menu-item index="/admin/email/logs">
          <i class="el-icon-tickets"></i>
          <span>邮件日志</span>
        </el-menu-item>
      </el-menu>
    </div>
    <div class="email-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmailLayout',
  computed: {
    activeSubmenu() {
      return this.$route.path
    }
  }
}
</script>

<style scoped>
.email-layout {
  width: 100%;
  height: 100%;
}

.email-submenu {
  margin-bottom: 20px;
  border-bottom: 1px solid #e6e6e6;
}

.email-menu {
  border-bottom: none;
}

.email-content {
  padding: 0;
}
</style> 