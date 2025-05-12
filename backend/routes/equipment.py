"""
设备API路由
Equipment API routes
"""
import os
import logging
import shutil
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from io import BytesIO

from backend.database import get_db
from backend.models.equipment import Equipment
from backend.schemas.equipment import EquipmentCreate, EquipmentUpdate, EquipmentList, Equipment as EquipmentSchema
from backend.routes.crud.equipment import (
    create_equipment, get_equipment, get_equipments,
    get_equipment_count, get_equipment_categories,
    update_equipment, delete_equipment
)
from backend.routes.crud.reservation import get_equipment_reservations, is_equipment_available
from backend.utils.excel_handler import parse_equipment_excel, generate_equipment_template, export_equipment_data
from backend.routes.auth import get_current_admin

router = APIRouter(
    prefix="/api/equipment",
    tags=["equipment"],
)

# 设置模板引擎
templates = Jinja2Templates(directory="backend/templates")

logger = logging.getLogger(__name__)

@router.post("/", response_model=EquipmentSchema)
async def create_equipment_api(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    创建新设备（需要管理员权限）
    Create new equipment (admin required)
    """
    try:
        db_equipment = create_equipment(db, equipment)

        # 生成设备二维码
        base_url = "http://localhost:8080"
        # 二维码功能已移除

        # 如果没有设置图片，使用默认图片
        if not db_equipment.image_path:
            db_equipment.image_path = "/static/images/default_equipment.png"

        # 更新设备信息
        db.commit()

        return db_equipment
    except Exception as e:
        logger.error(f"创建设备出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建设备出错: {str(e)}")

@router.get("/", response_model=EquipmentList)
async def get_equipments_api(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取设备列表
    Get equipment list
    """
    try:
        items = get_equipments(db, skip, limit, category, status, search)
        total = get_equipment_count(db, category, status, search)

        # 检查每个设备当前是否被预约
        from backend.routes.crud.reservation import is_equipment_currently_reserved
        for item in items:
            item.currently_reserved = is_equipment_currently_reserved(db, item.id)

        return {"items": items, "total": total}
    except Exception as e:
        logger.error(f"获取设备列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备列表出错: {str(e)}")

@router.get("/categories")
async def get_equipment_categories_api(db: Session = Depends(get_db)):
    """
    获取设备类别列表
    Get equipment categories
    """
    try:
        categories = get_equipment_categories(db)
        # 将元组列表转换为字符串列表
        category_list = [category[0] for category in categories if category[0]]
        return {"categories": category_list}
    except Exception as e:
        logger.error(f"获取设备类别出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备类别出错: {str(e)}")

@router.get("/{equipment_id}", response_model=EquipmentSchema)
async def get_equipment_api(
    equipment_id: int,
    db: Session = Depends(get_db)
):
    """
    获取设备详情
    Get equipment details
    """
    try:
        equipment = get_equipment(db, equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail="设备不存在")
        return equipment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取设备详情出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备详情出错: {str(e)}")

@router.put("/{equipment_id}", response_model=EquipmentSchema)
async def update_equipment_api(
    equipment_id: int,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    更新设备信息（需要管理员权限）
    Update equipment information (admin required)
    """
    try:
        db_equipment = update_equipment(db, equipment_id, equipment)
        if not db_equipment:
            raise HTTPException(status_code=404, detail="设备不存在")
        return db_equipment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新设备信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新设备信息出错: {str(e)}")

@router.delete("/{equipment_id}")
async def delete_equipment_api(
    equipment_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    删除设备（需要管理员权限）
    Delete equipment (admin required)
    """
    try:
        success = delete_equipment(db, equipment_id)
        if not success:
            raise HTTPException(status_code=404, detail="设备不存在")
        return {"success": True, "message": "设备已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除设备出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除设备出错: {str(e)}")

@router.get("/{equipment_id}/availability")
async def get_equipment_availability_api(
    equipment_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """
    获取设备可用性
    Get equipment availability
    """
    try:
        # 检查设备是否存在
        equipment = get_equipment(db, equipment_id)
        if not equipment:
            raise HTTPException(status_code=404, detail="设备不存在")

        # 获取设备预定情况
        availability = is_equipment_available(db, equipment_id, start_date, end_date)
        return availability
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取设备可用性出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备可用性出错: {str(e)}")

@router.post("/upload-image", response_model=dict)
async def upload_equipment_image(
    file: UploadFile = File(...),
    equipment_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    上传设备图片（需要管理员权限）
    Upload equipment image (admin required)
    """
    try:
        # 记录上传文件信息
        logger.info(f"正在上传文件: {file.filename}, 类型: {file.content_type}, 大小: {file.size} bytes")

        # 检查文件类型
        if not file.content_type.startswith('image/'):
            logger.warning(f"文件类型错误: {file.content_type}")
            raise HTTPException(status_code=400, detail="只允许上传图片文件")

        # 检查文件大小（限制为8MB）
        contents = await file.read()
        size = len(contents)
        logger.info(f"文件大小: {size} bytes ({size/1024/1024:.2f} MB)")

        if size > 8 * 1024 * 1024:  # 8MB
            logger.warning(f"文件过大: {size/1024/1024:.2f} MB")
            raise HTTPException(status_code=400, detail="图片大小不能超过8MB")

        # 重置文件指针
        await file.seek(0)

        # 创建上传目录（如果不存在）
        from config import BASE_DIR
        upload_dir = os.path.join(BASE_DIR, "backend", "static", "uploads", "equipment")
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"上传目录: {upload_dir}")

        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)

        # 保存文件
        try:
            logger.info(f"尝试保存文件到: {file_path}")
            logger.info(f"文件路径是否存在: {os.path.exists(os.path.dirname(file_path))}")

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"文件保存成功: {file_path}")
            logger.info(f"文件是否存在: {os.path.exists(file_path)}")
            logger.info(f"文件大小: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'} bytes")
        except Exception as save_error:
            logger.error(f"保存文件失败: {str(save_error)}")
            raise HTTPException(status_code=500, detail=f"保存文件失败: {str(save_error)}")

        # 生成URL路径
        image_url = f"/static/uploads/equipment/{filename}"
        logger.info(f"图片URL: {image_url}")

        # 如果提供了设备ID，更新设备的图片URL
        if equipment_id:
            equipment = get_equipment(db, equipment_id)
            if not equipment:
                raise HTTPException(status_code=404, detail="设备不存在")

            # 更新设备图片URL
            equipment.image_path = image_url
            db.commit()

        return {
            "success": True,
            "data": {
                "image_url": image_url,
                "filename": filename
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"上传设备图片出错: {str(e)}"
        logger.error(error_msg)
        logger.error(f"异常类型: {type(e).__name__}")
        # 返回更详细的错误信息
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/export")
async def export_equipment_api(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    导出设备数据（需要管理员权限）
    Export equipment data (admin required)
    """
    try:
        # 获取所有设备数据
        equipments = get_equipments(db, 0, 1000, category, status)

        # 导出数据
        excel_bytes = export_equipment_data(equipments)

        # 设置文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"equipment_export_{timestamp}.xlsx"

        # 返回Excel文件
        return StreamingResponse(
            BytesIO(excel_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"导出设备数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导出设备数据出错: {str(e)}")

@router.get("/template")
async def get_equipment_template_api(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    获取设备导入模板（需要管理员权限）
    Get equipment import template (admin required)
    """
    try:
        # 生成模板
        template_bytes = generate_equipment_template()

        # 设置文件名
        filename = "equipment_import_template.xlsx"

        # 返回Excel文件
        return StreamingResponse(
            BytesIO(template_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"获取设备导入模板出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备导入模板出错: {str(e)}")

@router.post("/import")
async def import_equipment_api(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    导入设备数据（需要管理员权限）
    Import equipment data (admin required)
    """
    try:
        # 检查文件类型
        filename = file.filename.lower()
        if not (filename.endswith('.xlsx') or filename.endswith('.xls')):
            raise ValueError("文件类型不支持，请上传Excel文件（.xlsx或.xls）")

        # 读取文件内容
        try:
            contents = await file.read()
            if not contents:
                raise ValueError("文件内容为空")
        except Exception as read_error:
            logger.error(f"读取文件内容失败: {str(read_error)}")
            raise ValueError(f"读取文件内容失败: {str(read_error)}")

        # 解析Excel文件
        try:
            equipment_data = parse_equipment_excel(contents)
        except ValueError as ve:
            # 直接抛出用户可读的错误
            raise ve
        except Exception as parse_error:
            logger.error(f"解析Excel文件失败: {str(parse_error)}")
            raise ValueError(f"解析Excel文件失败: {str(parse_error)}")

        # 导入设备数据
        imported_count = 0
        try:
            for item in equipment_data:
                equipment = EquipmentCreate(**item)
                create_equipment(db, equipment)
                imported_count += 1
        except Exception as import_error:
            logger.error(f"导入设备数据失败: {str(import_error)}")
            if imported_count > 0:
                return {
                    "success": True,
                    "message": f"部分导入成功，已导入 {imported_count} 个设备，但在导入过程中出现错误: {str(import_error)}",
                    "count": imported_count
                }
            else:
                raise ValueError(f"导入设备数据失败: {str(import_error)}")

        return {
            "success": True,
            "message": f"成功导入 {imported_count} 个设备",
            "count": imported_count
        }
    except ValueError as ve:
        # 直接抛出用户可读的错误
        logger.error(f"导入设备数据出错: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"导入设备数据出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"导入设备数据出错: {str(e)}")

