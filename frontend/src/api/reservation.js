import axios from 'axios'

/**
 * 预定API
 */
export default {
  // 创建预定
  createReservation(data) {
    return axios.post('/api/reservation/', data)
  },

  // 获取预定列表（管理员）
  getReservations(params) {
    return axios.get('/api/reservation', { params })
  },

  // 获取预定详情
  getReservation(code) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()
    return axios.get(`/api/reservation/${code}`, { params: { _t: timestamp } })
  },

  // 通过预定码获取预定详情
  getReservationByCode(code, params = {}) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()

    // 处理预约序号参数，确保它是字符串格式
    if (params.reservation_number) {
      if (typeof params.reservation_number === 'object') {
        console.log('预约序号参数是对象类型，尝试提取预约序号:', params.reservation_number);
        if (params.reservation_number.reservation_number) {
          params.reservation_number = params.reservation_number.reservation_number;
          console.log(`从对象中提取预约序号: ${params.reservation_number}`);
        } else {
          console.warn('无法从对象中提取预约序号，尝试使用整个对象');
          try {
            // 尝试将对象转换为字符串
            params.reservation_number = JSON.stringify(params.reservation_number);
          } catch (e) {
            console.error('序列化对象失败:', e);
            delete params.reservation_number;
          }
        }
      } else {
        console.log(`预约序号参数是${typeof params.reservation_number}类型: ${params.reservation_number}`);
      }
    } else if (typeof params === 'string' || params.startsWith && params.startsWith('RN-')) {
      // 如果params本身是字符串或者以RN-开头，则将其作为预约序号
      console.log(`将参数作为预约序号处理: ${params}`);
      params = { reservation_number: params };
    } else if (typeof params === 'object' && params.reservation_number === undefined) {
      // 检查params是否可能是预约序号对象
      const keys = Object.keys(params);
      if (keys.length === 1 && keys[0] === 'reservation_number') {
        console.log(`从对象中提取预约序号: ${params.reservation_number}`);
      }
    }

    params = { ...params, _t: timestamp }

    // 构建API基础URL
    const url = `/api/reservation/code/${code}`

    // 记录API请求信息
    console.log(`API请求: ${url}`, '参数:', params);
    console.log('获取预约详情URL:', url);

    // 发送请求并记录响应
    return axios.get(url, { params })
      .then(response => {
        console.log(`API响应: ${url}`, response.data);

        // 调试状态信息
        if (response.data && response.data.success && response.data.data) {
          console.log(`预约状态: ${response.data.data.status}`);
        }

        return response;
      })
      .catch(error => {
        console.error(`API错误: ${url}`, error);
        throw error;
      });
  },

  // 更新预定
  updateReservation(code, data) {
    return axios.put(`/api/reservation/code/${code}`, data)
  },

  // 取消预定
  cancelReservation(code, data = {}) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()
    if (!data._t) {
      data._t = timestamp
    }

    // 确保reservation_number参数被正确传递
    if (data.reservation_number) {
      console.log('取消预约 - 预约序号:', data.reservation_number)
    } else {
      console.warn('取消预约 - 未提供预约序号，将取消所有具有相同预约码的预约')
    }

    console.log('取消预约请求参数:', data)
    console.log('取消预约请求URL:', `/api/reservation/cancel/code/${code}`)

    // 使用JSON格式发送请求
    return axios.post(`/api/reservation/cancel/code/${code}`, data)
  },


  // 获取设备在指定日期的可用性
  getEquipmentAvailability(equipmentId, params) {
    return axios.get(`/api/equipment/${equipmentId}/availability`, { params })
  },

  // 获取预定历史记录
  getReservationHistory(code, reservationNumber = null) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()
    let url = `/api/reservation/code/${code}/history?_t=${timestamp}`

    // 如果提供了预约序号，添加到URL中
    if (reservationNumber) {
      url += `&reservation_number=${encodeURIComponent(reservationNumber)}`
    }

    return axios.get(url)
  },

  // 导出预定数据
  exportReservations(exportData) {
    return axios.post('/api/reservation/export', exportData, {
      responseType: 'blob' // 重要：设置响应类型为blob以处理文件下载
    })
  }
}
