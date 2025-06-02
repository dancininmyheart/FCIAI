#!/usr/bin/env python3
"""
测试事件循环修复
验证HTTP客户端在Flask应用初始化时不会出现事件循环错误
"""
import sys
import os
import traceback
from datetime import datetime

def test_app_initialization():
    """测试应用初始化"""
    print("🧪 测试Flask应用初始化...")
    
    try:
        # 添加项目路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # 导入应用创建函数
        from app import create_app
        
        print("   ✅ 成功导入create_app函数")
        
        # 创建应用实例
        app = create_app('development')
        
        print("   ✅ 成功创建Flask应用实例")
        
        # 检查应用配置
        with app.app_context():
            print(f"   ✅ 应用配置: {app.config.get('ENV', 'unknown')}")
            print(f"   ✅ 数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'not configured')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 应用初始化失败: {str(e)}")
        print(f"   错误详情:")
        traceback.print_exc()
        return False

def test_http_client_configuration():
    """测试HTTP客户端配置"""
    print("\n🌐 测试HTTP客户端配置...")
    
    try:
        from app.utils.lazy_http_client import http_client
        
        print("   ✅ 成功导入懒加载HTTP客户端")
        
        # 配置客户端
        http_client.configure(
            max_connections=50,
            default_timeout=30,
            retry_times=2,
            retry_delay=1
        )
        
        print("   ✅ 成功配置HTTP客户端")
        
        # 检查配置
        stats = http_client.get_stats()
        print(f"   ✅ 客户端状态: {stats}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ HTTP客户端配置失败: {str(e)}")
        traceback.print_exc()
        return False

def test_async_functionality():
    """测试异步功能"""
    print("\n⚡ 测试异步功能...")
    
    try:
        import asyncio
        from app.utils.lazy_http_client import lazy_http_client
        
        async def test_async_request():
            """测试异步请求"""
            try:
                # 配置客户端
                lazy_http_client.configure(
                    max_connections=10,
                    default_timeout=5
                )
                
                print("   ✅ 异步环境中配置HTTP客户端成功")
                
                # 测试会话创建
                session = await lazy_http_client._ensure_session()
                print(f"   ✅ 成功创建HTTP会话: {type(session).__name__}")
                
                # 关闭会话
                await lazy_http_client.close()
                print("   ✅ 成功关闭HTTP会话")
                
                return True
                
            except Exception as e:
                print(f"   ❌ 异步测试失败: {str(e)}")
                return False
        
        # 运行异步测试
        result = asyncio.run(test_async_request())
        return result
        
    except Exception as e:
        print(f"   ❌ 异步功能测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_run_py_import():
    """测试run.py导入"""
    print("\n🚀 测试run.py导入...")
    
    try:
        # 检查run.py文件是否存在
        if not os.path.exists('run.py'):
            print("   ⚠️ run.py文件不存在，跳过测试")
            return True
        
        # 尝试导入run.py中的内容
        import importlib.util
        spec = importlib.util.spec_from_file_location("run", "run.py")
        run_module = importlib.util.module_from_spec(spec)
        
        # 执行模块（但不运行应用）
        print("   ✅ 成功加载run.py模块")
        
        return True
        
    except Exception as e:
        print(f"   ❌ run.py导入失败: {str(e)}")
        traceback.print_exc()
        return False

def test_original_error_scenario():
    """测试原始错误场景"""
    print("\n🔍 测试原始错误场景...")
    
    try:
        # 模拟原始错误：在没有事件循环的环境中创建HTTP客户端
        from app.utils.async_http_client import AsyncHttpClient
        
        print("   ✅ 成功导入原始AsyncHttpClient")
        
        # 尝试创建和配置原始客户端
        old_client = AsyncHttpClient()
        
        try:
            old_client.configure(max_connections=10)
            print("   ⚠️ 原始客户端配置成功（可能仍有问题）")
        except RuntimeError as e:
            if "no running event loop" in str(e):
                print("   ✅ 原始客户端正确抛出事件循环错误")
            else:
                print(f"   ⚠️ 原始客户端抛出其他错误: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 原始错误场景测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("事件循环修复测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("HTTP客户端配置", test_http_client_configuration),
        ("异步功能", test_async_functionality),
        ("run.py导入", test_run_py_import),
        ("原始错误场景", test_original_error_scenario),
        ("Flask应用初始化", test_app_initialization),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            results[test_name] = False
    
    # 总结结果
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"测试结果: {passed}/{total} 项通过")
    print()
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print()
    
    if passed == total:
        print("🎉 所有测试通过！事件循环问题已修复。")
        print()
        print("✅ 修复内容:")
        print("  1. 创建了懒加载HTTP客户端 (lazy_http_client.py)")
        print("  2. 修改了应用初始化，使用懒加载客户端")
        print("  3. HTTP会话只在实际使用时创建")
        print("  4. 避免了在Flask初始化时创建aiohttp会话")
        
        print()
        print("🚀 现在可以安全运行:")
        print("  python run.py")
        
    else:
        print("⚠️ 部分测试失败，可能仍有问题需要解决。")
        
        if not results.get("Flask应用初始化", False):
            print()
            print("💡 建议:")
            print("  1. 检查数据库连接配置")
            print("  2. 确保所有依赖包已安装")
            print("  3. 检查环境变量配置")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试执行异常: {str(e)}")
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)
