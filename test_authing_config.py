#!/usr/bin/env python3
"""
Authing SSO配置验证工具
验证FCI AI翻译助手UAT环境的Authing配置
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


def test_authing_endpoints():
    """测试Authing端点连通性"""
    logger.info("=" * 60)
    logger.info("测试Authing端点连通性")
    logger.info("=" * 60)
    
    # FCI AI翻译助手UAT配置
    app_id = "683ebc2889ae4d4c1ff7e111"
    app_host = f"https://sso.rfc-friso.com/{app_id}"
    
    endpoints = {
        "授权端点": f"{app_host}/oidc/auth",
        "令牌端点": f"{app_host}/oidc/token",
        "用户信息端点": f"{app_host}/oidc/me",
        "登出端点": f"{app_host}/oidc/session/end",
        "OIDC配置": f"{app_host}/.well-known/openid_configuration"
    }
    
    results = {}
    
    for name, url in endpoints.items():
        try:
            logger.info(f"测试 {name}: {url}")
            
            # 对于需要认证的端点，只测试连通性
            if name in ["令牌端点", "用户信息端点"]:
                response = requests.post(url, timeout=10) if name == "令牌端点" else requests.get(url, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            if response.status_code in [200, 400, 401, 403]:  # 这些状态码表示端点可达
                logger.info(f"✅ {name} - 可达 (状态码: {response.status_code})")
                results[name] = True
            else:
                logger.warning(f"⚠️ {name} - 异常状态码: {response.status_code}")
                results[name] = False
                
        except requests.RequestException as e:
            logger.error(f"❌ {name} - 连接失败: {e}")
            results[name] = False
        except Exception as e:
            logger.error(f"❌ {name} - 测试异常: {e}")
            results[name] = False
    
    return all(results.values())


def test_oidc_discovery():
    """测试OIDC发现文档"""
    logger.info("=" * 60)
    logger.info("测试OIDC发现文档")
    logger.info("=" * 60)
    
    app_id = "683ebc2889ae4d4c1ff7e111"
    discovery_url = f"https://sso.rfc-friso.com/{app_id}/.well-known/openid_configuration"
    
    try:
        logger.info(f"获取OIDC配置: {discovery_url}")
        response = requests.get(discovery_url, timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            
            logger.info("✅ OIDC发现文档获取成功")
            logger.info("支持的端点:")
            
            important_endpoints = [
                'authorization_endpoint',
                'token_endpoint',
                'userinfo_endpoint',
                'end_session_endpoint',
                'issuer'
            ]
            
            for endpoint in important_endpoints:
                if endpoint in config:
                    logger.info(f"  {endpoint}: {config[endpoint]}")
                else:
                    logger.warning(f"  {endpoint}: 未找到")
            
            # 检查支持的scope
            if 'scopes_supported' in config:
                logger.info(f"支持的scope: {config['scopes_supported']}")
            
            return True
        else:
            logger.error(f"❌ OIDC发现文档获取失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ OIDC发现文档测试失败: {e}")
        return False


def test_authing_config_validation():
    """验证Authing配置"""
    logger.info("=" * 60)
    logger.info("验证Authing配置")
    logger.info("=" * 60)
    
    # FCI AI翻译助手UAT配置
    config = {
        'app_id': '683ebc2889ae4d4c1ff7e111',
        'secret': '082339b43a8da9636332e1f4d11111',
        'app_host': 'https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111',
        'redirect_uri': 'https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback'
    }
    
    logger.info("配置验证:")
    
    # 验证App ID
    if config['app_id'] and len(config['app_id']) > 10:
        logger.info("✅ App ID: 格式正确")
    else:
        logger.error("❌ App ID: 格式错误")
        return False
    
    # 验证Secret
    if config['secret'] and len(config['secret']) > 10:
        logger.info("✅ App Secret: 格式正确")
    else:
        logger.error("❌ App Secret: 格式错误")
        return False
    
    # 验证App Host
    if config['app_host'].startswith('https://') and config['app_id'] in config['app_host']:
        logger.info("✅ App Host: 格式正确")
    else:
        logger.error("❌ App Host: 格式错误")
        return False
    
    # 验证回调URL
    parsed_uri = urlparse(config['redirect_uri'])
    if parsed_uri.scheme == 'https' and parsed_uri.path == '/auth/sso/callback':
        logger.info("✅ 回调URL: 格式正确")
    else:
        logger.error("❌ 回调URL: 格式错误")
        return False
    
    logger.info("✅ 所有配置验证通过")
    return True


def test_sso_service_with_authing():
    """测试SSO服务与Authing集成"""
    logger.info("=" * 60)
    logger.info("测试SSO服务与Authing集成")
    logger.info("=" * 60)
    
    try:
        # 设置环境变量模拟Authing配置
        os.environ['SSO_ENABLED'] = 'true'
        os.environ['SSO_PROVIDER'] = 'oauth2'
        os.environ['OAUTH2_CLIENT_ID'] = '683ebc2889ae4d4c1ff7e111'
        os.environ['OAUTH2_CLIENT_SECRET'] = '082339b43a8da9636332e1f4d11111'
        os.environ['OAUTH2_AUTHORIZATION_URL'] = 'https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/auth'
        os.environ['OAUTH2_TOKEN_URL'] = 'https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/token'
        os.environ['OAUTH2_USERINFO_URL'] = 'https://sso.rfc-friso.com/683ebc2889ae4d4c1ff7e111/oidc/me'
        os.environ['OAUTH2_REDIRECT_URI'] = 'https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback'
        
        # 创建Flask应用测试
        from flask import Flask
        from config import Config
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            from app.services.sso_service import get_sso_service
            
            sso_service = get_sso_service()
            sso_service._ensure_initialized()
            
            # 检查是否识别为Authing提供者
            if 'authing' in sso_service.providers:
                logger.info("✅ Authing提供者已正确初始化")
                
                # 测试获取授权URL
                provider = sso_service.get_provider('authing')
                if provider:
                    auth_url = provider.get_authorization_url()
                    if 'sso.rfc-friso.com' in auth_url:
                        logger.info("✅ 授权URL生成正确")
                        logger.info(f"授权URL: {auth_url[:100]}...")
                    else:
                        logger.error("❌ 授权URL格式错误")
                        return False
                else:
                    logger.error("❌ 无法获取Authing提供者")
                    return False
            else:
                logger.error("❌ Authing提供者未初始化")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ SSO服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_test_urls():
    """生成测试URL"""
    logger.info("=" * 60)
    logger.info("生成测试URL")
    logger.info("=" * 60)
    
    app_id = "683ebc2889ae4d4c1ff7e111"
    app_host = f"https://sso.rfc-friso.com/{app_id}"
    
    # 生成测试授权URL
    from urllib.parse import urlencode
    
    auth_params = {
        'client_id': app_id,
        'response_type': 'code',
        'scope': 'openid profile email phone',
        'redirect_uri': 'https://fci-ai-agent-uat.rfc-friso.com/auth/sso/callback',
        'state': 'test_state_123'
    }
    
    auth_url = f"{app_host}/oidc/auth?{urlencode(auth_params)}"
    
    logger.info("测试URL:")
    logger.info(f"授权URL: {auth_url}")
    logger.info(f"OIDC配置: {app_host}/.well-known/openid_configuration")
    logger.info(f"用户池域名: {app_host}")
    
    logger.info("\n💡 测试步骤:")
    logger.info("1. 在浏览器中访问授权URL")
    logger.info("2. 完成Authing登录")
    logger.info("3. 检查是否正确重定向到回调URL")
    logger.info("4. 验证回调URL中包含authorization code")


def main():
    """主测试函数"""
    logger.info("🔐 Authing SSO配置验证工具")
    logger.info("=" * 80)
    logger.info("FCI AI翻译助手 UAT环境 Authing配置测试")
    logger.info("=" * 80)
    
    tests = [
        ("配置验证", test_authing_config_validation),
        ("端点连通性", test_authing_endpoints),
        ("OIDC发现文档", test_oidc_discovery),
        ("SSO服务集成", test_sso_service_with_authing)
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
    
    # 生成测试URL
    logger.info("")
    generate_test_urls()
    
    # 总结
    logger.info("=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    logger.info(f"通过: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 Authing配置验证通过！")
        logger.info("\n✅ 配置正确，可以使用以下步骤部署:")
        logger.info("1. 复制 .env.authing.example 为 .env")
        logger.info("2. 运行数据库迁移")
        logger.info("3. 启动应用并测试SSO登录")
    elif passed >= 2:
        logger.warning("⚠️ 部分测试通过，基本配置正确")
        logger.info("请检查失败的测试项目")
    else:
        logger.error("❌ 多数测试失败，请检查Authing配置")
    
    return passed >= 2


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
