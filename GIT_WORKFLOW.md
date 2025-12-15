# Git Workflow Guide

This guide will help you manage your trading bot project with Git and GitHub/GitLab.

---

## 🚀 Initial Setup

### 1. Initialize Git Repository

```bash
cd /path/to/trading-bot
git init
```

### 2. Create config.ini (DO NOT COMMIT!)

```bash
# Copy the example config
cp config.ini.example config.ini

# Edit with your credentials
nano config.ini  # or vim, or your favorite editor
```

### 3. Make Initial Commit

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: EMA Trading Bot v1.0

- 9-15 EMA strategy with confirmations
- Multi-broker support (Angel One, Zerodha, Mudrex)
- Stocks + Crypto trading
- Paper trading simulator
- Backtesting engine
- Web dashboard (Streamlit)
- Database for trade tracking
- Complete documentation"
```

---

## 📤 Push to GitHub

### Option 1: Create New Repository on GitHub

1. Go to GitHub: https://github.com/new
2. Repository name: `ema-trading-bot`
3. Description: `Algorithmic trading bot with 9-15 EMA strategy`
4. **Keep it Private** (your trading strategy!)
5. Don't initialize with README (we have one)
6. Click "Create repository"

### Option 2: Push to GitHub

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/ema-trading-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🔄 Daily Workflow

### Making Changes

```bash
# Check status
git status

# Add specific files
git add main.py dashboard.py

# Or add all changed files
git add .

# Commit with message
git commit -m "feat: Add trailing stop loss feature"

# Push to GitHub
git push
```

### Commit Message Convention

Use semantic commit messages:

```bash
feat: Add new feature
fix: Fix a bug
docs: Documentation changes
style: Code formatting
refactor: Code restructuring
test: Add tests
chore: Maintenance tasks
perf: Performance improvements
```

Examples:
```bash
git commit -m "feat: Add WhatsApp notifications"
git commit -m "fix: Resolve stop-loss calculation error"
git commit -m "docs: Update setup instructions"
git commit -m "perf: Optimize backtest speed by 50%"
```

---

## 🌿 Branching Strategy

### Create Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/add-telegram-bot

# Make your changes
# ... edit files ...

# Commit changes
git add .
git commit -m "feat: Add Telegram bot integration"

# Push branch
git push -u origin feature/add-telegram-bot
```

### Merge to Main

```bash
# Switch to main
git checkout main

# Merge feature
git merge feature/add-telegram-bot

# Push to GitHub
git push

# Delete feature branch (optional)
git branch -d feature/add-telegram-bot
```

---

## 🏷️ Version Tagging

### Create Release Tag

```bash
# Tag current version
git tag -a v1.0.0 -m "Release v1.0.0: Initial stable release"

# Push tags
git push --tags
```

### Semantic Versioning

- **v1.0.0**: Major release
- **v1.1.0**: New features (minor)
- **v1.0.1**: Bug fixes (patch)

---

## 🔙 Undo Changes

### Discard Local Changes

```bash
# Discard changes to specific file
git checkout -- filename.py

# Discard all local changes
git reset --hard HEAD
```

### Undo Last Commit

```bash
# Keep changes, undo commit
git reset --soft HEAD~1

# Discard changes and commit
git reset --hard HEAD~1
```

---

## 👥 Working with Claude Code

### 1. Clone Repository in Claude Code

```bash
# In Claude Code terminal
git clone https://github.com/YOUR_USERNAME/ema-trading-bot.git
cd ema-trading-bot
```

### 2. Tell Claude What You Want

```
Me: Add a feature to automatically optimize strategy parameters using grid search

Claude: [Implements feature, tests, commits]
```

### 3. Claude Will Handle Git

Claude Code can:
- Create commits with meaningful messages
- Create feature branches
- Push changes
- Create pull requests

---

## 📊 GitHub Actions (Automated Testing)

Your project includes GitHub Actions that will:

1. **Run tests** on every push
2. **Check code quality** (linting)
3. **Test on multiple Python versions** (3.8, 3.9, 3.10, 3.11)
4. **Verify imports** work correctly

View results in the "Actions" tab on GitHub.

---

## 🐳 Docker Workflow

### Build and Run with Docker

```bash
# Build image
docker build -t ema-trading-bot .

# Run dashboard
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Update and Rebuild

```bash
# After making changes
git add .
git commit -m "feat: New feature"
git push

