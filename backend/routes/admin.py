"""
管理员API路由
Admin API routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.admin import Admin
from backend.schemas.admin import (
    AdminCreate, AdminUpdate, AdminList,
    Admin as AdminSchema, Token, TokenData,
    ChangePasswordRequest
)
from backend.routes.crud.admin import (
    get_admin, get_admins, get_admin_count,
    create_admin, update_admin, delete_admin,
    change_admin_password
)
from backend.routes.auth import (
    authenticate_admin, create_access_token,
    get_current_admin
)
from backend.routes.crud.email import router as email_router

router = APIRouter(
    prefix="/api/admin",
    tags=["admin"],
)

logger = logging.getLogger(__name__)

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    管理员登录获取令牌
    Admin login to get token
    """
    admin = await authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": admin.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "admin_id": admin.id,
        "username": admin.username,
        "name": admin.name,
        "role": admin.role
    }

@router.get("/", response_model=AdminList)
async def get_admins_api(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    获取管理员列表（需要管理员权限）
    Get admin list (admin required)
    """
    # 验证当前用户是否为超级管理员
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        )

    try:
        items = get_admins(db, skip, limit, search)
        total = get_admin_count(db, search)
        return {"items": items, "total": total}
    except Exception as e:
        logger.error(f"获取管理员列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取管理员列表出错: {str(e)}")

@router.post("/", response_model=AdminSchema)
async def create_admin_api(
    admin: AdminCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    创建管理员（需要超级管理员权限）
    Create admin (superadmin required)
    """
    # 验证当前用户是否为超级管理员
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限创建管理员账户"
        )

    try:
        db_admin = create_admin(db, admin)
        return db_admin
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建管理员出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建管理员出错: {str(e)}")

@router.get("/{admin_id}", response_model=AdminSchema)
async def get_admin_api(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    通过ID获取管理员
    Get admin by ID
    """
    # 只允许超级管理员查看其他管理员，或者管理员查看自己
    if current_admin.role != "superadmin" and current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问此资源"
        )

    db_admin = get_admin(db, admin_id)
    if not db_admin:
        raise HTTPException(status_code=404, detail="管理员不存在")
    return db_admin

@router.put("/{admin_id}", response_model=AdminSchema)
async def update_admin_api(
    admin_id: int,
    admin: AdminUpdate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    更新管理员信息
    Update admin information
    """
    # 只允许超级管理员修改其他管理员，或者管理员修改自己
    if current_admin.role != "superadmin" and current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改此管理员"
        )

    # 不允许非超级管理员修改自己的角色
    if current_admin.role != "superadmin" and admin.role and admin.role != current_admin.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限修改管理员角色"
        )

    try:
        db_admin = update_admin(db, admin_id, admin)
        if not db_admin:
            raise HTTPException(status_code=404, detail="管理员不存在")
        return db_admin
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"更新管理员信息出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新管理员信息出错: {str(e)}")

@router.delete("/{admin_id}")
async def delete_admin_api(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    删除管理员（需要超级管理员权限）
    Delete admin (superadmin required)
    """
    # 验证当前用户是否为超级管理员
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限删除管理员账户"
        )

    # 不允许删除自己
    if current_admin.id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )

    try:
        success = delete_admin(db, admin_id)
        if not success:
            raise HTTPException(status_code=404, detail="管理员不存在")
        return {"success": True, "message": "管理员已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除管理员出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除管理员出错: {str(e)}")

# 修改密码
@router.put("/{admin_id}/change-password", response_model=dict)
async def change_password_api(
    admin_id: int,
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """
    修改管理员密码
    Change admin password
    """
    # 只允许修改自己的密码
    if current_admin.id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能修改自己的密码"
        )

    try:
        success, message = change_admin_password(
            db,
            current_admin.id,
            password_data.old_password,
            password_data.new_password
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {"success": True, "message": message}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"修改密码出错: {str(e)}")

# 包含邮件相关路由
router.include_router(
    email_router,
    prefix="/email",
    tags=["email"],
)
