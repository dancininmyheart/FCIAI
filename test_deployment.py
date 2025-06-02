#!/usr/bin/env python3
"""
部署环境测试脚本
验证系统部署是否正确配置
"""
import os
import sys
import subprocess
import importlib
import socket
import urllib.request
import json
from datetime import datetime

def test_python_version():
    """测试Python版本"""
    print("🐍 Python版本检查:")
    version = sys.version_info
    print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("   ✅ Python版本符合要求 (3.8+)")
        return True
    else:
        print("   ❌ Python版本过低，需要3.8+")
        return False

def test_required_packages():
    """测试必需的Python包"""
    print("\n📦 Python包检查:")
    
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_cors',
        'pymysql', 'aiohttp', 'aiofiles', 'gunicorn',
        'python_pptx', 'easyocr', 'PIL', 'numpy',
        'requests', 'beautifulsoup4', 'selenium',
        'psutil', 'python_dotenv', 'pytz'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('_', '.'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   缺少包: {', '.join(missing_packages)}")
        print("   请运行: pip install -r requirements.txt")
        return False
    
    return True

def test_database_connection():
    """测试数据库连接"""
    print("\n🗄️ 数据库连接检查:")
    
    try:
        import pymysql
        from config import DB_CONFIG
        
        connection = pymysql.connect(
            host=DB_CONFIG.get('host', 'localhost'),
            port=DB_CONFIG.get('port', 3306),
            user=DB_CONFIG.get('user', 'root'),
            password=DB_CONFIG.get('password', ''),
            database=DB_CONFIG.get('database', 'ppt_translate_db'),
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            print(f"   ✅ MySQL连接成功，版本: {version}")
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['users', 'role', 'permission', 'upload_records', 'translation', 'stop_words']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"   ⚠️ 缺少表: {', '.join(missing_tables)}")
                print("   请运行: python setup_database.py")
                return False
            else:
                print(f"   ✅ 所有必需表存在: {', '.join(tables)}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {str(e)}")
        return False

def test_directories():
    """测试目录结构"""
    print("\n📁 目录结构检查:")
    
    required_dirs = [
        'uploads', 'uploads/ppt', 'uploads/pdf', 'uploads/annotation', 'uploads/temp',
        'logs', 'static', 'app', 'app/templates', 'app/function'
    ]
    
    missing_dirs = []
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"   ✅ {directory}")
        else:
            print(f"   ❌ {directory} - 不存在")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n   创建缺少的目录...")
        for directory in missing_dirs:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"   ✅ 创建目录: {directory}")
            except Exception as e:
                print(f"   ❌ 创建目录失败 {directory}: {str(e)}")
                return False
    
    return True

def test_file_permissions():
    """测试文件权限"""
    print("\n🔐 文件权限检查:")
    
    # 检查上传目录写权限
    test_dirs = ['uploads', 'logs']
    
    for directory in test_dirs:
        if os.path.exists(directory):
            if os.access(directory, os.W_OK):
                print(f"   ✅ {directory} - 可写")
            else:
                print(f"   ❌ {directory} - 无写权限")
                return False
        else:
            print(f"   ⚠️ {directory} - 目录不存在")
    
    return True

def test_environment_config():
    """测试环境配置"""
    print("\n⚙️ 环境配置检查:")
    
    if os.path.exists('.env'):
        print("   ✅ .env 文件存在")
        
        # 检查关键配置项
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        required_configs = [
            'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME',
            'SECRET_KEY', 'DASHSCOPE_API_KEY'
        ]
        
        missing_configs = []
        for config in required_configs:
            if config in env_content and f'{config}=your-' not in env_content:
                print(f"   ✅ {config} - 已配置")
            else:
                print(f"   ⚠️ {config} - 需要配置")
                missing_configs.append(config)
        
        if missing_configs:
            print(f"   请配置: {', '.join(missing_configs)}")
            return False
    else:
        print("   ❌ .env 文件不存在")
        print("   请运行: python setup_database.py")
        return False
    
    return True

