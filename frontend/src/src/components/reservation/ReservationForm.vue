<template>
  <div class="reservation-form">
    <el-form 
      ref="form" 
      :model="form" 
      :rules="rules" 
      label-width="100px"
      label-position="top"
    >
      <!-- 设备信息 -->
      <div class="equipment-info" v-if="equipment">
        <h3>{{ equipment.name }}</h3>
        <div class="equipment-meta">
          <span>
            <i class="el-icon-collection-tag"></i> {{ equipment.category }}
          </span>
          <span>
            <i class="el-icon-location-outline"></i> {{ equipment.location }}
          </span>
        </div>
      </div>
      
      <!-- 时间选择 -->
      <el-form-item :label="$t('reservation.selectDate')" prop="date">
        <el-date-picker
          v-model="form.date"
          type="date"
          :placeholder="$t('reservation.selectDate')"
          :picker-options="datePickerOptions"
          style="width: 100%"
          @change="handleDateChange"
        ></el-date-picker>
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item :label="$t('reservation.startTime')" prop="startTime">
            <el-time-picker
              v-model="form.startTime"
              :placeholder="$t('reservation.selectTime')"
              :picker-options="startTimeOptions"
              style="width: 100%"
              @change="validateTimeRange"
            ></el-time-picker>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="$t('reservation.endTime')" prop="endTime">
            <el-time-picker
              v-model="form.endTime"
              :placeholder="$t('reservation.selectTime')"
              :picker-options="endTimeOptions"
              style="width: 100%"
              @change="validateTimeRange"
            ></el-time-picker>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 用户信息 -->
      <el-form-item :label="$t('reservation.userName')" prop="userName">
        <el-input v-model="form.userName"></el-input>
      </el-form-item>
      
      <el-form-item :label="$t('reservation.userDepartment')" prop="userDepartment">
        <el-input v-model="form.userDepartment"></el-input>
      </el-form-item>
      
      <el-form-item :label="$t('reservation.userContact')" prop="userContact">
        <el-input v-model="form.userContact"></el-input>
      </el-form-item>
      
      <el-form-item :label="$t('reservation.userEmail')" prop="userEmail">
        <el-input v-model="form.userEmail"></el-input>
      </el-form-item>
      
      <el-form-item :label="$t('reservation.purpose')" prop="purpose">
        <el-input 
          type="textarea" 
          v-model="form.purpose" 
          :rows="3"
        ></el-input>
      </el-form-item>
      
      <!-- 提交按钮 -->
      <el-form-item>
        <el-button 
          type="primary" 
          @click="submitForm" 
          :loading="loading"
        >
          {{ $t('reservation.createReservation') }}
        </el-button>
        <el-button @click="resetForm">
          {{ $t('common.reset') }}
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 预定成功对话框 -->
    <el-dialog
      :title="$t('reservation.createSuccess')"
      :visible.sync="dialogVisible"
      width="30%"
      :before-close="handleDialogClose"
    >
      <div class="success-info">
        <i class="el-icon-success success-icon"></i>
        <p>{{ $t('reservation.saveReservationCode') }}</p>
        <div class="reservation-code">{{ reservationCode }}</div>
        <p class="code-tip">{{ $t('reservation.reservationCodeTip') }}</p>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="handleDialogClose">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="viewReservation">
          {{ $t('reservation.detail') }}
        </el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import { reservationApi } from '@/api'
import { formatDate, isTimeOverlap } from '@/utils/date'

