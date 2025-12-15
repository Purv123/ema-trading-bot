# 🤖 EMA Trading Bot

**Professional Algorithmic Trading Platform for Stocks & Cryptocurrencies**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)

> Automated trading bot using the proven 9-15 EMA crossover strategy with advanced confirmations. Trade stocks through Angel One/Zerodha and cryptocurrencies through Mudrex. Features include live trading, paper trading, backtesting, and a beautiful web dashboard.

---

## ✨ Features

### 🎯 **Multi-Asset Support**
- 📊 **Stocks**: Angel One & Zerodha integration
- 💰 **Crypto**: Mudrex (BTC, ETH, 100+ coins)
- 🔄 Same strategy across all markets

### 🚀 **Trading Modes**
- **Live Trading**: Real money, real markets
- **Paper Trading**: Risk-free practice with virtual money
- **Backtesting**: Test strategies on historical data

### 📈 **Advanced Platform**
- **Web Dashboard**: Beautiful Streamlit interface
- **Database**: SQLite for trade history & analytics
- **Risk Management**: Auto position sizing & stop-loss
- **Analytics**: Performance metrics, equity curves, drawdown charts
- **Alerts**: Email & Telegram notifications

---

## 🚀 Quick Start

### Installation

#### Option 1: Automated Setup

**Linux/Mac:**
```bash
git clone https://github.com/YOUR_USERNAME/ema-trading-bot.git
cd ema-trading-bot
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
git clone https://github.com/YOUR_USERNAME/ema-trading-bot.git
cd ema-trading-bot
setup.bat
```

#### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy config template
cp config.ini.example config.ini

# Edit with your API credentials
nano config.ini
```

### 🎨 Launch Dashboard

```bash
python main.py --dashboard
```

Dashboard opens at: **http://localhost:8501**

---

## 📖 Usage

```bash
# Web Dashboard
python main.py --dashboard

# Paper Trading (practice)
python main.py --paper

# Live Trading (stocks)
python main.py --live-stocks

# Live Trading (crypto)
python main.py --live-crypto

# Backtest
python main.py --backtest data.csv

# Performance Summary
python main.py --performance
```

---

## 🎯 Strategy

### Entry Conditions
✅ 9 EMA crosses 15 EMA  
✅ Volume > 1.2x average  
✅ RSI filter (< 70 for longs, > 30 for shorts)  
✅ MACD confirmation  
✅ Near support/resistance  

### Exit Conditions
❌ Stop loss hit  
✅ Target hit (1:2 RR)  
❌ Opposite crossover  

---

## 📚 Documentation

- **[Setup Guide](SETUP_GUIDE.md)** - Detailed installation
- **[Git Workflow](GIT_WORKFLOW.md)** - Version control
- **[Claude Code Guide](CLAUDE_CODE_GUIDE.md)** - AI development
- **[Contributing](CONTRIBUTING.md)** - Contribution guide

---

## 🐳 Docker

```bash
# Launch dashboard
docker-compose up -d

# With paper trading
docker-compose --profile paper up -d

# Stop
docker-compose down
```

---

## 🔒 Security

⚠️ **NEVER commit `config.ini`** - Contains API keys  
✅ Use `config.ini.example` as template  
✅ Check `.gitignore` before committing  

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📝 License

MIT License - See [LICENSE](LICENSE)

**Disclaimer**: Educational purposes only. Trading involves risk.

---

## 🙏 Acknowledgments

Python • Pandas • NumPy • Streamlit • Plotly • TA-Lib

---

**Made with ❤️ for traders**

*Trade safely, trade smart!* 📈
