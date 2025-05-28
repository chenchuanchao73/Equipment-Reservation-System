"""
日志中间件
Log middleware
"""
import logging
import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from backend.database import get_db
from backend.services.log_service import log_operation

logger = logging.getLogger(__name__)

class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取请求开始时间
        start_time = time.time()

        # 获取请求路径和方法
        path = request.url.path
        method = request.method

        # 获取客户端IP
        client_host = request.client.host if request.client else None

        # 尝试获取当前管理员
        admin = None
        db = None

        # 判断是否是登录请求
        is_login_request = path == "/api/admin/login" and method == "POST"

        try:
            # 获取数据库会话
            db_generator = get_db()
            db = next(db_generator)

            # 获取认证令牌
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                # 使用optional_admin来避免抛出异常
                from backend.routes.auth import optional_admin
                admin = await optional_admin(token, db)
        except Exception as e:
            # 只在调试模式下记录这个错误，因为大部分请求都是普通用户请求
            logger.debug(f"获取当前管理员失败: {e}")

        # 处理请求
        response = await call_next(request)

        # 计算请求处理时间
        process_time = time.time() - start_time

        # 判断是否需要记录日志
        # 只记录API请求，不记录静态文件请求
        if path.startswith("/api/") and not path.startswith("/api/health"):
            # 获取响应状态码
            status_code = response.status_code

            # 判断请求是否成功
            is_success = 200 <= status_code < 400

            # 获取操作类型和模块
            action = "login" if is_login_request else self._get_action_from_method(method)
            module = self._get_module_from_path(path)

            # 构建日志描述
            description = f"{method} {path} - {status_code}"

            # 记录日志
            if admin:
                # 管理员操作日志
                try:
                    await log_operation(
                        db=db,
                        user_type="admin",
                        user_id=admin.username,
                        user_name=admin.name,
                        action=action,
                        module=module,
                        description=description,
                        ip_address=client_host,
                        status="success" if is_success else "failed",
                        error_message=None if is_success else f"HTTP {status_code}",
                        details={
                            "path": path,
                            "method": method,
                            "status_code": status_code,
                            "process_time": process_time
                        }
                    )
                except Exception as e:
                    logger.error(f"记录管理员操作日志失败: {e}")
            elif is_login_request and is_success:
                # 登录成功的特殊处理
                try:
                    # 尝试从响应体中获取用户名
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk

                    # 重新设置响应体
                    response = Response(
                        content=response_body,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )

                    # 解析响应体获取用户信息
                    try:
                        response_data = json.loads(response_body)
                        username = response_data.get("username")
                        name = response_data.get("name", username)

                        # 记录登录日志
                        await log_operation(
                            db=db,
                            user_type="admin",
                            user_id=username,
                            user_name=name,
                            action="login",
                            module="admin",
                            description=f"管理员 {username} 登录成功",
                            ip_address=client_host,
                            status="success",
                            details={
                                "path": path,
                                "method": method,
                                "status_code": status_code,
                                "process_time": process_time
                            }
                        )
                    except json.JSONDecodeError:
                        logger.error("解析登录响应数据失败")
                except Exception as e:
                    logger.error(f"记录登录日志失败: {e}")
            else:
                # 匿名用户或普通用户操作日志
                # 只记录特定操作，如预约创建、取消等
                if self._should_log_anonymous_request(path, method):
                    try:
                        await log_operation(
                            db=db,
                            user_type="user",
                            user_id=None,
                            user_name=None,
                            action=action,
                            module=module,
                            description=description,
                            ip_address=client_host,
                            status="success" if is_success else "failed",
                            error_message=None if is_success else f"HTTP {status_code}",
                            details={
                                "path": path,
                                "method": method,
                                "status_code": status_code,
                                "process_time": process_time
                            }
                        )
                    except Exception as e:
                        logger.error(f"记录匿名用户操作日志失败: {e}")

        # 关闭数据库会话
        if db:
            db.close()

        return response

    def _get_action_from_method(self, method: str) -> str:
        """根据HTTP方法获取操作类型"""
        method_action_map = {
            "GET": "view",
            "POST": "create",
            "PUT": "update",
            "DELETE": "delete",
            "PATCH": "update"
        }
        return method_action_map.get(method, "other")

    def _get_module_from_path(self, path: str) -> str:
        """根据请求路径获取模块"""
        if "/equipment" in path:
            return "equipment"
        elif "/reservation" in path:
            return "reservation"
        elif "/admin" in path:
            return "admin"
        elif "/system" in path:
            return "system"
        else:
            return "other"

    def _should_log_anonymous_request(self, path: str, method: str) -> bool:
        """判断是否应该记录匿名用户请求"""
        # 只记录特定操作，如预约创建、取消等
        if "/reservation" in path and method in ["POST", "DELETE"]:
            return True
        return False


