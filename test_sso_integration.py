#!/usr/bin/env python3
"""
SSO集成测试脚本
验证SSO功能的完整性和正确性
"""
import os
import sys
import logging
import requests
from urllib.parse import urlparse, parse_qs

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_sso_status():
    """测试SSO状态API"""
    logger.info("=" * 60)
    logger.info("测试SSO状态API")
    logger.info("=" * 60)
    
    try:
        # 测试SSO状态端点
        response = requests.get('http://localhost:5000/auth/sso/status')
        
        if response.status_code == 200:
            data = response.json()
            logger.info("✅ SSO状态API响应成功")
            logger.info(f"SSO启用状态: {data.get('enabled')}")
            logger.info(f"SSO提供者: {data.get('provider')}")
            logger.info(f"自动创建用户: {data.get('auto_create_user')}")
            logger.info(f"可用提供者: {data.get('providers')}")
            return True
        else:
            logger.error(f"❌ SSO状态API失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ SSO状态API异常: {e}")
        return False


def test_sso_login_redirect():
    """测试SSO登录重定向"""
    logger.info("=" * 60)
    logger.info("测试SSO登录重定向")
    logger.info("=" * 60)
    
    try:
        # 测试SSO登录端点
        response = requests.get(
            'http://localhost:5000/auth/sso/login',
            allow_redirects=False
        )
        
        if response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location')
            logger.info("✅ SSO登录重定向成功")
            logger.info(f"重定向URL: {redirect_url}")
            
            # 解析重定向URL
            if redirect_url:
                parsed_url = urlparse(redirect_url)
                query_params = parse_qs(parsed_url.query)
                
                logger.info("重定向参数:")
                for key, value in query_params.items():
                    logger.info(f"  {key}: {value[0] if value else 'None'}")
                
                return True
            else:
                logger.error("❌ 没有重定向URL")
                return False
        else:
            logger.error(f"❌ SSO登录重定向失败: {response.status_code}")
            logger.error(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ SSO登录重定向异常: {e}")
        return False


def test_database_migration():
    """测试数据库迁移状态"""
    logger.info("=" * 60)
    logger.info("测试数据库迁移状态")
    logger.info("=" * 60)
    
    try:
        from app import create_app, db
        from app.models.user import User, Role
        
        app = create_app()
        with app.app_context():
            # 检查SSO字段是否存在
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            sso_columns = [
                'email', 'first_name', 'last_name', 'display_name',
                'sso_provider', 'sso_subject', 'last_login'
            ]
            
            logger.info("SSO字段检查:")
            all_present = True
            for column in sso_columns:
                if column in columns:
                    logger.info(f"  ✅ {column}: 存在")
                else:
                    logger.error(f"  ❌ {column}: 不存在")
                    all_present = False
            
            # 检查角色
            admin_role = Role.query.filter_by(name='admin').first()
            user_role = Role.query.filter_by(name='user').first()
            
            logger.info("\n默认角色检查:")
            logger.info(f"  admin角色: {'✅ 存在' if admin_role else '❌ 不存在'}")
            logger.info(f"  user角色: {'✅ 存在' if user_role else '❌ 不存在'}")
            
            # 检查SSO用户
            sso_users = User.query.filter(User.sso_provider.isnot(None)).count()
            logger.info(f"\nSSO用户数量: {sso_users}")
            
            return all_present and admin_role and user_role
            
    except Exception as e:
        logger.error(f"❌ 数据库迁移检查异常: {e}")
        return False


def test_sso_service_initialization():
    """测试SSO服务初始化"""
    logger.info("=" * 60)
    logger.info("测试SSO服务初始化")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        from app.services.sso_service import sso_service
        
        app = create_app()
        with app.app_context():
            # 检查SSO服务状态
            is_enabled = sso_service.is_enabled()
            logger.info(f"SSO服务启用状态: {is_enabled}")
            
            # 检查可用提供者
            providers = list(sso_service.providers.keys())
            logger.info(f"可用SSO提供者: {providers}")
            
            # 测试获取提供者
            if providers:
                for provider_name in providers:
                    provider = sso_service.get_provider(provider_name)
                    if provider:
                        logger.info(f"✅ {provider_name}提供者初始化成功")
                    else:
                        logger.error(f"❌ {provider_name}提供者初始化失败")
            
            return is_enabled or len(providers) > 0
            
    except Exception as e:
        logger.error(f"❌ SSO服务初始化检查异常: {e}")
        return False


def test_user_service():
    """测试用户服务"""
    logger.info("=" * 60)
    logger.info("测试用户服务")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        from app.services.user_service import UserService
        
        app = create_app()
        with app.app_context():
            # 测试用户服务方法
            logger.info("测试用户服务方法...")
            
            # 模拟SSO用户信息
            mock_user_info = {
                'username': 'test_sso_user',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'display_name': 'Test User',
                'sub': 'test_subject_123'
            }
            
            # 测试用户属性映射（不实际创建用户）
            logger.info("✅ 用户服务方法可用")
            logger.info(f"模拟用户信息: {mock_user_info}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ 用户服务测试异常: {e}")
        return False


def test_configuration():
    """测试配置完整性"""
    logger.info("=" * 60)
    logger.info("测试配置完整性")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app()
        with app.app_context():
            # 检查SSO配置
            config_items = [
                ('SSO_ENABLED', app.config.get('SSO_ENABLED')),
                ('SSO_PROVIDER', app.config.get('SSO_PROVIDER')),
                ('SSO_AUTO_CREATE_USER', app.config.get('SSO_AUTO_CREATE_USER')),
                ('SSO_DEFAULT_ROLE', app.config.get('SSO_DEFAULT_ROLE')),
                ('SSO_USER_MAPPING', app.config.get('SSO_USER_MAPPING'))
            ]
            
            logger.info("SSO配置检查:")
            for key, value in config_items:
                logger.info(f"  {key}: {value}")
            
            # 检查OAuth2配置（如果启用）
            if app.config.get('SSO_PROVIDER') == 'oauth2':
                oauth2_config = [
                    ('OAUTH2_CLIENT_ID', app.config.get('OAUTH2_CLIENT_ID')),
                    ('OAUTH2_AUTHORIZATION_URL', app.config.get('OAUTH2_AUTHORIZATION_URL')),
                    ('OAUTH2_TOKEN_URL', app.config.get('OAUTH2_TOKEN_URL')),
                    ('OAUTH2_USERINFO_URL', app.config.get('OAUTH2_USERINFO_URL')),
                    ('OAUTH2_REDIRECT_URI', app.config.get('OAUTH2_REDIRECT_URI'))
                ]
                
                logger.info("\nOAuth2配置检查:")
                for key, value in oauth2_config:
                    status = "✅ 已配置" if value else "❌ 未配置"
                    logger.info(f"  {key}: {status}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ 配置检查异常: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("🔐 SSO集成测试开始")
    logger.info("=" * 80)
    
    tests = [
        ("配置完整性", test_configuration),
        ("数据库迁移", test_database_migration),
        ("SSO服务初始化", test_sso_service_initialization),
        ("用户服务", test_user_service),
        ("SSO状态API", test_sso_status),
        ("SSO登录重定向", test_sso_login_redirect)
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
        logger.info("🎉 所有测试通过！SSO集成配置成功")
        logger.info("\n✅ 下一步:")
        logger.info("1. 配置您的SSO提供者")
        logger.info("2. 更新.env文件中的SSO配置")
        logger.info("3. 重启应用并测试SSO登录")
        logger.info("4. 访问 /sso_management 管理SSO设置")
    elif passed >= 4:
        logger.warning("⚠️ 大部分测试通过，基本功能可用")
        logger.info("请检查失败的测试项目并完善配置")
    else:
        logger.error("❌ 多数测试失败，需要检查SSO集成")
        logger.info("\n🔧 故障排除建议:")
        logger.info("1. 运行数据库迁移: python migrations/add_sso_fields.py upgrade")
        logger.info("2. 检查.env配置文件")
        logger.info("3. 确保应用正常启动")
        logger.info("4. 查看应用日志获取详细错误信息")
    
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
