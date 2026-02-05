#!/bin/bash

################################################################################
# NewsGap 生产环境部署脚本
# 
# 功能：
# 1. 安装依赖
# 2. 构建前端
# 3. 配置Nginx
# 4. 配置systemd
# 5. 启动服务
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

# 配置变量（请根据实际情况修改）
PROJECT_USER="${USER}"
PROJECT_PATH="${SCRIPT_DIR}"
DOMAIN_NAME=""  # 留空则使用IP

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

print_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▶ $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "不建议使用root用户运行此脚本"
        read -p "是否继续？[y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 获取服务器IP
get_server_ip() {
    SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "unknown")
    if [ "$SERVER_IP" = "unknown" ]; then
        print_warning "无法自动获取服务器IP，请手动输入"
        read -p "请输入服务器公网IP: " SERVER_IP
    fi
    print_info "服务器IP: $SERVER_IP"
}

# 询问域名配置
ask_domain() {
    print_step "1. 域名配置"
    
    echo "请选择访问方式："
    echo "  1) 使用域名（推荐）"
    echo "  2) 使用IP地址"
    read -p "请选择 [1/2]: " -n 1 -r
    echo
    
    if [[ $REPLY == "1" ]]; then
        read -p "请输入域名（例如：newsgap.example.com）: " DOMAIN_NAME
        if [ -z "$DOMAIN_NAME" ]; then
            print_error "域名不能为空"
            exit 1
        fi
        print_success "将使用域名: $DOMAIN_NAME"
    else
        get_server_ip
        DOMAIN_NAME="$SERVER_IP"
        print_success "将使用IP地址: $DOMAIN_NAME"
    fi
}

# 安装系统依赖
install_system_dependencies() {
    print_step "2. 安装系统依赖"
    
    # 检测系统类型
    if [ -f /etc/debian_version ]; then
        print_info "检测到 Debian/Ubuntu 系统"
        sudo apt update
        sudo apt install -y python3 python3-venv python3-pip nodejs npm nginx curl
    elif [ -f /etc/redhat-release ]; then
        print_info "检测到 CentOS/RHEL 系统"
        sudo yum install -y python3 python3-pip nodejs nginx curl
    else
        print_warning "未识别的系统类型，请手动安装依赖"
    fi
    
    print_success "系统依赖安装完成"
}

# 安装项目依赖
install_project_dependencies() {
    print_step "3. 安装项目依赖"
    
    # 后端依赖
    print_info "安装后端依赖..."
    cd "$PROJECT_PATH/backend"
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    print_success "后端依赖安装完成"
    
    # 前端依赖
    print_info "安装前端依赖..."
    cd "$PROJECT_PATH/frontend"
    npm install
    
    print_success "前端依赖安装完成"
}

# 配置环境变量
configure_environment() {
    print_step "4. 配置环境变量"
    
    # 后端环境变量
    if [ ! -f "$PROJECT_PATH/backend/.env" ]; then
        print_info "创建后端 .env 文件..."
        cp "$PROJECT_PATH/backend/.env.example" "$PROJECT_PATH/backend/.env"
        
        print_warning "请配置 API Keys："
        echo "编辑文件: $PROJECT_PATH/backend/.env"
        echo "至少需要配置一个LLM的API Key"
        echo ""
        read -p "按 Enter 继续，或 Ctrl+C 退出后手动配置..."
    fi
    
    # 前端环境变量
    print_info "配置前端 API 地址..."
    cat > "$PROJECT_PATH/frontend/.env.production" <<EOF
# NewsGap Frontend - Production Configuration
VITE_API_BASE_URL=/api
EOF
    
    print_success "环境配置完成"
}

# 构建前端
build_frontend() {
    print_step "5. 构建前端"
    
    cd "$PROJECT_PATH/frontend"
    print_info "开始构建前端..."
    npm run build
    
    if [ ! -d "dist" ]; then
        print_error "前端构建失败"
        exit 1
    fi
    
    print_success "前端构建完成"
}

