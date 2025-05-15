<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <el-row type="flex" justify="space-between" align="middle">
        <el-col :span="8">
          <h1>{{ $t('calendar.title') }}</h1>
          <h2 class="calendar-current-date">{{ currentViewTitle }}</h2>
        </el-col>
        <el-col :span="16">
          <div class="calendar-controls">
            <el-button-group>
              <el-button size="small" @click="changeView('dayGridMonth')">{{ $t('calendar.month') }}</el-button>
              <el-button size="small" @click="changeView('timeGridWeek')">{{ $t('calendar.week') }}</el-button>
              <el-button size="small" @click="changeView('timeGridDay')">{{ $t('calendar.day') }}</el-button>
            </el-button-group>
            <el-button size="small" @click="today">{{ $t('calendar.today') }}</el-button>
            <el-button-group>
              <el-button size="small" icon="el-icon-arrow-left" @click="prev"></el-button>
              <el-button size="small" icon="el-icon-arrow-right" @click="next"></el-button>
            </el-button-group>
          </div>
        </el-col>
      </el-row>

      <!-- 设备筛选器 -->
      <el-row :gutter="20" class="filter-row">
        <el-col :span="24">
          <div class="equipment-filter">
            <el-select
              v-model="selectedEquipment"
              :placeholder="$t('calendar.selectEquipment')"
              clearable
              @change="handleEquipmentChange"
              style="width: 300px;"
            >
              <el-option
                v-for="item in equipmentList"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              ></el-option>
            </el-select>
          </div>
        </el-col>
      </el-row>
    </div>

    <FullCalendar
      ref="fullCalendar"
      :options="calendarOptions"
    />

    <!-- 预约详情弹窗 -->
    <el-dialog :visible.sync="detailVisible" width="400px" :title="$t('calendar.reservationInfo')">
      <div v-if="selectedEvent" class="event-detail-card">
        <div class="event-header" :class="'status-' + selectedEvent.extendedProps.status">
          <h3>{{ selectedEvent.title }}</h3>
          <el-tag size="small" :type="getStatusTagType(selectedEvent.extendedProps.status)">
            {{ getStatusText(selectedEvent.extendedProps.status) }}
          </el-tag>
        </div>

        <div class="event-info">
          <div class="info-item time-info">
            <i class="el-icon-time"></i>
            <span class="time-display">{{ formatDateTime(selectedEvent.start) }} - {{ formatDateTime(selectedEvent.end) }}</span>
          </div>

          <div class="info-item">
            <i class="el-icon-user"></i>
            <span>{{ selectedEvent.extendedProps.userName }} ({{ selectedEvent.extendedProps.userDepartment }})</span>
          </div>

          <div class="info-item" v-if="selectedEvent.extendedProps.userEmail">
            <i class="el-icon-message"></i>
            <span>{{ selectedEvent.extendedProps.userEmail }}</span>
          </div>
        </div>

        <!-- 循环预约提示 -->
        <div v-if="selectedEvent.extendedProps.isRecurring" class="recurring-notice">
          <el-alert
            :title="$t('reservation.partOfRecurringReservation')"
            type="info"
            :closable="false">
          </el-alert>
        </div>

        <!-- 取消预约/提前归还按钮 -->
        <div class="action-buttons">
          <el-button
            type="danger"
            @click="showCancelDialog"
          >
            {{ selectedEvent.extendedProps.status === 'in_use' ? $t('reservation.earlyReturn') : $t('reservation.cancelReservation') }}
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 取消预约/提前归还对话框 -->
    <el-dialog
      :title="selectedEvent && selectedEvent.extendedProps.status === 'in_use' ? $t('reservation.earlyReturn') : $t('reservation.cancelReservation')"
      :visible.sync="cancelDialogVisible"
      width="400px"
    >
      <div class="cancel-content">
        <p>{{ selectedEvent && selectedEvent.extendedProps.status === 'in_use' ? $t('reservation.confirmEarlyReturn') : $t('reservation.confirmCancel') }}</p>

        <el-form ref="cancelForm" :model="cancelForm" :rules="cancelRules" label-position="top">
          <el-form-item :label="$t('reservation.code')" prop="reservationCode">
            <el-input
              v-model="cancelForm.reservationCode"
              :placeholder="$t('reservation.queryPlaceholder')"
            ></el-input>
          </el-form-item>
        </el-form>
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="cancelDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="danger" :loading="cancelling" @click="cancelReservation">{{ $t('common.confirm') }}</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
// import { Calendar } from '@fullcalendar/core';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import FullCalendar from '@fullcalendar/vue';
import { formatDate } from '@/utils/date';
import reservationApi from '@/api/reservation';
import equipmentApi from '@/api/equipment';

