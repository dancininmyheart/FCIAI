#!/usr/bin/env python3
"""
项目函数分析和清理工具
分析项目中的所有函数，识别冗余内容并提供整合建议
"""
import os
import ast
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple

def analyze_python_file(file_path: str) -> Dict:
    """分析Python文件中的函数"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args],
                    'docstring': ast.get_docstring(node),
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'line': node.lineno,
                    'methods': [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                else:
                    module = node.module or ''
                    imports.extend([f"{module}.{alias.name}" for alias in node.names])
        
        return {
            'file': file_path,
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'line_count': len(content.split('\n'))
        }
    except Exception as e:
        print(f"分析文件 {file_path} 时出错: {e}")
        return {'file': file_path, 'functions': [], 'classes': [], 'imports': [], 'line_count': 0}

def find_duplicate_functions(file_analyses: List[Dict]) -> Dict:
    """查找重复的函数"""
    function_map = {}
    duplicates = {}
    
    for analysis in file_analyses:
        for func in analysis['functions']:
            func_name = func['name']
            if func_name not in function_map:
                function_map[func_name] = []
            function_map[func_name].append({
                'file': analysis['file'],
                'line': func['line'],
                'args': func['args'],
                'docstring': func['docstring'],
                'is_async': func['is_async']
            })
    
    # 找出出现在多个文件中的函数
    for func_name, occurrences in function_map.items():
        if len(occurrences) > 1:
            duplicates[func_name] = occurrences
    
    return duplicates

def analyze_translation_functions():
    """分析翻译相关函数的冗余"""
    translation_functions = {
        'translate_local_qwen': {
            'files': ['app/function/local_qwen.py'],
            'purpose': '同步翻译函数（旧版）',
            'status': '已弃用，被translate_qwen替代'
        },
        'translate_qwen': {
            'files': ['app/function/local_qwen.py', 'app/function/translate_by_qwen.py'],
            'purpose': '同步翻译函数（新版阿里云API）',
            'status': '当前使用'
        },
        'translate_async': {
            'files': ['app/function/local_qwen_async.py'],
            'purpose': '异步翻译函数（新版阿里云API）',
            'status': '当前使用'
        },
        'translate_by_fields': {
            'files': ['app/function/local_qwen.py', 'app/function/translate_by_qwen.py'],
            'purpose': '按领域翻译的底层函数',
            'status': '重复实现'
        },
        'translate_by_fields_async': {
            'files': ['app/function/local_qwen_async.py'],
            'purpose': '按领域翻译的异步底层函数',
            'status': '当前使用'
        },
        'get_field': {
            'files': ['app/function/local_qwen.py', 'app/function/translate_by_qwen.py'],
            'purpose': '获取文本领域',
            'status': '重复实现'
        },
        'get_field_async': {
            'files': ['app/function/local_qwen_async.py'],
            'purpose': '异步获取文本领域',
            'status': '当前使用'
        }
    }
    
    return translation_functions

def analyze_ppt_processing_functions():
    """分析PPT处理函数的冗余"""
    ppt_functions = {
        'process_presentation': {
            'files': ['app/function/ppt_translate.py', 'app/function/ppt_translate_async.py'],
            'purpose': 'PPT翻译主函数',
            'status': 'ppt_translate.py版本已弃用，使用async版本'
        },
        'process_presentation_async': {
            'files': ['app/function/ppt_translate_async.py'],
            'purpose': '异步PPT翻译主函数',
            'status': '当前使用'
        },
        'process_presentation_add_annotations': {
            'files': ['app/function/ppt_translate.py', 'app/function/ppt_translate_async.py'],
            'purpose': '带注释PPT翻译函数',
            'status': 'ppt_translate.py版本已弃用，使用async版本'
        },
        'process_presentation_add_annotations_async': {
            'files': ['app/function/ppt_translate_async.py'],
            'purpose': '异步带注释PPT翻译函数',
            'status': '当前使用'
        }
    }
    
    return ppt_functions

def analyze_utility_functions():
    """分析工具函数的冗余"""
    utility_functions = {
        'build_map': {
            'files': ['app/function/local_qwen.py', 'app/function/translate_by_qwen.py', 'app/function/local_qwen_async.py'],
            'purpose': '构建翻译映射字典',
            'status': '重复实现，应该统一'
        },
        'parse_formatted_text': {
            'files': ['app/function/local_qwen.py', 'app/function/translate_by_qwen.py'],
            'purpose': '解析JSON格式翻译结果',
            'status': '重复实现'
        },
        'parse_formatted_text_async': {
            'files': ['app/function/local_qwen_async.py'],
            'purpose': '异步解析JSON格式翻译结果',
            'status': '当前使用'
        },
        'find_most_similar': {
            'files': ['app/function/ppt_translate.py'],
            'purpose': '查找最相似文本',
            'status': '在多个地方被调用'
        }
    }
    
    return utility_functions

def create_cleanup_recommendations():
    """创建清理建议"""
    recommendations = {
        '删除冗余文件': {
            'app/function/local_qwen.py': {
                'reason': '旧版翻译API，已被新版替代',
                'replacement': 'app/function/translate_by_qwen.py (同步) 和 app/function/local_qwen_async.py (异步)',
                'action': '删除整个文件'
            }
        },
        '整合重复函数': {
            'build_map': {
                'reason': '在多个文件中重复实现',
                'action': '移动到独立的utils模块',
                'target_file': 'app/utils/translation_utils.py'
            },
            'parse_formatted_text': {
                'reason': '在多个文件中重复实现',
                'action': '移动到独立的utils模块',
                'target_file': 'app/utils/translation_utils.py'
            },
            'get_field': {
                'reason': '在translate_by_qwen.py中重复实现',
                'action': '删除translate_by_qwen.py中的版本，统一使用local_qwen_async.py'
            }
        },
        '简化PPT处理': {
            'ppt_translate.py': {
                'reason': '同步版本已被异步版本替代',
                'action': '删除同步版本的主要函数，保留工具函数',
                'keep_functions': ['find_most_similar', 'compare_strings_ignore_spaces', '形状处理相关函数']
            }
        },
        '统一API调用': {
            'translation_api': {
                'reason': '统一使用新的阿里云API',
                'action': '确保所有翻译调用都使用local_qwen_async.py或translate_by_qwen.py',
                'remove': '所有对local_qwen.py的引用'
            }
        }
    }
    
    return recommendations

def main():
    """主函数"""
    print("项目函数分析和清理工具")
    print("=" * 60)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 分析主要功能模块
    function_modules = [
        'app/function/ppt_translate.py',
        'app/function/ppt_translate_async.py',
        'app/function/local_qwen.py',
        'app/function/local_qwen_async.py',
        'app/function/translate_by_qwen.py',
        'app/function/page_based_translation.py',
        'app/function/pdf_annotate_async.py',
        'app/function/adjust_text_size.py'
    ]
    
    print("\n🔍 分析功能模块:")
    file_analyses = []
    for module in function_modules:
        if os.path.exists(module):
            analysis = analyze_python_file(module)
            file_analyses.append(analysis)
            print(f"  ✓ {module}: {len(analysis['functions'])} 个函数, {analysis['line_count']} 行代码")
        else:
            print(f"  ✗ {module}: 文件不存在")
    
    # 分析重复函数
    print("\n🔍 查找重复函数:")
    duplicates = find_duplicate_functions(file_analyses)
    if duplicates:
        for func_name, occurrences in duplicates.items():
            print(f"  📋 {func_name}:")
            for occ in occurrences:
                async_marker = " (异步)" if occ['is_async'] else ""
                print(f"    - {occ['file']}:{occ['line']}{async_marker}")
    else:
        print("  ✓ 未发现重复的函数名")
    
    # 分析翻译函数
    print("\n🔍 翻译函数分析:")
    translation_funcs = analyze_translation_functions()
    for func_name, info in translation_funcs.items():
        print(f"  📋 {func_name}:")
        print(f"    文件: {', '.join(info['files'])}")
        print(f"    用途: {info['purpose']}")
        print(f"    状态: {info['status']}")
    
    # 分析PPT处理函数
    print("\n🔍 PPT处理函数分析:")
    ppt_funcs = analyze_ppt_processing_functions()
    for func_name, info in ppt_funcs.items():
        print(f"  📋 {func_name}:")
        print(f"    文件: {', '.join(info['files'])}")
        print(f"    用途: {info['purpose']}")
        print(f"    状态: {info['status']}")
    
    # 分析工具函数
    print("\n🔍 工具函数分析:")
    utility_funcs = analyze_utility_functions()
    for func_name, info in utility_funcs.items():
        print(f"  📋 {func_name}:")
        print(f"    文件: {', '.join(info['files'])}")
        print(f"    用途: {info['purpose']}")
        print(f"    状态: {info['status']}")
    
    # 生成清理建议
    print("\n📋 清理建议:")
    recommendations = create_cleanup_recommendations()
    for category, items in recommendations.items():
        print(f"\n  🔧 {category}:")
        for item_name, details in items.items():
            print(f"    📁 {item_name}:")
            for key, value in details.items():
                print(f"      {key}: {value}")
    
    # 生成详细报告
    create_detailed_report(file_analyses, duplicates, translation_funcs, ppt_funcs, utility_funcs, recommendations)
    
    print(f"\n✅ 分析完成！详细报告已保存到 function_cleanup_report.md")

def create_detailed_report(file_analyses, duplicates, translation_funcs, ppt_funcs, utility_funcs, recommendations):
    """创建详细的清理报告"""
    report = f"""
