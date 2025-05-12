<template>
  <div class="app-footer">
    <div class="footer-content">
      <div class="footer-content-inner">
        <p>&copy; {{ currentYear }} {{ $t('common.appName') }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AppFooter',

  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.app-footer {
  width: 100%;
  padding: 20px 0;
  background-color: #f5f7fa;
  border-top: 1px solid #e4e7ed;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.footer-content-inner p {
  margin: 0;
  color: #606266;
  text-align: center;
}

@media (max-width: 768px) {
  .footer-content {
    padding: 0 10px;
  }
}
</style>
