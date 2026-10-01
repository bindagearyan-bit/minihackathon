# EcoTrace Deployment Guide 🚀

EcoTrace can be deployed in multiple ways depending on your preferred environment:

---

## Option 1: Render.com (Recommended Free Full-Stack Deployment)
> **Why Render?** It runs both your FastAPI backend and all interactive frontend pages (`dashboard.html`, `login.html`, `scanner.html`, etc.) in **ONE single URL** with zero CORS configuration!

### Method A: Web UI (1-Click)
1. Go to [https://dashboard.render.com](https://dashboard.render.com) and sign in with GitHub.
2. Click **New +** > **Web Service**.
3. Connect your repository: `https://github.com/bindagearyan-bit/minihackathon`.
4. Configure the settings:
   - **Name**: `ecotrace-campus-auditor`
   - **Environment**: `Python 3`
   - **Region**: `Singapore` or `Frankfurt`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
5. Click **Create Web Service**.
6. Once deployed, Render will provide a live URL like: `https://ecotrace-campus-auditor.onrender.com`.

---

## Option 2: Railway.app (Instant 1-Click Deployment)
1. Go to [https://railway.app](https://railway.app) and log in with GitHub.
2. Click **New Project** > **Deploy from GitHub repo**.
3. Select `bindagearyan-bit/minihackathon`.
4. Railway will automatically detect the `Procfile` and `requirements.txt`.
5. Under service settings, generate a public domain:
   - Go to **Settings** > **Networking** > **Generate Domain**.
6. Your application is live instantly!

---

## Option 3: Docker Container Deployment (Any Cloud / AWS / GCP / DigitalOcean)

### Build and Run with Docker:
```bash
# 1. Build the Docker image
docker build -t ecotrace-auditor:latest .

# 2. Run the container on port 8000
docker run -d -p 8000:8000 --name ecotrace ecotrace-auditor:latest

# 3. Access in browser
http://localhost:8000
```

---

## Option 4: Deploying to Linux VPS / Ubuntu Server (DigitalOcean, AWS EC2, Hostinger)

### Step 1: Connect and Clone
```bash
# Update packages and install Python & Tesseract OCR
sudo apt update && sudo apt install -y python3-pip python3-venv git tesseract-ocr tesseract-ocr-mar tesseract-ocr-hin poppler-utils

# Clone the repository
git clone https://github.com/bindagearyan-bit/minihackathon.git
cd minihackathon

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run with systemd service (Production Background Daemon)
Create a systemd unit file:
```bash
sudo nano /etc/systemd/system/ecotrace.service
```
Paste this configuration:
```ini
[Unit]
Description=EcoTrace Campus Carbon Auditor Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/minihackathon
ExecStart=/home/ubuntu/minihackathon/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ecotrace
sudo systemctl start ecotrace
sudo systemctl status ecotrace
```

---

## Option 5: Free Frontend Hosting on GitHub Pages (Static UI)
1. Go to your GitHub repository: [https://github.com/bindagearyan-bit/minihackathon](https://github.com/bindagearyan-bit/minihackathon)
2. Click **Settings** > **Pages** (in the left sidebar).
3. Under **Branch**, select `main` and `/ (root)`, then click **Save**.
4. GitHub Pages will publish your site at: `https://bindagearyan-bit.github.io/minihackathon/`
