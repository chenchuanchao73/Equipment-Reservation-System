<template>
  <div class="db-viewer" v-if="isSuperAdmin">
    <el-row>
      <el-col :span="4" class="db-tables-list">
        <el-card shadow="never" style="height: 100%">
          <div slot="header"><b>数据库表</b></div>
          <el-scrollbar style="height: 70vh">
            <el-menu :default-active="selectedTable" @select="handleTableSelect">
              <el-menu-item v-for="table in tables" :key="table" :index="table">
                {{ table }}
              </el-menu-item>
            </el-menu>
          </el-scrollbar>
        </el-card>
      </el-col>
      <el-col :span="20" class="db-table-content">
        <el-card shadow="never" style="min-height: 70vh">
          <div slot="header" class="db-table-header">
            <span v-if="selectedTable"><b>{{ selectedTable }}</b>（共 {{ total }} 条）</span>
            <el-button v-if="selectedTable" size="mini" icon="el-icon-refresh" @click="refreshTable" style="float: right;">刷新</el-button>
          </div>
          <div v-if="selectedTable" class="table-container">
            <!-- 主表格区域：保留水平滚动容器 -->
            <div class="horizontal-scroll-container data-table-container">
              <el-table
                :data="rows"
                border
                size="small"
                :table-layout="isSmallTable ? 'fixed' : 'auto'"
                style="width: 100%"
                :height="540"
                class="custom-table"
                highlight-current-row
              >
                <el-table-column
                  v-for="col in columns"
                  :key="col.name"
                  :prop="col.name"
                  :label="col.name"
                  :width="isSmallTable ? getColumnWidth(col.name) : ''"
                  :min-width="isSmallTable ? '' : getColumnMinWidth(col.name)"
                  :formatter="formatCell"
                  show-overflow-tooltip
                  header-align="center"
                  align="center"
                />
              </el-table>
            </div>
            <el-pagination
              v-if="total > 0"
              background
              :layout="paginationLayout"
              :current-page.sync="page"
              :page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :pager-count="7"
              :total="total"
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
              style="margin-top: 16px; text-align: right;"
            />
            <div class="db-table-columns-info" style="margin-top: 16px;">
              <b>字段信息：</b>
              <!-- 字段信息区域：使用普通容器，无水平滚动提示 -->
              <div class="columns-info-container">
                <el-table :data="columns" border size="mini" table-layout="fixed" style="width: 100%; margin-top: 8px;">
                  <el-table-column prop="name" label="字段名" width="150" />
                  <el-table-column prop="type" label="类型" width="150" />
                  <el-table-column prop="nullable" label="可空" width="80">
                    <template slot-scope="scope">
                      <el-tag :type="scope.row.nullable ? 'info' : 'success'">{{ scope.row.nullable ? '是' : '否' }}</el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="comment" label="注释" min-width="250">
                    <template slot-scope="scope">
                      {{ getFieldComment(scope.row.name) }}
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
          <div v-else style="text-align:center; color:#888; padding: 60px 0;">请选择左侧表名</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
  <div v-else style="text-align:center; color:#888; padding: 60px 0;">正在加载数据库表...</div>
</template>

<script>
import { getDbTables, getDbTableColumns, getDbTableRows } from '@/api/dbAdmin'
import { mapState } from 'vuex'
import { formatDate } from '@/utils/date'

