<template>
  <div v-if="announcements.length && visible" class="announcement-bar">
    <div class="announcement-content">
      <span v-for="(item, idx) in announcements" :key="item.id" class="announcement-item">
        <strong>{{ item.title }}：</strong>{{ item.content }}
        <small class="announcement-date">[{{ formatDate(item.created_at) }}]</small>
        <span v-if="idx < announcements.length - 1" class="separator">|</span>
      </span>
    </div>
    <button class="close-btn" @click="visible = false">×</button>
  </div>
</template>

<script>
import { fetchAnnouncements } from '@/api/announcement'

export default {
  name: 'AnnouncementBar',
  data() {
    return {
      announcements: [],
      visible: true
    }
  },
  created() {
    this.loadAnnouncements()
  },
  methods: {
    // 格式化日期为YYYY-MM-DD HH:mm格式
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },
    async loadAnnouncements() {
      try {
        const res = await fetchAnnouncements()
        this.announcements = Array.isArray(res) ? res : []
        console.log('加载到公告数据:', this.announcements)
      } catch (e) {
        console.error('加载公告失败:', e)
      }
    }
  }
}
</script>

<style scoped>
.announcement-bar {
  background: #fffbe6;
  color: #ad6800;
  padding: 10px 16px;
  border-bottom: 1px solid #ffe58f;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 15px;
  position: sticky;
  top: 0;
  width: 100%;
  z-index: 1001;
}
.announcement-content {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.announcement-item {
  margin-right: 8px;
}
.announcement-date {
  font-size: 12px;
  color: #999;
  margin-left: 4px;
}
.separator {
  margin: 0 8px;
  color: #ffd666;
}
.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #ad6800;
  cursor: pointer;
  margin-left: 12px;
}
</style> 