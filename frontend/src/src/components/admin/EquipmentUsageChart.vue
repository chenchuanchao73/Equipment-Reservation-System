<template>
  <div class="equipment-usage-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-actions">
        <el-radio-group v-model="timeRange" size="small" @change="handleTimeRangeChange">
          <el-radio-button label="week">{{ $t('admin.week') }}</el-radio-button>
          <el-radio-button label="month">{{ $t('admin.month') }}</el-radio-button>
          <el-radio-button label="year">{{ $t('admin.year') }}</el-radio-button>
        </el-radio-group>
      </div>
    </div>
    
    <div v-if="loading" class="chart-loading">
      <el-skeleton :rows="5" animated />
    </div>
    
    <div v-else-if="!chartData.labels.length" class="chart-empty">
      <el-empty :description="$t('common.noData')"></el-empty>
    </div>
    
    <div v-else ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必要的组件
echarts.use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  BarChart,
  LineChart,
  PieChart,
  CanvasRenderer
])

export default {
  name: 'EquipmentUsageChart',
  
  props: {
    title: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'bar', // bar, line, pie
      validator: value => ['bar', 'line', 'pie'].includes(value)
    },
    loading: {
      type: Boolean,
      default: false
    },
    chartData: {
      type: Object,
      default: () => ({
        labels: [],
        datasets: []
      })
    }
  },
  
  data() {
    return {
      chart: null,
      timeRange: 'week', // week, month, year
      chartOptions: {}
    }
  },
  
  watch: {
    chartData: {
      handler() {
        this.renderChart()
      },
      deep: true
    }
  },
  
  mounted() {
    this.initChart()
    
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', this.resizeChart)
  },
  
  beforeDestroy() {
    // 销毁图表实例
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
    
    // 移除事件监听
    window.removeEventListener('resize', this.resizeChart)
  },
  
  methods: {
    initChart() {
      // 初始化图表
      this.chart = echarts.init(this.$refs.chartContainer)
      this.renderChart()
    },
    
    renderChart() {
      if (!this.chart || !this.chartData.labels.length) return
      
      // 根据图表类型生成不同的配置
      switch (this.type) {
        case 'bar':
          this.renderBarChart()
          break
        case 'line':
          this.renderLineChart()
          break
        case 'pie':
          this.renderPieChart()
          break
        default:
          this.renderBarChart()
      }
      
      // 设置图表选项
      this.chart.setOption(this.chartOptions)
    },
    
    renderBarChart() {
      // 生成柱状图配置
      this.chartOptions = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: this.chartData.datasets.map(dataset => dataset.label)
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.chartData.labels
        },
        yAxis: {
          type: 'value'
        },
        series: this.chartData.datasets.map(dataset => ({
          name: dataset.label,
          type: 'bar',
          data: dataset.data,
          itemStyle: {
            color: dataset.backgroundColor
          }
        }))
      }
    },
    
    renderLineChart() {
      // 生成折线图配置
      this.chartOptions = {
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: this.chartData.datasets.map(dataset => dataset.label)
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.chartData.labels
        },
        yAxis: {
          type: 'value'
        },
        series: this.chartData.datasets.map(dataset => ({
          name: dataset.label,
          type: 'line',
          data: dataset.data,
          itemStyle: {
            color: dataset.borderColor
          },
          lineStyle: {
            color: dataset.borderColor
          },
          areaStyle: dataset.fill ? {
            color: dataset.backgroundColor
          } : null
        }))
      }
    },
    
    renderPieChart() {
      // 生成饼图配置
      this.chartOptions = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 10,
          data: this.chartData.labels
        },
        series: [
          {
            name: this.title,
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: this.chartData.labels.map((label, index) => ({
              value: this.chartData.datasets[0].data[index],
              name: label,
              itemStyle: {
                color: this.chartData.datasets[0].backgroundColor[index]
              }
            }))
          }
        ]
      }
    },
    
    resizeChart() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    
    handleTimeRangeChange() {
      // 触发时间范围变化事件
      this.$emit('time-range-change', this.timeRange)
    }
  }
}
</script>

<style scoped>
.equipment-usage-chart {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.chart-loading,
.chart-empty {
  width: 100%;
  height: 300px;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
