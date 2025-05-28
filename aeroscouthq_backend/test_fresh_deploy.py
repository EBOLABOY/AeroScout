#!/usr/bin/env python3
"""测试全新部署的数据库迁移"""

import os
import shutil
import sqlite3
import subprocess
import sys

def test_fresh_deployment():
    """测试从零开始的数据库部署"""
    
    print("🧪 测试全新部署的数据库迁移")
    print("=" * 50)
    
    # 备份现有数据库
    backup_db = 'aeroscout.db.backup'
    if os.path.exists('aeroscout.db'):
        print("📦 备份现有数据库...")
        shutil.copy2('aeroscout.db', backup_db)
        print(f"✅ 数据库已备份到: {backup_db}")
    
    # 删除现有数据库
    if os.path.exists('aeroscout.db'):
        os.remove('aeroscout.db')
        print("🗑️  删除现有数据库")
    
    try:
        # 运行Alembic迁移
        print("🔄 运行Alembic迁移...")
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Alembic迁移失败:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        
        print("✅ Alembic迁移成功")
        print(f"输出: {result.stdout}")
        
        # 检查数据库是否创建
        if not os.path.exists('aeroscout.db'):
            print("❌ 数据库文件未创建")
            return False
        
        print("✅ 数据库文件已创建")
        
        # 检查表结构
        conn = sqlite3.connect('aeroscout.db')
        cursor = conn.cursor()
        
        # 检查必要的表是否存在
        expected_tables = [
            'users', 'invitation_codes', 'locations', 'airports', 
            'potential_hubs', 'user_searches', 'legal_texts', 'alembic_version'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"📋 期望的表: {len(expected_tables)} 个")
        print(f"📋 实际的表: {len(actual_tables)} 个")
        
        missing_tables = set(expected_tables) - set(actual_tables)
        if missing_tables:
            print(f"❌ 缺少表: {missing_tables}")
            conn.close()
            return False
        
        print("✅ 所有必要的表都已创建")
        
        # 检查Alembic版本
        cursor.execute("SELECT version_num FROM alembic_version")
        version = cursor.fetchone()
        if version:
            print(f"✅ Alembic版本: {version[0]}")
        else:
            print("❌ Alembic版本表为空")
            conn.close()
            return False
        
        conn.close()
        
        # 测试默认管理员创建
        print("👤 测试默认管理员创建...")
        result = subprocess.run([sys.executable, 'init_default_admin.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ 默认管理员创建失败:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        
        print("✅ 默认管理员创建成功")
        print(f"输出: {result.stdout}")
        
        # 验证管理员账户
        conn = sqlite3.connect('aeroscout.db')
        cursor = conn.cursor()
        cursor.execute("SELECT email, is_admin FROM users WHERE email = '1242772513@qq.com'")
        admin = cursor.fetchone()
        
        if admin and admin[1]:  # is_admin = True
            print(f"✅ 默认管理员账户验证成功: {admin[0]}")
        else:
            print("❌ 默认管理员账户验证失败")
            conn.close()
            return False
        
        conn.close()
        
        print("🎉 全新部署测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False
    
    finally:
        # 恢复备份数据库
        if os.path.exists(backup_db):
            print("🔄 恢复备份数据库...")
            if os.path.exists('aeroscout.db'):
                os.remove('aeroscout.db')
            shutil.move(backup_db, 'aeroscout.db')
            print("✅ 数据库已恢复")

if __name__ == "__main__":
    success = test_fresh_deployment()
    sys.exit(0 if success else 1)