def test_port_availability():
    """测试端口可用性"""
    print("\n🌐 端口可用性检查:")
    
    ports_to_check = [5000, 3306]  # Flask默认端口和MySQL端口
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                if port == 3306:
                    print(f"   ✅ 端口 {port} (MySQL) - 服务运行中")
                else:
                    print(f"   ⚠️ 端口 {port} - 已被占用")
            else:
                if port == 5000:
                    print(f"   ✅ 端口 {port} (Flask) - 可用")
                else:
                    print(f"   ❌ 端口 {port} (MySQL) - 服务未运行")
        except Exception as e:
            print(f"   ❌ 端口 {port} - 检查失败: {str(e)}")
        finally:
            sock.close()
    
    return True

def test_system_resources():
    """测试系统资源"""
    print("\n💻 系统资源检查:")
    
    try:
        import psutil
        
        # 检查内存
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"   内存: {memory_gb:.1f}GB 总计, {memory.percent}% 已使用")
        
        if memory_gb < 4:
            print("   ⚠️ 内存可能不足，推荐8GB+")
        else:
            print("   ✅ 内存充足")
        
        # 检查磁盘空间
        disk = psutil.disk_usage('.')
        disk_gb = disk.free / (1024**3)
        print(f"   磁盘: {disk_gb:.1f}GB 可用空间")
        
        if disk_gb < 10:
            print("   ⚠️ 磁盘空间不足，推荐50GB+")
        else:
            print("   ✅ 磁盘空间充足")
        
        # 检查CPU
        cpu_count = psutil.cpu_count()
        print(f"   CPU: {cpu_count} 核心")
        
        if cpu_count < 2:
            print("   ⚠️ CPU核心数较少，推荐4核+")
        else:
            print("   ✅ CPU配置合适")
        
        return True
        
    except ImportError:
        print("   ⚠️ psutil未安装，跳过系统资源检查")
        return True

def test_api_connectivity():
    """测试API连通性"""
    print("\n🌍 API连通性检查:")
    
    # 测试网络连接
    try:
        response = urllib.request.urlopen('https://www.baidu.com', timeout=5)
        if response.getcode() == 200:
            print("   ✅ 网络连接正常")
        else:
            print("   ⚠️ 网络连接异常")
            return False
    except Exception as e:
        print(f"   ❌ 网络连接失败: {str(e)}")
        return False
    
    # 测试阿里云API（如果配置了密钥）
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if api_key and api_key != 'your-dashscope-api-key':
            print("   ✅ 阿里云API密钥已配置")
            # 这里可以添加实际的API测试
        else:
            print("   ⚠️ 阿里云API密钥未配置")
    except Exception as e:
        print(f"   ⚠️ API配置检查失败: {str(e)}")
    
    return True

def generate_report(results):
    """生成测试报告"""
    print("\n" + "="*60)
    print("部署环境测试报告")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"测试结果: {passed}/{total} 项通过")
    print()
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print()
    
    if passed == total:
        print("🎉 所有测试通过！系统已准备就绪。")
        print()
        print("下一步操作:")
        print("1. 启动应用: python app.py")
        print("2. 访问系统: http://localhost:5000")
        print("3. 使用管理员账户登录: admin / admin123")
    else:
        print("⚠️ 部分测试失败，请解决问题后重新测试。")
        print()
        print("常见解决方案:")
        print("1. 安装缺少的依赖: pip install -r requirements.txt")
        print("2. 配置数据库: python setup_database.py")
        print("3. 检查环境配置: 编辑 .env 文件")
    
    # 保存报告到文件
    with open('deployment_test_report.txt', 'w', encoding='utf-8') as f:
        f.write(f"部署环境测试报告\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试结果: {passed}/{total} 项通过\n\n")
        
        for test_name, result in results.items():
            status = "通过" if result else "失败"
            f.write(f"{test_name}: {status}\n")
    
    print(f"\n📄 详细报告已保存到: deployment_test_report.txt")

def main():
    """主函数"""
    print("PPT翻译系统 - 部署环境测试")
    print("="*60)
    
    # 运行所有测试
    tests = [
        ("Python版本", test_python_version),
        ("Python包", test_required_packages),
        ("数据库连接", test_database_connection),
        ("目录结构", test_directories),
        ("文件权限", test_file_permissions),
        ("环境配置", test_environment_config),
        ("端口可用性", test_port_availability),
        ("系统资源", test_system_resources),
        ("API连通性", test_api_connectivity)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            results[test_name] = False
    
    # 生成报告
    generate_report(results)
    
    return all(results.values())

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
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)