# 项目函数分析和清理报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 总体统计

### 分析的文件
"""
    
    for analysis in file_analyses:
        report += f"- **{analysis['file']}**: {len(analysis['functions'])} 个函数, {analysis['line_count']} 行代码\n"
    
    report += f"""
### 重复函数统计
共发现 {len(duplicates)} 个重复函数名

## 🔍 详细分析

### 翻译函数冗余分析
"""
    
    for func_name, info in translation_funcs.items():
        report += f"""
#### {func_name}
- **文件**: {', '.join(info['files'])}
- **用途**: {info['purpose']}
- **状态**: {info['status']}
"""
    
    report += """
### PPT处理函数冗余分析
"""
    
    for func_name, info in ppt_funcs.items():
        report += f"""
#### {func_name}
- **文件**: {', '.join(info['files'])}
- **用途**: {info['purpose']}
- **状态**: {info['status']}
"""
    
    report += """
### 工具函数冗余分析
"""
    
    for func_name, info in utility_funcs.items():
        report += f"""
#### {func_name}
- **文件**: {', '.join(info['files'])}
- **用途**: {info['purpose']}
- **状态**: {info['status']}
"""
    
    report += """
## 🔧 清理建议

### 立即执行的清理任务

#### 1. 删除冗余文件
- **app/function/local_qwen.py**: 旧版翻译API，已被新版替代
  - 替代方案: app/function/translate_by_qwen.py (同步) 和 app/function/local_qwen_async.py (异步)
  - 操作: 删除整个文件

