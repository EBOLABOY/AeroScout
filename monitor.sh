#!/bin/bash

# AeroScout 监控和维护脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示菜单
show_menu() {
    echo -e "${BLUE}=================================="
    echo -e "    AeroScout 监控和维护工具"
    echo -e "==================================${NC}"
    echo "1. 查看服务状态"
    echo "2. 查看服务日志"
    echo "3. 重启服务"
    echo "4. 更新服务"
    echo "5. 备份数据"
    echo "6. 清理系统"
    echo "7. 查看资源使用情况"
    echo "8. 健康检查"
    echo "9. 退出"
    echo ""
    read -p "请选择操作 (1-9): " choice
}

# 查看服务状态
check_status() {
    echo -e "${BLUE}📊 服务状态:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
    
    echo -e "${BLUE}🔍 端口监听状态:${NC}"
    netstat -tlnp | grep -E ':3000|:8000|:6379' || echo "未找到监听端口"
    echo ""
}

# 查看服务日志
view_logs() {
    echo "选择要查看的服务日志:"
    echo "1. 前端 (frontend)"
    echo "2. 后端 (backend)"
    echo "3. Celery (celery)"
    echo "4. Redis (redis)"
    echo "5. 所有服务"
    read -p "请选择 (1-5): " log_choice
    
    case $log_choice in
        1) docker-compose -f docker-compose.prod.yml logs -f frontend ;;
        2) docker-compose -f docker-compose.prod.yml logs -f backend ;;
        3) docker-compose -f docker-compose.prod.yml logs -f celery ;;
        4) docker-compose -f docker-compose.prod.yml logs -f redis ;;
        5) docker-compose -f docker-compose.prod.yml logs -f ;;
        *) echo "无效选择" ;;
    esac
}

# 重启服务
restart_services() {
    echo -e "${YELLOW}🔄 重启服务...${NC}"
    docker-compose -f docker-compose.prod.yml restart
    echo -e "${GREEN}✅ 服务重启完成${NC}"
}

# 更新服务
update_services() {
    echo -e "${YELLOW}🔄 更新服务...${NC}"
    
    # 拉取最新代码（如果是git仓库）
    if [ -d ".git" ]; then
        echo "拉取最新代码..."
        git pull
    fi
    
    # 重新构建并启动
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}✅ 服务更新完成${NC}"
}

# 备份数据
backup_data() {
    echo -e "${YELLOW}💾 备份数据...${NC}"
    
    # 创建备份目录
    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份数据库
    docker cp aeroscout-backend:/app/aeroscout.db "$backup_dir/"
    
    # 备份配置文件
    cp .env.production "$backup_dir/"
    cp docker-compose.prod.yml "$backup_dir/"
    
    # 压缩备份
    tar -czf "$backup_dir.tar.gz" "$backup_dir"
    rm -rf "$backup_dir"
    
    echo -e "${GREEN}✅ 数据备份完成: $backup_dir.tar.gz${NC}"
}

# 清理系统
cleanup_system() {
    echo -e "${YELLOW}🧹 清理系统...${NC}"
    
    # 清理Docker
    docker system prune -f
    docker volume prune -f
    
    # 清理旧的备份（保留最近7天）
    find backups/ -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ 系统清理完成${NC}"
}

# 查看资源使用情况
check_resources() {
    echo -e "${BLUE}💻 系统资源使用情况:${NC}"
    
    # CPU和内存使用
    echo "CPU和内存使用:"
    top -bn1 | head -5
    echo ""
    
    # 磁盘使用
    echo "磁盘使用:"
    df -h
    echo ""
    
    # Docker容器资源使用
    echo "Docker容器资源使用:"
    docker stats --no-stream
    echo ""
}

# 健康检查
health_check() {
    echo -e "${BLUE}🏥 健康检查:${NC}"
    
    # 检查前端
    if curl -f http://localhost:3000 &> /dev/null; then
        echo -e "${GREEN}✅ 前端服务正常${NC}"
    else
        echo -e "${RED}❌ 前端服务异常${NC}"
    fi
    
    # 检查后端
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo -e "${GREEN}✅ 后端服务正常${NC}"
    else
        echo -e "${RED}❌ 后端服务异常${NC}"
    fi
    
    # 检查Redis
    if docker exec aeroscout-redis redis-cli ping &> /dev/null; then
        echo -e "${GREEN}✅ Redis服务正常${NC}"
    else
        echo -e "${RED}❌ Redis服务异常${NC}"
    fi
    
    echo ""
}

# 主循环
while true; do
    show_menu
    case $choice in
        1) check_status ;;
        2) view_logs ;;
        3) restart_services ;;
        4) update_services ;;
        5) backup_data ;;
        6) cleanup_system ;;
        7) check_resources ;;
        8) health_check ;;
        9) echo "退出"; exit 0 ;;
        *) echo -e "${RED}无效选择，请重新输入${NC}" ;;
    esac
    echo ""
    read -p "按回车键继续..."
    clear
done
