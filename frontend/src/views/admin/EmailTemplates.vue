<template>
  <div class="email-templates">
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
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmailTemplates',
  data() {
    return {
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
      editRow: null,
      editCache: {}
    }
  },
  created() {
    this.fetchTemplates()
  },
  methods: {
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
    }
  }
}
</script>

<style scoped>
.email-templates {
  padding: 20px;
}
</style> 