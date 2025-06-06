#!/usr/bin/env python3
"""
简化的SSO数据库迁移脚本
专门用于添加SSO相关字段，避免其他依赖问题
"""
import os
import sys
import logging
import pymysql
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """加载配置"""
    load_dotenv()
    
    config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'charset': 'utf8mb4'
    }
    
    logger.info(f"数据库配置: {config['host']}:{config['port']}/{config['database']}")
    return config


def get_connection(config):
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**config)
        logger.info("✅ 数据库连接成功")
        return connection
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise


def check_table_exists(cursor, table_name):
    """检查表是否存在"""
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    return cursor.fetchone() is not None


def check_column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    cursor.execute(f"""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE() 
        AND TABLE_NAME = '{table_name}' 
        AND COLUMN_NAME = '{column_name}'
    """)
    return cursor.fetchone()[0] > 0


def add_sso_fields_to_users(cursor):
    """添加SSO字段到users表"""
    logger.info("=" * 60)
    logger.info("添加SSO字段到users表")
    logger.info("=" * 60)
    
    # 检查users表是否存在
    if not check_table_exists(cursor, 'users'):
        logger.error("❌ users表不存在")
        return False
    
    # 定义需要添加的SSO字段
    sso_fields = [
        {
            'name': 'email',
            'definition': 'VARCHAR(255) NULL COMMENT "用户邮箱"',
            'index': 'INDEX idx_users_email (email)'
        },
        {
            'name': 'first_name',
            'definition': 'VARCHAR(100) NULL COMMENT "名字"'
        },
        {
            'name': 'last_name',
            'definition': 'VARCHAR(100) NULL COMMENT "姓氏"'
        },
        {
            'name': 'display_name',
            'definition': 'VARCHAR(200) NULL COMMENT "显示名称"'
        },
        {
            'name': 'sso_provider',
            'definition': 'VARCHAR(50) NULL COMMENT "SSO提供者"',
            'index': 'INDEX idx_users_sso_provider (sso_provider)'
        },
        {
            'name': 'sso_subject',
            'definition': 'VARCHAR(255) NULL COMMENT "SSO用户标识"',
            'index': 'INDEX idx_users_sso_subject (sso_subject)'
        },
        {
            'name': 'last_login',
            'definition': 'DATETIME NULL COMMENT "最后登录时间"'
        }
    ]
    
    added_fields = 0
    
    for field in sso_fields:
        field_name = field['name']
        field_definition = field['definition']
        
        # 检查字段是否已存在
        if check_column_exists(cursor, 'users', field_name):
            logger.info(f"  ✅ {field_name}: 已存在")
        else:
            try:
                # 添加字段
                sql = f"ALTER TABLE users ADD COLUMN {field_name} {field_definition}"
                cursor.execute(sql)
                logger.info(f"  ✅ {field_name}: 已添加")
                added_fields += 1
                
                # 添加索引（如果定义了）
                if 'index' in field:
                    try:
                        cursor.execute(f"ALTER TABLE users ADD {field['index']}")
                        logger.info(f"    ✅ 索引已添加: {field_name}")
                    except Exception as e:
                        logger.warning(f"    ⚠️ 索引添加失败: {e}")
                        
            except Exception as e:
                logger.error(f"  ❌ {field_name}: 添加失败 - {e}")
                return False
    
    logger.info(f"✅ 成功添加 {added_fields} 个新字段")
    return True


def create_roles_table(cursor):
    """创建角色表"""
    logger.info("=" * 60)
    logger.info("创建角色表")
    logger.info("=" * 60)
    
    # 检查roles表是否存在
    if check_table_exists(cursor, 'roles'):
        logger.info("✅ roles表已存在")
        return True
    
    try:
        # 创建roles表
        create_roles_sql = """
        CREATE TABLE roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
            description VARCHAR(200) NULL COMMENT '角色描述',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_roles_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色表'
        """
        
        cursor.execute(create_roles_sql)
        logger.info("✅ roles表创建成功")
        
        # 插入默认角色
        default_roles = [
            ('admin', '管理员'),
            ('user', '普通用户'),
            ('translator', '翻译员')
        ]
        
        for role_name, role_desc in default_roles:
            try:
                cursor.execute(
                    "INSERT INTO roles (name, description) VALUES (%s, %s)",
                    (role_name, role_desc)
                )
                logger.info(f"  ✅ 默认角色已添加: {role_name}")
            except Exception as e:
                logger.warning(f"  ⚠️ 角色添加失败: {role_name} - {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ roles表创建失败: {e}")
        return False


