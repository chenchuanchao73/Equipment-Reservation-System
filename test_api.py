"""
测试后端API是否可访问
"""
import requests
import json

def test_api():
    """测试后端API是否可访问"""
    # 测试健康检查接口
    try:
        response = requests.get('http://localhost:8000/api/health')
        print(f'健康检查接口: {response.status_code}')
        if response.status_code == 200:
            print(f'响应内容: {response.json()}')
    except Exception as e:
        print(f'健康检查接口访问失败: {str(e)}')

    # 测试预约详情接口
    try:
        response = requests.get('http://localhost:8000/api/reservation/code/QOUB7R9F?reservation_number=RN-20250519-8594-5')
        print(f'预约详情接口: {response.status_code}')
        if response.status_code == 200:
            print(f'响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
        else:
            print(f'响应内容: {response.text}')
    except Exception as e:
        print(f'预约详情接口访问失败: {str(e)}')

if __name__ == '__main__':
    test_api()
