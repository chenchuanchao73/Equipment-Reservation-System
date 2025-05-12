<template>
  <div class="admin-settings">
    <el-tabs v-model="activeTab" @tab-click="handleTabClick">
      <el-tab-pane label="基础设置" name="base">
        <p>（这里是原有系统设置内容）</p>
      </el-tab-pane>
      <el-tab-pane label="邮件设置" name="email">
        <el-form :model="emailSettings" label-width="120px" @submit.native.prevent="saveEmailSettings">
          <el-form-item label="SMTP服务器">
            <el-input v-model="emailSettings.smtp_server"></el-input>
          </el-form-item>
          <el-form-item label="端口">
            <el-input v-model="emailSettings.smtp_port" type="number"></el-input>
          </el-form-item>
          <el-form-item label="发件人邮箱">
            <el-input v-model="emailSettings.sender_email"></el-input>
          </el-form-item>
          <el-form-item label="发件人名称">
            <el-input v-model="emailSettings.sender_name"></el-input>
          </el-form-item>
          <el-form-item label="SMTP用户名">
            <el-input v-model="emailSettings.smtp_username"></el-input>
          </el-form-item>
          <el-form-item label="SMTP密码">
            <el-input v-model="emailSettings.smtp_password" show-password></el-input>
          </el-form-item>
          <el-form-item label="抄送人列表">
            <el-input
              v-model="emailSettings.cc_list"
              type="textarea"
              :rows="2"
              placeholder="多个邮箱请用逗号分隔，例如：admin1@example.com, admin2@example.com"
            ></el-input>
            <div class="form-tip">多个邮箱请用逗号分隔，所有发出的邮件都会抄送给这些邮箱</div>
          </el-form-item>
          <el-form-item label="密送人列表">
            <el-input
              v-model="emailSettings.bcc_list"
              type="textarea"
              :rows="2"
              placeholder="多个邮箱请用逗号分隔，例如：manager1@example.com, manager2@example.com"
            ></el-input>
            <div class="form-tip">多个邮箱请用逗号分隔，所有发出的邮件都会密送给这些邮箱</div>
          </el-form-item>
          <el-form-item label="使用SSL">
            <el-switch v-model="emailSettings.use_ssl"></el-switch>
          </el-form-item>
          <el-form-item label="启用邮件功能">
            <el-switch v-model="emailSettings.enabled"></el-switch>
          </el-form-item>
          <el-form-item label="测试收件人邮箱">
            <el-input v-model="testEmail"></el-input>
            <el-button type="primary" @click="testEmailSend" :loading="testLoading" style="margin-left:10px;">测试邮件</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveEmailSettings">保存</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
      <el-tab-pane label="邮件模板" name="template">
        <div style="margin-bottom: 10px;">
          <el-button type="primary" @click="openTemplateDialog()">新增模板</el-button>
        </div>
        <el-table :data="templateList" border style="width: 100%">
          <el-table-column prop="name" label="模板名称" min-width="120">
            <template slot-scope="scope">
              <span v-if="editRow !== scope.row.id">{{ scope.row.name }}</span>
              <el-input v-else v-model="editCache.name" size="small"></el-input>
            </template>
          </el-table-column>
          <el-table-column prop="template_key" label="模板键名" min-width="120"/>
          <el-table-column prop="subject" label="主题" min-width="150">
            <template slot-scope="scope">
              <span v-if="editRow !== scope.row.id">{{ scope.row.subject }}</span>
              <el-input v-else v-model="editCache.subject" size="small"></el-input>
            </template>
          </el-table-column>
          <el-table-column prop="language" label="语言" min-width="80">
            <template slot-scope="scope">
              <span v-if="editRow !== scope.row.id">{{ scope.row.language }}</span>
              <el-select v-else v-model="editCache.language" size="small" style="width:100px">
                <el-option label="中文" value="zh_CN"/>
                <el-option label="English" value="en"/>
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="content_html" label="HTML内容" min-width="250">
            <template slot-scope="scope">
              <span v-if="editRow !== scope.row.id" style="white-space:pre-line;word-break:break-all;max-width:400px;display:inline-block;">
                {{ scope.row.content_html }}
              </span>
              <el-input
                v-else
                type="textarea"
                v-model="editCache.content_html"
                :rows="4"
                size="small"
              ></el-input>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="150">
            <template slot-scope="scope">
              <template v-if="editRow === scope.row.id">
                <el-button type="primary" size="mini" @click="saveEdit(scope.row)">保存</el-button>
                <el-button size="mini" @click="cancelEdit">取消</el-button>
              </template>
              <template v-else>
                <el-button type="text" @click="startEdit(scope.row)">编辑</el-button>
                <el-button type="text" style="color:red" @click="deleteTemplate(scope.row)">删除</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
        <el-dialog :title="templateDialogTitle" :visible.sync="templateDialogVisible" width="600px">
          <el-form :model="templateForm" label-width="100px" :rules="templateRules" ref="templateFormRef">
            <el-form-item label="模板名称" prop="name">
              <el-input v-model="templateForm.name"></el-input>
            </el-form-item>
            <el-form-item label="模板键名" prop="template_key">
              <el-input v-model="templateForm.template_key"></el-input>
            </el-form-item>
            <el-form-item label="主题" prop="subject">
              <el-input v-model="templateForm.subject"></el-input>
            </el-form-item>
            <el-form-item label="语言" prop="language">
              <el-select v-model="templateForm.language" placeholder="请选择">
                <el-option label="中文" value="zh_CN"/>
                <el-option label="English" value="en"/>
              </el-select>
            </el-form-item>
            <el-form-item label="HTML内容" prop="content_html">
              <el-input type="textarea" v-model="templateForm.content_html" :rows="8" placeholder="支持Jinja2变量，如 reservation.user_name"></el-input>
            </el-form-item>
          </el-form>
          <div slot="footer" class="dialog-footer">
            <el-button @click="templateDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveTemplate">保存</el-button>
          </div>
        </el-dialog>
      </el-tab-pane>
      <el-tab-pane label="邮件日志" name="log">
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
          <el-table-column prop="status" label="状态" min-width="80">
            <template slot-scope="scope">
              <el-tag :type="scope.row.status === 'success' ? 'success' : 'danger'">
                {{ scope.row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" min-width="160">
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
          layout="prev, pager, next, jumper"
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
      </el-tab-pane>
      <el-tab-pane v-if="isSuperAdmin" label="数据库表查看" name="db-viewer">
        <DatabaseViewer ref="dbViewer" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import axios from 'axios'
import { mapState } from 'vuex'
import DatabaseViewer from './DatabaseViewer.vue'
export default {
  name: 'AdminSettings',
  components: { DatabaseViewer },
  data() {
    return {
      activeTab: 'base',
      emailSettings: {
        smtp_server: '',
        smtp_port: 587,
        sender_email: '',
        sender_name: '',
        smtp_username: '',
        smtp_password: '',
        cc_list: '',
        bcc_list: '',
        use_ssl: true,
        enabled: false
      },
      templateList: [],
      templateDialogVisible: false,
      templateDialogTitle: '新增模板',
      templateForm: {
        id: null,
        name: '',
        template_key: '',
        subject: '',
        content_html: '',
        language: 'zh_CN'
      },
      templateRules: {
        name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
        template_key: [{ required: true, message: '请输入模板键名', trigger: 'blur' }],
        subject: [{ required: true, message: '请输入主题', trigger: 'blur' }],
        content_html: [{ required: true, message: '请输入HTML内容', trigger: 'blur' }],
        language: [{ required: true, message: '请选择语言', trigger: 'change' }]
      },
      logList: [],
      logTotal: 0,
      logPage: 1,
      logPageSize: 10,
      logFilter: {
        status: '',
        event_type: ''
      },
      testEmail: '',
      testLoading: false,
      editRow: null,
      editCache: {},
      logContentDialogVisible: false,
      selectedLog: null
    }
  },
  computed: {
    ...mapState({
      user: state => state.user,
    }),
    isSuperAdmin() {
      return this.user && this.user.role === 'superadmin'
    },
  },
  created() {
    this.fetchEmailSettings()
    this.fetchTemplates()
    this.fetchLogs()
  },
  methods: {
    handleTabClick(tab) {
      if (tab.name === 'db-viewer' && this.$refs.dbViewer) {
        this.$refs.dbViewer.initIfNeeded()
      }
    },
    async fetchEmailSettings() {
      try {
        const res = await axios.get('/api/admin/email/settings')
        this.emailSettings = res.data
      } catch (e) {
        this.$message.error('获取邮件设置失败')
      }
    },
    async saveEmailSettings() {
      try {
        await axios.post('/api/admin/email/settings', this.emailSettings)
        this.$message.success('保存成功')
      } catch (e) {
        this.$message.error('保存失败')
      }
    },
    async fetchTemplates() {
      try {
        const res = await axios.get('/api/admin/email/templates')
        this.templateList = res.data
      } catch (e) {
        this.$message.error('获取模板失败')
      }
    },
    openTemplateDialog(row) {
      if (row) {
        this.templateDialogTitle = '编辑模板'
        this.templateForm = { ...row }
      } else {
        this.templateDialogTitle = '新增模板'
        this.templateForm = {
          id: null,
          name: '',
          template_key: '',
          subject: '',
          content_html: '',
          language: 'zh_CN'
        }
      }
      this.templateDialogVisible = true
    },
    async saveTemplate() {
      this.$refs.templateFormRef.validate(async valid => {
        if (!valid) return
        try {
          if (this.templateForm.id) {
            await axios.put(`/api/admin/email/templates/${this.templateForm.id}`, this.templateForm)
            this.$message.success('更新成功')
          } else {
            await axios.post('/api/admin/email/templates', this.templateForm)
            this.$message.success('新增成功')
          }
          this.templateDialogVisible = false
          this.fetchTemplates()
        } catch (e) {
          this.$message.error(e.response?.data?.detail || '保存失败')
        }
      })
    },
    async deleteTemplate(row) {
      this.$confirm('确定要删除该模板吗？', '提示', { type: 'warning' })
        .then(async () => {
          await axios.delete(`/api/admin/email/templates/${row.id}`)
          this.$message.success('删除成功')
          this.fetchTemplates()
        })
        .catch(() => {})
    },
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
    async deleteLog(row) {
      this.$confirm('确定要删除该日志吗？', '提示', { type: 'warning' })
        .then(async () => {
          await axios.delete(`/api/admin/email/logs/${row.id}`)
          this.$message.success('删除成功')
          this.fetchLogs()
        })
        .catch(() => {})
    },
    formatDate(val) {
      if (!val) return ''
      let d = typeof val === 'string' && !val.endsWith('Z')
        ? new Date(val + 'Z')
        : new Date(val)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    },
    async testEmailSend() {
      if (!this.testEmail) {
        this.$message.warning('请输入测试收件人邮箱')
        return
      }
      this.testLoading = true
      try {
        const payload = {
          ...this.emailSettings,
          to_email: this.testEmail
        }
        const res = await axios.post('/api/admin/email/test', payload)
        if (res.data.success) {
          this.$message.success(res.data.message)
        } else {
          this.$message.error(res.data.message)
        }
      } catch (e) {
        this.$message.error('请求失败')
      } finally {
        this.testLoading = false
      }
    },
    startEdit(row) {
      this.editRow = row.id
      this.editCache = { ...row }
    },
    cancelEdit() {
      this.editRow = null
      this.editCache = {}
    },
    async saveEdit(row) {
      try {
        await this.$confirm('确定保存修改吗？', '提示', { type: 'warning' })
        await axios.put(`/api/admin/email/templates/${row.id}`, this.editCache)
        this.$message.success('保存成功')
        this.editRow = null
        this.editCache = {}
        this.fetchTemplates()
      } catch (e) {
        this.$message.error(e.response?.data?.detail || '保存失败')
      }
    },
    showLogContent(log) {
      this.selectedLog = log;
      window.selectedLog = log;
      this.logContentDialogVisible = true;
    }
  }
}
</script>

<style scoped>
.admin-settings {
  padding: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
  padding-top: 4px;
}
</style>
