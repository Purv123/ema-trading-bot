# 🚀 Deployment Guide - EMA Trading Bot

Complete guide to deploy your trading bot to FREE hosting platforms!

---

## 🌟 **Option 1: Streamlit Community Cloud (RECOMMENDED - 100% FREE)**

**Best for:** This trading bot (it's a Streamlit app!)
**Cost:** Completely FREE ✅
**Requirements:** GitHub account only
**Deployment Time:** 5 minutes

### **Step 1: Prepare Your Repository**

Your code is already ready! Just make sure it's pushed to GitHub:

```bash
git push origin claude/bot-ui-configuration-3UNS7
```

### **Step 2: Deploy to Streamlit Cloud**

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Click "Sign in" → Sign in with GitHub

2. **Create New App**
   - Click "New app" button
   - Select your repository: `Purv123/ema-trading-bot`
   - Branch: `claude/bot-ui-configuration-3UNS7` (or `main` after merging)
   - Main file path: `app.py`
   - App URL: Choose a custom name (e.g., `ema-trading-bot`)

3. **Deploy!**
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment
   - Your app will be live at: `https://your-app-name.streamlit.app`

### **Step 3: Access Your App**

Your bot will be accessible at:
```
https://your-chosen-name.streamlit.app
```

### **Features on Streamlit Cloud:**
- ✅ Automatic HTTPS
- ✅ Auto-redeploy on git push
- ✅ Free subdomain
- ✅ Always-on (restarts if inactive)
- ✅ Logs and monitoring
- ✅ No credit card required

### **Important Notes:**

⚠️ **Security:** Your app will be PUBLIC. To make it private:
- Add authentication in the app code
- Or use Streamlit Cloud's private apps (paid)

⚠️ **Data Persistence:**
- Database files (`bot_config.db`, `trading.db`) will reset on redeploy
- Use Streamlit secrets for API keys (see below)

### **Adding API Credentials (Streamlit Secrets):**

1. In Streamlit Cloud dashboard, click your app
2. Go to "Settings" → "Secrets"
3. Add your secrets:

```toml
[angel_one]
api_key = "your_api_key"
client_code = "your_client_code"
password = "your_password"
totp_secret = "your_totp_secret"

[mudrex]
api_key = "your_api_key"
api_secret = "your_api_secret"
```

4. Access in code:
```python
import streamlit as st
api_key = st.secrets["angel_one"]["api_key"]
```

---

## 🖥️ **Option 2: AWS EC2 Free Tier**

**Best for:** Full control, long-running bots
**Cost:** FREE for 12 months (750 hours/month)
**Requirements:** AWS account, credit card (no charges if within limits)

### **Step 1: Launch EC2 Instance**

1. **Sign up for AWS Free Tier**
   - Visit: https://aws.amazon.com/free/
   - Create account (requires credit card but won't charge)

2. **Launch Instance**
   - Go to EC2 Dashboard
   - Click "Launch Instance"
   - **Name:** ema-trading-bot
   - **OS:** Ubuntu Server 22.04 LTS
   - **Instance type:** t2.micro (Free tier eligible)
   - **Key pair:** Create new (download .pem file)
   - **Security group:** Allow SSH (22), HTTP (80), Custom TCP (8501)
   - Click "Launch Instance"

3. **Get Public IP**
   - Wait for instance to start
   - Note the "Public IPv4 address"

### **Step 2: Connect to Your Server**

**From Linux/Mac:**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

**From Windows:**
- Use PuTTY or Windows Terminal with OpenSSH

### **Step 3: Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv git

# Install system packages for TA-Lib
sudo apt install -y build-essential wget
```

### **Step 4: Install TA-Lib (Required)**

```bash
# Download and install TA-Lib
cd /tmp
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
sudo ldconfig
```

### **Step 5: Clone and Setup Your Bot**

```bash
# Clone your repository
cd ~
git clone https://github.com/Purv123/ema-trading-bot.git
cd ema-trading-bot
git checkout claude/bot-ui-configuration-3UNS7

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### **Step 6: Run the Bot**

**Option A: Temporary (for testing):**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Access at: `http://YOUR_EC2_IP:8501`

**Option B: Permanent (keeps running):**

Create a systemd service:

```bash
sudo nano /etc/systemd/system/ema-bot.service
```

Add:
```ini
[Unit]
Description=EMA Trading Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ema-trading-bot
Environment="PATH=/home/ubuntu/ema-trading-bot/venv/bin"
ExecStart=/home/ubuntu/ema-trading-bot/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl daemon-reload
sudo systemctl start ema-bot
sudo systemctl enable ema-bot
sudo systemctl status ema-bot
```

### **Step 7: Access Your Bot**

Visit: `http://YOUR_EC2_IP:8501`

### **Optional: Add Domain & HTTPS**

1. **Get a free domain:**
   - Freenom.com (free domains)
   - Or use AWS Route 53

2. **Install Nginx:**
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

3. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/ema-bot
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/ema-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Get SSL Certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

---

## 🆓 **Option 3: Other Free Alternatives**

### **Render.com**
- **Pros:** Easy deployment, auto-deploy from GitHub
- **Cons:** Free tier sleeps after 15 min inactivity
- **Steps:**
  1. Go to render.com
  2. Connect GitHub repo
  3. Deploy as "Web Service"
  4. Free tier available

### **Railway.app**
- **Pros:** $5 free credit monthly, easy deployment
- **Cons:** Requires credit card
- **Steps:**
  1. Go to railway.app
  2. Connect GitHub
  3. Deploy from repo
  4. Get $5 free/month

### **Google Cloud Platform (GCP)**
- **Pros:** Free tier with e2-micro instance
- **Cons:** Similar setup to AWS EC2
- **Free Tier:** Always free e2-micro VM

### **PythonAnywhere**
- **Pros:** Python-focused, free tier
- **Cons:** Limited to 512MB RAM on free tier
- **Note:** May not support Streamlit on free tier

---

## 📊 **Comparison Table**

| Platform | Cost | Uptime | Ease | Best For |
|----------|------|--------|------|----------|
| **Streamlit Cloud** | FREE ✅ | High | ⭐⭐⭐⭐⭐ | This app! |
| **AWS EC2** | FREE (12mo) | 24/7 | ⭐⭐⭐ | Full control |
| **Render** | FREE | Sleep 15min | ⭐⭐⭐⭐ | Small apps |
| **Railway** | $5/mo credit | 24/7 | ⭐⭐⭐⭐ | Dev projects |
| **GCP** | FREE | 24/7 | ⭐⭐⭐ | Enterprise |

---

## 🎯 **Recommended Approach**

### **For Testing & Demo:**
Use **Streamlit Community Cloud**
- Fastest to deploy
- No infrastructure management
- Perfect for showing your bot

### **For Serious Trading:**
Use **AWS EC2** or your own VPS
- 24/7 uptime
- Full control
- Can run multiple bots
- Keep database persistent

### **Hybrid Approach:**
- **Frontend UI:** Streamlit Cloud (free, public access)
- **Trading Bot:** AWS EC2 (private, runs 24/7)
- Connect via API

---

## 🔒 **Security Best Practices**

1. **Never commit API keys to GitHub**
   - Use environment variables
   - Use Streamlit secrets (for Streamlit Cloud)
   - Use AWS Secrets Manager (for EC2)

2. **Protect your EC2 instance**
   ```bash
   # Install fail2ban
   sudo apt install -y fail2ban

   # Configure firewall
   sudo ufw allow 22
   sudo ufw allow 8501
   sudo ufw enable
   ```

3. **Enable 2FA on AWS account**

4. **Regular backups**
   ```bash
   # Backup database
   cp bot_config.db bot_config.db.backup
   cp trading.db trading.db.backup
   ```

---

## 🆘 **Troubleshooting**

### **Streamlit Cloud Issues:**

**Problem:** App crashes on deployment
- Check logs in Streamlit Cloud dashboard
- Ensure all dependencies in requirements.txt
- Check Python version compatibility

**Problem:** Database resets
- Expected behavior on redeploy
- Use persistent storage (AWS S3, external database)

### **AWS EC2 Issues:**

**Problem:** Can't connect to port 8501
```bash
# Check security group allows port 8501
# Check if app is running
sudo systemctl status ema-bot
```

**Problem:** TA-Lib installation fails
```bash
# Make sure build tools installed
sudo apt install -y build-essential
```

**Problem:** Out of memory
```bash
# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📞 **Need Help?**

- **Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud
- **AWS Free Tier:** https://aws.amazon.com/free/
- **Community:** Streamlit Forum, AWS Forums

---

**Good luck with your deployment! 🚀**

*Remember: Always test in paper trading mode before going live with real money!*
