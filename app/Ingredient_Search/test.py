import json

src = "保健食品注册.json"          # 原始大 JSON 文件
out1 = "保健食品注册1.json"       # 第一份
out2 = "保健食品备案.json"       # 第二份

with open(src, "r", encoding="utf-8") as f:
    data = json.load(f)   # data 是一个 dict：{name: {path, ingredient}, ...}

keys = list(data.keys())
mid = len(keys) // 2

data1 = {k: data[k] for k in keys[:mid]}
data2 = {k: data[k] for k in keys[mid:]}

with open(out1, "w", encoding="utf-8") as f:
    json.dump(data1, f, ensure_ascii=False, indent=2)

with open(out2, "w", encoding="utf-8") as f:
    json.dump(data2, f, ensure_ascii=False, indent=2)

print(f"切分完成：{out1} {len(data1)}项，{out2} {len(data2)}项")
