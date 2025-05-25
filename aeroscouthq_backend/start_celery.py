import subprocess
import sys
import os
import time

def check_redis():
    """检查Redis服务器是否已安装并运行"""
    print("检查Redis服务器状态...")
    try:
        # 尝试使用redis-cli ping命令检查Redis是否运行
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
        if result.stdout.strip() == "PONG":
            print("Redis服务器正在运行")
            return True
        else:
            print("Redis服务器未响应PING命令")
            return False
    except FileNotFoundError:
        print("未找到redis-cli命令，Redis可能未安装")
        return False
    except Exception as e:
        print(f"检查Redis状态时出错: {e}")
        return False

def start_celery_worker():
    """启动Celery工作进程"""
    print("正在启动Celery工作进程...")
    try:
        # 使用Python解释器启动Celery工作进程
        celery_cmd = [
            sys.executable,
            "-m", "celery",
            "-A", "app.celery_worker",
            "worker",
            "--loglevel=info",
            "-Q", "main-queue"
        ]
        
        # 启动Celery工作进程
        process = subprocess.Popen(celery_cmd, cwd=os.getcwd())
        print(f"Celery工作进程已启动，PID: {process.pid}")
        return process
    except Exception as e:
        print(f"启动Celery工作进程时出错: {e}")
        return None

def main():
    """主函数"""
    print("AeroScout Celery工作进程启动脚本")
    print("=" * 50)
    
    # 检查Redis服务器
    redis_running = check_redis()
    if not redis_running:
        print("警告: Redis服务器未运行，Celery可能无法正常工作")
        print("请确保Redis服务器已安装并运行")
        print("在Windows上，您可以使用以下命令启动Redis服务器:")
        print("  redis-server.exe")
        print("或者使用Windows服务管理器启动Redis服务")
        print("\n是否继续启动Celery工作进程? (y/n)")
        choice = input().strip().lower()
        if choice != 'y':
            print("已取消启动Celery工作进程")
            return
    
    # 启动Celery工作进程
    celery_process = start_celery_worker()
    if celery_process:
        print("\nCelery工作进程已启动")
        print("按Ctrl+C停止Celery工作进程")
        try:
            # 保持脚本运行，直到用户按Ctrl+C
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在停止Celery工作进程...")
            celery_process.terminate()
            celery_process.wait()
            print("Celery工作进程已停止")
    else:
        print("无法启动Celery工作进程")

if __name__ == "__main__":
    main()
