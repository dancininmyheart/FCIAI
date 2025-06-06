#!/usr/bin/env python3
"""
SSO回调地址检查工具
验证回调地址配置是否正确
"""
import os
import sys
import logging
from urllib.parse import urlparse

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_callback_configuration():
    """检查回调地址配置"""
    logger.info("=" * 60)
    logger.info("SSO回调地址配置检查")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # 获取配置的回调地址
            redirect_uri = app.config.get('OAUTH2_REDIRECT_URI')
            
            if not redirect_uri:
                logger.error("❌ 未配置OAUTH2_REDIRECT_URI")
                return False
            
            logger.info(f"配置的回调地址: {redirect_uri}")
            
            # 解析URL
            parsed = urlparse(redirect_uri)
            
            logger.info("回调地址分析:")
            logger.info(f"  协议: {parsed.scheme}")
            logger.info(f"  域名: {parsed.netloc}")
            logger.info(f"  路径: {parsed.path}")
            
            # 检查路径是否正确
            expected_path = "/auth/sso/callback"
            if parsed.path == expected_path:
                logger.info(f"✅ 回调路径正确: {parsed.path}")
            else:
                logger.error(f"❌ 回调路径错误，应为: {expected_path}")
                return False
            
            # 检查协议
            if parsed.scheme in ['http', 'https']:
                logger.info(f"✅ 协议正确: {parsed.scheme}")
            else:
                logger.error(f"❌ 协议错误，应为http或https: {parsed.scheme}")
                return False
            
            # 生产环境建议使用HTTPS
            if parsed.scheme == 'http' and 'localhost' not in parsed.netloc:
                logger.warning("⚠️ 生产环境建议使用HTTPS协议")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ 配置检查异常: {e}")
        return False


def generate_callback_urls():
    """生成不同环境的回调地址示例"""
    logger.info("=" * 60)
    logger.info("不同环境的回调地址示例")
    logger.info("=" * 60)
    
    environments = [
        ("本地开发", "http://localhost:5000"),
        ("本地开发(其他端口)", "http://localhost:8080"),
        ("测试环境", "http://test.your-company.com"),
        ("预生产环境", "https://staging.your-company.com"),
        ("生产环境", "https://your-company.com"),
        ("生产环境(子域名)", "https://app.your-company.com")
    ]
    
    callback_path = "/auth/sso/callback"
    
    for env_name, base_url in environments:
        full_url = f"{base_url}{callback_path}"
        logger.info(f"{env_name:12}: {full_url}")
    
    logger.info("\n💡 配置提示:")
    logger.info("1. 在SSO提供者中配置上述对应环境的回调地址")
    logger.info("2. 确保.env文件中OAUTH2_REDIRECT_URI与实际环境匹配")
    logger.info("3. 生产环境务必使用HTTPS协议")


def test_callback_route():
    """测试回调路由是否可访问"""
    logger.info("=" * 60)
    logger.info("测试回调路由可访问性")
    logger.info("=" * 60)
    
    try:
        import requests
        
        # 测试回调路由（应该返回错误，因为没有有效参数）
        test_url = "http://localhost:5000/auth/sso/callback"
        
        try:
            response = requests.get(test_url, timeout=5)
            
            if response.status_code in [200, 302, 400]:
                logger.info(f"✅ 回调路由可访问，状态码: {response.status_code}")
                
                # 检查是否重定向到登录页面
                if response.status_code == 302:
                    location = response.headers.get('Location', '')
                    if 'login' in location:
                        logger.info("✅ 正确重定向到登录页面")
                    else:
                        logger.info(f"重定向到: {location}")
                
                return True
            else:
                logger.error(f"❌ 回调路由访问异常，状态码: {response.status_code}")
                return False
                
        except requests.ConnectionError:
            logger.warning("⚠️ 无法连接到应用，请确保应用正在运行")
            logger.info("可以通过以下命令启动应用:")
            logger.info("  python app.py")
            return False
            
    except ImportError:
        logger.warning("⚠️ requests库未安装，跳过路由测试")
        logger.info("可以通过以下命令安装:")
        logger.info("  pip install requests")
        return True
    except Exception as e:
        logger.error(f"❌ 路由测试异常: {e}")
        return False


def show_sso_flow():
    """显示SSO认证流程"""
    logger.info("=" * 60)
    logger.info("SSO认证流程说明")
    logger.info("=" * 60)
    
    flow_steps = [
        "1. 用户访问登录页面",
        "2. 用户点击'SSO登录'按钮",
        "3. 系统重定向到SSO提供者授权页面",
        "   URL: https://sso-provider.com/oauth2/authorize?client_id=xxx&redirect_uri=YOUR_CALLBACK",
        "4. 用户在SSO提供者完成认证",
        "5. SSO提供者重定向回您的回调地址",
        "   URL: YOUR_CALLBACK?code=AUTH_CODE&state=RANDOM_STATE",
        "6. 系统接收到authorization code",
        "7. 系统用code换取access_token",
        "8. 系统用access_token获取用户信息",
        "9. 系统创建/更新用户账户",
        "10. 用户登录成功"
    ]
    
    for step in flow_steps:
        if step.startswith("   "):
            logger.info(f"    {step[3:]}")
        else:
            logger.info(step)
    
    logger.info("\n🔑 关键点:")
    logger.info("• 回调地址必须与SSO提供者配置完全一致")
    logger.info("• 回调地址必须是您系统的有效路由")
    logger.info("• 生产环境必须使用HTTPS")
    logger.info("• state参数用于防止CSRF攻击")


def main():
    """主函数"""
    logger.info("🔄 SSO回调地址检查工具")
    logger.info("=" * 80)
    
    tests = [
        ("回调地址配置检查", check_callback_configuration),
        ("回调路由测试", test_callback_route)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔧 执行: {test_name}")
        logger.info("-" * 50)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} - 通过")
                passed += 1
            else:
                logger.error(f"❌ {test_name} - 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    # 显示额外信息
    logger.info("")
    generate_callback_urls()
    logger.info("")
    show_sso_flow()
    
    # 总结
    logger.info("=" * 80)
    logger.info("检查总结")
    logger.info("=" * 80)
    logger.info(f"通过: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 回调地址配置正确！")
        logger.info("\n✅ 下一步:")
        logger.info("1. 在SSO提供者中配置回调地址")
        logger.info("2. 测试完整的SSO登录流程")
    else:
        logger.warning("⚠️ 请检查失败的项目")
        logger.info("\n🔧 故障排除:")
        logger.info("1. 检查.env文件中的OAUTH2_REDIRECT_URI配置")
        logger.info("2. 确保应用正常启动")
        logger.info("3. 验证路由配置正确")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("检查被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"检查执行异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
