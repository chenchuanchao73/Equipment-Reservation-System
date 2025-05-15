from pydantic import BaseModel, Field, model_validator
from datetime import datetime, timedelta
from typing import Optional
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

class AnnouncementBase(BaseModel):
    title: str
    content: str
    is_active: Optional[bool] = True

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class AnnouncementOut(AnnouncementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # 新版Pydantic使用from_attributes替代orm_mode
        orm_mode = True  # 保留向后兼容

    @model_validator(mode='after')
    def convert_to_beijing_time(self):
        """模型验证后的最后一步，确保北京时间转换只发生一次"""
        if hasattr(self, 'created_at') and self.created_at:
            # 判断是否已经转换过
            # 简单判断：如果小时数>=8，可能已经是北京时间
            hour = self.created_at.hour
            
            # 记录转换前的时间
            logger.debug(f"【最终转换】created_at: {self.created_at}, 小时: {hour}")
            
            # 只有在小时数<8时才加8小时，避免重复转换
            if hour < 8:
                beijing_time = self.created_at + timedelta(hours=8)
                logger.debug(f"【最终转换】转换为北京时间: {beijing_time}")
                self.created_at = beijing_time
            else:
                logger.debug(f"【最终转换】已经是北京时间，不再转换")
                
        return self
        
    # 简化model_validate方法，依赖最终的model_validator
    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # 处理ORM对象情况
        if hasattr(obj, '__dict__') and not isinstance(obj, dict):
            # 记录原始时间
            original_time = getattr(obj, 'created_at', None)
            logger.debug(f"【model_validate】原始ORM时间: {original_time}")
            
            # 创建字典
            data = {
                "id": obj.id,
                "title": obj.title,
                "content": obj.content,
                "is_active": obj.is_active,
                "created_at": original_time
            }
            
            # 直接使用字典数据，让model_validator处理时区
            return super().model_validate(data, *args, **kwargs)
        
        # 其他情况直接传递，让model_validator处理时区
        logger.debug(f"【model_validate】传递对象: {type(obj)}")
        return super().model_validate(obj, *args, **kwargs) 