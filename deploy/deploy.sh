#!/bin/bash
# ==============================================
# 皮皮剧本工坊 — 一键部署脚本
# 服务器：Ubuntu, root 用户
# ==============================================
set -e

SERVER_IP="47.238.77.221"
PROJECT_DIR="/opt/pipi-script-studio"
DOMAIN="${SERVER_IP}"  # 后续替换为真实域名

echo "========================================"
echo "  皮皮剧本工坊 — 部署到 ${SERVER_IP}"
echo "========================================"

# 1. 安装系统依赖
echo "[1/7] 安装系统依赖..."
ssh root@${SERVER_IP} "apt update && apt install -y python3 python3-pip python3-venv nginx sqlite3"

# 2. 创建目录结构
echo "[2/7] 创建项目目录..."
ssh root@${SERVER_IP} "mkdir -p ${PROJECT_DIR}/app/{routes,services,templates,static} /var/log/pipi-studio"

# 3. 上传代码
echo "[3/7] 上传代码..."
rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='data.db' --exclude='.git' \
    ./app/ ./wsgi.py ./requirements.txt root@${SERVER_IP}:${PROJECT_DIR}/

# 4. 上传 .env（如果本地有的话）
if [ -f ".env" ]; then
    scp .env root@${SERVER_IP}:${PROJECT_DIR}/.env
    echo "  .env 已上传"
else
    echo "  ⚠ 请手动创建 ${PROJECT_DIR}/.env"
fi

# 5. 安装 Python 依赖
echo "[5/7] 安装 Python 依赖..."
ssh root@${SERVER_IP} "cd ${PROJECT_DIR} && python3 -m venv venv && venv/bin/pip install -r requirements.txt"

# 6. 配置 Nginx
echo "[6/7] 配置 Nginx..."
scp deploy/nginx.conf root@${SERVER_IP}:/etc/nginx/sites-available/pipi-studio
ssh root@${SERVER_IP} "\
    ln -sf /etc/nginx/sites-available/pipi-studio /etc/nginx/sites-enabled/ && \
    rm -f /etc/nginx/sites-enabled/default && \
    nginx -t && systemctl reload nginx"

# 7. 配置 Systemd
echo "[7/7] 配置 Systemd 服务..."
scp deploy/pipi-studio.service root@${SERVER_IP}:/etc/systemd/system/pipi-studio.service
ssh root@${SERVER_IP} "\
    systemctl daemon-reload && \
    systemctl enable pipi-studio && \
    systemctl restart pipi-studio"

echo ""
echo "========================================"
echo "  部署完成！"
echo "  访问: http://${DOMAIN}"
echo ""
echo "  常用命令："
echo "    systemctl status pipi-studio  # 查看状态"
echo "    systemctl restart pipi-studio # 重启"
echo "    journalctl -u pipi-studio -f  # 查看日志"
echo "========================================"
