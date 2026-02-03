#!/bin/bash

################################################################################
# NewsGap Docker 服务管理脚本
# 功能：管理 RSSHub Docker 容器
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        echo ""
        echo "请先安装 Docker："
        echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
        echo "  Ubuntu: https://docs.docker.com/engine/install/ubuntu/"
        echo "  或运行: curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装"
        echo ""
        echo "Docker Compose 安装："
        echo "  新版 Docker 自带: docker compose"
        echo "  或安装独立版: pip install docker-compose"
        exit 1
    fi
}

# 获取 docker compose 命令
get_compose_cmd() {
    if docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

# 启动 Docker 服务
start_docker() {
    print_header "启动 Docker 服务"
    
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    
    print_info "拉取最新的 RSSHub 镜像..."
    docker pull diygod/rsshub:latest
    
    print_info "启动 RSSHub 容器..."
    $COMPOSE_CMD up -d
    
    print_info "等待 RSSHub 服务启动..."
    sleep 5
    
    # 检查容器状态
    if docker ps | grep -q newsgap-rsshub; then
        print_success "RSSHub 容器已启动"
        
        # 等待服务就绪
        print_info "等待 RSSHub 服务就绪..."
        for i in {1..30}; do
            if curl -sf http://localhost:1200/ > /dev/null 2>&1; then
                print_success "RSSHub 服务已就绪"
                echo ""
                echo "🌐 RSSHub 访问地址："
                echo "   - 服务: http://localhost:1200"
                echo "   - 文档: http://localhost:1200/docs"
                echo ""
                return 0
            fi
            sleep 1
        done
        
        print_warning "RSSHub 服务启动超时，但容器正在运行"
        echo "请稍后访问: http://localhost:1200"
    else
        print_error "RSSHub 容器启动失败"
        echo ""
        echo "查看日志："
        $COMPOSE_CMD logs rsshub
        exit 1
    fi
}

# 停止 Docker 服务
stop_docker() {
    print_header "停止 Docker 服务"
    
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    
    if docker ps | grep -q newsgap-rsshub; then
        print_info "停止 RSSHub 容器..."
        $COMPOSE_CMD down
        print_success "RSSHub 容器已停止"
    else
        print_warning "RSSHub 容器未运行"
    fi
}

# 重启 Docker 服务
restart_docker() {
    print_header "重启 Docker 服务"
    stop_docker
    start_docker
}

# 查看 Docker 状态
status_docker() {
    print_header "Docker 服务状态"
    
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    
    echo "━━━ 容器状态 ━━━"
    if docker ps -a | grep -q newsgap-rsshub; then
        docker ps -a --filter "name=newsgap-rsshub" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        echo "RSSHub 容器未创建"
    fi
    
    echo ""
    echo "━━━ 服务健康检查 ━━━"
    if curl -sf http://localhost:1200/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ RSSHub 服务运行正常${NC}"
        echo "访问地址: http://localhost:1200"
    else
        echo -e "${RED}❌ RSSHub 服务不可访问${NC}"
    fi
    
    echo ""
}

# 查看日志
logs_docker() {
    print_header "Docker 服务日志"
    
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    
    if docker ps | grep -q newsgap-rsshub; then
        print_info "显示 RSSHub 日志（按 Ctrl+C 退出）..."
        echo ""
        $COMPOSE_CMD logs -f --tail=50 rsshub
    else
        print_error "RSSHub 容器未运行"
        exit 1
    fi
}

# 更新镜像
update_docker() {
    print_header "更新 Docker 镜像"
    
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    
    print_info "拉取最新的 RSSHub 镜像..."
    docker pull diygod/rsshub:latest
    
    print_info "重启容器以应用更新..."
    $COMPOSE_CMD up -d --force-recreate
    
    print_success "RSSHub 已更新到最新版本"
}

# 清理容器和镜像
clean_docker() {
    print_header "清理 Docker 资源"
    
    check_docker
    
    COMPOSE_CMD=$(get_compose_cmd)
    
    read -p "确定要清理所有 RSSHub 容器和数据吗？[y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "取消清理"
        exit 0
    fi
    
    print_info "停止并删除容器..."
    $COMPOSE_CMD down -v
    
    print_info "删除镜像..."
    docker rmi diygod/rsshub:latest 2>/dev/null || true
    
    print_success "清理完成"
}

# 显示帮助
show_help() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  NewsGap Docker 服务管理脚本"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "用法: ./docker.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start      启动 RSSHub Docker 服务"
    echo "  stop       停止 RSSHub Docker 服务"
    echo "  restart    重启 RSSHub Docker 服务"
    echo "  status     查看服务状态"
    echo "  logs       查看服务日志"
    echo "  update     更新 RSSHub 到最新版本"
    echo "  clean      清理容器和镜像"
    echo "  help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./docker.sh start      # 启动 RSSHub"
    echo "  ./docker.sh status     # 查看状态"
    echo "  ./docker.sh logs       # 查看日志"
    echo ""
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            start_docker
            ;;
        stop)
            stop_docker
            ;;
        restart)
            restart_docker
            ;;
        status)
            status_docker
            ;;
        logs)
            logs_docker
            ;;
        update)
            update_docker
            ;;
        clean)
            clean_docker
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
