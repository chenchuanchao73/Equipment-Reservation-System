<template>
  <div class="email-settings">
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
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'EmailSettings',
  data() {
    return {
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
      testEmail: '',
      testLoading: false
    }
  },
  created() {
    this.fetchEmailSettings()
  },
  methods: {
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
    }
  }
}
</script>

<style scoped>
.email-settings {
  padding: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
  padding-top: 4px;
}
</style> 