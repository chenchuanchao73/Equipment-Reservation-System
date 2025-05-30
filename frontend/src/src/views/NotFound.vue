<template>
  <div class="not-found">
    <div class="error-container">
      <div class="error-code">404</div>
      <h1>{{ $t('error.notFound') }}</h1>
      <p>{{ $t('error.errorMessage') }}</p>
      <el-button type="primary" @click="goHome">
        {{ $t('error.backHome') }}
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  
  methods: {
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70vh;
}

.error-container {
  text-align: center;
  max-width: 500px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: #409EFF;
  line-height: 1;
  margin-bottom: 20px;
}

h1 {
  font-size: 2rem;
  color: #303133;
  margin-bottom: 20px;
}

p {
  color: #606266;
  margin-bottom: 30px;
}
</style>
