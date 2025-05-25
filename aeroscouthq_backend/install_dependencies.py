import subprocess
import sys

def install_package(package):
    print(f"正在安装 {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"{package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{package} 安装失败: {e}")
        return False

def main():
    # 需要安装的依赖项
    dependencies = [
        "databases",
        "aiosqlite",
        "sqlalchemy",
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "python-jose",
        "passlib",
        "bcrypt",
        "python-multipart"
    ]
    
    success_count = 0
    for dep in dependencies:
        if install_package(dep):
            success_count += 1
    
    print(f"\n安装完成: {success_count}/{len(dependencies)} 个依赖项安装成功")
    
    # 创建locations表
    print("\n现在将创建locations表...")
    try:
        import sqlite3
        
        # 数据库文件路径
        db_path = "aeroscout.db"
        
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 创建locations表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            trip_type TEXT,
            mode TEXT,
            raw_data TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_query ON locations (query)')
        
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        
        print("locations表和索引创建成功")
    except Exception as e:
        print(f"创建locations表时出错: {e}")

if __name__ == "__main__":
    main()