# 配置 Nginx
configure_nginx() {
    print_step "6. 配置 Nginx"
    
    # 创建日志目录
    sudo mkdir -p /var/log/nginx
    
    # 生成Nginx配置
    NGINX_CONF="/etc/nginx/sites-available/newsgap"
    
    print_info "生成 Nginx 配置文件..."
    sudo tee "$NGINX_CONF" > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    access_log /var/log/nginx/newsgap-access.log;
    error_log /var/log/nginx/newsgap-error.log;
    
    # 前端静态文件
    location / {
        root $PROJECT_PATH/frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        proxy_cache_bypass \$http_upgrade;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
EOF
    
    # 启用站点
    if [ ! -L "/etc/nginx/sites-enabled/newsgap" ]; then
        sudo ln -s "$NGINX_CONF" /etc/nginx/sites-enabled/newsgap
    fi
    
    # 测试配置
    sudo nginx -t
    
    print_success "Nginx 配置完成"
}

# 配置 systemd
configure_systemd() {
    print_step "7. 配置 systemd 服务"
    
    # 创建日志目录
    sudo mkdir -p /var/log/newsgap
    sudo chown -R $PROJECT_USER:$PROJECT_USER /var/log/newsgap
    
    # 生成systemd服务文件
    SYSTEMD_SERVICE="/etc/systemd/system/newsgap-backend.service"
    
    print_info "生成 systemd 服务文件..."
    sudo tee "$SYSTEMD_SERVICE" > /dev/null <<EOF
[Unit]
Description=NewsGap Backend Service
After=network.target

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_PATH/backend
Environment="PATH=$PROJECT_PATH/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="ENV=production"
EnvironmentFile=-$PROJECT_PATH/backend/.env

ExecStart=$PROJECT_PATH/backend/venv/bin/python main.py

Restart=always
RestartSec=10

StandardOutput=append:/var/log/newsgap/backend.log
StandardError=append:/var/log/newsgap/backend-error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # 重载systemd
    sudo systemctl daemon-reload
    
    print_success "systemd 配置完成"
}

# 配置防火墙
configure_firewall() {
    print_step "8. 配置防火墙"
    
    if command -v ufw &> /dev/null; then
        print_info "配置 ufw 防火墙..."
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw --force enable
    elif command -v firewall-cmd &> /dev/null; then
        print_info "配置 firewalld 防火墙..."
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --reload
    else
        print_warning "未检测到防火墙，请手动配置"
    fi
    
    print_success "防火墙配置完成"
}

# 启动服务
start_services() {
    print_step "9. 启动服务"
    
    # 启动后端
    print_info "启动后端服务..."
    sudo systemctl enable newsgap-backend
    sudo systemctl start newsgap-backend
    sleep 2
    
    if sudo systemctl is-active --quiet newsgap-backend; then
        print_success "后端服务已启动"
    else
        print_error "后端服务启动失败"
        sudo journalctl -u newsgap-backend -n 20
        exit 1
    fi
    
    # 启动 Docker（RSSHub）
    if command -v docker &> /dev/null; then
        print_info "启动 RSSHub Docker 服务..."
        ./docker.sh start || print_warning "RSSHub 启动失败（可选服务）"
    fi
    
    # 重载 Nginx
    print_info "重载 Nginx..."
    sudo systemctl reload nginx
    
    print_success "所有服务已启动"
}

# 显示部署总结
show_summary() {
    echo ""
    echo "=================================="
    echo -e "${GREEN}✅ 部署完成！${NC}"
    echo "=================================="
    echo ""
    echo "📊 服务信息："
    echo "  - 访问地址: http://$DOMAIN_NAME"
    echo "  - API文档: http://$DOMAIN_NAME/api/docs"
    echo "  - 后端日志: /var/log/newsgap/backend.log"
    echo "  - Nginx日志: /var/log/nginx/newsgap-access.log"
    echo ""
    echo "💡 管理命令："
    echo "  - 查看后端状态: sudo systemctl status newsgap-backend"
    echo "  - 重启后端: sudo systemctl restart newsgap-backend"
    echo "  - 查看后端日志: sudo journalctl -u newsgap-backend -f"
    echo "  - 重载Nginx: sudo systemctl reload nginx"
    echo ""
    echo "🔒 配置 HTTPS（可选）："
    echo "  sudo apt install certbot python3-certbot-nginx"
    echo "  sudo certbot --nginx -d $DOMAIN_NAME"
    echo ""
    echo "📝 下一步："
    echo "  1. 配置 API Keys: 编辑 $PROJECT_PATH/backend/.env"
    echo "  2. 重启后端服务: sudo systemctl restart newsgap-backend"
    echo "  3. 访问应用: http://$DOMAIN_NAME"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=================================="
    echo "  NewsGap 生产环境部署脚本"
    echo "=================================="
    echo ""
    
    check_root
    ask_domain
    install_system_dependencies
    install_project_dependencies
    configure_environment
    build_frontend
    configure_nginx
    configure_systemd
    configure_firewall
    start_services
    show_summary
}

# 错误处理
trap 'print_error "部署失败！请查看上面的错误信息。"; exit 1' ERR

main
