import axios from 'axios'

// Unsplash API
export const unsplashApi = {
  // 搜索图片
  searchPhotos(query, page = 1, perPage = 10) {
    return axios.get('/api/unsplash/search', {
      params: {
        query,
        page,
        per_page: perPage
      }
    })
  },

  // 获取随机图片
  getRandomPhoto(query) {
    return axios.get('/api/unsplash/random', {
      params: { query }
    })
  }
}

// 设备API
export const equipmentApi = {
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

// 设备类别API
export const categoryApi = {
  // 获取设备类别列表
  getCategories(params) {
    return axios.get('/api/equipment-categories', { params })
  },

  // 获取所有设备类别
  getAllCategories() {
    return axios.get('/api/equipment-categories/all')
  },

  // 获取设备类别详情
  getCategory(id) {
    return axios.get(`/api/equipment-categories/${id}`)
  },

  // 创建设备类别（管理员）
  createCategory(data) {
    return axios.post('/api/equipment-categories', data)
  },

  // 更新设备类别（管理员）
  updateCategory(id, data) {
    return axios.put(`/api/equipment-categories/${id}`, data)
  },

  // 删除设备类别（管理员）
  deleteCategory(id) {
    return axios.delete(`/api/equipment-categories/${id}`)
  }
}

// 预定API
export const reservationApi = {
  // 创建预定
  createReservation(data) {
    return axios.post('/api/reservation', data)
  },

  // 获取预定列表（管理员）
  getReservations(params) {
    return axios.get('/api/reservation', { params })
  },

  // 获取预定详情
  getReservation(code) {
    return axios.get(`/api/reservation/${code}`)
  },

  // 通过预约序号获取预约详情
  getReservationByNumber(reservationNumber) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()
    const url = `/api/reservation/number/${reservationNumber}?_t=${timestamp}`

    console.log(`通过预约序号获取预约详情URL: ${url}`)
    return axios.get(url)
  },

  // 通过预定码或预约序号获取预定详情
  getReservationByCode(code, reservationNumber = null) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()

    // 构建基本URL
    let url = code.includes('?')
      ? `${code}&_t=${timestamp}`
      : `/api/reservation/code/${code}?_t=${timestamp}`

    // 如果提供了预约序号，添加到URL参数中
    if (reservationNumber) {
      // 处理预约序号参数，确保它是字符串格式
      let reservationNumberStr = '';

      if (typeof reservationNumber === 'object') {
        console.log('预约序号参数是对象类型，尝试提取预约序号:', reservationNumber);
        if (reservationNumber.reservation_number) {
          reservationNumberStr = String(reservationNumber.reservation_number);
          console.log(`从对象中提取预约序号: ${reservationNumberStr}`);
        } else {
          console.warn('预约序号参数是对象但没有reservation_number字段，忽略此参数');
          // 不再序列化整个对象，直接忽略
          reservationNumberStr = '';
        }
      } else if (typeof reservationNumber === 'string' && reservationNumber.trim()) {
        // 确保是有效的预约序号格式（通常以RN-开头）
        if (reservationNumber.startsWith('RN-') || reservationNumber.match(/^[A-Z0-9-]+$/)) {
          reservationNumberStr = reservationNumber.trim();
          console.log(`预约序号参数是字符串类型: ${reservationNumberStr}`);
        } else {
          console.warn(`预约序号格式不正确，忽略: ${reservationNumber}`);
          reservationNumberStr = '';
        }
      } else {
        console.warn(`预约序号参数类型不支持: ${typeof reservationNumber}, 值: ${reservationNumber}`);
        reservationNumberStr = '';
      }

      if (reservationNumberStr) {
        url += `&reservation_number=${encodeURIComponent(reservationNumberStr)}`;
        console.log(`添加预约序号参数: ${reservationNumberStr}`);
      }
    }

    console.log(`获取预约详情URL: ${url}`)
    return axios.get(url)
  },

  // 通过预约序号获取预定详情
  getReservationByNumber(reservationNumber) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()
    const url = `/api/reservation/number/${reservationNumber}?_t=${timestamp}`

    console.log(`通过预约序号获取预约详情URL: ${url}`)
    return axios.get(url)
  },

  // 更新预定
  updateReservation(code, data, reservationNumber = null) {
    if (reservationNumber) {
      // 如果提供了预约序号，使用专门的预约序号API
      return axios.put(`/api/reservation/number/${reservationNumber}`, data)
    } else {
      // 否则使用原有的预约码API
      return axios.put(`/api/reservation/code/${code}`, data)
    }
  },

  // 通过预约序号更新预定
  updateReservationByNumber(reservationNumber, data) {
    return axios.put(`/api/reservation/number/${reservationNumber}`, data)
  },

  // 通过预约码更新预定（支持预约序号参数）
  updateReservationByCode(code, data, reservationNumber = null) {
    const params = reservationNumber ? { reservation_number: reservationNumber } : {}
    return axios.put(`/api/reservation/code/${code}`, data, { params })
  },

  // 通过预约码获取预定详情（支持查询参数）
  getReservationByCodeWithParams(code, params = {}) {
    // 添加时间戳参数，防止缓存
    const timestamp = new Date().getTime()
    const queryParams = { ...params, _t: timestamp }

    console.log(`通过预约码获取预定详情（带参数）: ${code}`, queryParams)
    return axios.get(`/api/reservation/code/${code}`, { params: queryParams })
  },

  // 取消预定
  cancelReservation(code, data) {
    return axios.post(`/api/reservation/cancel/code/${code}`, data)
  },

  // 获取预定二维码
  getReservationQrcode(code) {
    return axios.get(`/api/reservation/qrcode/${code}`)
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

// 循环预约API
export const recurringReservationApi = {
  // 创建循环预约
  createRecurringReservation(data) {
    return axios.post('/api/recurring-reservation', data)
  },

  // 获取循环预约列表
  getRecurringReservations(params) {
    return axios.get('/api/recurring-reservation', { params })
  },

  // 获取循环预约详情
  getRecurringReservation(id) {
    return axios.get(`/api/recurring-reservation/${id}`)
  },

  // 通过预定码获取循环预约详情
  getRecurringReservationByCode(code) {
    return axios.get(`/api/recurring-reservation/code/${code}`)
  },

  // 更新循环预约
  updateRecurringReservation(id, data, updateFutureOnly = 1) {
    return axios.put(`/api/recurring-reservation/${id}`, data, {
      params: { update_future_only: updateFutureOnly }
    })
  },

  // 取消循环预约
  cancelRecurringReservation(id, userEmail = null, lang = 'zh_CN') {
    return axios.post(`/api/recurring-reservation/cancel/${id}`, null, {
      params: {
        user_email: userEmail,
        lang: lang
      }
    })
  },

  // 获取循环预约的子预约
  getChildReservations(id, includePast = 0) {
    return axios.get(`/api/recurring-reservation/${id}/reservations`, {
      params: { include_past: includePast }
    })
  }
}

// 管理员API
export const adminApi = {
  // 管理员登录
  login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    return axios.post('/api/admin/login', formData)
  },

  // 获取管理员列表（超级管理员）
  getAdmins(params) {
    return axios.get('/api/admin', { params })
  },

  // 创建管理员（超级管理员）
  createAdmin(data) {
    return axios.post('/api/admin', data)
  },

  // 更新管理员
  updateAdmin(id, data) {
    return axios.put(`/api/admin/${id}`, data)
  },

  // 删除管理员（超级管理员）
  deleteAdmin(id) {
    return axios.delete(`/api/admin/${id}`)
  },

  // 获取系统设置
  getSettings() {
    return axios.get('/api/admin/settings')
  },

  // 更新系统设置
  updateSettings(data) {
    return axios.put('/api/admin/settings', data)
  }
}

// 用户API
export const userApi = {
  // 用户登录
  login(credentials) {
    return axios.post('/api/user/login', credentials)
  },

  // 获取当前用户信息
  getProfile() {
    return axios.get('/api/user/profile')
  }
}

// 公告API
export const announcementApi = {
  // 获取所有公告
  getAnnouncements(params) {
    return axios.get('/api/announcements', { params })
  },

  // 获取单个公告
  getAnnouncement(id) {
    return axios.get(`/api/announcements/${id}`)
  },

  // 创建公告
  createAnnouncement(data) {
    return axios.post('/api/announcements', data)
  },

  // 更新公告
  updateAnnouncement(id, data) {
    return axios.put(`/api/announcements/${id}`, data)
  },

  // 删除公告
  deleteAnnouncement(id) {
    return axios.delete(`/api/announcements/${id}`)
  }
}

// 导出API对象供Vue组件使用
export const api = {
  equipment: equipmentApi,
  reservation: reservationApi,
  recurringReservation: recurringReservationApi,
  category: categoryApi,
  user: userApi,
  admin: adminApi,
  announcement: announcementApi
}

