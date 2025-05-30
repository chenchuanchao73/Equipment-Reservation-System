<template>
  <div class="admin-accounts">
    <div class="page-header">
      <h2>管理员账号管理</h2>
      <div class="page-actions">
        <el-button
          type="primary"
          icon="el-icon-plus"
          @click="handleAdd"
          v-if="isSuperAdmin"
        >
          添加管理员
        </el-button>
      </div>
    </div>

    <!-- 管理员列表 -->
    <el-card shadow="hover" class="admin-list-card">
      <div slot="header">
        <span>管理员列表</span>
      </div>
      <el-table
        :data="admins"
        v-loading="loading"
        style="width: 100%"
        :header-cell-style="{background:'#f5f7fa',color:'#606266'}"
      >
        <el-table-column prop="id" label="ID" width="80"></el-table-column>
        <el-table-column prop="username" label="用户名" width="150"></el-table-column>
        <el-table-column prop="name" label="姓名" width="150"></el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template slot-scope="scope">
            <el-tag :type="scope.row.role === 'superadmin' ? 'danger' : 'primary'">
              {{ scope.row.role === 'superadmin' ? '超级管理员' : '管理员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              icon="el-icon-edit"
              @click="handleEdit(scope.row)"
              :disabled="!isSuperAdmin && currentUser.id !== scope.row.id"
            >
              编辑
            </el-button>
            <el-button
              size="mini"
              type="danger"
              icon="el-icon-delete"
              @click="handleDelete(scope.row)"
              v-if="isSuperAdmin && currentUser.id !== scope.row.id"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 修改密码卡片 -->
    <el-card shadow="hover" class="change-password-card">
      <div slot="header">
        <span>修改密码</span>
      </div>
      <el-form
        :model="passwordForm"
        :rules="passwordRules"
        ref="passwordForm"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="oldPassword">
          <el-input
            v-model="passwordForm.oldPassword"
            type="password"
            placeholder="请输入当前密码"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新密码"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          ></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="changePassword" :loading="submitting">修改密码</el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 添加/编辑管理员对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '添加管理员' : '编辑管理员'"
      :visible.sync="dialogVisible"
      width="500px"
    >
      <el-form
        :model="form"
        :rules="rules"
        ref="form"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="dialogType === 'edit'"></el-input>
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogType === 'add'">
          <el-input v-model="form.password" type="password" show-password></el-input>
        </el-form-item>
        <el-form-item label="角色" prop="role" v-if="isSuperAdmin">
          <el-select v-model="form.role" placeholder="请选择角色">
            <el-option label="管理员" value="admin"></el-option>
            <el-option label="超级管理员" value="superadmin"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="is_active" v-if="isSuperAdmin">
          <el-switch v-model="form.is_active"></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import axios from 'axios'

export default {
  name: 'AdminAccounts',

  data() {
    // 确认密码验证
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }

    return {
      loading: false,
      submitting: false,
      admins: [],
      dialogVisible: false,
      dialogType: 'add', // 'add' or 'edit'

      // 管理员表单
      form: {
        id: null,
        username: '',
        name: '',
        password: '',
        role: 'admin',
        is_active: true
      },

      // 表单验证规则
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        name: [
          { required: true, message: '请输入姓名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能小于 6 个字符', trigger: 'blur' }
        ]
      },

      // 修改密码表单
      passwordForm: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      },

      // 密码表单验证规则
      passwordRules: {
        oldPassword: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能小于 6 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },

  computed: {
    ...mapGetters(['currentUser']),

    isSuperAdmin() {
      return this.currentUser && this.currentUser.role === 'superadmin'
    }
  },

  created() {
    this.fetchAdmins()
  },

  methods: {
    // 获取管理员列表
    async fetchAdmins() {
      this.loading = true
      try {
        // 如果是超级管理员，获取所有管理员列表
        if (this.isSuperAdmin) {
          const response = await axios.get('/api/admin')
          this.admins = response.data.items
        } else {
          // 如果是普通管理员，只获取自己的信息
          // 从API获取最新的管理员信息，确保is_active字段是最新的
          const response = await axios.get(`/api/admin/${this.currentUser.id}`)
          this.admins = [response.data]
        }
      } catch (error) {
        console.error('获取管理员列表失败:', error)
        this.$message.error('获取管理员列表失败')
      } finally {
        this.loading = false
      }
    },

    // 添加管理员
    handleAdd() {
      this.dialogType = 'add'
      this.form = {
        id: null,
        username: '',
        name: '',
        password: '',
        role: 'admin',
        is_active: true
      }
      this.dialogVisible = true
    },

    // 编辑管理员
    handleEdit(row) {
      this.dialogType = 'edit'
      this.form = { ...row }
      delete this.form.password // 编辑时不需要密码字段
      this.dialogVisible = true
    },

    // 删除管理员
    handleDelete(row) {
      this.$confirm('确认删除该管理员?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await axios.delete(`/api/admin/${row.id}`)
          this.$message.success('删除成功')
          this.fetchAdmins()
        } catch (error) {
          console.error('删除管理员失败:', error)
          this.$message.error('删除管理员失败')
        }
      }).catch(() => {
        // 取消删除
      })
    },

    // 提交表单
    submitForm() {
      this.$refs.form.validate(async valid => {
        if (!valid) return

        this.submitting = true
        try {
          if (this.dialogType === 'add') {
            // 创建管理员
            await axios.post('/api/admin', this.form)
            this.$message.success('添加管理员成功')
          } else {
            // 更新管理员
            await axios.put(`/api/admin/${this.form.id}`, this.form)
            this.$message.success('更新管理员成功')
          }

          this.dialogVisible = false
          this.fetchAdmins()
        } catch (error) {
          console.error('操作失败:', error)
          this.$message.error(error.response?.data?.detail || '操作失败')
        } finally {
          this.submitting = false
        }
      })
    },

    // 修改密码
    changePassword() {
      this.$refs.passwordForm.validate(async valid => {
        if (!valid) return

        this.submitting = true
        try {
          // 使用当前用户ID作为路径参数，避免路由冲突
          await axios.put(`/api/admin/${this.currentUser.id}/change-password`, {
            old_password: this.passwordForm.oldPassword,
            new_password: this.passwordForm.newPassword
          })

          this.$message.success('密码修改成功')
          this.resetPasswordForm()
        } catch (error) {
          console.error('修改密码失败:', error)
          this.$message.error(error.response?.data?.detail || '修改密码失败')
        } finally {
          this.submitting = false
        }
      })
    },

    // 重置密码表单
    resetPasswordForm() {
      this.$refs.passwordForm.resetFields()
    }
  }
}
</script>

<style scoped>
.admin-accounts {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.admin-list-card,
.admin-info-card {
  margin-bottom: 20px;
}

.change-password-card {
  max-width: 600px;
}

.admin-info-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .change-password-card {
    max-width: 100%;
  }
}
</style>