export default {
  name: 'CalendarView',
  components: {
    FullCalendar
  },
  data() {
    return {
      calendarOptions: {
        plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
        initialView: 'dayGridMonth',
        headerToolbar: false, // 我们使用自定义的头部控件
        events: [], // 将通过API加载
        eventClick: this.handleEventClick,
        eventDidMount: this.handleEventDidMount,
        datesSet: this.handleDatesSet,
        locale: this.$i18n.locale === 'zh-CN' ? 'zh-cn' : 'en',
        firstDay: 1, // 周一作为一周的第一天
        allDaySlot: false, // 不显示"全天"选项
        slotMinTime: '00:00:00', // 从0点开始
        slotMaxTime: '24:00:00', // 到24点结束
        height: 'auto',
        nowIndicator: true, // 显示当前时间指示器
        slotLabelFormat: {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false // 使用24小时制
        },
        slotEventOverlap: false, // 禁止事件重叠
        eventTimeFormat: { // 统一时间格式
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        },
        titleFormat: { year: 'numeric', month: 'long' }, // 标题格式
        views: {
          dayGridMonth: {
            dayHeaderFormat: { weekday: 'long' }, // 月视图只显示星期几
            fixedWeekCount: false, // 根据当月天数动态调整行数
            showNonCurrentDates: false // 隐藏不属于当前月份的日期
          },
          timeGridWeek: {
            dayHeaderFormat: { weekday: 'long', month: 'numeric', day: 'numeric', omitCommas: true } // 周视图显示完整日期
          },
          timeGridDay: {
            dayHeaderFormat: { weekday: 'long', month: 'numeric', day: 'numeric', omitCommas: true }, // 日视图显示完整日期
            slotEventOverlap: false, // 日视图特别禁止事件重叠
            eventMaxStack: 4, // 最多显示4个事件，超过则显示"+更多"
            moreLinkClick: 'popover' // 点击"+更多"时显示弹窗
          }
        },
        locales: {
          'zh-cn': {
            week: {
              dow: 1, // 周一作为一周的第一天
              doy: 4  // 一年中第一周必须包含1月4日
            },
            buttonText: {
              today: '今天',
              month: '月',
              week: '周',
              day: '日'
            },
            weekText: '周',
            allDayText: '全天',
            moreLinkText: '更多',
            noEventsText: '没有事件'
          },
          'en': {
            week: {
              dow: 1, // 周一作为一周的第一天
              doy: 4  // 一年中第一周必须包含1月4日
            },
            buttonText: {
              today: 'Today',
              month: 'Month',
              week: 'Week',
              day: 'Day'
            },
            weekText: 'W',
            allDayText: 'All day',
            moreLinkText: 'more',
            noEventsText: 'No events'
          }
        }
      },
      detailVisible: false,
      selectedEvent: null,
      loading: false,
      currentViewTitle: '',
      cancelDialogVisible: false,
      cancelling: false,
      cancelForm: {
        reservationCode: ''
      },
      cancelRules: {
        reservationCode: [
          { required: true, message: this.$t('reservation.codeOrContactRequired'), trigger: 'blur' }
        ]
      },

      // 设备筛选相关
      selectedEquipment: null,
      equipmentList: []
    };
  },
  mounted() {
    this.loadEvents();
    this.loadEquipmentList();
  },

  beforeDestroy() {
    // 清除资源
  },
  watch: {
    // 监听语言变化
    '$i18n.locale': {
      handler(newLocale) {
        if (this.$refs.fullCalendar) {
          const calendarApi = this.$refs.fullCalendar.getApi();
          calendarApi.setOption('locale', newLocale === 'zh-CN' ? 'zh-cn' : 'en');
          this.currentViewTitle = calendarApi.view.title;
        }
      },
      immediate: true
    }
  },
  methods: {
    // 加载预约数据
    async loadEvents() {
      this.loading = true;
      try {
        const calendarApi = this.$refs.fullCalendar.getApi();
        const start = this.formatDate(calendarApi.view.activeStart);
        const end = this.formatDate(calendarApi.view.activeEnd);

        // 构建请求参数
        const params = {
          start_date: start,
          end_date: end
        };

        // 如果选择了设备，添加设备ID参数
        if (this.selectedEquipment) {
          params.equipment_id = this.selectedEquipment;
        }

        const response = await this.$http.get('/api/reservations/calendar', { params });

        if (response.data.success) {
          calendarApi.removeAllEvents();
          calendarApi.addEventSource(response.data.events);
        } else {
          this.$message.error(response.data.message || this.$t('calendar.loadFailed'));
        }
      } catch (error) {
        console.error('Failed to load calendar events:', error);
        this.$message.error(this.$t('calendar.loadFailed'));
      } finally {
        this.loading = false;
      }
    },

    // 加载设备列表
    async loadEquipmentList() {
      try {
        const response = await equipmentApi.getEquipments({ limit: 100 });
        if (response.data && response.data.items) {
          this.equipmentList = response.data.items;
        }
      } catch (error) {
        console.error('Failed to load equipment list:', error);
        this.$message.error(this.$t('error.serverError'));
      }
    },

    // 处理设备选择变化
    handleEquipmentChange() {
      this.loadEvents();
    },

    // 处理日期范围变化
    handleDatesSet() {
      // 更新当前视图标题
      const calendarApi = this.$refs.fullCalendar.getApi();
      this.currentViewTitle = calendarApi.view.title;

      // 加载事件数据
      this.loadEvents();
    },

    // 处理事件点击
    handleEventClick(info) {
      this.selectedEvent = info.event;
      this.detailVisible = true;
    },

    // 处理事件渲染
    handleEventDidMount(info) {
      // 获取事件状态
      const status = info.event.extendedProps.status;

      // 根据状态设置事件颜色（适用于所有视图）
      if (status) {
        if (status === 'confirmed') {
          info.el.style.backgroundColor = 'rgba(103, 194, 58, 0.7)'; // 已确认 - 半透明绿色
          info.el.style.borderColor = 'rgba(103, 194, 58, 0.9)';
        } else if (status === 'in_use') {
          info.el.style.backgroundColor = 'rgba(64, 158, 255, 0.7)'; // 使用中 - 半透明蓝色
          info.el.style.borderColor = 'rgba(64, 158, 255, 0.9)';
        }
      }

      // 添加鼠标悬停工具提示
      this.addEventTooltip(info);

      // 为循环预约添加标记 - 适用于所有视图
      if (info.event.extendedProps.isRecurring) {
        // 月视图的处理方式
        if (info.view.type === 'dayGridMonth') {
          const recurringIcon = document.createElement('span');
          recurringIcon.className = 'recurring-icon';
          recurringIcon.innerHTML = '<i class="el-icon-refresh-right"></i>';
          const titleEl = info.el.querySelector('.fc-event-title');
          if (titleEl) {
            titleEl.appendChild(recurringIcon);
          }
        }
        // 周视图和日视图的处理方式
        else if (info.view.type === 'timeGridWeek' || info.view.type === 'timeGridDay') {
          // 为事件添加循环图标标记
          const recurringIcon = document.createElement('span');
          recurringIcon.className = 'recurring-icon-timegrid';
          recurringIcon.innerHTML = '<i class="el-icon-refresh-right"></i>';

          // 添加到自定义内容中
          const eventContent = info.el.querySelector('.custom-event-content');
          if (eventContent) {
            eventContent.appendChild(recurringIcon);
          } else {
            // 如果还没有自定义内容，添加到事件主体
            const mainContent = info.el.querySelector('.fc-event-main');
            if (mainContent) {
              mainContent.appendChild(recurringIcon);
            }
          }
        }
      }

      // 在月视图中修改时间格式为24小时制
      if (info.view.type === 'dayGridMonth') {
        const timeEl = info.el.querySelector('.fc-event-time');
        if (timeEl && info.event.start) {
          // 使用24小时制格式化时间
          const formattedTime = info.event.start.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
          });
          timeEl.textContent = formattedTime;
        }
      }

      // 在周视图和日视图中自定义事件内容
      if (info.view.type === 'timeGridWeek' || info.view.type === 'timeGridDay') {
        // 清除默认内容
        const eventContent = info.el.querySelector('.fc-event-main');
        if (eventContent) {
          // 创建自定义内容
          const customContent = document.createElement('div');
          customContent.className = 'custom-event-content';

          // 设备名称
          const title = document.createElement('div');
          title.className = 'event-title';
          title.textContent = info.event.title;
          customContent.appendChild(title);

          // 使用人
          const user = document.createElement('div');
          user.className = 'event-user';
          user.textContent = info.event.extendedProps.userName || '';
          customContent.appendChild(user);

          // 时间
          const time = document.createElement('div');
          time.className = 'event-time';
          const startTime = info.event.start ? info.event.start.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', hour12: false}) : '';
          const endTime = info.event.end ? info.event.end.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', hour12: false}) : '';
          time.textContent = `${startTime}-${endTime}`;
          customContent.appendChild(time);

          // 替换内容
          eventContent.innerHTML = '';
          eventContent.appendChild(customContent);

          // 为循环预约添加图标
          if (info.event.extendedProps.isRecurring) {
            const recurringIcon = document.createElement('span');
            recurringIcon.className = 'recurring-icon-timegrid';
            recurringIcon.innerHTML = '<i class="el-icon-refresh-right"></i>';
            eventContent.appendChild(recurringIcon);
          }
        }
      }
    },

    // 切换视图
    changeView(viewName) {
      const calendarApi = this.$refs.fullCalendar.getApi();
      calendarApi.changeView(viewName);
    },

    // 跳转到今天
    today() {
      const calendarApi = this.$refs.fullCalendar.getApi();
      calendarApi.today();
    },

    // 上一个时间段
    prev() {
      const calendarApi = this.$refs.fullCalendar.getApi();
      calendarApi.prev();
    },

    // 下一个时间段
    next() {
      const calendarApi = this.$refs.fullCalendar.getApi();
      calendarApi.next();
    },

    // 获取状态标签类型
    getStatusTagType(status) {
      const statusMap = {
        'confirmed': 'success',
        'in_use': 'primary',
        'cancelled': 'info',
        'expired': 'danger'
      };
      return statusMap[status] || 'info';
    },

    // 格式化日期
    formatDate(date) {
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    },

    // 格式化日期时间
    formatDateTime(date) {
      return formatDate(date, 'YYYY-MM-DD HH:mm');
    },

    // 格式化短时间（只显示小时和分钟）
    formatShortTime(date) {
      if (!date) return '';
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    },

    // 获取状态文本
    getStatusText(status) {
      const statusMap = {
        'confirmed': this.$t('reservation.confirmed'),
        'in_use': this.$t('reservation.inUse'),
        'cancelled': this.$t('reservation.cancelled'),
        'expired': this.$t('reservation.expired')
      };
      return statusMap[status] || status;
    },

    // 添加事件工具提示
    addEventTooltip(info) {
      // 获取事件信息
      const event = info.event;
      const props = event.extendedProps;

      // 计算事件持续时间（分钟）
      const start = event.start;
      const end = event.end;
      const durationMs = end - start;
      const durationMinutes = Math.round(durationMs / (1000 * 60));

      // 获取当前视图类型
      const calendarApi = this.$refs.fullCalendar.getApi();
      const viewType = calendarApi.view.type;

      // 获取事件元素
      const titleEl = info.el.querySelector('.fc-event-title');
      const timeEl = info.el.querySelector('.fc-event-time');
      const mainEl = info.el.querySelector('.fc-event-main');

      // 根据视图类型处理事件显示
      if (viewType === 'dayGridMonth') {
        // 月视图：所有预约显示相同，显示设备名称+开始和结束时间
        if (titleEl) {
          // 提取完整设备名称（通常是前两个单词，如"M2F Mic"）
          const titleParts = event.title.split(' ');
          let deviceName = titleParts[0]; // 至少包含第一个单词

          // 如果第二个单词是"Mic"或其他设备类型标识，也包含它
          if (titleParts.length > 1 &&
              (titleParts[1] === 'Mic' ||
               titleParts[1] === 'Speaker' ||
               titleParts[1].startsWith('Speaker'))) {
            deviceName = `${titleParts[0]} ${titleParts[1]}`;
          }

          // 格式化时间
          const startTime = this.formatShortTime(start);
          const endTime = this.formatShortTime(end);

          // 设置标题为"设备名称 开始-结束"
          titleEl.textContent = `${deviceName}     ${startTime}-${endTime}`;

          // 完全移除时间元素，防止重复显示时间
          if (timeEl) {
            timeEl.remove(); // 彻底移除时间元素，而不仅仅是隐藏
          }
        }
      } else if (viewType === 'timeGridWeek' || viewType === 'timeGridDay') {
        // 周视图和日视图：短时间预约特殊处理
        if (durationMinutes <= 30) {
          // 添加短时间预约的类
          info.el.classList.add('very-short-duration-event');

          // 只显示设备名称
          if (titleEl) {
            const deviceName = event.title.split(' ')[0];
            titleEl.textContent = deviceName;
          }

          // 调整主容器样式
          if (mainEl) {
            mainEl.style.display = 'flex';
            mainEl.style.alignItems = 'center';
            mainEl.style.justifyContent = 'center';
            mainEl.style.padding = '2px';

            // 日视图和周视图的不同布局
            if (viewType === 'timeGridDay') {
              // 日视图：水平排列
              mainEl.style.flexDirection = 'row';
              if (timeEl) {
                timeEl.style.marginRight = '4px';
              }
            } else {
              // 周视图：垂直排列
              mainEl.style.flexDirection = 'column';
              if (timeEl) {
                timeEl.style.marginBottom = '2px';
              }
            }
          }

          // 调整字体样式
          if (titleEl) {
            titleEl.style.fontWeight = 'bold';
            titleEl.style.fontSize = '0.9em';
          }
          if (timeEl) {
            timeEl.style.fontWeight = 'bold';
            timeEl.style.fontSize = '0.9em';
          }
        }
      }

      // 设置title属性（原生浏览器工具提示）
      const tooltipText = `${event.title}\n${props.userName || ''}\n${this.formatDateTime(start)} - ${this.formatDateTime(end)}\n${this.getStatusText(props.status)}\n${props.reservationNumber}`;
      info.el.setAttribute('title', tooltipText);
    },

    // 显示取消预约对话框
    showCancelDialog() {
      this.cancelForm.reservationCode = '';
      this.cancelDialogVisible = true;
    },

    // 取消预约
    async cancelReservation() {
      try {
        // 验证表单
        await this.$refs.cancelForm.validate();

        // 检查输入的预约码是否与当前预约码匹配
        if (this.cancelForm.reservationCode !== this.selectedEvent.extendedProps.reservationCode) {
          this.$message.error(this.$t('reservation.checkCodeAndContact'));
          return;
        }

        this.cancelling = true;

        // 准备请求数据
        const data = {
          reservation_number: this.selectedEvent.extendedProps.reservationNumber || null,
          lang: this.$i18n.locale
        };

        // 调用取消预约API
        const response = await reservationApi.cancelReservation(this.selectedEvent.extendedProps.reservationCode, data);

        if (response.data.success) {
          this.$message.success(this.$t('reservation.cancelSuccess'));
          this.cancelDialogVisible = false;

          // 关闭预约详情弹窗
          this.detailVisible = false;

          // 重新加载日历事件
          this.loadEvents();
        } else {
          this.$message.error(response.data.message || this.$t('reservation.cancelFailed'));
        }
      } catch (error) {
        console.error('Failed to cancel reservation:', error);
        this.$message.error(this.$t('error.serverError'));
      } finally {
        this.cancelling = false;
      }
    }
  }
};
</script>

