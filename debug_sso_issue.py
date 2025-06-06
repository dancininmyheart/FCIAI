#!/usr/bin/env python3
"""
调试SSO问题
检查为什么SSO未启用和按钮不显示
"""
import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def debug_env_loading():
    """调试环境变量加载"""
    logger.info("=" * 60)
    logger.info("调试环境变量加载")
    logger.info("=" * 60)
    
    # 加载.env文件
    load_dotenv()
    
    sso_vars = [
        'SSO_ENABLED',
        'SSO_PROVIDER', 
        'OAUTH2_CLIENT_ID',
        'OAUTH2_CLIENT_SECRET',
        'OAUTH2_AUTHORIZATION_URL',
        'OAUTH2_TOKEN_URL',
        'OAUTH2_USERINFO_URL',
        'OAUTH2_REDIRECT_URI'
    ]
    
    logger.info("环境变量检查:")
    for var in sso_vars:
        value = os.getenv(var)
        if var == 'OAUTH2_CLIENT_SECRET':
            display_value = f"{value[:10]}..." if value and len(value) > 10 else value
        else:
            display_value = value
        logger.info(f"  {var}: {display_value}")
    
    return all(os.getenv(var) for var in sso_vars[:4])  # 检查关键变量


def debug_flask_config():
    """调试Flask配置"""
    logger.info("=" * 60)
    logger.info("调试Flask配置")
    logger.info("=" * 60)
    
    try:
        from flask import Flask
        from dotenv import load_dotenv
        
        # 加载环境变量
        load_dotenv()
        
        app = Flask(__name__, template_folder='app/templates')
        
        # 模拟app.py中的配置加载
        app.config['SSO_ENABLED'] = os.getenv('SSO_ENABLED', 'false').lower() == 'true'
        app.config['SSO_PROVIDER'] = os.getenv('SSO_PROVIDER', 'oauth2')
        app.config['OAUTH2_CLIENT_ID'] = os.getenv('OAUTH2_CLIENT_ID', '')
        app.config['OAUTH2_CLIENT_SECRET'] = os.getenv('OAUTH2_CLIENT_SECRET', '')
        app.config['OAUTH2_AUTHORIZATION_URL'] = os.getenv('OAUTH2_AUTHORIZATION_URL', '')
        app.config['OAUTH2_TOKEN_URL'] = os.getenv('OAUTH2_TOKEN_URL', '')
        app.config['OAUTH2_USERINFO_URL'] = os.getenv('OAUTH2_USERINFO_URL', '')
        app.config['OAUTH2_LOGOUT_URL'] = os.getenv('OAUTH2_LOGOUT_URL', '')
        app.config['OAUTH2_SCOPE'] = os.getenv('OAUTH2_SCOPE', 'openid profile email')
        app.config['OAUTH2_REDIRECT_URI'] = os.getenv('OAUTH2_REDIRECT_URI', '')
        
        logger.info("Flask配置:")
        sso_configs = [
            'SSO_ENABLED',
            'SSO_PROVIDER',
            'OAUTH2_CLIENT_ID',
            'OAUTH2_AUTHORIZATION_URL'
        ]
        
        for config in sso_configs:
            value = app.config.get(config)
            logger.info(f"  {config}: {value}")
        
        return app
        
    except Exception as e:
        logger.error(f"Flask配置失败: {e}")
        return None


