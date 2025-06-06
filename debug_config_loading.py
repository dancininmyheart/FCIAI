#!/usr/bin/env python3
"""
调试配置加载问题
检查为什么SSO配置没有正确加载
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


def debug_env_file():
    """调试.env文件"""
    logger.info("=" * 60)
    logger.info("调试.env文件")
    logger.info("=" * 60)
    
    # 检查.env文件是否存在
    env_file = ".env"
    if os.path.exists(env_file):
        logger.info(f"✅ .env文件存在: {env_file}")
        
        # 读取.env文件内容
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找SSO相关配置
        sso_lines = []
        for i, line in enumerate(lines):
            if 'SSO' in line or 'OAUTH' in line:
                sso_lines.append((i+1, line.strip()))
        
        logger.info(f"找到 {len(sso_lines)} 行SSO相关配置:")
        for line_num, line in sso_lines[:10]:  # 只显示前10行
            logger.info(f"  第{line_num}行: {line}")
        
        return True
    else:
        logger.error(f"❌ .env文件不存在: {env_file}")
        return False


def debug_env_loading():
    """调试环境变量加载"""
    logger.info("=" * 60)
    logger.info("调试环境变量加载")
    logger.info("=" * 60)
    
    # 加载前检查
    logger.info("加载.env文件前的环境变量:")
    logger.info(f"  SSO_ENABLED: {os.environ.get('SSO_ENABLED', 'NOT_SET')}")
    
    # 加载.env文件
    load_dotenv()
    
    # 加载后检查
    logger.info("加载.env文件后的环境变量:")
    sso_vars = [
        'SSO_ENABLED',
        'SSO_PROVIDER',
        'OAUTH2_CLIENT_ID',
        'OAUTH2_CLIENT_SECRET',
        'OAUTH2_AUTHORIZATION_URL'
    ]
    
    for var in sso_vars:
        value = os.environ.get(var, 'NOT_SET')
        if var == 'OAUTH2_CLIENT_SECRET':
            display_value = f"{value[:10]}..." if value != 'NOT_SET' and len(value) > 10 else value
        else:
            display_value = value
        logger.info(f"  {var}: {display_value}")
    
    return os.environ.get('SSO_ENABLED') == 'true'


def debug_config_class():
    """调试Config类"""
    logger.info("=" * 60)
    logger.info("调试Config类")
    logger.info("=" * 60)
    
    try:
        from config import Config
        
        logger.info("Config类的SSO配置:")
        sso_configs = [
            'SSO_ENABLED',
            'SSO_PROVIDER',
            'OAUTH2_CLIENT_ID',
            'OAUTH2_AUTHORIZATION_URL'
        ]
        
        for config_name in sso_configs:
            value = getattr(Config, config_name, 'NOT_SET')
            logger.info(f"  {config_name}: {value}")
        
        return Config.SSO_ENABLED
        
    except Exception as e:
        logger.error(f"❌ Config类加载失败: {e}")
        return False


def debug_flask_app_config():
    """调试Flask应用配置"""
    logger.info("=" * 60)
    logger.info("调试Flask应用配置")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app('development')
        
        with app.app_context():
            logger.info("Flask应用的SSO配置:")
            sso_configs = [
                'SSO_ENABLED',
                'SSO_PROVIDER',
                'OAUTH2_CLIENT_ID',
                'OAUTH2_AUTHORIZATION_URL'
            ]
            
            for config_name in sso_configs:
                value = app.config.get(config_name, 'NOT_SET')
                logger.info(f"  {config_name}: {value}")
            
            return app.config.get('SSO_ENABLED', False)
            
    except Exception as e:
        logger.error(f"❌ Flask应用配置检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def debug_sso_service_in_app():
    """调试应用中的SSO服务"""
    logger.info("=" * 60)
    logger.info("调试应用中的SSO服务")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        
        app = create_app('development')
        
        with app.app_context():
            from app.services.sso_service import get_sso_service
            
            logger.info("获取SSO服务实例...")
            sso_service = get_sso_service()
            
            logger.info("检查SSO服务状态...")
            is_enabled = sso_service.is_enabled()
            logger.info(f"SSO启用状态: {is_enabled}")
            
            # 检查配置访问
            logger.info("检查SSO服务中的配置访问...")
            try:
                from flask import current_app
                app_sso_enabled = current_app.config.get('SSO_ENABLED', False)
                logger.info(f"current_app.config.SSO_ENABLED: {app_sso_enabled}")
                
                providers_count = len(sso_service.providers)
                logger.info(f"提供者数量: {providers_count}")
                
                return is_enabled
                
            except Exception as e:
                logger.error(f"配置访问失败: {e}")
                return False
            
    except Exception as e:
        logger.error(f"❌ SSO服务检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主调试函数"""
    logger.info("🔍 配置加载调试工具")
    logger.info("=" * 80)
    
    tests = [
        (".env文件检查", debug_env_file),
        ("环境变量加载", debug_env_loading),
        ("Config类检查", debug_config_class),
        ("Flask应用配置", debug_flask_app_config),
        ("SSO服务检查", debug_sso_service_in_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔧 执行调试: {test_name}")
        logger.info("-" * 50)
        
        try:
            result = test_func()
            if result:
                logger.info(f"✅ {test_name} - SSO启用")
                passed += 1
            else:
                logger.error(f"❌ {test_name} - SSO未启用")
        except Exception as e:
            logger.error(f"❌ {test_name} - 错误: {e}")
    
    # 总结
    logger.info("=" * 80)
    logger.info("调试总结")
    logger.info("=" * 80)
    logger.info(f"SSO启用检查: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 所有检查都显示SSO已启用")
        logger.info("问题可能在其他地方")
    elif passed >= 3:
        logger.warning("⚠️ 大部分检查显示SSO已启用")
        logger.info("问题可能在SSO服务初始化")
    else:
        logger.error("❌ 多数检查显示SSO未启用")
        logger.info("需要检查配置文件和环境变量")
    
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
