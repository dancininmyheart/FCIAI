#!/usr/bin/env python3
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
        ".\find_send_file_issues.py",
    ]
    
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
    print("\n请重启应用以应用更改")

if __name__ == "__main__":
    main()