def add_role_id_to_users(cursor):
    """添加role_id字段到users表"""
    logger.info("=" * 60)
    logger.info("添加role_id字段到users表")
    logger.info("=" * 60)
    
    # 检查role_id字段是否已存在
    if check_column_exists(cursor, 'users', 'role_id'):
        logger.info("✅ role_id字段已存在")
        return True
    
    try:
        # 添加role_id字段
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN role_id INT NULL COMMENT '用户角色ID',
            ADD INDEX idx_users_role_id (role_id)
        """)
        
        logger.info("✅ role_id字段添加成功")
        
        # 设置默认角色（user角色）
        cursor.execute("SELECT id FROM roles WHERE name = 'user'")
        user_role = cursor.fetchone()
        
        if user_role:
            user_role_id = user_role[0]
            cursor.execute(
                "UPDATE users SET role_id = %s WHERE role_id IS NULL",
                (user_role_id,)
            )
            logger.info(f"✅ 已为现有用户设置默认角色: user (ID: {user_role_id})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ role_id字段添加失败: {e}")
        return False


def verify_migration(cursor):
    """验证迁移结果"""
    logger.info("=" * 60)
    logger.info("验证迁移结果")
    logger.info("=" * 60)
    
    # 检查users表结构
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    
    logger.info("users表字段:")
    sso_fields = ['email', 'first_name', 'last_name', 'display_name', 'sso_provider', 'sso_subject', 'last_login', 'role_id']
    found_fields = []
    
    for column in columns:
        column_name = column[0]
        if column_name in sso_fields:
            found_fields.append(column_name)
            logger.info(f"  ✅ {column_name}: {column[1]}")
    
    missing_fields = set(sso_fields) - set(found_fields)
    if missing_fields:
        logger.warning(f"⚠️ 缺少字段: {missing_fields}")
    else:
        logger.info("✅ 所有SSO字段都已存在")
    
    # 检查roles表
    if check_table_exists(cursor, 'roles'):
        cursor.execute("SELECT COUNT(*) FROM roles")
        role_count = cursor.fetchone()[0]
        logger.info(f"✅ roles表存在，包含 {role_count} 个角色")
    else:
        logger.warning("⚠️ roles表不存在")
    
    return len(missing_fields) == 0


def main():
    """主函数"""
    logger.info("🔧 SSO数据库迁移工具")
    logger.info("=" * 80)
    
    try:
        # 加载配置
        config = load_config()
        
        # 连接数据库
        connection = get_connection(config)
        cursor = connection.cursor()
        
        # 执行迁移
        migrations = [
            ("添加SSO字段到users表", add_sso_fields_to_users),
            ("创建roles表", create_roles_table),
            ("添加role_id到users表", add_role_id_to_users),
            ("验证迁移结果", verify_migration)
        ]
        
        success_count = 0
        
        for migration_name, migration_func in migrations:
            logger.info(f"\n🔧 执行: {migration_name}")
            logger.info("-" * 50)
            
            try:
                if migration_func(cursor):
                    logger.info(f"✅ {migration_name} - 成功")
                    success_count += 1
                else:
                    logger.error(f"❌ {migration_name} - 失败")
            except Exception as e:
                logger.error(f"❌ {migration_name} - 异常: {e}")
        
        # 提交事务
        connection.commit()
        logger.info("\n✅ 数据库事务已提交")
        
        # 总结
        logger.info("=" * 80)
        logger.info("迁移总结")
        logger.info("=" * 80)
        logger.info(f"成功: {success_count}/{len(migrations)}")
        
        if success_count == len(migrations):
            logger.info("🎉 SSO数据库迁移完成！")
            logger.info("\n下一步:")
            logger.info("1. 启动应用: python app.py")
            logger.info("2. 访问登录页面测试SSO功能")
        else:
            logger.warning("⚠️ 部分迁移失败，请检查错误信息")
        
        return success_count >= 3
        
    except Exception as e:
        logger.error(f"❌ 迁移执行失败: {e}")
        return False
        
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("数据库连接已关闭")


if __name__ == "__main__":
    try:
        success = main()
        input("\n按回车键退出...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("迁移被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"迁移执行异常: {e}")
        input("按回车键退出...")
        sys.exit(1)
