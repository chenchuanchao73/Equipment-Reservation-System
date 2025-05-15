<template>
  <div class="announcement-manage">
    <h2>公告管理</h2>
    <el-form :model="form" ref="formRef" label-width="80px" class="form-container" v-if="editMode">
      <el-form-item label="标题">
        <el-input v-model="form.title" maxlength="200" show-word-limit />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" rows="3" maxlength="1000" show-word-limit />
      </el-form-item>
      <el-form-item label="有效">
        <el-switch v-model="form.is_active" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm">{{ form.id ? '更新' : '发布' }}</el-button>
        <el-button @click="cancelEdit">取消</el-button>
      </el-form-item>
    </el-form>

    <el-button type="primary" @click="addAnnouncement" v-if="!editMode" style="margin-bottom: 16px;">发布新公告</el-button>

    <el-table :data="announcements" stripe style="width: 100%" v-if="announcements.length">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="content" label="内容" />
      <el-table-column prop="created_at" label="发布时间" width="180">
        <template slot-scope="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="is_active" label="有效" width="80">
        <template slot-scope="scope">
          <el-tag :type="scope.row.is_active ? 'success' : 'info'">
            {{ scope.row.is_active ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template slot-scope="scope">
          <el-button size="mini" @click="editAnnouncement(scope.row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="deleteAnnouncement(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div v-else class="empty-tip">暂无公告</div>
  </div>
</template>

<script>
import {
  fetchAllAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement
} from '@/api/announcement'

export default {
  name: 'AnnouncementManage',
  data() {
    return {
      announcements: [],
      form: {
        id: null,
        title: '',
        content: '',
        is_active: true
      },
      editMode: false
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
        const res = await fetchAllAnnouncements()
        this.announcements = Array.isArray(res) ? res : []
        console.log('加载到所有公告数据:', this.announcements)
      } catch (e) {
        console.error('公告加载失败:', e)
        this.$message.error('公告加载失败')
      }
    },
    addAnnouncement() {
      this.form = { id: null, title: '', content: '', is_active: true }
      this.editMode = true
    },
    editAnnouncement(row) {
      this.form = { ...row }
      this.editMode = true
    },
    cancelEdit() {
      this.editMode = false
      this.form = { id: null, title: '', content: '', is_active: true }
    },
    async submitForm() {
      if (!this.form.title || !this.form.content) {
        this.$message.error('标题和内容不能为空')
        return
      }
      try {
        if (this.form.id) {
          await updateAnnouncement(this.form.id, this.form)
          this.$message.success('公告已更新')
        } else {
          await createAnnouncement(this.form)
          this.$message.success('公告已发布')
        }
        this.editMode = false
        this.loadAnnouncements()
      } catch (e) {
        this.$message.error('操作失败')
      }
    },
    async deleteAnnouncement(id) {
      try {
        await deleteAnnouncement(id)
        this.$message.success('公告已删除')
        this.loadAnnouncements()
      } catch (e) {
        this.$message.error('删除失败')
      }
    }
  }
}
</script>

<style scoped>
.announcement-manage {
  max-width: 900px;
  margin: 0 auto;
  background: #fff;
  padding: 24px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.form-container {
  margin-bottom: 24px;
}
.empty-tip {
  text-align: center;
  color: #999;
  margin: 32px 0;
  font-size: 16px;
}
</style> 