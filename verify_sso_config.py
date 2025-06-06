#!/usr/bin/env python3
"""
验证.env文件中的SSO配置
确认所有必需的SSO配置项都已正确设置
"""
import os
import sys
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_env_config():
    """加载.env配置文件"""
    logger.info("=" * 60)
    logger.info("加载.env配置文件")
    logger.info("=" * 60)
    
    try:
        # 加载.env文件
        load_dotenv()
        logger.info("✅ .env文件加载成功")
        return True
    except Exception as e:
        logger.error(f"❌ .env文件加载失败: {e}")
        return False


def verify_basic_sso_config():
    """验证基础SSO配置"""
    logger.info("=" * 60)
    logger.info("验证基础SSO配置")
    logger.info("=" * 60)
    
    basic_configs = {
        'SSO_ENABLED': os.getenv('SSO_ENABLED'),
        'SSO_PROVIDER': os.getenv('SSO_PROVIDER'),
        'SSO_AUTO_CREATE_USER': os.getenv('SSO_AUTO_CREATE_USER'),
        'SSO_DEFAULT_ROLE': os.getenv('SSO_DEFAULT_ROLE')
    }
    
    logger.info("基础SSO配置:")
    all_present = True
    
    for key, value in basic_configs.items():
        if value:
            logger.info(f"  ✅ {key}: {value}")
        else:
            logger.error(f"  ❌ {key}: 未配置")
            all_present = False
    
    # 验证SSO是否启用
    if basic_configs['SSO_ENABLED'] == 'true':
        logger.info("✅ SSO已启用")
    else:
        logger.warning("⚠️ SSO未启用")
    
    return all_present


def verify_authing_config():
    """验证Authing配置"""
    logger.info("=" * 60)
    logger.info("验证Authing配置")
    logger.info("=" * 60)
    
    authing_configs = {
        'OAUTH2_CLIENT_ID': os.getenv('OAUTH2_CLIENT_ID'),
        'OAUTH2_CLIENT_SECRET': os.getenv('OAUTH2_CLIENT_SECRET'),
        'OAUTH2_AUTHORIZATION_URL': os.getenv('OAUTH2_AUTHORIZATION_URL'),
        'OAUTH2_TOKEN_URL': os.getenv('OAUTH2_TOKEN_URL'),
        'OAUTH2_USERINFO_URL': os.getenv('OAUTH2_USERINFO_URL'),
        'OAUTH2_REDIRECT_URI': os.getenv('OAUTH2_REDIRECT_URI'),
        'OAUTH2_SCOPE': os.getenv('OAUTH2_SCOPE')
    }
    
    logger.info("Authing OAuth2配置:")
    all_present = True
    
    for key, value in authing_configs.items():
        if value:
            # 对于敏感信息只显示部分内容
            if 'SECRET' in key:
                display_value = f"{value[:10]}..." if len(value) > 10 else value
            else:
                display_value = value
            logger.info(f"  ✅ {key}: {display_value}")
        else:
            logger.error(f"  ❌ {key}: 未配置")
            all_present = False
    
    # 验证特定配置
    client_id = authing_configs['OAUTH2_CLIENT_ID']
    if client_id == '683ebc2889ae4d4c1ff7e111':
        logger.info("✅ 使用FCI AI翻译助手UAT应用ID")
    elif client_id:
        logger.info(f"ℹ️ 使用自定义应用ID: {client_id}")
    
    redirect_uri = authing_configs['OAUTH2_REDIRECT_URI']
    if redirect_uri:
        if 'fci-ai-agent-uat.rfc-friso.com' in redirect_uri:
            logger.info("✅ 使用生产环境回调URL")
        elif 'localhost' in redirect_uri:
            logger.info("ℹ️ 使用本地开发回调URL")
        else:
            logger.info(f"ℹ️ 使用自定义回调URL")
    
    return all_present


def verify_user_mapping_config():
    """验证用户属性映射配置"""
    logger.info("=" * 60)
    logger.info("验证用户属性映射配置")
    logger.info("=" * 60)
    
    mapping_configs = {
        'SSO_ATTR_USERNAME': os.getenv('SSO_ATTR_USERNAME'),
        'SSO_ATTR_EMAIL': os.getenv('SSO_ATTR_EMAIL'),
        'SSO_ATTR_FIRST_NAME': os.getenv('SSO_ATTR_FIRST_NAME'),
        'SSO_ATTR_LAST_NAME': os.getenv('SSO_ATTR_LAST_NAME'),
        'SSO_ATTR_DISPLAY_NAME': os.getenv('SSO_ATTR_DISPLAY_NAME'),
        'SSO_ATTR_PHONE': os.getenv('SSO_ATTR_PHONE'),
        'SSO_ATTR_PICTURE': os.getenv('SSO_ATTR_PICTURE')
    }
    
    logger.info("用户属性映射:")
    all_present = True
    
    for key, value in mapping_configs.items():
        if value:
            logger.info(f"  ✅ {key}: {value}")
        else:
            logger.warning(f"  ⚠️ {key}: 未配置")
            # 用户属性映射不是必需的，所以不标记为错误
    
    return True