#### 2. 整合重复函数
- **build_map**: 在多个文件中重复实现
  - 操作: 移动到 app/utils/translation_utils.py
- **parse_formatted_text**: 在多个文件中重复实现
  - 操作: 移动到 app/utils/translation_utils.py
- **get_field**: 在translate_by_qwen.py中重复实现
  - 操作: 删除重复版本，统一使用async版本

#### 3. 简化PPT处理
- **ppt_translate.py**: 同步版本已被异步版本替代
  - 操作: 删除主要翻译函数，保留工具函数
  - 保留: find_most_similar, compare_strings_ignore_spaces, 形状处理相关函数

#### 4. 统一API调用
- **translation_api**: 统一使用新的阿里云API
  - 操作: 确保所有翻译调用都使用新版API
  - 删除: 所有对local_qwen.py的引用

### 清理后的文件结构

```
app/function/
├── ppt_translate_async.py          # 主要PPT翻译功能（异步）
├── ppt_translate_utils.py          # PPT处理工具函数（从ppt_translate.py提取）
├── translate_by_qwen.py            # 阿里云翻译API（同步）
├── local_qwen_async.py             # 阿里云翻译API（异步）
├── page_based_translation.py       # 基于页面的翻译
├── pdf_annotate_async.py           # PDF注释功能
└── adjust_text_size.py             # 文本大小调整

app/utils/
├── translation_utils.py            # 翻译相关工具函数
└── ...
```

## 🎯 清理效果预期

### 代码减少
- 删除约 500+ 行冗余代码
- 减少 1 个完整的模块文件
- 整合 3+ 个重复函数

### 维护性提升
- 统一API调用方式
- 减少代码重复
- 清晰的模块职责

### 性能优化
- 减少导入开销
- 统一使用高效的异步API
- 简化调用链路

## ✅ 执行计划

1. **第一阶段**: 创建工具函数模块
   - 创建 app/utils/translation_utils.py
   - 移动重复的工具函数

2. **第二阶段**: 更新引用
   - 更新所有对重复函数的引用
   - 测试功能完整性

3. **第三阶段**: 删除冗余文件
   - 删除 app/function/local_qwen.py
   - 清理 ppt_translate.py 中的冗余函数

4. **第四阶段**: 验证和测试
   - 运行完整的功能测试
   - 确保所有功能正常工作

## 📝 注意事项

- 在删除任何文件前，确保所有引用都已更新
- 保留关键的工具函数，如形状处理相关函数
- 测试翻译功能的完整性
- 确保异步和同步版本都能正常工作
"""
    
    with open('function_cleanup_report.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    main()
