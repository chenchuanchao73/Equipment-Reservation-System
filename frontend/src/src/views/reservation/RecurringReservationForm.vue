<template>
  <div class="recurring-reservation-form">
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
        
        <!-- 添加返回单次预约按钮 -->
        <el-button 
          type="primary" 
          icon="el-icon-refresh-left" 
          @click="backToSingleReservation" 
          class="back-to-single">
          {{ $t('reservation.singleReservation') }}
        </el-button>
      </div>

      <h1 class="page-title">{{ $t('reservation.recurringForm') }}</h1>

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
          <!-- 循环模式选择 -->
          <el-divider>{{ $t('reservation.recurringPattern') }}</el-divider>

          <el-form-item :label="$t('reservation.patternType')" prop="patternType">
            <el-radio-group v-model="form.patternType">
              <el-radio label="daily">{{ $t('reservation.daily') }}</el-radio>
              <el-radio label="weekly">{{ $t('reservation.weekly') }}</el-radio>
              <el-radio label="monthly">{{ $t('reservation.monthly') }}</el-radio>
            </el-radio-group>
          </el-form-item>

          <!-- 每周几 (仅在每周模式下显示) -->
          <el-form-item 
            v-if="form.patternType === 'weekly'" 
            :label="$t('reservation.daysOfWeek')" 
            prop="daysOfWeek"
          >
            <el-checkbox-group v-model="form.daysOfWeek">
              <el-checkbox :label="0">{{ $t('reservation.sunday') }}</el-checkbox>
              <el-checkbox :label="1">{{ $t('reservation.monday') }}</el-checkbox>
              <el-checkbox :label="2">{{ $t('reservation.tuesday') }}</el-checkbox>
              <el-checkbox :label="3">{{ $t('reservation.wednesday') }}</el-checkbox>
              <el-checkbox :label="4">{{ $t('reservation.thursday') }}</el-checkbox>
              <el-checkbox :label="5">{{ $t('reservation.friday') }}</el-checkbox>
              <el-checkbox :label="6">{{ $t('reservation.saturday') }}</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <!-- 每月几号 (仅在每月模式下显示) -->
          <el-form-item 
            v-if="form.patternType === 'monthly'" 
            :label="$t('reservation.daysOfMonth')" 
            prop="daysOfMonth"
          >
            <el-select 
              v-model="form.daysOfMonth" 
              multiple 
              :placeholder="$t('reservation.selectDaysOfMonth')"
              style="width: 100%"
            >
              <el-option 
                v-for="day in 31" 
                :key="day" 
                :label="day" 
                :value="day"
              ></el-option>
            </el-select>
          </el-form-item>

          <!-- 日期范围选择 -->
          <el-form-item :label="$t('reservation.dateRange')" prop="dateRange">
            <el-date-picker
              v-model="form.dateRange"
              type="daterange"
              range-separator="→"
              :start-placeholder="$t('reservation.startDate')"
              :end-placeholder="$t('reservation.endDate')"
              style="width: 100%"
              :picker-options="dateRangePickerOptions"
              @change="checkTimeAvailability"
            ></el-date-picker>
          </el-form-item>

          <!-- 时间选择 -->
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.startTime')" prop="startTime">
                <el-time-picker
                  v-model="form.startTime"
                  :placeholder="$t('reservation.startTime')"
                  style="width: 100%"
                  format="HH:mm"
                  @change="checkTimeAvailability"
                ></el-time-picker>
              </el-form-item>
            </el-col>

            <el-col :xs="24" :sm="12">
              <el-form-item :label="$t('reservation.endTime')" prop="endTime">
                <el-time-picker
                  v-model="form.endTime"
                  :placeholder="$t('reservation.endTime')"
                  style="width: 100%"
                  format="HH:mm"
                  @change="checkTimeAvailability"
                ></el-time-picker>
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
              {{ $t('reservation.createRecurringReservation') }}
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

          <!-- 预定码单独显示在最上方 -->
          <div class="reservation-code-container">
            <span class="reservation-code">{{ reservationCode || '无预约码' }}</span>
          </div>

          <div class="reservation-summary">
            <p><strong>{{ $t('reservation.patternType') }}:</strong> {{ getPatternTypeText() }}</p>
            <p v-if="form.patternType === 'weekly'">
              <strong>{{ $t('reservation.daysOfWeek') }}:</strong> {{ getWeekdaysText() }}
            </p>
            <p v-if="form.patternType === 'monthly'">
              <strong>{{ $t('reservation.daysOfMonth') }}:</strong> {{ getDaysOfMonthText() }}
            </p>
            <p>
              <strong>{{ $t('reservation.dateRange') }}:</strong> 
              {{ formatDate(form.dateRange[0]) }} → {{ formatDate(form.dateRange[1]) }}
            </p>
            <p>
              <strong>{{ $t('reservation.timeRange') }}:</strong> 
              {{ formatTime(form.startTime) }} → {{ formatTime(form.endTime) }}
            </p>
          </div>

          <!-- 冲突信息显示区域 -->
          <div v-if="hasConflicts" class="conflict-info">
            <el-alert
              :title="$t('reservation.conflictAlert')"
              type="warning"
              :closable="false"
              show-icon
            >
              <div class="conflict-details">
                <p>{{ $t('reservation.totalPlanned') }}: {{ totalPlanned }}</p>
                <p>{{ $t('reservation.createdCount') }}: {{ createdCount }}</p>
                <p>{{ $t('reservation.skippedCount') }}: {{ skippedCount }}</p>
              </div>
              
              <div v-if="conflictDates && conflictDates.length > 0" class="conflict-dates">
                <p><strong>{{ $t('reservation.conflictDates') }}:</strong></p>
                <el-tag
                  v-for="(date, index) in conflictDates"
                  :key="index"
                  type="danger"
                  size="small"
                  effect="plain"
                  class="conflict-date-tag"
                >
                  {{ date }}
                </el-tag>
              </div>
            </el-alert>
          </div>

          <p class="reservation-tip">{{ $t('reservation.recurringReservationTip') }}</p>

          <div class="dialog-footer">
            <el-button @click="viewRecurringReservation">{{ $t('reservation.viewDetail') }}</el-button>
            <el-button type="primary" @click="closeSuccessDialog">{{ $t('common.confirm') }}</el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { equipmentApi, recurringReservationApi } from '@/api'
