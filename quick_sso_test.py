#!/usr/bin/env python3
"""
快速SSO测试
检查登录页面是否显示SSO按钮
"""
import requests
import time

def test_sso_button():
    """测试SSO按钮"""
    try:
        print("🔐 测试SSO按钮显示")
        print("=" * 50)
        
        url = "http://127.0.0.1:5000/login"
        print(f"访问: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 登录页面访问成功")
            
            content = response.text
            
            # 检查SSO相关内容
            checks = [
                ("SSO区域", "sso-section" in content),
                ("SSO按钮", "sso-btn" in content),
                ("SSO登录文本", "使用SSO登录" in content),
                ("SSO路由", "/auth/sso/login" in content),
                ("分隔线", "divider" in content),
                ("条件判断", "{% if sso_enabled %}" not in content)  # 应该已被渲染
            ]
            
            print("\nSSO元素检查:")
            passed = 0
            for name, check in checks:
                if check:
                    print(f"  ✅ {name}: 存在")
                    passed += 1
                else:
                    print(f"  ❌ {name}: 不存在")
            
            print(f"\n检查结果: {passed}/{len(checks)}")
            
            if passed >= 4:
                print("🎉 SSO按钮应该正确显示！")
                return True
            else:
                print("⚠️ SSO按钮可能有问题")
                
                # 显示部分页面内容用于调试
                print("\n页面内容片段:")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'sso' in line.lower() or 'SSO' in line:
                        print(f"  第{i+1}行: {line.strip()}")
                
                return False
        else:
            print(f"❌ 登录页面访问失败: {response.status_code}")
            return False
            
    except requests.ConnectionError:
        print("❌ 无法连接到应用")
        print("请确保应用正在运行: python app.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    # 等待应用启动
    time.sleep(1)
    
    success = test_sso_button()
    
    if success:
        print("\n✅ 测试通过！")
        print("📱 请在浏览器中访问: http://127.0.0.1:5000/login")
        print("🔍 查看是否有蓝色的'使用SSO登录'按钮")
    else:
        print("\n❌ 测试失败！")
        print("🔧 请检查应用配置和模板文件")
    
    input("\n按回车键退出...")
