# 🤖 EMA Trading Bot - Complete End-to-End Platform

**Professional Algorithmic Trading System**  
Stocks + Crypto | Live + Paper + Backtest | Dashboard + Analytics

---

## 🌟 Features

### ✅ **Multi-Asset Support**
- 📊 **Stocks**: Angel One / Zerodha integration
- 💰 **Crypto**: Mudrex integration (BTC, ETH, 100+ coins)
- 🔄 Same strategy works on both markets

### ✅ **Trading Modes**
- 🚀 **Live Trading**: Real money, real markets
- 📝 **Paper Trading**: Practice with virtual money
- 🔬 **Backtesting**: Test on historical data

### ✅ **Advanced Features**
- 📈 **Web Dashboard**: Beautiful Streamlit interface
- 💾 **Database**: SQLite storage for all trades
- 📊 **Analytics**: Performance metrics, equity curves
- 🎯 **Risk Management**: Auto position sizing, stop-loss
- 🔔 **Alerts**: Email/Telegram notifications (configurable)

### ✅ **Strategy**
- **9-15 EMA Crossover** with confirmations
- **RSI** filter (avoid overbought/oversold)
- **MACD** confirmation
- **Volume** spike detection
- **Support/Resistance** levels
- **1:2 Risk-Reward** ratio

---

## 📁 Project Structure

```
trading-bot/
├── main.py                      # Main application entry point
├── dashboard.py                 # Web dashboard (Streamlit)
│
├── ema_algo_trading.py          # Core strategy logic
├── angel_one_live_trading.py    # Angel One stocks integration
├── mudrex_crypto_trading.py     # Mudrex crypto integration
│
├── paper_trading.py             # Paper trading simulator
├── backtest_engine.py           # Backtesting system
├── database_handler.py          # Database operations
│
├── config.ini                   # Configuration file
├── requirements.txt             # Python dependencies
│
├── README.md                    # This file
├── SETUP_GUIDE.md              # Detailed setup instructions
│
└── trading_data.db             # SQLite database (created automatically)
```

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials

Edit `config.ini`:

```ini
[ANGEL_ONE]
API_KEY = your_actual_api_key
CLIENT_CODE = your_client_code
PASSWORD = your_password
TOTP_SECRET = your_totp_secret

[MUDREX]
API_KEY = your_mudrex_api_key
API_SECRET = your_mudrex_api_secret
```

### 3. Launch Dashboard

```bash
python main.py --dashboard
```

Or use Streamlit directly:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 💻 Command Line Usage

```bash
# Launch web dashboard (RECOMMENDED)
python main.py --dashboard

# Paper trading (practice mode)
python main.py --paper

# Live stock trading (Angel One)
python main.py --live-stocks

# Live crypto trading (Mudrex)
python main.py --live-crypto

# Backtest on historical data
python main.py --backtest historical_data.csv

# View performance summary
python main.py --performance

# Use custom config file
python main.py --dashboard --config my_config.ini
```

---

## 📊 Dashboard Features

### **Main Tabs:**

1. **📈 Live Trading**
   - Real-time performance metrics
   - Open positions
   - Recent trade history
   - Equity curve

2. **📝 Paper Trading**
   - Practice trading interface
   - Virtual balance tracking
   - Risk-free testing

3. **🔬 Backtesting**
   - Upload historical CSV
   - Run strategy simulation
   - Detailed performance analysis
   - Equity curve visualization

4. **⚙️ Settings**
   - Strategy parameters
   - API configuration
   - Notification settings

---

## 📖 Usage Examples

### Example 1: Paper Trading

```python
from paper_trading import PaperTradingSimulator

# Initialize simulator
simulator = PaperTradingSimulator(
    initial_capital=10000,
    risk_per_trade=0.02
)

# Run paper trading
run_paper_trading(symbol='SBIN', exchange='NSE', capital=10000)
```

### Example 2: Backtest on Historical Data