export default {
  name: 'ReservationForm',
  
  props: {
    equipment: {
      type: Object,
      required: true
    }
  },
  
  data() {
    // 邮箱验证规则
    const validateEmail = (rule, value, callback) => {
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        callback(new Error(this.$t('reservation.emailFormat')))
      } else {
        callback()
      }
    }
    
    // 时间范围验证规则
    const validateTimeRange = (rule, value, callback) => {
      if (this.form.startTime && this.form.endTime) {
        if (this.form.startTime >= this.form.endTime) {
          callback(new Error(this.$t('reservation.invalidTime')))
        } else {
          callback()
        }
      } else {
        callback()
      }
    }
    
    return {
      form: {
        date: null,
        startTime: null,
        endTime: null,
        userName: '',
        userDepartment: '',
        userContact: '',
        userEmail: '',
        purpose: ''
      },
      rules: {
        date: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' }
        ],
        startTime: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateTimeRange, trigger: 'change' }
        ],
        endTime: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' },
          { validator: validateTimeRange, trigger: 'change' }
        ],
        userName: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' }
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
      datePickerOptions: {
        disabledDate: this.disabledDate
      },
      startTimeOptions: {
        selectableRange: '08:00:00 - 20:00:00'
      },
      endTimeOptions: {
        selectableRange: '08:00:00 - 20:00:00'
      },
      loading: false,
      dialogVisible: false,
      reservationCode: '',
      reservations: [] // 已有的预定
    }
  },
  
  methods: {
    ...mapActions(['fetchEquipmentAvailability']),
    
    // 禁用日期（今天之前的日期不可选）
    disabledDate(time) {
      return time.getTime() < Date.now() - 8.64e7 // 8.64e7是一天的毫秒数
    },
    
    // 日期变更时获取该日期的预定情况
    async handleDateChange(date) {
      if (!date) return
      
      try {
        this.loading = true
        
        // 格式化日期
        const formattedDate = formatDate(date, 'YYYY-MM-DD')
        
        // 获取设备在该日期的预定情况
        const response = await reservationApi.getEquipmentAvailability(
          this.equipment.id, 
          { date: formattedDate }
        )
        
        this.reservations = response.reservations || []
      } catch (error) {
        console.error('获取设备可用性失败:', error)
        this.$message.error(this.$t('error.serverError'))
      } finally {
        this.loading = false
      }
    },
    
    // 验证时间范围
    validateTimeRange() {
      if (this.form.startTime && this.form.endTime) {
        if (this.form.startTime >= this.form.endTime) {
          this.$message.warning(this.$t('reservation.invalidTime'))
          return false
        }
        
        // 检查是否与已有预定冲突
        if (this.checkTimeConflict()) {
          this.$message.warning(this.$t('reservation.timeConflict'))
          return false
        }
      }
      
      return true
    },
    
    // 检查时间冲突
    checkTimeConflict() {
      if (!this.form.date || !this.form.startTime || !this.form.endTime) {
        return false
      }
      
      // 组合日期和时间
      const startDate = new Date(this.form.date)
      const endDate = new Date(this.form.date)
      
      startDate.setHours(
        this.form.startTime.getHours(),
        this.form.startTime.getMinutes(),
        0
      )
      
      endDate.setHours(
        this.form.endTime.getHours(),
        this.form.endTime.getMinutes(),
        0
      )
      
      // 检查是否与已有预定冲突
      for (const reservation of this.reservations) {
        if (reservation.status === 'cancelled') continue
        
        const reserveStart = new Date(reservation.start_time)
        const reserveEnd = new Date(reservation.end_time)
        
        if (isTimeOverlap(startDate, endDate, reserveStart, reserveEnd)) {
          return true
        }
      }
      
      return false
    },
    
    // 提交表单
    submitForm() {
      this.$refs.form.validate(async valid => {
        if (!valid) return
        
        // 验证时间范围
        if (!this.validateTimeRange()) return
        
        try {
          this.loading = true
          
          // 组合日期和时间
          const startDate = new Date(this.form.date)
          const endDate = new Date(this.form.date)
          
          startDate.setHours(
            this.form.startTime.getHours(),
            this.form.startTime.getMinutes(),
            0
          )
          
          endDate.setHours(
            this.form.endTime.getHours(),
            this.form.endTime.getMinutes(),
            0
          )
          
          // 构建预定数据
          const reservationData = {
            equipment_id: this.equipment.id,
            start_time: startDate.toISOString(),
            end_time: endDate.toISOString(),
            user_name: this.form.userName,
            user_department: this.form.userDepartment,
            user_contact: this.form.userContact,
            user_email: this.form.userEmail || null,
            purpose: this.form.purpose || null
          }
          
          // 创建预定
          const response = await reservationApi.createReservation(reservationData)
          
          // 显示成功对话框
          this.reservationCode = response.code
          this.dialogVisible = true
          
          // 重置表单
          this.resetForm()
        } catch (error) {
          console.error('创建预定失败:', error)
          this.$message.error(this.$t('error.serverError'))
        } finally {
          this.loading = false
        }
      })
    },
    
    // 重置表单
    resetForm() {
      this.$refs.form.resetFields()
    },
    
    // 关闭对话框
    handleDialogClose() {
      this.dialogVisible = false
    },
    
    // 查看预定详情
    viewReservation() {
      this.dialogVisible = false
      this.$router.push(`/reservation/${this.reservationCode}`)
    }
  },
  
  created() {
    // 如果有设备ID，则获取设备详情
    if (this.equipment && this.equipment.id) {
      // 设置默认日期为今天
      this.form.date = new Date()
      
      // 获取设备可用性
      this.handleDateChange(this.form.date)
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

.equipment-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.equipment-info h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 18px;
}

.equipment-meta {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #606266;
}

.success-info {
  text-align: center;
  padding: 20px 0;
}

.success-icon {
  font-size: 60px;
  color: #67C23A;
  margin-bottom: 20px;
}

.reservation-code {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin: 15px 0;
  padding: 10px;
  background-color: #ecf5ff;
  border-radius: 4px;
}

.code-tip {
  font-size: 14px;
  color: #909399;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .reservation-form {
    padding: 10px;
  }
  
  .equipment-meta {
    flex-direction: column;
  }
  
  .equipment-meta span {
    margin-bottom: 5px;
  }
}
</style>
