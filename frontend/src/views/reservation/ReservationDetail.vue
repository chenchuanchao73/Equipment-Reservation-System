<template>
  <div class="reservation-detail">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="!reservation" class="error-container">
      <el-result
        icon="error"
        :title="$t('error.errorMessage')"
        :sub-title="$t('reservation.reservationNotFound')"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/reservation/query')">
            {{ $t('reservation.query') }}
          </el-button>
        </template>
      </el-result>
    </div>

    <div v-else>
      <!-- 返回按钮 -->
      <div class="back-link">
        <el-button icon="el-icon-arrow-left" @click="goBack">
          {{ $t('common.back') }}
        </el-button>
      </div>

      <h1 class="page-title">{{ $t('reservation.detail') }}</h1>

      <!-- 预定状态 -->
      <div class="reservation-status-card" :class="getStatusClass(reservation.status)">
        <div class="status-icon">
          <i :class="getStatusIcon(reservation.status)"></i>
        </div>
        <div class="status-text">
          <h2>{{ getStatusText(reservation.status) }}</h2>
          <p>{{ $t('reservation.code') }}: {{ reservation.reservation_code }}</p>
        </div>
      </div>

      <!-- 预定详情 -->
      <el-card shadow="never" class="detail-card">
        <div slot="header">
          <span>{{ $t('reservation.detail') }}</span>
        </div>

        <el-descriptions :column="1" border>
          <el-descriptions-item :label="$t('reservation.equipmentName')">
            {{ reservation.equipment_name }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('equipment.category')" v-if="reservation.equipment_category">
            {{ reservation.equipment_category }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('equipment.location')" v-if="reservation.equipment_location">
            {{ reservation.equipment_location }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.startTime')">
            {{ formatDateTime(reservation.start_datetime) }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.endTime')">
            {{ formatDateTime(reservation.end_datetime) }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.purpose')" v-if="reservation.purpose">
            {{ reservation.purpose }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 用户信息 -->
      <el-card shadow="never" class="user-card">
        <div slot="header">
          <span>{{ $t('common.userInfo') }}</span>
        </div>

        <el-descriptions :column="1" border>
          <el-descriptions-item :label="$t('reservation.userName')">
            {{ reservation.user_name }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userDepartment')">
            {{ reservation.user_department }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userContact')">
            {{ reservation.user_contact }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userEmail')" v-if="reservation.user_email">
            {{ reservation.user_email }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <!-- 已确认状态的预约显示取消按钮 -->
        <el-button v-if="canCancel" type="danger" @click="showCancelDialog" icon="el-icon-close">
          {{ $t('reservation.cancelReservation') }}
        </el-button>

        <!-- 使用中状态的预约显示提前归还按钮 -->
        <el-button v-if="canReturn" type="primary" @click="showReturnDialog" icon="el-icon-time">
          {{ $t('reservation.earlyReturn') }}
        </el-button>
      </div>

      <!-- 取消预定对话框 -->
      <el-dialog
        :title="$t('reservation.cancelConfirmation')"
        :visible.sync="cancelDialogVisible"
        width="400px"
      >
        <p>{{ $t('reservation.cancelConfirmationMessage') }}</p>
        <div slot="footer" class="dialog-footer">
          <el-button @click="cancelDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="danger" @click="cancelReservation" :loading="cancelling">
            {{ $t('common.confirm') }}
          </el-button>
        </div>
      </el-dialog>

      <!-- 提前归还对话框 -->
      <el-dialog
        :title="$t('reservation.earlyReturn')"
        :visible.sync="returnDialogVisible"
        width="400px"
      >
        <p>{{ $t('reservation.confirmEarlyReturn') }}</p>
        <div slot="footer" class="dialog-footer">
          <el-button @click="returnDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="returnEquipment" :loading="returning">
            {{ $t('common.confirm') }}
          </el-button>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { reservationApi } from '@/api'
import { formatDate } from '@/utils/date'

export default {
  name: 'ReservationDetail',

  props: {
    isAdmin: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      loading: true,
      reservation: null,
      cancelDialogVisible: false,
      cancelling: false,
      returnDialogVisible: false,
      returning: false
    }
  },

  computed: {
    // 是否可以取消预定
    canCancel() {
      if (!this.reservation) return false

      // 只有确认状态的预定可以取消
      return this.reservation.status === 'confirmed'
    },

    // 是否可以提前归还
    canReturn() {
      if (!this.reservation) return false

      // 只有使用中状态的预定可以提前归还
      return this.reservation.status === 'in_use'
    }
  },

  created() {
    this.fetchReservation()
  },

  methods: {
    // 获取预定详情
    async fetchReservation() {
      this.loading = true
      try {
        // 检查是否是通过预约序号查看
        const reservationNumber = this.$route.params.number
        const code = this.$route.params.code
        let response

        if (reservationNumber) {
          console.log('通过预约序号查看预约详情:', reservationNumber)

          // 从URL中获取预约码（如果有）
          const codeFromQuery = this.$route.query.code

          // 如果URL中有预约码，使用预约码和预约序号查询
          if (codeFromQuery) {
            console.log('使用预约码和预约序号查询:', codeFromQuery, reservationNumber)

            // 直接使用预约序号作为参数，不要包装在对象中
            console.log('直接使用预约序号作为参数:', reservationNumber);

            // 使用预约码和预约序号查询
            response = await reservationApi.getReservationByCode(codeFromQuery, reservationNumber)
          } else {
            // 如果URL中没有预约码，直接使用预约序号查询
            console.log('直接使用预约序号查询:', reservationNumber)

            // 从localStorage中获取预约码（如果有）
            const savedCode = localStorage.getItem('current_reservation_code')

            if (savedCode) {
              console.log('从localStorage中获取到预约码:', savedCode)

              // 直接使用预约序号作为参数，不要包装在对象中
              console.log('使用保存的预约码和预约序号查询:', savedCode, reservationNumber);

              // 使用预约码和预约序号查询
              response = await reservationApi.getReservationByCode(savedCode, reservationNumber)
            } else {
              // 如果没有预约码，直接使用预约序号查询
              response = await reservationApi.getReservationByCode(reservationNumber)
            }
          }
        } else if (this.isAdmin) {
          // 管理员查询
          response = await reservationApi.getReservation(code)
        } else {
          // 用户查询
          response = await reservationApi.getReservationByCode(code)
        }

        if (response.data.success) {
          this.reservation = response.data.data
          console.log('获取到预约详情:', this.reservation)
        } else {
          this.$message.error(response.data.message || this.$t('reservation.notFound'))
          this.reservation = null
        }
      } catch (error) {
        console.error('Failed to fetch reservation:', error)
        this.$message.error(this.$t('common.error'))
        this.reservation = null
      } finally {
        this.loading = false
      }
    },

    // 返回上一页
    goBack() {
      console.log('ReservationDetail.goBack() - 当前路由参数:', this.$route.query)

      // 直接返回到个人预约管理页面
      console.log('ReservationDetail.goBack() - 直接返回个人预约管理页面')

      // 使用Vue Router的push方法
      this.$router.push('/reservation/query')
    },

    // 格式化日期时间
    formatDateTime(datetime) {
      return formatDate(datetime, 'YYYY-MM-DD HH:mm:ss', false) // 设置toBeijingTime为false，不进行时区转换
    },

    // 获取状态类名
    getStatusClass(status) {
      const statusMap = {
        confirmed: 'status-confirmed',
        cancelled: 'status-cancelled',
        completed: 'status-completed',
        in_use: 'status-in-use',
        expired: 'status-expired'
      }
      return statusMap[status] || 'status-unknown'
    },

    // 获取状态图标
    getStatusIcon(status) {
      const iconMap = {
        confirmed: 'el-icon-check',
        cancelled: 'el-icon-close',
        completed: 'el-icon-success',
        in_use: 'el-icon-time',
        expired: 'el-icon-warning'
      }
      return iconMap[status] || 'el-icon-question'
    },

    // 获取状态文本
    getStatusText(status) {
      const statusMap = {
        confirmed: this.$t('reservation.statusConfirmed'),
        cancelled: this.$t('reservation.statusCancelled'),
        completed: this.$t('reservation.statusCompleted'),
        in_use: this.$t('reservation.statusInUse'),
        expired: this.$t('reservation.statusExpired')
      }
      return statusMap[status] || this.$t('reservation.statusUnknown')
    },



    // 显示取消对话框
    showCancelDialog() {
      this.cancelDialogVisible = true
    },

    // 显示提前归还对话框
    showReturnDialog() {
      this.returnDialogVisible = true
    },

    // 取消预定
    async cancelReservation() {
      this.cancelling = true
      try {
        const response = await reservationApi.cancelReservation(
          this.reservation.reservation_code,
          { reservation_number: this.reservation.reservation_number }
        )

        if (response.data.success) {
          this.$message.success(this.$t('reservation.cancelSuccess'))
          this.cancelDialogVisible = false
          // 重新获取预定信息
          await this.fetchReservation()
        } else {
          this.$message.error(response.data.message || this.$t('reservation.cancelFailed'))
        }
      } catch (error) {
        console.error('Failed to cancel reservation:', error)
        this.$message.error(this.$t('reservation.cancelFailed'))
      } finally {
        this.cancelling = false
      }
    },

    // 提前归还设备
    async returnEquipment() {
      this.returning = true
      try {
        // 这里应该调用提前归还API，但目前后端可能没有实现
        // 暂时使用取消预约API代替
        const response = await reservationApi.cancelReservation(
          this.reservation.reservation_code,
          {
            reservation_number: this.reservation.reservation_number,
            is_early_return: true
          }
        )

        if (response.data.success) {
          this.$message.success(this.$t('reservation.returnSuccess'))
          this.returnDialogVisible = false
          // 重新获取预定信息
          await this.fetchReservation()
        } else {
          this.$message.error(response.data.message || this.$t('reservation.returnFailed'))
        }
      } catch (error) {
        console.error('Failed to return equipment:', error)
        this.$message.error(this.$t('reservation.returnFailed'))
      } finally {
        this.returning = false
      }
    }
  }
}
</script>

<style scoped>
.reservation-detail {
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
  padding: 40px 0;
  text-align: center;
}

.error-container {
  padding: 40px 0;
}

.reservation-status-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  color: white;
}

.status-icon {
  font-size: 40px;
  margin-right: 20px;
}

.status-text h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
}

.status-text p {
  margin: 0;
  font-size: 16px;
}

.status-confirmed {
  background-color: #67c23a;
}

.status-cancelled {
  background-color: #f56c6c;
}

.status-completed {
  background-color: #909399;
}

.status-in-use {
  background-color: #409eff;
}

.status-expired {
  background-color: #e6a23c;
}

.status-unknown {
  background-color: #909399;
}

.detail-card, .user-card {
  margin-bottom: 20px;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}
</style>
