# 🤖 EMA Trading Bot

**Automated Trading Bot with Complete Web UI Configuration**

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)

> Automated trading bot using the proven 9-15 EMA crossover strategy. Trade Indian stocks or cryptocurrencies with **everything configured through an easy-to-use web interface** - no config files needed!

---

## ✨ Features

### 🎯 **Complete UI Configuration**
- 🎨 **No Config Files!** - Everything configured through web UI
- 🚀 **Setup Wizard** - Step-by-step guided setup
- 🔄 **Easy Reconfiguration** - Change settings anytime
- 💾 **Automatic Saving** - All settings saved to database

### 📊 **Multi-Market Support**
- **Indian Stock Market** - Trade NSE/BSE stocks with Angel One/Zerodha
- **Cryptocurrency** - Trade BTC, ETH, and more on Mudrex/Binance
- **Market Selection** - Choose your market through UI

### 🚀 **Trading Modes**
- **Live Trading** - Real money, real markets
- **Paper Trading** - Risk-free practice with virtual money
- **Backtesting** - Test strategies on historical data

### 📈 **Professional Dashboard**
- **Real-time Monitoring** - Track performance live
- **Beautiful Charts** - Equity curves, P&L graphs
- **Trade History** - Complete trading journal
- **Performance Metrics** - Win rate, profit factor, Sharpe ratio

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 🎨 Launch the Application

```bash
streamlit run app.py
```

The app will open in your browser at: **http://localhost:8501**

### ✅ Complete Setup Wizard

On first launch, you'll be guided through:

1. **Step 1: Choose Market**
   - Select Indian Stock Market or Cryptocurrency

2. **Step 2: Configure API**
   - Enter your broker/exchange credentials
   - All saved securely in database

3. **Step 3: Set Trading Parameters**
   - Define your capital
   - Set risk per trade (1-5%)

4. **Step 4: Strategy Settings**
   - Customize EMA periods
   - Adjust RSI parameters
   - Set risk-reward ratio

5. **Step 5: Done!**
   - Dashboard ready to use
   - Start with paper trading

---

## 📖 How to Use

### First Time Setup

```bash
streamlit run app.py
```

Follow the setup wizard to configure everything through the UI!

### Using the Dashboard

After setup, you get access to:

- **🏠 Dashboard** - View trading performance and stats
- **▶️ Trading Control** - Start/stop live trading
- **📝 Paper Trading** - Practice with virtual money
- **🔬 Backtesting** - Test on historical data
- **⚙️ Settings** - Update configuration anytime
- **🔄 Reconfigure** - Run setup wizard again

### Recommended Workflow

1. **Complete Initial Setup** through the wizard
2. **Start Paper Trading** to test the strategy risk-free
3. **Run Backtests** on historical data
4. **Monitor Performance** for a few days
5. **Go Live** when confident (start small!)

---

## 📖 Old CLI Interface (Deprecated)

The old command-line interface (`main.py`) is still available but deprecated:

```bash
# Old way (deprecated)
python main.py --dashboard
python main.py --paper
python main.py --live-stocks

# New way (recommended)
streamlit run app.py
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