# Rebuild Docker image
docker-compose build
docker-compose up -d
```

---

## 🔒 Security Best Practices

### Never Commit These Files

✅ Already in `.gitignore`:
- `config.ini`
- `*.db` (database files)
- `*.env` (environment files)
- `*.log` (log files)

### Before Committing

```bash
# Check what will be committed
git diff --cached

# Make sure no secrets are included
grep -r "api_key\|password\|secret" .
```

### If You Accidentally Commit Secrets

```bash
# Remove file from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch config.ini" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (DANGER: rewrites history)
git push --force --all
```

⚠️ **Better**: Immediately revoke exposed API keys!

---

## 📦 Backup Strategy

### Cloud Backup (GitHub)

```bash
# Regular pushes to GitHub
git push
```

### Local Backup

```bash
# Create backup branch
git checkout -b backup/$(date +%Y%m%d)
git push origin backup/$(date +%Y%m%d)
```

### Database Backup

```bash
# Backup database (not in Git)
cp trading_data.db backups/trading_data_$(date +%Y%m%d).db
```

---

## 🤝 Collaboration

### Invite Collaborators

1. Go to repository on GitHub
2. Settings → Collaborators
3. Add teammates
4. They can now push to your repository

### Pull Request Workflow

```bash
# Team member creates feature
git checkout -b feature/new-indicator
# ... make changes ...
git push origin feature/new-indicator

# Create Pull Request on GitHub
# Review → Approve → Merge
```

---

## 📱 Using with Claude Code

### Typical Claude Code Session

```bash
# Start Claude Code
claude-code

# Tell Claude what you want
You: "Review the code for bugs, fix any issues, commit with proper message"

Claude: 
[Analyzes code]
[Fixes bugs]
[Runs tests]
[Creates commit: "fix: Resolve position sizing bug in low capital scenarios"]
[Pushes to GitHub]

✓ 3 bugs fixed
✓ Tests passing
✓ Changes committed and pushed
```

### Advanced Claude Code Usage

```bash
You: "Optimize the strategy. Run parameter sweep, backtest results, 
     commit best parameters to a new branch"

Claude:
[Runs grid search on parameters]
[Tests 100 parameter combinations]
[Identifies best: EMA 8-21, RSI 65/35]
[Creates branch: optimize/parameters-v2]
[Commits results]
[Creates comparison chart]

✓ Optimal parameters found
✓ Win rate improved: 52% → 61%
✓ Branch created: optimize/parameters-v2
```

---

## 🎯 Quick Commands

```bash
# Status
git status

# Add all
git add .

# Commit
git commit -m "feat: description"

# Push
git push

# Pull latest
git pull

# View log
git log --oneline

# Create branch
git checkout -b branch-name

# Switch branch
git checkout branch-name

# Merge branch
git merge branch-name

# Tag version
git tag -a v1.0.0 -m "Release v1.0.0"

# Push tags
git push --tags
```

---

## 🆘 Troubleshooting

### Merge Conflicts

```bash
# Edit conflicted files manually
# Then:
git add .
git commit -m "fix: Resolve merge conflicts"
```

### Lost Commits

```bash
# Find lost commits
git reflog

# Recover
git checkout <commit-hash>
git checkout -b recovery-branch
```

### Large Files Error

```bash
# If you accidentally committed large files
# Install Git LFS
git lfs install
git lfs track "*.csv"
git add .gitattributes
```

---

## 📚 Resources

- **Git Documentation**: https://git-scm.com/doc
- **GitHub Guides**: https://guides.github.com/
- **Semantic Versioning**: https://semver.org/
- **Conventional Commits**: https://www.conventionalcommits.org/

---

## ✅ Checklist

Before you start:
- [ ] Git installed
- [ ] GitHub account created
- [ ] SSH keys configured (optional but recommended)
- [ ] config.ini created (from template)
- [ ] .gitignore includes config.ini

Initial setup:
- [ ] `git init`
- [ ] `git add .`
- [ ] `git commit -m "Initial commit"`
- [ ] Created GitHub repository
- [ ] `git remote add origin <url>`
- [ ] `git push -u origin main`

---

**Now you're ready to manage your trading bot with Git!** 🚀

Use Claude Code to make development even faster! 💪
