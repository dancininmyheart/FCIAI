import requests
import json

# 测试成分搜索API
url = "http://127.0.0.1:5000/ingredient/api/ingredient/search"
params = {
    "keyword": "维生素",
    "page": 1,
    "per_page": 5
}

try:
    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    
    # 打印原始响应内容
    print("Response Content:", response.text[:500])  # 只打印前500个字符
    
    # 尝试解析JSON
    try:
        data = response.json()
        print("Parsed JSON:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 检查是否有数据
        if data.get('success') and data.get('data'):
            print("\n搜索到的产品:")
            for item in data['data']:
                print(f"- {item['产品名称']}")
                if item.get('截图路径') and item['截图路径'] != '无截图路径':
                    print(f"  图片路径: {item['截图路径']}")
                    # 测试下载链接
                    download_url = f"http://127.0.0.1:5000/ingredient/api/ingredient/download/{item['截图路径']}"
                    print(f"  下载链接: {download_url}")
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print("响应内容不是有效的JSON格式")
        
except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
