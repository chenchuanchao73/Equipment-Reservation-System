<template>
  <div class="email-logs">
    <el-form :inline="true" size="small" style="margin-bottom:10px;">
      <el-form-item label="状态">
        <el-select v-model="logFilter.status" clearable placeholder="全部">
          <el-option label="成功" value="success"/>
          <el-option label="失败" value="failed"/>
        </el-select>
      </el-form-item>
      <el-form-item label="事件类型">
        <el-input v-model="logFilter.event_type" placeholder="如 reservation_created" clearable></el-input>
      </el-form-item>
      <el-form-item>
        <el-button @click="fetchLogs" type="primary">查询</el-button>
        <el-button @click="clearLogFilter">重置</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="logList" border style="width: 100%">
      <el-table-column prop="recipient" label="收件人" min-width="120"/>
      <el-table-column prop="subject" label="主题" min-width="150"/>
      <el-table-column prop="event_type" label="事件类型" min-width="120"/>
      <el-table-column prop="status" label="状态" min-width="40">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
            {{ scope.row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" min-width="40">
        <template slot-scope="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template slot-scope="scope">
          <el-button size="mini" @click="showLogContent(scope.row)">查看内容</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      style="margin-top:10px;text-align:right"
      background
      :layout="paginationLayout"
      :total="logTotal"
      :page-size="logPageSize"
      :current-page.sync="logPage"
      @current-change="fetchLogs"
    />
    <el-dialog
      title="邮件内容"
      :visible.sync="logContentDialogVisible"
      width="60%">
      <div v-if="selectedLog && selectedLog.content_html" v-html="selectedLog.content_html"></div>
      <div v-else>暂无内容</div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmailLogs',
  data() {
    return {
      logList: [],
      logTotal: 0,
      logPage: 1,
      logPageSize: 10,
      logFilter: {
        status: '',
        event_type: ''
      },
      logContentDialogVisible: false,
      selectedLog: null,
      // 响应式布局相关
      isMobile: window.innerWidth <= 768
    }
  },

  computed: {
    // 根据屏幕宽度动态调整分页组件布局
    paginationLayout() {
      return this.isMobile
        ? 'prev, next'
        : 'prev, pager, next, jumper';
    }
  },
  created() {
    this.fetchLogs()
    // 添加窗口大小变化的监听器
    window.addEventListener('resize', this.handleResize)
  },

  beforeDestroy() {
    // 移除窗口大小变化的监听器
    window.removeEventListener('resize', this.handleResize)
  },
  methods: {
    async fetchLogs() {
      try {
        const params = {
          skip: (this.logPage - 1) * this.logPageSize,
          limit: this.logPageSize,
          status: this.logFilter.status,
          event_type: this.logFilter.event_type
        }
        const res = await axios.get('/api/admin/email/logs', { params })
        this.logList = res.data.items
        this.logTotal = res.data.total
      } catch (e) {
        this.$message.error('获取日志失败')
      }
    },
    clearLogFilter() {
      this.logFilter = { status: '', event_type: '' }
      this.logPage = 1
      this.fetchLogs()
    },
    formatDate(val) {
      if (!val) return ''
      // 将日期字符串拆分并手动构建Date对象，避免自动时区转换
      try {
        // 假设输入格式为 "YYYY-MM-DD HH:MM:SS" 或 ISO格式
        let dateTimeStr = val;
        // 如果是ISO格式带T和Z，则去掉
        if (typeof val === 'string' && val.includes('T')) {
          dateTimeStr = val.replace('T', ' ').replace('Z', '');
        }

        // 将日期时间字符串分割为组件
        const parts = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})(?::(\d{2}))?/.exec(dateTimeStr);
        if (parts) {
          const year = parseInt(parts[1]);
          const month = parseInt(parts[2]) - 1; // 月份从0开始
          const day = parseInt(parts[3]);
          const hour = parseInt(parts[4]);
          const minute = parseInt(parts[5]);
          const second = parts[6] ? parseInt(parts[6]) : 0;

          // 直接使用提取的时间组件，避免时区转换
          return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
        }
      } catch (e) {
        console.error('解析日期失败:', e);
      }

      // 如果解析失败，回退到简单方法
      const d = new Date(val);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    },
    showLogContent(log) {
      this.selectedLog = log;
      this.logContentDialogVisible = true;
    },

    // 处理窗口大小变化
    handleResize() {
      this.isMobile = window.innerWidth <= 768;
    }
  }
}
</script>

<style scoped>
.email-logs {
  padding: 20px;
}
</style>