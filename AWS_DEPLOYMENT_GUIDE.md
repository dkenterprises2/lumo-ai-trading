# LUMO TRADING BOT & ARBITRAGE AI — AWS PRODUCTION DEPLOYMENT GUIDE

This document provides complete, step-by-step instructions to deploy the entire Lumo ecosystem on **Amazon Web Services (AWS)** using a **$100 testing budget**.

---

## 1. AWS Cost & Hardware Budget Optimization ($100 Capacity)

To maximize your $100 budget and get **3 to 4 months of continuous testing**:

| Resource | Recommended Spec | Monthly Cost (USD) | 3-Month Total | Notes |
| :--- | :--- | :---: | :---: | :--- |
| **EC2 Compute** | `t4g.medium` (2 vCPU, 4GB RAM, ARM64 Graviton) | ~$24.50 / mo | ~$73.50 | 20% cheaper & faster than `t3.medium`. |
| **Alternative** | `t3.medium` (2 vCPU, 4GB RAM, x86_64) | ~$30.00 / mo | ~$90.00 | Standard Intel/AMD instance. |
| **EBS Storage** | 30 GB gp3 SSD (3000 IOPS, 125 MB/s) | ~$2.40 / mo | ~$7.20 | Blazing fast SQLite WAL disk throughput. |
| **Data Transfer**| 100 GB Outbound Data | Free Tier / ~$1.00 | ~$2.00 | WebSockets & API telemetry. |
| **Total Cost** | **Complete Full Stack on AWS** | **~$27.90 / mo** | **~$82.70** | **Easily covers 3+ full months on $100!** |

---

## 2. Step-by-Step EC2 Launch Instructions

### Step 1: Launch EC2 Instance in AWS Console
1. Log in to your [AWS Management Console](https://console.aws.amazon.com/ec2/).
2. Select a low-latency Region (e.g. `us-east-1` N. Virginia or `ap-south-1` Mumbai).
3. Click **Launch Instances**:
   - **Name:** `lumo-trading-workstation`
   - **OS (AMI):** `Ubuntu Server 24.04 LTS` (or `22.04 LTS`)
   - **Architecture:** `64-bit (Arm)` if using `t4g.medium`, or `64-bit (x86)` if using `t3.medium`.
   - **Instance Type:** `t4g.medium` (Recommended) or `t3.medium`.
   - **Key Pair:** Create or select your `.pem` key pair (e.g. `lumo-aws-key.pem`).
   - **Storage:** 30 GiB `gp3`.

### Step 2: Configure Security Group (Inbound Rules)
Open only the necessary ports in the AWS Security Group:

| Type | Port Range | Source | Purpose |
| :--- | :---: | :--- | :--- |
| **SSH** | `22` | `My IP` (or `0.0.0.0/0`) | Secure terminal access via SSH key. |
| **HTTP** | `80` | `0.0.0.0/0` | Web redirection & SSL verification. |
| **HTTPS** | `443` | `0.0.0.0/0` | Secure SSL Web Dashboard & API traffic. |
| **Custom TCP** | `8000` | `0.0.0.0/0` (Optional) | Direct Backend API access. |
| **Custom TCP** | `3000` | `0.0.0.0/0` (Optional) | Direct Next.js Web access. |

---

## 3. Deployment via Automated Script

### Step 1: Connect to your EC2 instance via SSH
```bash
chmod 400 lumo-aws-key.pem
ssh -i lumo-aws-key.pem ubuntu@<YOUR-EC2-PUBLIC-IP>
```

### Step 2: Clone or Upload your code
```bash
git clone <YOUR-GIT-REPO-URL> /home/ubuntu/lumo-trading-bot
cd /home/ubuntu/lumo-trading-bot
```

### Step 3: Run the 1-Click Deployment Script
```bash
chmod +x deploy_aws.sh
./deploy_aws.sh
```

The script will automatically:
1. Update Ubuntu packages and enable unattended security upgrades.
2. Configure the local UFW firewall.
3. Install Docker Engine and Docker Compose.
4. Build and start the Python FastAPI backend, Next.js frontend, and Caddy reverse proxy.
5. Verify health endpoints.

---

## 4. Alternative: Running Directly via PM2 (No Docker)

If you prefer running directly on the host without containers:

```bash
# 1. Install Node.js 20 & Python 3.12
sudo apt update && sudo apt install -y python3-pip python3-venv nodejs npm
sudo npm install -g pm2

# 2. Setup Python Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Build Next.js Frontend
cd frontend
npm install
npx cross-env NEXT_PUBLIC_API_URL='http://<YOUR-EC2-IP>:8000' npm run build
cd ..

# 4. Start services with PM2
pm2 start "venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000" --name "lumo-backend"
pm2 start "npm run start --prefix frontend -- -p 3000" --name "lumo-frontend"
pm2 save
pm2 startup
```

---

## 5. Production Maintenance & Monitoring Commands

- **Check Backend Logs:** `docker compose logs -f lumo-backend` (or `pm2 logs lumo-backend`)
- **Check System Health:** `curl http://localhost:8000/api/system/health`
- **Check Telemetry & Memory:** `curl http://localhost:8000/api/system/metrics`
- **Restart Application:** `docker compose restart` (or `pm2 restart all`)
