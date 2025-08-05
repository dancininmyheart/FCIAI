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
    print("Response:")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Error: {e}")
