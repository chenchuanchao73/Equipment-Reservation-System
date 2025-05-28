"""
Excel处理工具
Excel Handler
"""
import os
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from io import BytesIO

# 设置日志
logger = logging.getLogger(__name__)

def read_excel(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    读取Excel文件
    Read Excel file

    Args:
        file_path (str): Excel文件路径
        sheet_name (str, optional): 工作表名称. Defaults to None.

    Returns:
        List[Dict[str, Any]]: 数据列表
    """
    try:
        # 读取Excel文件
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(file_path)

        # 将DataFrame转换为字典列表
        data = df.to_dict(orient="records")

        return data
    except Exception as e:
        logger.error(f"读取Excel文件失败: {str(e)}")
        raise e

def read_excel_from_bytes(file_bytes: bytes, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    从字节流读取Excel文件
    Read Excel file from bytes

    Args:
        file_bytes (bytes): Excel文件字节流
        sheet_name (str, optional): 工作表名称. Defaults to None.

    Returns:
        List[Dict[str, Any]]: 数据列表
    """
    try:
        # 从字节流读取Excel文件
        # 明确指定Excel引擎，防止自动检测失败
        if sheet_name:
            df = pd.read_excel(BytesIO(file_bytes), sheet_name=sheet_name, engine='openpyxl')
        else:
            df = pd.read_excel(BytesIO(file_bytes), engine='openpyxl')

        # 将DataFrame转换为字典列表
        data = df.to_dict(orient="records")

        return data
    except Exception as e:
        logger.error(f"从字节流读取Excel文件失败: {str(e)}")
        raise e

def write_excel(data: List[Dict[str, Any]], file_path: str, sheet_name: str = "Sheet1") -> str:
    """
    将数据写入Excel文件
    Write data to Excel file

    Args:
        data (List[Dict[str, Any]]): 数据列表
        file_path (str): Excel文件路径
        sheet_name (str, optional): 工作表名称. Defaults to "Sheet1".

    Returns:
        str: Excel文件路径
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 将字典列表转换为DataFrame
        df = pd.DataFrame(data)

        # 写入Excel文件
        df.to_excel(file_path, sheet_name=sheet_name, index=False)

        return file_path
    except Exception as e:
        logger.error(f"写入Excel文件失败: {str(e)}")
        raise e

def write_excel_to_bytes(data: List[Dict[str, Any]], sheet_name: str = "Sheet1") -> bytes:
    """
    将数据写入Excel文件并返回字节流
    Write data to Excel file and return bytes

    Args:
        data (List[Dict[str, Any]]): 数据列表
        sheet_name (str, optional): 工作表名称. Defaults to "Sheet1".

    Returns:
        bytes: Excel文件字节流
    """
    try:
        # 将字典列表转换为DataFrame
        df = pd.DataFrame(data)

        # 写入Excel文件
        output = BytesIO()
        df.to_excel(output, sheet_name=sheet_name, index=False, engine='openpyxl')

        # 获取字节流
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        logger.error(f"将数据写入Excel文件并返回字节流失败: {str(e)}")
        raise e

def parse_equipment_excel(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    解析设备Excel文件
    Parse equipment Excel file

    Args:
        file_bytes (bytes): Excel文件字节流

    Returns:
        List[Dict[str, Any]]: 设备数据列表
    """
    try:
        # 检查文件内容是否为空
        if not file_bytes:
            raise ValueError("文件内容为空")

        # 从字节流读取Excel文件
        try:
            data = read_excel_from_bytes(file_bytes)
        except Exception as excel_error:
            logger.error(f"读取Excel文件失败: {str(excel_error)}")
            raise ValueError(f"读取Excel文件失败: {str(excel_error)}")

        # 检查数据是否为空
        if not data:
            raise ValueError("文件中没有数据")

        # 验证必填字段
        required_fields = ["name", "category"]
        for i, item in enumerate(data):
            for field in required_fields:
                if field not in item or pd.isna(item[field]):
                    raise ValueError(f"第 {i+1} 行缺少必填字段: {field}")

        # 处理数据
        for item in data:
            # 设置默认值
            if "status" not in item or pd.isna(item["status"]):
                item["status"] = "available"

            # 处理NaN值
            for key, value in item.items():
                if pd.isna(value):
                    item[key] = None

        return data
    except ValueError as ve:
        # 直接抛出用户可读的错误
        logger.error(f"解析设备Excel文件失败: {str(ve)}")
        raise ve
    except Exception as e:
        logger.error(f"解析设备Excel文件失败: {str(e)}")
        raise ValueError(f"解析设备Excel文件失败: {str(e)}")

def generate_equipment_template() -> bytes:
    """
    生成设备导入模板
    Generate equipment import template

    Returns:
        bytes: Excel文件字节流
    """
    try:
        # 模板数据
        data = [
            {
                "name": "示例设备1",
                "category": "笔记本电脑",
                "model": "ThinkPad X1 Carbon",
                "location": "IT部门",
                "status": "available",
                "description": "这是一个示例设备"
            },
            {
                "name": "示例设备2",
                "category": "投影仪",
                "model": "Epson EB-U05",
                "location": "会议室A",
                "status": "available",
                "description": "这是另一个示例设备"
            }
        ]

        # 生成Excel文件
        return write_excel_to_bytes(data, sheet_name="设备导入模板")
    except Exception as e:
        logger.error(f"生成设备导入模板失败: {str(e)}")
        raise e

def export_equipment_data(equipment_list: List[Dict[str, Any]]) -> bytes:
    """
    导出设备数据
    Export equipment data

    Args:
        equipment_list (List[Dict[str, Any]]): 设备数据列表

    Returns:
        bytes: Excel文件字节流
    """
    try:
        # 处理数据
        export_data = []
        for equipment in equipment_list:
            export_data.append({
                "name": equipment.get("name"),
                "category": equipment.get("category"),
                "model": equipment.get("model"),
                "location": equipment.get("location"),
                "status": equipment.get("status"),
                "description": equipment.get("description"),
                "created_at": equipment.get("created_at"),
                "updated_at": equipment.get("updated_at")
            })

        # 生成Excel文件
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return write_excel_to_bytes(export_data, sheet_name=f"设备数据_{timestamp}")
    except Exception as e:
        logger.error(f"导出设备数据失败: {str(e)}")
        raise e

def export_reservation_data_simple(reservation_list: List[Dict[str, Any]], selected_fields: List[str] = None, export_format: str = "csv") -> bytes:
    """
    导出预定数据（简化版，不依赖pandas）
    Export reservation data (simplified version without pandas dependency)

    Args:
        reservation_list (List[Dict[str, Any]]): 预定数据列表
        selected_fields (List[str], optional): 选择的导出字段. Defaults to None.
        export_format (str, optional): 导出格式 csv. Defaults to "csv".

    Returns:
        bytes: CSV文件字节流
    """
    try:
        import csv
        from io import StringIO

        # 定义所有可用字段及其中文名称
        field_mapping = {
            "id": "ID",
            "reservation_number": "预约编号",
            "reservation_code": "预约码",
            "equipment_name": "设备名称",
            "equipment_category": "设备类别",
            "equipment_location": "设备位置",
            "user_name": "预约人姓名",
            "user_department": "预约人部门",
            "user_contact": "联系方式",
            "user_email": "邮箱地址",
            "start_datetime": "开始时间",
            "end_datetime": "结束时间",
            "purpose": "使用目的",
            "status": "预约状态",
            "created_at": "创建时间"
        }

        # 如果没有指定字段，使用所有字段
        if not selected_fields:
            selected_fields = list(field_mapping.keys())

        # 处理数据
        export_data = []
        for reservation in reservation_list:
            row_data = {}
            for field in selected_fields:
                if field in field_mapping:
                    # 使用中文字段名作为列名
                    chinese_field_name = field_mapping[field]
                    value = reservation.get(field)

                    # 处理特殊字段
                    if field == "status":
                        # 状态字段转换为中文
                        status_mapping = {
                            "confirmed": "已确认",
                            "in_use": "使用中",
                            "expired": "已过期",
                            "cancelled": "已取消"
                        }
                        value = status_mapping.get(value, value)
                    elif field in ["start_datetime", "end_datetime", "created_at"] and value:
                        # 时间字段格式化
                        if isinstance(value, str):
                            try:
                                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                value = dt.strftime("%Y-%m-%d %H:%M:%S")
                            except:
                                pass
                        elif hasattr(value, 'strftime'):
                            value = value.strftime("%Y-%m-%d %H:%M:%S")

                    # 确保值不为None
                    if value is None:
                        value = ""

                    row_data[chinese_field_name] = str(value)

            export_data.append(row_data)

        # 生成CSV文件
        output = StringIO()
        if export_data:
            fieldnames = list(export_data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(export_data)

        # 转换为字节流
        csv_content = output.getvalue()
        return csv_content.encode('utf-8-sig')  # 使用UTF-8 BOM以便Excel正确显示中文

    except Exception as e:
        logger.error(f"导出预定数据失败: {str(e)}")
        raise e

def export_reservation_data(reservation_list: List[Dict[str, Any]], selected_fields: List[str] = None, export_format: str = "excel") -> bytes:
    """
    导出预定数据
    Export reservation data

    Args:
        reservation_list (List[Dict[str, Any]]): 预定数据列表
        selected_fields (List[str], optional): 选择的导出字段. Defaults to None.
        export_format (str, optional): 导出格式 excel/csv. Defaults to "excel".

    Returns:
        bytes: Excel/CSV文件字节流
    """
    try:
        # 如果是CSV格式或者pandas不可用，使用简化版本
        if export_format.lower() == "csv":
            return export_reservation_data_simple(reservation_list, selected_fields, "csv")

        # 尝试使用pandas导出Excel
        try:
            import pandas as pd

            # 定义所有可用字段及其中文名称
            field_mapping = {
                "id": "ID",
                "reservation_number": "预约编号",
                "reservation_code": "预约码",
                "equipment_name": "设备名称",
                "equipment_category": "设备类别",
                "equipment_location": "设备位置",
                "user_name": "预约人姓名",
                "user_department": "预约人部门",
                "user_contact": "联系方式",
                "user_email": "邮箱地址",
                "start_datetime": "开始时间",
                "end_datetime": "结束时间",
                "purpose": "使用目的",
                "status": "预约状态",
                "created_at": "创建时间"
            }

            # 如果没有指定字段，使用所有字段
            if not selected_fields:
                selected_fields = list(field_mapping.keys())

            # 处理数据
            export_data = []
            for reservation in reservation_list:
                row_data = {}
                for field in selected_fields:
                    if field in field_mapping:
                        # 使用中文字段名作为列名
                        chinese_field_name = field_mapping[field]
                        value = reservation.get(field)

                        # 处理特殊字段
                        if field == "status":
                            # 状态字段转换为中文
                            status_mapping = {
                                "confirmed": "已确认",
                                "in_use": "使用中",
                                "expired": "已过期",
                                "cancelled": "已取消"
                            }
                            value = status_mapping.get(value, value)
                        elif field in ["start_datetime", "end_datetime", "created_at"] and value:
                            # 时间字段格式化
                            if isinstance(value, str):
                                try:
                                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                    value = dt.strftime("%Y-%m-%d %H:%M:%S")
                                except:
                                    pass
                            elif hasattr(value, 'strftime'):
                                value = value.strftime("%Y-%m-%d %H:%M:%S")

                        row_data[chinese_field_name] = value

                export_data.append(row_data)

            # 生成Excel文件
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return write_excel_to_bytes(export_data, sheet_name=f"预约数据_{timestamp}")

        except ImportError:
            # 如果pandas不可用，回退到CSV格式
            logger.warning("pandas不可用，回退到CSV格式导出")
            return export_reservation_data_simple(reservation_list, selected_fields, "csv")

    except Exception as e:
        logger.error(f"导出预定数据失败: {str(e)}")
        raise e
