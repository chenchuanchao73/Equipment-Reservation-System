<template>
  <div class="home-page">
    <div class="banner">
      <h1>{{ $t('home.welcome') }}</h1>
      <p class="description">{{ $t('home.description') }}</p>
    </div>

    <div class="features">
      <el-row :gutter="30">
        <el-col :xs="24" :sm="8">
          <div class="feature-card">
            <i class="el-icon-date feature-icon"></i>
            <h3>{{ $t('home.calendarView') }}</h3>
            <p>{{ $t('home.calendarViewDesc') }}</p>
            <el-button type="danger" @click="goToCalendar">
              <i class="el-icon-date"></i> {{ $t('home.viewCalendar') }} <i class="el-icon-arrow-right"></i>
            </el-button>
          </div>
        </el-col>

        <el-col :xs="24" :sm="8">
          <div class="feature-card">
            <i class="el-icon-view feature-icon"></i>
            <h3>{{ $t('home.viewReservations') }}</h3>
            <p>{{ $t('home.viewReservationsDesc') }}</p>
            <el-button type="primary" @click="goToEquipment">
              <i class="el-icon-view"></i> {{ $t('home.browseEquipment') }} <i class="el-icon-arrow-right"></i>
            </el-button>
          </div>
        </el-col>

        <el-col :xs="24" :sm="8">
          <div class="feature-card">
            <i class="el-icon-s-order feature-icon"></i>
            <h3>{{ $t('home.myReservations') }}</h3>
            <p>{{ $t('home.myReservationsDesc') }}</p>
            <el-button type="success" @click="goToReservationManage">
              <i class="el-icon-s-order"></i> {{ $t('home.manageReservations') }} <i class="el-icon-arrow-right"></i>
            </el-button>
          </div>
        </el-col>

      </el-row>
    </div>

    <div class="public-query-section">
      <h2>{{ $t('home.publicQuery') }}</h2>

      <el-form :model="queryForm" label-position="top" class="query-form">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="8">
            <el-form-item :label="$t('equipment.category')">
              <el-select
                v-model="queryForm.category"
                :placeholder="$t('common.all') + ' ' + $t('equipment.category')"
                clearable
                style="width: 100%"
                @change="handleQuery"
              >
                <el-option
                  v-for="category in categories"
                  :key="category"
                  :label="category"
                  :value="category"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="8">
            <el-form-item :label="$t('common.status')">
              <el-select
                v-model="queryForm.status"
                :placeholder="$t('common.all') + ' ' + $t('common.status')"
                clearable
                style="width: 100%"
                @change="handleQuery"
              >
                <el-option
                  :label="$t('reservation.statusConfirmed')"
                  value="confirmed"
                ></el-option>
                <el-option
                  :label="$t('reservation.statusInUse')"
                  value="in_use"
                ></el-option>
                <el-option
                  :label="$t('reservation.statusExpired')"
                  value="expired"
                ></el-option>
                <el-option
                  :label="$t('reservation.statusCancelled')"
                  value="cancelled"
                ></el-option>
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="8">
            <el-form-item :label="$t('reservation.dateRange')">
              <el-date-picker
                v-model="queryForm.dateRange"
                type="daterange"
                range-separator="-"
                :start-placeholder="$t('reservation.startDate')"
                :end-placeholder="$t('reservation.endDate')"
                style="width: 100%"
                @change="handleQuery"
              ></el-date-picker>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleQuery" :loading="loading">
            {{ $t('common.search') }}
          </el-button>
          <el-button @click="resetQuery" icon="el-icon-refresh-left">{{ $t('common.reset') }}</el-button>
        </el-form-item>
      </el-form>

      <!-- 查询结果 -->
      <div v-if="reservations.length > 0" class="query-results">
        <!-- 查询结果标题 -->
        <div class="query-results-header">
          <h3>
            <i class="el-icon-document"></i>
            <span>{{ $t('home.queryResults') }}</span>
            <span class="results-count">
              ({{ $t('common.total') }} {{ reservations.length }} {{ $t('common.items') }})
            </span>
          </h3>
        </div>

        <!-- 桌面端表格视图 -->
        <el-table
          v-if="!isMobile"
          :data="paginatedReservations"
          style="width: 100%"
          v-loading="loading"
          border
          stripe
          @sort-change="handleSortChange"
        >
          <el-table-column
            prop="id"
            :label="$t('common.id')"
            min-width="80"
            sortable
          ></el-table-column>

          <el-table-column
            prop="equipment_name"
            :label="$t('equipment.name')"
            min-width="120"
          ></el-table-column>

          <el-table-column
            prop="equipment_category"
            :label="$t('equipment.category')"
            min-width="180"
          ></el-table-column>

          <el-table-column
            prop="user_name"
            :label="$t('reservation.reserver')"
            min-width="100"
          ></el-table-column>

          <el-table-column
            prop="user_department"
            :label="$t('reservation.department')"
            min-width="100"
          ></el-table-column>

          <el-table-column
            prop="start_datetime"
            :label="$t('reservation.startTime')"
            min-width="120"
            :formatter="formatDateTime"
            sortable
          ></el-table-column>

          <el-table-column
            prop="end_datetime"
            :label="$t('reservation.endTime')"
            min-width="120"
            :formatter="formatDateTime"
            sortable
          ></el-table-column>

          <el-table-column
            prop="status"
            :label="$t('common.status')"
            width="140"
            sortable
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
        </el-table>

        <!-- 移动端卡片视图 -->
        <div v-else class="mobile-card-container" v-loading="loading">
          <div
            v-for="reservation in paginatedReservations"
            :key="reservation.id"
            class="reservation-mobile-card"
          >
            <div class="card-header">
              <div class="card-title">
                <span class="equipment-name">{{ reservation.equipment_name }}</span>
                <el-tag
                  :type="getStatusType(reservation)"
                  size="small"
                  class="status-tag"
                >
                  {{ getStatusText(reservation) }}
                </el-tag>
              </div>
              <div class="reservation-id">#{{ reservation.id }}</div>
            </div>

            <div class="card-content">
              <div class="info-row">
                <span class="label">{{ $t('equipment.category') }}:</span>
                <span class="value">{{ reservation.equipment_category }}</span>
              </div>

              <div class="info-row">
                <span class="label">{{ $t('reservation.reserver') }}:</span>
                <span class="value">{{ reservation.user_name }}</span>
              </div>

              <div class="info-row">
                <span class="label">{{ $t('reservation.department') }}:</span>
                <span class="value">{{ reservation.user_department }}</span>
              </div>

              <div class="time-info">
                <div class="time-row">
                  <i class="el-icon-time"></i>
                  <span class="time-label">{{ $t('reservation.startTime') }}:</span>
                  <span class="time-value">{{ formatDateTime(null, null, reservation.start_datetime) }}</span>
                </div>
                <div class="time-row">
                  <i class="el-icon-time"></i>
                  <span class="time-label">{{ $t('reservation.endTime') }}:</span>
                  <span class="time-value">{{ formatDateTime(null, null, reservation.end_datetime) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页控件 -->
        <div class="pagination-container">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[5, 10, 20, 50]"
            :page-size="pageSize"
            :layout="paginationLayout"
            :total="reservations.length"
          >
          </el-pagination>
        </div>
      </div>

      <!-- 无查询结果提示 -->
      <div v-else-if="querySubmitted" class="no-results">
        <el-empty :description="$t('home.noRecordsFound')"></el-empty>
      </div>
    </div>
  </div>
</template>

<script>
import { formatDateTime } from '@/utils/dateUtils'
import equipmentApi from '@/api/equipment'
import reservationApi from '@/api/reservation'
import { categoryApi } from '@/api'

export default {
  name: 'HomePage',

  data() {
    return {
      // 公共查询相关
      loading: false,
      querySubmitted: false,
      reservations: [],
      categories: [],
      queryForm: {
        category: '',
        status: '',
        dateRange: null
      },
      // 分页相关
      currentPage: 1,
      pageSize: 10,
      // 公告数据
      announcements: [],
      // 响应式布局相关
      isMobile: window.innerWidth <= 768
    }
  },

  computed: {
    // 根据当前页码和每页显示条数计算当前页的数据
    paginatedReservations() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      const endIndex = startIndex + this.pageSize;
      return this.reservations.slice(startIndex, endIndex);
    },

    // 根据屏幕宽度动态调整分页组件布局
    paginationLayout() {
      return this.isMobile
        ? 'prev, next'
        : 'total, sizes, prev, pager, next, jumper';
    }
  },

  created() {
    // 获取设备类别
    this.fetchCategories()

    // 默认加载公开查询数据
    this.handleQuery()

    // 添加窗口大小变化的监听器
    window.addEventListener('resize', this.handleResize)
  },

  beforeDestroy() {
    // 移除窗口大小变化的监听器
    window.removeEventListener('resize', this.handleResize)
  },

  methods: {
    // 处理窗口大小变化
    handleResize() {
      this.isMobile = window.innerWidth <= 768
    },

    goToEquipment() {
      this.$router.push('/equipment')
    },

    goToQuery() {
      this.$router.push('/reservation/query')
    },

    goToReservationManage() {
      this.$router.push('/reservation/query')
    },

    goToCalendar() {
      this.$router.push('/calendar')
    },

    // 获取设备类别
    async fetchCategories() {
      try {
        // 使用类别管理API获取完整的类别信息
        const response = await categoryApi.getAllCategories()
        if (response.data && Array.isArray(response.data)) {
          // 使用类别的完整名称
          this.categories = response.data.map(item => item.name)
        } else {
          console.error('Invalid categories data format:', response.data)
          this.categories = []
        }
      } catch (error) {
        console.error('Failed to fetch equipment categories:', error)
        this.categories = []
      }
    },

    // 处理公共查询
    async handleQuery() {
      this.loading = true
      this.querySubmitted = true

      try {
        // 准备查询参数
        const params = {
          limit: 1000  // 设置为显示最多1000条结果，确保能显示所有记录
        }

        // 添加类别过滤
        if (this.queryForm.category) {
          // 需要先获取该类别的所有设备ID
          const equipmentResponse = await equipmentApi.getEquipments({
            category: this.queryForm.category,
            limit: 100  // 增加限制，确保能获取所有设备
          })

          if (equipmentResponse.data && equipmentResponse.data.items && equipmentResponse.data.items.length > 0) {
            // 如果有设备，使用类别参数进行查询
            params.category = this.queryForm.category
          }
        }

        // 添加状态过滤
        if (this.queryForm.status) {
          // 直接使用选择的状态值，因为后端现在支持所有状态
          params.status = this.queryForm.status;
          console.log(`设置状态参数为 "${this.queryForm.status}"`);
        }

        // 添加日期范围过滤
        if (this.queryForm.dateRange && this.queryForm.dateRange.length === 2) {
          const [startDate, endDate] = this.queryForm.dateRange
          params.from_date = startDate.toISOString()

          // 将结束日期调整为当天的最后一秒
          const endDateObj = new Date(endDate)
          endDateObj.setHours(23, 59, 59, 999)
          params.to_date = endDateObj.toISOString()
        }

        // 发送请求
        const response = await reservationApi.getReservations(params)
        let reservations = response.data.items

        // 不再需要在前端进行筛选，因为后端已经返回了正确的状态
        // 只记录日志，帮助调试
        if (this.queryForm.status) {
          console.log(`获取到状态为 ${this.queryForm.status} 的预约数量: ${reservations.length}`);

          // 记录每个预约的状态，帮助调试
          reservations.forEach(reservation => {
            console.log(`预约ID=${reservation.id}, 状态=${reservation.status}, 开始时间=${reservation.start_datetime}, 结束时间=${reservation.end_datetime}`);
          });
        }

        // 默认按状态优先级排序
        this.sortByStatus(reservations);

        this.reservations = reservations
      } catch (error) {
        console.error('Failed to query public reservations:', error)
        this.$message.error(this.$t('error.queryFailed'))
        this.reservations = []
      } finally {
        this.loading = false
      }
    },

    // 按状态优先级排序
    sortByStatus(reservations) {
      reservations.sort((a, b) => {
        // 按状态优先级排序
        const priorityMap = {
          'in_use': 4,      // 使用中 - 最高优先级
          'confirmed': 3,   // 已确认 - 次高优先级
          'expired': 2,     // 已过期 - 较低优先级
          'cancelled': 1,   // 已取消 - 最低优先级
        };

        const priorityA = priorityMap[a.status] || 0;
        const priorityB = priorityMap[b.status] || 0;

        // 如果优先级不同，按优先级降序排序
        if (priorityA !== priorityB) {
          return priorityB - priorityA;
        }

        // 如果优先级相同，按ID降序排序
        return b.id - a.id;
      });

      console.log(`按状态优先级排序后的预约数量: ${reservations.length}`);
    },

    // 重置查询表单
    resetQuery() {
      this.queryForm.category = ''
      this.queryForm.status = ''
      this.queryForm.dateRange = null
      this.handleQuery()
    },

    // 格式化日期时间
    formatDateTime(_, __, cellValue) {
      return formatDateTime(cellValue)
    },

    // 获取状态类型
    getStatusType(reservation) {
      // 直接根据后端返回的状态返回对应的类型
      switch (reservation.status) {
        case 'cancelled':
          return 'danger';  // 已取消 - 红色
        case 'expired':
          return 'warning'; // 已过期 - 橙色
        case 'in_use':
          return 'primary'; // 使用中 - 蓝色
        case 'confirmed':
          return 'success'; // 已确认 - 绿色
        default:
          return 'info';    // 其他状态 - 灰色
      }
    },

    // 获取状态文本
    getStatusText(reservation) {
      // 直接根据后端返回的状态返回对应的文本
      switch (reservation.status) {
        case 'cancelled':
          return this.$t('reservation.statusCancelled'); // 已取消
        case 'expired':
          return this.$t('reservation.statusExpired');   // 已过期
        case 'in_use':
          return this.$t('reservation.statusInUse');     // 使用中
        case 'confirmed':
          return this.$t('reservation.statusConfirmed'); // 已确认
        default:
          return reservation.status; // 其他状态直接显示
      }
    },

    // 处理每页显示条数变化
    handleSizeChange(size) {
      this.pageSize = size;
      // 如果当前页码超出了总页数，重置为第一页
      const totalPages = Math.ceil(this.reservations.length / this.pageSize);
      if (this.currentPage > totalPages) {
        this.currentPage = 1;
      }
    },

    // 处理页码变化
    handleCurrentChange(page) {
      this.currentPage = page;
    },

    // 处理表格排序变化
    handleSortChange(column) {
      if (!column.prop) return;

      if (column.prop === 'id') {
        // 按ID排序
        this.reservations.sort((a, b) => {
          if (column.order === 'ascending') {
            return a.id - b.id;  // 升序
          } else {
            return b.id - a.id;  // 降序
          }
        });
      } else if (column.prop === 'start_datetime' || column.prop === 'end_datetime') {
        // 按日期排序
        this.reservations.sort((a, b) => {
          const dateA = new Date(a[column.prop]);
          const dateB = new Date(b[column.prop]);

          if (column.order === 'ascending') {
            return dateA - dateB;  // 升序
          } else {
            return dateB - dateA;  // 降序
          }
        });
      } else if (column.prop === 'status') {
        // 按状态排序
        if (column.order === 'ascending') {
          // 升序：已取消 > 已过期 > 已确认 > 使用中
          this.reservations.sort((a, b) => {
            const priorityMap = {
              'cancelled': 4,   // 已取消 - 升序时最高
              'expired': 3,     // 已过期
              'confirmed': 2,   // 已确认
              'in_use': 1,      // 使用中 - 升序时最低
            };

            const priorityA = priorityMap[a.status] || 0;
            const priorityB = priorityMap[b.status] || 0;

            if (priorityA !== priorityB) {
              return priorityB - priorityA;
            }

            return b.id - a.id;  // 相同状态按ID降序
          });
        } else {
          // 降序：使用中 > 已确认 > 已过期 > 已取消
          this.sortByStatus(this.reservations);
        }
      }

      // 重置当前页为第一页
      this.currentPage = 1;
    },
  }
}
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
}

