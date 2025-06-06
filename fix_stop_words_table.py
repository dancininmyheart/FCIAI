#!/usr/bin/env python3
"""
修复停翻词表结构
移除全局唯一约束，添加用户级别的唯一约束
"""
import os
import sys
import logging
from sqlalchemy import text

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_stop_words_table():
    """修复停翻词表结构"""
    try:
        from app import create_app, db
        from app.models.stop_word import StopWord
        
        app = create_app('development')
        
        with app.app_context():
            logger.info("开始修复停翻词表结构...")
            
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'stop_words' not in tables:
                logger.info("停翻词表不存在，创建新表...")
                db.create_all()
                logger.info("✅ 停翻词表创建成功")
                return True
            
            # 检查当前表结构
            columns = inspector.get_columns('stop_words')
            indexes = inspector.get_indexes('stop_words')
            unique_constraints = inspector.get_unique_constraints('stop_words')
            
            logger.info("当前表结构:")
            for col in columns:
                logger.info(f"  列: {col['name']} - {col['type']} - nullable: {col['nullable']}")
            
            logger.info("当前索引:")
            for idx in indexes:
                logger.info(f"  索引: {idx['name']} - 列: {idx['column_names']} - 唯一: {idx['unique']}")
            
            logger.info("当前唯一约束:")
            for uc in unique_constraints:
                logger.info(f"  约束: {uc['name']} - 列: {uc['column_names']}")
            
            # 检查是否需要修复
            needs_fix = False
            
            # 检查是否有全局word唯一约束
            for uc in unique_constraints:
                if uc['column_names'] == ['word']:
                    logger.warning("发现全局word唯一约束，需要修复")
                    needs_fix = True
                    break
            
            # 检查是否缺少用户级别的唯一约束
            has_user_constraint = False
            for uc in unique_constraints:
                if set(uc['column_names']) == {'word', 'user_id'}:
                    has_user_constraint = True
                    break
            
            if not has_user_constraint:
                logger.warning("缺少用户级别的唯一约束，需要修复")
                needs_fix = True
            
            if not needs_fix:
                logger.info("✅ 停翻词表结构正确，无需修复")
                return True
            
            logger.info("开始修复表结构...")
            
            # 备份现有数据
            existing_data = db.session.execute(text("SELECT * FROM stop_words")).fetchall()
            logger.info(f"备份了 {len(existing_data)} 条现有数据")
            
            # 删除表并重新创建
            logger.info("删除现有表...")
            db.session.execute(text("DROP TABLE IF EXISTS stop_words"))
            db.session.commit()
            
            logger.info("重新创建表...")
            db.create_all()
            
            # 恢复数据（去重）
            if existing_data:
                logger.info("恢复数据...")
                restored_count = 0
                skipped_count = 0
                
                # 用于去重的集合
                seen_combinations = set()
                
                for row in existing_data:
                    # 检查是否已存在相同的 (word, user_id) 组合
                    combination = (row[1], row[3])  # (word, user_id)
                    
                    if combination in seen_combinations:
                        skipped_count += 1
                        logger.debug(f"跳过重复数据: word='{row[1]}', user_id={row[3]}")
                        continue
                    
                    seen_combinations.add(combination)
                    
                    try:
                        # 插入数据
                        db.session.execute(text(
                            "INSERT INTO stop_words (word, created_at, user_id) VALUES (:word, :created_at, :user_id)"
                        ), {
                            'word': row[1],
                            'created_at': row[2],
                            'user_id': row[3]
                        })
                        restored_count += 1
                    except Exception as e:
                        logger.error(f"恢复数据失败: {e}")
                        skipped_count += 1
                
                db.session.commit()
                logger.info(f"✅ 数据恢复完成: 恢复 {restored_count} 条，跳过 {skipped_count} 条重复数据")
            
            logger.info("✅ 停翻词表结构修复完成")
            return True
            
    except Exception as e:
        logger.error(f"❌ 修复停翻词表失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False


def test_stop_words_functionality():
    """测试停翻词功能"""
    try:
        from app import create_app, db
        from app.models.stop_word import StopWord
        from app.models.user import User
        
        app = create_app('development')
        
        with app.app_context():
            logger.info("测试停翻词功能...")
            
            # 查找一个测试用户
            test_user = User.query.first()
            if not test_user:
                logger.warning("没有找到测试用户，跳过功能测试")
                return True
            
            logger.info(f"使用测试用户: {test_user.username} (ID: {test_user.id})")
            
            # 测试添加停翻词
            test_word = "test_stop_word"
            
            # 清理可能存在的测试数据
            existing = StopWord.query.filter_by(word=test_word, user_id=test_user.id).first()
            if existing:
                db.session.delete(existing)
                db.session.commit()
            
            # 添加测试停翻词
            stop_word = StopWord(word=test_word, user_id=test_user.id)
            db.session.add(stop_word)
            db.session.commit()
            logger.info("✅ 添加停翻词成功")
            
            # 测试查询
            found_word = StopWord.query.filter_by(word=test_word, user_id=test_user.id).first()
            if found_word:
                logger.info("✅ 查询停翻词成功")
            else:
                logger.error("❌ 查询停翻词失败")
                return False
            
            # 测试重复添加（应该失败）
            try:
                duplicate_word = StopWord(word=test_word, user_id=test_user.id)
                db.session.add(duplicate_word)
                db.session.commit()
                logger.error("❌ 重复添加应该失败但成功了")
                return False
            except Exception:
                db.session.rollback()
                logger.info("✅ 重复添加正确被阻止")
            
            # 清理测试数据
            db.session.delete(found_word)
            db.session.commit()
            logger.info("✅ 清理测试数据完成")
            
            logger.info("✅ 停翻词功能测试通过")
            return True
            
    except Exception as e:
        logger.error(f"❌ 停翻词功能测试失败: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")
        return False


def main():
    """主函数"""
    logger.info("🔧 停翻词表结构修复工具")
    logger.info("=" * 60)
    
    # 修复表结构
    if not fix_stop_words_table():
        logger.error("❌ 表结构修复失败")
        return False
    
    # 测试功能
    if not test_stop_words_functionality():
        logger.error("❌ 功能测试失败")
        return False
    
    logger.info("=" * 60)
    logger.info("🎉 停翻词表修复完成！")
    logger.info("")
    logger.info("✅ 修复内容:")
    logger.info("  1. 移除了全局word唯一约束")
    logger.info("  2. 添加了用户级别的唯一约束")
    logger.info("  3. 保留了现有数据（去重）")
    logger.info("  4. 测试了基本功能")
    logger.info("")
    logger.info("现在您可以:")
    logger.info("  - 每个用户可以添加自己的停翻词")
    logger.info("  - 不同用户可以有相同的停翻词")
    logger.info("  - 同一用户不能添加重复的停翻词")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("操作被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
