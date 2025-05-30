<template>
  <div class="admin-login">
    <div class="login-container">
      <div class="login-header">
        <img src="@/assets/logo.png" alt="Logo" class="login-logo" />
        <h1>{{ $t('admin.login') }}</h1>
      </div>

      <el-card shadow="never" class="login-card">
        <el-form
          ref="loginForm"
          :model="loginForm"
          :rules="loginRules"
          label-position="top"
          @submit.native.prevent="handleLogin"
        >
          <el-form-item :label="$t('admin.username')" prop="username">
            <el-input
              v-model="loginForm.username"
              prefix-icon="el-icon-user"
              :placeholder="$t('admin.username')"
            ></el-input>
          </el-form-item>

          <el-form-item :label="$t('admin.password')" prop="password">
            <el-input
              v-model="loginForm.password"
              prefix-icon="el-icon-lock"
              type="password"
              :placeholder="$t('admin.password')"
              show-password
            ></el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              :loading="loading"
              style="width: 100%"
            >
              {{ $t('admin.loginButton') }}
            </el-button>
          </el-form-item>

          <!-- 后端连接状态 -->
          <div class="backend-status">
            <span>后端服务状态: </span>
            <el-tag v-if="backendStatus === 'online'" type="success" size="small">在线</el-tag>
            <el-tag v-else-if="backendStatus === 'partial'" type="warning" size="small">部分可用</el-tag>
            <el-tag v-else-if="backendStatus === 'offline'" type="danger" size="small">离线</el-tag>
            <el-tag v-else-if="backendStatus === 'error'" type="danger" size="small">错误</el-tag>
            <el-tag v-else-if="checkingBackend" type="info" size="small">检查中...</el-tag>
            <el-tag v-else type="info" size="small">未知</el-tag>
            <el-button type="text" size="small" @click="checkBackendConnection" :loading="checkingBackend">重新检查</el-button>
          </div>

          <!-- 后端连接问题提示 -->
          <el-alert
            v-if="backendStatus === 'offline' || backendStatus === 'error'"
            title="无法连接到后端服务"
            type="error"
            description="请确保后端服务已启动并运行在 http://localhost:8000"
            show-icon
            :closable="false">
          </el-alert>
        </el-form>
      </el-card>

      <div class="login-footer">
        <el-button type="text" @click="$router.push('/')">
          {{ $t('common.back') }} {{ $t('nav.home') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'AdminLogin',

  data() {
    return {
      loading: false,
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 3, max: 20, message: this.$t('common.lengthLimit', { min: 3, max: 20 }), trigger: 'blur' }
        ],
        password: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 6, max: 20, message: this.$t('common.lengthLimit', { min: 6, max: 20 }), trigger: 'blur' }
        ]
      },
      backendStatus: null,  // 后端状态
      checkingBackend: false  // 检查后端状态中
    }
  },

  mounted() {
    // 页面加载时检查后端连接
    this.checkBackendConnection()
  },

  methods: {
    ...mapActions(['login']),

    // 检查后端连接状态
    async checkBackendConnection() {
      this.checkingBackend = true
      this.backendStatus = null

      try {
        // 尝试访问后端健康检查端点
        const response = await this.$http.get('/api/health', { timeout: 5000 })
        if (response.status === 200) {
          this.backendStatus = 'online'
          console.log('Backend is online:', response.data)
        } else {
          this.backendStatus = 'error'
          console.error('Backend health check failed:', response)
        }
      } catch (error) {
        this.backendStatus = 'offline'
        console.error('Backend connection error:', error)

        // 尝试直接访问后端根路径
        try {
          await this.$http.get('/', { timeout: 5000 })
          this.backendStatus = 'partial'
          console.log('Backend root is accessible but API is not')
        } catch (e) {
          console.error('Backend root is also not accessible')
        }
      } finally {
        this.checkingBackend = false
      }
    },

    handleLogin() {
      this.$refs.loginForm.validate(async (valid) => {
        if (!valid) {
          return false
        }

        this.loading = true

        try {
          const success = await this.login({
            username: this.loginForm.username,
            password: this.loginForm.password
          })

          if (success) {
            this.$message.success(this.$t('admin.loginSuccess'))

            // 登录成功后的重定向处理
            const redirectPath = this.$route.query.redirect || '/admin/dashboard'
            // 直接使用字符串路径，避免复杂的对象参数
            this.$router.replace(redirectPath)
          } else {
            // 显示更详细的错误信息
            this.$message.error(this.$t('admin.loginFailed') + ' - 请检查后端服务是否正常运行')
            console.log('登录失败，请检查后端服务是否在 ' + this.$http.defaults.baseURL + ' 运行')
          }
        } catch (error) {
          console.error('Login error:', error)
          this.$message.error(this.$t('admin.loginFailed'))
        } finally {
          this.loading = false
        }
      })
    }
  }
}
</script>

<style scoped>
.admin-login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #f5f7fa;
}

.login-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo {
  height: 60px;
  margin-bottom: 20px;
}

.login-header h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.login-card {
  margin-bottom: 20px;
}

.login-footer {
  text-align: center;
}

.backend-status {
  margin: 15px 0;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 4px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.backend-status span {
  margin-right: 10px;
  font-size: 14px;
  color: #606266;
}

.backend-status .el-button {
  margin-left: auto;
}
</style>
