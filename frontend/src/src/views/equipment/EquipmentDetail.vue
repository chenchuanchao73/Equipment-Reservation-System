<template>
  <div class="equipment-detail">
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
        <el-button icon="el-icon-arrow-left" @click="$router.push('/equipment')">
          {{ $t('common.back') }}
        </el-button>
      </div>

      <!-- 设备信息 -->
      <el-row :gutter="20">
        <el-col :xs="24" :sm="24" :md="10" :lg="8">
          <el-card shadow="never" class="image-card">
            <div class="equipment-image-container">
              <img
                :src="equipment.image_path ? getFullImageUrl(equipment.image_path) : require('@/assets/upload.png')"
                :alt="equipment.name"
                class="equipment-image"
              />
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="24" :md="14" :lg="16">
          <el-card shadow="never" class="info-card">
            <div class="equipment-header">
              <h1 class="equipment-name">{{ equipment.name }}</h1>
              <div class="equipment-tags">
                <el-tag
                  :type="equipment.status === 'available' ? 'success' : 'warning'"
                  size="medium"
                >
                  {{ equipment.status === 'available' ? $t('equipment.available') : $t('equipment.maintenance') }}
                </el-tag>
                
                <!-- 可同时预定标记 -->
                <el-tag
                  v-if="equipment.allow_simultaneous"
                  type="primary"
                  size="medium"
                  style="margin-left: 8px;"
                >
                  {{ $t('equipment.simultaneousReservation') }} ({{ equipment.max_simultaneous }})
                </el-tag>
              </div>
            </div>

            <el-divider></el-divider>

            <el-descriptions :column="1" border>
              <el-descriptions-item :label="$t('equipment.category')">
                {{ equipment.category }}
              </el-descriptions-item>

              <el-descriptions-item :label="$t('equipment.model')" v-if="equipment.model">
                {{ equipment.model }}
              </el-descriptions-item>

              <el-descriptions-item :label="$t('equipment.location')" v-if="equipment.location">
                {{ equipment.location }}
              </el-descriptions-item>

              <el-descriptions-item :label="$t('equipment.description')" v-if="equipment.description">
                {{ equipment.description }}
              </el-descriptions-item>

              <!-- 可同时预定说明 -->
              <el-descriptions-item v-if="equipment.allow_simultaneous" :label="$t('equipment.simultaneousReservationInfo')">
                <div class="simultaneous-info">
                  <i class="el-icon-info"></i>
                  {{ $t('equipment.simultaneousReservationDesc', { max: equipment.max_simultaneous }) }}
                </div>
              </el-descriptions-item>

              <el-descriptions-item :label="$t('equipment.userGuide')" v-if="equipment.user_guide">
                <div class="user-guide-content rich-text-content" v-html="equipment.user_guide"></div>
              </el-descriptions-item>

              <el-descriptions-item :label="$t('equipment.videoTutorial')" v-if="equipment.video_tutorial">
                <div class="video-container">
                  <iframe
                    :src="equipment.video_tutorial"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowfullscreen
                  ></iframe>
                </div>
              </el-descriptions-item>
            </el-descriptions>

            <div class="action-buttons">
              <el-button
                type="primary"
                size="large"
                @click="reserveEquipment"
                :disabled="equipment.status !== 'available'"
              >
                {{ $t('equipment.reserve') }}
              </el-button>

              <el-button
                type="success"
                size="large"
                @click="recurringReserveEquipment"
                :disabled="equipment.status !== 'available'"
              >
                {{ $t('reservation.createRecurringReservation') }}
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 预定情况 -->
      <el-card shadow="never" class="reservations-card">
        <div slot="header" class="reservations-header">
          <span>{{ $t('equipment.currentReservations') }}</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="→"
            :start-placeholder="$t('reservation.startTime')"
            :end-placeholder="$t('reservation.endTime')"
            :picker-options="pickerOptions"
            @change="fetchReservations"
            size="small"
          ></el-date-picker>
        </div>

        <div v-if="loadingReservations" class="loading-container">
          <el-skeleton :rows="3" animated />
        </div>

        <div v-else-if="reservations.length === 0" class="empty-reservations">
          <el-empty :description="$t('equipment.noReservations')"></el-empty>
        </div>

        <div v-else class="reservations-list">
          <el-timeline>
            <el-timeline-item
              v-for="reservation in reservations"
              :key="reservation.id"
              :timestamp="formatDateTime(reservation.start_datetime) + ' → ' + formatDateTime(reservation.end_datetime)"
              :type="getTimelineItemType(reservation)"
            >
              <el-card class="reservation-card">
                <div class="reservation-info">
                  <div class="reservation-user">
                    <span class="user-name">{{ reservation.user_name }}</span>
                    <span class="user-department">{{ reservation.user_department }}</span>
                  </div>

                  <div class="reservation-purpose" v-if="reservation.purpose">
                    <strong>{{ $t('reservation.purpose') }}:</strong> {{ reservation.purpose }}
                  </div>

                  <div class="reservation-status">
                    <el-tag
                      size="small"
                      :type="getStatusTagType(reservation)"
                    >
                      {{ getStatusText(reservation) }}
                    </el-tag>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { equipmentApi, reservationApi } from '@/api'
import axios from 'axios'
import { isReservationExpired } from '@/utils/date'