export default {
  name: 'DatabaseViewer',
  data() {
    return {
      tables: [],
      selectedTable: '',
      columns: [],
      rows: [],
      total: 0,
      page: 1,
      pageSize: 20,
      loading: false,
      inited: false,
      // 响应式布局相关
      isMobile: window.innerWidth <= 768,
      // 表字段注释对照表
      fieldComments: {
        // admin表：系统管理员
        'admin.id': '管理员唯一ID',
        'admin.username': '管理员登录账号',
        'admin.password_hash': '加密后的登录密码',
        'admin.name': '管理员姓名',
        'admin.role': '管理员角色（如superadmin）',
        'admin.is_active': '账号是否激活（1激活，0禁用）',
        'admin.created_at': '账号创建时间',

        // announcements表：公告表
        'announcements.id': '公告ID',
        'announcements.title': '公告标题',
        'announcements.content': '公告内容',
        'announcements.created_at': '公告创建（发布）时间',
        'announcements.is_active': '公告是否启用',

        // email_logs表：系统邮件发送日志
        'email_logs.id': '日志唯一ID',
        'email_logs.recipient': '收件人邮箱',
        'email_logs.subject': '邮件主题',
        'email_logs.template_key': '邮件模板标识',
        'email_logs.event_type': '触发邮件的事件类型',
        'email_logs.status': '发送状态（如success/failed）',
        'email_logs.error_message': '发送失败时的错误信息',
        'email_logs.reservation_code': '关联预约的编码',
        'email_logs.reservation_number': '关联预约的编号',
        'email_logs.created_at': '日志创建时间',
        'email_logs.content_html': '邮件HTML内容',

        // email_settings表：邮件服务器配置
        'email_settings.id': '配置唯一ID',
        'email_settings.smtp_server': 'SMTP服务器地址',
        'email_settings.smtp_port': 'SMTP服务器端口',
        'email_settings.sender_email': '发件人邮箱',
        'email_settings.sender_name': '发件人显示名称',
        'email_settings.smtp_username': 'SMTP登录用户名',
        'email_settings.smtp_password': 'SMTP登录密码',
        'email_settings.use_ssl': '是否使用SSL加密（1是，0否）',
        'email_settings.enabled': '配置是否启用（1启用，0禁用）',
        'email_settings.created_at': '配置创建时间',
        'email_settings.updated_at': '配置更新时间',
        'email_settings.cc_list': '抄送人列表，多个邮箱用逗号分隔',
        'email_settings.bcc_list':'密送人列表，多个邮箱用逗号分隔',

        // email_templates表：邮件模板
        'email_templates.id': '模板唯一ID',
        'email_templates.name': '模板名称',
        'email_templates.template_key': '模板标识（代码）',
        'email_templates.subject': '邮件主题模板',
        'email_templates.content_html': 'HTML格式邮件内容',
        'email_templates.content_text': '纯文本邮件内容',
        'email_templates.variables': '可用变量说明',
        'email_templates.language': '模板语言',
        'email_templates.created_at': '模板创建时间',
        'email_templates.updated_at': '模板更新时间',

        // equipment表：可预约设备
        'equipment.id': '设备唯一ID',
        'equipment.name': '设备名称',
        'equipment.category': '设备类别名称',
        'equipment.model': '设备型号',
        'equipment.location': '设备存放位置',
        'equipment.status': '设备状态（如可用/维修/借出）',
        'equipment.description': '设备详细描述',
        'equipment.image_path': '设备图片路径',
        'equipment.user_guide': '设备使用说明',
        'equipment.created_at': '设备信息创建时间',
        'equipment.updated_at': '设备信息更新时间',
        'equipment.video_tutorial': '设备视频教程地址',
        'equipment.category_id': '设备类别ID',
        'equipment.allow_simultaneous': '是否允许同时多人预约（1允许，0不允许）',
        'equipment.max_simultaneous': '最大同时预约人数',


        // equipment_category表：设备类别
        'equipment_category.id': '类别唯一ID',
        'equipment_category.name': '类别名称',
        'equipment_category.description': '类别描述',

        // equipment_time_slots表：设备时间段
        'equipment_time_slots.id': '时间段唯一ID',
        'equipment_time_slots.equipment_id': '关联的设备ID',
        'equipment_time_slots.start_datetime': '时间段开始时间',
        'equipment_time_slots.end_datetime': '时间段结束时间',
        'equipment_time_slots.current_count': '当前时间段内的预约数量',

        // recurring_reservation表：周期性预约
        'recurring_reservation.id': '周期预约唯一ID',
        'recurring_reservation.equipment_id': '设备ID',
        'recurring_reservation.pattern_type': '重复模式类型（如每周/每月）',
        'recurring_reservation.days_of_week': '每周重复的星期（如1,3,5）',
        'recurring_reservation.days_of_month': '每月重复的日期（如5,15,25）',
        'recurring_reservation.start_date': '预约周期开始日期',
        'recurring_reservation.end_date': '预约周期结束日期',
        'recurring_reservation.start_time': '每天预约开始时间',
        'recurring_reservation.end_time': '每天预约结束时间',
        'recurring_reservation.user_name': '预约人姓名',
        'recurring_reservation.user_department': '预约人部门',
        'recurring_reservation.user_contact': '预约人联系方式',
        'recurring_reservation.user_email': '预约人邮箱',
        'recurring_reservation.purpose': '预约用途',
        'recurring_reservation.status': '周期预约状态',
        'recurring_reservation.created_at': '创建时间',
        'recurring_reservation.reservation_code': '周期预约编码',
        'recurring_reservation.conflicts': '冲突日期列表，逗号分隔的YYYY-MM-DD格式',
        'recurring_reservation.total_planned': '计划创建的子预约总数',
        'recurring_reservation.created_count': '成功创建的子预约数量',




        // reservation表：单次预约
        'reservation.id': '预约唯一ID',
        'reservation.equipment_id': '设备ID',
        'reservation.reservation_code': '预约编码',
        'reservation.user_name': '预约人姓名',
        'reservation.user_department': '预约人部门',
        'reservation.user_contact': '预约人联系方式',
        'reservation.user_email': '预约人邮箱',
        'reservation.start_datetime': '预约开始时间',
        'reservation.end_datetime': '预约结束时间',
        'reservation.purpose': '预约用途',
        'reservation.status': '预约状态',
        'reservation.created_at': '预约创建时间',
        'reservation.recurring_reservation_id': '关联的周期预约ID',
        'reservation.is_exception': '是否为周期预约的特例',
        'reservation.reservation_number': '预约编号',
        'reservation.time_slot_id': '关联的设备时间段ID(整数)',

        // system_settings表：系统设置
        'system_settings.id': '设置唯一ID',
        'system_settings.site_name': '系统站点名称',
        'system_settings.maintenance_mode': '维护模式开关（1开启，0关闭）',
        'system_settings.reservation_limit_per_day': '单日预约上限',
        'system_settings.allow_equipment_conflict': '是否允许设备冲突预约（1允许，0不允许）',
        'system_settings.advance_reservation_days': '可提前预约天数',
        'system_settings.created_at': '设置创建时间',
        'system_settings.updated_at': '设置更新时间'
      }
    }
  },
  computed: {
    ...mapState({
      user: state => state.user,
    }),
    isSuperAdmin() {
      // 允许所有管理员访问数据库表查看功能
      return this.user && (this.user.role === 'superadmin' || this.user.role === 'admin')
    },
    // 判断是否为小表格（列少的表格）
    isSmallTable() {
      const smallTables = ['admin', 'equipment_category', 'system_settings', 'announcements','equipment_time_slots','reservation_history'];
      return !smallTables.includes(this.selectedTable);
    },

    // 根据屏幕宽度动态调整分页组件布局
    paginationLayout() {
      return this.isMobile
        ? 'prev, next'
        : 'total, sizes, prev, pager, next, jumper';
    }
  },
  created() {
    console.log("DatabaseViewer 组件 created")
    // 添加窗口大小变化的监听器
    window.addEventListener('resize', this.handleResize)
  },

  beforeDestroy() {
    // 移除窗口大小变化的监听器
    window.removeEventListener('resize', this.handleResize)
  },
  mounted() {
    console.log("DatabaseViewer 组件 mounted, 调用 initIfNeeded")
    this.initIfNeeded()
  },
  methods: {
    async initIfNeeded() {
      console.log("initIfNeeded 被调用，inited=", this.inited, "isSuperAdmin=", this.isSuperAdmin)
      if (!this.inited && this.isSuperAdmin) {
        this.inited = true
        await this.fetchTables()
      }
    },
    async fetchTables() {
      console.log("开始获取数据库表名...")
      try {
        console.log("调用 getDbTables()")
        const res = await getDbTables()
        console.log("获取表名结果:", res)
        this.tables = res.data.tables || []
        if (this.tables.length > 0) {
          this.handleTableSelect(this.tables[0])
        }
      } catch (e) {
        console.error("获取表名失败:", e)
        this.$message.error('获取表名失败: ' + (e.message || e))
      }
    },
    async handleTableSelect(table) {
      this.selectedTable = table
      this.page = 1
      await this.fetchTableColumns()
      await this.fetchTableRows()
    },
    async fetchTableColumns() {
      try {
        const res = await getDbTableColumns(this.selectedTable)
        // 兼容不同数据库字段名
        this.columns = (res.data.columns || []).map(col => ({
          name: col.name || col.column_name,
          type: col.type || col.type_name,
          nullable: col.nullable !== undefined ? col.nullable : col.nullable_,
          default: col.default,
          comment: col.comment || ''
        }))
      } catch (e) {
        this.columns = []
        this.$message.error('获取字段信息失败')
      }
    },
    async fetchTableRows() {
      this.loading = true
      try {
        const res = await getDbTableRows(this.selectedTable, {
          skip: (this.page - 1) * this.pageSize,
          limit: this.pageSize,
        })
        this.rows = res.data.rows || []

        // 使用后端返回的总行数
        if (res.data.total !== undefined) {
          this.total = res.data.total;
        } else {
          // 兼容旧版API，如果后端没有返回总行数，则使用简单估算
          if (this.rows.length < this.pageSize) {
            // 当前页不满，可能是最后一页
            this.total = (this.page - 1) * this.pageSize + this.rows.length;
          } else {
            // 当前页是满的，假设至少还有一页
            this.total = this.page * this.pageSize + this.pageSize;
          }
        }
      } catch (e) {
        this.rows = []
        this.$message.error('获取表数据失败')
      } finally {
        this.loading = false
      }
    },
    handlePageChange(page) {
      this.page = page
      this.fetchTableRows()
    },
    handleSizeChange(size) {
      this.pageSize = size
      this.page = 1
      this.fetchTableRows()
    },
    refreshTable() {
      this.fetchTableColumns()
      this.fetchTableRows()
    },

    // 处理窗口大小变化
    handleResize() {
      this.isMobile = window.innerWidth <= 768
    },
    // 获取字段注释 - 简化版本
    getFieldComment(fieldName) {
      const key = `${this.selectedTable}.${fieldName}`;
      return this.fieldComments[key] || '暂无注释';
    },
    // 获取最小列宽（用于自适应模式的表格）
    getColumnMinWidth(columnName) {
      const lowerColumnName = columnName.toLowerCase();

      // 针对特定表格中的特定列进行特殊处理
      if (this.selectedTable === 'admin') {
        if (lowerColumnName === 'id') return 80;
        if (lowerColumnName === 'username') return 150;
        if (lowerColumnName === 'password_hash') return 300;
        if (lowerColumnName === 'name') return 150;
        if (lowerColumnName === 'role') return 120;
        if (lowerColumnName === 'is_active') return 100;
        if (lowerColumnName === 'created_at') return 180;
        return 150;
      }

      if (this.selectedTable === 'equipment_category') {
        if (lowerColumnName === 'id') return 80;
        if (lowerColumnName === 'name') return 200;
        if (lowerColumnName === 'description') return 300;
        if (lowerColumnName === 'created_at') return 180;
        return 200;
      }

      if (this.selectedTable === 'system_settings') {
        if (lowerColumnName === 'id') return 80;
        if (lowerColumnName === 'key') return 200;
        if (lowerColumnName === 'value') return 400;
        if (lowerColumnName === 'description') return 300;
        return 200;
      }

      // 添加针对announcements表的最小列宽设置
      if (this.selectedTable === 'announcements') {
        if (lowerColumnName === 'id') return 80;
        if (lowerColumnName === 'title') return 250;
        if (lowerColumnName === 'content') return 450;
        if (lowerColumnName === 'created_at') return 180;
        if (lowerColumnName === 'is_active') return 120;
        return 150;
      }

      // 默认最小列宽
      if (lowerColumnName.includes('content_html') || lowerColumnName.includes('html')) {
        return 300;
      } else if (lowerColumnName === 'id') {
        return 80;
      } else if (lowerColumnName.includes('date') || lowerColumnName.includes('time')) {
        return 160;
      } else {
        return 120;
      }
    },

    // 标准列宽（用于固定模式的表格）
    getColumnWidth(columnName) {
      const lowerColumnName = columnName.toLowerCase();

      // 特殊表格特殊处理
      if (this.selectedTable === 'email_logs' && lowerColumnName === 'content_html') {
        return 500;
      }

      // 专门为announcements表添加列宽处理
      if (this.selectedTable === 'announcements') {
        if (lowerColumnName === 'id') return 80;
        if (lowerColumnName === 'title') return 200;
        if (lowerColumnName === 'content') return 350;
        if (lowerColumnName === 'created_at') return 180;
        if (lowerColumnName === 'is_active') return 120;
        return 150; // 其他可能的列
      }

      // 根据列名类型分配宽度
      if (lowerColumnName.includes('content_html') || lowerColumnName.includes('html') || lowerColumnName.includes('content')) {
        return 300;
      } else if (lowerColumnName === 'id') {
        return 80;
      } else if (lowerColumnName.includes('date') || lowerColumnName.includes('time')) {
        return 160;
      } else if (lowerColumnName.includes('name')) {
        return 120;
      } else if (lowerColumnName.includes('code') || lowerColumnName.includes('number')) {
        return 140;
      } else if (lowerColumnName.includes('title')) {
        return 120;
      } else if (lowerColumnName.includes('email')) {
        return 180;
      } else if (lowerColumnName.includes('description') || lowerColumnName.includes('comment')) {
        return 200;
      } else if (lowerColumnName.includes('status')) {
        return 120;
      } else if (lowerColumnName.includes('password') || lowerColumnName.includes('hash')) {
        return 250;
      } else {
        return 120;
      }
    },

    // 格式化单元格内容
    formatCell(row, column, cellValue) {
      if (cellValue === null || cellValue === undefined) {
        return '';
      }

      // 如果是HTML内容，只显示部分文本并添加提示
      if (column.property.toLowerCase().includes('content_html') || column.property.toLowerCase().includes('html')) {
        if (typeof cellValue === 'string' && cellValue.length > 100) {
          return cellValue.substring(0, 100) + '...';
        }
      }

      const tableName = this.selectedTable;
      const columnName = column.property;

      // 特殊处理recurring_reservation表的start_date和end_date，只显示日期部分
      if (tableName === 'recurring_reservation' &&
          (columnName === 'start_date' || columnName === 'end_date')) {
        if (typeof cellValue === 'string' && cellValue.length >= 10) {
          return cellValue.substring(0, 10); // 只保留YYYY-MM-DD部分
        }
      }

      // 特殊处理recurring_reservation表的start_time和end_time，移除微秒
      if (tableName === 'recurring_reservation' &&
          (columnName === 'start_time' || columnName === 'end_time')) {
        if (typeof cellValue === 'string') {
          // 如果包含空格（例如"09:00:00 000000"）
          if (cellValue.includes(' ')) {
            return cellValue.split(' ')[0]; // 只保留时间部分
          }
          // 如果只有时间部分
          return cellValue;
        }
      }

      // 对日期时间格式化，不进行时区转换
      // 排除明确是ID字段的列，比如time_slot_id
      if (column.property !== 'time_slot_id' && column.property !== 'timeslot_number' &&
          (column.property.toLowerCase().includes('date') || column.property.toLowerCase().includes('time')) &&
          !isNaN(Date.parse(cellValue))) {
        try {
          // 以下字段已经是北京时间，不需要再转换
          const skipTimeZoneConversion = [
            'updated_at', 'created_at', 'start_datetime', 'end_datetime'
          ];

          // 不进行时区转换，直接显示数据库中的原始时间
          const toBeijingTime = false;

          // 根据字段类型选择显示格式
          let format = 'YYYY-MM-DD HH:mm:ss';

          // 只显示日期部分
          if (columnName === 'start_date' || columnName === 'end_date') {
            format = 'YYYY-MM-DD';
          }

          // 只显示时间部分
          if (columnName === 'start_time' || columnName === 'end_time') {
            format = 'HH:mm:ss';
          }

          return formatDate(cellValue, format, toBeijingTime);
        } catch (e) {
          console.error('日期格式化错误:', e);
          return cellValue;
        }
      }

      return cellValue;
    }
  },
}
</script>

