#!/usr/bin/env python3
"""
最终登录页面测试
验证SSO按钮是否正确显示
"""
import requests
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_login_page():
    """测试登录页面"""
    logger.info("🔐 测试登录页面")
    logger.info("=" * 60)
    
    try:
        url = "http://localhost:5000/login"
        logger.info(f"访问: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ 登录页面访问成功")
            
            # 检查页面内容
            content = response.text
            
            # 检查关键元素
            checks = [
                ("用户名输入框", 'name="username"' in content),
                ("密码输入框", 'name="password"' in content),
                ("登录按钮", '登录' in content),
                ("SSO区域", 'sso-section' in content),
                ("SSO按钮", 'sso-btn' in content),
                ("使用SSO登录文本", '使用SSO登录' in content),
                ("SSO路由", '/auth/sso/login' in content),
                ("分隔线", 'divider' in content)
            ]
            
            logger.info("页面元素检查:")
            passed = 0
            for name, check in checks:
                if check:
                    logger.info(f"  ✅ {name}: 存在")
                    passed += 1
                else:
                    logger.error(f"  ❌ {name}: 不存在")
            
            logger.info(f"检查结果: {passed}/{len(checks)}")
            
            if passed >= 6:
                logger.info("🎉 登录页面基本正常，SSO按钮应该显示")
                return True
            else:
                logger.warning("⚠️ 登录页面可能有问题")
                return False
                
        else:
            logger.error(f"❌ 登录页面访问失败: {response.status_code}")
            logger.error(f"响应内容: {response.text[:200]}...")
            return False
            
    except requests.ConnectionError:
        logger.error("❌ 无法连接到应用")
        logger.info("请确保应用正在运行: python app.py")
        return False
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


def test_sso_routes():
    """测试SSO路由"""
    logger.info("🔗 测试SSO路由")
    logger.info("=" * 60)
    
    routes = [
        ("/auth/sso/login", "SSO登录"),
        ("/auth/sso/callback", "SSO回调"),
        ("/auth/sso/status", "SSO状态")
    ]
    
    available = 0
    
    for route, name in routes:
        try:
            url = f"http://localhost:5000{route}"
            response = requests.get(url, timeout=5, allow_redirects=False)
            
            # SSO路由应该返回重定向或特定状态码
            if response.status_code in [200, 302, 400, 401]:
                logger.info(f"  ✅ {name} ({route}): 可用 (状态码: {response.status_code})")
                available += 1
            else:
                logger.warning(f"  ⚠️ {name} ({route}): 异常状态码 {response.status_code}")
                
        except Exception as e:
            logger.error(f"  ❌ {name} ({route}): 失败 - {e}")
    
    logger.info(f"可用路由: {available}/{len(routes)}")
    return available >= 2


def test_sso_status_api():
    """测试SSO状态API"""
    logger.info("📊 测试SSO状态API")
    logger.info("=" * 60)
    
    try:
        url = "http://localhost:5000/auth/sso/status"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ SSO状态API响应成功")
            
            logger.info("SSO配置状态:")
            logger.info(f"  启用状态: {data.get('enabled', False)}")
            logger.info(f"  提供者: {data.get('provider', '未知')}")
            logger.info(f"  自动创建用户: {data.get('auto_create_user', False)}")
            logger.info(f"  可用提供者: {data.get('providers', [])}")
            
            return data.get('enabled', False)
        else:
            logger.error(f"❌ SSO状态API失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ SSO状态API测试失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("🎯 最终登录页面测试")
    logger.info("=" * 80)
    
    # 等待应用启动
    logger.info("等待应用启动...")
    time.sleep(2)
    
    tests = [
        ("登录页面", test_login_page),
        ("SSO路由", test_sso_routes),
        ("SSO状态API", test_sso_status_api)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔧 执行测试: {test_name}")
        logger.info("-" * 50)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} - 通过")
                passed += 1
            else:
                logger.error(f"❌ {test_name} - 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    # 总结
    logger.info("=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"通过: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 所有测试通过！")
        logger.info("\n✅ 登录页面应该正常显示SSO按钮")
        logger.info("📱 请在浏览器中访问: http://localhost:5000/login")
        logger.info("🔍 查看是否有蓝色的'使用SSO登录'按钮")
        
        logger.info("\n🔄 SSO登录流程:")
        logger.info("1. 点击'使用SSO登录'按钮")
        logger.info("2. 重定向到Authing认证页面")
        logger.info("3. 完成认证后自动登录")
        
    elif passed >= 2:
        logger.warning("⚠️ 大部分测试通过，基本功能可用")
        logger.info("请检查失败的测试项目")
    else:
        logger.error("❌ 多数测试失败，请检查应用配置")
        
        logger.info("\n🔧 故障排除:")
        logger.info("1. 确保应用正在运行: python app.py")
        logger.info("2. 检查.env配置文件")
        logger.info("3. 清除浏览器缓存")
        logger.info("4. 查看应用日志")
    
    return passed >= 2


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        exit(1)
    except Exception as e:
        logger.error(f"测试执行异常: {e}")
        input("按回车键退出...")
        exit(1)
