<template>
  <el-card class="reservation-card" shadow="hover">
    <div class="reservation-header">
      <div class="reservation-title">
        <span class="equipment-name">{{ reservation.equipment_name }}</span>
        <el-tag
          :type="statusType"
          size="medium"
          style="font-weight: bold; padding: 8px 12px; font-size: 16px;"
        >
          {{ statusText }}
        </el-tag>
      </div>
      <div class="reservation-code">
        {{ $t('reservation.code') }}: {{ reservation.code }}
      </div>
    </div>

    <div class="reservation-time">
      <i class="el-icon-time"></i>
      {{ formatDateTime(reservation.start_time) }} - {{ formatTime(reservation.end_time) }}
    </div>

    <div class="reservation-info">
      <div class="info-item">
        <span class="info-label">{{ $t('reservation.userName') }}:</span>
        <span class="info-value">{{ reservation.user_name }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">{{ $t('reservation.userDepartment') }}:</span>
        <span class="info-value">{{ reservation.user_department }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">{{ $t('reservation.userContact') }}:</span>
        <span class="info-value">{{ reservation.user_contact }}</span>
      </div>
      <div class="info-item" v-if="reservation.purpose">
        <span class="info-label">{{ $t('reservation.purpose') }}:</span>
        <span class="info-value">{{ reservation.purpose }}</span>
      </div>
    </div>

    <div class="reservation-actions">
      <el-button
        type="primary"
        size="small"
        @click="viewDetail"
      >
        {{ $t('common.detail') }}
      </el-button>
      <el-button
        type="danger"
        size="small"
        @click="cancelReservation"
        :disabled="!canCancel"
      >
        {{ $t('reservation.cancelReservation') }}
      </el-button>
    </div>
  </el-card>
</template>

<script>
import { formatDate } from '@/utils/date'

export default {
  name: 'ReservationCard',

  props: {
    reservation: {
      type: Object,
      required: true
    }
  },

  computed: {
    statusType() {
      const statusMap = {
        'confirmed': 'success',
        'cancelled': 'info',
        'completed': 'warning'
      }

      return statusMap[this.reservation.status] || 'info'
    },

    statusText() {
      const statusMap = {
        'confirmed': this.$t('reservation.confirmed'),
        'cancelled': this.$t('reservation.cancelled'),
        'completed': this.$t('common.completed')
      }

      return statusMap[this.reservation.status] || this.reservation.status
    },

    canCancel() {
      // 只有确认状态的预定可以取消
      return this.reservation.status === 'confirmed'
    }
  },

  methods: {
    formatDateTime(dateTime) {
      return formatDate(dateTime, 'YYYY-MM-DD HH:mm')
    },

    formatTime(dateTime) {
      return formatDate(dateTime, 'HH:mm')
    },

    viewDetail() {
      this.$router.push(`/reservation/${this.reservation.code}`)
    },

    cancelReservation() {
      this.$confirm(
        this.$t('reservation.confirmCancel'),
        this.$t('common.warning'),
        {
          confirmButtonText: this.$t('common.confirm'),
          cancelButtonText: this.$t('common.cancel'),
          type: 'warning'
        }
      ).then(() => {
        this.$emit('cancel', this.reservation.code)
      }).catch(() => {
        // 取消操作，不做任何处理
      })
    }
  }
}
</script>

<style scoped>
.reservation-card {
  margin-bottom: 20px;
}

.reservation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.reservation-title {
  display: flex;
  align-items: center;
}

.equipment-name {
  font-weight: bold;
  margin-right: 10px;
}

.reservation-code {
  font-size: 14px;
  color: #909399;
}

.reservation-time {
  margin-bottom: 15px;
  font-size: 14px;
  color: #606266;
}

.reservation-info {
  margin-bottom: 15px;
}

.info-item {
  margin-bottom: 5px;
  font-size: 14px;
}

.info-label {
  color: #909399;
  margin-right: 5px;
}

.info-value {
  color: #606266;
}

.reservation-actions {
  display: flex;
  justify-content: flex-end;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .reservation-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .reservation-code {
    margin-top: 5px;
  }

  .reservation-actions {
    justify-content: space-between;
  }
}
</style>
