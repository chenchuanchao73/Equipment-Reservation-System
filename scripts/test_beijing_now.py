"""
测试BeijingNow函数
Test BeijingNow function
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
from backend.utils.db_utils import BeijingNow, get_beijing_now
from sqlalchemy import create_engine, Column, Integer, String, DateTime, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建一个内存数据库用于测试
engine = create_engine('sqlite:///:memory:')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# 定义一个测试模型
class TestModel(Base):
    __tablename__ = 'test_model'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=BeijingNow(), nullable=False)
    
    def __repr__(self):
        return f"<TestModel(id={self.id}, name='{self.name}', created_at='{self.created_at}')>"

def test_beijing_now_function():
    """测试BeijingNow函数"""
    logger.info("测试BeijingNow函数")
    
    # 创建表
    Base.metadata.create_all(engine)
    
    # 获取当前北京时间
    current_beijing_time = get_beijing_now()
    current_utc_time = datetime.now(timezone.utc)
    
    logger.info(f"当前北京时间: {current_beijing_time}")
    logger.info(f"当前UTC时间: {current_utc_time}")
    logger.info(f"时差（小时）: {(current_beijing_time - current_utc_time.replace(tzinfo=None)).total_seconds() / 3600}")
    
    # 创建会话
    session = Session()
    
    try:
        # 创建一个新记录
        test_record = TestModel(name=f"test_{int(datetime.now().timestamp())}")
        session.add(test_record)
        session.commit()
        
        # 刷新记录以获取最新数据
        session.refresh(test_record)
        
        # 检查created_at时间戳
        created_at = test_record.created_at
        logger.info(f"数据库记录的created_at: {created_at}")
        
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
        logger.error(f"测试过程中出错: {str(e)}")
        session.rollback()
    finally:
        session.close()

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
    logger.info("开始测试BeijingNow函数")
    test_beijing_now_function()
    print("\n" + "-" * 50 + "\n")
    test_manual_reservation()
    logger.info("测试完成")
