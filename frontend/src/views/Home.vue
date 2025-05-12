<template>
  <div class="home-page">
    <div class="banner">
      <h1>{{ $t('home.welcome') }}</h1>
      <p class="description">{{ $t('home.description') }}</p>
      <!-- 移除重复按钮 -->
    </div>

    <div class="features">
      <el-row :gutter="30">
        <el-col :xs="24" :sm="12">
          <div class="feature-card">
            <i class="el-icon-view feature-icon"></i>
            <h3>{{ $t('home.viewReservations') }}</h3>
            <p>{{ $t('home.viewReservationsDesc') }}</p>
            <el-button type="primary" @click="goToEquipment">
              <i class="el-icon-view"></i> {{ $t('home.browseEquipment') }} <i class="el-icon-arrow-right"></i>
            </el-button>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12">
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
        <el-table
          :data="paginatedReservations"
          style="width: 100%"
          :default-sort="{ prop: 'id', order: 'descending' }"
          v-loading="loading"
          border
          stripe
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

        <!-- 分页控件 -->
        <div class="pagination-container">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[5, 10, 20, 50]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="reservations.length"
          >
          </el-pagination>
        </div>
      </div>

      <!-- 无查询结果提示 -->
      <div v-else-if="querySubmitted" class="no-results">
        <el-empty :description="$t('reservation.noRecordsFound')"></el-empty>
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
      pageSize: 10
    }
  },

  computed: {
    // 根据当前页码和每页显示条数计算当前页的数据
    paginatedReservations() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      const endIndex = startIndex + this.pageSize;
      return this.reservations.slice(startIndex, endIndex);
    }
  },

  created() {
    // 获取设备类别
    this.fetchCategories()

    // 默认加载公开查询数据
    this.handleQuery()
  },

  methods: {
    goToEquipment() {
      this.$router.push('/equipment')
    },

    goToQuery() {
      this.$router.push('/reservation/query')
    },

    goToReservationManage() {
      this.$router.push('/reservation/query')
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

        // 按照ID降序排序，使最新的预约显示在前面
        reservations.sort((a, b) => b.id - a.id);
        console.log(`按ID降序排序后的预约数量: ${reservations.length}`);

        this.reservations = reservations
      } catch (error) {
        console.error('Failed to query public reservations:', error)
        this.$message.error(this.$t('error.queryFailed'))
        this.reservations = []
      } finally {
        this.loading = false
      }
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
    }
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

.pagination-container {
  margin-top: 20px;
  text-align: center;
}

.no-results {
  margin-top: 30px;
  text-align: center;
}

@media (max-width: 768px) {
  .banner {
    padding: 20px;
  }

  .banner h1 {
    font-size: 2rem;
  }

  .description {
    font-size: 1rem;
  }

  .banner-buttons {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }

  .feature-card {
    margin-bottom: 20px;
  }

  .public-query-section {
    padding: 15px;
  }

  .public-query-section h2 {
    font-size: 1.5rem;
  }
}
</style>
