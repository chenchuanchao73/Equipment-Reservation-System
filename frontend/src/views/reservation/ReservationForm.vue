<template>
  <div class="reservation-form">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="!equipment" class="error-container">
      <el-result
        icon="error"
        :title="$t('error.errorMessage')"
        :sub-title="$t('equipment.notFound')"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/equipment')">
            {{ $t('equipment.list') }}
          </el-button>
        </template>
      </el-result>
    </div>

    <div v-else>
      <!-- 返回按钮 -->
      <div class="back-link">
        <el-button icon="el-icon-arrow-left" @click="$router.push(`/equipment/${equipment.id}`)">
          {{ $t('common.back') }}
        </el-button>
      </div>

      <h1 class="page-title">{{ $t('reservation.form') }}</h1>

      <!-- 设备信息 -->
      <el-card shadow="never" class="equipment-card">
        <div class="equipment-info">
          <div class="equipment-image-container">
            <img
              :src="equipment.image_path ? getFullImageUrl(equipment.image_path) : require('@/assets/upload.png')"
              :alt="equipment.name"
              class="equipment-image"
            />
          </div>

          <div class="equipment-details">
            <h2 class="equipment-name">{{ equipment.name }}</h2>
            <p class="equipment-category">{{ equipment.category }}</p>

            <div v-if="equipment.location" class="equipment-location">
              <i class="el-icon-location"></i> {{ equipment.location }}
            </div>

            <el-tag
              :type="equipment.status === 'available' ? 'success' : 'warning'"
              size="medium"
              style="font-weight: bold; padding: 0px 10px; font-size: 14px;"
            >
              {{ equipment.status === 'available' ? $t('equipment.available') : $t('equipment.maintenance') }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 预定表单 -->
      <el-card shadow="never" class="form-card">
        <el-form
          ref="reservationForm"
          :model="form"
          :rules="rules"
          label-position="top"
          size="medium"
        >
          <!-- 预约类型选择 -->
          <el-divider>{{ $t('reservation.reservationType') }}</el-divider>

          <el-form-item :label="$t('reservation.reservationType')" prop="reservationType">
            <el-radio-group v-model="form.reservationType" @change="handleReservationTypeChange">
              <el-radio label="single">{{ $t('reservation.singleReservation') }}</el-radio>
              <el-radio label="recurring">{{ $t('reservation.recurringReservation') }}</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 时间选择 -->
          <el-divider>{{ $t('reservation.selectTime') }}</el-divider>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.startTime')" prop="startDateTime">
                <el-date-picker
                  v-model="form.startDateTime"
                  type="datetime"
                  :placeholder="$t('reservation.startTime')"
                  style="width: 100%"
                  :picker-options="startPickerOptions"
                  @change="checkTimeAvailability"
                ></el-date-picker>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.endTime')" prop="endDateTime">
                <el-date-picker
                  v-model="form.endDateTime"
                  type="datetime"
                  :placeholder="$t('reservation.endTime')"
                  style="width: 100%"
                  :picker-options="endPickerOptions"
                  @change="checkTimeAvailability"
                ></el-date-picker>
              </el-form-item>
            </el-col>
          </el-row>

          <div v-if="timeConflict" class="time-conflict-warning">
            <el-alert
              :title="$t('reservation.timeConflict')"
              type="error"
              :closable="false"
              show-icon
            ></el-alert>
          </div>

          <!-- 用户信息 -->
          <el-divider>{{ $t('common.userInfo') }}</el-divider>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.userName')" prop="userName">
                <el-input v-model="form.userName"></el-input>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.userDepartment')" prop="userDepartment">
                <el-input v-model="form.userDepartment"></el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.userContact')" prop="userContact">
                <el-input v-model="form.userContact"></el-input>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.userEmail')" prop="userEmail">
                <el-input v-model="form.userEmail" type="email"></el-input>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item :label="$t('reservation.purpose')" prop="purpose">
            <el-input
              v-model="form.purpose"
              type="textarea"
              :rows="3"
            ></el-input>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="submitting"
              @click="submitForm"
              :disabled="timeConflict"
              icon="el-icon-plus"
            >
              {{ $t('reservation.createReservation') }}
            </el-button>
            <el-button @click="resetForm" icon="el-icon-refresh-left">{{ $t('common.reset') }}</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 预定成功对话框 -->
      <el-dialog
        :title="$t('reservation.createSuccess')"
        :visible.sync="successDialogVisible"
        width="500px"
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :show-close="false"
      >
        <div class="success-content">
          <i class="el-icon-success success-icon"></i>

          <p class="success-message">{{ $t('reservation.saveReservationCode') }}</p>

          <div class="reservation-code">
            {{ reservationCode }}
          </div>

          <p class="reservation-tip">{{ $t('reservation.reservationCodeTip') }}</p>

          <div class="dialog-footer">
            <el-button @click="viewReservation">{{ $t('reservation.viewDetail') }}</el-button>
            <el-button type="primary" @click="closeSuccessDialog">{{ $t('common.confirm') }}</el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { equipmentApi, reservationApi } from '@/api'
import axios from 'axios'

export default {
  name: 'ReservationForm',

  computed: {
    // 获取完整的图片URL
    baseUrl() {
      return axios.defaults.baseURL || 'http://localhost:8000';
    }
  },

  data() {
    // 表单验证规则
    const validateTime = (rule, value, callback) => {
      if (!value) {
        callback(new Error(this.$t('reservation.requiredField')))
      } else if (this.form.startDateTime && this.form.endDateTime) {
        if (this.form.startDateTime >= this.form.endDateTime) {
          callback(new Error(this.$t('reservation.invalidTime')))
        } else {
          callback()
        }
      } else {
        callback()
      }
    }

    const validateEmail = (rule, value, callback) => {
      if (!value) {
        callback()
      } else {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) {
          callback(new Error(this.$t('reservation.emailFormat')))
        } else {
          callback()
        }
      }
    }

    return {
      loading: true,
      equipment: null,
      submitting: false,
      timeConflict: false,
      successDialogVisible: false,
      reservationCode: '',
      qrcodeUrl: null, // 二维码功能已移除

      // 表单数据
      form: {
        reservationType: 'single',
        startDateTime: null,
        endDateTime: null,
        userName: '',
        userDepartment: '',
        userContact: '',
        userEmail: '',
        purpose: ''
      },

      // 表单验证规则
      rules: {
        startDateTime: [
          { required: true, validator: validateTime, trigger: 'change' }
        ],
        endDateTime: [
          { required: true, validator: validateTime, trigger: 'change' }
        ],
        userName: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 2, max: 50, message: this.$t('reservation.nameLength'), trigger: 'blur' }
        ],
        userDepartment: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' }
        ],
        userContact: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' }
        ],
        userEmail: [
          { validator: validateEmail, trigger: 'blur' }
        ]
      },

      // 日期选择器配置
      startPickerOptions: {
        disabledDate: (time) => {
          return time.getTime() < Date.now() - 8.64e7; // 禁用过去的日期
        }
      },
      endPickerOptions: {
        disabledDate: (time) => {
          if (!this.form.startDateTime) {
            return time.getTime() < Date.now() - 8.64e7; // 如果没有选择开始时间，禁用过去的日期
          }
          return time.getTime() < this.form.startDateTime.getTime(); // 禁用早于开始时间的日期
        }
      }
    }
  },

  created() {
    this.fetchEquipment()
  },

  methods: {
    // 获取设备信息
    async fetchEquipment() {
      this.loading = true
      try {
        const equipmentId = this.$route.params.id
        const response = await equipmentApi.getEquipment(equipmentId)
        this.equipment = response.data

        if (this.equipment.status !== 'available') {
          this.$message.warning(this.$t('equipment.notAvailable'))
        }
      } catch (error) {
        console.error('Failed to fetch equipment:', error)
        this.$message.error(this.$t('common.error'))
      } finally {
        this.loading = false
      }
    },

    // 检查时间可用性
    async checkTimeAvailability() {
      if (!this.form.startDateTime || !this.form.endDateTime) {
        return
      }

      try {
        const equipmentId = this.equipment.id
        const startDate = this.formatDateTime(this.form.startDateTime)
        const endDate = this.formatDateTime(this.form.endDateTime)

        const response = await equipmentApi.getAvailability(equipmentId, startDate, endDate)

        // 检查是否有冲突
        this.timeConflict = response.data.available.includes(false)
      } catch (error) {
        console.error('Failed to check availability:', error)
        this.timeConflict = true
      }
    },

    // 处理预约类型变更
    handleReservationTypeChange(value) {
      if (value === 'recurring') {
        // 跳转到循环预约表单页面
        this.$router.push(`/equipment/${this.equipment.id}/recurring-reserve`)
      }
    },

    // 格式化日期时间
    formatDateTime(date) {
      if (!date) return null
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}:00`
    },

    // 提交表单
    submitForm() {
      this.$refs.reservationForm.validate(async (valid) => {
        if (!valid) {
          return false
        }

        this.submitting = true

        try {
          const reservationData = {
            equipment_id: this.equipment.id,
            user_name: this.form.userName,
            user_department: this.form.userDepartment,
            user_contact: this.form.userContact,
            user_email: this.form.userEmail || undefined,
            start_datetime: this.formatDateTime(this.form.startDateTime),
            end_datetime: this.formatDateTime(this.form.endDateTime),
            purpose: this.form.purpose || undefined,
            lang: this.$i18n.locale
          }

          const response = await reservationApi.createReservation(reservationData)

          if (response.data.success) {
            this.reservationCode = response.data.data.reservation_code
            this.successDialogVisible = true
            this.$refs.reservationForm.resetFields()
          } else {
            this.$message.error(response.data.message || this.$t('reservation.createFailed'))
          }
        } catch (error) {
          console.error('Failed to create reservation:', error)
          this.$message.error(this.$t('reservation.createFailed'))
        } finally {
          this.submitting = false
        }
      })
    },

    // 重置表单
    resetForm() {
      this.$refs.reservationForm.resetFields()
      this.timeConflict = false
    },

    // 查看预定详情
    viewReservation() {
      this.$router.push(`/reservation/${this.reservationCode}`)
    },

    // 关闭成功对话框
    closeSuccessDialog() {
      this.successDialogVisible = false
      this.$router.push('/equipment')
    },

    // 获取完整图片URL
    getFullImageUrl(url) {
      if (!url) return '';

      // 如果已经是完整URL，直接返回
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
      }

      // 否则拼接基础URL
      return `${this.baseUrl}${url}`;
    }
  }
}
</script>

<style scoped>
.reservation-form {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #303133;
}

.back-link {
  margin-bottom: 20px;
}

.loading-container {
  padding: 40px;
}

.error-container {
  padding: 40px;
}

.equipment-card {
  margin-bottom: 20px;
}

.equipment-info {
  display: flex;
  align-items: center;
}

.equipment-image-container {
  width: 120px;
  height: 120px;
  margin-right: 20px;
  overflow: hidden;
  border-radius: 4px;
  flex-shrink: 0;
}

.equipment-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.equipment-details {
  flex-grow: 1;
}

.equipment-name {
  font-size: 20px;
  margin: 0 0 10px 0;
  color: #303133;
}

.equipment-category {
  color: #606266;
  margin: 0 0 10px 0;
}

.equipment-location {
  color: #606266;
  margin-bottom: 10px;
}

.form-card {
  margin-bottom: 20px;
}

.time-conflict-warning {
  margin: 10px 0;
}

.success-content {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 72px;
  color: #67c23a;
  margin-bottom: 20px;
}

.success-message {
  font-size: 18px;
  margin-bottom: 20px;
}

.reservation-code {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  padding: 10px;
  background-color: white;
  margin-bottom: 10px;
}

.reservation-tip {
  color: #909399;
  margin-bottom: 20px;
}

.dialog-footer {
  margin-top: 20px;
}
</style>
