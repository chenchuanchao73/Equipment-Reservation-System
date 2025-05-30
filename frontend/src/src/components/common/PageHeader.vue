<template>
  <div class="page-header">
    <h1 class="page-title">{{ title }}</h1>
    <div class="page-description" v-if="description">{{ description }}</div>
    <slot></slot>
  </div>
</template>

<script>
export default {
  name: 'PageHeader',

  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: #FFFFFF;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.page-title {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.page-description {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .page-header {
    margin-bottom: 15px;
    padding-bottom: 10px;
  }

  .page-title {
    font-size: 20px;
  }
}
</style>