def verify_security_config():
    """验证安全配置"""
    logger.info("=" * 60)
    logger.info("验证安全配置")
    logger.info("=" * 60)
    
    security_configs = {
        'SESSION_TIMEOUT': os.getenv('SESSION_TIMEOUT'),
        'REMEMBER_COOKIE_DURATION': os.getenv('REMEMBER_COOKIE_DURATION'),
        'SESSION_COOKIE_SECURE': os.getenv('SESSION_COOKIE_SECURE'),
        'SESSION_COOKIE_HTTPONLY': os.getenv('SESSION_COOKIE_HTTPONLY'),
        'SESSION_COOKIE_SAMESITE': os.getenv('SESSION_COOKIE_SAMESITE'),
        'SECRET_KEY': os.getenv('SECRET_KEY')
    }
    
    logger.info("安全配置:")
    
    for key, value in security_configs.items():
        if value:
            if key == 'SECRET_KEY':
                # 不显示完整的密钥
                display_value = f"{value[:10]}..." if len(value) > 10 else "已设置"
            else:
                display_value = value
            logger.info(f"  ✅ {key}: {display_value}")
        else:
            logger.warning(f"  ⚠️ {key}: 未配置")
    
    # 检查密钥强度
    secret_key = security_configs['SECRET_KEY']
    if secret_key and secret_key != 'your-secret-key-change-me' and len(secret_key) >= 32:
        logger.info("✅ SECRET_KEY配置安全")
    elif secret_key == 'your-secret-key-change-me':
        logger.warning("⚠️ SECRET_KEY使用默认值，建议更改")
    else:
        logger.warning("⚠️ SECRET_KEY可能不够安全")
    
    return True


def verify_environment_consistency():
    """验证环境一致性"""
    logger.info("=" * 60)
    logger.info("验证环境一致性")
    logger.info("=" * 60)
    
    flask_env = os.getenv('FLASK_ENV', 'production')
    redirect_uri = os.getenv('OAUTH2_REDIRECT_URI', '')
    
    logger.info(f"Flask环境: {flask_env}")
    logger.info(f"回调URL: {redirect_uri}")
    
    # 检查环境和回调URL的一致性
    if flask_env == 'development' and 'localhost' in redirect_uri:
        logger.info("✅ 开发环境配置一致")
    elif flask_env == 'production' and 'localhost' not in redirect_uri:
        logger.info("✅ 生产环境配置一致")
    else:
        logger.warning("⚠️ 环境配置可能不一致，请检查FLASK_ENV和回调URL")
    
    return True


def generate_test_summary():
    """生成测试总结"""
    logger.info("=" * 60)
    logger.info("配置总结")
    logger.info("=" * 60)
    
    # 显示关键配置信息
    logger.info("关键配置信息:")
    logger.info(f"  SSO状态: {'启用' if os.getenv('SSO_ENABLED') == 'true' else '禁用'}")
    logger.info(f"  SSO提供者: {os.getenv('SSO_PROVIDER', '未配置')}")
    logger.info(f"  应用ID: {os.getenv('OAUTH2_CLIENT_ID', '未配置')}")
    logger.info(f"  回调URL: {os.getenv('OAUTH2_REDIRECT_URI', '未配置')}")
    
    logger.info("\n下一步操作:")
    logger.info("1. 运行数据库迁移: python migrations/add_sso_fields.py upgrade")
    logger.info("2. 启动应用: python app.py")
    logger.info("3. 访问登录页面测试SSO: http://localhost:5000/auth/login")
    logger.info("4. 管理员可访问SSO管理页面: http://localhost:5000/sso_management")


def main():
    """主验证函数"""
    logger.info("🔐 SSO配置验证工具")
    logger.info("=" * 80)
    logger.info("验证.env文件中的SSO配置")
    logger.info("=" * 80)
    
    tests = [
        ("加载.env配置", load_env_config),
        ("基础SSO配置", verify_basic_sso_config),
        ("Authing配置", verify_authing_config),
        ("用户属性映射", verify_user_mapping_config),
        ("安全配置", verify_security_config),
        ("环境一致性", verify_environment_consistency)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔧 验证: {test_name}")
        logger.info("-" * 50)
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} - 通过")
                passed += 1
            else:
                logger.error(f"❌ {test_name} - 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    # 生成总结
    logger.info("")
    generate_test_summary()
    
    # 最终结果
    logger.info("=" * 80)
    logger.info("验证结果")
    logger.info("=" * 80)
    logger.info(f"通过: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 所有配置验证通过！SSO配置已正确集成到.env文件")
    elif passed >= 4:
        logger.warning("⚠️ 大部分配置正确，请检查失败的项目")
    else:
        logger.error("❌ 配置验证失败，请检查.env文件")
    
    return passed >= 4


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("验证被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"验证执行异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
