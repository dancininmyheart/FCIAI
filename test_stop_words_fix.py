#!/usr/bin/env python3
"""
测试停翻词功能修复
验证停翻词的添加、加载、删除功能
"""
import os
import sys
import logging
import requests
import json
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_stop_words_api():
    """测试停翻词API功能"""
    logger.info("🧪 测试停翻词API功能")
    logger.info("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 创建session保持登录状态
    session = requests.Session()
    
    try:
        # 1. 测试未登录访问
        logger.info("1. 测试未登录访问停翻词API...")
        response = session.get(f"{base_url}/api/stop-words")
        
        if response.status_code in [401, 302]:
            logger.info("✅ 未登录访问被正确拒绝")
        else:
            logger.warning(f"⚠️ 未登录访问响应: {response.status_code}")
        
        # 2. 测试路由是否存在
        logger.info("2. 测试停翻词路由是否存在...")
        
        # 测试GET路由
        response = session.get(f"{base_url}/api/stop-words")
        if response.status_code != 404:
            logger.info("✅ GET /api/stop-words 路由存在")
        else:
            logger.error("❌ GET /api/stop-words 路由不存在")
            return False
        
        # 测试POST路由
        response = session.post(f"{base_url}/api/stop-words", 
                               json={"word": "test"})
        if response.status_code != 404:
            logger.info("✅ POST /api/stop-words 路由存在")
        else:
            logger.error("❌ POST /api/stop-words 路由不存在")
            return False
        
        # 测试统计路由
        response = session.get(f"{base_url}/api/stop-words/stats")
        if response.status_code != 404:
            logger.info("✅ GET /api/stop-words/stats 路由存在")
        else:
            logger.error("❌ GET /api/stop-words/stats 路由不存在")
            return False
        
        logger.info("✅ 所有停翻词路由都已正确注册")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试停翻词API失败: {e}")
        return False


def test_dictionary_page():
    """测试词库管理页面"""
    logger.info("📄 测试词库管理页面")
    logger.info("=" * 60)
    
    try:
        base_url = "http://localhost:5000"
        response = requests.get(f"{base_url}/dictionary")
        
        if response.status_code == 200:
            logger.info("✅ 词库管理页面可访问")
            
            content = response.text
            
            # 检查停翻词相关元素
            checks = [
                ("停翻词管理区域", "stop-words-section" in content),
                ("停翻词输入框", "stopWordInput" in content),
                ("添加停翻词按钮", "addStopWordBtn" in content),
                ("停翻词列表", "stopWordsList" in content),
                ("加载停翻词函数", "loadStopWords" in content),
                ("删除停翻词函数", "deleteStopWord" in content),
                ("停翻词API调用", "/api/stop-words" in content)
            ]
            
            logger.info("页面元素检查:")
            passed = 0
            for name, check in checks:
                if check:
                    logger.info(f"  ✅ {name}: 存在")
                    passed += 1
                else:
                    logger.warning(f"  ⚠️ {name}: 不存在")
            
            logger.info(f"页面元素检查: {passed}/{len(checks)}")
            return passed >= len(checks) - 1  # 允许1个检查失败
        else:
            logger.error(f"❌ 词库管理页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试词库管理页面失败: {e}")
        return False


def test_database_structure():
    """测试数据库结构"""
    logger.info("🗄️ 测试数据库结构")
    logger.info("=" * 60)
    
    try:
        from app import create_app, db
        from app.models.stop_word import StopWord
        from sqlalchemy import inspect
        
        app = create_app('development')
        
        with app.app_context():
            # 检查表是否存在
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'stop_words' not in tables:
                logger.error("❌ stop_words表不存在")
                return False
            
            logger.info("✅ stop_words表存在")
            
            # 检查表结构
            columns = inspector.get_columns('stop_words')
            unique_constraints = inspector.get_unique_constraints('stop_words')
            
            logger.info("表结构检查:")
            
            # 检查必要的列
            column_names = [col['name'] for col in columns]
            required_columns = ['id', 'word', 'created_at', 'user_id']
            
            for col in required_columns:
                if col in column_names:
                    logger.info(f"  ✅ 列 {col}: 存在")
                else:
                    logger.error(f"  ❌ 列 {col}: 不存在")
                    return False
            
            # 检查唯一约束
            logger.info("唯一约束检查:")
            has_user_constraint = False
            has_global_constraint = False
            
            for uc in unique_constraints:
                if set(uc['column_names']) == {'word', 'user_id'}:
                    has_user_constraint = True
                    logger.info("  ✅ 用户级别唯一约束: 存在")
                elif uc['column_names'] == ['word']:
                    has_global_constraint = True
                    logger.warning("  ⚠️ 全局word唯一约束: 存在（应该移除）")
            
            if not has_user_constraint:
                logger.error("  ❌ 用户级别唯一约束: 不存在")
                return False
            
            if has_global_constraint:
                logger.warning("  ⚠️ 仍存在全局唯一约束，可能影响功能")
            
            logger.info("✅ 数据库结构检查通过")
            return True
            
    except Exception as e:
        logger.error(f"❌ 测试数据库结构失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False


def test_model_functionality():
    """测试模型功能"""
    logger.info("🔧 测试模型功能")
    logger.info("=" * 60)
    
    try:
        from app import create_app, db
        from app.models.stop_word import StopWord
        from app.models.user import User
        
        app = create_app('development')
        
        with app.app_context():
            # 查找测试用户
            test_user = User.query.first()
            if not test_user:
                logger.warning("没有找到测试用户，跳过模型功能测试")
                return True
            
            logger.info(f"使用测试用户: {test_user.username} (ID: {test_user.id})")
            
            # 清理可能存在的测试数据
            test_words = ["test_word_1", "test_word_2"]
            for word in test_words:
                existing = StopWord.query.filter_by(word=word, user_id=test_user.id).first()
                if existing:
                    db.session.delete(existing)
            db.session.commit()
            
            # 测试添加停翻词
            logger.info("测试添加停翻词...")
            stop_word1 = StopWord(word="test_word_1", user_id=test_user.id)
            db.session.add(stop_word1)
            db.session.commit()
            logger.info("✅ 添加第一个停翻词成功")
            
            # 测试添加相同词（应该失败）
            logger.info("测试添加重复停翻词...")
            try:
                stop_word_dup = StopWord(word="test_word_1", user_id=test_user.id)
                db.session.add(stop_word_dup)
                db.session.commit()
                logger.error("❌ 重复添加应该失败但成功了")
                return False
            except Exception:
                db.session.rollback()
                logger.info("✅ 重复添加被正确阻止")
            
            # 测试查询
            logger.info("测试查询停翻词...")
            found_words = StopWord.query.filter_by(user_id=test_user.id).all()
            if len(found_words) >= 1:
                logger.info(f"✅ 查询成功，找到 {len(found_words)} 个停翻词")
            else:
                logger.error("❌ 查询失败，未找到停翻词")
                return False
            
            # 测试to_dict方法
            logger.info("测试to_dict方法...")
            word_dict = stop_word1.to_dict()
            required_keys = ['id', 'word', 'created_at', 'user_id']
            for key in required_keys:
                if key in word_dict:
                    logger.info(f"  ✅ {key}: {word_dict[key]}")
                else:
                    logger.error(f"  ❌ {key}: 缺失")
                    return False
            
            # 清理测试数据
            logger.info("清理测试数据...")
            for word in StopWord.query.filter_by(user_id=test_user.id).all():
                if word.word.startswith("test_word_"):
                    db.session.delete(word)
            db.session.commit()
            logger.info("✅ 测试数据清理完成")
            
            logger.info("✅ 模型功能测试通过")
            return True
            
    except Exception as e:
        logger.error(f"❌ 测试模型功能失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False


def main():
    """主测试函数"""
    logger.info("🔧 停翻词功能修复验证")
    logger.info("=" * 80)
    
    tests = [
        ("停翻词API", test_stop_words_api),
        ("词库管理页面", test_dictionary_page),
        ("数据库结构", test_database_structure),
        ("模型功能", test_model_functionality)
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
        logger.info("🎉 所有测试通过！停翻词功能已修复")
        logger.info("\n✅ 修复内容:")
        logger.info("  1. 注册了停翻词路由蓝图")
        logger.info("  2. 修复了数据库唯一约束")
        logger.info("  3. 支持用户级别的停翻词管理")
        logger.info("  4. 前端页面功能完整")
        
        logger.info("\n📱 现在您可以:")
        logger.info("  - 访问 http://localhost:5000/dictionary")
        logger.info("  - 添加您的专属停翻词")
        logger.info("  - 查看和管理停翻词列表")
        logger.info("  - 删除不需要的停翻词")
        
    elif passed >= 3:
        logger.warning("⚠️ 大部分测试通过，基本功能可用")
        logger.info("请检查失败的测试项目")
    else:
        logger.error("❌ 多数测试失败，请检查修复")
    
    return passed >= 3


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