```python
from backtest_engine import BacktestEngine, load_historical_data

# Load data
data = load_historical_data('historical_data.csv')

# Run backtest
engine = BacktestEngine(initial_capital=10000, risk_per_trade=0.02)
results = engine.run_backtest(data, symbol='SBIN')

# Plot results
engine.plot_results('backtest_chart.png')
```

### Example 3: Live Crypto Trading

```python
from mudrex_crypto_trading import run_crypto_trading

run_crypto_trading(
    api_key='your_api_key',
    api_secret='your_api_secret',
    symbol='BTC/USDT',
    capital=10000,
    risk_per_trade=0.02
)
```

### Example 4: Database Queries

```python
from database_handler import TradingDatabase

db = TradingDatabase()

# Get all trades
trades = db.get_all_trades(mode='live')

# Get performance summary
summary = db.get_performance_summary(mode='paper')

print(f"Total Trades: {summary['total_trades']}")
print(f"Win Rate: {summary['win_rate']:.2f}%")
print(f"Total P&L: ₹{summary['total_pnl']:,.2f}")
```

---

## 📈 Strategy Explanation

### Entry Conditions (ALL must be met):

1. ✅ **9 EMA crosses above 15 EMA** (bullish)
2. ✅ **Price above both EMAs** (trend confirmation)
3. ✅ **Volume > 1.2x average** (volume spike)
4. ✅ **RSI < 70** (not overbought for longs)
5. ✅ **RSI > 30** (not oversold for shorts)
6. ✅ **MACD confirms direction**
7. ✅ **Near support/resistance** (key levels)

### Exit Conditions (ANY met):

- ❌ Stop loss hit (recent swing low/high)
- ✅ Target hit (2x risk = 1:2 RR)
- ❌ Opposite EMA crossover

### Risk Management:

```
Capital: ₹10,000
Risk per Trade: 2% = ₹200
Position Size: Automatically calculated
Stop Loss: At recent swing low/high
Target: 2x risk (1:2 risk-reward)
Max Positions: 2-3 concurrent
Daily Loss Limit: 6% = ₹600
```

---

## 🏦 Broker Setup

### **Angel One (Stocks)**

1. Open account: https://www.angelone.in/
2. Go to: My Profile → API → Generate API Key
3. Note down: API Key, Client Code, Password, TOTP Secret
4. **Cost**: Free API (limited calls)

### **Zerodha (Stocks)**

1. Open account: https://zerodha.com/
2. Subscribe to Kite Connect
3. Create app and get API Key, Secret
4. **Cost**: ₹2,000/month

### **Mudrex (Crypto)**

1. Create account: https://mudrex.com/
2. Go to API settings
3. Generate API Key and Secret
4. **Cost**: Free for basic usage

---

## 📊 Database Schema

### **trades** table:
- trade_id (unique identifier)
- timestamp, entry_time, exit_time
- symbol, exchange, asset_type
- signal_type (BUY/SELL)
- entry_price, exit_price, quantity
- stop_loss, target
- pnl, pnl_percent
- status (OPEN/CLOSED)
- mode (live/paper/backtest)
- indicators (JSON)

---

## 🔧 Configuration

### **config.ini Structure:**

```ini
[ANGEL_ONE]
API_KEY = ...
CLIENT_CODE = ...
PASSWORD = ...
TOTP_SECRET = ...

[MUDREX]
API_KEY = ...
API_SECRET = ...

[TRADING]
SYMBOL = SBIN
EXCHANGE = NSE
TOTAL_CAPITAL = 10000
RISK_PER_TRADE = 0.02

[CRYPTO]
SYMBOL = BTC/USDT
CAPITAL = 10000
RISK_PER_TRADE = 0.02

[STRATEGY]
EMA_FAST = 9
EMA_SLOW = 15
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
RISK_REWARD_RATIO = 2.0

[NOTIFICATIONS]
ENABLE_EMAIL = False
EMAIL_ADDRESS = your@email.com
ENABLE_TELEGRAM = False
TELEGRAM_BOT_TOKEN = ...
```

---

