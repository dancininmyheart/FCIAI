#!/usr/bin/env python3
"""
查找项目中所有使用send_file和attachment_filename的地方
并提供修复建议
"""
import os
import re
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_send_file_issues(root_dir="."):
    """查找send_file相关问题"""
    logger.info("🔍 搜索send_file相关问题")
    logger.info("=" * 60)
    
    issues_found = []
    files_checked = 0
    
    # 要搜索的模式
    patterns = [
        (r'attachment_filename\s*=', 'attachment_filename参数（已废弃）'),
        (r'send_file\s*\([^)]*attachment_filename', 'send_file使用attachment_filename'),
        (r'from\s+flask\s+import.*send_file', 'Flask send_file导入'),
    ]
    
    # 要检查的文件扩展名
    extensions = ['.py']
    
    for root, dirs, files in os.walk(root_dir):
        # 跳过一些目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                files_checked += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for i, line in enumerate(lines, 1):
                            for pattern, description in patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    issues_found.append({
                                        'file': file_path,
                                        'line': i,
                                        'content': line.strip(),
                                        'issue': description,
                                        'pattern': pattern
                                    })
                                    
                except Exception as e:
                    logger.warning(f"无法读取文件 {file_path}: {e}")
    
    logger.info(f"检查了 {files_checked} 个文件")
    logger.info(f"发现 {len(issues_found)} 个问题")
    
    if issues_found:
        logger.info("\n发现的问题:")
        logger.info("-" * 60)
        
        for issue in issues_found:
            logger.info(f"文件: {issue['file']}")
            logger.info(f"行号: {issue['line']}")
            logger.info(f"问题: {issue['issue']}")
            logger.info(f"代码: {issue['content']}")
            logger.info("-" * 40)
    
    return issues_found


def generate_fix_suggestions(issues):
    """生成修复建议"""
    logger.info("\n🔧 修复建议:")
    logger.info("=" * 60)
    
    attachment_filename_issues = [
        issue for issue in issues 
        if 'attachment_filename' in issue['pattern']
    ]
    
    if attachment_filename_issues:
        logger.info("1. attachment_filename参数修复:")
        logger.info("   将 attachment_filename=filename 替换为 download_name=filename")
        logger.info("")
        logger.info("   修复前:")
        logger.info("   send_file(path, as_attachment=True, attachment_filename=filename)")
        logger.info("")
        logger.info("   修复后:")
        logger.info("   send_file(path, as_attachment=True, download_name=filename)")
        logger.info("")
        
        for issue in attachment_filename_issues:
            logger.info(f"   需要修复: {issue['file']}:{issue['line']}")
        
        logger.info("")
    
    logger.info("2. Flask版本兼容性:")
    logger.info("   - Flask 2.0+ 使用 download_name 参数")
    logger.info("   - Flask 1.x 使用 attachment_filename 参数")
    logger.info("   - 建议升级到Flask 2.0+并使用新参数")
    logger.info("")
    
    logger.info("3. 其他send_file参数:")
    logger.info("   - as_attachment=True: 强制下载")
    logger.info("   - mimetype: 指定MIME类型")
    logger.info("   - conditional=True: 支持条件请求")
    logger.info("   - etag=True: 启用ETag")


def create_fix_script(issues):
    """创建自动修复脚本"""
    script_content = '''#!/usr/bin/env python3
"""
自动修复send_file相关问题
"""
import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """备份文件"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"已备份: {backup_path}")
    return backup_path

def fix_attachment_filename(file_path):
    """修复attachment_filename参数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 备份原文件
        backup_file(file_path)
        
        # 替换attachment_filename为download_name
        pattern = r'attachment_filename\s*='
        replacement = 'download_name='
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 已修复: {file_path}")
            return True
        else:
            print(f"⚠️ 无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    files_to_fix = [
'''
    
    # 添加需要修复的文件
    attachment_filename_files = [
        issue['file'] for issue in issues 
        if 'attachment_filename' in issue['pattern']
    ]
    
    for file_path in set(attachment_filename_files):
        script_content += f'        "{file_path}",\n'
    
    script_content += '''    ]
    
    print("🔧 开始修复send_file问题...")
    print("=" * 50)
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_attachment_filename(file_path):
                fixed_count += 1
        else:
            print(f"⚠️ 文件不存在: {file_path}")
    
    print("=" * 50)
    print(f"修复完成: {fixed_count}/{len(files_to_fix)} 个文件")
    print("\\n请重启应用以应用更改")

if __name__ == "__main__":
    main()
'''
    
    with open('auto_fix_send_file.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info("已生成自动修复脚本: auto_fix_send_file.py")


def main():
    """主函数"""
    logger.info("🔍 Flask send_file问题检测工具")
    logger.info("=" * 80)
    
    # 查找问题
    issues = find_send_file_issues()
    
    if issues:
        # 生成修复建议
        generate_fix_suggestions(issues)
        
        # 创建自动修复脚本
        create_fix_script(issues)
        
        logger.info("\n📋 总结:")
        logger.info(f"发现 {len(issues)} 个问题需要修复")
        logger.info("建议:")
        logger.info("1. 运行 python auto_fix_send_file.py 自动修复")
        logger.info("2. 或手动将 attachment_filename 替换为 download_name")
        logger.info("3. 重启应用测试修复效果")
        
    else:
        logger.info("✅ 未发现send_file相关问题")
    
    return len(issues) == 0


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
        exit(1)
    except Exception as e:
        logger.error(f"执行异常: {e}")
        input("按回车键退出...")
        exit(1)
