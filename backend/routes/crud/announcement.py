from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
from backend.models.announcement import Announcement
from backend.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
from typing import List, Optional

# 获取日志记录器
logger = logging.getLogger(__name__)

def get_announcements(db: Session, skip: int = 0, limit: int = 10, active_only: bool = True) -> List[Announcement]:
    query = db.query(Announcement)
    if active_only:
        query = query.filter(Announcement.is_active == True)
    return query.order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()

def get_announcement(db: Session, announcement_id: int) -> Optional[Announcement]:
    return db.query(Announcement).filter(Announcement.id == announcement_id).first()

def create_announcement(db: Session, announcement: AnnouncementCreate) -> Announcement:
    # 创建公告数据
    announcement_dict = announcement.dict()
    
    # 记录调试信息
    current_time = datetime.now()
    logger.debug(f"【时区调试】CRUD-创建前时间: {current_time}")
    
    # 注意：SQLAlchemy会自动设置created_at，这里不需要手动设置
    db_announcement = Announcement(**announcement_dict)
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    
    # 调试：查看数据库中存储的时间
    logger.debug(f"【时区调试】CRUD-数据库存储时间: {db_announcement.created_at}, 时区信息: {getattr(db_announcement.created_at, 'tzinfo', None)}")
    
    return db_announcement

def update_announcement(db: Session, announcement_id: int, announcement: AnnouncementUpdate) -> Optional[Announcement]:
    db_announcement = get_announcement(db, announcement_id)
    if not db_announcement:
        return None
    for field, value in announcement.dict(exclude_unset=True).items():
        setattr(db_announcement, field, value)
    db.commit()
    db.refresh(db_announcement)
    return db_announcement

def delete_announcement(db: Session, announcement_id: int) -> bool:
    db_announcement = get_announcement(db, announcement_id)
    if not db_announcement:
        return False
    db.delete(db_announcement)
    db.commit()
    return True 