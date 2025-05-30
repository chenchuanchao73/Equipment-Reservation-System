<template>
  <div class="empty-state">
    <div class="empty-image">
      <i :class="icon"></i>
    </div>
    <div class="empty-text">{{ text }}</div>
    <div class="empty-action" v-if="actionText">
      <el-button type="primary" @click="$emit('action-click')">
        {{ actionText }}
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  
  props: {
    text: {
      type: String,
      default: '暂无数据'
    },
    icon: {
      type: String,
      default: 'el-icon-document'
    },
    actionText: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  text-align: center;
}

.empty-image {
  margin-bottom: 20px;
}

.empty-image i {
  font-size: 60px;
  color: #c0c4cc;
}

.empty-text {
  font-size: 14px;
  color: #909399;
  margin-bottom: 20px;
}

.empty-action {
  margin-top: 10px;
}
</style>
