<template>
  <div class="admin-reservation">
    <div class="page-header">
      <h1 class="page-title">{{ $t('admin.reservation') }}</h1>
    </div>

    <!-- 筛选卡片 -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filter" class="filter-form">
        <el-form-item :label="$t('reservation.code')">
          <el-input
            v-model="filter.code"
            :placeholder="$t('reservation.queryPlaceholder')"
            clearable
            @keyup.enter.native="handleFilterChange"
          ></el-input>
        </el-form-item>

        <el-form-item :label="$t('reservation.userName')">
          <el-input
            v-model="filter.userName"
            :placeholder="$t('reservation.userName')"
            clearable
            @keyup.enter.native="handleFilterChange"
          ></el-input>
        </el-form-item>

        <el-form-item :label="$t('reservation.status')">
          <el-select
            v-model="filter.status"
            :placeholder="$t('equipment.allStatus')"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              :label="$t('reservation.confirmed')"
              value="confirmed"
            ></el-option>
            <el-option
              :label="$t('reservation.inUse')"
              value="in_use"
            ></el-option>
            <el-option
              :label="$t('reservation.expired')"
              value="expired"
            ></el-option>
            <el-option
              :label="$t('reservation.cancelled')"
              value="cancelled"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('reservation.dateRange')">
          <el-date-picker
            v-model="filter.dateRange"
            type="daterange"
            range-separator="至"
            :start-placeholder="$t('reservation.startDate')"
            :end-placeholder="$t('reservation.endDate')"
            value-format="yyyy-MM-dd"
            @change="handleFilterChange"
          >
          </el-date-picker>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" icon="el-icon-search" @click="handleFilterChange">
            {{ $t('common.search') }}
          </el-button>
          <el-button @click="resetFilter" icon="el-icon-refresh-left">
            {{ $t('common.reset') }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预定列表 -->
    <el-card shadow="hover" class="reservation-list">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>

      <div v-else-if="reservations.length === 0" class="empty-data">
        <el-empty :description="$t('common.noData')"></el-empty>
      </div>

      <el-table
        v-else
        :data="reservations"
        style="width: 100%"
        :default-sort="{ prop: 'id', order: 'descending' }"
        header-align="center"
        cell-class-name="text-center"
        border
        stripe
      >
        <!-- 添加ID列 -->
        <el-table-column
          prop="id"
          :label="$t('common.id')"
          min-width="60"
          sortable
        >
          <template slot-scope="scope">
            <span style="font-weight: bold;">{{ scope.row.id }}</span>
          </template>
        </el-table-column>

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
        ></el-table-column>

        <el-table-column
          prop="user_contact"
          :label="$t('reservation.userContact')"
          min-width="120"
        ></el-table-column>

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

      <!-- 分页 -->
      <div class="pagination-container" v-if="reservations.length > 0">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page.sync="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script>
import { reservationApi } from '@/api'
import { isReservationExpired } from '@/utils/date'

export default {
  name: 'AdminReservation',

  data() {
    return {
      loading: false,
      reservations: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filter: {
        code: '',
        userName: '',
        status: '',
        dateRange: []
      },
      // 添加一个保存页面状态的变量
      savedState: null
    }
  },

  created() {
    // 检查是否有保存的状态并恢复它
    this.restoreState();
  },

  // 添加activated钩子函数，在组件被激活时调用（如从预定详情页面返回）
  activated() {
    // 检查是否需要强制刷新
    const forceRefresh = localStorage.getItem('force_refresh_reservation_list');
    if (forceRefresh === 'true') {
      console.log('检测到强制刷新标记，重新获取数据');
      localStorage.removeItem('force_refresh_reservation_list');
      this.fetchData();
      return;
    }

    // 当从其他页面返回时，尝试恢复状态
    this.restoreState();
    // 检查预约状态更新
    this.checkReservationUpdates();
  },

  // 添加deactivated钩子函数，在组件被停用时调用（如进入预定详情页面）
  deactivated() {
    // 保存当前页面状态
    this.saveState();
  },

  // 添加beforeRouteLeave导航守卫，在离开组件时调用
  beforeRouteLeave(to, from, next) {
    // 如果是跳转到预定详情页面，保存状态
    if (to.path.includes('/admin/reservation/') && to.path !== '/admin/reservation') {
      this.saveState();
    }
    next();
  },

  methods: {
    async fetchData() {
      this.loading = true
      console.log('Fetching data with filter:', this.filter);
      console.log('Current page:', this.currentPage);

      try {
        // 添加时间戳参数，确保每次都获取最新数据
        const timestamp = new Date().getTime()
        console.log('添加时间戳参数:', timestamp)

        const params = {
          skip: (this.currentPage - 1) * this.pageSize, // 将页码转换为skip参数
          limit: this.pageSize,
          reservation_code: this.filter.code || undefined,
          user_name: this.filter.userName || undefined,
          _t: timestamp, // 添加时间戳，防止缓存
          sort_by: 'id', // 按ID排序
          sort_order: 'desc' // 降序排序
        }

        // 添加日期范围过滤
        if (this.filter.dateRange && this.filter.dateRange.length === 2) {
          params.from_date = this.filter.dateRange[0]
          params.to_date = this.filter.dateRange[1]
        }

        // 处理不同的状态筛选
        if (this.filter.status) {
          console.log('Filtering by status:', this.filter.status);

          // 直接使用选择的状态值，因为后端现在支持所有状态
          params.status = this.filter.status;
          console.log(`Setting status parameter to "${this.filter.status}"`);
        }

        console.log('Fetching reservations with params:', params)
        const response = await reservationApi.getReservations(params)
        console.log('API Response:', response)
        let reservations = response.data.items || []
        console.log('Received reservations:', reservations)

        // 不再需要在前端进行筛选，因为后端已经返回了正确的状态
        // 只记录日志，帮助调试
        if (this.filter.status) {
          console.log(`获取到状态为 ${this.filter.status} 的预约数量: ${reservations.length}`);

          // 记录每个预约的状态，帮助调试
          reservations.forEach(reservation => {
            console.log(`预约ID=${reservation.id}, 状态=${reservation.status}, 开始时间=${reservation.start_datetime}, 结束时间=${reservation.end_datetime}`);
          });
        }

        console.log('Filtered reservations:', reservations)
        this.reservations = reservations

        // 如果是特殊状态，总数需要重新计算
        if (this.filter.status === 'in_use' || this.filter.status === 'expired' || this.filter.status === 'confirmed' || this.filter.status === 'cancelled') {
          // 对于特殊状态，我们需要获取所有页的数据来计算总数
          // 这里我们先使用当前页的数据计算一个临时总数
          this.total = reservations.length
          console.log(`Temporary total based on current page: ${this.total}`);

          // 无论当前页是否有数据，都获取所有数据来计算真实总数
          this.fetchTotalForSpecialStatus()
        } else {
          this.total = response.data.total
          console.log(`Total from API response: ${this.total}`);
        }
      } catch (error) {
        console.error('Failed to fetch reservations:', error)
        this.$message.error(this.$t('error.serverError'))
      } finally {
        this.loading = false
      }
    },

    formatDateTime(_row, _column, cellValue) {
      if (!cellValue) return ''

      const date = new Date(cellValue)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

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

    handleFilterChange() {
      this.currentPage = 1
      this.fetchData()
    },

    resetFilter() {
      this.filter = {
        code: '',
        userName: '',
        status: '',
        dateRange: []
      }
      this.handleFilterChange()
    },

    handlePageChange(page) {
      this.currentPage = page
      this.fetchData()
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
      // 使用预约序号作为路径参数，而不是预约码
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
    },

    // 获取特殊状态的总记录数并更新当前页面的预约列表
    async fetchTotalForSpecialStatus() {
      try {
        console.log('Fetching total for special status:', this.filter.status);
        console.log('Current page before fetchTotal:', this.currentPage);

        // 保存当前页码，以便后续恢复
        const savedCurrentPage = this.currentPage;

        // 添加时间戳参数，确保每次都获取最新数据
        const timestamp = new Date().getTime()
        console.log('添加时间戳参数:', timestamp)

        // 构建查询参数，不包含分页参数
        const params = {
          // 不设置limit，获取所有记录
          limit: 1000, // 设置一个较大的值以获取尽可能多的记录
          skip: 0,
          reservation_code: this.filter.code || undefined, // 使用reservation_code而不是code
          user_name: this.filter.userName || undefined,
          _t: timestamp, // 添加时间戳，防止缓存
          sort_by: 'id', // 按ID排序
          sort_order: 'desc' // 降序排序
        }

        // 添加日期范围过滤
        if (this.filter.dateRange && this.filter.dateRange.length === 2) {
          params.from_date = this.filter.dateRange[0]
          params.to_date = this.filter.dateRange[1]
        }

        // 直接获取指定状态的预约
        const statusParams = { ...params, status: this.filter.status };

        console.log(`直接获取状态为 ${this.filter.status} 的预约`);
        const response = await reservationApi.getReservations(statusParams);

        // 使用后端返回的结果
        let allReservations = response.data.items || [];

        console.log(`Total reservations before filtering: ${allReservations.length}`);

        const now = new Date();
        console.log(`当前日期: ${now}`);

        // 不再需要在前端进行筛选，因为后端已经返回了正确的状态
        // 只记录日志，帮助调试
        console.log(`获取到状态为 ${this.filter.status} 的预约数量: ${allReservations.length}`);

        // 记录每个预约的状态，帮助调试
        allReservations.forEach(reservation => {
          console.log(`预约ID=${reservation.id}, 状态=${reservation.status}, 开始时间=${reservation.start_datetime}, 结束时间=${reservation.end_datetime}`);
        });

        // 更新总数
        this.total = allReservations.length;
        console.log(`Updated total to: ${this.total}`);

        // 对筛选后的结果进行排序
        if (this.filter.status === 'expired') {
          // 对于已过期，按结束时间倒序排列
          allReservations.sort((a, b) => new Date(b.end_datetime) - new Date(a.end_datetime));
        } else if (this.filter.status === 'in_use') {
          // 对于使用中，按开始时间倒序排列
          allReservations.sort((a, b) => new Date(b.start_datetime) - new Date(a.start_datetime));
        } else if (this.filter.status === 'confirmed') {
          // 对于已确认，按开始时间升序排列
          allReservations.sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime));
        } else if (this.filter.status === 'cancelled') {
          // 对于已取消，按结束时间倒序排列
          allReservations.sort((a, b) => new Date(b.end_datetime) - new Date(a.end_datetime));
        }

        // 计算当前页应该显示的预约
        const maxPage = Math.ceil(allReservations.length / this.pageSize) || 1;

        // 确保页码不超过最大页数
        const targetPage = Math.min(savedCurrentPage, maxPage);
        console.log(`计算页数: 总记录数=${allReservations.length}, 每页记录数=${this.pageSize}, 最大页数=${maxPage}, 目标页码=${targetPage}`);

        const startIndex = (targetPage - 1) * this.pageSize;
        const endIndex = Math.min(startIndex + this.pageSize, allReservations.length);
        const currentPageReservations = allReservations.slice(startIndex, endIndex);

        console.log(`当前页数据范围: 开始索引=${startIndex}, 结束索引=${endIndex}, 当前页记录数=${currentPageReservations.length}`);

        // 更新当前页面的预约列表
        if (currentPageReservations.length > 0) {
          // 先更新数据
          this.reservations = currentPageReservations;
          // 然后更新页码，避免触发不必要的重新获取数据
          if (this.currentPage !== targetPage) {
            console.log(`更新页码: 从 ${this.currentPage} 到 ${targetPage}`);
            this.$nextTick(() => {
              this.currentPage = targetPage;
            });
          }
          console.log(`更新当前页面的预约列表: ${this.reservations.length} 条记录`);
        } else if (allReservations.length > 0) {
          // 如果当前页没有数据但总数据不为空，自动回到第一页
          console.log(`当前页没有数据，回到第一页`);
          this.reservations = allReservations.slice(0, this.pageSize);
          if (this.currentPage !== 1) {
            this.$nextTick(() => {
              this.currentPage = 1;
            });
          }
        } else {
          // 如果没有找到任何预约
          this.reservations = [];
          console.log('没有找到符合条件的预约');
        }

        console.log('Current page after fetchTotal:', this.currentPage);
      } catch (error) {
        console.error('Failed to fetch total for special status:', error);
      }
    },

    // 保存当前页面状态
    saveState() {
      this.savedState = {
        filter: { ...this.filter },
        currentPage: this.currentPage
      };
      console.log('Saved state:', this.savedState);
    },

    // 恢复保存的页面状态
    restoreState() {
      if (this.savedState) {
        this.filter = { ...this.savedState.filter };
        this.currentPage = this.savedState.currentPage;
        console.log('Restored state:', this.savedState);
        this.fetchData();
      } else {
        this.fetchData();
      }
    },

    // 打开预约详情
    openReservationDetail(reservation) {
      console.log('打开预约详情:', reservation);

      // 计算当前状态
      const statusText = this.getStatusText(reservation);
      const statusType = this.getStatusType(reservation);
      const dbStatus = reservation.status || 'confirmed';
      const startTime = reservation.start_datetime;
      const endTime = reservation.end_datetime;

      console.log('计算的状态信息:', {
        statusText,
        statusType,
        dbStatus,
        startTime,
        endTime
      });

      // 将状态保存到localStorage，以便详情页面使用
      const stateKey = `reservation_status_${reservation.reservation_code}`;
      const state = {
        statusText,
        statusType,
        dbStatus,
        timestamp: new Date().getTime()
      };

      console.log('Saved state:', state);
      localStorage.setItem(stateKey, JSON.stringify(state));

      // 导航到详情页面，并传递状态和时间参数
      this.$router.push({
        name: 'AdminReservationDetail',
        params: { code: reservation.reservation_code },
        query: {
          displayStatus: statusText,
          displayStatusType: statusType,
          startTime: startTime,
          endTime: endTime
        }
      });
    },

    // 在激活（从其他页面返回）时，检查预约状态是否需要更新
    async checkReservationUpdates() {
      // 如果当前显示的是预约列表，则检查是否需要刷新
      if (this.reservations.length > 0) {
        // 检查localStorage中是否有任何预约状态发生了变化
        for (let i = 0; i < this.reservations.length; i++) {
          const reservation = this.reservations[i];
          const stateKey = `reservation_status_${reservation.reservation_code}`;
          const savedStateStr = localStorage.getItem(stateKey);

          if (savedStateStr) {
            try {
              const savedState = JSON.parse(savedStateStr);

              // 检查保存的状态是否还是新鲜的（5分钟内）
              const now = new Date().getTime();
              const fiveMinutes = 5 * 60 * 1000;

              if (now - savedState.timestamp <= fiveMinutes) {
                console.log(`检测到预约 ${reservation.reservation_code} 的状态可能已更改，保存的状态:`, savedState);

                // 检查是否有强制状态更新，特别是已取消状态
                if (savedState.forcedStatus === 'cancelled' ||
                    (savedState.statusText === this.$t('reservation.cancelled') &&
                     savedState.statusType === 'danger')) {
                  console.log(`预约 ${reservation.reservation_code} 已被标记为已取消，将在界面上更新`);

                  // 更新当前列表中的预约状态
                  this.reservations[i].status = 'cancelled';

                  // 强制更新UI
                  this.$forceUpdate();
                }
              } else {
                // 如果状态过期，则移除它
                console.log(`预约 ${reservation.reservation_code} 的保存状态已过期，移除`);
                localStorage.removeItem(stateKey);
              }
            } catch (e) {
              console.error('解析保存的状态时出错:', e);
            }
          }
        }
      }
    }
  }
}
</script>

<style scoped>
.admin-reservation {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px 20px;
  background-color: #FFFFFF;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.page-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.reservation-list {
  margin-bottom: 20px;
}

.loading-container {
  padding: 40px 0;
}

.empty-data {
  padding: 40px 0;
  text-align: center;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}

.text-center {
  text-align: center !important;
}

@media (max-width: 768px) {
  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>