.banner {
  text-align: center;
  padding: 30px 20px;
  background-color: #fff;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.banner h1 {
  font-size: 2.2rem;
  color: #303133;
  margin-bottom: 15px;
}

.description {
  font-size: 1.1rem;
  color: #606266;
  max-width: 800px;
  margin: 0 auto 20px;
}

.banner-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.features {
  margin-bottom: 30px;
}

.feature-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  height: 100%;
  transition: transform 0.3s, box-shadow 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}

.feature-icon {
  font-size: 3.5rem;
  color: #409EFF;
  margin-bottom: 20px;
  background-color: #ecf5ff;
  padding: 20px;
  border-radius: 50%;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-card h3 {
  font-size: 1.6rem;
  color: #303133;
  margin-bottom: 15px;
  font-weight: 500;
}

.feature-card p {
  color: #606266;
  margin-bottom: 25px;
  line-height: 1.6;
  font-size: 1.1rem;
}

.public-query-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.public-query-section h2 {
  text-align: center;
  margin-bottom: 25px;
  color: #303133;
  font-size: 1.8rem;
}

.query-form {
  margin-bottom: 20px;
}

.query-results {
  margin-top: 20px;
}

.query-results-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.query-results-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  display: flex;
  align-items: center;
}

.query-results-header h3 i {
  margin-right: 8px;
  color: #409eff;
}

