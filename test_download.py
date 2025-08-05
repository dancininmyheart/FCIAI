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
    # 先搜索获取数据
    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    
    # 打印响应内容的前500个字符用于调试
    print("Response Content (first 500 chars):", response.text[:500])
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("搜索成功:")
            print(f"总共找到 {data['pagination']['total']} 个产品")
            
            # 检查是否有数据
            if data.get('success') and data.get('data'):
                print("\n搜索到的产品:")
                for i, item in enumerate(data['data']):
                    print(f"{i+1}. {item['产品名称']}")
                    if item.get('截图路径') and item['截图路径'] != '无截图路径':
                        print(f"   图片路径: {item['截图路径']}")
                        
                        # 测试下载链接
                        download_url = f"http://127.0.0.1:5000/ingredient/api/ingredient/download/{item['截图路径']}"
                        print(f"   下载链接: {download_url}")
                        
                        # 尝试下载
                        download_response = requests.get(download_url)
                        print(f"   下载状态: {download_response.status_code}")
                        if download_response.status_code == 200:
                            # 保存文件
                            filename = item['截图路径'].split('/')[-1]  # 获取文件名
                            with open(f"test_{filename}", "wb") as f:
                                f.write(download_response.content)
                            print(f"   文件已保存为: test_{filename}")
                        print()
                    else:
                        print("   无图片")
                        print()
            else:
                print("未找到产品")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print("响应内容:", response.text)
    else:
        print("搜索失败:", response.text)
        
except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