def debug_sso_service(app):
    """调试SSO服务"""
    logger.info("=" * 60)
    logger.info("调试SSO服务")
    logger.info("=" * 60)
    
    try:
        with app.app_context():
            from app.services.sso_service import get_sso_service
            
            logger.info("获取SSO服务实例...")
            sso_service = get_sso_service()
            
            logger.info("检查SSO服务状态...")
            is_enabled = sso_service.is_enabled()
            logger.info(f"SSO启用状态: {is_enabled}")
            
            logger.info("强制初始化SSO服务...")
            sso_service._ensure_initialized()
            
            logger.info("检查提供者...")
            providers = list(sso_service.providers.keys())
            logger.info(f"可用提供者: {providers}")
            
            if providers:
                for provider_name in providers:
                    provider = sso_service.get_provider(provider_name)
                    if provider:
                        logger.info(f"✅ {provider_name}提供者: 已初始化")
                        
                        # 尝试生成授权URL
                        try:
                            auth_url = provider.get_authorization_url()
                            logger.info(f"授权URL: {auth_url[:100]}...")
                        except Exception as e:
                            logger.error(f"生成授权URL失败: {e}")
                    else:
                        logger.error(f"❌ {provider_name}提供者: 初始化失败")
            
            return is_enabled
            
    except Exception as e:
        logger.error(f"SSO服务调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def debug_login_template():
    """调试登录模板"""
    logger.info("=" * 60)
    logger.info("调试登录模板")
    logger.info("=" * 60)
    
    try:
        template_path = "app/templates/auth/login.html"
        
        if os.path.exists(template_path):
            logger.info(f"✅ 模板文件存在: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键元素
            checks = [
                ("SSO条件判断", "{% if sso_enabled %}" in content),
                ("SSO区域", "sso-section" in content),
                ("SSO按钮", "sso-btn" in content),
                ("SSO登录文本", "使用SSO登录" in content),
                ("SSO路由", "/auth/sso/login" in content),
                ("分隔线", "divider" in content)
            ]
            
            logger.info("模板元素检查:")
            all_present = True
            for name, check in checks:
                if check:
                    logger.info(f"  ✅ {name}: 存在")
                else:
                    logger.error(f"  ❌ {name}: 不存在")
                    all_present = False
            
            return all_present
        else:
            logger.error(f"❌ 模板文件不存在: {template_path}")
            return False
            
    except Exception as e:
        logger.error(f"模板调试失败: {e}")
        return False


def debug_login_view():
    """调试登录视图"""
    logger.info("=" * 60)
    logger.info("调试登录视图")
    logger.info("=" * 60)
    
    try:
        app = debug_flask_config()
        if not app:
            return False
        
        with app.app_context():
            # 模拟登录视图中的SSO状态获取
            try:
                from app.services.sso_service import get_sso_service
                sso_service = get_sso_service()
                sso_enabled = sso_service.is_enabled()
                sso_provider = app.config.get('SSO_PROVIDER', 'oauth2')
                
                logger.info("登录视图SSO状态:")
                logger.info(f"  sso_enabled: {sso_enabled}")
                logger.info(f"  sso_provider: {sso_provider}")
                
                if sso_enabled:
                    logger.info("✅ SSO按钮应该显示")
                else:
                    logger.error("❌ SSO按钮不会显示")
                
                return sso_enabled
                
            except Exception as e:
                logger.error(f"SSO状态获取失败: {e}")
                logger.info("使用默认值:")
                logger.info("  sso_enabled: False")
                logger.info("  sso_provider: oauth2")
                return False
                
    except Exception as e:
        logger.error(f"登录视图调试失败: {e}")
        return False


def test_direct_access():
    """测试直接访问登录页面"""
    logger.info("=" * 60)
    logger.info("测试直接访问登录页面")
    logger.info("=" * 60)
    
    try:
        import requests
        
        url = "http://localhost:5000/login"
        logger.info(f"访问: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ 登录页面访问成功")
            
            content = response.text
            
            # 检查SSO相关内容
            if "sso-section" in content:
                logger.info("✅ 页面包含SSO区域")
            else:
                logger.error("❌ 页面不包含SSO区域")
            
            if "使用SSO登录" in content:
                logger.info("✅ 页面包含SSO登录文本")
            else:
                logger.error("❌ 页面不包含SSO登录文本")
            
            # 检查是否有条件判断的痕迹
            if "{% if sso_enabled %}" in content:
                logger.warning("⚠️ 页面包含未渲染的Jinja2模板代码")
            
            return True
        else:
            logger.error(f"❌ 登录页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"直接访问测试失败: {e}")
        return False


def main():
    """主调试函数"""
    logger.info("🔍 SSO问题调试工具")
    logger.info("=" * 80)
    
    tests = [
        ("环境变量加载", debug_env_loading),
        ("登录模板检查", debug_login_template),
        ("直接访问测试", test_direct_access)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔧 执行调试: {test_name}")
        logger.info("-" * 50)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} - 正常")
                passed += 1
            else:
                logger.error(f"❌ {test_name} - 异常")
        except Exception as e:
            logger.error(f"❌ {test_name} - 错误: {e}")
    
    # Flask应用相关测试
    logger.info(f"\n🔧 执行调试: Flask配置")
    logger.info("-" * 50)
    app = debug_flask_config()
    if app:
        logger.info("✅ Flask配置 - 正常")
        passed += 1
        
        logger.info(f"\n🔧 执行调试: SSO服务")
        logger.info("-" * 50)
        if debug_sso_service(app):
            logger.info("✅ SSO服务 - 正常")
            passed += 1
        else:
            logger.error("❌ SSO服务 - 异常")
        
        logger.info(f"\n🔧 执行调试: 登录视图")
        logger.info("-" * 50)
        if debug_login_view():
            logger.info("✅ 登录视图 - 正常")
            passed += 1
        else:
            logger.error("❌ 登录视图 - 异常")
    else:
        logger.error("❌ Flask配置 - 异常")
    
    total += 3  # 添加了3个额外测试
    
    # 总结
    logger.info("=" * 80)
    logger.info("调试总结")
    logger.info("=" * 80)
    logger.info(f"正常: {passed}/{total}")
    
    if passed >= 5:
        logger.info("🎉 大部分功能正常，可能是小问题")
    elif passed >= 3:
        logger.warning("⚠️ 部分功能异常，需要修复")
    else:
        logger.error("❌ 多数功能异常，需要全面检查")
    
    return passed >= 3


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("调试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"调试执行异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
