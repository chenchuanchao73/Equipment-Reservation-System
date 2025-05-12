<template>
  <div class="admin-reservation-detail">
    <div class="page-header">
      <h1 class="page-title">{{ $t('reservation.detail') }}</h1>
      <el-button @click="goBack" icon="el-icon-back">
        {{ $t('common.back') }}
      </el-button>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <el-card v-else-if="!reservation" class="error-card">
      <div class="error-message">
        <i class="el-icon-warning-outline"></i>
        <p>{{ $t('reservation.reservationNotFound') }}</p>
      </div>
      <el-button type="primary" @click="goBack">
        {{ $t('common.back') }}
      </el-button>
    </el-card>

    <div v-else>
      <!-- 预定详情卡片 -->
      <el-card shadow="hover" class="detail-card">
        <div slot="header" class="card-header">
          <span>{{ $t('reservation.detail') }}</span>
          <el-tag :type="displayStatusType">
            {{ displayStatusText }}
          </el-tag>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item :label="$t('reservation.code')">
            {{ reservation.reservation_code }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.status')">
            <el-tag :type="displayStatusType">
              {{ displayStatusText }}
            </el-tag>
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.equipmentName')">
            <router-link :to="`/equipment/${reservation.equipment_id}`">
              {{ reservation.equipment_name }}
            </router-link>
          </el-descriptions-item>

          <el-descriptions-item :label="$t('common.createTime')">
            {{ formatDateTime(reservation.created_at) }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.startTime')">
            {{ formatDateTime(reservation.start_datetime) }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.endTime')">
            {{ formatDateTime(reservation.end_datetime) }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userName')">
            {{ reservation.user_name }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userDepartment')">
            {{ reservation.user_department }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userContact')">
            {{ reservation.user_contact }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.userEmail')">
            {{ reservation.user_email || '-' }}
          </el-descriptions-item>

          <el-descriptions-item :label="$t('reservation.purpose')" :span="2">
            {{ reservation.purpose || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="actions">
          <!-- 已确认且未开始的预约才显示取消按钮 -->
          <el-button
            v-if="displayStatusText === $t('reservation.confirmed')"
            type="danger"
            @click="handleCancel"
          >
            {{ $t('reservation.cancelReservation') }}
          </el-button>

          <!-- 使用中的预约才显示提前归还按钮 -->
          <el-button
            v-if="displayStatusText === $t('reservation.inUse')"
            type="primary"
            @click="handleReturn"
          >
            {{ $t('reservation.earlyReturn') }}
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 取消预定确认对话框 -->
    <el-dialog
      :title="$t('common.warning')"
      :visible.sync="cancelDialogVisible"
      width="30%"
    >
      <span>{{ $t('reservation.confirmCancel') }}</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="cancelDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="danger" @click="confirmCancel" :loading="submitting">{{ $t('common.confirm') }}</el-button>
      </span>
    </el-dialog>

    <!-- 提前归还确认对话框 -->
    <el-dialog
      :title="$t('reservation.earlyReturn')"
      :visible.sync="returnDialogVisible"
      width="30%"
    >
      <span>{{ $t('reservation.confirmEarlyReturn') }}</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="returnDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmReturn" :loading="submitting">{{ $t('common.confirm') }}</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { reservationApi } from '@/api'
import { isReservationExpired } from '@/utils/date'

export default {
  name: 'AdminReservationDetail',

  data() {
    return {
      loading: false,
      submitting: false,
      reservation: null,
      cancelDialogVisible: false,
      returnDialogVisible: false,
      // 强制显示状态值 - 用于覆盖计算属性的显示
      forcedStatusText: null,
      forcedStatusType: null,
      // 添加日期匹配标志
      dateMatches: false,
      // 用于记录状态变更
      statusUpdated: false,
      forcedStatus: null,
      // 添加特定预约状态缓存标识
      reservationStatusCacheKey: ''
    }
  },

  created() {
    this.fetchReservation()

    // 注册页面刷新事件监听器
    window.addEventListener('beforeunload', this.saveState)
  },

  destroyed() {
    // 移除事件监听器，避免内存泄漏
    window.removeEventListener('beforeunload', this.saveState)
  },

  mounted() {
    this.loadReservation();
  },

  // 监听路由参数变化，当路由参数变化时重新获取数据
  watch: {
    '$route': {
      handler: function(to, from) {
        // 如果路由参数发生变化，重新获取数据
        if (to.params.code !== from.params.code ||
            to.query.reservationNumber !== from.query.reservationNumber) {
          console.log('路由参数变化，重新获取数据')
          this.fetchReservation()
        }
      },
      deep: true
    }
  },

  // 在路由参数变化时调用
  beforeRouteUpdate(to, from, next) {
    console.log('路由参数更新，重新获取数据')
    this.fetchReservation()
    next()
  },

  computed: {
    getStatusTagText() {
      if (!this.reservation) return ''

      // 尝试恢复存储的状态
      const savedState = this.getSavedState()
      if (savedState && savedState.statusText) {
        console.log('Using saved status text:', savedState.statusText)
        return savedState.statusText
      }

      // 调用方法获取状态文本
      const statusText = this.getStatusText(this.reservation)
      console.log('Computed status text:', statusText)
      return statusText
    },

    getStatusTagType() {
      if (!this.reservation) return ''

      // 尝试恢复存储的状态
      const savedState = this.getSavedState()
      if (savedState && savedState.statusType) {
        console.log('Using saved status type:', savedState.statusType)
        return savedState.statusType
      }

      // 调用方法获取状态类型
      const statusType = this.getStatusType(this.reservation)
      console.log('Computed status type:', statusType)
      return statusType
    },
    // 获取显示的状态文本
    displayStatusText() {
      // 如果有URL传递的状态参数，最优先使用它
      if (this.$route.query.displayStatus) {
        console.log('使用URL传递的状态文本:', this.$route.query.displayStatus);
        return this.$route.query.displayStatus;
      }

      // 次高优先级：使用强制状态（针对操作后立即更新）
      if (this.forcedStatusText) {
        console.log('使用强制状态文本:', this.forcedStatusText);
        return this.forcedStatusText;
      }

      // 再次优先级：使用本地存储的状态
      const savedState = this.getSavedState();
      if (savedState && savedState.statusText) {
        console.log('使用本地存储的状态文本:', savedState.statusText);
        return savedState.statusText;
      }

      // 最低优先级：动态计算状态（实时计算）
      if (!this.reservation) return '';

      // 在这里添加实时计算逻辑，确保已过期和使用中状态能立即更新
      // 检查是否已过期
      const now = new Date();
      const endTime = new Date(this.reservation.end_datetime);
      if (endTime < now) {
        console.log('实时计算：预定已过期');
        return this.$t('reservation.expired');
      }

      // 检查是否使用中
      const startTime = new Date(this.reservation.start_datetime);
      if (now >= startTime && now <= endTime) {
        console.log('实时计算：预定使用中');
        return this.$t('reservation.inUse');
      }

      // 默认为已确认，但如果数据库中确实标记为已取消，则显示取消状态
      if (this.reservation.status === 'cancelled') {
        console.log('数据库标记为已取消');
        return this.$t('reservation.cancelled');
      }

      console.log('实时计算：预定已确认');
      return this.$t('reservation.confirmed');
    },

    // 获取显示的状态类型（用于样式）
    displayStatusType() {
      // 如果有URL传递的状态类型参数，最优先使用它
      if (this.$route.query.displayStatusType) {
        console.log('使用URL传递的状态类型:', this.$route.query.displayStatusType);
        return this.$route.query.displayStatusType;
      }

      // 次高优先级：使用强制状态类型（针对操作后立即更新）
      if (this.forcedStatusType) {
        console.log('使用强制状态类型:', this.forcedStatusType);
        return this.forcedStatusType;
      }

      // 再次优先级：使用本地存储的状态
      const savedState = this.getSavedState();
      if (savedState && savedState.statusType) {
        console.log('使用本地存储的状态类型:', savedState.statusType);
        return savedState.statusType;
      }

      // 最低优先级：动态计算状态类型（实时计算）
      if (!this.reservation) return '';

      // 实时计算逻辑，与状态文本保持一致
      const now = new Date();
      const endTime = new Date(this.reservation.end_datetime);

      if (endTime < now) {
        return 'warning';
      }

      const startTime = new Date(this.reservation.start_datetime);
      if (now >= startTime && now <= endTime) {
        return 'primary';
      }

      // 如果数据库中确实标记为已取消，则显示取消状态类型
      if (this.reservation.status === 'cancelled') {
        return 'danger';
      }

      return 'success';
    },
    formattedStartTime() {
      if (!this.reservation) return '';
      return this.formatDateTime(this.reservation.start_datetime);
    },
    formattedEndTime() {
      if (!this.reservation) return '';
      return this.formatDateTime(this.reservation.end_datetime);
    }
  },

  methods: {
    isReservationExpired,

    async fetchReservation() {
      this.loading = true

      try {
        const code = this.$route.params.code
        console.log('Fetching reservation with code:', code)

        // 获取URL中的查询参数（用于时间和状态）
        const startTime = this.$route.query.startTime
        const endTime = this.$route.query.endTime
        let reservationNumber = this.$route.query.reservationNumber

        // 如果URL中没有预约序号，尝试从localStorage中获取
        if (!reservationNumber) {
          const savedReservationNumber = localStorage.getItem('current_reservation_number')
          if (savedReservationNumber) {
            console.log('从localStorage中获取预约序号:', savedReservationNumber)
            reservationNumber = savedReservationNumber
          }
        }

        // 检查是否强制使用预约序号查询
        const forceUseReservationNumber = localStorage.getItem('force_use_reservation_number')
        if (forceUseReservationNumber === 'true') {
          console.log('强制使用预约序号查询')
          // 使用后清除标记
          localStorage.removeItem('force_use_reservation_number')
        }

        console.log('URL 时间参数:', startTime, endTime)
        console.log('预约序号:', reservationNumber)

        // 构建API请求参数
        let params = {}

        // 添加时间戳参数，确保每次都获取最新数据
        const timestamp = new Date().getTime()
        params._t = timestamp
        console.log('添加时间戳参数:', timestamp)

        // 只有当同时提供了开始和结束时间才添加到请求参数中
        if (startTime && endTime) {
          params.start_time = startTime
          params.end_time = endTime
          console.log('Including time parameters in API request:', params)
        }

        // 添加预约序号参数
        if (reservationNumber) {
          params.reservation_number = reservationNumber
          console.log('Including reservation number in API request:', params)
        }

        // 如果有预约序号，优先使用预约序号查询
        if (reservationNumber) {
          console.log('使用预约序号查询:', reservationNumber)
          try {
            const response = await reservationApi.getReservationByNumber(reservationNumber)
            console.log('通过预约序号查询结果:', response)

            // 如果通过预约序号查询成功，直接使用结果
            if (response.data && response.data.success) {
              console.log('通过预约序号查询成功')

              // 获取原始数据
              this.reservation = response.data.data
              console.log('Original reservation data:', this.reservation)

              // 检查是否需要显示预约序号通知
              const showNotification = localStorage.getItem('show_reservation_number_notification')
              if (showNotification === 'true') {
                // 显示预约序号信息
                this.$notify({
                  title: '预约详情',
                  message: `当前查看的是预约序号: ${this.reservation.reservation_number}`,
                  type: 'info',
                  duration: 5000
                })
                // 使用后清除标记
                localStorage.removeItem('show_reservation_number_notification')
              }

              // 重要：从URL参数中获取时间覆盖预约显示时间（这确保显示的时间与列表页一致）
              if (startTime && endTime) {
                console.log('使用URL参数覆盖显示时间 - 原始时间:', this.reservation.start_datetime, this.reservation.end_datetime)

                // 保存原始时间以备后用
                this.originalStartTime = this.reservation.start_datetime
                this.originalEndTime = this.reservation.end_datetime

                // 覆盖显示时间
                this.reservation.start_datetime = startTime
                this.reservation.end_datetime = endTime

                console.log('覆盖后的显示时间:', this.reservation.start_datetime, this.reservation.end_datetime)
              }

              // 添加详细日志，帮助调试状态判断
              console.log('Status from API:', this.reservation.status)
              console.log('Current time:', new Date())

              // 确保状态字段正确
              if (!this.reservation.status) {
                // 如果API返回的状态为空，默认设置为confirmed
                console.warn('API returned empty status, setting default to confirmed')
                this.reservation.status = 'confirmed'
              }

              // 重要：确保状态字段是正确的
              console.log(`最终数据库状态: ${this.reservation.status}，展示状态为: ${this.getStatusText(this.reservation)}`)

              this.loading = false
              return
            } else {
              console.warn('通过预约序号查询失败，将使用预约码查询')
            }
          } catch (error) {
            console.error('通过预约序号查询出错:', error)
            console.warn('将使用预约码查询')
          }
        }

        // 使用API进行请求，直接传递预定码和参数
        console.log('Calling API with code and params:', code, params)
        const response = await reservationApi.getReservationByCode(code, params)

        console.log('API Response:', response)

        if (response.data && response.data.success) {
          // 获取原始数据
          this.reservation = response.data.data
          console.log('Original reservation data:', this.reservation)

          // 显示预约序号信息（无论通过何种方式查询）
          if (this.reservation.reservation_number) {
            this.$notify({
              title: '预约详情',
              message: `当前查看的是预约序号: ${this.reservation.reservation_number}`,
              type: 'info',
              duration: 5000
            })
          }

          // 重要：从URL参数中获取时间覆盖预约显示时间（这确保显示的时间与列表页一致）
          if (startTime && endTime) {
            console.log('使用URL参数覆盖显示时间 - 原始时间:', this.reservation.start_datetime, this.reservation.end_datetime)

            // 保存原始时间以备后用
            this.originalStartTime = this.reservation.start_datetime
            this.originalEndTime = this.reservation.end_datetime

            // 覆盖显示时间
            this.reservation.start_datetime = startTime
            this.reservation.end_datetime = endTime

            console.log('覆盖后的显示时间:', this.reservation.start_datetime, this.reservation.end_datetime)
          }

          // 添加详细日志，帮助调试状态判断
          console.log('Status from API:', this.reservation.status)
          console.log('Current time:', new Date())

          // 确保状态字段正确
          if (!this.reservation.status) {
            // 如果API返回的状态为空，默认设置为confirmed
            console.warn('API returned empty status, setting default to confirmed')
            this.reservation.status = 'confirmed'
          }

          // 重要：现在只检查当前预约序号对应的缓存状态，不再通用应用
          if (this.reservation.reservation_number) {
            // 使用当前预约序号创建缓存键
            const cacheKey = `reservation_status_${this.reservation.reservation_number}`
            const cachedStatus = localStorage.getItem(cacheKey)

            if (cachedStatus) {
              try {
                const statusData = JSON.parse(cachedStatus)
                console.log('找到预约序号缓存状态:', statusData)

                // 验证是否为当前预约序号的状态
                if (statusData.reservationNumber === this.reservation.reservation_number) {
                  // 如果缓存中标记为已取消，则覆盖API返回的状态
                  if (statusData.dbStatus === 'cancelled' || statusData.forcedStatus === 'cancelled') {
                    console.log('使用缓存中的已取消状态覆盖API返回状态，仅适用于预约序号:', this.reservation.reservation_number)
                    this.reservation.status = 'cancelled'
                    this.forcedStatus = 'cancelled'
                    this.forcedStatusText = this.$t('reservation.cancelled')
                    this.forcedStatusType = 'danger'
                  }
                } else {
                  console.log('缓存状态预约序号不匹配，不应用缓存状态')
                }
              } catch (e) {
                console.error('解析缓存状态出错:', e)
              }
            }
          }

          // 重要：确保状态字段是正确的
          console.log(`最终数据库状态: ${this.reservation.status}，展示状态为: ${this.getStatusText(this.reservation)}`)
        } else {
          const errorMsg = response.data ? response.data.message : this.$t('reservation.reservationNotFound')
          this.$message.error(errorMsg)
          this.reservation = null
        }
      } catch (error) {
        console.error('Failed to fetch reservation:', error)
        this.$message.error(this.$t('error.serverError'))
        this.reservation = null
      } finally {
        this.loading = false
      }
    },

    async loadReservation() {
      try {
        this.loading = true;
        // 获取预约码
        const code = this.$route.params.code;
        if (!code) {
          this.error = '预约码不存在';
          this.loading = false;
          return;
        }

        // 构建查询参数，确保传递日期时间参数
        const params = {};

        // 添加时间戳参数，确保每次都获取最新数据
        const timestamp = new Date().getTime()
        params._t = timestamp
        console.log('添加时间戳参数:', timestamp)

        // 从URL获取日期时间参数
        const startTime = this.$route.query.startTime;
        const endTime = this.$route.query.endTime;

        if (startTime) {
          params.start_time = startTime;
          console.log('查询开始时间:', startTime);
        }
        if (endTime) {
          params.end_time = endTime;
          console.log('查询结束时间:', endTime);
        }

        // 获取预约信息
        const response = await this.$api.reservation.getReservationByCode(code, params);
        console.log('预约API响应:', response);

        if (response.success) {
          this.reservation = response.data;

          // 设置日期匹配标志
          this.dateMatches = !!response.data.date_matches;
          console.log('日期是否匹配:', this.dateMatches);

          // 设置预约状态信息
          if (this.reservation.status === 'confirmed') {
            this.statusText = this.$t('reservation.confirmed');
            this.statusType = 'success';
          } else if (this.reservation.status === 'cancelled') {
            this.statusText = this.$t('reservation.cancelled');
            this.statusType = 'danger';

            // 如果日期匹配且状态为cancelled，强制使用取消状态
            if (this.dateMatches) {
              this.forcedStatus = 'cancelled';
              console.log('强制使用取消状态');
            }
          }

          // 如果有设备ID，获取设备详情
          if (this.reservation.equipment_id) {
            this.loadEquipment(this.reservation.equipment_id);
          }
        } else {
          this.error = response.message || '获取预约信息失败';
        }
      } catch (error) {
        console.error('加载预约详情出错:', error);
        this.error = '加载预约详情出错: ' + (error.message || error);
      } finally {
        this.loading = false;
      }
    },

    formatDateTime(dateString) {
      if (!dateString) return '-'

      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

    // 获取状态文本
    getStatusText(reservation) {
      // 首先检查状态是否直接来自API响应
      console.log('Checking status from API:', reservation.status);

      // 如果API明确返回了cancelled状态，显示已取消
      if (reservation.status === 'cancelled') {
        console.log('Using cancelled status from API');
        return this.$t('reservation.cancelled');
      }

      // 其他状态根据时间动态计算
      if (isReservationExpired(reservation.end_datetime)) {
        console.log('Calculated status: expired');
        return this.$t('reservation.expired');
      }

      // 如果预约正在进行中，显示"使用中"
      const now = new Date();
      const start = new Date(reservation.start_datetime);
      const end = new Date(reservation.end_datetime);
      if (now >= start && now <= end) {
        console.log('Calculated status: in use');
        return this.$t('reservation.inUse');
      }

      // 如果预约已确认且未开始，显示"已确认"
      console.log('Calculated status: confirmed');
      return this.$t('reservation.confirmed');
    },

    // 获取状态类型（样式）
    getStatusType(reservation) {
      // 首先检查状态是否直接来自API响应
      if (reservation.status === 'cancelled') {
        return 'danger';
      }

      // 如果预约已过期，返回橙色
      if (isReservationExpired(reservation.end_datetime)) {
        return 'warning';
      }

      // 如果预约正在进行中，返回蓝色
      const now = new Date();
      const start = new Date(reservation.start_datetime);
      const end = new Date(reservation.end_datetime);
      if (now >= start && now <= end) {
        return 'primary';
      }

      // 如果预约已确认且未开始，返回绿色
      return 'success';
    },

    // 判断预约是否正在进行中
    isReservationInProgress(reservation) {
      if (!reservation) return false

      const now = new Date()
      const start = new Date(reservation.start_datetime)
      const end = new Date(reservation.end_datetime)

      // 当前时间在开始时间和结束时间之间
      return now >= start && now <= end
    },

    handleCancel() {
      this.cancelDialogVisible = true
    },

    handleReturn() {
      this.returnDialogVisible = true
    },

    async confirmCancel() {
      this.submitting = true

      try {
        // 检查是否是循环预约的子预约
        if (this.reservation.recurring_reservation_id) {
          console.log('Cancelling a child reservation of recurring reservation:', this.reservation.recurring_reservation_id)

          // 获取当前预约的详细信息
          const reservationCode = this.reservation.reservation_code
          const reservationNumber = this.reservation.reservation_number

          // 取消单个子预约
          const response = await reservationApi.cancelReservation(reservationCode)

          console.log('Cancel child reservation response:', response)

          // 无论API响应成功与否，检查返回消息以确定实际状态
          if (response.data) {
            // 特殊处理：如果消息表明预定已经取消，视为成功
            if (response.data.message === '预定已取消' || response.data.message.includes('已取消')) {
              console.log('预定已经处于取消状态，视为取消成功');

              // 关闭取消对话框
              this.cancelDialogVisible = false

              // 立即更新预约状态，不等待API重新获取
              this.reservation.status = 'cancelled'

              // 立即更新UI显示的状态
              this.forceUpdateStatus('cancelled')

              // 关键改进：同时保存预约序号的状态
              if (reservationNumber) {
                this.saveStatusByReservationNumber(reservationNumber, 'cancelled')
              }

              // 显示成功消息
              this.$message.success(this.$t('reservation.cancelSuccess'))

              // 提示用户返回循环预约详情页面
              this.$confirm(
                '已成功取消此子预约。是否查看循环预约详情？',
                '操作成功',
                {
                  confirmButtonText: '查看循环预约',
                  cancelButtonText: '留在当前页面',
                  type: 'success'
                }
              ).then(() => {
                // 跳转到循环预约详情页面
                this.$router.push(`/admin/recurring-reservation/${this.reservation.recurring_reservation_id}`)
              }).catch(() => {
                // 用户选择留在当前页面，直接重新获取预定信息
                this.fetchReservation()
              })
              return;
            } else if (response.data.success) {
              // 常规成功响应处理
              // 关闭取消对话框
              this.cancelDialogVisible = false

              // 立即更新预约状态，不等待API重新获取
              this.reservation.status = 'cancelled'

              // 立即更新UI显示的状态
              this.forceUpdateStatus('cancelled')

              // 关键改进：同时保存预约序号的状态
              if (reservationNumber) {
                this.saveStatusByReservationNumber(reservationNumber, 'cancelled')
              }

              // 显示成功消息
              this.$message.success(this.$t('reservation.cancelSuccess'))

              // 提示用户返回循环预约详情页面
              this.$confirm(
                '已成功取消此子预约。是否查看循环预约详情？',
                '操作成功',
                {
                  confirmButtonText: '查看循环预约',
                  cancelButtonText: '留在当前页面',
                  type: 'success'
                }
              ).then(() => {
                // 跳转到循环预约详情页面
                this.$router.push(`/admin/recurring-reservation/${this.reservation.recurring_reservation_id}`)
              }).catch(() => {
                // 用户选择留在当前页面，直接重新获取预定信息
                this.fetchReservation()
              })
            } else {
              // 真正的错误消息
              const errorMsg = response.data.message || this.$t('reservation.cancelFailed')
              this.$message.error(errorMsg)
              // 关闭取消对话框
              this.cancelDialogVisible = false
            }
          }
        } else {
          // 普通预约的取消逻辑
          // 添加预约序号参数，确保只取消特定的子预约
          const data = {}

          // 添加预约序号参数，确保只取消特定的子预约
          if (this.reservation.reservation_number) {
            data.reservation_number = this.reservation.reservation_number
            console.log('预约序号参数存在:', this.reservation.reservation_number)
          } else {
            console.warn('预约序号参数不存在，将取消所有具有相同预约码的预约')
          }

          console.log('取消预约请求参数:', data)

          const response = await reservationApi.cancelReservation(this.reservation.reservation_code, data)

          console.log('Cancel response:', response)

          // 无论API响应成功与否，检查返回消息以确定实际状态
          if (response.data) {
            // 特殊处理：如果消息表明预定已经取消，视为成功
            if (response.data.message === '预定已取消' || response.data.message.includes('已取消')) {
              console.log('预定已经处于取消状态，视为取消成功');

              // 关闭取消对话框
              this.cancelDialogVisible = false

              // 显示成功消息
              this.$message.success(this.$t('reservation.cancelSuccess'))

              // 直接刷新整个页面，确保获取最新数据
              console.log('预约已取消，即将刷新页面...')

              // 设置一个短暂的延迟，让用户看到成功消息
              setTimeout(() => {
                // 强制刷新整个页面，包括所有资源
                window.location.href = '#/admin/reservation'
                window.location.reload(true)
              }, 1000)
              return;
            } else if (response.data.success) {
              // 常规成功响应处理
              // 关闭取消对话框
              this.cancelDialogVisible = false

              // 显示成功消息
              this.$message.success(this.$t('reservation.cancelSuccess'))

              // 直接刷新整个页面，确保获取最新数据
              console.log('预约已取消，即将刷新页面...')

              // 设置一个短暂的延迟，让用户看到成功消息
              setTimeout(() => {
                // 强制刷新整个页面，包括所有资源
                window.location.href = '#/admin/reservation'
                window.location.reload(true)
              }, 1000)
            } else {
              // 真正的错误消息
              const errorMsg = response.data.message || this.$t('reservation.cancelFailed')
              this.$message.error(errorMsg)
              // 关闭取消对话框
              this.cancelDialogVisible = false
            }
          }
        }
      } catch (error) {
        console.error('Failed to cancel reservation:', error)
        this.$message.error(this.$t('error.serverError'))
        // 关闭取消对话框
        this.cancelDialogVisible = false
      } finally {
        this.submitting = false
      }
    },

    async confirmReturn() {
      this.submitting = true

      try {
        // 使用取消预定的API，但添加early_return参数和预约序号参数
        const data = {
          early_return: true
        }

        // 添加预约序号参数，确保只取消特定的子预约
        if (this.reservation.reservation_number) {
          data.reservation_number = this.reservation.reservation_number
          console.log('提前归还 - 预约序号参数存在:', this.reservation.reservation_number)
        } else {
          console.warn('提前归还 - 预约序号参数不存在，将取消所有具有相同预约码的预约')
        }

        console.log('提前归还 - 请求参数:', data)

        const response = await reservationApi.cancelReservation(this.reservation.reservation_code, data)

        console.log('Return response:', response)

        if (response.data && response.data.success) {
          // 关闭对话框
          this.returnDialogVisible = false

          // 显示成功消息
          this.$message.success(this.$t('reservation.returnSuccess'))

          // 直接重新获取预定信息
          this.fetchReservation()
        } else {
          const errorMsg = response.data ? response.data.message : this.$t('reservation.returnFailed')
          this.$message.error(errorMsg)
          this.returnDialogVisible = false
        }
      } catch (error) {
        console.error('Failed to return equipment:', error)
        this.$message.error(this.$t('error.serverError'))
        this.returnDialogVisible = false
      } finally {
        this.submitting = false
      }
    },

    goBack() {
      // 使用浏览器的历史记录返回，而不是直接跳转
      if (window.history.length > 1) {
        this.$router.go(-1); // 返回上一页
      } else {
        // 如果没有历史记录，则导航到预定管理页面
        this.$router.push('/admin/reservation');
      }
    },

    // 状态保存相关方法
    saveState() {
      if (!this.reservation) return

      // 计算当前状态
      const statusText = this.getStatusText(this.reservation)
      const statusType = this.getStatusType(this.reservation)

      // 将状态保存到localStorage
      const stateKey = `reservation_status_${this.reservation.reservation_code}`
      const state = {
        statusText,
        statusType,
        timestamp: new Date().getTime()
      }

      console.log('Saving state to localStorage:', state)
      localStorage.setItem(stateKey, JSON.stringify(state))
    },

    getSavedState() {
      if (!this.reservation) return null

      // 从localStorage获取状态
      const stateKey = `reservation_status_${this.reservation.reservation_code}`
      const savedStateStr = localStorage.getItem(stateKey)

      if (!savedStateStr) return null

      try {
        const savedState = JSON.parse(savedStateStr)
        console.log('Retrieved saved state:', savedState)

        // 检查保存的状态是否过期（超过5分钟）
        const now = new Date().getTime()
        const fiveMinutes = 5 * 60 * 1000
        if (now - savedState.timestamp > fiveMinutes) {
          console.log('Saved state is expired, removing it')
          localStorage.removeItem(stateKey)
          return null
        }

        return savedState
      } catch (e) {
        console.error('Error parsing saved state:', e)
        return null
      }
    },

    // 更新URL中的状态参数
    updateUrlWithNewStatus(newStatus) {
      console.log('更新URL状态为:', newStatus);

      // 获取当前状态对应的文本和类型
      let statusText = '';
      let statusType = '';

      if (newStatus === 'cancelled') {
        statusText = this.$t('reservation.cancelled');
        statusType = 'danger';
      } else if (newStatus === 'confirmed') {
        const now = new Date();
        const start = new Date(this.reservation.start_datetime);
        const end = new Date(this.reservation.end_datetime);

        if (now >= start && now <= end) {
          // 使用中
          statusText = this.$t('reservation.inUse');
          statusType = 'primary';
        } else if (isReservationExpired(this.reservation.end_datetime)) {
          // 已过期
          statusText = this.$t('reservation.expired');
          statusType = 'warning';
        } else {
          // 已确认
          statusText = this.$t('reservation.confirmed');
          statusType = 'success';
        }
      }

      console.log('新状态文本和类型:', statusText, statusType);

      // 更新路由参数，但不触发路由变化
      const query = { ...this.$route.query, displayStatus: statusText, displayStatusType: statusType };

      // 更新URL但不重新加载页面
      this.$router.replace({
        path: this.$route.path,
        query
      }).catch(err => {
        // 忽略重复导航错误
        if (err.name !== 'NavigationDuplicated') {
          throw err;
        }
      });
    },

    // 强制更新状态显示（用于操作后立即更新UI）
    forceUpdateStatus(newStatus) {
      console.log('强制更新状态为:', newStatus);

      // 更新状态文本和类型
      let statusText = '';
      let statusType = '';

      if (newStatus === 'cancelled') {
        statusText = this.$t('reservation.cancelled');
        statusType = 'danger';

        // 只为当前操作的预约添加永久状态标记，不影响其他预约
        if (this.reservation && this.reservation.reservation_number) {
          // 仅使用预约序号作为键保存状态，不再使用预约代码
          const stateKey = `reservation_status_${this.reservation.reservation_number}`;
          const state = {
            statusText: this.$t('reservation.cancelled'),
            statusType: 'danger',
            dbStatus: 'cancelled',
            forcedStatus: 'cancelled',
            timestamp: new Date().getTime(),
            permanent: true,
            reservationNumber: this.reservation.reservation_number
          };
          console.log('永久保存特定预约序号的已取消状态:', state);
          localStorage.setItem(stateKey, JSON.stringify(state));
        }

        // 确保数据模型中的状态也是正确的
        if (this.reservation) {
          this.reservation.status = 'cancelled';
        }

        // 强制状态文本和类型
        this.forcedStatusText = statusText;
        this.forcedStatusType = statusType;
        this.forcedStatus = 'cancelled';
      } else if (newStatus === 'confirmed') {
        const now = new Date();
        const start = new Date(this.reservation.start_datetime);
        const end = new Date(this.reservation.end_datetime);

        if (now >= start && now <= end) {
          // 使用中
          statusText = this.$t('reservation.inUse');
          statusType = 'primary';
        } else if (isReservationExpired(this.reservation.end_datetime)) {
          // 已过期
          statusText = this.$t('reservation.expired');
          statusType = 'warning';
        } else {
          // 已确认
          statusText = this.$t('reservation.confirmed');
          statusType = 'success';
        }

        // 确保数据模型中的状态也是正确的
        if (this.reservation) {
          this.reservation.status = 'confirmed';

          // 如果当前预约曾被标记为取消，则移除该标记
          if (this.reservation.reservation_number) {
            const stateKey = `reservation_status_${this.reservation.reservation_number}`;
            localStorage.removeItem(stateKey);
          }
        }

        // 强制状态文本和类型
        this.forcedStatusText = statusText;
        this.forcedStatusType = statusType;
        this.forcedStatus = 'confirmed';
      }

      // 更新路由状态参数
      this.updateUrlWithNewStatus(newStatus);
    },

    // 修改方法：通过预约序号保存状态
    saveStatusByReservationNumber(reservationNumber, status) {
      if (!reservationNumber) return;

      console.log('通过预约序号保存状态:', reservationNumber, status);

      // 创建缓存键
      const cacheKey = `reservation_status_${reservationNumber}`;

      let statusText = '';
      let statusType = '';

      if (status === 'cancelled') {
        statusText = this.$t('reservation.cancelled');
        statusType = 'danger';
      } else if (status === 'confirmed') {
        statusText = this.$t('reservation.confirmed');
        statusType = 'success';
      }

      // 保存状态到本地存储，确保包含预约序号信息
      const state = {
        statusText,
        statusType,
        dbStatus: status,
        forcedStatus: status,
        timestamp: new Date().getTime(),
        permanent: true,
        reservationNumber: reservationNumber
      };

      console.log('保存预约序号状态到缓存:', cacheKey, state);
      localStorage.setItem(cacheKey, JSON.stringify(state));
    },

    // 检查URL时间参数是否与预定时间匹配
    isTimeMatching(urlStartTime, urlEndTime, resStartTime, resEndTime) {
      if (!urlStartTime || !urlEndTime || !resStartTime || !resEndTime) {
        return false;
      }

      console.log('比较时间参数:', {
        urlStartTime,
        urlEndTime,
        resStartTime,
        resEndTime
      });

      // 将所有时间转换为字符串以便比较
      const formatTime = (timeStr) => {
        try {
          // 处理可能的日期格式
          const date = new Date(timeStr);
          if (isNaN(date.getTime())) {
            // 如果无法解析为日期，直接使用原始字符串
            return timeStr;
          }

          // 将日期格式化为 YYYY-MM-DD 的形式
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');

          // 返回日期部分，用于匹配同一天的不同预定
          return `${year}-${month}-${day}`;
        } catch (e) {
          console.error('格式化时间出错:', e);
          return timeStr;
        }
      };

      const urlStartFormatted = formatTime(urlStartTime);
      const urlEndFormatted = formatTime(urlEndTime);
      const resStartFormatted = formatTime(resStartTime);
      const resEndFormatted = formatTime(resEndTime);

      console.log('格式化后的时间比较:', {
        urlStartFormatted,
        urlEndFormatted,
        resStartFormatted,
        resEndFormatted
      });

      // 判断日期是否匹配（只比较日期部分）
      const isMatch = urlStartFormatted === resStartFormatted && urlEndFormatted === resEndFormatted;

      console.log('时间匹配结果:', isMatch);

      return isMatch;
    },

    // 检查URL时间参数是否与预定时间精确匹配（包括时间部分）
    isExactTimeMatching(urlStartTime, urlEndTime, resStartTime, resEndTime) {
      if (!urlStartTime || !urlEndTime || !resStartTime || !resEndTime) {
        return false;
      }

      console.log('精确比较时间参数:', {
        urlStartTime,
        urlEndTime,
        resStartTime,
        resEndTime
      });

      try {
        // 尝试解析日期时间，转换为ISO格式进行精确比较
        // 注意：我们需要比较的是时间精度而不仅仅是日期

        // 处理URL中的时间参数
        let urlStart, urlEnd;
        if (typeof urlStartTime === 'string') {
          // 如果是ISO格式字符串，直接创建Date对象
          if (urlStartTime.includes('T')) {
            urlStart = new Date(urlStartTime);
          } else {
            // 如果是"YYYY-MM-DD HH:MM"格式，手动解析
            const parts = urlStartTime.split(' ');
            if (parts.length === 2) {
              const dateParts = parts[0].split('-');
              const timeParts = parts[1].split(':');
              urlStart = new Date(
                parseInt(dateParts[0]),
                parseInt(dateParts[1]) - 1, // 月份是0-11
                parseInt(dateParts[2]),
                parseInt(timeParts[0]),
                parseInt(timeParts[1])
              );
            } else {
              urlStart = new Date(urlStartTime);
            }
          }
        } else {
          urlStart = new Date(urlStartTime);
        }

        if (typeof urlEndTime === 'string') {
          if (urlEndTime.includes('T')) {
            urlEnd = new Date(urlEndTime);
          } else {
            const parts = urlEndTime.split(' ');
            if (parts.length === 2) {
              const dateParts = parts[0].split('-');
              const timeParts = parts[1].split(':');
              urlEnd = new Date(
                parseInt(dateParts[0]),
                parseInt(dateParts[1]) - 1,
                parseInt(dateParts[2]),
                parseInt(timeParts[0]),
                parseInt(timeParts[1])
              );
            } else {
              urlEnd = new Date(urlEndTime);
            }
          }
        } else {
          urlEnd = new Date(urlEndTime);
        }

        // 处理预约中的时间
        let resStart = new Date(resStartTime);
        let resEnd = new Date(resEndTime);

        // 将所有时间转换为ISO字符串进行比较（不包括毫秒和时区信息）
        const formatForCompare = (date) => {
          if (isNaN(date.getTime())) {
            console.error('无效的日期对象:', date);
            return '';
          }
          return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
        };

        const urlStartFormatted = formatForCompare(urlStart);
        const urlEndFormatted = formatForCompare(urlEnd);
        const resStartFormatted = formatForCompare(resStart);
        const resEndFormatted = formatForCompare(resEnd);

        console.log('格式化后的精确时间比较:', {
          urlStartFormatted,
          urlEndFormatted,
          resStartFormatted,
          resEndFormatted
        });

        // 判断时间是否精确匹配
        const isMatch = urlStartFormatted === resStartFormatted && urlEndFormatted === resEndFormatted;

        console.log('精确时间匹配结果:', isMatch);

        return isMatch;
      } catch (e) {
        console.error('精确比较时间出错:', e);
        // 出错时保守返回不匹配
        return false;
      }
    },
  }
}
</script>

<style scoped>
.admin-reservation-detail {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.loading-container {
  padding: 40px 0;
}

.error-card {
  text-align: center;
  padding: 40px 0;
}

.error-message {
  margin-bottom: 20px;
}

.error-message i {
  font-size: 48px;
  color: #E6A23C;
  margin-bottom: 10px;
}

.error-message p {
  font-size: 18px;
  color: #606266;
}

.detail-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  margin-top: 20px;
  text-align: right;
}

@media (max-width: 768px) {
  .el-descriptions-item {
    width: 100%;
  }
}
</style>
