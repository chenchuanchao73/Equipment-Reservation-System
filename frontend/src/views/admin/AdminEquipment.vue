<template>
  <div class="admin-equipment">
    <div class="page-header">
      <h2>设备管理</h2>
      <div class="page-actions">
        <el-button
          type="primary"
          icon="el-icon-plus"
          @click="handleAdd"
        >
          添加设备
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filter" class="filter-form">
        <el-form-item :label="$t('equipment.category')">
          <el-select
            v-model="filter.category"
            :placeholder="$t('equipment.allCategories')"
            clearable
            @change="handleFilterChange"
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item :label="$t('equipment.status')">
          <el-select
            v-model="filter.status"
            :placeholder="$t('equipment.allStatus')"
            clearable
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
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="filter.search"
            :placeholder="$t('equipment.searchPlaceholder')"
            clearable
            @keyup.enter.native="handleFilterChange"
          >
            <el-button
              slot="append"
              icon="el-icon-search"
              @click="handleFilterChange"
            ></el-button>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 设备列表 -->
    <el-table
      v-loading="loading"
      :data="equipments"
      border
      stripe
      style="width: 100%; margin-top: 20px;"
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
        label="设备名称"
        width="120"
      ></el-table-column>

      <el-table-column
        prop="category"
        label="设备类别"
        width="120"
      ></el-table-column>

      <el-table-column
        prop="location"
        label="设备位置"
        width="100"
      ></el-table-column>

      <el-table-column
        prop="description"
        label="设备描述"
        min-width="150"
      >
        <template slot-scope="scope">
          {{ scope.row.description || '无' }}
        </template>
      </el-table-column>

      <el-table-column
        prop="status"
        label="设备状态"
        width="100"
      >
        <template slot-scope="scope">
          <el-tag
            :type="scope.row.status === 'available' ? 'success' : 'warning'"
            size="small"
          >
            {{ scope.row.status === 'available' ? '可用' : '维护中' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column
        label="可同时预定"
        width="110"
        align="center"
      >
        <template slot-scope="scope">
          <el-tag
            :type="scope.row.allow_simultaneous ? 'success' : 'info'"
            size="small"
          >
            {{ scope.row.allow_simultaneous ? `支持(${scope.row.max_simultaneous}人)` : '不支持' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column
        label="设备图片"
        width="100"
        align="center"
      >
        <template slot-scope="scope">
          <div>
            <el-image
              :src="scope.row.image_path ? getFullImageUrl(scope.row.image_path) : require('@/assets/upload.png')"
              :preview-src-list="scope.row.image_path ? [getFullImageUrl(scope.row.image_path)] : []"
              style="width: 60px; height: 60px;"
              fit="contain"
              :class="scope.row.image_path ? 'preview-image' : 'default-image'"
              @error="() => handleImageLoadError(scope.row)"
            ></el-image>
          </div>
        </template>
      </el-table-column>

      <el-table-column
        label="操作"
        width="200"
      >
        <template slot-scope="scope">
          <el-button
            type="text"
            size="small"
            @click="handleEdit(scope.row)"
          >
            编辑
          </el-button>

          <el-button
            v-if="scope.row.image_path"
            type="text"
            size="small"
            @click="handleUploadImage(scope.row)"
          >
            更换图片
          </el-button>

          <el-button
            type="text"
            size="small"
            class="danger-button"
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
        :page-size="pageSize"
        :current-page.sync="currentPage"
        @current-change="handlePageChange"
      ></el-pagination>
    </div>

    <!-- 添加/编辑设备对话框 -->
    <el-dialog
      :title="dialogType === 'add' ? '添加设备' : '编辑设备'"
      :visible.sync="dialogVisible"
      width="50%"
      @close="resetForm"
    >
      <el-form
        ref="form"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name"></el-input>
        </el-form-item>

        <el-form-item label="设备类别" prop="category">
          <el-select
            v-model="form.category"
            filterable
            allow-create
            default-first-option
            style="width: 100%"
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            ></el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="设备型号" prop="model">
          <el-input v-model="form.model"></el-input>
        </el-form-item>

        <el-form-item label="设备位置" prop="location">
          <el-input v-model="form.location"></el-input>
        </el-form-item>

        <el-form-item label="设备状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="available">可用</el-radio>
            <el-radio label="maintenance">维护中</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="可同时预定" prop="allow_simultaneous">
          <el-switch
            v-model="form.allow_simultaneous"
            active-text="启用"
            inactive-text="禁用"
          ></el-switch>

          <div v-if="form.allow_simultaneous" style="margin-top: 10px;">
            <el-form-item label="最大预定人数" prop="max_simultaneous">
              <el-input-number
                v-model="form.max_simultaneous"
                :min="1"
                :max="20"
                size="small"
              ></el-input-number>
              <div class="form-tip">设置可同时预定的最大人数</div>
            </el-form-item>
          </div>
        </el-form-item>

        <el-form-item label="设备描述" prop="description">
          <el-input
            type="textarea"
            v-model="form.description"
            :rows="4"
          ></el-input>
        </el-form-item>

        <el-form-item label="使用指南" prop="user_guide">
          <rich-text-editor
            v-model="form.user_guide"
            placeholder="请输入设备的详细使用步骤、注意事项等信息..."
          ></rich-text-editor>
        </el-form-item>

        <el-form-item label="视频教程" prop="video_tutorial">
          <el-input
            v-model="form.video_tutorial"
            placeholder="请输入视频链接，支持YouTube、Bilibili等平台"
          >
            <template slot="prepend">
              <el-select
                v-model="videoType"
                style="width: 120px;"
                @change="handleVideoTypeChange"
              >
                <el-option label="YouTube" value="youtube"></el-option>
                <el-option label="Bilibili" value="bilibili"></el-option>
                <el-option label="其他" value="other"></el-option>
              </el-select>
            </template>
          </el-input>
          <div class="video-tip">输入视频链接后可以在设备详情页面查看视频教程</div>
        </el-form-item>

        <el-form-item label="设备图片">
          <div class="equipment-image-uploader">
            <img v-if="form.image_path" :src="getFullImageUrl(form.image_path)" class="equipment-image">
            <img v-else :src="require('@/assets/upload.png')" class="equipment-image default-equipment-image">
          </div>
          <div class="image-tip">建议尺寸：800x600像素，最大8MB</div>
          <div class="manual-upload">
            <el-button size="small" type="primary" @click="triggerManualUpload">手动上传</el-button>
            <input
              ref="manualFileInput"
              type="file"
              accept="image/*"
              style="display: none;"
              @change="handleManualFileChange"
            >
          </div>
        </el-form-item>
      </el-form>

      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
      </span>
    </el-dialog>

    <!-- 上传图片对话框 -->
    <el-dialog
      title="上传设备图片"
      :visible.sync="uploadDialogVisible"
      width="30%"
    >
      <div class="equipment-image-uploader">
        <img v-if="imageUrl" :src="getFullImageUrl(imageUrl)" class="equipment-image">
        <img v-else :src="require('@/assets/upload.png')" class="equipment-image default-equipment-image">
      </div>
      <div class="image-tip">建议尺寸：800x600像素，最大8MB</div>
      <div class="manual-upload">
        <el-button size="small" type="primary" @click="triggerDialogManualUpload">手动上传</el-button>
        <input
          ref="dialogManualFileInput"
          type="file"
          accept="image/*"
          style="display: none;"
          @change="handleDialogManualFileChange"
        >
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="uploadDialogVisible = false">取消</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { equipmentApi, categoryApi } from '@/api'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import axios from 'axios'

export default {
  name: 'AdminEquipment',

  components: {
    RichTextEditor
  },

  data() {
    return {
      loading: false,
      submitting: false,
      equipments: [],
      total: 0,
      currentPage: 1,
      pageSize: 10,
      categories: [],
      filter: {
        category: '',
        status: '',
        search: ''
      },
      // 响应式布局相关
      isMobile: window.innerWidth <= 768,

      dialogVisible: false,
      dialogType: 'add', // 'add' or 'edit'
      form: {
        id: null,
        name: '',
        category: '',
        model: '',
        location: '',
        status: 'available',
        description: '',
        user_guide: '',
        video_tutorial: '',
        image_path: '',
        allow_simultaneous: false,
        max_simultaneous: 1
      },
      rules: {
        name: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'blur' }
        ],
        category: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' }
        ],
        status: [
          { required: true, message: this.$t('reservation.requiredField'), trigger: 'change' }
        ]
      },

      uploadDialogVisible: false,
      currentEquipment: {},
      imageUrl: '',

      // 上传相关
      uploadUrl: axios.defaults.baseURL + '/api/equipment/upload-image',

      // 视频相关
      videoType: 'youtube',

      // 富文本编辑器选项
      editorOptions: {
        modules: {
          toolbar: [
            ['bold', 'italic', 'underline', 'strike'],
            ['blockquote', 'code-block'],
            [{ 'header': 1 }, { 'header': 2 }],
            [{ 'list': 'ordered' }, { 'list': 'bullet' }],
            [{ 'script': 'sub' }, { 'script': 'super' }],
            [{ 'indent': '-1' }, { 'indent': '+1' }],
            [{ 'direction': 'rtl' }],
            [{ 'size': ['small', false, 'large', 'huge'] }],
            [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
            [{ 'color': [] }, { 'background': [] }],
            [{ 'font': [] }],
            [{ 'align': [] }],
            ['clean'],
            ['link', 'image', 'video']
          ]
        },
        placeholder: '',
        theme: 'snow'
      },
    }
  },

  computed: {
    // 获取token
    getToken() {
      return localStorage.getItem('token') || ''
    },

    uploadHeaders() {
      return {
        Authorization: `Bearer ${localStorage.getItem('token') || ''}`
      }
    },

    // 获取完整的图片URL
    baseUrl() {
      return axios.defaults.baseURL || 'http://localhost:8000';
    },

    // 根据屏幕宽度动态调整分页组件布局
    paginationLayout() {
      return this.isMobile
        ? 'prev, next'
        : 'total, prev, pager, next';
    }
  },

  created() {
    this.fetchData()
    this.fetchCategories()
    // 添加窗口大小变化的监听器
    window.addEventListener('resize', this.handleResize)
  },

  beforeDestroy() {
    // 移除窗口大小变化的监听器
    window.removeEventListener('resize', this.handleResize)
  },

  methods: {
    // 获取设备列表
    async fetchData() {
      try {
        this.loading = true

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
        console.error('获取设备列表失败:', error)
        this.$message.error(this.$t('error.serverError'))
      } finally {
        this.loading = false
      }
    },

    // 获取设备类别
    async fetchCategories() {
      try {
        const response = await categoryApi.getAllCategories()
        this.categories = response.data.map(item => item.name)
      } catch (error) {
        console.error('获取设备类别失败:', error)
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

    // 添加设备
    handleAdd() {
      this.dialogType = 'add'
      this.form = {
        id: null,
        name: '',
        category: '',
        model: '',
        location: '',
        status: 'available',
        description: '',
        user_guide: '',
        video_tutorial: '',
        image_path: '',
        allow_simultaneous: false,
        max_simultaneous: 1
      }
      this.dialogVisible = true
    },

    // 编辑设备
    handleEdit(row) {
      this.dialogType = 'edit'
      this.form = { ...row }
      this.dialogVisible = true
    },

    // 删除设备
    handleDelete(row) {
      this.$confirm(
        this.$t('admin.confirmDeleteEquipment'),
        this.$t('common.warning'),
        {
          confirmButtonText: this.$t('common.confirm'),
          cancelButtonText: this.$t('common.cancel'),
          type: 'warning'
        }
      ).then(async () => {
        try {
          this.loading = true

          await equipmentApi.deleteEquipment(row.id)

          this.$message.success(this.$t('admin.equipmentDeleted'))
          this.fetchData()
        } catch (error) {
          console.error('删除设备失败:', error)
          this.$message.error(this.$t('error.serverError'))
        } finally {
          this.loading = false
        }
      }).catch(() => {
        // 取消删除，不做任何处理
      })
    },

    // 上传设备图片
    handleUploadImage(row) {
      this.currentEquipment = row
      this.imageUrl = row.image_path || ''
      this.uploadDialogVisible = true
    },

    // 提交表单
    submitForm() {
      this.$refs.form.validate(async valid => {
        if (!valid) return

        try {
          this.submitting = true

          if (this.dialogType === 'add') {
            // 创建设备
            const response = await equipmentApi.createEquipment(this.form)
            this.$message.success(this.$t('admin.equipmentAdded'))
          } else {
            // 更新设备
            const response = await equipmentApi.updateEquipment(this.form.id, this.form)
            this.$message.success(this.$t('admin.equipmentUpdated'))
          }

          this.dialogVisible = false
          this.fetchData()
        } catch (error) {
          console.error('保存设备失败:', error)
          this.$message.error(this.$t('error.serverError'))
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
    },

    // 上传前验证
    beforeUpload(file) {
      const isImage = file.type.startsWith('image/')
      const isLt8M = file.size / 1024 / 1024 < 8

      if (!isImage) {
        this.$message.error(this.$t('admin.imageTypeError'))
        return false
      }

      if (!isLt8M) {
        this.$message.error(this.$t('admin.imageSizeError').replace('2MB', '8MB'))
        return false
      }

      return true
    },

    // 上传成功（添加/编辑表单中）
    handleUploadSuccess(response) {
      this.form.image_path = response.data.image_url
      this.$message.success(this.$t('admin.imageUploadSuccess'))
    },

    // 上传成功（单独上传图片对话框）
    handleImageUploadSuccess(response) {
      this.imageUrl = response.data.image_url
      this.currentEquipment.image_path = response.data.image_url

      // 更新设备列表中的图片URL
      const index = this.equipments.findIndex(item => item.id === this.currentEquipment.id)
      if (index !== -1) {
        this.$set(this.equipments, index, { ...this.currentEquipment })
      }

      this.$message.success(this.$t('admin.imageUploadSuccess'))

      // 关闭对话框
      setTimeout(() => {
        this.uploadDialogVisible = false
      }, 1500)
    },

    // 上传失败
    handleUploadError(error, file) {
      console.error('上传图片失败:', error)
      console.log('文件信息:', file ? {
        name: file.name,
        size: file.size,
        type: file.type,
        lastModified: file.lastModified
      } : 'No file info')

      // 尝试获取更详细的错误信息
      let errorMessage = this.$t('admin.imageUploadError')
      if (error.response && error.response.data) {
        console.error('错误响应数据:', error.response.data)
        if (error.response.data.detail) {
          errorMessage += ': ' + error.response.data.detail
        }
      }

      this.$message.error(errorMessage)
    },

    // 处理视频类型变化
    handleVideoTypeChange() {
      // 如果已经有视频URL，则根据新的视频类型进行转换
      if (this.form.video_tutorial) {
        // 提取视频ID
        let videoId = ''

        // 尝试从当前的URL中提取视频ID
        if (this.form.video_tutorial.includes('youtube.com') || this.form.video_tutorial.includes('youtu.be')) {
          // 从 YouTube URL 提取视频ID
          const match = this.form.video_tutorial.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})/)
          if (match && match[1]) {
            videoId = match[1]
          }
        } else if (this.form.video_tutorial.includes('bilibili.com')) {
          // 从 Bilibili URL 提取视频ID
          const match = this.form.video_tutorial.match(/bilibili\.com\/video\/([^\/?]+)/)
          if (match && match[1]) {
            videoId = match[1].replace('BV', '')
          }
        }

        // 如果成功提取到视频ID，则根据新的视频类型生成URL
        if (videoId) {
          switch (this.videoType) {
            case 'youtube':
              this.form.video_tutorial = `https://www.youtube.com/embed/${videoId}`
              break
            case 'bilibili':
              this.form.video_tutorial = `https://player.bilibili.com/player.html?bvid=BV${videoId}`
              break
            default:
              // 其他类型不做处理
              break
          }
        }
      }
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

    // 触发手动上传
    triggerManualUpload() {
      this.$refs.manualFileInput.click()
    },

    // 处理手动文件选择
    async handleManualFileChange(event) {
      const file = event.target.files[0]
      if (!file) return

      // 验证文件
      const isImage = file.type.startsWith('image/')
      const isLt8M = file.size / 1024 / 1024 < 8

      if (!isImage) {
        this.$message.error(this.$t('admin.imageTypeError'))
        return
      }

      if (!isLt8M) {
        this.$message.error(this.$t('admin.imageSizeError').replace('2MB', '8MB'))
        return
      }

      // 创建 FormData
      const formData = new FormData()
      formData.append('file', file)

      try {
        this.loading = true

        // 直接使用 axios 发送请求
        const response = await axios.post(this.uploadUrl, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          }
        })

        // 处理成功响应
        this.form.image_path = response.data.data.image_url
        this.$message.success(this.$t('admin.imageUploadSuccess'))
      } catch (error) {
        console.error('手动上传图片失败:', error)
        console.log('文件信息:', {
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified
        })

        // 尝试获取更详细的错误信息
        let errorMessage = this.$t('admin.imageUploadError')
        if (error.response && error.response.data) {
          console.error('错误响应数据:', error.response.data)
          if (error.response.data.detail) {
            errorMessage += ': ' + error.response.data.detail
          }
        }

        this.$message.error(errorMessage)
      } finally {
        this.loading = false
        // 清空文件输入框，允许再次选择同一文件
        this.$refs.manualFileInput.value = ''
      }
    },

    // 触发对话框手动上传
    triggerDialogManualUpload() {
      this.$refs.dialogManualFileInput.click()
    },

    // 处理图片加载失败
    handleImageLoadError(row) {
      console.log('图片加载失败，使用默认图片', row)
      // 如果图片加载失败，将image_path设置为空，这样会显示默认图片
      if (row && row.image_path) {
        // 在Vue中安全地更新对象属性
        this.$set(row, 'image_path', '')
      }
    },

    // 处理对话框手动文件选择
    async handleDialogManualFileChange(event) {
      const file = event.target.files[0]
      if (!file) return

      // 验证文件
      const isImage = file.type.startsWith('image/')
      const isLt8M = file.size / 1024 / 1024 < 8

      if (!isImage) {
        this.$message.error(this.$t('admin.imageTypeError'))
        return
      }

      if (!isLt8M) {
        this.$message.error(this.$t('admin.imageSizeError').replace('2MB', '8MB'))
        return
      }

      // 创建 FormData
      const formData = new FormData()
      formData.append('file', file)
      if (this.currentEquipment.id) {
        formData.append('equipment_id', this.currentEquipment.id)
      }

      try {
        this.loading = true

        // 直接使用 axios 发送请求
        const response = await axios.post(this.uploadUrl, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
          }
        })

        // 处理成功响应
        this.imageUrl = response.data.data.image_url
        this.currentEquipment.image_path = response.data.data.image_url

        // 更新设备列表中的图片URL
        const index = this.equipments.findIndex(item => item.id === this.currentEquipment.id)
        if (index !== -1) {
          this.$set(this.equipments, index, { ...this.currentEquipment })
        }

        this.$message.success(this.$t('admin.imageUploadSuccess'))

        // 关闭对话框
        setTimeout(() => {
          this.uploadDialogVisible = false
        }, 1500)
      } catch (error) {
        console.error('手动上传图片失败:', error)
        console.log('文件信息:', {
          name: file.name,
          size: file.size,
          type: file.type,
          lastModified: file.lastModified
        })

        // 尝试获取更详细的错误信息
        let errorMessage = this.$t('admin.imageUploadError')
        if (error.response && error.response.data) {
          console.error('错误响应数据:', error.response.data)
          if (error.response.data.detail) {
            errorMessage += ': ' + error.response.data.detail
          }
        }

        this.$message.error(errorMessage)
      } finally {
        this.loading = false
        // 清空文件输入框，允许再次选择同一文件
        this.$refs.dialogManualFileInput.value = ''
      }
    }
  }
}
</script>

<style scoped>
.admin-equipment {
  padding: 20px;
  width: 100%;
  max-width: 100%;
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

.page-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form .el-form-item {
  margin-bottom: 0;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}

.quill-editor {
  height: 300px;
  margin-bottom: 10px;
}

.editor-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.danger-button {
  color: #F56C6C;
}

.equipment-image-uploader {
  text-align: center;
}

.equipment-image-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 300px;
  height: 225px;
  display: inline-block;
}

.equipment-image-uploader .el-upload:hover {
  border-color: #409EFF;
}

.equipment-image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 300px;
  height: 225px;
  line-height: 225px;
  text-align: center;
}

.equipment-image {
  width: 300px;
  height: 225px;
  display: block;
  object-fit: contain;
}

.default-equipment-image {
  opacity: 0.7;
  background-color: #f5f7fa;
  padding: 20px;
  box-sizing: border-box;
}

.image-tip,
.video-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.manual-upload {
  margin-top: 10px;
}

.clickable-image {
  cursor: pointer;
  transition: all 0.3s;
}

.clickable-image:hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.preview-image {
  cursor: zoom-in;
  transition: all 0.3s;
}

.preview-image:hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.default-image {
  cursor: default;
  opacity: 0.7;
  transition: all 0.3s;
}

.default-image:hover {
  opacity: 1;
}

.text-center {
  text-align: center !important;
}

@media (max-width: 768px) {
  .admin-equipment {
    padding: 10px;
  }

  .filter-form {
    display: flex;
    flex-direction: column;
  }

  .filter-form .el-form-item {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>
