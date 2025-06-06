#!/usr/bin/env python3
"""
LibreOffice UNO包装脚本
自动配置UNO环境并导入必要模块
"""
import sys
import os

# 添加LibreOffice UNO路径
UNO_PATH = r"C:\Program Files\LibreOffice\program"
if UNO_PATH not in sys.path:
    sys.path.insert(0, UNO_PATH)

# 设置环境变量
if os.name == "nt":  # Windows
    os.environ["PATH"] = UNO_PATH + os.pathsep + os.environ.get("PATH", "")
else:  # Linux/macOS
    os.environ["PYTHONPATH"] = UNO_PATH + os.pathsep + os.environ.get("PYTHONPATH", "")

# 导入UNO模块
try:
    import uno
    from com.sun.star.beans import PropertyValue
    from com.sun.star.connection import NoConnectException
    from com.sun.star.lang import DisposedException
    
    print("✅ LibreOffice UNO模块加载成功")
    UNO_AVAILABLE = True
    
except ImportError as e:
    print(f"❌ LibreOffice UNO模块加载失败: {e}")
    UNO_AVAILABLE = False

if __name__ == "__main__":
    if UNO_AVAILABLE:
        print("LibreOffice UNO环境配置成功！")
        print(f"UNO路径: {UNO_PATH}")
    else:
        print("LibreOffice UNO环境配置失败！")