.results-count {
  color: #909399;
  font-weight: normal;
  margin-left: 10px;
  font-size: 14px;
}

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.no-results {
  margin-top: 30px;
  text-align: center;
}

/* 移动端卡片样式 */
.mobile-card-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reservation-mobile-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  overflow: hidden;
  transition: box-shadow 0.3s ease;
}

.reservation-mobile-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.equipment-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
}

.status-tag {
  align-self: flex-start;
  font-weight: 500;
}

.reservation-id {
  font-size: 14px;
  color: #409eff;
  font-weight: 600;
  margin-left: 12px;
  background: #ecf5ff;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: monospace;
  border: 1px solid #b3d8ff;
}

.card-content {
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-of-type {
  border-bottom: none;
  margin-bottom: 16px;
}

.info-row .label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  flex-shrink: 0;
  margin-right: 12px;
}

.info-row .value {
  font-size: 14px;
  color: #303133;
  text-align: right;
  word-break: break-word;
}

.time-info {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 12px;
  margin-top: 8px;
}

.time-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;
}

.time-row:last-child {
  margin-bottom: 0;
}

.time-row i {
  color: #409eff;
  margin-right: 8px;
  font-size: 14px;
}

.time-label {
  color: #606266;
  margin-right: 8px;
  font-weight: 500;
  min-width: 60px;
}

