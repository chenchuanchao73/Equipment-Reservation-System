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

          <!-- 预定码单独显示在最上方 -->
          <div class="reservation-code-container">
            <span class="reservation-code">{{ reservationCode || '无预约码' }}</span>
          </div>

          <div class="reservation-info-box">
            <div class="reservation-info-item">
              <span class="info-label">{{ $t('reservation.equipmentName') }}:</span>
              <span>{{ reservationInfo.equipment_name }}</span>
            </div>

            <div class="reservation-info-item">
              <span class="info-label">{{ $t('reservation.startTime') }}:</span>
              <span>{{ formatDateTimeString(reservationInfo.start_datetime) }}</span>
            </div>

            <div class="reservation-info-item">
              <span class="info-label">{{ $t('reservation.endTime') }}:</span>
              <span>{{ formatDateTimeString(reservationInfo.end_datetime) }}</span>
            </div>

            <div class="reservation-info-item">
              <span class="info-label">{{ $t('reservation.userName') }}:</span>
              <span>{{ reservationInfo.user_name }}</span>
            </div>
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
      reservationNumber: '',
      reservationInfo: {
        equipment_name: '',
        start_datetime: null,
        end_datetime: null,
        user_name: '',
        reservation_number: ''
      },
      reservationType: 'single',
      qrcodeUrl: null, // 二维码功能已移除

      // 表单数据
      form: {
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
        reservationType: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' }
        ],

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
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' },
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
          // 如果没有选择开始时间，禁用过去的日期
          if (!this.form.startDateTime) {
            return time.getTime() < Date.now() - 8.64e7;
          }

          // 获取选择日期的年月日部分（不含时间）
          const selectedDate = new Date(time.getFullYear(), time.getMonth(), time.getDate());
          const startDate = new Date(
            this.form.startDateTime.getFullYear(),
            this.form.startDateTime.getMonth(),
            this.form.startDateTime.getDate()
          );

          // 如果日期早于开始日期，则禁用
          if (selectedDate < startDate) {
            return true;
          }

          // 如果是同一天，检查一下当前是否为00:00（一天的开始）
          // 如果是00:00，可以选择，因为用户可以设置晚于开始时间的结束时间
          // 如果不是00:00，说明这是日期选择器显示的时间，不是用户最终选择的时间，可以允许选择
          if (selectedDate.getTime() === startDate.getTime()) {
            return false; // 同一天也可以选择
          }

          return false; // 允许选择晚于开始日期的所有日期
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

      // 添加更严格的验证
      if (this.form.startDateTime >= this.form.endDateTime) {
        this.$message.warning(this.$t('reservation.invalidTime'))
        this.timeConflict = true
        return
      }

      try {
        const equipmentId = this.equipment.id
        const startDate = this.formatDateTime(this.form.startDateTime)
        const endDate = this.formatDateTime(this.form.endDateTime)

        // 添加日志
        console.log('检查时间可用性:', {
          equipmentId,
          startDate,
          endDate,
          startDateTime: this.form.startDateTime,
          endDateTime: this.form.endDateTime
        })

        const response = await equipmentApi.getAvailability(equipmentId, startDate, endDate)

        // 添加日志
        console.log('可用性检查结果:', response.data)

        // 检查是否有冲突 - 处理新的API响应格式
        if (response.data.specific_time_check) {
          // 如果是具体时间段检查
          console.log('具体时间段检查结果:', response.data.available)
          this.timeConflict = response.data.available.includes(false)
        } else {
          // 如果是按日期检查
          console.log('按日期检查结果:', response.data.available)
          this.timeConflict = response.data.available.includes(false)
        }

        if (this.timeConflict) {
          console.log('检测到时间冲突:', response.data.available)
          this.$message.warning(this.$t('reservation.timeConflict'))
        } else {
          console.log('时间段可用')
        }
      } catch (error) {
        console.error('Failed to check availability:', error)
        this.timeConflict = true
        this.$message.error(this.$t('common.error'))
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

      // 确保date是一个有效的Date对象
      if (!(date instanceof Date) || isNaN(date.getTime())) {
        console.error('无效的日期对象:', date)
        return null
      }

      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')

      const formattedDateTime = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
      console.log('格式化日期时间:', date, '->', formattedDateTime)

      return formattedDateTime
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

          console.log("发送预约数据:", JSON.stringify(reservationData));
          const response = await reservationApi.createReservation(reservationData);

          // 详细记录API响应
          console.log("API响应状态:", response.status);
          console.log("API响应数据:", JSON.stringify(response.data));

          if (response.data && response.data.success) {
            // 检查响应数据结构
            console.log("API响应成功，详细信息:", JSON.stringify(response.data, null, 2));

            const responseData = response.data.data;
            console.log("提取的响应数据:", JSON.stringify(responseData, null, 2));

            // 观察后端响应模型字段，特别检查reservation_number字段
            console.log("获取的预约号信息:");
            console.log("- reservation_code:", responseData.reservation_code);
            console.log("- reservation_number:", responseData.reservation_number);

            // 从后端模型中我们知道reservation_number是唯一的预约标识
            // reservation_code是用于关联相同循环预约的
            // 对于查看详情，我们应该使用reservation_number

            // 设置预定码和预约序号
            this.reservationCode = responseData.reservation_code || '';
            this.reservationNumber = responseData.reservation_number || '';

            console.log("设置的预约序号:", this.reservationNumber);
            console.log("设置的预定码:", this.reservationCode);

                          // 检查预定码是否设置成功
              if (!this.reservationCode) {
                console.error("警告: 预定码为空! API响应数据:", JSON.stringify(response.data));
              }

            // 确保所有字段都被正确赋值
            this.reservationInfo = {
              equipment_name: responseData.equipment_name || this.equipment.name,
              start_datetime: responseData.start_datetime || this.formatDateTime(this.form.startDateTime),
              end_datetime: responseData.end_datetime || this.formatDateTime(this.form.endDateTime),
              user_name: responseData.user_name || this.form.userName,
              reservation_number: this.reservationNumber // 添加预约序号到预约信息中
            }

            console.log("设置的预约信息:", JSON.stringify(this.reservationInfo));

            // 显示成功对话框
            this.successDialogVisible = true
            this.$refs.reservationForm.resetFields()
          } else {
            console.error("API响应失败:", response.data.message || "未知错误");
            this.$message.error(response.data.message || this.$t('reservation.createFailed'))
          }
        } catch (error) {
          console.error('创建预约失败，错误详情:', error)
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
    // 记录当前预约号
    console.log("查看预定详情，当前预约号:", this.reservationNumber);

    // 确保预约号存在
    if (!this.reservationNumber) {
      console.error("错误: 预约号为空，无法查看预定详情");
      this.$message.error(this.$t('reservation.reservationNotFound'));
      return;
    }

      // 添加详细的日志信息
      console.log("准备跳转到预定详情页面");
      console.log("跳转URL:", `/reservation/number/${this.reservationNumber}`);
      console.log("完整状态:", {
        reservationCode: this.reservationCode,
        reservationNumber: this.reservationNumber,
        reservationInfo: this.reservationInfo,
        dialogVisible: this.successDialogVisible
      });

      // 跳转到预定详情页面，使用reservation_number查询
      this.$router.push({
        path: `/reservation/number/${this.reservationNumber}`,
        query: { _t: new Date().getTime() } // 添加时间戳防止缓存
      });
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
    },

    // 格式化显示日期时间
    formatDisplayDateTime(date) {
      if (!date) return '';
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    },

    // 格式化日期时间字符串
    formatDateTimeString(dateTimeStr) {
      if (!dateTimeStr) return '';

      // 假设输入格式为 YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DDTHH:MM:SS
      try {
        // 处理ISO格式的日期时间
        if (dateTimeStr.includes('T')) {
          const date = new Date(dateTimeStr);
          if (isNaN(date.getTime())) {
            return dateTimeStr.substring(0, 16).replace('T', ' '); // 简单地替换T为空格
          }
          return this.formatDisplayDateTime(date);
        }

        // 处理标准格式的日期时间
        return dateTimeStr.substring(0, 16); // 返回 YYYY-MM-DD HH:MM 部分
      } catch (e) {
        console.error('日期格式化错误:', e);
        return dateTimeStr; // 出错时返回原始字符串
      }
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
  /* 不设置颜色，使用全局CSS中的颜色 */
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
  color: #303133; /* 亮色主题下的颜色 */
}

.equipment-category {
  margin: 0 0 10px 0;
  color: #606266; /* 亮色主题下的颜色 */
}

.equipment-location {
  margin-bottom: 10px;
  color: #606266; /* 亮色主题下的颜色 */
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
  color: #303133; /* 亮色主题下的颜色 */
}

.reservation-info-box {
  background-color: #f5f7fa;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
  text-align: left;
}

.reservation-info-item {
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
}

.info-label {
  font-weight: bold;
  margin-right: 8px;
  min-width: 80px;
  flex-shrink: 0;
  text-align: right;
}

.reservation-code {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  background-color: #ecf5ff;
  padding: 10px 15px;
  border-radius: 4px;
  border: 2px solid #b3d8ff;
  letter-spacing: 2px;
  text-shadow: 0 0 1px rgba(0,0,0,0.2);
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  display: block;
  margin: 10px auto;
  text-align: center;
  max-width: 90%;
}

.reservation-code-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px dashed #e6e6e6;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.reservation-tip {
  margin-bottom: 20px;
  color: #909399; /* 亮色主题下的颜色 */
}

.dialog-footer {
  margin-top: 20px;
}

.reservation-code-container {
  margin-bottom: 20px;
}
</style>