## 📱 Notifications (Optional)

### **Email Alerts:**
```python
# In config.ini
ENABLE_EMAIL = True
EMAIL_ADDRESS = your@email.com
```

### **Telegram Alerts:**
```python
# In config.ini
ENABLE_TELEGRAM = True
TELEGRAM_BOT_TOKEN = your_bot_token
TELEGRAM_CHAT_ID = your_chat_id
```

---

## 🧪 Testing Workflow

### Recommended Testing Sequence:

1. ✅ **Backtest** (Test on historical data)
   ```bash
   python main.py --backtest historical_data.csv
   ```

2. ✅ **Paper Trading** (2-4 weeks minimum)
   ```bash
   python main.py --paper
   ```

3. ✅ **Live Trading** (Start small: ₹5-10k)
   ```bash
   python main.py --live-stocks
   ```

4. ✅ **Scale Up** (Gradually increase capital)

---

## 📊 Performance Tracking

### View Performance:

```bash
python main.py --performance
```

### Dashboard Analytics:

- Total Trades
- Win Rate %
- Total P&L
- Profit Factor
- Max Drawdown
- Sharpe Ratio
- Equity Curve
- Trade History

---

## 🚨 Risk Warnings

⚠️ **IMPORTANT:**

- Trading involves substantial risk of loss
- Start with paper trading (minimum 2-4 weeks)
- Test thoroughly before live trading
- Use only risk capital you can afford to lose
- Never remove stop-loss orders
- Follow risk management rules strictly
- Monitor positions daily
- This is for educational purposes

---

## 📚 Documentation

- **SETUP_GUIDE.md**: Detailed setup instructions
- **README.md**: This file (overview)
- Code comments: Inline documentation
- Dashboard: Built-in help tooltips

---

## 🔄 Updates & Maintenance

### Regular Tasks:

**Daily:**
- Check open positions
- Review executed trades
- Monitor system logs

**Weekly:**
- Analyze performance metrics
- Adjust parameters if needed
- Update historical data

**Monthly:**
- Full strategy review
- Optimize settings
- Backup database

---

## 🛠️ Troubleshooting

### **Issue**: API Connection Failed
**Solution**: Verify credentials, check internet, ensure 2FA is correct

### **Issue**: No Signals Generated
**Solution**: Market may be sideways (normal), wait for proper setup

### **Issue**: Database Error
**Solution**: Check file permissions, ensure SQLite is installed

### **Issue**: Dashboard Won't Load
**Solution**: Install Streamlit: `pip install streamlit`

---

## 🎯 Roadmap

### **Completed:**
- ✅ Core strategy implementation
- ✅ Multi-broker support (Angel One, Mudrex)
- ✅ Paper trading
- ✅ Backtesting
- ✅ Web dashboard
- ✅ Database storage
- ✅ Risk management

### **Planned:**
- 🔲 Machine learning optimization
- 🔲 Multiple strategies
- 🔲 Mobile app
- 🔲 Real-time alerts
- 🔲 Cloud deployment
- 🔲 Multi-timeframe analysis

---

## 📞 Support

### **Angel One:**
- Support: 1800-123-9555
- API Help: smartapi@angelbroking.com

### **Zerodha:**
- Support: 080-40402020
- Forum: tradingqna.com

### **Mudrex:**
- Support: support@mudrex.com
- Docs: docs.mudrex.com

---

## ⚖️ License

This project is for educational purposes only.  
Not financial advice. Use at your own risk.

---

## 🙏 Acknowledgments

Built with:
- Python 3.8+
- Pandas & NumPy (data processing)
- Streamlit (dashboard)
- Plotly (charts)
- SQLite (database)

---

## 📝 Version History

**v1.0** (December 2024)
- Initial release
- Stocks + Crypto support
- Live + Paper + Backtest modes
- Web dashboard
- Database storage
- Complete documentation

---

**Made with ❤️ for Indian Traders**

**Trade Safely! 📈**

*"Plan your trade, trade your plan."*
