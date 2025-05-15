from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime
from backend.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
from backend.routes.crud import announcement as crud_announcement
from backend.database import get_db
from backend.models.announcement import Announcement
# from backend.dependencies import get_current_admin  # 假设已有管理员依赖

router = APIRouter(
    prefix="/api/announcements",
    tags=["announcements"]
)

# 获取日志记录器
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[AnnouncementOut])
def read_announcements(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """获取有效公告列表（转换为北京时间）"""
    announcements = crud_announcement.get_announcements(db, skip=skip, limit=limit, active_only=True)
    
    # 调试信息：记录公告时间
    for ann in announcements:
        logger.debug(f"【时区调试】读取公告ID:{ann.id}, 原始时间:{ann.created_at}, 类型:{type(ann.created_at)}")
    
    return announcements

@router.get("/all", response_model=List[AnnouncementOut])
def read_all_announcements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有公告列表（转换为北京时间）"""
    # admin = get_current_admin()  # 权限校验，后续补充
    announcements = crud_announcement.get_announcements(db, skip=skip, limit=limit, active_only=False)
    
    # 调试信息：记录公告时间
    for ann in announcements:
        logger.debug(f"【时区调试】读取所有公告ID:{ann.id}, 原始时间:{ann.created_at}, 类型:{type(ann.created_at)}")
    
    return announcements

@router.get("/{announcement_id}", response_model=AnnouncementOut)
def read_announcement(announcement_id: int, db: Session = Depends(get_db)):
    db_announcement = crud_announcement.get_announcement(db, announcement_id)
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告未找到")
    
    # 调试信息
    logger.debug(f"【时区调试】读取单个公告ID:{db_announcement.id}, 原始时间:{db_announcement.created_at}, 类型:{type(db_announcement.created_at)}")
    
    return db_announcement

@router.post("/", response_model=AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(announcement: AnnouncementCreate, db: Session = Depends(get_db)):
    # admin = get_current_admin()  # 权限校验，后续补充
    
    # 调试信息：记录创建前的当前时间
    current_time = datetime.now()
    logger.debug(f"【时区调试】创建公告前的当前时间: {current_time}, 本地时区信息: {current_time.astimezone().tzinfo}")
    
    # 创建公告
    db_announcement = crud_announcement.create_announcement(db, announcement)
    
    # 调试信息：记录创建后的公告时间
    logger.debug(f"【时区调试】创建公告后ID:{db_announcement.id}, 数据库存储时间:{db_announcement.created_at}, 类型:{type(db_announcement.created_at)}")
    
    return db_announcement

@router.put("/{announcement_id}", response_model=AnnouncementOut)
def update_announcement(announcement_id: int, announcement: AnnouncementUpdate, db: Session = Depends(get_db)):
    db_announcement = crud_announcement.update_announcement(db, announcement_id, announcement)
    if not db_announcement:
        raise HTTPException(status_code=404, detail="公告未找到")
    return db_announcement

@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: int, db: Session = Depends(get_db)):
    # admin = get_current_admin()  # 权限校验，后续补充
    if not crud_announcement.delete_announcement(db, announcement_id):
        raise HTTPException(status_code=404, detail="公告未找到")
    return None 