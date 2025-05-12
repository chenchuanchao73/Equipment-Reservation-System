"""
文件上传API路由
File upload API routes
"""
import os
import logging
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.routes.auth import get_current_admin, optional_admin

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(
    prefix="/api/upload",
    tags=["upload"],
)

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    type: str = "general",
    db: Session = Depends(get_db),
    current_user = Depends(optional_admin)
):
    """
    上传图片
    Upload image
    
    Args:
        file: 上传的文件
        type: 图片类型，可选值：general, equipment, guide
    """
    try:
        # 检查文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只允许上传图片文件")
        
        # 检查文件大小（限制为5MB）
        contents = await file.read()
        size = len(contents)
        if size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="图片大小不能超过5MB")
        
        # 重置文件指针
        await file.seek(0)
        
        # 根据类型确定上传目录
        if type == "equipment":
            upload_dir = os.path.join("backend", "static", "uploads", "equipment")
        elif type == "guide":
            upload_dir = os.path.join("backend", "static", "uploads", "guide")
        else:
            upload_dir = os.path.join("backend", "static", "uploads", "general")
        
        # 创建上传目录（如果不存在）
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 生成URL路径
        url_path = f"/static/uploads/{type}/{filename}"
        
        return {
            "success": True,
            "url": url_path,
            "filename": filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传图片失败: {str(e)}")

@router.post("/editor-image")
async def upload_editor_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(optional_admin)
):
    """
    上传富文本编辑器图片
    Upload rich text editor image
    """
    try:
        # 使用通用图片上传API，类型为guide
        result = await upload_image(file, "guide", db, current_user)
        
        # 返回Quill编辑器所需的格式
        return {"success": True, "url": result["url"]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传富文本编辑器图片失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传富文本编辑器图片失败: {str(e)}")
