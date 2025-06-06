#!/usr/bin/env python3
"""
LibreOffice UNO接口安装和配置脚本
自动检测、安装和配置LibreOffice UNO Python SDK
"""
import os
import sys
import platform
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LibreOfficeUNOSetup:
    """LibreOffice UNO安装配置器"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
    def check_libreoffice_installation(self) -> bool:
        """检查LibreOffice是否已安装"""
        logger.info("检查LibreOffice安装状态...")
        
        if self.system == "Windows":
            possible_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
            ]
        elif self.system == "Linux":
            possible_paths = [
                "/usr/bin/libreoffice",
                "/usr/local/bin/libreoffice",
                "/opt/libreoffice/program/soffice"
            ]
        elif self.system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            ]
        else:
            logger.error(f"不支持的操作系统: {self.system}")
            return False
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✅ 找到LibreOffice: {path}")
                return True
        
        logger.error("❌ 未找到LibreOffice安装")
        return False
    
    def install_libreoffice(self) -> bool:
        """安装LibreOffice"""
        logger.info("开始安装LibreOffice...")
        
        if self.system == "Windows":
            return self._install_libreoffice_windows()
        elif self.system == "Linux":
            return self._install_libreoffice_linux()
        elif self.system == "Darwin":
            return self._install_libreoffice_macos()
        else:
            logger.error(f"不支持的操作系统: {self.system}")
            return False
    
    def _install_libreoffice_windows(self) -> bool:
        """Windows下安装LibreOffice"""
        logger.info("Windows系统请手动下载并安装LibreOffice:")
        logger.info("1. 访问: https://www.libreoffice.org/download/download/")
        logger.info("2. 下载Windows版本")
        logger.info("3. 运行安装程序")
        logger.info("4. 确保选择'Python脚本支持'选项")
        
        input("安装完成后按回车键继续...")
        return self.check_libreoffice_installation()
    
    def _install_libreoffice_linux(self) -> bool:
        """Linux下安装LibreOffice"""
        try:
            # 尝试使用包管理器安装
            distro_commands = [
                # Ubuntu/Debian
                ["sudo", "apt-get", "update"],
                ["sudo", "apt-get", "install", "-y", "libreoffice", "libreoffice-script-provider-python"],
                
                # 如果上面失败，尝试snap
                ["sudo", "snap", "install", "libreoffice"],
                
                # CentOS/RHEL/Fedora
                ["sudo", "yum", "install", "-y", "libreoffice"],
                ["sudo", "dnf", "install", "-y", "libreoffice"]
            ]
            
            for cmd in distro_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        logger.info(f"✅ 执行成功: {' '.join(cmd)}")
                        if self.check_libreoffice_installation():
                            return True
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            logger.error("❌ 自动安装失败，请手动安装LibreOffice")
            return False
            
        except Exception as e:
            logger.error(f"安装LibreOffice时出错: {e}")
            return False
    
    def _install_libreoffice_macos(self) -> bool:
        """macOS下安装LibreOffice"""
        try:
            # 尝试使用Homebrew安装
            result = subprocess.run(
                ["brew", "install", "--cask", "libreoffice"],
                capture_output=True, text=True, timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ 通过Homebrew安装LibreOffice成功")
                return True
            else:
                logger.info("Homebrew安装失败，请手动安装:")
                logger.info("1. 访问: https://www.libreoffice.org/download/download/")
                logger.info("2. 下载macOS版本")
                logger.info("3. 安装到Applications文件夹")
                
                input("安装完成后按回车键继续...")
                return self.check_libreoffice_installation()
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            logger.info("未找到Homebrew或安装失败，请手动安装LibreOffice")
            return False
    
    def find_uno_path(self) -> str:
        """查找UNO Python路径"""
        logger.info("查找LibreOffice UNO Python路径...")
        
        if self.system == "Windows":
            possible_paths = [
                r"C:\Program Files\LibreOffice\program",
                r"C:\Program Files (x86)\LibreOffice\program"
            ]
        elif self.system == "Linux":
            possible_paths = [
                "/usr/lib/libreoffice/program",
                "/opt/libreoffice/program",
                "/usr/local/lib/libreoffice/program"
            ]
        elif self.system == "Darwin":
            possible_paths = [
                "/Applications/LibreOffice.app/Contents/Resources/program"
            ]
        else:
            return ""
        
        for path in possible_paths:
            uno_py = os.path.join(path, "uno.py")
            if os.path.exists(uno_py):
                logger.info(f"✅ 找到UNO路径: {path}")
                return path
        
        logger.error("❌ 未找到UNO Python路径")
        return ""
    
    def setup_uno_environment(self) -> bool:
        """设置UNO环境"""
        logger.info("配置LibreOffice UNO环境...")
        
        uno_path = self.find_uno_path()
        if not uno_path:
            return False
        
        try:
            # 添加UNO路径到Python路径
            if uno_path not in sys.path:
                sys.path.insert(0, uno_path)
            
            # 设置环境变量
            if self.system == "Windows":
                os.environ["PATH"] = uno_path + os.pathsep + os.environ.get("PATH", "")
            else:
                os.environ["PYTHONPATH"] = uno_path + os.pathsep + os.environ.get("PYTHONPATH", "")
            
            # 测试UNO导入
            try:
                import uno
                logger.info("✅ UNO模块导入成功")
                return True
            except ImportError as e:
                logger.error(f"❌ UNO模块导入失败: {e}")
                return False
                
        except Exception as e:
            logger.error(f"配置UNO环境失败: {e}")
            return False
    
    def create_uno_wrapper_script(self) -> bool:
        """创建UNO包装脚本"""
        logger.info("创建UNO包装脚本...")
        
        uno_path = self.find_uno_path()
        if not uno_path:
            return False
        
        wrapper_content = f'''#!/usr/bin/env python3
"""
LibreOffice UNO包装脚本
自动配置UNO环境并导入必要模块
"""
import sys
import os

# 添加LibreOffice UNO路径
UNO_PATH = r"{uno_path}"
if UNO_PATH not in sys.path:
    sys.path.insert(0, UNO_PATH)

# 设置环境变量
if os.name == "nt":  # Windows
    os.environ["PATH"] = UNO_PATH + os.pathsep + os.environ.get("PATH", "")
else:  # Linux/macOS
    os.environ["PYTHONPATH"] = UNO_PATH + os.pathsep + os.environ.get("PYTHONPATH", "")

# 导入UNO模块
try:
    import uno
    from com.sun.star.beans import PropertyValue
    from com.sun.star.connection import NoConnectException
    from com.sun.star.lang import DisposedException
    
    print("✅ LibreOffice UNO模块加载成功")
    UNO_AVAILABLE = True
    
except ImportError as e:
    print(f"❌ LibreOffice UNO模块加载失败: {{e}}")
    UNO_AVAILABLE = False

if __name__ == "__main__":
    if UNO_AVAILABLE:
        print("LibreOffice UNO环境配置成功！")
        print(f"UNO路径: {{UNO_PATH}}")
    else:
        print("LibreOffice UNO环境配置失败！")
'''
        
        try:
            wrapper_path = "uno_wrapper.py"
            with open(wrapper_path, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            
            logger.info(f"✅ UNO包装脚本创建成功: {wrapper_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建UNO包装脚本失败: {e}")
            return False
    
    def test_uno_functionality(self) -> bool:
        """测试UNO功能"""
        logger.info("测试LibreOffice UNO功能...")
        
        try:
            from app.function.libreoffice_uno_color import test_uno_color_preservation
            return test_uno_color_preservation()
        except ImportError:
            logger.error("无法导入UNO颜色保护模块")
            return False
    
    def run_setup(self) -> bool:
        """运行完整安装配置流程"""
        logger.info("=" * 60)
        logger.info("LibreOffice UNO接口安装配置")
        logger.info("=" * 60)
        
        # 1. 检查LibreOffice安装
        if not self.check_libreoffice_installation():
            if not self.install_libreoffice():
                return False
        
        # 2. 配置UNO环境
        if not self.setup_uno_environment():
            logger.error("UNO环境配置失败")
            return False
        
        # 3. 创建包装脚本
        if not self.create_uno_wrapper_script():
            logger.warning("创建包装脚本失败，但不影响主要功能")
        
        # 4. 测试功能
        if self.test_uno_functionality():
            logger.info("🎉 LibreOffice UNO接口配置成功！")
            return True
        else:
            logger.error("❌ UNO功能测试失败")
            return False


def main():
    """主函数"""
    setup = LibreOfficeUNOSetup()
    
    try:
        success = setup.run_setup()
        
        if success:
            print("\n" + "=" * 60)
            print("🎉 LibreOffice UNO接口配置完成！")
            print("=" * 60)
            print("\n✅ 现在您可以使用UNO接口进行PPT颜色保护翻译:")
            print("  from app.function.libreoffice_uno_color import translate_ppt_with_uno_color_preservation")
            print("  translate_ppt_with_uno_color_preservation(ppt_path, translation_map)")
            print("\n🔧 UNO接口的优势:")
            print("  • 精确的颜色控制")
            print("  • 完整的格式保护")
            print("  • 原生LibreOffice支持")
            print("  • 跨平台兼容性")
        else:
            print("\n" + "=" * 60)
            print("❌ LibreOffice UNO接口配置失败")
            print("=" * 60)
            print("\n🔧 手动配置步骤:")
            print("1. 确保LibreOffice已正确安装")
            print("2. 找到LibreOffice的program目录")
            print("3. 将该目录添加到Python路径")
            print("4. 测试导入uno模块")
        
        input("\n按回车键退出...")
        return success
        
    except KeyboardInterrupt:
        print("\n配置被用户中断")
        return False
    except Exception as e:
        logger.error(f"配置过程中出现异常: {e}")
        return False


if __name__ == "__main__":
    main()