.time-value {
  color: #303133;
  font-weight: 500;
}

@media (max-width: 768px) {
  /* 移动端整体容器优化 - 与个人预约管理页面一致 */
  .home-container {
    padding: 10px 4px !important; /* 进一步减少左右边距 */
  }

  /* Banner 横幅优化 - 更宽的显示 */
  .banner {
    padding: 20px 8px; /* 进一步减少左右内边距 */
    margin: 0 -20px 20px -20px; /* 更大的负边距让banner更宽 */
    border-radius: 4px; /* 进一步减小圆角 */
  }

  .banner h1 {
    font-size: 2rem;
  }

  .description {
    font-size: 1rem;
    padding: 0 4px; /* 减少描述文字内边距 */
  }

  .banner-buttons {
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 0 4px; /* 减少按钮内边距 */
  }

  /* Feature Cards 功能卡片优化 - 更宽的显示 */
  .features .el-row {
    margin: 0 -22px !important; /* 更大的负边距让卡片行更宽 */
  }

  .features .el-col {
    padding: 0 2px !important; /* 进一步减少列间距 */
  }

  .feature-card {
    margin-bottom: 16px;
    padding: 20px 12px; /* 进一步减少左右内边距 */
    border-radius: 4px; /* 进一步减小圆角 */
  }

  .feature-icon {
    width: 70px;
    height: 70px;
    font-size: 3rem; /* 稍微减小图标大小 */
    padding: 15px;
  }

  .feature-card h3 {
    font-size: 1.4rem; /* 稍微减小标题字体 */
  }

  .feature-card p {
    font-size: 1rem; /* 稍微减小描述字体 */
    margin-bottom: 20px;
  }

  /* Public Query Section 查询区域优化 - 更宽的显示 */
  .public-query-section {
    padding: 16px 8px; /* 进一步减少左右内边距 */
    margin: 0 -20px 20px -20px; /* 更大的负边距让查询区域更宽 */
    border-radius: 4px; /* 进一步减小圆角 */
  }

  .public-query-section h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
  }

  /* 查询表单优化 */
  .query-form .el-row {
    margin: 0 -2px !important; /* 进一步减少表单行边距 */
  }

  .query-form .el-col {
    padding: 0 2px !important; /* 进一步减少表单列间距 */
  }

  /* 移动端卡片容器优化 - 与个人预约管理页面一致 */
  .mobile-card-container {
    margin: 0 -2px; /* 更小的负边距，与个人预约管理页面一致 */
    gap: 16px; /* 保持与个人预约管理页面一致的间距 */
  }

  .reservation-mobile-card {
    margin: 0 2px; /* 给卡片更小的边距 */
    border-radius: 8px; /* 与个人预约管理页面保持一致的圆角 */
  }

  /* 分页容器优化 */
  .pagination-container {
    margin: 16px -8px 0 -8px; /* 更大的负边距让分页区域更宽 */
    padding: 0 4px; /* 减少分页内容内边距 */
  }
}
</style>
