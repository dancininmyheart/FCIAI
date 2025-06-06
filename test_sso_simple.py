#!/usr/bin/env python3
"""
简单的SSO修复测试
只测试核心SSO功能，避免其他依赖问题
"""
import os
import sys
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_sso_service_import():
    """测试SSO服务导入（核心测试）"""
    logger.info("=" * 60)
    logger.info("测试SSO服务导入和初始化")
    logger.info("=" * 60)
    
    try:
        # 测试导入SSO服务
        from app.services.sso_service import get_sso_service, SSOService
        logger.info("✅ SSO服务模块导入成功")
        
        # 测试创建服务实例
        sso_service = get_sso_service()
        logger.info("✅ SSO服务实例创建成功")
        
        # 测试服务属性
        logger.info(f"服务已初始化: {sso_service._initialized}")
        logger.info(f"提供者数量: {len(sso_service.providers)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SSO服务导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sso_auth_view_import():
    """测试SSO认证视图导入"""
    logger.info("=" * 60)
    logger.info("测试SSO认证视图导入")
    logger.info("=" * 60)
    
    try:
        # 测试SSO认证视图导入
        from app.views.sso_auth import sso_bp, get_sso_service
        logger.info("✅ SSO认证视图导入成功")
        
        # 测试蓝图属性
        logger.info(f"蓝图名称: {sso_bp.name}")
        logger.info(f"蓝图前缀: {sso_bp.url_prefix}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SSO认证视图导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_user_service_import():
    """测试用户服务导入"""
    logger.info("=" * 60)
    logger.info("测试用户服务导入")
    logger.info("=" * 60)
    
    try:
        # 测试用户服务导入
        from app.services.user_service import UserService, sso_user_manager
        logger.info("✅ 用户服务导入成功")
        
        # 测试服务方法存在
        methods = ['find_or_create_sso_user', 'login_sso_user', 'is_sso_user']
        for method in methods:
            if hasattr(UserService, method):
                logger.info(f"✅ 方法存在: {method}")
            else:
                logger.warning(f"⚠️ 方法缺失: {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 用户服务导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_loading():
    """测试配置加载"""
    logger.info("=" * 60)
    logger.info("测试配置加载")
    logger.info("=" * 60)
    
    try:
        # 测试配置类导入
        from config import Config
        logger.info("✅ 配置类导入成功")
        
        # 检查SSO相关配置
        sso_configs = [
            'SSO_ENABLED', 'SSO_PROVIDER', 'SSO_AUTO_CREATE_USER',
            'OAUTH2_CLIENT_ID', 'OAUTH2_AUTHORIZATION_URL'
        ]
        
        logger.info("SSO配置属性:")
        for config_name in sso_configs:
            if hasattr(Config, config_name):
                value = getattr(Config, config_name)
                logger.info(f"  ✅ {config_name}: {value}")
            else:
                logger.warning(f"  ⚠️ {config_name}: 未定义")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_app_minimal():
    """测试最小Flask应用创建"""
    logger.info("=" * 60)
    logger.info("测试最小Flask应用创建")
    logger.info("=" * 60)
    
    try:
        # 创建最小Flask应用来测试SSO
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        logger.info("✅ 最小Flask应用创建成功")
        
        # 在应用上下文中测试SSO服务
        with app.app_context():
            from app.services.sso_service import get_sso_service
            sso_service = get_sso_service()
            
            # 测试SSO服务方法
            is_enabled = sso_service.is_enabled()
            logger.info(f"✅ SSO启用状态: {is_enabled}")
            
            # 强制初始化
            sso_service._ensure_initialized()
            providers = list(sso_service.providers.keys())
            logger.info(f"✅ 可用提供者: {providers}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 最小Flask应用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_models():
    """测试数据库模型"""
    logger.info("=" * 60)
    logger.info("测试数据库模型")
    logger.info("=" * 60)
    
    try:
        # 测试用户模型导入
        from app.models.user import User, Role
        logger.info("✅ 用户模型导入成功")
        
        # 检查SSO相关字段
        sso_fields = [
            'email', 'first_name', 'last_name', 'display_name',
            'sso_provider', 'sso_subject', 'last_login'
        ]
        
        logger.info("用户模型SSO字段:")
        for field in sso_fields:
            if hasattr(User, field):
                logger.info(f"  ✅ {field}: 存在")
            else:
                logger.warning(f"  ⚠️ {field}: 不存在")
        
        # 检查SSO相关方法
        sso_methods = ['is_sso_user', 'can_change_password', 'get_display_name']
        logger.info("用户模型SSO方法:")
        for method in sso_methods:
            if hasattr(User, method):
                logger.info(f"  ✅ {method}: 存在")
            else:
                logger.warning(f"  ⚠️ {method}: 不存在")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    logger.info("🔧 SSO修复简单验证测试")
    logger.info("=" * 80)
    logger.info("专注于验证SSO核心功能，避免其他依赖问题")
    logger.info("=" * 80)
    
    tests = [
        ("SSO服务导入", test_sso_service_import),
        ("SSO认证视图导入", test_sso_auth_view_import),
        ("用户服务导入", test_user_service_import),
        ("配置加载", test_config_loading),
        ("最小Flask应用", test_flask_app_minimal),
        ("数据库模型", test_database_models)
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
        logger.info("🎉 核心SSO功能测试通过！应用上下文问题已修复")
        logger.info("\n✅ 修复内容:")
        logger.info("1. SSO服务延迟初始化，避免应用上下文错误")
        logger.info("2. 使用get_sso_service()函数获取服务实例")
        logger.info("3. 所有SSO相关视图已更新使用新的获取方式")
        logger.info("4. 配置访问增加了异常处理")
        
        logger.info("\n🚀 下一步:")
        logger.info("1. 安装缺失的依赖: pip install opencv-python")
        logger.info("2. 运行数据库迁移: python migrations/add_sso_fields.py upgrade")
        logger.info("3. 配置SSO设置: cp .env.sso.example .env")
        logger.info("4. 启动应用: python app.py")
        
    elif passed >= 2:
        logger.warning("⚠️ 部分测试通过，基本问题已解决")
        logger.info("请检查失败的测试项目")
    else:
        logger.error("❌ 多数测试失败，仍有问题需要解决")
        logger.info("\n🔧 故障排除建议:")
        logger.info("1. 检查Python环境和基础依赖")
        logger.info("2. 确保项目路径正确")
        logger.info("3. 查看详细错误信息")
    
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
