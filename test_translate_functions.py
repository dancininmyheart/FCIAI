"""
测试翻译函数
"""
import asyncio
from app.function.translate_deepseek_async import translate_deepseek_async
from app.function.translate_gpt4o_async import translate_gpt4o_async

async def test_translation():
    """测试翻译功能"""
    # 测试文本
    test_text = "Hello, world!\nThis is a test.\nHow are you?"
    
    # 测试停止词和自定义翻译
    stop_words = ["Hello"]
    custom_translations = {"test": "测试"}
    
    print("测试DeepSeek翻译功能...")
    try:
        result = await translate_deepseek_async(
            text=test_text,
            field="通用",
            stop_words=stop_words,
            custom_translations=custom_translations,
            source_language="en",
            target_language="zh"
        )
        print("DeepSeek翻译结果:")
        for source, target in result.items():
            print(f"  {source} -> {target}")
    except Exception as e:
        print(f"DeepSeek翻译失败: {e}")
    
    print("\n测试GPT翻译功能...")
    try:
        result = await translate_gpt4o_async(
            text=test_text,
            field="通用",
            stop_words=stop_words,
            custom_translations=custom_translations,
            source_language="en",
            target_language="zh"
        )
        print("GPT翻译结果:")
        for source, target in result.items():
            print(f"  {source} -> {target}")
    except Exception as e:
        print(f"GPT翻译失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_translation())
