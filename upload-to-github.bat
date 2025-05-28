@echo off
chcp 65001 >nul
echo 🚀 AeroScout GitHub 上传脚本
echo ================================
echo.

echo 📋 上传信息:
echo   - 仓库地址: https://github.com/EBOLABOY/AeroScout.git
echo   - 本地路径: %CD%
echo   - 分支: main
echo.

echo 🔍 检查Git状态...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git未安装或不在PATH中
    echo 请先安装Git: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo ✅ Git已安装

echo.
echo 📂 检查项目文件...
if not exist "aeroscout-frontend" (
    echo ❌ 前端目录不存在
    pause
    exit /b 1
)
if not exist "aeroscouthq_backend" (
    echo ❌ 后端目录不存在
    pause
    exit /b 1
)
if not exist "docker-compose.production.yml" (
    echo ❌ 生产环境配置文件不存在
    pause
    exit /b 1
)
echo ✅ 项目文件检查通过

echo.
echo 🧹 最后清理检查...
if exist "aeroscout-frontend\node_modules" (
    echo ⚠️  发现node_modules目录，建议删除以减少上传大小
    set /p cleanup="是否删除node_modules? (y/N): "
    if /i "!cleanup!"=="y" (
        echo 删除中...
        rmdir /s /q "aeroscout-frontend\node_modules" 2>nul
        echo ✅ node_modules已删除
    )
)

echo.
echo 🔧 初始化Git仓库...
if not exist ".git" (
    git init
    echo ✅ Git仓库已初始化
) else (
    echo ℹ️  Git仓库已存在
)

echo.
echo 🔗 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/EBOLABOY/AeroScout.git
echo ✅ 远程仓库已配置

echo.
echo 📝 添加文件到Git...
git add .
if %errorlevel% neq 0 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)
echo ✅ 文件已添加到暂存区

echo.
echo 💾 提交更改...
git commit -m "Initial commit: AeroScout project ready for production deployment

Features:
- ✅ Frontend: Next.js 15 with optimized dependencies
- ✅ Backend: FastAPI with SQLite database
- ✅ Docker: Production-ready containers
- ✅ Nginx: Reverse proxy with SSL support
- ✅ Redis: Caching and session management
- ✅ Celery: Async task processing
- ✅ Documentation: Complete deployment guides

Deployment:
- Use docker-compose.production.yml for one-click deployment
- Default admin: 1242772513@qq.com / 1242772513
- Domain: AeroScout.izlx.de"

if %errorlevel% neq 0 (
    echo ❌ 提交失败
    pause
    exit /b 1
)
echo ✅ 更改已提交

echo.
echo 🌐 推送到GitHub...
echo 正在推送到 https://github.com/EBOLABOY/AeroScout.git
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ 推送失败
    echo.
    echo 💡 可能的原因:
    echo   1. 网络连接问题
    echo   2. GitHub认证问题
    echo   3. 仓库权限问题
    echo.
    echo 🔧 解决方案:
    echo   1. 检查网络连接
    echo   2. 配置GitHub认证: git config --global user.name "EBOLABOY"
    echo   3. 配置GitHub邮箱: git config --global user.email "your-email@example.com"
    echo   4. 使用GitHub Desktop或手动推送
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 上传成功!
echo ================================
echo.
echo 📊 上传总结:
echo   ✅ 仓库地址: https://github.com/EBOLABOY/AeroScout.git
echo   ✅ 分支: main
echo   ✅ 提交状态: 成功
echo   ✅ 推送状态: 成功
echo.
echo 🔗 GitHub链接:
echo   - 仓库主页: https://github.com/EBOLABOY/AeroScout
echo   - 部署指南: https://github.com/EBOLABOY/AeroScout/blob/main/DEPLOYMENT_GUIDE.md
echo   - API文档: https://github.com/EBOLABOY/AeroScout/blob/main/API_Documentation.md
echo.
echo 🚀 下一步 - 服务器部署:
echo   1. 登录到您的服务器
echo   2. 运行: git clone https://github.com/EBOLABOY/AeroScout.git
echo   3. 运行: cd AeroScout
echo   4. 运行: cp .env.example .env
echo   5. 编辑: nano .env (填入配置)
echo   6. 部署: docker-compose -f docker-compose.production.yml up -d --build
echo.
echo 💡 提示: 确保服务器已安装Docker和Docker Compose
echo.
pause
