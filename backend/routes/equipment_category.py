"""
设备类别API路由
Equipment Category API routes
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.equipment_category import (
    EquipmentCategoryCreate, EquipmentCategoryUpdate, 
    EquipmentCategory as EquipmentCategorySchema, EquipmentCategoryList
)
from backend.routes.crud.equipment_category import (
    create_category, get_category, get_categories,
    get_category_count, get_all_categories,
    update_category, delete_category, get_category_by_name
)
from backend.routes.auth import get_current_admin

router = APIRouter(
    prefix="/api/equipment-categories",
    tags=["equipment-categories"],
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=EquipmentCategorySchema)
async def create_category_api(
    category: EquipmentCategoryCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    创建新设备类别（需要管理员权限）
    Create new equipment category (admin required)
    """
    try:
        # 检查类别名称是否已存在
        existing_category = get_category_by_name(db, category.name)
        if existing_category:
            raise HTTPException(status_code=400, detail="类别名称已存在")
        
        db_category = create_category(db, category)
        return db_category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建设备类别出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建设备类别出错: {str(e)}")

@router.get("/", response_model=EquipmentCategoryList)
async def get_categories_api(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备类别列表
    Get equipment category list
    """
    try:
        items = get_categories(db, skip, limit, search)
        total = get_category_count(db, search)
        return {"items": items, "total": total}
    except Exception as e:
        logger.error(f"获取设备类别列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备类别列表出错: {str(e)}")

@router.get("/all", response_model=list[EquipmentCategorySchema])
async def get_all_categories_api(db: Session = Depends(get_db)):
    """
    获取所有设备类别
    Get all equipment categories
    """
    try:
        categories = get_all_categories(db)
        return categories
    except Exception as e:
        logger.error(f"获取所有设备类别出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取所有设备类别出错: {str(e)}")

@router.get("/{category_id}", response_model=EquipmentCategorySchema)
async def get_category_api(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    获取设备类别详情
    Get equipment category details
    """
    try:
        category = get_category(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="设备类别不存在")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取设备类别详情出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备类别详情出错: {str(e)}")

@router.put("/{category_id}", response_model=EquipmentCategorySchema)
async def update_category_api(
    category_id: int,
    category: EquipmentCategoryUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    更新设备类别信息（需要管理员权限）
    Update equipment category information (admin required)
    """
    try:
        # 检查类别名称是否已存在
        if category.name:
            existing_category = get_category_by_name(db, category.name)
            if existing_category and existing_category.id != category_id:
                raise HTTPException(status_code=400, detail="类别名称已存在")
        
        db_category = update_category(db, category_id, category)
        if not db_category:
            raise HTTPException(status_code=404, detail="设备类别不存在")
        return db_category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新设备类别信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新设备类别信息出错: {str(e)}")

@router.delete("/{category_id}")
async def delete_category_api(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    删除设备类别（需要管理员权限）
    Delete equipment category (admin required)
    """
    try:
        success = delete_category(db, category_id)
        if not success:
            raise HTTPException(status_code=404, detail="设备类别不存在")
        return {"success": True, "message": "设备类别已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除设备类别出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除设备类别出错: {str(e)}")
