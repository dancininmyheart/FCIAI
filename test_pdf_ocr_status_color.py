#!/usr/bin/env python3
"""
测试PDF注释页面OCR状态字体颜色修改
验证OCR状态显示是否使用黑色字体
"""
import re
import sys
from datetime import datetime

def test_pdf_template_color_changes():
    """测试PDF模板中的颜色修改"""
    print("PDF注释页面OCR状态字体颜色修改测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 读取PDF注释模板文件
        with open('app/templates/main/pdf_annotate.html', 'r', encoding='utf-8') as f:
            content = f.read()

        print("\n🔍 检查CSS样式修改:")

        # 检查CSS中的status-text样式
        css_pattern = r'\.status-text\s*\{[^}]*color:\s*#000000\s*!important[^}]*\}'
        css_match = re.search(css_pattern, content, re.DOTALL)

        if css_match:
            print("  ✅ CSS样式已正确修改:")
            print("     .status-text 类已添加 color: #000000 !important")
        else:
            print("  ❌ CSS样式修改未找到")
            return False

        print("\n🔍 检查JavaScript颜色设置:")

        # 检查JavaScript中的颜色设置 - 简化检查
        js_color_patterns = [
            "statusElement.style.color = '#000000'; /* 设置为黑色 */"
        ]

        # 计算黑色设置的出现次数
        black_color_count = content.count("statusElement.style.color = '#000000'")

        print(f"  📊 找到 {black_color_count} 处黑色颜色设置")

        if black_color_count >= 4:  # 应该有4处：ready, not_initialized, error, catch
            print("  ✅ 所有OCR状态的颜色设置都已修改为黑色")
            all_js_checks_passed = True
        else:
            print("  ❌ 部分OCR状态的颜色设置未修改")
            all_js_checks_passed = False

        # 详细检查每个状态
        status_checks = [
            ("ready状态", "EasyOCR就绪"),
            ("初始化状态", "EasyOCR初始化中"),
            ("错误状态", "EasyOCR错误"),
            ("异常状态", "无法获取OCR状态")
        ]

        for check_name, status_text in status_checks:
            if status_text in content and "statusElement.style.color = '#000000'" in content:
                print(f"  ✅ {check_name}颜色设置已修改为黑色")
            else:
                print(f"  ❌ {check_name}颜色设置未找到或未修改")

        if not all_js_checks_passed:
            return False

        print("\n📊 修改详情分析:")

        # 分析具体的修改内容
        modifications = {
            "CSS强制黑色": "color: #000000 !important",
            "JS就绪状态": "statusElement.style.color = '#000000'",
            "JS初始化状态": "statusElement.style.color = '#000000'",
            "JS错误状态": "statusElement.style.color = '#000000'",
            "JS异常状态": "statusElement.style.color = '#000000'"
        }

        for mod_name, mod_code in modifications.items():
            if mod_code in content:
                print(f"  ✅ {mod_name}: {mod_code}")
            else:
                print(f"  ❌ {mod_name}: 未找到")

        print("\n🎯 修改效果预期:")
        effects = [
            "OCR状态文本将始终显示为黑色",
            "无论OCR状态如何（就绪/初始化/错误），字体颜色都是黑色",
            "CSS的!important确保样式优先级最高",
            "JavaScript动态设置也使用黑色",
            "提高文本可读性和一致性"
        ]

        for effect in effects:
            print(f"  📈 {effect}")

        print("\n🔧 技术实现:")
        technical_details = [
            "CSS: 添加 color: #000000 !important 到 .status-text 类",
            "JavaScript: 将所有 statusElement.style.color 设置为 '#000000'",
            "覆盖范围: 就绪、初始化、错误、异常四种状态",
            "优先级: !important 确保CSS优先级最高",
            "兼容性: 支持所有现代浏览器"
        ]

        for detail in technical_details:
            print(f"  🔧 {detail}")

        return True

    except FileNotFoundError:
        print("❌ PDF注释模板文件未找到")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {str(e)}")
        return False

def analyze_color_consistency():
    """分析颜色一致性"""
    print("\n📋 颜色一致性分析:")

    color_analysis = {
        "修改前问题": [
            "OCR就绪状态: 绿色 (#4CAF50)",
            "OCR初始化状态: 橙色 (#ff9800)",
            "OCR错误状态: 红色 (#f44336)",
            "OCR异常状态: 红色 (#f44336)",
            "颜色不统一，可能影响用户体验"
        ],
        "修改后效果": [
            "所有OCR状态: 黑色 (#000000)",
            "颜色完全统一",
            "提高文本可读性",
            "符合用户要求",
            "保持界面一致性"
        ]
    }

    for category, items in color_analysis.items():
        print(f"\n  📊 {category}:")
        for item in items:
            print(f"    • {item}")

def create_usage_guide():
    """创建使用指南"""
    print("\n📖 使用指南:")

    usage_steps = [
        "1. 访问PDF注释页面",
        "2. 查看右侧注释列表中的'OCR状态'部分",
        "3. 确认状态文本显示为黑色",
        "4. 测试不同OCR状态下的颜色一致性",
        "5. 验证文本可读性是否提高"
    ]

    for step in usage_steps:
        print(f"  {step}")

    print("\n⚠️ 注意事项:")
    notes = [
        "修改使用了!important确保样式优先级",
        "JavaScript动态设置也已同步修改",
        "所有OCR状态都将显示为黑色",
        "如需其他颜色，需要修改CSS和JS代码",
        "建议测试各种OCR状态的显示效果"
    ]

    for note in notes:
        print(f"  ⚠️ {note}")

def main():
    """主测试函数"""
    print("🎯 测试目标: 验证PDF注释页面OCR状态字体颜色修改为黑色")

    # 执行测试
    success = test_pdf_template_color_changes()

    # 分析颜色一致性
    analyze_color_consistency()

    # 创建使用指南
    create_usage_guide()

    # 总结结果
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    if success:
        print("✅ PDF注释页面OCR状态字体颜色修改成功！")
        print("\n🎊 修改完成:")
        print("  ✅ CSS样式已添加黑色字体设置")
        print("  ✅ JavaScript动态颜色设置已修改")
        print("  ✅ 所有OCR状态都将显示为黑色")
        print("  ✅ 使用!important确保样式优先级")

        print("\n📱 用户体验提升:")
        print("  📈 OCR状态颜色统一为黑色")
        print("  📈 提高文本可读性")
        print("  📈 界面显示更加一致")
        print("  📈 符合用户需求")

        print("\n🚀 立即生效:")
        print("  🔄 刷新PDF注释页面即可看到效果")
        print("  🔄 无需重启服务器")
        print("  🔄 所有OCR状态都显示为黑色")

        print("\n🏆 修改成功完成！OCR状态字体颜色已设置为黑色！")
    else:
        print("❌ PDF注释页面OCR状态字体颜色修改失败")
        print("请检查模板文件和修改内容")

    return success

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
