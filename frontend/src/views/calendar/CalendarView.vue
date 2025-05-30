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
              <el-button
                size="small"
                @click="changeView('dayGridMonth')"
                :type="calendarOptions.initialView === 'dayGridMonth' ? 'primary' : ''"
              >{{ $t('calendar.month') }}</el-button>
              <el-button
                size="small"
                @click="changeView('timeGridWeek')"
                :type="calendarOptions.initialView === 'timeGridWeek' ? 'primary' : ''"
              >{{ $t('calendar.week') }}</el-button>
              <el-button
                size="small"
                @click="changeView('timeGridDay')"
                :type="calendarOptions.initialView === 'timeGridDay' ? 'primary' : ''"
              >{{ $t('calendar.day') }}</el-button>
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

      <!-- 预约状态提示 -->
      <el-row :gutter="20" class="status-legend-row">
        <el-col :span="24">
          <div class="status-legend">
            <el-alert
              type="primary"
              :closable="false"

            >
              <div class="status-legend-content">
                <div class="status-colors">
                  <span class="status-item">
                    <span class="status-color confirmed-color"></span>
                    {{ $t('calendar.confirmedStatus') }}
                  </span>
                  <span class="status-item">
                    <span class="status-color inuse-color"></span>
                    {{ $t('calendar.inUseStatus') }}
                  </span>
                </div>
                <div class="cancel-tip-container">
                  <span class="status-item cancel-tip">
                    <i class="el-icon-info"></i>
                    {{ $t('calendar.cancelTip') }}
                  </span>
                </div>
                <div class="update-tip-container">
                  <span class="status-item update-tip">
                    <i class="el-icon-info"></i>
                    {{ $t('calendar.updateTip') }}
                  </span>
                </div>
              </div>
            </el-alert>
          </div>
        </el-col>
      </el-row>
    </div>

    <FullCalendar
      ref="fullCalendar"
      :options="calendarOptions"
    />

    <!-- 预约详情弹窗 -->
    <el-dialog
      :visible.sync="detailVisible"
      width="400px"
      :title="$t('calendar.reservationInfo')"
      :modal-append-to-body="false"
      :close-on-click-modal="true"
      class="calendar-detail-dialog"
    >
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
          <!-- 添加修改按钮，只在预约状态为 confirmed 且未开始时显示 -->
          <el-button
            v-if="selectedEvent.extendedProps.status === 'confirmed' && !isReservationStarted(selectedEvent)"
            type="primary"
            @click="showModifyDialog"
            style="margin-right: 10px;"
          >
            {{ $t('reservation.modifyReservation') }}
          </el-button>

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
      :modal-append-to-body="false"
      :close-on-click-modal="true"
      class="calendar-cancel-dialog"
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

    <!-- 修改预约对话框 -->
    <el-dialog
      :title="$t('reservation.modifyReservation')"
      :visible.sync="modifyDialogVisible"
      width="400px"
      :modal-append-to-body="false"
      :close-on-click-modal="true"
      class="calendar-modify-dialog"
    >
      <div class="cancel-content">
        <p>{{ $t('reservation.modifyReservation') }}</p>

        <el-form ref="modifyForm" :model="modifyForm" :rules="modifyRules" label-position="top">
          <el-form-item :label="$t('reservation.code')" prop="reservationCode">
            <el-input
              v-model="modifyForm.reservationCode"
              :placeholder="$t('reservation.queryPlaceholder')"
            ></el-input>
          </el-form-item>
        </el-form>
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="modifyDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="modifying" @click="confirmModifyDialog">{{ $t('common.confirm') }}</el-button>
      </span>
    </el-dialog>

    <!-- 修改预约表单对话框 -->
    <el-dialog
      :title="$t('reservation.modifyReservation')"
      :visible.sync="modifyFormDialogVisible"
      width="600px"
      :modal-append-to-body="false"
      :close-on-click-modal="true"
      class="calendar-modify-form-dialog"
    >
      <el-form
        ref="modifyFormRef"
        :model="modifyFormData"
        :rules="modifyFormRules"
        label-width="120px"
        v-loading="modifyFormSubmitting"
      >
        <!-- 开始时间 -->
        <el-form-item :label="$t('reservation.startTime')" prop="startDateTime">
          <el-date-picker
            v-model="modifyFormData.startDateTime"
            type="datetime"
            :placeholder="$t('reservation.selectStartTime')"
            style="width: 100%"
            :picker-options="dateTimePickerOptions"
            value-format="yyyy-MM-ddTHH:mm:ss"
            format="yyyy-MM-dd HH:mm:ss"
            @change="checkModifyTimeAvailability"
          ></el-date-picker>
        </el-form-item>

        <!-- 结束时间 -->
        <el-form-item :label="$t('reservation.endTime')" prop="endDateTime">
          <el-date-picker
            v-model="modifyFormData.endDateTime"
            type="datetime"
            :placeholder="$t('reservation.selectEndTime')"
            style="width: 100%"
            :picker-options="dateTimePickerOptions"
            value-format="yyyy-MM-ddTHH:mm:ss"
            format="yyyy-MM-dd HH:mm:ss"
            @change="checkModifyTimeAvailability"
          ></el-date-picker>
        </el-form-item>

        <!-- 时间冲突提示 -->
        <el-alert
          v-if="modifyTimeConflict"
          :title="modifyTimeConflictTitle"
          type="error"
          :closable="false"
          show-icon
          style="margin-bottom: 15px;"
        >
          <div v-if="modifyConflictingReservations && modifyConflictingReservations.length > 0">
            <p style="margin-bottom: 10px;">{{ $t('reservation.conflictWithFollowing') }}</p>
            <div v-for="conflict in modifyConflictingReservations" :key="conflict.id" style="margin-bottom: 8px; padding: 8px; background-color: #fef0f0; border-radius: 4px;">
              <div><strong>{{ $t('reservation.conflictTime') }}</strong>{{ conflict.start_datetime }} {{ $t('reservation.conflictTo') }} {{ conflict.end_datetime }}</div>
              <div><strong>{{ $t('reservation.conflictUser') }}</strong>{{ conflict.user_name }} ({{ conflict.user_department }})</div>
              <div v-if="conflict.user_email"><strong>{{ $t('reservation.conflictEmail') }}</strong>{{ conflict.user_email }}</div>
              <div v-if="conflict.user_phone"><strong>{{ $t('reservation.conflictPhone') }}</strong>{{ conflict.user_phone }}</div>
              <div v-if="conflict.purpose"><strong>{{ $t('reservation.conflictPurpose') }}</strong>{{ conflict.purpose }}</div>
            </div>
          </div>
          <template v-else-if="modifyConflictMessage">
            {{ modifyConflictMessage }}
          </template>
        </el-alert>

        <!-- 时间可用提示 -->
        <el-alert
          v-if="!modifyTimeConflict && modifyTimeAvailabilityChecked"
          :title="$t('reservation.timeSlotAvailable')"
          type="success"
          :closable="false"
          show-icon
          style="margin-bottom: 15px;"
        ></el-alert>

        <!-- 使用目的 -->
        <el-form-item :label="$t('reservation.purpose')" prop="purpose">
          <el-input
            v-model="modifyFormData.purpose"
            :placeholder="$t('reservation.purposePlaceholder')"
            type="textarea"
            :rows="3"
          ></el-input>
        </el-form-item>

        <!-- 用户邮箱 -->
        <el-form-item :label="$t('reservation.userEmail')" prop="userEmail">
          <el-input
            v-model="modifyFormData.userEmail"
            :placeholder="$t('reservation.emailPlaceholder')"
          ></el-input>
        </el-form-item>
      </el-form>

      <div slot="footer" class="dialog-footer">
        <el-button @click="modifyFormDialogVisible = false">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitModifyForm" :loading="modifyFormSubmitting" :disabled="modifyTimeConflict">
          {{ $t('common.confirm') }}
        </el-button>
      </div>
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

      // 修改预约相关
      modifyDialogVisible: false,
      modifying: false,
      modifyForm: {
        reservationCode: ''
      },
      modifyRules: {
        reservationCode: [
          { required: true, message: this.$t('reservation.codeOrContactRequired'), trigger: 'blur' }
        ]
      },

      // 修改预约表单相关
      modifyFormDialogVisible: false,
      modifyFormSubmitting: false,
      modifyTimeConflict: false,
      modifyConflictMessage: '',
      modifyConflictingReservations: [],
      modifyTimeAvailabilityChecked: false,
      modifyFormData: {
        startDateTime: '',
        endDateTime: '',
        purpose: '',
        userEmail: ''
      },
      modifyFormRules: {
        startDateTime: [
          { required: true, message: this.$t('reservation.startTimeRequired'), trigger: 'change' }
        ],
        endDateTime: [
          { required: true, message: this.$t('reservation.endTimeRequired'), trigger: 'change' }
        ],
        userEmail: [
          { required: true, message: this.$t('reservation.emailRequired'), trigger: 'blur' },
          { type: 'email', message: this.$t('reservation.emailFormat'), trigger: 'blur' }
        ]
      },
      dateTimePickerOptions: {
        disabledDate: (time) => {
          return time.getTime() < Date.now() - 8.64e7; // 8.64e7是一天的毫秒数
        }
      },

      // 设备筛选相关
      selectedEquipment: null,
      equipmentList: []
    };
  },

  computed: {
    // 修改时间冲突标题
    modifyTimeConflictTitle() {
      if (this.modifyConflictingReservations && this.modifyConflictingReservations.length > 0) {
        return this.$t('reservation.timeConflictWith', { count: this.modifyConflictingReservations.length })
      } else if (this.modifyConflictMessage) {
        return this.modifyConflictMessage
      } else {
        return this.$t('reservation.timeSlotOccupied')
      }
    }
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

      // 确保 extendedProps 中包含 reservationCode 和 reservationNumber
      if (info.event.extendedProps) {
        // 如果没有 reservationCode，尝试从其他属性中获取
        if (!info.event.extendedProps.reservationCode && info.event.extendedProps.reservation_code) {
          info.event.extendedProps.reservationCode = info.event.extendedProps.reservation_code;
        }

        // 如果没有 reservationNumber，尝试从其他属性中获取
        if (!info.event.extendedProps.reservationNumber && info.event.extendedProps.reservation_number) {
          info.event.extendedProps.reservationNumber = info.event.extendedProps.reservation_number;
        }
      }

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
        // 计算事件持续时间（分钟）
        const start = info.event.start;
        const end = info.event.end;
        const durationMs = end - start;
        const durationMinutes = Math.round(durationMs / (1000 * 60));

        // 清除默认内容
        const eventContent = info.el.querySelector('.fc-event-main');
        if (eventContent) {
          // 创建自定义内容
          const customContent = document.createElement('div');
          customContent.className = 'custom-event-content';

          // 根据预约时长决定显示内容
          if (durationMinutes <= 30) {
            // 短时间预约：只显示设备名称+时间（一排）
            const shortContent = document.createElement('div');
            shortContent.className = 'event-short-content';

            // 智能提取设备名称（优先显示中文，备选英文前两个单词）
            let deviceName;
            const title = info.event.title;

            // 检测是否包含中文字符
            const chineseRegex = /[\u4e00-\u9fa5]/;
            if (chineseRegex.test(title)) {
              // 如果包含中文，提取第一个中文词组
              const chineseMatch = title.match(/[\u4e00-\u9fa5]+/);
              deviceName = chineseMatch ? chineseMatch[0] : title.split(' ')[0];
            } else {
              // 如果不包含中文，使用英文逻辑（前两个单词）
              const titleParts = title.split(' ');
              if (titleParts.length >= 2) {
                deviceName = `${titleParts[0]} ${titleParts[1]}`;
              } else {
                deviceName = titleParts[0];
              }
            }

            // 格式化时间
            const startTime = start ? start.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', hour12: false}) : '';
            const endTime = end ? end.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', hour12: false}) : '';

            shortContent.textContent = `${deviceName} ${startTime}-${endTime}`;
            shortContent.style.fontWeight = 'bold';
            shortContent.style.fontSize = '0.9em';
            shortContent.style.textAlign = 'center';
            shortContent.style.lineHeight = '1.2';
            shortContent.style.color = '#000000';

            customContent.appendChild(shortContent);
          } else {
            // 长时间预约：保持原有的3排显示
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
            const startTime = start ? start.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', hour12: false}) : '';
            const endTime = end ? end.toLocaleTimeString('zh-CN', {hour: '2-digit', minute:'2-digit', hour12: false}) : '';
            time.textContent = `${startTime}-${endTime}`;
            customContent.appendChild(time);
          }

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
      // 更新当前视图类型
      this.calendarOptions.initialView = viewName;
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
      // 不进行时区转换（第三个参数设为false），避免时间多加8小时
      return formatDate(date, 'YYYY-MM-DD HH:mm', false);
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

    // 检查预约是否已开始
    isReservationStarted(event) {
      const now = new Date();
      const startTime = new Date(event.start);
      return startTime <= now;
    },

    // 显示修改对话框
    showModifyDialog() {
      this.modifyForm.reservationCode = '';
      this.modifyDialogVisible = true;
    },

    // 确认修改预约
    async confirmModifyDialog() {
      try {
        // 验证表单
        await this.$refs.modifyForm.validate();

        // 检查输入的预约码是否与当前预约码匹配
        if (this.modifyForm.reservationCode !== this.selectedEvent.extendedProps.reservationCode) {
          this.$message.error(this.$t('reservation.checkCodeAndContact'));
          return;
        }

        // 关闭验证对话框
        this.modifyDialogVisible = false;

        // 初始化修改表单数据
        let startDateTime, endDateTime;

        try {
          startDateTime = new Date(this.selectedEvent.start);
          endDateTime = new Date(this.selectedEvent.end);

          // 检查日期是否有效
          if (isNaN(startDateTime.getTime()) || isNaN(endDateTime.getTime())) {
            throw new Error('Invalid date');
          }
        } catch (e) {
          console.error('Error creating date objects:', e);
          // 使用当前时间作为默认值
          startDateTime = new Date();
          endDateTime = new Date();
          endDateTime.setHours(endDateTime.getHours() + 1); // 结束时间默认为当前时间加1小时
        }

        // 手动格式化日期时间，确保格式与el-date-picker的value-format属性匹配
        const formatDateTimeForPicker = (date) => {
          if (!date || isNaN(date.getTime())) return null;

          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');
          const hours = String(date.getHours()).padStart(2, '0');
          const minutes = String(date.getMinutes()).padStart(2, '0');
          const seconds = String(date.getSeconds()).padStart(2, '0');

          return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
        };

        this.modifyFormData = {
          startDateTime: formatDateTimeForPicker(startDateTime),
          endDateTime: formatDateTimeForPicker(endDateTime),
          purpose: this.selectedEvent.extendedProps.purpose || '',
          userEmail: this.selectedEvent.extendedProps.userEmail || ''
        };

        // 显示修改表单对话框
        this.modifyFormDialogVisible = true;
      } catch (error) {
        console.error('Failed to validate modification form:', error);
        this.$message.error(this.$t('error.serverError'));
      } finally {
        this.modifying = false;
      }
    },

    // 验证时间范围
    validateTimeRange() {
      const startTime = new Date(this.modifyFormData.startDateTime);
      const endTime = new Date(this.modifyFormData.endDateTime);

      if (startTime >= endTime) {
        this.$message.error(this.$t('reservation.invalidTime'));
        return false;
      }

      return true;
    },

    // 检查修改时间可用性
    async checkModifyTimeAvailability() {
      if (!this.modifyFormData.startDateTime || !this.modifyFormData.endDateTime) {
        this.modifyTimeAvailabilityChecked = false
        return
      }

      // 添加更严格的验证
      if (this.modifyFormData.startDateTime >= this.modifyFormData.endDateTime) {
        this.modifyTimeConflict = true
        this.modifyTimeAvailabilityChecked = false
        return
      }

      try {
        const equipmentId = this.selectedEvent.extendedProps.equipmentId
        const startDate = this.modifyFormData.startDateTime
        const endDate = this.modifyFormData.endDateTime

        // 调用API检查时间可用性，排除当前预定
        const excludeId = this.selectedEvent.id  // 使用事件的id字段，而不是extendedProps.reservationId
        const params = {
          start_date: startDate,
          end_date: endDate
        }

        // 只有当excludeId存在且不为null/undefined时才添加参数
        if (excludeId != null && excludeId !== undefined) {
          params.exclude_reservation_id = excludeId
        }



        const response = await this.$http.get(`/api/equipment/${equipmentId}/availability`, { params })

        // 检查是否有冲突 - 处理API响应格式
        if (response.data.specific_time_check) {
          // 如果是具体时间段检查
          console.log('具体时间段检查结果:', response.data.available)
          this.modifyTimeConflict = response.data.available.includes(false)
        } else {
          // 如果是按日期检查
          console.log('按日期检查结果:', response.data.available)
          this.modifyTimeConflict = response.data.available.includes(false)
        }

        // 设置冲突信息
        if (this.modifyTimeConflict) {
          console.log('检测到时间冲突:', response.data.available)

          // 获取冲突的预定信息
          this.modifyConflictingReservations = response.data.conflicting_reservations || []

          // 检查是否是因为达到最大同时预定数量
          if (response.data.allow_simultaneous && response.data.max_simultaneous > 1) {
            this.modifyConflictMessage = this.$t('reservation.maxSimultaneousReached', { count: response.data.max_simultaneous });
          } else {
            this.modifyConflictMessage = '';
          }
        } else {
          console.log('时间段可用')
          this.modifyConflictMessage = '';
          this.modifyConflictingReservations = [];
        }

        this.modifyTimeAvailabilityChecked = true
      } catch (error) {
        console.error('Failed to check availability:', error)
        this.modifyTimeConflict = true
        this.modifyTimeAvailabilityChecked = false
        this.modifyConflictingReservations = []
        this.$message.error(this.$t('common.error'))
      }
    },

    // 提交修改表单
    async submitModifyForm() {
      try {
        // 验证表单
        await this.$refs.modifyFormRef.validate();

        // 验证时间范围
        if (!this.validateTimeRange()) return;

        // 检查时间冲突
        if (this.modifyTimeConflict) {
          this.$message.error(this.$t('reservation.timeConflict'))
          return
        }

        this.modifyFormSubmitting = true;

        // 构建更新数据
        const updateData = {
          start_datetime: this.modifyFormData.startDateTime,
          end_datetime: this.modifyFormData.endDateTime,
          purpose: this.modifyFormData.purpose || undefined,
          user_email: this.modifyFormData.userEmail || undefined,
          lang: this.$i18n.locale
        };

        // 调用更新API - 传递预约序号以确保修改正确的子预约
        const response = await reservationApi.updateReservation(
          this.selectedEvent.extendedProps.reservationCode,
          updateData,
          this.selectedEvent.extendedProps.reservationNumber  // 传递预约序号
        );

        if (response.data && response.data.success) {
          this.$message.success(this.$t('reservation.updateSuccess'));
          this.modifyFormDialogVisible = false;

          // 关闭预约详情弹窗
          this.detailVisible = false;

          // 重新加载日历事件
          this.loadEvents();
        } else {
          const errorMessage = response.data && response.data.message ? response.data.message : this.$t('reservation.updateFailed');
          this.$message.error(errorMessage);
        }
      } catch (error) {
        console.error('Failed to update reservation:', error);
        this.$message.error(this.$t('error.serverError'));
      } finally {
        this.modifyFormSubmitting = false;
      }
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

.status-legend-row {
  margin-top: 10px;
  margin-bottom: 15px;
}

.status-legend {
  width: 100%;
}

.status-legend-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.status-colors {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.status-color {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  margin-right: 5px;
}

.confirmed-color {
  background-color: rgba(103, 194, 58, 0.7);
  border: 1px solid rgba(103, 194, 58, 0.9);
}

.inuse-color {
  background-color: rgba(64, 158, 255, 0.7);
  border: 1px solid rgba(64, 158, 255, 0.9);
}

.cancel-tip-container {
  margin-top: 5px;
}

.cancel-tip {
  font-weight: bold;
}

.cancel-tip i {
  margin-right: 5px;
  color: #ff4040;
}


.update-tip-container {
  margin-top: 5px;
}

.update-tip {
  font-weight: bold;
}

.update-tip i {
  margin-right: 5px;
  color: #40a9ff;
}

/* 移动端适配 */
@media screen and (max-width: 768px) {
  .calendar-view {
    padding: 10px;
  }

  .calendar-header {
    margin-bottom: 15px;
  }

  /* 日历头部布局调整 */
  .calendar-header .el-row {
    flex-direction: column;
    gap: 15px;
  }

  .calendar-header .el-col {
    width: 100% !important;
    max-width: 100% !important;
    flex: none !important;
  }

  /* 标题区域 */
  .calendar-header .el-col:first-child {
    text-align: center;
  }

  .calendar-header h1 {
    font-size: 1.5rem;
    margin-bottom: 5px;
  }

  .calendar-current-date {
    font-size: 1rem;
    margin-top: 0;
  }

  /* 控制按钮区域 */
  .calendar-controls {
    justify-content: center;
    flex-wrap: wrap;
    gap: 8px;
  }

  .calendar-controls .el-button-group {
    margin-bottom: 8px;
  }

  .calendar-controls .el-button {
    font-size: 12px;
    padding: 6px 12px;
  }

  /* 设备筛选器 */
  .equipment-filter .el-select {
    width: 100% !important;
    max-width: 300px;
  }

  /* 状态图例 */
  .status-colors {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .status-legend-content {
    gap: 8px;
  }

  .status-item {
    font-size: 13px;
  }

  /* FullCalendar 移动端优化 */
  /* 日历头部星期几显示优化 */
  :deep(.fc-col-header-cell) {
    padding: 4px 2px !important;
    font-size: 12px !important;
  }

  :deep(.fc-col-header-cell-cushion) {
    padding: 2px !important;
    font-size: 12px !important;
    line-height: 1.2 !important;
    word-break: break-word !important;
    white-space: normal !important;
    text-align: center !important;
  }

  /* 月视图中的星期几文字换行 */
  :deep(.fc-daygrid-header .fc-col-header-cell-cushion) {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    hyphens: auto !important;
    max-width: 100% !important;
    display: block !important;
    height: auto !important;
    min-height: 30px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
  }

  /* 周视图和日视图的头部优化 */
  :deep(.fc-timegrid-header .fc-col-header-cell-cushion) {
    font-size: 11px !important;
    line-height: 1.1 !important;
    padding: 2px 1px !important;
    white-space: normal !important;
    word-break: break-word !important;
  }

  /* 日期数字样式 */
  :deep(.fc-daygrid-day-number) {
    font-size: 14px !important;
    padding: 2px !important;
  }

  /* 时间轴标签 */
  :deep(.fc-timegrid-slot-label) {
    font-size: 11px !important;
    padding: 2px !important;
  }

  /* 事件文字大小调整 */
  :deep(.fc-event-title) {
    font-size: 11px !important;
    line-height: 1.2 !important;
  }

  :deep(.fc-event-time) {
    font-size: 10px !important;
  }

  /* 月视图事件优化 */
  :deep(.fc-daygrid-event) {
    font-size: 11px !important;
    padding: 1px 2px !important;
    margin: 1px 0 !important;
  }

  /* 时间网格事件优化 */
  :deep(.fc-timegrid-event) {
    font-size: 10px !important;
    min-height: 20px !important;
  }

  /* 今天按钮和导航按钮 */
  :deep(.fc-button) {
    font-size: 12px !important;
    padding: 4px 8px !important;
  }

  /* 特别针对英文星期几名称的换行处理 */
  :deep(.fc-col-header-cell-cushion) {
    /* 强制英文单词换行 */
    word-break: break-all !important;
    overflow-wrap: anywhere !important;
    /* 设置最小高度确保有足够空间显示换行文字 */
    min-height: 35px !important;
    /* 使用flex布局居中显示 */
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    /* 允许多行显示 */
    white-space: normal !important;
    line-height: 1.1 !important;
  }

  /* 日历表格头部行高调整 */
  :deep(.fc-col-header) {
    height: auto !important;
    min-height: 40px !important;
  }

  :deep(.fc-col-header-row) {
    height: auto !important;
    min-height: 40px !important;
  }

  /* 确保日历头部有足够的空间 */
  :deep(.fc-daygrid-header) {
    margin-bottom: 5px !important;
  }

  /* 月视图日期格子高度调整 */
  :deep(.fc-daygrid-day) {
    min-height: 80px !important;
  }

  /* 周视图和日视图的列头部高度 */
  :deep(.fc-timegrid-header .fc-col-header-cell) {
    height: auto !important;
    min-height: 40px !important;
  }

  /* 移动端周末字体颜色强制设置为红色 */
  /* 周末表头文字颜色 - 红色 */
  :deep(.fc-col-header-cell.fc-day-sat),
  :deep(.fc-col-header-cell.fc-day-sun) {
    color: #ff0000 !important;
  }

  :deep(.fc-col-header-cell.fc-day-sat .fc-col-header-cell-cushion),
  :deep(.fc-col-header-cell.fc-day-sun .fc-col-header-cell-cushion) {
    color: #ff0000 !important;
  }

  /* 月视图中周末日期数字颜色 - 红色 */
  :deep(.fc-daygrid-day.fc-day-sat .fc-daygrid-day-number),
  :deep(.fc-daygrid-day.fc-day-sun .fc-daygrid-day-number) {
    color: #ff0000 !important;
  }

  /* 周视图和日视图中周末列头文字样式 - 红色 */
  :deep(.fc-timeGridWeek-view .fc-col-header-cell.fc-day-sat .fc-col-header-cell-cushion),
  :deep(.fc-timeGridWeek-view .fc-col-header-cell.fc-day-sun .fc-col-header-cell-cushion),
  :deep(.fc-timeGridDay-view .fc-col-header-cell.fc-day-sat .fc-col-header-cell-cushion),
  :deep(.fc-timeGridDay-view .fc-col-header-cell.fc-day-sun .fc-col-header-cell-cushion) {
    color: #ff0000 !important;
  }

  /* 确保周末的所有文字都是红色，包括换行后的文字 */
  :deep(.fc-day-sat .fc-col-header-cell-cushion),
  :deep(.fc-day-sun .fc-col-header-cell-cushion),
  :deep(.fc-day-sat),
  :deep(.fc-day-sun) {
    color: #ff0000 !important;
  }
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

/* 修复日视图右侧的多余空白 */
:deep(.fc-timegrid-slots table),
:deep(.fc-timegrid-cols table) {
  width: 100% !important;
}

/* 让日视图列容器更好地利用可用空间 */
:deep(.fc-timegrid-col.fc-day) {
  padding-right: 0 !important; /* 移除右侧内边距 */
  max-width: none !important; /* 移除最大宽度限制 */
}

/* 修复日视图整体容器宽度 */
:deep(.fc-timegrid-body) {
  width: 100% !important;
}

/* 移除日视图主体右侧的内边距/外边距 */
:deep(.fc-timegrid-body .fc-scroller-liquid-absolute) {
  right: 0 !important;
}

/* 预约块布局优化 */
:deep(.fc-timegrid-event-harness) {
  /* 保持原有的自适应宽度，但移除过多的边距 */
  margin: 1px !important;
}

/* 确保同时间段的预约能合理并排 */
:deep(.fc-timegrid-col-events) {
  /* 仅调整右边距，不影响自适应布局 */
  margin-right: 0 !important;
  right: 0 !important;
}

/* 短时间预约样式 */
:deep(.event-short-content) {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  height: 100% !important;
  padding: 2px 4px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  color: #000000 !important;
}

/* 确保短时间预约的容器样式 */
:deep(.custom-event-content .event-short-content) {
  width: 100% !important;
  min-height: 20px !important;
}

/* 移动端弹窗优化 */
@media (max-width: 768px) {
  /* 预约详情弹窗移动端优化 */
  :deep(.calendar-detail-dialog .el-dialog) {
    width: 85% !important;
    margin: 0 auto !important;
    top: 5vh !important;
  }

  :deep(.calendar-detail-dialog .el-dialog__body) {
    padding: 15px !important;
    max-height: 70vh;
    overflow-y: auto;
  }

  /* 取消预约弹窗移动端优化 */
  :deep(.calendar-cancel-dialog .el-dialog) {
    width: 80% !important;
    margin: 0 auto !important;
    top: 10vh !important;
  }

  :deep(.calendar-cancel-dialog .el-dialog__body) {
    padding: 15px !important;
  }

  /* 修改预约弹窗移动端优化 */
  :deep(.calendar-modify-dialog .el-dialog) {
    width: 80% !important;
    margin: 0 auto !important;
    top: 10vh !important;
  }

  :deep(.calendar-modify-dialog .el-dialog__body) {
    padding: 15px !important;
  }

  /* 修改预约表单弹窗移动端优化 */
  :deep(.calendar-modify-form-dialog .el-dialog) {
    width: 95% !important;
    margin: 0 auto !important;
    top: 5vh !important;
  }

  :deep(.calendar-modify-form-dialog .el-dialog__body) {
    padding: 15px !important;
    max-height: 70vh;
    overflow-y: auto;
  }

  /* 移动端遮罩层优化 - 确保遮罩层不会阻挡弹窗交互 */
  :deep(.v-modal) {
    background-color: rgba(0, 0, 0, 0.3) !important; /* 降低遮罩层透明度 */
    pointer-events: none !important; /* 让遮罩层不阻挡点击事件 */
  }

  /* 确保弹窗本身可以接收点击事件 */
  :deep(.el-dialog__wrapper) {
    pointer-events: auto !important;
  }

  :deep(.el-dialog) {
    pointer-events: auto !important;
  }

  /* 弹窗按钮在移动端的优化 */
  :deep(.action-buttons) {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  :deep(.action-buttons .el-button) {
    width: 100% !important;
    margin: 0 !important;
  }

  :deep(.dialog-footer .el-button) {
    width: 48% !important;
    margin: 0 1% !important;
  }
}

</style>

