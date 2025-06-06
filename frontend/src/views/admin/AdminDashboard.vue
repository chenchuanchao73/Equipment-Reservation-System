<template>
  <div class="admin-dashboard">
    <div class="page-header">
      <h1 class="page-title">{{ $t('admin.dashboard') }}</h1>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card primary">
            <div class="stats-content">
              <div class="stats-value">{{ stats.totalEquipment }}</div>
              <div class="stats-label">{{ $t('admin.totalEquipment') }}</div>
            </div>
            <i class="el-icon-s-grid stats-icon"></i>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card success">
            <div class="stats-content">
              <div class="stats-value">{{ stats.availableEquipment }}</div>
              <div class="stats-label">{{ $t('admin.availableEquipment') }}</div>
            </div>
            <i class="el-icon-s-cooperation stats-icon"></i>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card warning">
            <div class="stats-content">
              <div class="stats-value">{{ stats.totalReservation }}</div>
              <div class="stats-label">{{ $t('admin.totalReservation') }}</div>
            </div>
            <i class="el-icon-s-order stats-icon"></i>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card danger">
            <div class="stats-content">
              <div class="stats-value">{{ stats.activeReservation }}</div>
              <div class="stats-label">{{ $t('admin.activeReservation') }}</div>
            </div>
            <i class="el-icon-s-claim stats-icon"></i>
          </el-card>
        </el-col>
      </el-row>

      <!-- 详细预约状态统计 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card primary-light">
            <div class="stats-content">
              <div class="stats-value">{{ stats.inUseReservation || 0 }}</div>
              <div class="stats-label">{{ $t('reservation.inUse') }}</div>
            </div>
            <i class="el-icon-loading stats-icon"></i>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card success-light">
            <div class="stats-content">
              <div class="stats-value">{{ stats.confirmedReservation || 0 }}</div>
              <div class="stats-label">{{ $t('reservation.confirmed') }}</div>
            </div>
            <i class="el-icon-check stats-icon"></i>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card warning-light">
            <div class="stats-content">
              <div class="stats-value">{{ stats.expiredReservation || 0 }}</div>
              <div class="stats-label">{{ $t('reservation.expired') }}</div>
            </div>
            <i class="el-icon-time stats-icon"></i>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <el-card shadow="hover" class="stats-card danger-light">
            <div class="stats-content">
              <div class="stats-value">{{ stats.cancelledReservation || 0 }}</div>
              <div class="stats-label">{{ $t('reservation.cancelled') }}</div>
            </div>
            <i class="el-icon-close stats-icon"></i>
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近预定 -->
      <el-card shadow="hover" class="recent-reservations">
        <div slot="header" class="card-header">
          <div class="header-with-info">
            <span>{{ $t('admin.recentReservations') }}</span>
            <el-tooltip content="显示最近创建的10条预约记录" placement="top">
              <i class="el-icon-info info-icon"></i>
            </el-tooltip>
          </div>
          <el-button
            type="text"
            @click="$router.push('/admin/reservation')"
          >
            {{ $t('common.more') }} <i class="el-icon-arrow-right"></i>
          </el-button>
        </div>

        <div v-if="loading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="recentReservations.length === 0" class="empty-data">
          <el-empty :description="$t('common.noData')"></el-empty>
        </div>

        <el-table
          v-else
          :data="recentReservations"
          style="width: 100%"
          :default-sort="{ prop: 'created_at', order: 'descending' }"
          header-align="center"
          cell-class-name="text-center"
          border
          stripe
        >
          <!-- 添加预约序号列 -->
          <el-table-column
            prop="reservation_number"
            :label="$t('reservation.number')"
            min-width="180"
          >
            <template slot-scope="scope">
              <span style="font-weight: bold;">{{ scope.row.reservation_number || '-' }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="reservation_code"
            :label="$t('reservation.code')"
            min-width="100"
          >
            <template slot-scope="scope">
              <span style="color: #F56C6C; font-weight: bold;">{{ scope.row.reservation_code }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="equipment_name"
            :label="$t('reservation.equipmentName')"
            min-width="120"
          ></el-table-column>

          <el-table-column
            prop="user_name"
            :label="$t('reservation.userName')"
            min-width="100"
          ></el-table-column>

          <el-table-column
            prop="user_department"
            :label="$t('reservation.userDepartment')"
            min-width="100"
          >
            <template slot-scope="scope">
              {{ scope.row.user_department || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="user_contact"
            :label="$t('reservation.userContact')"
            min-width="120"
          >
            <template slot-scope="scope">
              {{ scope.row.user_contact || '-' }}
            </template>
          </el-table-column>

          <el-table-column
            prop="start_datetime"
            :label="$t('reservation.startTime')"
            min-width="150"
            :formatter="formatDateTime"
          ></el-table-column>

          <el-table-column
            prop="end_datetime"
            :label="$t('reservation.endTime')"
            min-width="150"
            :formatter="formatDateTime"
          ></el-table-column>

          <el-table-column
            prop="status"
            :label="$t('reservation.status')"
            min-width="100"
          >
            <template slot-scope="scope">
              <el-tag
                :type="getStatusType(scope.row)"
                size="medium"
                style="font-weight: bold; padding: 0px 10px; font-size: 14px;"
              >
                {{ getStatusText(scope.row) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            :label="$t('common.operation')"
            min-width="100"
          >
            <template slot-scope="scope">
              <el-button
                type="text"
                size="small"
                @click="viewReservation(scope.row)"
              >
                {{ $t('admin.viewReservation') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
  </div>
</template>

<script>
import { reservationApi, equipmentApi } from '@/api'
import { isReservationExpired } from '@/utils/date'
import axios from 'axios'

export default {
  name: 'AdminDashboard',

  data() {
    return {
      loading: false,
      stats: {
        totalEquipment: 0,
        availableEquipment: 0,
        totalReservation: 0,
        activeReservation: 0,
        inUseReservation: 0,
        confirmedReservation: 0,
        expiredReservation: 0,
        cancelledReservation: 0
      },
      recentReservations: []
    }
  },

  created() {
    this.fetchData()
  },

  methods: {
    async fetchData() {
      this.loading = true

      try {
        // 检查用户是否已登录
        const token = localStorage.getItem('token')
        if (!token) {
          console.log('用户未登录，跳过仪表盘数据获取')
          this.loading = false
          return
        }

        try {
          // 使用统计API获取仪表盘数据
          const dashboardResponse = await axios.get('/api/statistics/dashboard')
          const dashboardData = dashboardResponse.data

          this.stats.totalEquipment = dashboardData.total_equipment
          this.stats.availableEquipment = dashboardData.available_equipment
          this.stats.totalReservation = dashboardData.total_reservation
          this.stats.activeReservation = dashboardData.active_reservation

          // 处理最近预定数据
          if (dashboardData.recent_reservations && dashboardData.recent_reservations.length > 0) {
            this.recentReservations = dashboardData.recent_reservations.map(reservation => ({
              id: reservation.id,
              reservation_number: reservation.reservation_number, // 添加预约序号字段
              reservation_code: reservation.reservation_code,
              equipment_id: reservation.equipment_id,
              equipment_name: reservation.equipment_name,
              user_name: reservation.user_name,
              user_department: reservation.user_department || '',
              user_contact: reservation.user_contact || '',
              start_datetime: reservation.start_datetime,
              end_datetime: reservation.end_datetime,
              status: reservation.status,
              created_at: reservation.created_at
            }))
          }

          // 直接从预约管理表获取所有预约数据并计算统计数字
          try {
            // 获取预约管理表中的所有预约数据（可能需要分页）
            const allReservationsResponse = await reservationApi.getReservations({
              limit: 1000,  // 获取尽可能多的预约数据
              page: 1
            })

            if (allReservationsResponse.data && allReservationsResponse.data.items) {
              const now = new Date()
              let inUseCount = 0
              let confirmedCount = 0
              let expiredCount = 0
              let cancelledCount = 0

              // 遍历所有预约并计算状态
              allReservationsResponse.data.items.forEach(reservation => {
                const start = new Date(reservation.start_datetime)
                const end = new Date(reservation.end_datetime)

                if (reservation.status === 'cancelled') {
                  cancelledCount++
                } else if (now > end) {
                  expiredCount++
                } else if (now >= start && now <= end) {
                  inUseCount++
                } else if (now < start) {
                  confirmedCount++
                }
              })

              // 更新统计数据
              this.stats.inUseReservation = inUseCount
              this.stats.confirmedReservation = confirmedCount
              this.stats.expiredReservation = expiredCount
              this.stats.cancelledReservation = cancelledCount
            }
          } catch (error) {
            // 静默处理此错误，使用备选方案
            if (error._silenced) {
              console.log('预约数据获取被静默处理')
            } else {
              console.log('获取预约状态统计失败，使用备选数据')
            }

            // 出错时，尝试使用近期预约数据（最后的备选）
            if (dashboardData.recent_reservations && dashboardData.recent_reservations.length > 0) {
              const now = new Date()
              let inUseCount = 0
              let confirmedCount = 0
              let expiredCount = 0
              let cancelledCount = 0

              dashboardData.recent_reservations.forEach(r => {
                const start = new Date(r.start_datetime)
                const end = new Date(r.end_datetime)

                if (r.status === 'cancelled') {
                  cancelledCount++
                } else if (now > end) {
                  expiredCount++
                } else if (now >= start && now <= end) {
                  inUseCount++
                } else {
                  confirmedCount++
                }
              })

              this.stats.inUseReservation = inUseCount
              this.stats.confirmedReservation = confirmedCount
              this.stats.expiredReservation = expiredCount
              this.stats.cancelledReservation = cancelledCount
            }
          }
        } catch (error) {
          // 检查是否是被静默处理的错误
          if (error._silenced) {
            console.log('仪表盘数据获取被静默处理')
          } else {
            console.log('获取仪表盘数据失败，可能是权限问题')
          }
          // 不显示错误消息，静默处理
        }
      } catch (error) {
        // 捕获所有其他错误
        console.log('仪表盘组件出现未预期的错误')
      } finally {
        this.loading = false
      }
    },

    formatDateTime(row, column, cellValue) {
      if (!cellValue) return ''

      const date = new Date(cellValue)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

    getStatusType(reservation) {
      // 如果预约已取消，返回红色
      if (reservation.status === 'cancelled') {
        return 'danger'
      }

      // 如果预约已过期，返回橙色
      if (isReservationExpired(reservation.end_datetime)) {
        return 'warning'
      }

      // 如果预约正在进行中，返回蓝色
      const now = new Date()
      const start = new Date(reservation.start_datetime)
      const end = new Date(reservation.end_datetime)
      if (now >= start && now <= end) {
        return 'primary'
      }

      // 如果预约已确认且未开始，返回绿色
      // "已确认"状态出现在预约被管理员批准，但还未开始使用的情况
      return 'success'
    },

    getStatusText(reservation) {
      // 如果预约已取消，显示"已取消"
      if (reservation.status === 'cancelled') {
        return this.$t('reservation.cancelled')
      }

      // 如果预约已过期，显示"已过期"
      if (isReservationExpired(reservation.end_datetime)) {
        return this.$t('reservation.expired')
      }

      // 如果预约正在进行中，显示"使用中"
      const now = new Date()
      const start = new Date(reservation.start_datetime)
      const end = new Date(reservation.end_datetime)
      if (now >= start && now <= end) {
        return this.$t('reservation.inUse')
      }

      // 如果预约已确认且未开始，显示"已确认"
      // "已确认"状态出现在预约被管理员批准，但还未开始使用的情况
      return this.$t('reservation.confirmed')
    },

    viewReservation(reservation) {
      // 计算当前预约的实际状态文本和类型
      const statusText = this.getStatusText(reservation)
      const statusType = this.getStatusType(reservation)

      console.log('计算的状态信息:', {
        statusText,
        statusType,
        dbStatus: reservation.status,
        startTime: reservation.start_datetime,
        endTime: reservation.end_datetime,
        reservationNumber: reservation.reservation_number
      })

      // 构建URL，添加预约码、时间参数、预约序号和计算好的状态信息
      const url = {
        path: `/admin/reservation/${reservation.reservation_code}`,
        query: {
          startTime: reservation.start_datetime,
          endTime: reservation.end_datetime,
          displayStatus: statusText,
          displayStatusType: statusType,
          reservationNumber: reservation.reservation_number // 添加预约序号参数
        }
      }

      // 每次查看预约时，都重新设置一个标记，表示需要显示预约序号通知
      localStorage.setItem('show_reservation_number_notification', 'true')

      // 清除之前的预约序号，确保每次都使用新的预约序号
      localStorage.removeItem('current_reservation_number')

      // 将预约序号保存到localStorage，以便在页面刷新后仍然可以使用
      if (reservation.reservation_number) {
        localStorage.setItem('current_reservation_number', reservation.reservation_number)
        console.log('保存预约序号到localStorage:', reservation.reservation_number)

        // 强制使用预约序号查询，而不是预约码
        localStorage.setItem('force_use_reservation_number', 'true')
      }

      this.$router.push(url)
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  width: 100%;
}

.page-header {
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: #FFFFFF;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  height: 100px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
}

/* 第二行的状态卡片可以稍微高一些，以确保图标完全显示 */
.stats-row:nth-child(2) .stats-card {
  height: 120px; /* 增加高度 */
  padding: 20px 20px 25px 20px; /* 增加底部内边距 */
}

.stats-card.primary {
  border-left: 4px solid #409EFF;
}

.stats-card.success {
  border-left: 4px solid #67C23A;
}

.stats-card.warning {
  border-left: 4px solid #E6A23C;
}

.stats-card.danger {
  border-left: 4px solid #F56C6C;
}

/* 新增浅色样式卡片 */
.stats-card.primary-light {
  border-left: 4px solid #409EFF;
  background-color: rgba(64, 158, 255, 0.1);
}

.stats-card.success-light {
  border-left: 4px solid #67C23A;
  background-color: rgba(103, 194, 58, 0.1);
}

.stats-card.warning-light {
  border-left: 4px solid #E6A23C;
  background-color: rgba(230, 162, 60, 0.1);
}

.stats-card.danger-light {
  border-left: 4px solid #F56C6C;
  background-color: rgba(245, 108, 108, 0.1);
}

.stats-content {
  z-index: 1;
}

.stats-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  right: 20px;
  font-size: 60px;
  opacity: 0.1;
  color: #000;
}

/* 修改图标样式，确保完整显示在卡片内 */
.stats-card .stats-icon {
  position: absolute;
  right: 20px;
  bottom: 15px; /* 调整从底部的距离 */
  font-size: 50px; /* 调小图标尺寸 */
  opacity: 0.2; /* 增加透明度，让背景色更明显 */
  color: #000;
  overflow: hidden; /* 确保溢出部分隐藏 */
}

.recent-reservations {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-with-info {
  display: flex;
  align-items: center;
}

.info-icon {
  margin-left: 5px;
  font-size: 14px;
  color: #909399;
  cursor: pointer;
}

.loading-container {
  padding: 40px 0;
}

.empty-data {
  padding: 40px 0;
  text-align: center;
}

.text-center {
  text-align: center !important;
}

@media (max-width: 768px) {
  .stats-card {
    height: 80px;
  }

  .stats-value {
    font-size: 24px;
  }

  .stats-icon {
    font-size: 40px;
  }
}
</style>
