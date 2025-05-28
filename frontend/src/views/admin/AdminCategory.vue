<template>
  <div class="admin-category">
    <h1 class="page-title">设备类别管理</h1>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleAdd">
        <i class="el-icon-plus"></i> 添加类别
      </el-button>

      <div class="search-box">
        <el-input
          v-model="filter.search"
          placeholder="搜索类别名称"
          clearable
          @clear="handleFilterChange"
          @keyup.enter.native="handleFilterChange"
        >
          <el-button
            slot="append"
            icon="el-icon-search"
            @click="handleFilterChange"
          ></el-button>
        </el-input>
      </div>
    </div>

    <!-- 类别表格 -->
    <el-table
      v-loading="loading"
      :data="categories"
      border
      stripe
      style="width: 100%"
      header-align="center"
      cell-class-name="text-center"
    >
      <el-table-column
        prop="id"
        label="ID"
        width="80"
      ></el-table-column>

      <el-table-column
        prop="name"
        label="类别名称"
        min-width="150"
      ></el-table-column>

      <el-table-column
        prop="description"
        label="描述"
        min-width="250"
      >
        <template slot-scope="scope">
          {{ scope.row.description || '无' }}
        </template>
      </el-table-column>

      <el-table-column
        label="操作"
        width="200"
        align="center"
      >
        <template slot-scope="scope">
          <el-button
            size="mini"
            type="primary"
            @click="handleEdit(scope.row)"
          >
            编辑
          </el-button>
          <el-button
            size="mini"
            type="danger"
            @click="handleDelete(scope.row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        background
        :layout="paginationLayout"
        :total="total"
        :current-page.sync="currentPage"
        :page-size="pageSize"
        @current-change="handlePageChange"
      ></el-pagination>
    </div>

    <!-- 添加/编辑类别对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '添加类别' : '编辑类别'"
      :visible.sync="dialogVisible"
      width="40%"
      @close="resetForm"
    >
      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="类别名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            type="textarea"
            v-model="form.description"
            :rows="4"
          ></el-input>
        </el-form-item>
      </el-form>

      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { categoryApi } from '@/api'

export default {
  name: 'AdminCategory',

  data() {
    return {
      loading: false,
      submitting: false,
      categories: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      filter: {
        search: ''
      },
      // 响应式布局相关
      isMobile: window.innerWidth <= 768,

      dialogVisible: false,
      dialogType: 'add', // 'add' or 'edit'
      form: {
        id: null,
        name: '',
        description: ''
      },
      rules: {
        name: [
          { required: true, message: '请输入类别名称', trigger: 'blur' },
          { min: 1, max: 50, message: '长度在 1 到 50 个字符', trigger: 'blur' }
        ]
      }
    }
  },

  computed: {
    ...mapGetters(['getToken']),

    // 根据屏幕宽度动态调整分页组件布局
    paginationLayout() {
      return this.isMobile
        ? 'prev, next'
        : 'total, prev, pager, next';
    }
  },

  created() {
    this.fetchData()
    // 添加窗口大小变化的监听器
    window.addEventListener('resize', this.handleResize)
  },

  beforeDestroy() {
    // 移除窗口大小变化的监听器
    window.removeEventListener('resize', this.handleResize)
  },

  methods: {
    // 获取类别列表
    async fetchData() {
      try {
        this.loading = true

        const params = {
          skip: (this.currentPage - 1) * this.pageSize,
          limit: this.pageSize,
          search: this.filter.search || undefined
        }

        const response = await categoryApi.getCategories(params)
        this.categories = response.data.items
        this.total = response.data.total
      } catch (error) {
        console.error('获取类别列表失败:', error)
        this.$message.error('获取类别列表失败')
      } finally {
        this.loading = false
      }
    },

    // 处理筛选条件变化
    handleFilterChange() {
      this.currentPage = 1
      this.fetchData()
    },

    // 处理页码变化
    handlePageChange(page) {
      this.currentPage = page
      this.fetchData()
    },

    // 处理窗口大小变化
    handleResize() {
      this.isMobile = window.innerWidth <= 768
    },

    // 添加类别
    handleAdd() {
      this.dialogType = 'add'
      this.form = {
        id: null,
        name: '',
        description: ''
      }
      this.dialogVisible = true
    },

    // 编辑类别
    handleEdit(row) {
      this.dialogType = 'edit'
      this.form = { ...row }
      this.dialogVisible = true
    },

    // 删除类别
    handleDelete(row) {
      this.$confirm(
        '确定要删除该类别吗？删除后不可恢复，且可能影响已使用该类别的设备。',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          this.loading = true

          await categoryApi.deleteCategory(row.id)

          this.$message.success('类别已删除')
          this.fetchData()
        } catch (error) {
          console.error('删除类别失败:', error)
          this.$message.error('删除类别失败')
        } finally {
          this.loading = false
        }
      }).catch(() => {
        // 取消删除，不做任何处理
      })
    },

    // 提交表单
    submitForm() {
      this.$refs.form.validate(async valid => {
        if (!valid) return

        try {
          this.submitting = true

          if (this.dialogType === 'add') {
            // 创建类别
            await categoryApi.createCategory(this.form)
            this.$message.success('类别添加成功')
          } else {
            // 更新类别
            await categoryApi.updateCategory(this.form.id, this.form)
            this.$message.success('类别更新成功')
          }

          this.dialogVisible = false
          this.fetchData()
        } catch (error) {
          console.error('保存类别失败:', error)
          if (error.response && error.response.data && error.response.data.detail) {
            this.$message.error(error.response.data.detail)
          } else {
            this.$message.error('保存类别失败')
          }
        } finally {
          this.submitting = false
        }
      })
    },

    // 重置表单
    resetForm() {
      if (this.$refs.form) {
        this.$refs.form.resetFields()
      }
    }
  }
}
</script>

<style scoped>
.admin-category {
  padding: 20px;
  width: 100%;
  max-width: 100%;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #303133;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-box {
  width: 300px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.text-center {
  text-align: center !important;
}
</style>
