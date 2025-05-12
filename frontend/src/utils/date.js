/**
 * 日期处理工具函数
 */

/**
 * 将UTC时间转换为北京时间（UTC+8）
 * @param {Date|string|number} date - UTC日期对象、日期字符串或时间戳
 * @returns {Date} - 北京时间日期对象
 */
export function convertToBeijingTime(date) {
  if (!date) return null

  // 创建日期对象
  const utcDate = new Date(date)
  if (isNaN(utcDate.getTime())) return null

  // 获取UTC时间的时间戳
  const utcTimestamp = utcDate.getTime()

  // 添加8小时的毫秒数 (8 * 60 * 60 * 1000 = 28800000)
  const beijingTimestamp = utcTimestamp + 28800000

  // 创建北京时间的日期对象
  return new Date(beijingTimestamp)
}

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期对象、日期字符串或时间戳
 * @param {string} format - 格式化模板，例如：'YYYY-MM-DD HH:mm:ss'
 * @param {boolean} toBeijingTime - 是否转换为北京时间
 * @returns {string} - 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss', toBeijingTime = true) {
  if (!date) return ''

  // 创建日期对象
  let d = new Date(date)
  if (isNaN(d.getTime())) return ''

  // 转换为北京时间
  if (toBeijingTime) {
    d = convertToBeijingTime(d)
  }

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

/**
 * 获取日期范围
 * @param {Date|string|number} startDate - 开始日期
 * @param {Date|string|number} endDate - 结束日期
 * @returns {Array} - 日期范围数组
 */
export function getDateRange(startDate, endDate) {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const range = []

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return range
  }

  const current = new Date(start)
  while (current <= end) {
    range.push(new Date(current))
    current.setDate(current.getDate() + 1)
  }

  return range
}

/**
 * 检查日期是否在范围内
 * @param {Date|string|number} date - 要检查的日期
 * @param {Date|string|number} startDate - 开始日期
 * @param {Date|string|number} endDate - 结束日期
 * @returns {boolean} - 是否在范围内
 */
export function isDateInRange(date, startDate, endDate) {
  const d = new Date(date)
  const start = new Date(startDate)
  const end = new Date(endDate)

  if (isNaN(d.getTime()) || isNaN(start.getTime()) || isNaN(end.getTime())) {
    return false
  }

  return d >= start && d <= end
}

/**
 * 获取两个日期之间的天数
 * @param {Date|string|number} startDate - 开始日期
 * @param {Date|string|number} endDate - 结束日期
 * @returns {number} - 天数
 */
export function getDaysBetween(startDate, endDate) {
  const start = new Date(startDate)
  const end = new Date(endDate)

  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return 0
  }

  // 将日期设置为当天的0点，以便计算准确的天数
  start.setHours(0, 0, 0, 0)
  end.setHours(0, 0, 0, 0)

  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  return diffDays
}

/**
 * 获取当前日期的开始时间（0点0分0秒）
 * @param {Date|string|number} date - 日期
 * @returns {Date} - 日期的开始时间
 */
export function getStartOfDay(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

/**
 * 获取当前日期的结束时间（23点59分59秒）
 * @param {Date|string|number} date - 日期
 * @returns {Date} - 日期的结束时间
 */
export function getEndOfDay(date) {
  const d = new Date(date)
  d.setHours(23, 59, 59, 999)
  return d
}

/**
 * 检查两个时间段是否重叠
 * @param {Date|string|number} start1 - 第一个时间段的开始时间
 * @param {Date|string|number} end1 - 第一个时间段的结束时间
 * @param {Date|string|number} start2 - 第二个时间段的开始时间
 * @param {Date|string|number} end2 - 第二个时间段的结束时间
 * @returns {boolean} - 是否重叠
 */
export function isTimeOverlap(start1, end1, start2, end2) {
  const s1 = new Date(start1).getTime()
  const e1 = new Date(end1).getTime()
  const s2 = new Date(start2).getTime()
  const e2 = new Date(end2).getTime()

  return Math.max(s1, s2) < Math.min(e1, e2)
}

/**
 * 检查预约是否已过期
 * @param {Date|string|number} endDateTime - 预约结束时间
 * @returns {boolean} - 是否已过期
 */
export function isReservationExpired(endDateTime) {
  // 使用当前日期检查是否过期
  const now = new Date()
  const end = new Date(endDateTime)

  if (isNaN(end.getTime())) {
    return false
  }

  // 检查是否过期
  const isExpired = now > end
  return isExpired
}

export default {
  formatDate,
  convertToBeijingTime,
  getDateRange,
  isDateInRange,
  getDaysBetween,
  getStartOfDay,
  getEndOfDay,
  isTimeOverlap,
  isReservationExpired
}