import axios from 'axios'

export default {
  name: 'RecurringReservationForm',

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
      } else if (this.form.startTime && this.form.endTime) {
        const start = new Date(this.form.startTime)
        const end = new Date(this.form.endTime)
        if (start >= end) {
          callback(new Error(this.$t('reservation.invalidTime')))
        } else {
          callback()
        }
      } else {
        callback()
      }
    }

    const validateDateRange = (rule, value, callback) => {
      if (!value || !value[0] || !value[1]) {
        callback(new Error(this.$t('reservation.requiredField')))
      } else {
        callback()
      }
    }

    const validateDaysOfWeek = (rule, value, callback) => {
      if (this.form.patternType === 'weekly' && (!value || value.length === 0)) {
        callback(new Error(this.$t('reservation.selectDaysOfWeek')))
      } else {
        callback()
      }
    }

    const validateDaysOfMonth = (rule, value, callback) => {
      if (this.form.patternType === 'monthly' && (!value || value.length === 0)) {
        callback(new Error(this.$t('reservation.selectDaysOfMonth')))
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
      loading: false,
      submitting: false,
      equipment: null,
      timeConflict: false,
      successDialogVisible: false,
      recurringReservationId: null,
      reservationCode: '',
      hasConflicts: false,
      conflictDates: [],
      totalPlanned: 0,
      createdCount: 0,
      skippedCount: 0,

      form: {
        patternType: 'weekly',
        daysOfWeek: [],
        daysOfMonth: [],
        dateRange: [],
        startTime: '',
        endTime: '',
        userName: '',
        userDepartment: '',
        userContact: '',
        userEmail: '',
        purpose: ''
      },

      rules: {
        patternType: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' }
        ],
        daysOfWeek: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateDaysOfWeek, trigger: 'change' }
        ],
        daysOfMonth: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateDaysOfMonth, trigger: 'change' }
        ],
        dateRange: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateDateRange, trigger: 'change' }
        ],
        startTime: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateTime, trigger: 'change' }
        ],
        endTime: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateTime, trigger: 'change' }
        ],
        userName: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 2, max: 50, message: this.$t('common.lengthLimit', { min: 2, max: 50 }), trigger: 'blur' }
        ],
        userDepartment: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 2, max: 50, message: this.$t('common.lengthLimit', { min: 2, max: 50 }), trigger: 'blur' }
        ],
        userContact: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 5, max: 50, message: this.$t('common.lengthLimit', { min: 5, max: 50 }), trigger: 'blur' }
        ],
        userEmail: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { validator: validateEmail, trigger: 'blur' }
        ],
        purpose: [
          { max: 500, message: this.$t('common.lengthLimit', { max: 500 }), trigger: 'blur' }
        ]
      },

      dateRangePickerOptions: {
        disabledDate(time) {
          return time.getTime() < Date.now() - 8.64e7 // 不能选择过去的日期
        }
      }
    }
  },

  created() {
    this.fetchEquipment()
  },

  methods: {
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
        this.equipment = null
      } finally {
        this.loading = false
      }
    },

    async checkTimeAvailability() {
      if (!this.form.dateRange || !this.form.dateRange[0] || !this.form.dateRange[1] || !this.form.startTime || !this.form.endTime) {
        this.timeConflict = false
        return
      }

      const start = new Date(this.form.startTime)
      const end = new Date(this.form.endTime)
      if (start >= end) {
        this.timeConflict = true
        return
      }

      // 对于循环预约，我们只检查第一天的可用性作为示例
      try {
        const equipmentId = this.equipment.id
        const startDate = this.formatDate(this.form.dateRange[0])
        const endDate = this.formatDate(this.form.dateRange[0]) // 只检查第一天

        const response = await equipmentApi.getAvailability(equipmentId, startDate, endDate)

        // 检查是否有冲突
        this.timeConflict = response.data.available.includes(false)
        
        if (this.timeConflict) {
          this.$message.warning(this.$t('reservation.timeConflictWarning'))
        }
      } catch (error) {
        console.error('Failed to check availability:', error)
        this.$message.error(this.$t('common.error'))
        this.timeConflict = true
      }
    },

    submitForm() {
      this.$refs.reservationForm.validate(async (valid) => {
        if (!valid) {
          return false
        }

        if (this.timeConflict) {
          this.$message.error(this.$t('reservation.timeConflict'))
          return false
        }

        this.submitting = true

        try {
          // 准备开始日期和结束日期
          const startDate = this.formatDate(this.form.dateRange[0])
          const endDate = this.formatDate(this.form.dateRange[1])
          
          // 准备开始时间和结束时间
          const startTime = this.formatTime(this.form.startTime)
          const endTime = this.formatTime(this.form.endTime)

          const recurringReservationData = {
            equipment_id: this.equipment.id,
            pattern_type: this.form.patternType,
            days_of_week: this.form.patternType === 'weekly' ? this.form.daysOfWeek : undefined,
            days_of_month: this.form.patternType === 'monthly' ? this.form.daysOfMonth : undefined,
            start_date: startDate,
            end_date: endDate,
            start_time: startTime,
            end_time: endTime,
            user_name: this.form.userName,
            user_department: this.form.userDepartment,
            user_contact: this.form.userContact,
            user_email: this.form.userEmail || undefined,
            purpose: this.form.purpose || undefined,
            lang: this.$i18n.locale
          }

          const response = await recurringReservationApi.createRecurringReservation(recurringReservationData)

          if (response.data.success) {
            // 保存循环预约ID
            this.recurringReservationId = response.data.data.id
            
            // 保存预约码
            this.reservationCode = response.data.data.reservation_code || ''
            
            // 处理冲突信息
            if (response.data.data.conflict_dates && response.data.data.conflict_dates.length > 0) {
              this.hasConflicts = true
              this.conflictDates = response.data.data.conflict_dates
              this.totalPlanned = response.data.data.total_planned || 0
              this.createdCount = response.data.data.created_count || 0
              this.skippedCount = this.totalPlanned - this.createdCount
            } else {
              this.hasConflicts = false
            }
            
            console.log("获取的循环预约信息:", response.data.data)
            console.log("设置的预约码:", this.reservationCode)
            
            // 显示成功对话框
            this.successDialogVisible = true
          } else {
            this.$message.error(response.data.message || this.$t('common.error'))
          }
        } catch (error) {
          console.error('Failed to create recurring reservation:', error)
          this.$message.error(this.$t('common.error'))
        } finally {
          this.submitting = false
        }
      })
    },

    resetForm() {
      this.$refs.reservationForm.resetFields()
      this.timeConflict = false
    },

    viewEquipment() {
      this.$router.push(`/equipment/${this.equipment.id}`)
    },
    
    // 查看循环预约详情
    viewRecurringReservation() {
      if (this.recurringReservationId) {
        console.log("跳转到循环预约详情页，ID:", this.recurringReservationId);
        this.$router.push(`/recurring-reservation/${this.recurringReservationId}`);
      } else {
        console.error("错误: 循环预约ID为空，无法查看详情");
        this.$message.error(this.$t('reservation.reservationNotFound'));
        
        // 关闭成功对话框
        this.closeSuccessDialog();
      }
    },

    // 返回单次预约表单
    backToSingleReservation() {
      this.$router.push(`/equipment/${this.equipment.id}/reserve`)
    },

    closeSuccessDialog() {
      this.successDialogVisible = false
      this.resetForm()
      this.$router.push('/equipment')
    },

    // 格式化日期为 YYYY-MM-DD
    formatDate(date) {
      if (!date) return ''
      
      const d = new Date(date)
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      
      return `${year}-${month}-${day}`
    },

    // 格式化时间为 HH:MM
    formatTime(time) {
      if (!time) return ''
      
      const d = new Date(time)
      const hours = String(d.getHours()).padStart(2, '0')
      const minutes = String(d.getMinutes()).padStart(2, '0')
      
      return `${hours}:${minutes}`
    },

    // 获取模式类型文本
    getPatternTypeText() {
      const types = {
        'daily': this.$t('reservation.daily'),
        'weekly': this.$t('reservation.weekly'),
        'monthly': this.$t('reservation.monthly')
      }
      return types[this.form.patternType] || this.form.patternType
    },

    // 获取星期几文本
    getWeekdaysText() {
      if (!this.form.daysOfWeek || this.form.daysOfWeek.length === 0) return ''
      
      const weekdays = [
        this.$t('reservation.sunday'),
        this.$t('reservation.monday'),
        this.$t('reservation.tuesday'),
        this.$t('reservation.wednesday'),
        this.$t('reservation.thursday'),
        this.$t('reservation.friday'),
        this.$t('reservation.saturday')
      ]
      
      return this.form.daysOfWeek.map(day => weekdays[day]).join(', ')
    },

    // 获取每月几号文本
    getDaysOfMonthText() {
      if (!this.form.daysOfMonth || this.form.daysOfMonth.length === 0) return ''
      
      return this.form.daysOfMonth.sort((a, b) => a - b).join(', ')
    },

    // 获取完整的图片URL
    getFullImageUrl(url) {
      if (!url) return '';

      // 如果已经是完整URL，直接返回
      if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
      }

      // 如果是相对路径，添加基础URL
      if (url.startsWith('/')) {
        return this.baseUrl + url;
      }

      // 其他情况，添加基础URL和斜杠
      return this.baseUrl + '/' + url;
    }
  }
}
</script>

