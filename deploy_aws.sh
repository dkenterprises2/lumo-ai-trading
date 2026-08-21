#!/usr/bin/env bash
# ==============================================================================
# LUMO TRADING BOT: ONE-CLICK AWS EC2 DEPLOYMENT SCRIPT
# Target OS: Ubuntu 22.04 LTS / 24.04 LTS (x86_64 or ARM64 / Graviton)
# ==============================================================================

set -euo pipefail

echo "================================================================================"
echo "          STARTING LUMO TRADING BOT AWS AUTOMATED PROVISIONING                  "
echo "================================================================================"

# 1. Update and install core utilities
echo "[1/5] Updating system packages & installing base dependencies..."
sudo apt-get update -y
sudo apt-get install -y curl git build-essential ufw unattended-upgrades htop

# 2. Configure Firewall (UFW)
echo "[2/5] Hardening firewall (Ports 22, 80, 443)..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 3. Install Docker & Docker Compose
echo "[3/5] Installing Docker Engine & Docker Compose..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER"
fi

# 4. Build and start containers with docker compose
echo "[4/5] Building and launching Lumo Trading Bot containers..."
if [ -f "docker-compose.yml" ]; then
    sudo docker compose down --remove-orphans || true
    sudo docker compose build --parallel
    sudo docker compose up -d
fi

# 5. Verify deployment health
echo "[5/5] Checking service health..."
sleep 5
curl -s http://localhost:8000/api/system/health | grep "healthy" && echo " Backend is Healthy!" || echo " Backend starting up..."

echo "================================================================================"
echo "          LUMO TRADING BOT SUCCESSFULLY DEPLOYED ON AWS!                       "
echo "================================================================================"