export default {
  name: 'EquipmentDetail',

  data() {
    return {
      loading: false,
      loadingReservations: false,
      equipment: null,
      reservations: [],
      dateRange: [
        new Date(),
        new Date(new Date().setDate(new Date().getDate() + 7))
      ],
      pickerOptions: {
        shortcuts: [
          {
            text: this.$t('common.today'),
            onClick(picker) {
              const end = new Date()
              const start = new Date()
              picker.$emit('pick', [start, end])
            }
          },
          {
            text: this.$t('common.week'),
            onClick(picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
              picker.$emit('pick', [start, end])
            }
          },
          {
            text: this.$t('common.month'),
            onClick(picker) {
              const end = new Date()
              const start = new Date()
              start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
              picker.$emit('pick', [start, end])
            }
          }
        ]
      }
    }
  },

  computed: {
    // 获取完整的图片URL
    baseUrl() {
      return axios.defaults.baseURL || 'http://localhost:8000';
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

        // 获取预定情况
        this.fetchReservations()
      } catch (error) {
        console.error('Failed to fetch equipment:', error)
        this.$message.error(this.$t('common.error'))
        this.equipment = null
      } finally {
        this.loading = false
      }
    },

    async fetchReservations() {
      if (!this.equipment) return

      this.loadingReservations = true
      try {
        const equipmentId = this.equipment.id
        const startDate = this.formatDate(this.dateRange[0])

        // 将结束日期调整为当天的最后一秒
        const endDateObj = new Date(this.dateRange[1])
        endDateObj.setHours(23, 59, 59, 999)
        const endDate = endDateObj.toISOString()

        const params = {
          equipment_id: equipmentId,
          from_date: startDate,
          to_date: endDate
          // 不指定status，获取所有状态的预定
        }

        const response = await reservationApi.getReservations(params)
        // 按开始时间升序排序，使最近的预约显示在前面
        this.reservations = response.data.items.sort((a, b) => {
          const dateA = new Date(a.start_datetime)
          const dateB = new Date(b.start_datetime)
          return dateA - dateB
        })
      } catch (error) {
        console.error('Failed to fetch reservations:', error)
        this.$message.error(this.$t('common.error'))
        this.reservations = []
      } finally {
        this.loadingReservations = false
      }
    },

    reserveEquipment() {
      this.$router.push(`/equipment/${this.equipment.id}/reserve`)
    },

    recurringReserveEquipment() {
      this.$router.push(`/equipment/${this.equipment.id}/recurring-reserve`)
    },

    formatDateTime(dateTime) {
      if (!dateTime) return ''

      const date = new Date(dateTime)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

    formatDate(date) {
      if (!date) return ''

      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
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
    },

    // 获取时间线项的类型
    getTimelineItemType(reservation) {
      // 根据实际状态返回不同的类型
      switch(reservation.status) {
        case 'cancelled':
          return 'danger'  // 已取消：从info改为danger(红色)
        case 'expired':
          return 'warning'
        case 'in_use':
          return 'primary' // 使用中：从success改为primary(蓝色)
        case 'confirmed':
          return 'success' // 已确认：从primary改为success(绿色)
        default:
          return 'success'
      }
    },

    // 获取状态标签的类型
    getStatusTagType(reservation) {
      // 根据实际状态返回不同的类型
      switch(reservation.status) {
        case 'cancelled':
          return 'danger'  // 已取消：从info改为danger(红色)
        case 'expired':
          return 'warning'
        case 'in_use':
          return 'primary' // 使用中：从success改为primary(蓝色)
        case 'confirmed':
          return 'success' // 已确认：从primary改为success(绿色)
        default:
          return 'success'
      }
    },

    // 获取状态文本
    getStatusText(reservation) {
      // 根据实际状态返回对应的文本
      switch(reservation.status) {
        case 'cancelled':
          return this.$t('reservation.cancelled')
        case 'expired':
          return this.$t('reservation.expired')
        case 'in_use':
          return this.$t('reservation.inUse')
        case 'confirmed':
          return this.$t('reservation.confirmed')
        default:
          return this.$t('reservation.confirmed')
      }
    }
  }
}
</script>

<style scoped>
.equipment-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.back-link {
  margin-bottom: 20px;
}

.image-card {
  margin-bottom: 20px;
}

.equipment-image-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: #f5f7fa;
}

.equipment-image {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
}

.info-card {
  margin-bottom: 20px;
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.equipment-name {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.reservations-card {
  margin-bottom: 20px;
}

.reservations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-reservations {
  padding: 20px 0;
  text-align: center;
}

.reservation-card {
  margin-bottom: 10px;
}

.reservation-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reservation-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  font-weight: bold;
  color: #303133;
}

.user-department {
  color: #909399;
  font-size: 13px;
}

.reservation-purpose {
  color: #606266;
  font-size: 14px;
}

.user-guide-content {
  line-height: 1.6;
}

.rich-text-content {
  max-width: 100%;
  overflow-x: auto;
}

.rich-text-content img {
  max-width: 100%;
  height: auto;
}

.rich-text-content table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 1rem;
}

.rich-text-content table td,
.rich-text-content table th {
  border: 1px solid #ddd;
  padding: 8px;
}

.rich-text-content ul,
.rich-text-content ol {
  padding-left: 2em;
}

.video-container {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
  overflow: hidden;
  max-width: 100%;
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.loading-container {
  padding: 40px 0;
}

.error-container {
  padding: 40px 0;
  text-align: center;
}

.reservations-status {
  margin-top: 20px;
}

.equipment-tags {
  display: flex;
  align-items: center;
}

.simultaneous-info {
  color: #409EFF;
  font-size: 14px;
  line-height: 1.5;
  margin: 5px 0;
}

.simultaneous-info i {
  margin-right: 5px;
}

@media (max-width: 768px) {
  .reservations-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .equipment-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
