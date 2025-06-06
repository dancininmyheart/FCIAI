#!/usr/bin/env python3
"""
测试SSO登录页面
验证登录页面是否显示SSO登录按钮
"""
import os
import sys
import logging
import requests
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_login_page_access():
    """测试登录页面访问"""
    logger.info("=" * 60)
    logger.info("测试登录页面访问")
    logger.info("=" * 60)
    
    try:
        url = "http://localhost:5000/auth/login"
        logger.info(f"访问登录页面: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ 登录页面访问成功")
            return response.text
        else:
            logger.error(f"❌ 登录页面访问失败: {response.status_code}")
            return None
            
    except requests.ConnectionError:
        logger.error("❌ 无法连接到应用，请确保应用正在运行")
        logger.info("启动应用: python app.py")
        return None
    except Exception as e:
        logger.error(f"❌ 登录页面访问异常: {e}")
        return None


def test_sso_button_presence(html_content):
    """测试SSO按钮是否存在"""
    logger.info("=" * 60)
    logger.info("测试SSO按钮是否存在")
    logger.info("=" * 60)
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找SSO相关元素
        sso_section = soup.find('div', class_='sso-section')
        sso_button = soup.find('a', class_='sso-btn')
        sso_text = soup.find('span', class_='sso-text')
        
        logger.info("SSO元素检查:")
        
        if sso_section:
            logger.info("  ✅ SSO区域 (.sso-section): 存在")
        else:
            logger.error("  ❌ SSO区域 (.sso-section): 不存在")
        
        if sso_button:
            logger.info("  ✅ SSO按钮 (.sso-btn): 存在")
            href = sso_button.get('href', '')
            logger.info(f"    按钮链接: {href}")
        else:
            logger.error("  ❌ SSO按钮 (.sso-btn): 不存在")
        
        if sso_text:
            logger.info("  ✅ SSO文本 (.sso-text): 存在")
            text_content = sso_text.get_text(strip=True)
            logger.info(f"    按钮文本: {text_content}")
        else:
            logger.error("  ❌ SSO文本 (.sso-text): 不存在")
        
        # 检查是否有"使用SSO登录"文本
        if "使用SSO登录" in html_content:
            logger.info("  ✅ 包含'使用SSO登录'文本")
        else:
            logger.error("  ❌ 不包含'使用SSO登录'文本")
        
        # 检查是否有分隔线
        divider = soup.find('div', class_='divider')
        if divider:
            logger.info("  ✅ 分隔线 (.divider): 存在")
        else:
            logger.error("  ❌ 分隔线 (.divider): 不存在")
        
        return bool(sso_section and sso_button and sso_text)
        
    except Exception as e:
        logger.error(f"❌ HTML解析失败: {e}")
        return False


def test_sso_route_availability():
    """测试SSO路由可用性"""
    logger.info("=" * 60)
    logger.info("测试SSO路由可用性")
    logger.info("=" * 60)
    
    sso_routes = [
        "/auth/sso/login",
        "/auth/sso/callback",
        "/auth/sso/status"
    ]
    
    available_routes = 0
    
    for route in sso_routes:
        try:
            url = f"http://localhost:5000{route}"
            logger.info(f"测试路由: {route}")
            
            response = requests.get(url, timeout=5, allow_redirects=False)
            
            # 对于SSO路由，我们期望重定向或特定的响应
            if response.status_code in [200, 302, 400, 401]:
                logger.info(f"  ✅ {route}: 可用 (状态码: {response.status_code})")
                available_routes += 1
            else:
                logger.warning(f"  ⚠️ {route}: 异常状态码 {response.status_code}")
                
        except Exception as e:
            logger.error(f"  ❌ {route}: 访问失败 - {e}")
    
    logger.info(f"可用路由: {available_routes}/{len(sso_routes)}")
    return available_routes >= 2


def test_sso_configuration():
    """测试SSO配置状态"""
    logger.info("=" * 60)
    logger.info("测试SSO配置状态")
    logger.info("=" * 60)
    
    try:
        url = "http://localhost:5000/auth/sso/status"
        logger.info(f"获取SSO状态: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ SSO状态API响应成功")
            
            logger.info("SSO配置状态:")
            logger.info(f"  启用状态: {data.get('enabled', False)}")
            logger.info(f"  提供者: {data.get('provider', '未知')}")
            logger.info(f"  自动创建用户: {data.get('auto_create_user', False)}")
            
            return data.get('enabled', False)
        else:
            logger.error(f"❌ SSO状态API失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ SSO状态检查失败: {e}")
        return False


def analyze_html_structure(html_content):
    """分析HTML结构"""
    logger.info("=" * 60)
    logger.info("分析HTML结构")
    logger.info("=" * 60)
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有相关的类和ID
        logger.info("页面结构分析:")
        
        # 查找表单
        forms = soup.find_all('form')
        logger.info(f"  表单数量: {len(forms)}")
        
        # 查找所有按钮和链接
        buttons = soup.find_all(['button', 'a'])
        logger.info(f"  按钮/链接数量: {len(buttons)}")
        
        for i, btn in enumerate(buttons):
            classes = btn.get('class', [])
            href = btn.get('href', '')
            text = btn.get_text(strip=True)
            logger.info(f"    {i+1}. 类: {classes}, 链接: {href}, 文本: {text[:30]}...")
        
        # 查找所有包含"sso"的元素
        sso_elements = soup.find_all(lambda tag: tag.get('class') and 
                                   any('sso' in str(cls).lower() for cls in tag.get('class')))
        logger.info(f"  SSO相关元素: {len(sso_elements)}")
        
        for elem in sso_elements:
            logger.info(f"    标签: {elem.name}, 类: {elem.get('class')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ HTML结构分析失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("🔐 SSO登录页面测试工具")
    logger.info("=" * 80)
    
    # 测试步骤
    tests = [
        ("SSO配置状态", test_sso_configuration),
        ("SSO路由可用性", test_sso_route_availability)
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
    
    # 测试登录页面
    logger.info(f"\n🔧 执行测试: 登录页面访问")
    logger.info("-" * 50)
    
    html_content = test_login_page_access()
    if html_content:
        logger.info("✅ 登录页面访问 - 通过")
        passed += 1
        
        # 分析HTML结构
        logger.info(f"\n🔧 执行测试: HTML结构分析")
        logger.info("-" * 50)
        if analyze_html_structure(html_content):
            logger.info("✅ HTML结构分析 - 通过")
            passed += 1
        
        # 测试SSO按钮
        logger.info(f"\n🔧 执行测试: SSO按钮检查")
        logger.info("-" * 50)
        if test_sso_button_presence(html_content):
            logger.info("✅ SSO按钮检查 - 通过")
            passed += 1
        else:
            logger.error("❌ SSO按钮检查 - 失败")
    else:
        logger.error("❌ 登录页面访问 - 失败")
    
    total += 3  # 添加了3个额外测试
    
    # 总结
    logger.info("=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"通过: {passed}/{total}")
    
    if passed >= 4:
        logger.info("🎉 SSO登录页面基本功能正常！")
        logger.info("\n✅ 下一步:")
        logger.info("1. 在浏览器中访问: http://localhost:5000/auth/login")
        logger.info("2. 查看是否显示'使用SSO登录'按钮")
        logger.info("3. 点击按钮测试SSO登录流程")
    elif passed >= 2:
        logger.warning("⚠️ 部分功能正常，请检查失败的测试")
    else:
        logger.error("❌ 多数测试失败，请检查应用配置")
    
    return passed >= 4


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试执行异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
