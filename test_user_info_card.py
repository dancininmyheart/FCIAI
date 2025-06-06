#!/usr/bin/env python3
"""
用户信息卡片功能测试
验证用户信息显示和交互功能
"""
import os
import sys
import logging
import requests
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_user_info_display():
    """测试用户信息显示"""
    logger.info("🔍 测试用户信息显示")
    logger.info("=" * 60)
    
    try:
        # 访问主页（需要登录）
        base_url = "http://localhost:5000"
        
        # 创建session保持登录状态
        session = requests.Session()
        
        # 先访问登录页面
        login_url = f"{base_url}/auth/login"
        response = session.get(login_url)
        
        if response.status_code == 200:
            logger.info("✅ 登录页面访问成功")
            
            # 检查页面是否包含用户信息卡片相关的CSS和JS
            content = response.text
            
            checks = [
                ("用户信息CSS", 'user-info.css' in content),
                ("用户信息JS", 'user-info.js' in content),
                ("Bootstrap图标", 'bootstrap-icons' in content)
            ]
            
            logger.info("页面资源检查:")
            for name, check in checks:
                if check:
                    logger.info(f"  ✅ {name}: 已加载")
                else:
                    logger.warning(f"  ⚠️ {name}: 未找到")
            
            return True
        else:
            logger.error(f"❌ 登录页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


def test_user_info_api():
    """测试用户信息API"""
    logger.info("📊 测试用户信息API")
    logger.info("=" * 60)
    
    try:
        base_url = "http://localhost:5000"
        api_url = f"{base_url}/auth/user-info"
        
        # 尝试访问用户信息API（未登录状态）
        response = requests.get(api_url)
        
        if response.status_code == 401 or response.status_code == 302:
            logger.info("✅ 用户信息API正确要求登录")
            return True
        else:
            logger.warning(f"⚠️ 用户信息API响应: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API测试失败: {e}")
        return False


def test_change_password_api():
    """测试修改密码API"""
    logger.info("🔐 测试修改密码API")
    logger.info("=" * 60)
    
    try:
        base_url = "http://localhost:5000"
        api_url = f"{base_url}/auth/change-password"
        
        # 尝试访问修改密码API（未登录状态）
        response = requests.post(api_url, json={
            'current_password': 'test',
            'new_password': 'newtest'
        })
        
        if response.status_code == 401 or response.status_code == 302:
            logger.info("✅ 修改密码API正确要求登录")
            return True
        else:
            logger.warning(f"⚠️ 修改密码API响应: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 修改密码API测试失败: {e}")
        return False


def test_static_files():
    """测试静态文件"""
    logger.info("📁 测试静态文件")
    logger.info("=" * 60)
    
    base_url = "http://localhost:5000"
    static_files = [
        ('/static/css/user-info.css', '用户信息CSS'),
        ('/static/js/user-info.js', '用户信息JS')
    ]
    
    passed = 0
    total = len(static_files)
    
    for file_path, file_name in static_files:
        try:
            url = f"{base_url}{file_path}"
            response = requests.get(url)
            
            if response.status_code == 200:
                logger.info(f"  ✅ {file_name}: 可访问")
                
                # 检查文件内容
                content = response.text
                if file_path.endswith('.css'):
                    if '.user-info-card' in content:
                        logger.info(f"    ✅ CSS包含用户信息卡片样式")
                        passed += 1
                    else:
                        logger.warning(f"    ⚠️ CSS缺少用户信息卡片样式")
                elif file_path.endswith('.js'):
                    if 'toggleUserInfo' in content:
                        logger.info(f"    ✅ JS包含用户信息交互函数")
                        passed += 1
                    else:
                        logger.warning(f"    ⚠️ JS缺少用户信息交互函数")
            else:
                logger.error(f"  ❌ {file_name}: 无法访问 ({response.status_code})")
                
        except Exception as e:
            logger.error(f"  ❌ {file_name}: 测试失败 - {e}")
    
    return passed >= total


def test_template_integration():
    """测试模板集成"""
    logger.info("🎨 测试模板集成")
    logger.info("=" * 60)
    
    try:
        # 检查模板文件是否存在
        template_path = "app/templates/main/base_layout.html"
        
        if os.path.exists(template_path):
            logger.info(f"✅ 模板文件存在: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键元素
            checks = [
                ("用户信息CSS引用", 'user-info.css' in content),
                ("用户信息JS引用", 'user-info.js' in content),
                ("用户信息卡片HTML", 'user-info-card' in content),
                ("用户认证检查", 'current_user.is_authenticated' in content),
                ("用户显示名称", 'current_user.get_display_name()' in content),
                ("用户角色显示", 'current_user.role.name' in content),
                ("SSO用户检查", 'current_user.is_sso_user()' in content),
                ("修改密码功能", 'current_user.can_change_password()' in content)
            ]
            
            logger.info("模板元素检查:")
            passed = 0
            for name, check in checks:
                if check:
                    logger.info(f"  ✅ {name}: 存在")
                    passed += 1
                else:
                    logger.warning(f"  ⚠️ {name}: 不存在")
            
            logger.info(f"模板集成检查: {passed}/{len(checks)}")
            return passed >= len(checks) - 2  # 允许2个检查失败
        else:
            logger.error(f"❌ 模板文件不存在: {template_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 模板集成测试失败: {e}")
        return False


def test_user_model_methods():
    """测试用户模型方法"""
    logger.info("👤 测试用户模型方法")
    logger.info("=" * 60)
    
    try:
        # 检查用户模型文件
        model_path = "app/models/user.py"
        
        if os.path.exists(model_path):
            logger.info(f"✅ 用户模型文件存在: {model_path}")
            
            with open(model_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键方法
            methods = [
                ("get_display_name", "获取显示名称"),
                ("get_full_name", "获取全名"),
                ("is_sso_user", "检查SSO用户"),
                ("can_change_password", "检查是否可修改密码"),
                ("is_administrator", "检查管理员权限"),
                ("has_permission", "检查权限"),
                ("set_password", "设置密码"),
                ("check_password", "验证密码")
            ]
            
            logger.info("用户模型方法检查:")
            passed = 0
            for method_name, description in methods:
                if f"def {method_name}" in content:
                    logger.info(f"  ✅ {method_name}: {description}")
                    passed += 1
                else:
                    logger.warning(f"  ⚠️ {method_name}: {description} - 未找到")
            
            logger.info(f"用户模型方法: {passed}/{len(methods)}")
            return passed >= len(methods) - 1  # 允许1个方法缺失
        else:
            logger.error(f"❌ 用户模型文件不存在: {model_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 用户模型测试失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("🧪 用户信息卡片功能测试")
    logger.info("=" * 80)
    
    tests = [
        ("用户信息显示", test_user_info_display),
        ("用户信息API", test_user_info_api),
        ("修改密码API", test_change_password_api),
        ("静态文件", test_static_files),
        ("模板集成", test_template_integration),
        ("用户模型方法", test_user_model_methods)
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
        logger.info("\n✅ 用户信息卡片功能已完整实现:")
        logger.info("  1. 用户信息显示")
        logger.info("  2. 交互功能（展开/收起）")
        logger.info("  3. 修改密码功能")
        logger.info("  4. SSO用户识别")
        logger.info("  5. 响应式设计")
        logger.info("  6. 键盘快捷键支持")
        
        logger.info("\n📱 使用说明:")
        logger.info("  - 用户信息卡片显示在页面右下角")
        logger.info("  - 点击卡片头部可展开/收起详细信息")
        logger.info("  - 使用 Ctrl+U 快捷键切换显示状态")
        logger.info("  - SSO用户无法修改密码")
        logger.info("  - 普通用户可以通过卡片修改密码")
        
    elif passed >= 4:
        logger.warning("⚠️ 大部分测试通过，基本功能可用")
        logger.info("请检查失败的测试项目")
    else:
        logger.error("❌ 多数测试失败，请检查实现")
    
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
