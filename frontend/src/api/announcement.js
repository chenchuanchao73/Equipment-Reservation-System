import request from '@/utils/request'

// 获取有效公告列表
export function fetchAnnouncements(params) {
  return request({
    url: '/api/announcements/',
    method: 'get',
    params
  })
}

// 获取所有公告（含未激活）
export function fetchAllAnnouncements(params) {
  return request({
    url: '/api/announcements/all',
    method: 'get',
    params
  })
}

// 获取单条公告
export function fetchAnnouncement(id) {
  return request({
    url: `/api/announcements/${id}`,
    method: 'get'
  })
}

// 创建公告
export function createAnnouncement(data) {
  return request({
    url: '/api/announcements/',
    method: 'post',
    data
  })
}

// 更新公告
export function updateAnnouncement(id, data) {
  return request({
    url: `/api/announcements/${id}`,
    method: 'put',
    data
  })
}

// 删除公告
export function deleteAnnouncement(id) {
  return request({
    url: `/api/announcements/${id}`,
    method: 'delete'
  })
} 