<style scoped>
.recurring-reservation-form {
  max-width: 800px;
  margin: 0 auto;
}

.back-link {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.back-to-single {
  margin-left: 10px;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #303133;
}

.equipment-card {
  margin-bottom: 20px;
}

.equipment-info {
  display: flex;
  align-items: center;
}

.equipment-image-container {
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin-right: 20px;
}

.equipment-image {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
}

.equipment-details {
  flex: 1;
}

.equipment-name {
  margin: 0 0 5px;
  font-size: 18px;
  color: #303133;
}

.equipment-category {
  margin: 0 0 10px;
  font-size: 14px;
  color: #909399;
}

.equipment-location {
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.form-card {
  margin-bottom: 20px;
}

.time-conflict-warning {
  margin-bottom: 20px;
}

.loading-container {
  padding: 40px 0;
}

.error-container {
  padding: 40px 0;
  text-align: center;
}

.success-content {
  text-align: center;
}

.success-icon {
  font-size: 72px;
  color: #67C23A;
  margin-bottom: 20px;
}

.success-message {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
}

.reservation-code-container {
  text-align: center;
  margin: 20px 0;
  padding: 15px;
  background-color: #f8f8f8;
  border-radius: 4px;
  border: 1px dashed #dcdfe6;
}

.reservation-code {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  letter-spacing: 2px;
}

.reservation-summary {
  text-align: left;
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.reservation-summary p {
  margin: 5px 0;
}

.reservation-tip {
  color: #909399;
  margin-bottom: 20px;
}

.dialog-footer {
  margin-top: 20px;
}

.conflict-info {
  margin-bottom: 20px;
}

.conflict-details {
  margin-bottom: 10px;
}

.conflict-dates {
  margin-top: 10px;
}

.conflict-date-tag {
  margin-right: 5px;
}

@media (max-width: 768px) {
  .equipment-info {
    flex-direction: column;
    align-items: flex-start;
  }

  .equipment-image-container {
    margin-right: 0;
    margin-bottom: 20px;
  }
}
</style>
