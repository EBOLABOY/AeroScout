#!/usr/bin/env python3
"""检查数据库表结构的脚本"""

import sqlite3
import os

def check_database():
    db_path = 'aeroscout.db'
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📊 数据库表结构检查")
        print("=" * 50)
        print(f"数据库文件: {db_path}")
        print(f"表数量: {len(tables)}")
        print()
        
        if not tables:
            print("⚠️  数据库中没有表")
            return
        
        print("📋 数据库中的表:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if columns:
                print(f"    列信息:")
                for col in columns:
                    col_id, col_name, col_type, not_null, default_val, pk = col
                    pk_str = " (主键)" if pk else ""
                    not_null_str = " NOT NULL" if not_null else ""
                    default_str = f" DEFAULT {default_val}" if default_val else ""
                    print(f"      {col_name}: {col_type}{not_null_str}{default_str}{pk_str}")
            
            # 获取记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"    记录数: {count}")
            print()
        
        # 检查Alembic版本表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        alembic_table = cursor.fetchone()
        
        if alembic_table:
            cursor.execute("SELECT version_num FROM alembic_version")
            version = cursor.fetchone()
            if version:
                print(f"🔄 当前Alembic版本: {version[0]}")
            else:
                print("⚠️  Alembic版本表为空")
        else:
            print("⚠️  未找到Alembic版本表")
        
        conn.close()
        print("✅ 数据库检查完成")
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")

if __name__ == "__main__":
    check_database()
