<template>
  <div class="equipment-list">
    <h1 class="page-title">{{ $t('equipment.list') }}</h1>

    <!-- 筛选和搜索 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8" :md="6">
          <el-select
            v-model="filter.category"
            :placeholder="$t('equipment.allCategories')"
            clearable
            style="width: 100%"
            @change="handleFilterChange"
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            ></el-option>
          </el-select>
        </el-col>

        <el-col :xs="24" :sm="8" :md="6">
          <el-select
            v-model="filter.status"
            :placeholder="$t('equipment.allStatus')"
            clearable
            style="width: 100%"
            @change="handleFilterChange"
          >
            <el-option
              :label="$t('equipment.available')"
              value="available"
            ></el-option>
            <el-option
              :label="$t('equipment.maintenance')"
              value="maintenance"
            ></el-option>
          </el-select>
        </el-col>

        <el-col :xs="24" :sm="8" :md="12">
          <el-input
            v-model="filter.search"
            :placeholder="$t('equipment.searchPlaceholder')"
            clearable
            @keyup.enter.native="handleFilterChange"
            @clear="handleFilterChange"
          >
            <el-button
              slot="append"
              icon="el-icon-search"
              @click="handleFilterChange"
            ></el-button>
          </el-input>
        </el-col>
      </el-row>
    </el-card>

    <!-- 设备列表 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else>
      <div v-if="equipments.length === 0" class="empty-data">
        <el-empty :description="$t('common.noData')"></el-empty>
      </div>

      <el-row :gutter="20" v-else>
        <el-col
          v-for="equipment in equipments"
          :key="equipment.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          class="equipment-item"
        >
          <el-card
            :body-style="{ padding: '0px' }"
            shadow="hover"
            @click.native="viewEquipmentDetail(equipment.id)"
          >
            <div class="equipment-image-container">
              <img
                :src="equipment.image_path ? getFullImageUrl(equipment.image_path) : require('@/assets/upload.png')"
                :alt="equipment.name"
                class="equipment-image"
              />
            </div>

            <div class="equipment-info">
              <h3 class="equipment-name">{{ equipment.name }}</h3>
              <p class="equipment-category">{{ equipment.category }}</p>

              <div class="equipment-meta">
                <span class="equipment-location" v-if="equipment.location">
                  <i class="el-icon-location"></i> {{ equipment.location }}
                </span>

                <el-tag
                  v-if="equipment.status !== 'available'"
                  type="warning"
                  size="medium"
                  style="font-weight: bold; padding: 0px 10px; font-size: 14px;"
                >
                  {{ $t('equipment.maintenance') }}
                </el-tag>
                <el-tag
                  v-else-if="equipment.currently_reserved"
                  type="danger"
                  size="medium"
                  style="font-weight: bold; padding: 0px 10px; font-size: 14px;"
                >
                  {{ $t('equipment.inUse') }}
                </el-tag>
                <el-tag
                  v-else
                  type="success"
                  size="medium"
                  style="font-weight: bold; padding: 0px 10px; font-size: 14px;"
                >
                  {{ $t('equipment.available') }}
                </el-tag>
              </div>

              <div class="equipment-actions">
                <el-button
                  type="text"
                  @click.stop="viewEquipmentDetail(equipment.id)"
                >
                  {{ $t('equipment.viewDetail') }}
                </el-button>

                <el-button
                  type="primary"
                  size="small"
                  @click.stop="reserveEquipment(equipment.id)"
                  :disabled="equipment.status !== 'available' || equipment.currently_reserved"
                >
                  {{ $t('equipment.reserve') }}
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page.sync="currentPage"
          @current-change="handlePageChange"
        ></el-pagination>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import { equipmentApi } from '@/api'
import axios from 'axios'

export default {
  name: 'EquipmentList',

  data() {
    return {
      loading: false,
      equipments: [],
      total: 0,
      currentPage: 1,
      pageSize: 20,
      categories: [],
      filter: {
        category: '',
        status: '',
        search: ''
      }
    }
  },

  computed: {
    ...mapGetters(['getEquipmentCategories']),

    // 获取完整的图片URL
    baseUrl() {
      return axios.defaults.baseURL || 'http://localhost:8000';
    }
  },

  created() {
    this.fetchData()
    this.fetchCategories()
  },

  methods: {
    ...mapActions(['fetchEquipmentCategories']),

    async fetchData() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          limit: this.pageSize,
          category: this.filter.category || undefined,
          status: this.filter.status || undefined,
          search: this.filter.search || undefined
        }

        const response = await equipmentApi.getEquipments(params)
        this.equipments = response.data.items
        this.total = response.data.total
      } catch (error) {
        console.error('Failed to fetch equipments:', error)
        this.$message.error(this.$t('common.error'))
      } finally {
        this.loading = false
      }
    },

    async fetchCategories() {
      try {
        const response = await equipmentApi.getCategories()
        // 直接使用返回的类别列表，不需要再映射
        this.categories = response.data.categories || []
      } catch (error) {
        console.error('Failed to fetch categories:', error)
        // 确保即使API调用失败，categories也是一个数组
        this.categories = []
      }
    },

    handleFilterChange() {
      this.currentPage = 1
      this.fetchData()
    },

    handlePageChange(page) {
      this.currentPage = page
      this.fetchData()
    },

    viewEquipmentDetail(id) {
      this.$router.push(`/equipment/${id}`)
    },

    reserveEquipment(id) {
      this.$router.push(`/equipment/${id}/reserve`)
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
    }
  }
}
</script>

<style scoped>
.equipment-list {
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.equipment-item {
  margin-bottom: 20px;
}

.equipment-image-container {
  height: 200px;
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

.equipment-info {
  padding: 14px;
}

.equipment-name {
  margin: 0 0 10px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.equipment-category {
  margin: 0 0 10px;
  font-size: 14px;
  color: #909399;
}

.equipment-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.equipment-location {
  font-size: 13px;
  color: #606266;
}

.equipment-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  border-top: 1px solid #ebeef5;
  padding-top: 10px;
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
  margin-top: 30px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .filter-card .el-col {
    margin-bottom: 10px;
  }
}
</style>
