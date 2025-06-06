#!/usr/bin/env python3
"""
简单的SSO测试
检查SSO配置和登录页面
"""
import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_sso_config():
    """测试SSO配置"""
    logger.info("=" * 60)
    logger.info("测试SSO配置")
    logger.info("=" * 60)
    
    # 加载环境变量
    load_dotenv()
    
    sso_configs = {
        'SSO_ENABLED': os.getenv('SSO_ENABLED'),
        'SSO_PROVIDER': os.getenv('SSO_PROVIDER'),
        'OAUTH2_CLIENT_ID': os.getenv('OAUTH2_CLIENT_ID'),
        'OAUTH2_AUTHORIZATION_URL': os.getenv('OAUTH2_AUTHORIZATION_URL'),
        'OAUTH2_REDIRECT_URI': os.getenv('OAUTH2_REDIRECT_URI')
    }
    
    logger.info("SSO配置检查:")
    all_configured = True
    
    for key, value in sso_configs.items():
        if value:
            if 'SECRET' in key:
                display_value = f"{value[:10]}..." if len(value) > 10 else value
            else:
                display_value = value
            logger.info(f"  ✅ {key}: {display_value}")
        else:
            logger.error(f"  ❌ {key}: 未配置")
            all_configured = False
    
    return all_configured


def test_sso_service():
    """测试SSO服务"""
    logger.info("=" * 60)
    logger.info("测试SSO服务")
    logger.info("=" * 60)
    
    try:
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            from app.services.sso_service import get_sso_service
            
            sso_service = get_sso_service()
            
            # 检查SSO服务状态
            is_enabled = sso_service.is_enabled()
            logger.info(f"SSO启用状态: {is_enabled}")
            
            # 强制初始化
            sso_service._ensure_initialized()
            
            # 检查提供者
            providers = list(sso_service.providers.keys())
            logger.info(f"可用提供者: {providers}")
            
            if providers:
                for provider_name in providers:
                    provider = sso_service.get_provider(provider_name)
                    if provider:
                        logger.info(f"✅ {provider_name}提供者: 已初始化")
                    else:
                        logger.error(f"❌ {provider_name}提供者: 初始化失败")
            
            return is_enabled and len(providers) > 0
            
    except Exception as e:
        logger.error(f"❌ SSO服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_login_template_variables():
    """测试登录模板变量"""
    logger.info("=" * 60)
    logger.info("测试登录模板变量")
    logger.info("=" * 60)
    
    try:
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            from app.services.sso_service import get_sso_service
            
            # 模拟登录视图中的逻辑
            try:
                sso_service = get_sso_service()
                sso_enabled = sso_service.is_enabled()
                sso_provider = app.config.get('SSO_PROVIDER', 'oauth2')
            except Exception:
                sso_enabled = False
                sso_provider = 'oauth2'
            
            logger.info("登录模板变量:")
            logger.info(f"  sso_enabled: {sso_enabled}")
            logger.info(f"  sso_provider: {sso_provider}")
            
            if sso_enabled:
                logger.info("✅ SSO按钮应该显示")
            else:
                logger.warning("⚠️ SSO按钮不会显示")
            
            return sso_enabled
            
    except Exception as e:
        logger.error(f"❌ 模板变量测试失败: {e}")
        return False


def test_sso_routes():
    """测试SSO路由注册"""
    logger.info("=" * 60)
    logger.info("测试SSO路由注册")
    logger.info("=" * 60)
    
    try:
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        # 注册蓝图
        from app.views.sso_auth import sso_bp
        app.register_blueprint(sso_bp)
        
        with app.app_context():
            # 获取所有路由
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(str(rule))
            
            sso_routes = [route for route in routes if '/auth/sso' in route]
            
            logger.info("SSO路由:")
            for route in sso_routes:
                logger.info(f"  ✅ {route}")
            
            expected_routes = ['/auth/sso/login', '/auth/sso/callback', '/auth/sso/status']
            found_routes = []
            
            for expected in expected_routes:
                if any(expected in route for route in sso_routes):
                    found_routes.append(expected)
                    logger.info(f"  ✅ {expected}: 已注册")
                else:
                    logger.error(f"  ❌ {expected}: 未注册")
            
            return len(found_routes) >= 2
            
    except Exception as e:
        logger.error(f"❌ 路由测试失败: {e}")
        return False


def generate_sso_login_url():
    """生成SSO登录URL"""
    logger.info("=" * 60)
    logger.info("生成SSO登录URL")
    logger.info("=" * 60)
    
    try:
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            from app.services.sso_service import get_sso_service
            
            sso_service = get_sso_service()
            sso_service._ensure_initialized()
            
            if sso_service.is_enabled():
                provider = sso_service.get_provider()
                if provider:
                    auth_url = provider.get_authorization_url()
                    logger.info(f"SSO授权URL: {auth_url[:100]}...")
                    return True
                else:
                    logger.error("❌ 无法获取SSO提供者")
                    return False
            else:
                logger.warning("⚠️ SSO未启用")
                return False
                
    except Exception as e:
        logger.error(f"❌ URL生成失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("🔐 简单SSO测试")
    logger.info("=" * 80)
    
    tests = [
        ("SSO配置", test_sso_config),
        ("SSO服务", test_sso_service),
        ("登录模板变量", test_login_template_variables),
        ("SSO路由", test_sso_routes),
        ("SSO登录URL", generate_sso_login_url)
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
    
    if passed >= 4:
        logger.info("🎉 SSO基本功能正常！")
        logger.info("\n✅ 检查登录页面:")
        logger.info("1. 访问: http://localhost:5000/auth/login")
        logger.info("2. 查看是否有'使用SSO登录'按钮")
        logger.info("3. 如果没有按钮，可能是模板缓存问题")
        
        logger.info("\n🔧 故障排除:")
        logger.info("1. 重启应用: Ctrl+C 然后 python app.py")
        logger.info("2. 清除浏览器缓存")
        logger.info("3. 检查浏览器开发者工具的控制台")
        
    elif passed >= 2:
        logger.warning("⚠️ 部分功能正常，请检查失败的测试")
    else:
        logger.error("❌ 多数测试失败，请检查配置")
    
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
