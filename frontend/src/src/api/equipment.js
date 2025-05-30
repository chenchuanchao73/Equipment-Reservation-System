import axios from 'axios'

/**
 * 设备API
 */
export default {
  // 获取设备列表
  getEquipments(params) {
    return axios.get('/api/equipment', { params })
  },

  // 获取设备详情
  getEquipment(id) {
    return axios.get(`/api/equipment/${id}`)
  },

  // 获取设备类别
  getCategories() {
    return axios.get('/api/equipment/categories')
  },

  // 获取设备可用性
  getAvailability(id, startDate, endDate) {
    return axios.get(`/api/equipment/${id}/availability`, {
      params: { start_date: startDate, end_date: endDate }
    })
  },

  // 创建设备（管理员）
  createEquipment(data) {
    return axios.post('/api/equipment', data)
  },

  // 更新设备（管理员）
  updateEquipment(id, data) {
    return axios.put(`/api/equipment/${id}`, data)
  },

  // 删除设备（管理员）
  deleteEquipment(id) {
    return axios.delete(`/api/equipment/${id}`)
  }
}
