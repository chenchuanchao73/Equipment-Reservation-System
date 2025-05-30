/**
 * 日期工具函数
 */

/**
 * 格式化日期时间
 * @param {Date|string|number} date - 日期对象、日期字符串或时间戳
 * @param {string} format - 格式化模板，例如：'YYYY-MM-DD HH:mm:ss'
 * @returns {string} - 格式化后的日期字符串
 */
export function formatDateTime(date, format = 'YYYY-MM-DD HH:mm') {
  if (!date) return ''

  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

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
 * 检查预约是否已过期
 * @param {Date|string|number} endDateTime - 预约结束时间
 * @returns {boolean} - 是否已过期
 */
export function isReservationExpired(endDateTime) {
  const now = new Date()
  const end = new Date(endDateTime)

  if (isNaN(end.getTime())) {
    return false
  }

  return now > end
}

export default {
  formatDateTime,
  isReservationExpired
}