<style scoped>
.calendar-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.calendar-header {
  margin-bottom: 20px;
}

.calendar-current-date {
  font-size: 1.2rem;
  color: #606266;
  margin-top: 5px;
  font-weight: normal;
}

.calendar-controls {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.filter-row {
  margin-top: 15px;
}

.equipment-filter {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.recurring-notice {
  margin: 15px 0;
}

.action-buttons {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.cancel-content {
  padding: 10px 0;
}

.recurring-icon {
  margin-left: 5px;
  color: #ff9800;
}

/* 周视图和日视图中的循环预约图标 */
:deep(.recurring-icon-timegrid) {
  position: absolute;
  top: 2px;
  right: 2px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  z-index: 2;
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 50%;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none; /* 确保图标不会影响点击事件 */
}

/* 自定义事件样式 */
:deep(.fc-event) {
  cursor: pointer;
}

:deep(.fc-event-title) {
  font-weight: bold;
}

/* 隐藏月视图中的点 */
:deep(.fc-daygrid-event-dot) {
  display: none !important;
}

/* 月视图中的事件内容居中显示 */
:deep(.fc-daygrid-event) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  padding: 2px 4px !important;
  white-space: nowrap !important;
}

:deep(.fc-daygrid-event-harness) {
  margin-top: 2px !important;
}

:deep(.fc-daygrid-event .fc-event-main) {
  width: 100% !important;
  text-align: center !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

:deep(.fc-daygrid-event .fc-event-time) {
  font-weight: bold !important;
  margin-right: 4px !important;
  text-align: center !important;
  display: inline !important;
}

:deep(.fc-daygrid-event .fc-event-title) {
  display: inline !important;
  text-align: center !important;
}

/* 日期头部样式 */
:deep(.fc-col-header-cell) {
  background-color: #f5f7fa;
  padding: 8px 0;
}

:deep(.fc-col-header-cell-cushion) {
  font-weight: bold;
  color: #303133;
  text-decoration: none;
  padding: 4px;
}

/* 时间格子样式 */
:deep(.fc-timegrid-slot) {
  height: 40px;
}

/* 设置事件的最小高度 */
:deep(.fc-timegrid-event) {
  min-height: 40px !important; /* 确保短时间预约有足够的显示空间 */
}

/* 今天高亮 - 使用突出边框而非背景色 */
:deep(.fc-day-today) {
  background-color: transparent !important; /* 移除背景色 */
  position: relative !important;
}

/* 为月视图中的今天添加突出边框 */
:deep(.fc-daygrid-day.fc-day-today::after) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border: 1px solid #006eff !important; /* 红色细线边框 */
  pointer-events: none; /* 确保边框不会影响点击事件 */
  z-index: 1; /* 确保边框在内容之上 */
}

/* 月视图中今天的日期数字加粗显示 */
:deep(.fc-day-today .fc-daygrid-day-number) {
  font-weight: bold !important;
  color: #006eff !important; /* 红色文字 */
}

/* 周视图和日视图中今天的列头样式 */
:deep(.fc-timeGridWeek-view .fc-col-header-cell.fc-day-today),
:deep(.fc-timeGridDay-view .fc-col-header-cell.fc-day-today) {
  background-color: transparent !important;
}

/* 周视图和日视图中今天的列头文字样式 */
:deep(.fc-timeGridWeek-view .fc-col-header-cell.fc-day-today .fc-col-header-cell-cushion),
:deep(.fc-timeGridDay-view .fc-col-header-cell.fc-day-today .fc-col-header-cell-cushion) {
  font-weight: bold !important;
  color: #006eff !important; /* 红色文字 */
}

/* 周视图中今天的时间轴列样式 */
:deep(.fc-timeGridWeek-view .fc-timegrid-col.fc-day-today) {
  background-color: transparent !important;
  position: relative !important;
}

/* 为周视图中今天的时间轴添加红色细线边框 */
:deep(.fc-timeGridWeek-view .fc-timegrid-col.fc-day-today::after) {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-top: 1px solid #006eff !important;
  border-left: 1px solid #006eff !important;
  border-right: 1px solid #006eff !important;
  border-bottom: 1px solid #006eff !important;
  pointer-events: none;
  z-index: 1;
}

/* 日视图中今天的时间轴列样式 */
:deep(.fc-timeGridDay-view .fc-timegrid-col.fc-day-today) {
  background-color: transparent !important;
  /* 日视图不需要边框 */
}

/* 周末颜色 */
:deep(.fc-day-sat), :deep(.fc-day-sun) {
  background-color: #ffffff;
}

/* 周末表头文字颜色 - 红色 */
:deep(.fc-col-header-cell.fc-day-sat), :deep(.fc-col-header-cell.fc-day-sun) {
  color: #ff0000;
}

:deep(.fc-col-header-cell.fc-day-sat .fc-col-header-cell-cushion),
:deep(.fc-col-header-cell.fc-day-sun .fc-col-header-cell-cushion) {
  color: #ff0000;
}

/* 月视图中周末日期数字颜色 - 红色 */
:deep(.fc-daygrid-day.fc-day-sat .fc-daygrid-day-number),
:deep(.fc-daygrid-day.fc-day-sun .fc-daygrid-day-number) {
  color: #ff0000;
}

/* 工作日颜色 */
:deep(.fc-day-mon), :deep(.fc-day-tue), :deep(.fc-day-wed), :deep(.fc-day-thu), :deep(.fc-day-fri) {
  background-color: #ffffff;
}

/* 预约详情弹窗样式 */
.event-detail-card {
  border-radius: 4px;
  overflow: hidden;
}

.event-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.event-header h3 {
  margin: 0;
  font-size: 18px;
}

.status-confirmed {
  background-color: #f0f9eb;
  border-left: 4px solid #67c23a;
}

.status-in_use {
  background-color: #ecf5ff;
  border-left: 4px solid #409eff;
}

.status-cancelled {
  background-color: #f4f4f5;
  border-left: 4px solid #909399;
}

.status-expired {
  background-color: #fef0f0;
  border-left: 4px solid #f56c6c;
}

.event-info {
  padding: 0 15px 15px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.info-item i {
  margin-right: 10px;
  color: #909399;
}

.time-info {
  margin-bottom: 15px;
}

.time-display {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

/* 周视图和日视图中的事件内容样式 */
:deep(.custom-event-content) {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2px;
  text-align: center;
  overflow: hidden;
}

/* 当事件宽度较窄时的样式调整 */
:deep(.fc-timegrid-col-events .custom-event-content) {
  font-size: 0.9em;
  line-height: 1.1;
}

/* 修复日视图和周视图中事件宽度问题 - 允许并排显示 */
:deep(.fc-timegrid-event-harness) {
  /* 移除强制宽度，允许事件并排显示 */
  border-radius: 3px !important;
}

:deep(.fc-timegrid-event) {
  border-radius: 3px !important;
  margin: 1px !important;
  padding: 2px !important;
}

/* 确保事件内容在较窄的事件中也能正常显示 */
:deep(.fc-timegrid-event .fc-event-main) {
  padding: 2px !important;
}

:deep(.fc-timeGridDay-view .fc-timegrid-event) {
  /* 移除强制宽度，允许事件并排显示 */
  width: auto !important;
  max-width: none !important;
  margin: 1px 2px !important;
  border-radius: 3px !important;
  box-sizing: border-box !important;
}

/* 修复日视图中的列宽度 */
:deep(.fc-timeGridDay-view .fc-timegrid-col) {
  width: 100% !important;
  max-width: 100% !important;
}

:deep(.fc-timeGridDay-view .fc-timegrid-col-frame) {
  width: 100% !important;
  max-width: 100% !important;
}

/* 日视图中的事件容器 */
:deep(.fc-timeGridDay-view .fc-timegrid-col-events) {
  display: flex !important;
  flex-direction: column !important;
}

/* 日视图中的事件容器组 */
:deep(.fc-timeGridDay-view .fc-timegrid-event-harness-inset) {
  margin-left: 0 !important;
  margin-right: 0 !important;
  width: auto !important;
  flex: 1 !important;
}

/* 日视图中的事件 */
:deep(.fc-timeGridDay-view .fc-timegrid-event) {
  flex: 1 !important;
  min-width: 0 !important;
}

/* 日视图中的事件内容 */
:deep(.fc-timeGridDay-view .custom-event-content) {
  padding: 2px !important;
  font-size: 0.9em !important;
  line-height: 1.1 !important;
}

/* 日视图中的事件容器 */
:deep(.fc-timeGridDay-view .fc-timegrid-event-harness) {
  margin: 0 1px !important;
}

/* 日视图中的事件 */
:deep(.fc-timeGridDay-view .fc-timegrid-event) {
  margin: 1px !important;
  border-radius: 3px !important;
}

/* 日视图中的更多链接 */
:deep(.fc-timeGridDay-view .fc-daygrid-more-link) {
  font-size: 12px !important;
  font-weight: bold !important;
  color: #409eff !important;
  background-color: rgba(64, 158, 255, 0.1) !important;
  border-radius: 3px !important;
  padding: 2px 4px !important;
  margin: 1px !important;
  text-align: center !important;
}

/* 日视图中的弹出窗口 */
:deep(.fc-timeGridDay-view .fc-popover) {
  border-radius: 4px !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1) !important;
  border: 1px solid #ebeef5 !important;
}

/* 短时间预约的特殊样式（30分钟或更短） */
:deep(.very-short-duration-event) {
  min-height: 30px !important; /* 确保最小高度 */
  font-weight: bold !important; /* 加粗文字 */
  border-width: 2px !important; /* 加粗边框 */
  z-index: 6 !important; /* 更高层级 */
  overflow: visible !important; /* 允许内容溢出 */
  height: auto !important; /* 自动调整高度 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important; /* 添加阴影，增加立体感 */
}

/* 短时间预约的标题样式 */
:deep(.very-short-duration-event .fc-event-title) {
  font-size: 1em !important; /* 保持正常字体大小 */
  line-height: 1.2 !important; /* 减小行高 */
  padding: 2px !important; /* 减小内边距 */
  text-align: center !important; /* 文字居中 */
  white-space: nowrap !important; /* 不允许文字换行 */
  overflow: hidden !important; /* 隐藏溢出内容 */
  text-overflow: ellipsis !important; /* 显示省略号 */
  font-weight: bold !important; /* 加粗文字 */
  color: #000 !important; /* 黑色文字，增加可读性 */
}

/* 确保时间显示清晰 */
:deep(.very-short-duration-event .fc-event-time) {
  font-size: 1em !important; /* 保持正常字体大小 */
  font-weight: bold !important;
  padding: 2px !important;
  text-align: center !important;
  color: #000 !important; /* 黑色文字，增加可读性 */
}

/* 日视图中的短时间预约 */
:deep(.fc-timeGridDay-view .very-short-duration-event) {
  min-height: 30px !important; /* 固定最小高度 */
  margin-top: 2px !important;
  margin-bottom: 2px !important;
  height: 30px !important; /* 固定高度 */
  padding: 2px !important; /* 增加内边距 */
  border-width: 2px !important; /* 加粗边框 */
}

/* 日视图中的短时间预约内容 */
:deep(.fc-timeGridDay-view .very-short-duration-event .fc-event-main) {
  padding: 2px !important; /* 增加内边距 */
  display: flex !important;
  flex-direction: row !important; /* 水平排列 */
  justify-content: center !important;
  align-items: center !important;
  height: 100% !important;
}

/* 日视图中的短时间预约时间和标题 */
:deep(.fc-timeGridDay-view .very-short-duration-event .fc-event-time),
:deep(.fc-timeGridDay-view .very-short-duration-event .fc-event-title) {
  display: inline-block !important;
  padding: 0 3px !important; /* 增加内边距 */
  margin: 0 !important;
  line-height: 1.2 !important; /* 增加行高 */
  font-size: 1em !important; /* 增加字体大小 */
  font-weight: bold !important; /* 加粗文字 */
  text-shadow: 0px 0px 1px rgba(0, 0, 0, 0.5) !important; /* 添加文字阴影，增加可读性 */
}

/* 周视图中的短时间预约 */
:deep(.fc-timeGridWeek-view .very-short-duration-event) {
  min-height: 30px !important;
  margin-top: 1px !important;
  margin-bottom: 1px !important;
  height: 30px !important; /* 固定高度 */
}

/* 周视图中的短时间预约内容 */
:deep(.fc-timeGridWeek-view .very-short-duration-event .fc-event-main) {
  padding: 1px !important;
  display: flex !important;
  flex-direction: row !important; /* 水平排列 */
  justify-content: center !important;
  align-items: center !important;
  height: 100% !important;
}

/* 周视图中的短时间预约时间和标题 */
:deep(.fc-timeGridWeek-view .very-short-duration-event .fc-event-time),
:deep(.fc-timeGridWeek-view .very-short-duration-event .fc-event-title) {
  display: inline-block !important;
  padding: 0 2px !important;
  margin: 0 !important;
  line-height: 1.2 !important;
  font-size: 1em !important;
  font-weight: bold !important;
  color: #000 !important; /* 黑色文字，增加可读性 */
}

/* 月视图中的事件样式 */
:deep(.fc-daygrid-event) {
  padding: 2px 4px !important;
  margin: 1px 0 !important;
  border-radius: 3px !important;
}

:deep(.event-title) {
  font-weight: bold;
  margin-bottom: 2px;
  font-size: 12px;
  line-height: 1.1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  color: #000; /* 黑色标题 */
}

:deep(.event-user) {
  font-size: 11px;
  color: #333; /* 深灰色用户名 */
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

:deep(.event-time) {
  font-size: 11px;
  font-weight: bold;
  color: #333; /* 深灰色时间 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

/* 当事件宽度足够大时的样式 */
:deep(.fc-timegrid-event-harness-inset .event-title) {
  font-size: 14px;
  margin-bottom: 4px;
  color: #000; /* 黑色标题 */
}

:deep(.fc-timegrid-event-harness-inset .event-user) {
  font-size: 13px;
  margin-bottom: 4px;
  color: #333; /* 深灰色用户名 */
}

:deep(.fc-timegrid-event-harness-inset .event-time) {
  font-size: 13px;
  color: #333; /* 深灰色时间 */
}

/* 当前时间指示器样式 */
:deep(.fc-timegrid-now-indicator-line) {
  border-color: #ff0000; /* 红色线条 */
  border-width: 0.1px; /* 加粗线条 */
  z-index: 10; /* 确保在事件上方显示 */
}

:deep(.fc-timegrid-now-indicator-arrow) {
  border-color: #ff0000; /* 红色箭头 */
  border-width: 5px 0px 0 0; /* 加大箭头 */
}


</style>

