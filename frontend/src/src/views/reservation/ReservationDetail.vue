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
          <el-descriptions-item :label="$t('reservation.number')">
            {{ reservation.reservation_number || '-' }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.reservationType')">
            <el-tag
              size="medium"
              :type="reservation.recurring_reservation_id ? 'primary' : 'success'"
              effect="plain"
            >
              {{ reservation.recurring_reservation_id ? $t('reservation.recurringReservation') : $t('reservation.singleReservation') }}
            </el-tag>
            <el-button
              v-if="reservation.recurring_reservation_id"
              type="primary"
              size="mini"
              style="margin-left: 10px;"
              @click="viewRecurringReservation"
            >
              {{ $t('reservation.viewRecurringReservation') }}
            </el-button>
          </el-descriptions-item>

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
        <!-- 已确认状态的预约显示修改按钮 -->
        <el-button v-if="canModify" type="primary" @click="showModifyDialog" icon="el-icon-edit">
          {{ $t('reservation.modifyReservation') }}
        </el-button>

        <!-- 已确认状态的预约显示取消按钮 -->
        <el-button v-if="canCancel" type="danger" @click="showCancelDialog" icon="el-icon-close">
          {{ $t('reservation.cancelReservation') }}
        </el-button>

        <!-- 使用中状态的预约显示提前归还按钮 -->
        <el-button v-if="canReturn" type="primary" @click="showReturnDialog" icon="el-icon-time">
          {{ $t('reservation.earlyReturn') }}
        </el-button>

        <!-- 查看历史记录按钮 -->
        <el-button type="info" @click="showHistory" icon="el-icon-document">
          {{ $t('reservation.viewHistory') }}
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

      <!-- 修改预定对话框 -->
      <el-dialog
        :title="$t('reservation.modifyReservation')"
        :visible.sync="modifyDialogVisible"
        width="600px"
      >
        <el-form
          ref="modifyForm"
          :model="modifyForm"
          :rules="modifyRules"
          label-width="120px"
          v-loading="modifying"
        >
          <!-- 开始时间 -->
          <el-form-item :label="$t('reservation.startTime')" prop="startDateTime">
            <el-date-picker
              v-model="modifyForm.startDateTime"
              type="datetime"
              :placeholder="$t('reservation.selectStartTime')"
              style="width: 100%"
              :picker-options="dateTimePickerOptions"
              value-format="yyyy-MM-ddTHH:mm:ss"
              format="yyyy-MM-dd HH:mm:ss"
              @change="checkTimeAvailability"
            ></el-date-picker>
          </el-form-item>

          <!-- 结束时间 -->
          <el-form-item :label="$t('reservation.endTime')" prop="endDateTime">
            <el-date-picker
              v-model="modifyForm.endDateTime"
              type="datetime"
              :placeholder="$t('reservation.selectEndTime')"
              style="width: 100%"
              :picker-options="dateTimePickerOptions"
              value-format="yyyy-MM-ddTHH:mm:ss"
              format="yyyy-MM-dd HH:mm:ss"
              @change="checkTimeAvailability"
            ></el-date-picker>
          </el-form-item>

          <!-- 时间冲突提示 -->
          <el-alert
            v-if="timeConflict"
            :title="timeConflictTitle"
            type="error"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          >
            <div v-if="conflictingReservations && conflictingReservations.length > 0">
              <p style="margin-bottom: 10px;">{{ $t('reservation.conflictWithFollowing') }}</p>
              <div v-for="conflict in conflictingReservations" :key="conflict.id" style="margin-bottom: 8px; padding: 8px; background-color: #fef0f0; border-radius: 4px;">
                <div><strong>{{ $t('reservation.conflictTime') }}</strong>{{ conflict.start_datetime }} {{ $t('reservation.conflictTo') }} {{ conflict.end_datetime }}</div>
                <div><strong>{{ $t('reservation.conflictUser') }}</strong>{{ conflict.user_name }} ({{ conflict.user_department }})</div>
                <div v-if="conflict.user_email"><strong>{{ $t('reservation.conflictEmail') }}</strong>{{ conflict.user_email }}</div>
                <div v-if="conflict.user_phone"><strong>{{ $t('reservation.conflictPhone') }}</strong>{{ conflict.user_phone }}</div>
                <div v-if="conflict.purpose"><strong>{{ $t('reservation.conflictPurpose') }}</strong>{{ conflict.purpose }}</div>
              </div>
            </div>
            <template v-else-if="conflictMessage">
              {{ conflictMessage }}
            </template>
          </el-alert>

          <!-- 时间可用提示 -->
          <el-alert
            v-if="!timeConflict && timeAvailabilityChecked"
            :title="$t('reservation.timeSlotAvailable')"
            type="success"
            :closable="false"
            show-icon
            style="margin-bottom: 15px;"
          ></el-alert>

          <!-- 使用目的 -->
          <el-form-item :label="$t('reservation.purpose')" prop="purpose">
            <el-input
              v-model="modifyForm.purpose"
              type="textarea"
              :rows="3"
              :placeholder="$t('reservation.purposePlaceholder')"
            ></el-input>
          </el-form-item>

          <!-- 用户邮箱 -->
          <el-form-item :label="$t('reservation.userEmail')" prop="userEmail" required>
            <el-input
              v-model="modifyForm.userEmail"
              :placeholder="$t('reservation.emailPlaceholder')"
            ></el-input>
          </el-form-item>
        </el-form>

        <div slot="footer" class="dialog-footer">
          <el-button @click="modifyDialogVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" @click="submitModifyForm" :loading="modifying" :disabled="timeConflict">
            {{ $t('common.confirm') }}
          </el-button>
        </div>
      </el-dialog>

      <!-- 修改历史记录对话框 -->
      <el-dialog
        :title="$t('reservation.modificationHistory')"
        :visible.sync="historyDialogVisible"
        width="700px"
      >
        <div v-loading="loadingHistory">
          <el-empty v-if="processedHistoryRecords.length === 0" :description="$t('reservation.noHistory')"></el-empty>
          <el-timeline v-else>
            <el-timeline-item
              v-for="(group, index) in processedHistoryRecords"
              :key="index"
              type="primary"
            >
              <el-card class="history-card">
                <!-- 修改时间显示在最上面 -->
                <div class="history-time">
                  <i class="el-icon-time"></i> {{ formatDateTime(group.timestamp) }}
                </div>

                <div class="history-user">
                  {{ group.user_type === 'admin' ? $t('reservation.admin') : $t('reservation.user') }}
                  {{ group.user_id ? ': ' + group.user_id : '' }}
                </div>

                <div v-for="(record, recordIndex) in group.records" :key="recordIndex" class="history-item">
                  <div class="history-action">
                    {{ getHistoryActionText(record.action) }}
                    <span class="history-field">{{ getFieldDisplayName(record.field_name) }}</span>
                  </div>
                  <div class="history-values">
                    <div class="history-old-value">
                      <span class="history-label">{{ $t('reservation.oldValue') }}:</span>
                      <span>{{ formatHistoryValue(record.field_name, record.old_value) }}</span>
                    </div>
                    <div class="history-new-value">
                      <span class="history-label">{{ $t('reservation.newValue') }}:</span>
                      <span>{{ formatHistoryValue(record.field_name, record.new_value) }}</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { reservationApi, equipmentApi } from '@/api'
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
      returning: false,
      modifyDialogVisible: false,
      modifying: false,
      timeConflict: false,
      conflictMessage: '',
      conflictingReservations: [],
      timeAvailabilityChecked: false,
      modifyForm: {
        startDateTime: '',
        endDateTime: '',
        purpose: '',
        userEmail: ''
      },
      modifyRules: {
        startDateTime: [
          { required: true, message: this.$t('reservation.startTimeRequired'), trigger: 'change' }
        ],
        endDateTime: [
          { required: true, message: this.$t('reservation.endTimeRequired'), trigger: 'change' }
        ],
        userEmail: [
          { required: true, message: this.$t('reservation.emailRequired'), trigger: 'blur' },
          { type: 'email', message: this.$t('reservation.emailFormat'), trigger: 'blur' }
        ]
      },
      dateTimePickerOptions: {
        disabledDate: this.disabledDate
      },
      historyDialogVisible: false,
      loadingHistory: false,
      historyRecords: [],
      // 添加循环预定相关属性
      recurringReservationId: null,
      isRecurringReservation: false
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
    },

    // 是否可以修改预定
    canModify() {
      if (!this.reservation) return false

      // 只有确认状态且未开始的预定可以修改
      if (this.reservation.status !== 'confirmed') return false

      // 检查是否已开始
      const now = new Date()
      const startTime = new Date(this.reservation.start_datetime)

      return startTime > now
    },

    // 处理历史记录，按时间分组并过滤掉不需要显示的字段
    processedHistoryRecords() {
      if (!this.historyRecords || this.historyRecords.length === 0) {
        return []
      }

      // 过滤掉 lang 字段的修改记录
      const filteredRecords = this.historyRecords.filter(record =>
        record.field_name !== 'lang'
      )

      // 按照修改时间分组
      const groupedRecords = {}
      filteredRecords.forEach(record => {
        const timestamp = record.created_at
        if (!groupedRecords[timestamp]) {
          groupedRecords[timestamp] = {
            timestamp: timestamp,
            user_type: record.user_type,
            user_id: record.user_id,
            records: []
          }
        }
        groupedRecords[timestamp].records.push(record)
      })

      // 转换为数组并按时间倒序排序
      return Object.values(groupedRecords).sort((a, b) => {
        return new Date(b.timestamp) - new Date(a.timestamp)
      })
    },

    // 时间冲突标题
    timeConflictTitle() {
      if (this.conflictingReservations && this.conflictingReservations.length > 0) {
        return this.$t('reservation.timeConflictWith', { count: this.conflictingReservations.length })
      } else if (this.conflictMessage) {
        return this.conflictMessage
      } else {
        return this.$t('reservation.timeSlotOccupied')
      }
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

          // 检查是否是循环预约的子预约
          if (this.reservation.recurring_reservation_id) {
            this.isRecurringReservation = true
            this.recurringReservationId = this.reservation.recurring_reservation_id
            console.log('这是循环预约的子预约，循环预约ID:', this.recurringReservationId)
          }

          // 检查是否是从循环预约详情页面跳转过来的
          const isFromRecurring = this.$route.query.child === 'true' && this.$route.query.recurringId
          if (isFromRecurring) {
            this.recurringReservationId = this.$route.query.recurringId
            console.log('从循环预约详情页面跳转过来，循环预约ID:', this.recurringReservationId)
          }

          // 检查是否需要自动进入编辑模式
          this.$nextTick(() => {
            if (this.$route.query.edit === 'true' && this.canModify) {
              console.log('自动进入编辑模式')
              this.showModifyDialog()
            }
          })
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

      // 检查是否是从循环预约详情页面跳转过来的
      const isFromRecurring = this.$route.query.child === 'true' && this.recurringReservationId

      if (isFromRecurring) {
        // 如果是从循环预约详情页面跳转过来的，返回到循环预约详情页面
        console.log('ReservationDetail.goBack() - 返回到循环预约详情页面:', this.recurringReservationId)

        // 构建查询参数，保留用户联系方式等信息
        const query = {
          fromChild: 'true',
          reservation_number: this.reservation.reservation_number
        }

        // 保留用户联系方式参数（如果有）
        if (this.$route.query.userContact) {
          query.userContact = this.$route.query.userContact
        }

        // 保留来源参数（如果有）
        if (this.$route.query.from) {
          query.from = this.$route.query.from
        }

        this.$router.push({
          path: `/recurring-reservation/${this.recurringReservationId}`,
          query: query
        })
      } else {
        // 否则返回到个人预约管理页面
        console.log('ReservationDetail.goBack() - 返回到个人预约管理页面')

        // 检查是否有查询参数，如果有则恢复查询状态
        if (this.$route.query.from === 'query' && (this.$route.query.userContact || this.$route.query.reservationCode)) {
          // 构建查询参数来恢复查询状态
          const queryParams = {}

          if (this.$route.query.userContact) {
            queryParams.userContact = this.$route.query.userContact
          }

          if (this.$route.query.reservationCode) {
            queryParams.reservationCode = this.$route.query.reservationCode
          }

          // 添加一个标记表示需要自动执行查询
          queryParams.autoQuery = 'true'

          console.log('ReservationDetail.goBack() - 恢复查询状态:', queryParams)

          this.$router.push({
            path: '/reservation/query',
            query: queryParams
          })
        } else {
          // 没有查询参数，直接返回空白查询页面
          this.$router.push('/reservation/query')
        }
      }
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

          // 设置一个延迟，让用户看到状态变化后再跳转
          setTimeout(() => {
            // 检查是否是从循环预约详情页面跳转过来的
            const isFromRecurring = this.$route.query.child === 'true' && this.recurringReservationId

            if (isFromRecurring) {
              // 如果是从循环预约详情页面跳转过来的，返回到循环预约详情页面
              const query = {
                fromChild: 'true',
                reservation_number: this.reservation.reservation_number
              }

              // 保留用户联系方式参数（如果有）
              if (this.$route.query.userContact) {
                query.userContact = this.$route.query.userContact
              }

              this.$router.push({
                path: `/recurring-reservation/${this.recurringReservationId}`,
                query: query
              })
            } else {
              // 否则返回到预约管理页面，恢复查询状态
              if (this.$route.query.from === 'query' && (this.$route.query.userContact || this.$route.query.reservationCode)) {
                const queryParams = {}

                if (this.$route.query.userContact) {
                  queryParams.userContact = this.$route.query.userContact
                }

                if (this.$route.query.reservationCode) {
                  queryParams.reservationCode = this.$route.query.reservationCode
                }

                queryParams.autoQuery = 'true'

                this.$router.push({
                  path: '/reservation/query',
                  query: queryParams
                })
              } else {
                this.$router.push('/reservation/query')
              }
            }
          }, 1500) // 增加延迟时间，让用户有更多时间看到状态变化
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

          // 设置一个延迟，让用户看到状态变化后再跳转
          setTimeout(() => {
            // 检查是否是从循环预约详情页面跳转过来的
            const isFromRecurring = this.$route.query.child === 'true' && this.recurringReservationId

            if (isFromRecurring) {
              // 如果是从循环预约详情页面跳转过来的，返回到循环预约详情页面
              const query = {
                fromChild: 'true',
                reservation_number: this.reservation.reservation_number
              }

              // 保留用户联系方式参数（如果有）
              if (this.$route.query.userContact) {
                query.userContact = this.$route.query.userContact
              }

              this.$router.push({
                path: `/recurring-reservation/${this.recurringReservationId}`,
                query: query
              })
            } else {
              // 否则返回到预约管理页面，恢复查询状态
              if (this.$route.query.from === 'query' && (this.$route.query.userContact || this.$route.query.reservationCode)) {
                const queryParams = {}

                if (this.$route.query.userContact) {
                  queryParams.userContact = this.$route.query.userContact
                }

                if (this.$route.query.reservationCode) {
                  queryParams.reservationCode = this.$route.query.reservationCode
                }

                queryParams.autoQuery = 'true'

                this.$router.push({
                  path: '/reservation/query',
                  query: queryParams
                })
              } else {
                this.$router.push('/reservation/query')
              }
            }
          }, 1500) // 增加延迟时间，让用户有更多时间看到状态变化
        } else {
          this.$message.error(response.data.message || this.$t('reservation.returnFailed'))
        }
      } catch (error) {
        console.error('Failed to return equipment:', error)
        this.$message.error(this.$t('reservation.returnFailed'))
      } finally {
        this.returning = false
      }
    },

    // 禁用日期（今天之前的日期不可选）
    disabledDate(time) {
      return time.getTime() < Date.now() - 8.64e7 // 8.64e7是一天的毫秒数
    },

    // 显示修改对话框
    showModifyDialog() {
      // 初始化表单数据
      this.modifyForm = {
        startDateTime: this.reservation.start_datetime,
        endDateTime: this.reservation.end_datetime,
        purpose: this.reservation.purpose || '',
        userEmail: this.reservation.user_email || ''
      }

      // 显示对话框
      this.modifyDialogVisible = true
    },

    // 验证时间范围
    validateTimeRange() {
      const startTime = new Date(this.modifyForm.startDateTime)
      const endTime = new Date(this.modifyForm.endDateTime)

      if (startTime >= endTime) {
        this.$message.error(this.$t('reservation.invalidTime'))
        return false
      }

      return true
    },

    // 检查时间可用性
    async checkTimeAvailability() {
      if (!this.modifyForm.startDateTime || !this.modifyForm.endDateTime) {
        this.timeAvailabilityChecked = false
        return
      }

      // 添加更严格的验证
      if (this.modifyForm.startDateTime >= this.modifyForm.endDateTime) {
        this.$message.warning(this.$t('reservation.invalidTime'))
        this.timeConflict = true
        this.timeAvailabilityChecked = false
        return
      }

      try {
        const equipmentId = this.reservation.equipment_id
        const startDate = this.modifyForm.startDateTime
        const endDate = this.modifyForm.endDateTime

        // 调用API检查时间可用性，排除当前预定
        const excludeId = this.reservation.id
        const params = {
          start_date: startDate,
          end_date: endDate
        }

        // 只有当excludeId存在且不为null/undefined时才添加参数
        if (excludeId != null && excludeId !== undefined) {
          params.exclude_reservation_id = excludeId
        }



        const response = await this.$http.get(`/api/equipment/${equipmentId}/availability`, { params })

        // 检查是否有冲突 - 处理API响应格式
        if (response.data.specific_time_check) {
          // 如果是具体时间段检查
          console.log('具体时间段检查结果:', response.data.available)
          this.timeConflict = response.data.available.includes(false)
        } else {
          // 如果是按日期检查
          console.log('按日期检查结果:', response.data.available)
          this.timeConflict = response.data.available.includes(false)
        }

        // 设置冲突信息
        if (this.timeConflict) {
          console.log('检测到时间冲突:', response.data.available)

          // 获取冲突的预定信息
          this.conflictingReservations = response.data.conflicting_reservations || []

          // 检查是否是因为达到最大同时预定数量
          if (response.data.allow_simultaneous && response.data.max_simultaneous > 1) {
            this.conflictMessage = this.$t('reservation.maxSimultaneousReached', { count: response.data.max_simultaneous });
          } else {
            this.conflictMessage = '';
          }
        } else {
          console.log('时间段可用')
          this.conflictMessage = '';
          this.conflictingReservations = [];
        }

        this.timeAvailabilityChecked = true
      } catch (error) {
        console.error('Failed to check availability:', error)
        this.timeConflict = true
        this.timeAvailabilityChecked = false
        this.conflictingReservations = []
        this.$message.error(this.$t('common.error'))
      }
    },

    // 查看修改历史
    async showHistory() {
      this.historyDialogVisible = true
      this.loadingHistory = true

      try {
        // 传递预约码和预约序号
        const response = await reservationApi.getReservationHistory(
          this.reservation.reservation_code,
          this.reservation.reservation_number
        )

        if (response.data.success) {
          this.historyRecords = response.data.data
        } else {
          this.$message.error(response.data.message || this.$t('reservation.historyFetchFailed'))
          this.historyRecords = []
        }
      } catch (error) {
        console.error('Failed to fetch history:', error)
        this.$message.error(this.$t('reservation.historyFetchFailed'))
        this.historyRecords = []
      } finally {
        this.loadingHistory = false
      }
    },

    // 获取历史记录项类型
    getHistoryItemType(action) {
      const typeMap = {
        'update': 'primary',
        'status_change': 'success'
      }
      return typeMap[action] || 'info'
    },

    // 获取历史记录操作文本
    getHistoryActionText(action) {
      const actionMap = {
        'update': this.$t('reservation.modified'),
        'create': this.$t('reservation.created'),
        'delete': this.$t('reservation.deleted'),
        'status_change': this.$t('reservation.statusChanged')
      }
      return actionMap[action] || action
    },

    // 获取字段显示名称
    getFieldDisplayName(fieldName) {
      const fieldMap = {
        'start_datetime': this.$t('reservation.startTime'),
        'end_datetime': this.$t('reservation.endTime'),
        'purpose': this.$t('reservation.purpose'),
        'user_email': this.$t('reservation.userEmail'),
        'status': this.$t('reservation.status')
      }
      return fieldMap[fieldName] || fieldName
    },

    // 格式化历史记录值
    formatHistoryValue(fieldName, value) {
      if (!value) return '-'

      if (fieldName === 'start_datetime' || fieldName === 'end_datetime') {
        return formatDate(value, 'YYYY-MM-DD HH:mm:ss', false) // 设置toBeijingTime为false，不进行时区转换
      } else if (fieldName === 'status') {
        return this.getStatusText(value)
      }

      return value
    },

    // 查看循环预约详情
    viewRecurringReservation() {
      if (!this.reservation || !this.reservation.recurring_reservation_id) return;

      // 跳转到循环预约详情页面，并传递来源信息和预约码
      this.$router.push({
        path: `/recurring-reservation/${this.reservation.recurring_reservation_id}`,
        query: {
          fromAdmin: this.isAdmin ? 'true' : 'false',
          reservationCode: this.reservation.reservation_code
        }
      });
    },

    // 提交修改表单
    submitModifyForm() {
      this.$refs.modifyForm.validate(async valid => {
        if (!valid) return

        // 验证时间范围
        if (!this.validateTimeRange()) return

        // 检查时间冲突
        if (this.timeConflict) {
          this.$message.error(this.$t('reservation.timeConflict'))
          return
        }

        this.modifying = true
        try {
          // 构建更新数据
          const updateData = {
            start_datetime: this.modifyForm.startDateTime,
            end_datetime: this.modifyForm.endDateTime,
            purpose: this.modifyForm.purpose || undefined,
            user_email: this.modifyForm.userEmail || undefined,
            lang: this.$i18n.locale
          }

          // 调用更新API - 传递预约序号以确保修改正确的子预约
          const response = await reservationApi.updateReservation(
            this.reservation.reservation_code,
            updateData,
            this.reservation.reservation_number  // 传递预约序号
          )

          if (response.data.success) {
            this.$message.success(this.$t('reservation.updateSuccess'))
            this.modifyDialogVisible = false
            // 重新获取预定信息
            await this.fetchReservation()
          } else {
            this.$message.error(response.data.message || this.$t('reservation.updateFailed'))
          }
        } catch (error) {
          console.error('Failed to update reservation:', error)
          this.$message.error(this.$t('reservation.updateFailed'))
        } finally {
          this.modifying = false
        }
      })
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

.history-card {
  margin-bottom: 10px;
}

.history-time {
  font-weight: bold;
  margin-bottom: 10px;
  color: #ff7c40;
  font-size: 16px;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 10px;
}

.history-user {
  font-weight: bold;
  margin-bottom: 10px;
  color: #606266;
}

.history-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #ebeef5;
}

.history-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.history-action {
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 14px;
}

.history-field {
  color: #409eff;
}

.history-values {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 10px;
  font-size: 13px;
}

.history-old-value, .history-new-value {
  display: flex;
  align-items: flex-start;
}

.history-old-value {
  color: #F56C6C;
}

.history-new-value {
  color: #67C23A;
}

.history-label {
  font-weight: bold;
  margin-right: 10px;
  min-width: 80px;
  color: #606266;
}

.detail-card, .user-card {
  margin-bottom: 20px;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}
</style>
