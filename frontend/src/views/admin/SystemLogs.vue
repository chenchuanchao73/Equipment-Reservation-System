<template>
  <div class="system-logs">
    <el-form :inline="true" size="small" style="margin-bottom:10px;">
      <el-form-item label="用户类型">
        <el-select v-model="logFilter.user_type" clearable placeholder="全部">
          <el-option label="管理员" value="admin"/>
          <el-option label="普通用户" value="user"/>
        </el-select>
      </el-form-item>
      <el-form-item label="操作类型">
        <el-select v-model="logFilter.action" clearable placeholder="全部">
          <el-option label="查看" value="view"/>
          <el-option label="创建" value="create"/>
          <el-option label="更新" value="update"/>
          <el-option label="删除" value="delete"/>
          <el-option label="登录" value="login"/>
          <el-option label="登出" value="logout"/>
          <el-option label="预约" value="reserve"/>
          <el-option label="取消预约" value="cancel"/>
        </el-select>
      </el-form-item>
      <el-form-item label="模块">
        <el-select v-model="logFilter.module" clearable placeholder="全部">
          <el-option label="设备" value="equipment"/>
          <el-option label="预约" value="reservation"/>
          <el-option label="管理员" value="admin"/>
          <el-option label="系统" value="system"/>
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="logFilter.status" clearable placeholder="全部">
          <el-option label="成功" value="success"/>
          <el-option label="失败" value="failed"/>
        </el-select>
      </el-form-item>
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="yyyy-MM-dd"
          value-format="yyyy-MM-dd"
        ></el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button @click="fetchLogs" type="primary">查询</el-button>
        <el-button @click="clearLogFilter">重置</el-button>
        <el-button type="danger" @click="showClearLogsDialog" v-if="isSuperAdmin">清理日志</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="logList" border style="width: 100%" v-loading="loading">
      <el-table-column prop="user_type" label="用户类型" width="100">
        <template slot-scope="scope">
          {{ scope.row.user_type === 'admin' ? '管理员' : '普通用户' }}
        </template>
      </el-table-column>
      <el-table-column prop="user_name" label="用户名/联系方式" width="150"/>
      <el-table-column prop="action" label="操作类型" width="100">
        <template slot-scope="scope">
          {{ getActionText(scope.row.action) }}
        </template>
      </el-table-column>
      <el-table-column prop="module" label="模块" width="100">
        <template slot-scope="scope">
          {{ getModuleText(scope.row.module) }}
        </template>
      </el-table-column>
      <el-table-column prop="description" label="操作描述" min-width="200"/>
      <el-table-column prop="status" label="状态" width="80">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
            {{ scope.row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="150">
        <template slot-scope="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template slot-scope="scope">
          <el-button size="mini" @click="showLogDetails(scope.row)">查看详情</el-button>
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
      title="日志详情"
      :visible.sync="logDetailsDialogVisible"
      width="60%">
      <div v-if="selectedLog">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户类型">{{ selectedLog.user_type === 'admin' ? '管理员' : '普通用户' }}</el-descriptions-item>
          <el-descriptions-item label="用户ID" v-if="selectedLog.user_id">{{ selectedLog.user_id }}</el-descriptions-item>
          <el-descriptions-item label="用户名/联系方式" v-if="selectedLog.user_name">{{ selectedLog.user_name }}</el-descriptions-item>
          <el-descriptions-item label="操作类型">{{ getActionText(selectedLog.action) }}</el-descriptions-item>
          <el-descriptions-item label="模块">{{ getModuleText(selectedLog.module) }}</el-descriptions-item>
          <el-descriptions-item label="操作描述">{{ selectedLog.description }}</el-descriptions-item>
          <el-descriptions-item label="IP地址" v-if="selectedLog.ip_address">{{ selectedLog.ip_address }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedLog.status === 'success' ? 'success' : 'danger'">
              {{ selectedLog.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="错误信息" v-if="selectedLog.error_message">{{ selectedLog.error_message }}</el-descriptions-item>
          <el-descriptions-item label="操作对象ID" v-if="selectedLog.target_id">{{ selectedLog.target_id }}</el-descriptions-item>
          <el-descriptions-item label="操作对象类型" v-if="selectedLog.target_type">{{ selectedLog.target_type }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ formatDate(selectedLog.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="详细信息" v-if="selectedLog.details">
            <pre>{{ formatDetails(selectedLog.details) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
    <el-dialog
      title="清理系统日志"
      :visible.sync="clearLogsDialogVisible"
      width="40%">
      <el-form :model="clearLogsForm" label-width="120px">
        <el-form-item label="清理时间范围">
          <el-select v-model="clearLogsForm.days" placeholder="请选择">
            <el-option label="所有日志" :value="null"></el-option>
            <el-option label="7天前的日志" :value="7"></el-option>
            <el-option label="30天前的日志" :value="30"></el-option>
            <el-option label="90天前的日志" :value="90"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="用户类型">
          <el-select v-model="clearLogsForm.user_type" clearable placeholder="全部">
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="普通用户" value="user"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="clearLogsForm.module" clearable placeholder="全部">
            <el-option label="设备" value="equipment"></el-option>
            <el-option label="预约" value="reservation"></el-option>
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="系统" value="system"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="clearLogsForm.status" clearable placeholder="全部">
            <el-option label="成功" value="success"></el-option>
            <el-option label="失败" value="failed"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="clearLogsDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="clearLogs" :loading="clearingLogs">确定清理</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
import { mapGetters } from 'vuex'

export default {
  name: 'SystemLogs',
  data() {
    return {
      logList: [],
      logTotal: 0,
      logPage: 1,
      logPageSize: 10,
      loading: false,
      logFilter: {
        user_type: '',
        action: '',
        module: '',
        status: ''
      },
      dateRange: [],
      logDetailsDialogVisible: false,
      selectedLog: null,
      clearLogsDialogVisible: false,
      clearLogsForm: {
        days: null,
        user_type: '',
        module: '',
        status: ''
      },
      clearingLogs: false,
      // 响应式布局相关
      isMobile: window.innerWidth <= 768
    }
  },

  computed: {
    ...mapGetters(['isSuperAdmin']),
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
        this.loading = true
        const params = {
          skip: (this.logPage - 1) * this.logPageSize,
          limit: this.logPageSize,
          user_type: this.logFilter.user_type,
          action: this.logFilter.action,
          module: this.logFilter.module,
          status: this.logFilter.status
        }
        
        // 添加日期范围
        if (this.dateRange && this.dateRange.length === 2) {
          params.from_date = this.dateRange[0]
          params.to_date = this.dateRange[1]
        }
        
        const res = await axios.get('/api/system/logs', { params })
        this.logList = res.data.items
        this.logTotal = res.data.total
      } catch (e) {
        this.$message.error('获取日志失败')
      } finally {
        this.loading = false
      }
    },
    clearLogFilter() {
      this.logFilter = { user_type: '', action: '', module: '', status: '' }
      this.dateRange = []
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
        
        // 拆分日期和时间
        const [datePart, timePart] = dateTimeStr.split(' ');
        const [year, month, day] = datePart.split('-').map(Number);
        const [hour, minute, second] = (timePart || '00:00:00').split(':').map(Number);
        
        // 构建日期字符串
        return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')} ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
      } catch (e) {
        console.error('日期格式化错误:', e);
      }

      // 如果解析失败，回退到简单方法
      const d = new Date(val);
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    },
    showLogDetails(log) {
      this.selectedLog = log;
      this.logDetailsDialogVisible = true;
    },
    formatDetails(details) {
      if (!details) return '';
      try {
        // 如果是JSON字符串，解析并格式化
        const obj = typeof details === 'string' ? JSON.parse(details) : details;
        return JSON.stringify(obj, null, 2);
      } catch (e) {
        return details;
      }
    },
    getActionText(action) {
      const actionMap = {
        'view': '查看',
        'create': '创建',
        'update': '更新',
        'delete': '删除',
        'login': '登录',
        'logout': '登出',
        'reserve': '预约',
        'cancel': '取消预约'
      };
      return actionMap[action] || action;
    },
    getModuleText(module) {
      const moduleMap = {
        'equipment': '设备',
        'reservation': '预约',
        'admin': '管理员',
        'system': '系统'
      };
      return moduleMap[module] || module;
    },
    // 处理窗口大小变化
    handleResize() {
      this.isMobile = window.innerWidth <= 768;
    },
    showClearLogsDialog() {
      this.clearLogsDialogVisible = true
    },
    async clearLogs() {
      try {
        this.clearingLogs = true
        
        // 构建查询参数
        const params = {}
        if (this.clearLogsForm.days) {
          params.days = this.clearLogsForm.days
        }
        if (this.clearLogsForm.user_type) {
          params.user_type = this.clearLogsForm.user_type
        }
        if (this.clearLogsForm.module) {
          params.module = this.clearLogsForm.module
        }
        if (this.clearLogsForm.status) {
          params.status = this.clearLogsForm.status
        }
        
        // 发送请求
        const res = await axios.delete('/api/system/logs', { params })
        
        // 显示成功消息
        this.$message.success(res.data.message)
        
        // 关闭对话框
        this.clearLogsDialogVisible = false
        
        // 重新获取日志列表
        this.fetchLogs()
      } catch (e) {
        this.$message.error('清理日志失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        this.clearingLogs = false
      }
    }
  }
}
</script>

<style scoped>
.system-logs {
  padding: 20px;
}
</style>
