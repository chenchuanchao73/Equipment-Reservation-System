<template>
  <el-card class="equipment-card" shadow="hover" :body-style="{ padding: '0px' }">
    <div class="equipment-image" :style="{ backgroundImage: `url(${imageUrl})` }">
      <div class="equipment-status" :class="statusClass">
        {{ statusText }}
      </div>
    </div>
    <div class="equipment-info">
      <h3 class="equipment-name">{{ equipment.name }}</h3>
      <div class="equipment-meta">
        <span class="equipment-category">
          <i class="el-icon-collection-tag"></i> {{ equipment.category }}
        </span>
        <span class="equipment-location">
          <i class="el-icon-location-outline"></i> {{ equipment.location }}
        </span>
      </div>
      <p class="equipment-description" v-if="equipment.description">
        {{ truncatedDescription }}
      </p>
      <p class="equipment-description" v-else>
        {{ $t('equipment.noDescription') }}
      </p>
      <div class="equipment-actions">
        <el-button 
          type="primary" 
          size="small" 
          @click="viewDetail"
        >
          {{ $t('equipment.viewDetail') }}
        </el-button>
        <el-button 
          type="success" 
          size="small" 
          @click="reserve"
          :disabled="!isAvailable"
        >
          {{ $t('equipment.reserve') }}
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import unsplashApi from '@/utils/unsplash'

export default {
  name: 'EquipmentCard',
  
  props: {
    equipment: {
      type: Object,
      required: true
    }
  },
  
  data() {
    return {
      imageUrl: ''
    }
  },
  
  computed: {
    isAvailable() {
      return this.equipment.status === 'available'
    },
    
    statusClass() {
      return {
        'status-available': this.isAvailable,
        'status-maintenance': !this.isAvailable
      }
    },
    
    statusText() {
      return this.isAvailable 
        ? this.$t('equipment.available') 
        : this.$t('equipment.maintenance')
    },
    
    truncatedDescription() {
      if (!this.equipment.description) return ''
      
      return this.equipment.description.length > 100
        ? this.equipment.description.substring(0, 100) + '...'
        : this.equipment.description
    }
  },
  
  methods: {
    viewDetail() {
      this.$router.push(`/equipment/${this.equipment.id}`)
    },
    
    reserve() {
      this.$router.push(`/equipment/${this.equipment.id}/reserve`)
    },
    
    async loadImage() {
      try {
        // 如果设备已有图片，则使用设备图片
        if (this.equipment.image_url) {
          this.imageUrl = this.equipment.image_url
          return
        }
        
        // 否则从Unsplash获取图片
        const response = await unsplashApi.getEquipmentPhoto(this.equipment.category)
        if (response && response.urls) {
          this.imageUrl = response.urls.regular
        } else {
          // 使用默认图片
          this.imageUrl = require('@/assets/images/default-equipment.jpg')
        }
      } catch (error) {
        console.error('加载设备图片失败:', error)
        // 使用默认图片
        this.imageUrl = require('@/assets/images/default-equipment.jpg')
      }
    }
  },
  
  created() {
    this.loadImage()
  }
}
</script>

<style scoped>
.equipment-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.equipment-card:hover {
  transform: translateY(-5px);
}

.equipment-image {
  height: 200px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.equipment-status {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status-available {
  background-color: #67C23A;
  color: white;
}

.status-maintenance {
  background-color: #F56C6C;
  color: white;
}

.equipment-info {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.equipment-name {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 18px;
  font-weight: bold;
}

.equipment-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  color: #606266;
}

.equipment-description {
  flex-grow: 1;
  margin-bottom: 15px;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.equipment-actions {
  display: flex;
  justify-content: space-between;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .equipment-image {
    height: 150px;
  }
  
  .equipment-meta {
    flex-direction: column;
  }
  
  .equipment-category {
    margin-bottom: 5px;
  }
}
</style>