<style>
.db-viewer {
  padding: 24px;
}
.db-tables-list {
  border-right: 1px solid #eee;
  min-height: 70vh;
}
.db-table-content {
  padding-left: 24px;
}
.db-table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.table-container {
  position: relative;
  margin-bottom: 16px;
}

/* 修改这里：优化水平滚动容器样式 */
.horizontal-scroll-container {
  width: 100%;
  overflow-x: auto !important;
  overflow-y: hidden;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
  margin-bottom: 5px;
  /* 确保滚动条始终可见 */
  scrollbar-width: auto;
  scrollbar-color: #909399 #f5f7fa;
}

/* 只为数据表格容器添加滚动提示文字 */
.data-table-container::after {
  content: '← 左右滑动可查看更多数据 →';
  position: absolute;
  bottom: 5px;
  right: 10px;
  font-size: 12px;
  color: #909399;
  background: rgba(255,255,255,0.8);
  padding: 2px 8px;
  border-radius: 4px;
  opacity: 0.7;
  z-index: 1;
}

/* 为字段信息容器移除滚动提示 */
.columns-info-container {
  width: 100%;
  overflow: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

/* 修改滚动条样式使其更明显 - 灰色滚动条 */
::-webkit-scrollbar {
  width: 12px !important;
  height: 12px !important;
  background-color: #f5f7fa !important;
}
::-webkit-scrollbar-thumb {
  background-color: #909399 !important;
  border-radius: 6px !important;
  border: 2px solid #f5f7fa !important;
}
::-webkit-scrollbar-thumb:hover {
  background-color: #606266 !important;
}
::-webkit-scrollbar-corner {
  background-color: #f5f7fa !important;
}

/* 强制表格显示滚动条 */
.el-table__body-wrapper {
  overflow: auto !important;
}

/* 表格样式优化 */
.el-table__header th {
  background-color: #f5f7fa !important;
  color: #606266 !important;
  font-weight: bold !important;
  padding: 8px 0 !important;
  white-space: nowrap;
}

/* 确保单元格内容不换行，允许水平滚动 */
.el-table .cell {
  white-space: nowrap !important;
}

/* 修复行高问题 */
.el-table__row {
  height: auto !important;
}

/* 修改tooltip样式 */
.el-tooltip__popper {
  max-width: 400px !important;
  white-space: pre-wrap !important;
  word-break: break-word !important;
}

/* 改进分页器外观 */
.el-pagination {
  padding: 16px 6px !important;
  background-color: #f9f9f9 !important;
  border-radius: 4px !important;
}

/* 字段信息表样式 */
.db-table-columns-info .el-table {
  margin-top: 10px !important;
}
.db-table-columns-info .el-table__header th {
  background-color: #f5f7fa !important;
  color: #606266 !important;
  padding: 8px !important;
}
.db-table-columns-info .el-table__cell {
  padding: 8px !important;
}
</style>