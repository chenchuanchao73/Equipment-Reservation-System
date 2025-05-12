<template>
  <div class="recurring-reservation-detail">
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        :title="$t('common.error')"
        :sub-title="errorMessage"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">{{ $t('common.backToHome') }}</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="content-container">
      <div class="header-actions">
        <el-button icon="el-icon-back" @click="goBack">{{ $t('common.back') }}</el-button>
        <el-button type="danger" @click="showCancelDialog" :disabled="recurringReservation.status === 'cancelled'">
          {{ $t('reservation.cancelRecurringReservation') }}
        </el-button>
      </div>

      <!-- 循环预约信息卡片 -->
      <el-card class="reservation-card" shadow="hover">
        <div slot="header" class="card-header">
          <span>{{ $t('reservation.recurringReservationDetails') }}</span>
          <el-tag :type="getStatusType(recurringReservation)" size="medium">
            {{ getStatusText(recurringReservation) }}
          </el-tag>
        </div>

        <div class="reservation-info">
          <div class="info-section">
            <h3>{{ $t('reservation.reservationInfo') }}</h3>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.code') }}:</span>
              <span class="info-value">{{ recurringReservation.reservation_code }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.pattern') }}:</span>
              <span class="info-value">{{ getPatternText(recurringReservation.pattern_type) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.dateRange') }}:</span>
              <span class="info-value">{{ formatDate(recurringReservation.start_date) }} - {{ formatDate(recurringReservation.end_date) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.timeRange') }}:</span>
              <span class="info-value">{{ formatTime(recurringReservation.start_time) }} - {{ formatTime(recurringReservation.end_time) }}</span>
            </div>
            <div class="info-row" v-if="recurringReservation.days_of_week && recurringReservation.days_of_week.length > 0">
              <span class="info-label">{{ $t('reservation.daysOfWeek') }}:</span>
              <span class="info-value">{{ formatDaysOfWeek(recurringReservation.days_of_week) }}</span>
            </div>
            <div class="info-row" v-if="recurringReservation.days_of_month && recurringReservation.days_of_month.length > 0">
              <span class="info-label">{{ $t('reservation.daysOfMonth') }}:</span>
              <span class="info-value">{{ formatDaysOfMonth(recurringReservation.days_of_month) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.purpose') }}:</span>
              <span class="info-value">{{ recurringReservation.purpose || $t('common.notProvided') }}</span>
            </div>
          </div>

          <div class="info-section">
            <h3>{{ $t('equipment.equipmentInfo') }}</h3>
            <div class="info-row">
              <span class="info-label">{{ $t('equipment.name') }}:</span>
              <span class="info-value">{{ recurringReservation.equipment_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('equipment.category') }}:</span>
              <span class="info-value">{{ recurringReservation.equipment_category }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('equipment.location') }}:</span>
              <span class="info-value">{{ recurringReservation.equipment_location || $t('common.notProvided') }}</span>
            </div>
          </div>

          <div class="info-section">
            <h3>{{ $t('reservation.userInfo') }}</h3>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.userName') }}:</span>
              <span class="info-value">{{ recurringReservation.user_name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.userDepartment') }}:</span>
              <span class="info-value">{{ recurringReservation.user_department }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">{{ $t('reservation.userContact') }}:</span>
              <span class="info-value">{{ recurringReservation.user_contact }}</span>
            </div>
            <div class="info-row" v-if="recurringReservation.user_email">
              <span class="info-label">{{ $t('reservation.userEmail') }}:</span>
              <span class="info-value">{{ recurringReservation.user_email }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 子预约列表 -->
      <el-card class="child-reservations-card" shadow="hover">
        <div slot="header" class="card-header">
          <span>{{ $t('reservation.childReservations') }}</span>
          <el-switch
            v-model="includePastReservations"
            :active-text="$t('reservation.includePast')"
            @change="loadChildReservations"
          ></el-switch>
        </div>

        <div v-if="childReservationsLoading" class="loading-container">
          <el-skeleton :rows="5" animated />
        </div>

        <div v-else-if="childReservations.length === 0" class="empty-state">
          <el-empty :description="$t('reservation.noChildReservations')"></el-empty>
        </div>

        <div v-else class="child-reservations-list">
          <el-table
            :data="childReservations"
            style="width: 100%"
            border
            stripe
            :row-class-name="getRowClassName"
          >
            <el-table-column
              type="index"
              :label="$t('common.id')"
              width="60"
            ></el-table-column>
            <el-table-column
              prop="reservation_number"
              :label="$t('reservation.number')"
              width="160"
            ></el-table-column>
            <el-table-column
              prop="reservation_code"
              :label="$t('reservation.code')"
              width="120"
            ></el-table-column>
            <el-table-column
              prop="start_datetime"
              :label="$t('reservation.startTime')"
              width="150"
              :formatter="formatDateTime"
            ></el-table-column>
            <el-table-column
              prop="end_datetime"
              :label="$t('reservation.endTime')"
              width="150"
              :formatter="formatDateTime"
            ></el-table-column>
            <el-table-column
              prop="status"
              :label="$t('reservation.status')"
              width="140"
            >
              <template slot-scope="scope">
                <el-tag :type="getChildStatusType(scope.row)" size="medium">
                  {{ getChildStatusText(scope.row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              :label="$t('common.actions')"
              width="150"
            >
              <template slot-scope="scope">
                <el-button
                  size="mini"
                  type="primary"
                  @click="viewChildReservation(scope.row)"
                  icon="el-icon-view"
                  circle
                ></el-button>
                <el-button
                  size="mini"
                  type="danger"
                  @click="cancelChildReservation(scope.row)"
                  :disabled="scope.row.status === 'cancelled' || scope.row.status === 'expired'"
                  icon="el-icon-delete"
                  circle
                ></el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-card>
    </div>

    <!-- 取消循环预约对话框 -->
    <el-dialog
      :title="$t('reservation.cancelRecurringReservation')"
      :visible.sync="cancelDialogVisible"
      width="500px"
    >
      <div class="cancel-options">
        <p>{{ $t('reservation.cancelRecurringReservationConfirm') }}</p>
        <div class="email-input">
          <el-form-item :label="$t('reservation.userEmail')" prop="userEmail">
            <el-input v-model="userEmail" :placeholder="$t('reservation.emailForConfirmation')"></el-input>
          </el-form-item>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancelDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="danger" @click="confirmCancel" :loading="cancelLoading">{{ $t('common.confirm') }}</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { recurringReservationApi, reservationApi } from '@/api'
import { isReservationExpired } from '@/utils/date'

export default {
  name: 'RecurringReservationDetail',

  data() {
    return {
      recurringReservationId: null,
      recurringReservation: null,
      childReservations: [],
      loading: true,
      childReservationsLoading: false,
      error: false,
      errorMessage: '',
      includePastReservations: true, // 默认选中"包含已过期预约"
      cancelDialogVisible: false,
      userEmail: '',
      cancelLoading: false,
      fromChildReservation: false,
      highlightReservationNumber: null // 用于高亮显示特定的子预约
    }
  },

  props: {
    id: {
      type: [String, Number],
      required: false
    }
  },

  created() {
    // 优先使用props中的id，如果没有则使用路由参数
    this.recurringReservationId = this.id || this.$route.params.id
    console.log('Recurring reservation ID:', this.recurringReservationId)

    // 检查是否是从子预约详情页面返回的
    this.fromChildReservation = this.$route.query.fromChild === 'true'

    // 检查是否有预约序号参数，用于高亮显示特定的子预约
    if (this.$route.query.reservation_number) {
      this.highlightReservationNumber = this.$route.query.reservation_number
      console.log('高亮显示预约序号:', this.highlightReservationNumber)
    }

    this.loadRecurringReservation()
  },

  // 添加activated钩子函数，在组件被激活时调用（如从子预约详情页面返回）
  activated() {
    // 检查子预约状态是否发生变化
    this.checkChildReservationUpdates()
  },

  methods: {
    // 加载循环预约详情
    async loadRecurringReservation() {
      this.loading = true
      this.error = false

      try {
        const response = await recurringReservationApi.getRecurringReservation(this.recurringReservationId)

        if (response.data.success) {
          this.recurringReservation = response.data.data
          this.userEmail = this.recurringReservation.user_email || ''
          this.loadChildReservations()
        } else {
          this.error = true
          this.errorMessage = response.data.message || this.$t('reservation.failedToLoadReservation')
        }
      } catch (error) {
        console.error('Failed to load recurring reservation:', error)
        this.error = true
        this.errorMessage = error.response?.data?.detail || this.$t('reservation.failedToLoadReservation')
      } finally {
        this.loading = false
      }
    },

    // 加载子预约列表
    async loadChildReservations() {
      this.childReservationsLoading = true

      try {
        // 始终包含已过期的预约，设置include_past=1
        const response = await recurringReservationApi.getChildReservations(
          this.recurringReservationId,
          1  // 始终设置为1，表示包含已过期的预约
        )

        if (response.data.success) {
          // 获取所有子预约
          this.childReservations = response.data.reservations || [];

          // 如果includePastReservations为false，则在前端过滤掉已过期的预约
          if (!this.includePastReservations) {
            const now = new Date();
            this.childReservations = this.childReservations.filter(reservation => {
              // 保留未过期的预约和已取消的预约
              const endTime = new Date(reservation.end_datetime);
              return endTime >= now || reservation.status === 'cancelled';
            });
          }

          // 按预约序号排序
          this.childReservations.sort((a, b) => {
            // 从预约序号中提取数字部分进行比较
            const numA = a.reservation_number ? parseInt(a.reservation_number.replace(/\D/g, '')) : 0;
            const numB = b.reservation_number ? parseInt(b.reservation_number.replace(/\D/g, '')) : 0;
            return numA - numB;
          });

          console.log('Child reservations loaded:', this.childReservations.length)
        } else {
          this.$message.error(response.data.message || this.$t('reservation.failedToLoadChildReservations'))
        }
      } catch (error) {
        console.error('Failed to load child reservations:', error)
        this.$message.error(this.$t('reservation.failedToLoadChildReservations'))
      } finally {
        this.childReservationsLoading = false
      }
    },

    // 返回上一页
    goBack() {
      // 对于所有情况，直接返回到个人预约管理页面
      window.location.href = '/#/reservation/query'
    },

    // 查看子预约详情
    viewChildReservation(reservation) {
      // 检查是否有预约序号
      if (reservation.reservation_number) {
        console.log('通过预约序号查看子预约详情:', reservation.reservation_number)

        // 使用预约序号直接跳转到预约详情页面
        const reservationNumber = reservation.reservation_number;
        const reservationCode = reservation.reservation_code;

        console.log('准备跳转到预约详情页面:', {
          reservationNumber,
          reservationCode
        });

        // 构建查询参数
        const query = {
          child: 'true',
          recurringId: this.recurringReservation.id,
          code: reservationCode  // 添加预约码作为查询参数
        }

        // 保留用户联系方式参数（如果有）
        if (this.$route.query.userContact) {
          console.log('viewChildReservation - 保留用户联系方式参数:', this.$route.query.userContact)
          query.userContact = this.$route.query.userContact
        }

        // 保留来源参数（如果有）
        if (this.$route.query.from) {
          console.log('viewChildReservation - 保留来源参数:', this.$route.query.from)
          query.from = this.$route.query.from
        }

        console.log('viewChildReservation - 跳转到子预约详情页面，参数:', query)
        this.$router.push({
          path: `/reservation/number/${reservationNumber}`,
          query: query
        })

        // 将预约序号和预约码保存到localStorage，以便在页面刷新后仍然可以使用
        localStorage.setItem('current_reservation_number', reservation.reservation_number)
        localStorage.setItem('current_reservation_code', reservation.reservation_code)

        console.log('查看子预约详情:', {
          id: reservation.id,
          reservation_code: reservation.reservation_code,
          reservation_number: reservation.reservation_number,
          startTime: reservation.start_datetime,
          endTime: reservation.end_datetime
        })
      } else if (reservation.id) {
        // 如果没有预约序号但有ID，则使用旧方法
        // 构建查询参数
        const query = {
          child: 'true',
          id: reservation.id,
          recurringId: this.recurringReservation.id,
          startTime: reservation.start_datetime,
          endTime: reservation.end_datetime
        }

        // 保留用户联系方式参数（如果有）
        if (this.$route.query.userContact) {
          console.log('viewChildReservation(旧方法) - 保留用户联系方式参数:', this.$route.query.userContact)
          query.userContact = this.$route.query.userContact
        }

        // 保留来源参数（如果有）
        if (this.$route.query.from) {
          console.log('viewChildReservation(旧方法) - 保留来源参数:', this.$route.query.from)
          query.from = this.$route.query.from
        }

        console.log('viewChildReservation(旧方法) - 跳转到子预约详情页面，参数:', query)
        this.$router.push({
          path: `/reservation/${reservation.reservation_code}`,
          query: query
        })

        console.log('使用旧方法查看子预约详情:', {
          id: reservation.id,
          reservation_code: reservation.reservation_code,
          startTime: reservation.start_datetime,
          endTime: reservation.end_datetime
        })
      } else {
        this.$message.warning('无法查看子预约详情，缺少预约序号和ID')
      }
    },

    // 取消子预约
    async cancelChildReservation(reservation) {
      try {
        console.log('准备取消子预约:', reservation)
        console.log('子预约序号:', reservation.reservation_number)

        const result = await this.$confirm(
          this.$t('reservation.cancelConfirmation'),
          this.$t('common.warning'),
          {
            confirmButtonText: this.$t('common.confirm'),
            cancelButtonText: this.$t('common.cancel'),
            type: 'warning'
          }
        )

        if (result === 'confirm') {
          // 添加预约序号参数，确保只取消特定的子预约
          const requestData = {
            user_email: this.recurringReservation.user_email
          }

          // 添加预约序号参数，确保只取消特定的子预约
          if (reservation.reservation_number) {
            requestData.reservation_number = reservation.reservation_number
            console.log('预约序号参数存在:', reservation.reservation_number)
          } else {
            console.warn('预约序号参数不存在，将取消所有具有相同预约码的预约')
          }

          console.log('取消子预约请求参数:', requestData)
          console.log('预约码:', reservation.reservation_code)

          const response = await reservationApi.cancelReservation(reservation.reservation_code, requestData)

          console.log('取消子预约响应:', response.data)

          if (response.data.success) {
            this.$message.success(this.$t('reservation.cancelSuccess'))

            // 直接更新子预约状态为已取消
            reservation.status = 'cancelled'

            // 保存状态变更到localStorage
            this.saveChildReservationStatus(reservation, 'cancelled')

            // 强制刷新整个页面，确保获取最新数据
            console.log('子预约已取消，即将刷新页面...')
            setTimeout(() => {
              window.location.reload(true)
            }, 1000)
          } else {
            this.$message.error(response.data.message || this.$t('reservation.cancelFailed'))
          }
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('Failed to cancel reservation:', error)
          this.$message.error(this.$t('reservation.cancelFailed'))
        }
      }
    },

    // 保存子预约状态到localStorage
    saveChildReservationStatus(reservation, status) {
      if (!reservation) return

      // 使用预约码作为键
      const stateKey = `reservation_status_${reservation.reservation_code}`

      // 保存状态信息
      const state = {
        statusText: this.getChildStatusText({ ...reservation, status: status }),
        statusType: this.getChildStatusType({ ...reservation, status: status }),
        dbStatus: status,
        forcedStatus: status,
        timestamp: new Date().getTime(),
        permanent: true,
        reservationCode: reservation.reservation_code
      }

      console.log('保存子预约状态到localStorage:', state)
      localStorage.setItem(stateKey, JSON.stringify(state))
    },

    // 检查子预约状态是否发生变化
    checkChildReservationUpdates() {
      console.log('检查子预约状态是否发生变化')

      // 检查是否有子预约状态变更标记
      const recurringStateKey = `recurring_reservation_${this.recurringReservationId}_child_status_changed`
      const recurringStateStr = localStorage.getItem(recurringStateKey)

      if (recurringStateStr) {
        try {
          const recurringState = JSON.parse(recurringStateStr)

          // 检查状态变更是否还是新鲜的（5分钟内）
          const now = new Date().getTime()
          const fiveMinutes = 5 * 60 * 1000

          if (now - recurringState.timestamp <= fiveMinutes) {
            console.log('检测到子预约状态变更，刷新列表:', recurringState)

            // 移除状态变更标记
            localStorage.removeItem(recurringStateKey)

            // 重新加载子预约列表
            this.loadChildReservations()
            return
          } else {
            // 如果状态变更过期，移除它
            localStorage.removeItem(recurringStateKey)
          }
        } catch (e) {
          console.error('解析子预约状态变更标记时出错:', e)
        }
      }

      // 如果没有子预约状态变更标记，检查每个子预约的状态
      if (this.childReservations.length > 0) {
        let needRefresh = false

        // 检查每个子预约的状态
        for (let i = 0; i < this.childReservations.length; i++) {
          const reservation = this.childReservations[i]
          const stateKey = `reservation_status_${reservation.reservation_code}`
          const savedStateStr = localStorage.getItem(stateKey)

          if (savedStateStr) {
            try {
              const savedState = JSON.parse(savedStateStr)

              // 检查保存的状态是否还是新鲜的（5分钟内）
              const now = new Date().getTime()
              const fiveMinutes = 5 * 60 * 1000

              if (now - savedState.timestamp <= fiveMinutes) {
                console.log(`检测到子预约 ${reservation.reservation_code} 的状态可能已更改，保存的状态:`, savedState)

                // 如果状态已变更为已取消，需要刷新子预约列表
                if (savedState.forcedStatus === 'cancelled' ||
                    (savedState.statusText === this.$t('reservation.cancelled') &&
                     savedState.statusType === 'danger')) {
                  console.log(`子预约 ${reservation.reservation_code} 已被标记为已取消，需要刷新列表`)
                  needRefresh = true
                  break
                }
              } else {
                // 如果状态过期，则移除它
                localStorage.removeItem(stateKey)
              }
            } catch (e) {
              console.error(`解析子预约 ${reservation.reservation_code} 的保存状态时出错:`, e)
            }
          }
        }

        // 如果需要刷新，重新加载子预约列表
        if (needRefresh) {
          console.log('检测到子预约状态变更，刷新列表')
          this.loadChildReservations()
        }
      }
    },

    // 显示取消循环预约对话框
    showCancelDialog() {
      this.cancelDialogVisible = true
    },

    // 确认取消循环预约
    async confirmCancel() {
      this.cancelLoading = true

      try {
        const response = await recurringReservationApi.cancelRecurringReservation(
          this.recurringReservationId,
          this.userEmail || null
        )

        if (response.data.success) {
          this.$message.success(this.$t('reservation.cancelSuccess'))
          this.cancelDialogVisible = false
          this.loadRecurringReservation()
        } else {
          this.$message.error(response.data.message || this.$t('reservation.cancelFailed'))
        }
      } catch (error) {
        console.error('Failed to cancel recurring reservation:', error)
        this.$message.error(this.$t('reservation.cancelFailed'))
      } finally {
        this.cancelLoading = false
      }
    },

    // 格式化日期
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    },

    // 格式化时间
    formatTime(timeStr) {
      if (!timeStr) return ''
      return timeStr.substring(0, 5)
    },

    // 格式化日期时间
    formatDateTime(row, column, cellValue) {
      if (!cellValue) return ''
      const date = new Date(cellValue)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
    },

    // 格式化星期几
    formatDaysOfWeek(days) {
      if (!days || days.length === 0) return ''

      const dayNames = [
        this.$t('reservation.sunday'),
        this.$t('reservation.monday'),
        this.$t('reservation.tuesday'),
        this.$t('reservation.wednesday'),
        this.$t('reservation.thursday'),
        this.$t('reservation.friday'),
        this.$t('reservation.saturday')
      ]

      return days.map(day => dayNames[day]).join(', ')
    },

    // 格式化每月几号
    formatDaysOfMonth(days) {
      if (!days || days.length === 0) return ''
      return days.join(', ')
    },

    // 获取循环模式文本
    getPatternText(pattern) {
      const patterns = {
        'daily': this.$t('reservation.daily'),
        'weekly': this.$t('reservation.weekly'),
        'monthly': this.$t('reservation.monthly'),
        'custom': this.$t('reservation.custom')
      }
      return patterns[pattern] || pattern
    },

    // 获取循环预约状态类型
    getStatusType(reservation) {
      if (reservation.status === 'cancelled') {
        return 'danger'
      }
      return 'success'
    },

    // 获取循环预约状态文本
    getStatusText(reservation) {
      if (reservation.status === 'cancelled') {
        return this.$t('reservation.cancelled')
      }
      return this.$t('reservation.active')
    },

    // 获取子预约状态类型
    getChildStatusType(reservation) {
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
      return 'success'
    },

    // 获取子预约状态文本
    getChildStatusText(reservation) {
      // 如果预约已取消，显示"已取消"
      if (reservation.status === 'cancelled') {
        return this.$t('reservation.cancelled')
      }

      // 如果预约已过期，显示"已过期"
      if (isReservationExpired(reservation.end_datetime)) {
        return this.$t('reservation.expired')
      }

      // 如果预约正在进行中，显示"进行中"
      const now = new Date()
      const start = new Date(reservation.start_datetime)
      const end = new Date(reservation.end_datetime)
      if (now >= start && now <= end) {
        return this.$t('reservation.ongoing')
      }

      // 如果预约已确认且未开始，显示"已确认"
      return this.$t('reservation.confirmed')
    },

    // 获取行的类名，用于高亮显示特定的子预约
    getRowClassName({ row }) {
      if (this.highlightReservationNumber && row.reservation_number === this.highlightReservationNumber) {
        return 'highlighted-row'
      }
      return ''
    }
  }
}
</script>

<style scoped>
.recurring-reservation-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container,
.error-container {
  margin: 40px 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.reservation-card,
.child-reservations-card {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.reservation-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.info-section {
  margin-bottom: 20px;
}

.info-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #303133;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 10px;
}

.info-row {
  margin-bottom: 10px;
  line-height: 1.5;
}

.info-label {
  font-weight: bold;
  color: #606266;
  margin-right: 5px;
}

.info-value {
  color: #303133;
}

.empty-state {
  padding: 30px 0;
}

.cancel-options {
  padding: 0 20px;
}

.cancel-options p {
  margin-bottom: 20px;
  color: #606266;
}

.email-input {
  margin-top: 20px;
}

.child-reservations-list {
  margin-top: 20px;
}

.highlighted-row {
  background-color: #fdf5e6 !important; /* 浅橙色背景 */
}
</style>
