import request from './request'

/**
 * Unsplash API 封装
 * 用于获取高质量图片资源
 */
const unsplashApi = {
  /**
   * 搜索图片
   * @param {string} query - 搜索关键词
   * @param {number} page - 页码
   * @param {number} perPage - 每页数量
   * @returns {Promise} - 返回搜索结果
   */
  searchPhotos(query, page = 1, perPage = 10) {
    return request({
      url: '/api/unsplash/search',
      method: 'get',
      params: {
        query,
        page,
        per_page: perPage
      }
    })
  },
  
  /**
   * 获取随机图片
   * @param {string} query - 搜索关键词
   * @returns {Promise} - 返回随机图片
   */
  getRandomPhoto(query) {
    return request({
      url: '/api/unsplash/random',
      method: 'get',
      params: { query }
    })
  },
  
  /**
   * 根据设备类型获取合适的图片
   * @param {string} category - 设备类型
   * @returns {Promise} - 返回图片
   */
  getEquipmentPhoto(category) {
    // 根据设备类型映射到合适的搜索关键词
    const keywordMap = {
      'laptop': 'laptop computer',
      'projector': 'projector device',
      'camera': 'digital camera',
      'audio': 'audio equipment',
      'printer': 'office printer',
      'tablet': 'tablet device',
      'other': 'technology equipment'
    }
    
    const keyword = keywordMap[category.toLowerCase()] || 'technology equipment'
    
    return this.getRandomPhoto(keyword)
  },
  
  /**
   * 构建图片URL
   * @param {Object} photo - Unsplash照片对象
   * @param {string} size - 尺寸，可选值：small, regular, full
   * @returns {string} - 图片URL
   */
  buildPhotoUrl(photo, size = 'regular') {
    if (!photo || !photo.urls) {
      return ''
    }
    
    return photo.urls[size] || photo.urls.regular
  }
}

export default unsplashApi
