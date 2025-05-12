import requests
import json
from datetime import datetime
import sys

def test_reservation_api(reservation_code, test_dates):
    """测试预约API在不同日期下的行为
    
    Args:
        reservation_code: 预约码
        test_dates: 测试日期列表，每个元素为yyyy-mm-dd格式的字符串
    """
    base_url = "http://localhost:8000/api/reservation/code"
    
    print(f"测试预约码 {reservation_code} 在不同日期下的API响应")
    print("-" * 50)
    
    for date in test_dates:
        # 构建开始和结束时间（假设开始时间为16:19，结束时间为16:20）
        start_time = f"{date} 16:19:00"
        end_time = f"{date} 16:20:00"
        
        # 构建API URL（使用params参数而不是直接拼接URL）
        url = f"{base_url}/{reservation_code}"
        params = {
            "start_time": start_time,
            "end_time": end_time
        }
        
        print(f"测试日期: {date}")
        print(f"API URL: {url}")
        print(f"请求参数: {params}")
        
        try:
            # 发送请求
            response = requests.get(url, params=params)
            
            # 检查请求是否成功
            if response.status_code == 200:
                data = response.json()
                
                # 检查API是否成功
                if data.get("success"):
                    reservation = data.get("data", {})
                    
                    # 提取关键信息
                    status = reservation.get("status")
                    date_matches = reservation.get("date_matches", False)
                    exact_datetime_matches = reservation.get("exact_datetime_matches", False)
                    
                    # 查看原始时间
                    original_start = reservation.get("original_start_datetime", "未知")
                    if isinstance(original_start, str) and "T" in original_start:
                        original_start = original_start.split("T")[0]
                    
                    # 查看当前返回的实际时间
                    res_start = reservation.get("start_datetime", "未知")
                    if isinstance(res_start, str) and "T" in res_start:
                        res_start = res_start.split("T")[0]
                    
                    # 打印结果
                    print(f"状态: {status}")
                    print(f"日期是否匹配: {date_matches}")
                    print(f"时间是否精确匹配: {exact_datetime_matches}")
                    print(f"查询日期: {date}")
                    print(f"返回日期: {res_start}")
                    
                    # 显示调试信息（如果有）
                    debug_info = reservation.get("debug_info", {})
                    if debug_info:
                        print(f"日期比较信息:")
                        print(f"  - 查询日期: {debug_info.get('query_date')}")
                        print(f"  - 预约日期: {debug_info.get('reservation_date')}")
                        print(f"  - 日期相等: {debug_info.get('dates_equal')}")
                        print(f"  - 查询星期几: {debug_info.get('weekday_query')}")
                        print(f"  - 预约星期几: {debug_info.get('res_weekday')}")
                    
                    if date_matches:
                        if exact_datetime_matches:
                            print("✅ 成功：找到精确时间匹配的预约")
                        else:
                            print("✅ 成功：找到日期匹配的预约（时间可能不匹配）")
                    else:
                        print("⚠️ 警告：未找到精确匹配的预约，返回了其他日期记录")
                else:
                    print(f"❌ 错误: {data.get('message', '未知错误')}")
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    # 默认测试预约码
    reservation_code = "SNPXSUQW"
    
    # 可以从命令行传入预约码
    if len(sys.argv) > 1:
        reservation_code = sys.argv[1]
    
    # 测试日期（包括已知的已取消日期和已确认日期）
    test_dates = [
        "2025-04-28",  # 已知被取消的日期
        "2025-04-30",  # 正常预约日期
        "2025-05-26",  # 问题中提到的日期
        "2025-05-27",  # 循环预约结束日期（可能不存在记录）
        "2025-04-29",  # 非预约日期（周二，不在循环周期内）
    ]
    
    # 执行测试
    test_reservation_api(reservation_code, test_dates)