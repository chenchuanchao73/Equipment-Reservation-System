"""
测试北京时间记录功能
Test Beijing time recording functionality
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所需模块
from backend.utils.db_utils import get_beijing_now

# 数据库路径
DB_PATH = os.path.join('equipment_reservation.db')

def test_direct_sql_insert():
    """使用直接SQL插入测试时间戳记录"""
    logger.info("使用直接SQL插入测试时间戳记录")

    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 获取当前北京时间
        current_beijing_time = get_beijing_now()
        current_utc_time = datetime.utcnow()

        logger.info(f"当前北京时间: {current_beijing_time}")
        logger.info(f"当前UTC时间: {current_utc_time}")
        logger.info(f"时差（小时）: {(current_beijing_time - current_utc_time).total_seconds() / 3600}")

        # 创建一个临时表用于测试
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_beijing_time (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP
        )
        ''')

        # 插入一条测试记录
        test_name = f"test_{int(datetime.now().timestamp())}"
        # 使用北京时间作为created_at的值
        beijing_time_str = current_beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
        INSERT INTO test_beijing_time (name, created_at) VALUES (?, ?)
        ''', (test_name, beijing_time_str))

        # 提交事务
        conn.commit()

        # 查询插入的记录
        cursor.execute('''
        SELECT id, name, created_at FROM test_beijing_time WHERE name = ?
        ''', (test_name,))

        row = cursor.fetchone()
        if row:
            record_id, record_name, created_at_str = row
            logger.info(f"记录ID: {record_id}, 名称: {record_name}, 创建时间: {created_at_str}")

            # 解析时间字符串
            try:
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                logger.info(f"解析后的创建时间: {created_at}")

                # 检查小时值是否符合北京时间（UTC+8）
                beijing_hour = current_beijing_time.hour
                created_hour = created_at.hour
                logger.info(f"当前北京时间小时值: {beijing_hour}, 记录的小时值: {created_hour}")

                # 小时值应该相同或相差不大
                hour_diff = abs(beijing_hour - created_hour)
                if hour_diff <= 1:  # 允许1小时误差（考虑测试执行时间）
                    logger.info("✅ 测试通过: 小时值符合北京时间")
                else:
                    logger.error(f"❌ 测试失败: 小时值不符合北京时间，相差{hour_diff}小时")
            except Exception as e:
                logger.error(f"解析时间字符串时出错: {str(e)}")
        else:
            logger.error("未找到插入的记录")

        # 删除测试表
        cursor.execute('DROP TABLE test_beijing_time')
        conn.commit()
        logger.info("已删除测试表")

    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
    finally:
        if conn:
            conn.close()

def test_through_api():
    """通过API测试时间戳记录"""
    logger.info("通过API测试时间戳记录")

    try:
        import requests

        # 获取当前北京时间
        current_beijing_time = get_beijing_now()
        logger.info(f"当前北京时间: {current_beijing_time}")

        # 创建一个新的设备分类（这是一个简单的API调用）
        test_name = f"测试分类_{int(datetime.now().timestamp())}"
        response = requests.post(
            "http://localhost:8000/api/admin/equipment/categories",
            json={"name": test_name, "description": "测试北京时间记录"},
            headers={"Authorization": "Bearer admin_token"}  # 假设有一个管理员令牌
        )

        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            logger.info(f"API响应: {data}")

            # 检查created_at时间戳
            if "created_at" in data:
                created_at_str = data["created_at"]
                logger.info(f"API返回的created_at: {created_at_str}")

                # 解析时间字符串
                try:
                    # 假设API返回的是ISO格式的时间字符串
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    logger.info(f"解析后的创建时间: {created_at}")

                    # 检查小时值是否符合北京时间（UTC+8）
                    beijing_hour = current_beijing_time.hour
                    created_hour = created_at.hour
                    logger.info(f"当前北京时间小时值: {beijing_hour}, 记录的小时值: {created_hour}")

                    # 小时值应该相同或相差不大
                    hour_diff = abs(beijing_hour - created_hour)
                    if hour_diff <= 1:  # 允许1小时误差（考虑测试执行时间）
                        logger.info("✅ 测试通过: 小时值符合北京时间")
                    else:
                        logger.error(f"❌ 测试失败: 小时值不符合北京时间，相差{hour_diff}小时")
                except Exception as e:
                    logger.error(f"解析时间字符串时出错: {str(e)}")
            else:
                logger.error("API响应中没有created_at字段")
        else:
            logger.error(f"API调用失败: {response.status_code} - {response.text}")

    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")

def test_manual_reservation():
    """手动创建预约测试"""
    logger.info("手动创建预约测试")
    logger.info("请按照以下步骤进行测试：")
    logger.info("1. 打开浏览器，访问 http://localhost:8080/")
    logger.info("2. 选择一个设备，点击'预约'按钮")
    logger.info("3. 填写预约表单，提交预约")
    logger.info("4. 登录管理控制台，访问 http://localhost:8081/#/admin/login")
    logger.info("5. 进入'预定管理'页面，查看新创建的预约")
    logger.info("6. 检查预约的'创建时间'是否为当前北京时间")
    logger.info("7. 进入'系统设置' -> '数据库表查看'，选择'reservation'表")
    logger.info("8. 查找刚才创建的预约记录，检查created_at字段是否为当前北京时间")

    # 获取当前北京时间，供用户参考
    current_beijing_time = get_beijing_now()
    logger.info(f"当前北京时间: {current_beijing_time}")

if __name__ == "__main__":
    logger.info("开始测试北京时间记录功能")
    test_direct_sql_insert()
    print("\n" + "-" * 50 + "\n")
    # test_through_api()  # 这个测试需要API令牌，可能无法直接运行
    # print("\n" + "-" * 50 + "\n")
    test_manual_reservation()
    logger.info("测试完成")
