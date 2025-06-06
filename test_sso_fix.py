#!/usr/bin/env python3
"""
测试SSO修复
验证应用上下文问题是否已解决
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


def test_import_sso_service():
    """测试SSO服务导入"""
    logger.info("=" * 60)
    logger.info("测试SSO服务导入")
    logger.info("=" * 60)
    
    try:
        # 测试导入SSO服务
        from app.services.sso_service import get_sso_service
        logger.info("✅ SSO服务导入成功")
        
        # 测试获取服务实例（应该不会报错）
        sso_service = get_sso_service()
        logger.info("✅ SSO服务实例创建成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SSO服务导入失败: {e}")
        return False


def test_app_creation():
    """测试应用创建"""
    logger.info("=" * 60)
    logger.info("测试应用创建")
    logger.info("=" * 60)
    
    try:
        # 测试创建应用
        from app import create_app
        app = create_app()
        logger.info("✅ 应用创建成功")
        
        # 测试应用上下文
        with app.app_context():
            from app.services.sso_service import get_sso_service
            sso_service = get_sso_service()
            
            # 测试SSO服务方法
            is_enabled = sso_service.is_enabled()
            logger.info(f"✅ SSO启用状态: {is_enabled}")
            
            providers = list(sso_service.providers.keys())
            logger.info(f"✅ 可用提供者: {providers}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_imports():
    """测试视图导入"""
    logger.info("=" * 60)
    logger.info("测试视图导入")
    logger.info("=" * 60)
    
    try:
        # 测试主视图导入
        from app.views.main import main
        logger.info("✅ 主视图导入成功")
        
        # 测试认证视图导入
        from app.views.auth import bp as auth_bp
        logger.info("✅ 认证视图导入成功")
        
        # 测试SSO认证视图导入
        from app.views.sso_auth import sso_bp
        logger.info("✅ SSO认证视图导入成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 视图导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sso_configuration():
    """测试SSO配置"""
    logger.info("=" * 60)
    logger.info("测试SSO配置")
    logger.info("=" * 60)
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # 检查SSO配置
            sso_config = {
                'SSO_ENABLED': app.config.get('SSO_ENABLED'),
                'SSO_PROVIDER': app.config.get('SSO_PROVIDER'),
                'SSO_AUTO_CREATE_USER': app.config.get('SSO_AUTO_CREATE_USER'),
                'SSO_DEFAULT_ROLE': app.config.get('SSO_DEFAULT_ROLE')
            }
            
            logger.info("SSO配置:")
            for key, value in sso_config.items():
                logger.info(f"  {key}: {value}")
            
            # 测试SSO服务在应用上下文中的工作
            from app.services.sso_service import get_sso_service
            sso_service = get_sso_service()
            
            # 强制初始化
            sso_service._ensure_initialized()
            
            logger.info(f"✅ SSO服务初始化完成")
            logger.info(f"可用提供者: {list(sso_service.providers.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SSO配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_run():
    """测试Flask运行"""
    logger.info("=" * 60)
    logger.info("测试Flask运行")
    logger.info("=" * 60)
    
    try:
        # 模拟Flask应用启动
        from app import create_app
        app = create_app()
        
        # 测试应用配置
        logger.info(f"应用名称: {app.name}")
        logger.info(f"调试模式: {app.debug}")
        logger.info(f"测试模式: {app.testing}")
        
        # 测试蓝图注册
        blueprints = list(app.blueprints.keys())
        logger.info(f"注册的蓝图: {blueprints}")
        
        # 检查SSO相关蓝图
        if 'sso' in blueprints:
            logger.info("✅ SSO蓝图已注册")
        else:
            logger.warning("⚠️ SSO蓝图未注册")
        
        # 测试路由
        with app.app_context():
            # 获取所有路由
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append(str(rule))
            
            sso_routes = [route for route in routes if '/auth/sso' in route]
            logger.info(f"SSO路由数量: {len(sso_routes)}")
            
            if sso_routes:
                logger.info("SSO路由:")
                for route in sso_routes[:5]:  # 只显示前5个
                    logger.info(f"  {route}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Flask运行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    logger.info("🔧 SSO修复验证测试")
    logger.info("=" * 80)
    
    tests = [
        ("SSO服务导入", test_import_sso_service),
        ("应用创建", test_app_creation),
        ("视图导入", test_view_imports),
        ("SSO配置", test_sso_configuration),
        ("Flask运行", test_flask_run)
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
        logger.info("🎉 所有测试通过！SSO应用上下文问题已修复")
        logger.info("\n✅ 现在可以正常启动应用:")
        logger.info("  python app.py")
        logger.info("  或")
        logger.info("  flask run")
    elif passed >= 3:
        logger.warning("⚠️ 大部分测试通过，基本问题已解决")
        logger.info("可以尝试启动应用")
    else:
        logger.error("❌ 多数测试失败，仍有问题需要解决")
        logger.info("\n🔧 故障排除建议:")
        logger.info("1. 检查Python环境和依赖")
        logger.info("2. 确保所有文件修改正确")
        logger.info("3. 查看详细错误信息")
    
    return passed >= 3


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
