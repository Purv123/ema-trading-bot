# 🚀 Git & GitHub Setup - Complete Guide

## ⚡ Quick Start (5 Minutes)

This guide will help you set up your trading bot with Git and GitHub/GitLab.

---

## 📋 Prerequisites

- [ ] Git installed ([Download](https://git-scm.com/downloads))
- [ ] GitHub account ([Sign up](https://github.com/signup))
- [ ] Project files downloaded

---

## 🎯 Step-by-Step Setup

### Step 1: Extract & Navigate

```bash
# Extract the downloaded files
cd /path/to/downloaded/folder

# Verify files are present
ls -la
```

You should see:
```
README.md
main.py
dashboard.py
config.ini.example
.gitignore
setup.sh
... and more
```

### Step 2: Initialize Git

```bash
# Initialize Git repository
git init

# Check status
git status
```

### Step 3: Create config.ini

```bash
# Copy template
cp config.ini.example config.ini

# Edit with your credentials
nano config.ini  # or use any text editor
```

**IMPORTANT**: Add your actual API keys to `config.ini`

### Step 4: First Commit

```bash
# Add all files (config.ini is excluded by .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: EMA Trading Bot v1.0"
```

### Step 5: Create GitHub Repository

**Option A: Using GitHub Website**

1. Go to: https://github.com/new
2. Repository name: `ema-trading-bot`
3. Description: `Algorithmic trading bot with 9-15 EMA strategy`
4. **Private** (recommended for trading strategies)
5. **Don't initialize** with README (we have one)
6. Click "Create repository"

**Option B: Using GitHub CLI** (if installed)

```bash
gh repo create ema-trading-bot --private --source=. --remote=origin --push
```

### Step 6: Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ema-trading-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Done!** 🎉 Your project is now on GitHub!

---

## 🔐 SSH Setup (Optional but Recommended)

### Generate SSH Key

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Start ssh-agent
eval "$(ssh-agent -s)"

# Add key
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

### Add to GitHub

1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Paste your public key
4. Click "Add SSH key"

### Use SSH URL

```bash
# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/ema-trading-bot.git
```

---

## 🏃 Running the Bot

### First Time Setup

```bash
# Run setup script
chmod +x setup.sh
./setup.sh

# Or on Windows
setup.bat
```

### Launch Dashboard

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start dashboard
python main.py --dashboard
```

### Paper Trading (Start Here!)

```bash
python main.py --paper
```

---

## 🔄 Daily Workflow

### Make Changes

```bash
# Edit files
nano main.py  # or use your IDE

# Check changes
git status
git diff

# Add changes
git add main.py

# Commit
git commit -m "feat: Add new feature"

# Push to GitHub
git push
```

### Pull Latest Changes

```bash
# Get latest from GitHub
git pull
```

---

## 🌿 Branching

### Create Feature Branch

```bash
# Create new branch
git checkout -b feature/add-whatsapp-alerts

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "feat: Add WhatsApp notifications"

# Push branch
git push -u origin feature/add-whatsapp-alerts
```

### Merge Branch

```bash
# Switch to main
git checkout main

# Merge feature
git merge feature/add-whatsapp-alerts

# Push
git push

# Delete branch (optional)
git branch -d feature/add-whatsapp-alerts
```

---

## 🐳 Docker Setup

### Build & Run

```bash
# Build image
docker build -t ema-trading-bot .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🤖 Using with Claude Code

### Install Claude Code

Follow instructions at: https://docs.claude.com

### Clone Your Repository

```bash
# In Claude Code
claude-code
```

Then:
```
Me: Clone my ema-trading-bot repository from GitHub and set it up

Claude: [Clones repo, installs dependencies, sets up environment]
```

### Development with Claude

```
Me: Add a feature to send WhatsApp alerts when trades are executed

Claude: [Implements feature, tests it, commits with proper message]
```

---

## 📊 GitHub Features

### Issues

Track bugs and features:
- Go to: `Issues` tab
- Click "New issue"
- Describe problem/feature
- Assign labels

### Projects

Organize work:
- Go to: `Projects` tab
- Create project board
- Add cards for tasks

### Actions

View automated tests:
- Go to: `Actions` tab
- See test results
- Check build status

---

## 🔒 Security Checklist

Before pushing to GitHub:

```bash
# Check what will be committed
git status

# Verify .gitignore is working
git ls-files | grep config.ini
# Should return nothing

# Check for secrets
grep -r "api_key\|password\|secret" . --exclude-dir=.git
# Review output carefully
```

---

## 📚 Important Files

### Never Commit These
- `config.ini` (contains API keys)
- `*.db` (database files)
- `*.log` (log files)
- `venv/` (virtual environment)

### Always Commit These
- `config.ini.example` (template)
- All `.py` files
- `requirements.txt`
- Documentation (`.md` files)
- `.gitignore`

---

## 🆘 Troubleshooting

### Problem: Can't push to GitHub

```bash
# Check remote
git remote -v

# Re-add remote
git remote set-url origin https://github.com/YOUR_USERNAME/ema-trading-bot.git

# Try again
git push
```

### Problem: Merge conflict

```bash
# Pull latest
git pull

# Edit conflicted files manually
# Look for <<<<<<< HEAD markers

# After fixing
git add .
git commit -m "fix: Resolve merge conflict"
git push
```

### Problem: Accidentally committed config.ini

```bash
# Remove from Git (keep local file)
git rm --cached config.ini

# Commit the removal
git commit -m "fix: Remove config.ini from Git"

# Push
git push

# IMPORTANT: Revoke exposed API keys immediately!
```

### Problem: Large file error

```bash
# For large historical data files
# Don't commit them - use .gitignore

# Already committed? Remove from history
git filter-branch --tree-filter 'rm -f data/large_file.csv' HEAD
```

---

## 📈 Next Steps

1. ✅ Repository on GitHub
2. ✅ Files committed
3. ✅ Config.ini created (not committed)
4. ⬜ Test paper trading (2-4 weeks)
5. ⬜ Run backtests
6. ⬜ Add features with Claude Code
7. ⬜ Go live (when ready)

---

## 🎓 Learning Resources

- **Git Basics**: https://git-scm.com/book/en/v2
- **GitHub Guides**: https://guides.github.com/
- **Git Cheatsheet**: https://education.github.com/git-cheat-sheet-education.pdf

---

## 💡 Tips

1. **Commit often**: Small commits are better than large ones
2. **Write good messages**: `"feat: Add feature"` not `"update"`
3. **Use branches**: Don't commit directly to main
4. **Pull before push**: Always sync before pushing
5. **Backup**: GitHub is your backup, push regularly

---

## ✅ Success Checklist

- [ ] Git initialized
- [ ] config.ini created from example
- [ ] config.ini added to .gitignore
- [ ] First commit made
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Setup script run
- [ ] Dashboard launches successfully
- [ ] Paper trading tested

---

## 🎉 You're All Set!

Your trading bot is now:
- ✅ Version controlled with Git
- ✅ Backed up on GitHub
- ✅ Ready for Claude Code
- ✅ Ready for development

**Start paper trading and iterate from there!**

---

## 📞 Need Help?

1. Check [GIT_WORKFLOW.md](GIT_WORKFLOW.md)
2. Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. Search GitHub Issues
4. Create new issue on GitHub

---

**Happy Trading! 📈**

*Remember: Start with paper trading, test thoroughly, then go live!*
