<template>
  <div class="reservation-query">
    <h1 class="page-title">{{ $t('reservation.personalManagement') }}</h1>

    <div class="query-card">
      <el-card shadow="never">
        <!-- 个人预约管理表单 -->
        <el-form
          ref="personalQueryForm"
          :model="personalQueryForm"
          :rules="personalQueryRules"
          label-position="top"
          @submit.native.prevent="handlePersonalQuery"
        >
          <el-form-item :label="$t('reservation.code')" prop="reservationCode">
            <el-input
              v-model="personalQueryForm.reservationCode"
              :placeholder="$t('reservation.codeOrContactRequired')"
            ></el-input>
          </el-form-item>

          <el-form-item :label="$t('reservation.userContact')" prop="userContact">
            <el-input
              v-model="personalQueryForm.userContact"
              :placeholder="$t('reservation.contactOrCodeRequired')"
            ></el-input>
          </el-form-item>

          <el-form-item>
            <div class="form-tip">
              <i class="el-icon-info"></i>
              <span>{{ $t('reservation.queryTip') }}</span>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              icon="el-icon-search"
              @click="handlePersonalQuery"
              :loading="personalLoading"
            >
              {{ $t('reservation.queryButton') }}
            </el-button>
            <el-button @click="resetForm" icon="el-icon-refresh-left">{{ $t('common.reset') }}</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 个人预约结果表格 -->
    <div v-if="personalQueryResults.length > 1" class="query-results">
      <el-card shadow="never">
        <div slot="header" style="font-size: 16px; font-weight: bold;">
          <i class="el-icon-document"></i>
          <span>{{ $t('reservation.queryResults') }}</span>
        </div>
        <el-table :data="personalQueryResults" style="width: 100%" border stripe>
          <el-table-column prop="reservation_code" :label="$t('reservation.code')" min-width="120" />
          <el-table-column prop="equipment_name" :label="$t('reservation.equipmentName')" min-width="120" />
          <el-table-column prop="start_datetime" :label="$t('reservation.startTime')" min-width="160" :formatter="formatDateTime" />
          <el-table-column prop="end_datetime" :label="$t('reservation.endTime')" min-width="160" :formatter="formatDateTime" />
          <el-table-column prop="status" :label="$t('common.status')" width="80">
            <template slot-scope="scope">
              <el-tag :type="getStatusType(scope.row)">{{ getStatusText(scope.row) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" width="120">
            <template slot-scope="scope">
              <el-button type="primary" size="mini" @click="viewReservationDetail(scope.row)">
                {{ $t('common.view') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 个人预约管理说明 -->
    <div v-if="showInstructions" class="instructions-card">
      <el-card shadow="hover">
        <div slot="header" style="font-size: 16px; font-weight: bold;">
          <i class="el-icon-info" style="color: #409EFF; margin-right: 5px;"></i>
          <span>{{ $t('common.instructions') }}</span>
        </div>

        <div class="instructions-content">
          <p>{{ $t('reservation.queryInstructions') }}</p>
          <ul>
            <li><i class="el-icon-arrow-right" style="color: #409EFF; margin-right: 5px;"></i>{{ $t('reservation.queryInstruction1') }}</li>
            <li><i class="el-icon-arrow-right" style="color: #409EFF; margin-right: 5px;"></i>{{ $t('reservation.queryInstruction2') }}</li>
            <li><i class="el-icon-arrow-right" style="color: #409EFF; margin-right: 5px;"></i>{{ $t('reservation.queryInstruction3') }}</li>
          </ul>
        </div>
      </el-card>
    </div>

    <!-- 个人预约未找到提示 -->
    <div v-if="notFound" class="not-found-card">
      <el-card shadow="never">
        <el-result
          icon="error"
          :title="$t('reservation.reservationNotFound')"
          :sub-title="$t('reservation.checkCodeAndContact')"
        ></el-result>
      </el-card>
    </div>
  </div>
</template>

<script>
import { reservationApi, recurringReservationApi } from '@/api'
import { isReservationExpired } from '@/utils/date'

export default {
  name: 'ReservationQuery',

  data() {
    return {
      // 个人预约管理相关
      personalLoading: false,
      showInstructions: true,
      notFound: false,
      personalQueryForm: {
        reservationCode: '',
        userContact: ''
      },
      personalQueryResults: [], // 新增：存放多条预约结果

      personalQueryRules: {
        reservationCode: [
          { required: false, message: this.$t('reservation.requiredField'), trigger: 'blur' },
          { min: 6, max: 20, message: this.$t('common.lengthLimit', { min: 6, max: 20 }), trigger: 'blur' }
        ],
        userContact: [
          { required: false, message: this.$t('reservation.requiredField'), trigger: 'blur' }
        ]
      }
    }
  },

  created() {
    // 如果URL中有预定码参数，自动填充
    const code = this.$route.query.code
    const userContact = this.$route.query.userContact

    if (code) {
      this.personalQueryForm.reservationCode = code
      // 自动查询
      this.$nextTick(() => {
        this.handlePersonalQuery()
      })
    } else if (userContact) {
      this.personalQueryForm.userContact = userContact
      // 自动查询
      this.$nextTick(() => {
        this.handlePersonalQuery()
      })
    }
  },

  methods: {

    // 处理个人预约查询
    handlePersonalQuery() {
      // 自定义验证：预定码和联系方式至少填写一项
      if (!this.personalQueryForm.reservationCode && !this.personalQueryForm.userContact) {
        this.$message.error(this.$t('reservation.atLeastOneField'))
        return false
      }

      this.$refs.personalQueryForm.validate(async (valid) => {
        if (!valid) {
          return false
        }

        this.personalLoading = true
        this.showInstructions = false
        this.notFound = false

        try {
          // 如果有预定码，优先使用预定码查询
          if (this.personalQueryForm.reservationCode) {
            try {
              // 先查普通预约
              const response = await reservationApi.getReservationByCode(this.personalQueryForm.reservationCode)
              if (response.data.success) {
                // 普通预约，导航到预定详情页
                console.log('找到普通预约，跳转到预约详情页:', this.personalQueryForm.reservationCode)
                this.$router.push({
                  path: `/reservation/${this.personalQueryForm.reservationCode}`,
                  query: {
                    code: this.personalQueryForm.reservationCode,
                    from: 'query'
                  }
                })
                return
              } else {
                // 检查是否是循环预约
                if (response.data.data && response.data.data.is_recurring === true && response.data.data.recurring_id) {
                  // 这是一个循环预约，跳转到循环预约详情页
                  console.log('检测到循环预约标记，跳转到循环预约详情页:', response.data.data.recurring_id)
                  this.$router.push({
                    path: `/recurring-reservation/${response.data.data.recurring_id}`,
                    query: {
                      code: this.personalQueryForm.reservationCode,
                      from: 'query'
                    }
                  })
                  return
                }

                // 如果普通预约查不到，再查循环预约
                try {
                  const recurringResponse = await recurringReservationApi.getRecurringReservationByCode(this.personalQueryForm.reservationCode)
                  if (recurringResponse.data.success) {
                    // 导航到循环预约详情页
                    console.log('找到循环预约，跳转到循环预约详情页:', recurringResponse.data.data.id)
                    this.$router.push({
                      path: `/recurring-reservation/${recurringResponse.data.data.id}`,
                      query: {
                        code: this.personalQueryForm.reservationCode,
                        from: 'query'
                      }
                    })
                    return
                  }
                } catch (recurringError) {
                  console.error('Failed to query by reservation code (recurring):', recurringError)
                }
              }
            } catch (error) {
              // 检查错误是否包含循环预约信息
              if (error.response && error.response.data && error.response.data.is_recurring === true && error.response.data.recurring_id) {
                // 这是一个循环预约，跳转到循环预约详情页
                console.log('错误响应中检测到循环预约标记，跳转到循环预约详情页:', error.response.data.recurring_id)
                this.$router.push({
                  path: `/recurring-reservation/${error.response.data.recurring_id}`,
                  query: {
                    code: this.personalQueryForm.reservationCode,
                    from: 'query'
                  }
                })
                return
              }

              // 普通预约接口报错时也查循环预约
              try {
                const recurringResponse = await recurringReservationApi.getRecurringReservationByCode(this.personalQueryForm.reservationCode)
                if (recurringResponse.data.success) {
                  // 导航到循环预约详情页
                  console.log('找到循环预约，跳转到循环预约详情页:', recurringResponse.data.data.id)
                  this.$router.push({
                    path: `/recurring-reservation/${recurringResponse.data.data.id}`,
                    query: {
                      code: this.personalQueryForm.reservationCode,
                      from: 'query'
                    }
                  })
                  return
                }
              } catch (recurringError) {
                console.error('Failed to query by reservation code (recurring):', recurringError)
              }
            }
          }

          // 如果没有预定码或预定码查询失败，尝试使用联系方式查询
          if (this.personalQueryForm.userContact) {
            try {
              // 这里需要调用后端接口根据联系方式查询预定
              const response = await reservationApi.getReservations({
                user_contact: this.personalQueryForm.userContact,
                limit: 50 // 查多一点
              })

              if (response.data.items && response.data.items.length > 0) {
                if (response.data.items.length === 1) {
                  // 只有一条，直接跳转
                  const firstReservation = response.data.items[0]
                  this.$router.push({
                    path: `/reservation/${firstReservation.reservation_code}`,
                    query: {
                      userContact: this.personalQueryForm.userContact,
                      from: 'query'
                    }
                  })
                  return
                } else {
                  // 多条，展示表格
                  this.personalQueryResults = response.data.items
                  return
                }
              }
            } catch (contactError) {
              console.error('Failed to query by contact:', contactError)
            }
          }

          // 如果两种方式都查询失败，显示未找到
          this.notFound = true

        } catch (error) {
          console.error('Failed to query personal reservation:', error)
          this.notFound = true
        } finally {
          this.personalLoading = false
        }
      })
    },

    // 格式化日期时间
    formatDateTime(row, column, cellValue) {
      if (!cellValue) return ''

      const date = new Date(cellValue)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

    // 获取状态类型
    getStatusType(reservation) {
      // 统一小写处理，兼容后端大小写不一致
      const status = (reservation.status || '').toLowerCase()
      console.log('status for switch:', reservation.status, '->', status)
      switch (status) {
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
      // 统一小写处理，兼容后端大小写不一致
      const status = (reservation.status || '').toLowerCase()
      console.log('status for switch:', reservation.status, '->', status)
      switch (status) {
        case 'cancelled':
          return this.$t('reservation.cancelled'); // 已取消
        case 'expired':
          return this.$t('reservation.expired');   // 已过期
        case 'in_use':
          return this.$t('reservation.inUse');     // 使用中
        case 'confirmed':
          return this.$t('reservation.confirmed'); // 已确认
        default:
          return reservation.status; // 其他状态直接显示
      }
    },

    // 重置表单
    resetForm() {
      this.$refs.personalQueryForm.resetFields()
      this.notFound = false
      this.showInstructions = true
      this.personalQueryResults = [] // 重置结果
    },

    // 查看预约详情
    async viewReservationDetail(reservation) {
      console.log('查看预约详情:', reservation);

      try {
        // 检查是否有预约序号，如果有，说明是子预约，直接跳转到子预约详情页面
        if (reservation.reservation_number) {
          console.log('检测到预约序号，直接跳转到子预约详情页面:', reservation.reservation_number);

          // 构建查询参数
          const query = {
            userContact: this.personalQueryForm.userContact,
            from: 'query'
          };

          // 如果有循环预约ID，添加到查询参数中
          if (reservation.recurring_reservation_id) {
            query.recurringId = reservation.recurring_reservation_id;
            query.child = 'true';
          }

          // 跳转到子预约详情页面
          this.$router.push({
            path: `/reservation/number/${reservation.reservation_number}`,
            query: query
          });

          return;
        }

        // 如果没有预约序号，按原有逻辑处理
        // 先查询预约详情，检查是否是循环预约
        const response = await reservationApi.getReservationByCode(reservation.reservation_code);

        if (response.data.success) {
          // 普通预约，导航到预定详情页
          console.log('找到普通预约，跳转到预约详情页:', reservation.reservation_code);
          this.$router.push({
            path: `/reservation/${reservation.reservation_code}`,
            query: {
              userContact: this.personalQueryForm.userContact,
              from: 'query'
            }
          });
        } else {
          // 检查是否是循环预约
          if (response.data.data && response.data.data.is_recurring === true && response.data.data.recurring_id) {
            // 这是一个循环预约，跳转到循环预约详情页
            console.log('检测到循环预约标记，跳转到循环预约详情页:', response.data.data.recurring_id);
            this.$router.push({
              path: `/recurring-reservation/${response.data.data.recurring_id}`,
              query: {
                userContact: this.personalQueryForm.userContact,
                from: 'query'
              }
            });
          } else {
            // 如果普通预约查不到，再查循环预约
            try {
              const recurringResponse = await recurringReservationApi.getRecurringReservationByCode(reservation.reservation_code);
              if (recurringResponse.data.success) {
                // 导航到循环预约详情页
                console.log('找到循环预约，跳转到循环预约详情页:', recurringResponse.data.data.id);
                this.$router.push(`/recurring-reservation/${recurringResponse.data.data.id}`);
              } else {
                this.$message.error(this.$t('reservation.notFound'));
              }
            } catch (recurringError) {
              console.error('Failed to query by reservation code (recurring):', recurringError);
              this.$message.error(this.$t('reservation.notFound'));
            }
          }
        }
      } catch (error) {
        // 检查错误是否包含循环预约信息
        if (error.response && error.response.data && error.response.data.data &&
            error.response.data.data.is_recurring === true && error.response.data.data.recurring_id) {
          // 这是一个循环预约，跳转到循环预约详情页
          console.log('错误响应中检测到循环预约标记，跳转到循环预约详情页:', error.response.data.data.recurring_id);
          this.$router.push(`/recurring-reservation/${error.response.data.data.recurring_id}`);
        } else {
          console.error('查看预约详情失败:', error);
          this.$message.error(this.$t('common.error'));
        }
      }
    }
  }
}
</script>

<style scoped>
.reservation-query {
  max-width: 800px;
  margin: 0 auto;
}

.page-title {
  margin-bottom: 20px;
  font-size: 24px;
  color: #303133;
}

.query-card {
  margin-bottom: 20px;
}

.query-results,
.no-results-card,
.instructions-card,
.not-found-card {
  margin-top: 30px;
}

.result-card {
  margin-bottom: 20px;
}

.instructions-content {
  color: #606266;
}

.instructions-content p {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 15px;
  color: #606266;
  font-weight: 500;
}

.instructions-content ul {
  padding-left: 20px;
  margin-top: 15px;
}

.instructions-content li {
  margin-bottom: 15px;
  line-height: 1.6;
  color: #606266;
}

/* 表单提示样式 */
.form-tip {
  font-size: 13px;
  color: #909399;
  margin-bottom: 15px;
  line-height: 1.5;
  display: flex;
  align-items: flex-start;
}

.form-tip i {
  margin-right: 5px;
  margin-top: 3px;
  color: #409EFF;
}

/* 选项卡样式 */
.el-tabs__item {
  font-size: 16px;
  padding: 0 20px;
}

/* 表格样式 */
.el-table {
  margin-top: 10px;
}

/* 日期选择器样式 */
.el-date-editor--daterange {
  width: 100% !important;
}
</style>
