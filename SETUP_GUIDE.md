# 9-15 EMA Algo Trading Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Broker Setup](#broker-setup)
4. [Testing Strategy](#testing-strategy)
5. [Live Trading](#live-trading)
6. [Risk Management](#risk-management)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Knowledge
- Basic Python programming
- Understanding of trading concepts
- Familiarity with EMA, RSI, MACD indicators

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- Stable internet connection
- Windows/Mac/Linux

---

## 📦 Installation

### Step 1: Install Python
Download from https://www.python.org/downloads/

### Step 2: Install Required Packages

```bash
# Create a virtual environment (recommended)
python -m venv trading_env

# Activate virtual environment
# On Windows:
trading_env\Scripts\activate
# On Mac/Linux:
source trading_env/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 3: Install TA-Lib (Technical Analysis Library)

**Windows:**
1. Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Install: `pip install TA_Lib‑0.4.xx‑cp3x‑cp3x‑win_amd64.whl`

**Mac:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux:**
```bash
sudo apt-get install ta-lib
pip install TA-Lib
```

---

## 🏦 Broker Setup

### Option 1: Angel One (Recommended for ₹10k capital)

**Advantages:**
- Free API (limited calls)
- No monthly charges
- Good for beginners

**Setup Steps:**

1. **Open Angel One Account**
   - Visit: https://www.angelone.in/
   - Complete KYC process

2. **Get API Access**
   - Login to Angel One web portal
   - Go to: My Profile → API
   - Generate API Key, Client Code
   - Enable 2FA (Two Factor Authentication)

3. **Get TOTP Secret** (for 2FA automation)
   - Download Google Authenticator
   - Scan QR code, note down the secret key
   - This is needed for automated login

4. **Update Code**
   ```python
   # In ema_algo_trading.py, update:
   api_key = "YOUR_ANGEL_ONE_API_KEY"
   client_code = "YOUR_CLIENT_CODE"
   password = "YOUR_PASSWORD"
   totp_secret = "YOUR_TOTP_SECRET"
   ```

5. **API Documentation**
   - Visit: https://smartapi.angelbroking.com/docs

---

### Option 2: Zerodha Kite Connect

**Advantages:**
- Most popular platform
- Excellent documentation
- Better developer community

**Disadvantages:**
- ₹2,000/month API charges

**Setup Steps:**

1. **Open Zerodha Account**
   - Visit: https://zerodha.com/

2. **Subscribe to Kite Connect**
   - Cost: ₹2,000/month
   - Login → Console → Create App

3. **Get API Credentials**
   - API Key
   - API Secret

4. **Update Code**
   ```python
   from kiteconnect import KiteConnect
   
   api_key = "YOUR_KITE_API_KEY"
   api_secret = "YOUR_KITE_API_SECRET"
   
   kite = KiteConnect(api_key=api_key)
   ```

5. **API Documentation**
   - Visit: https://kite.trade/docs/connect/v3/

---

## 🧪 Testing Strategy

### IMPORTANT: Test Before Live Trading!

### Step 1: Paper Trading (Simulated Trading)

Both Angel One and Zerodha offer paper trading accounts:

**Angel One:**
- Use sandbox environment for testing
- No real money involved

**Zerodha:**
- Kite Connect provides test environment
- Practice with virtual money

### Step 2: Backtesting with Historical Data

```python
import pandas as pd
from ema_algo_trading import backtest_strategy

# Load historical data
data = pd.read_csv('historical_data.csv')

# Required columns: timestamp, open, high, low, close, volume
# Run backtest
backtest_strategy(data)
```

**Where to get historical data:**
1. **Angel One API**: Use historicalAPI
2. **Zerodha**: Use historical data endpoint
3. **Free sources**: Yahoo Finance, Alpha Vantage

### Step 3: Forward Testing

Run the algo in paper trading for at least 2-4 weeks before going live.

---

## 🚀 Live Trading

### Before You Start Live Trading:

**Checklist:**
- ✅ Backtested on 3+ months of data
- ✅ Paper traded for 2-4 weeks successfully
- ✅ Understand all entry/exit rules
- ✅ Risk management parameters set
- ✅ Stop-loss and targets configured
- ✅ API credentials secured
- ✅ Emergency stop mechanism ready

### Running Live Trading:

```python
from ema_algo_trading import run_live_trading

# Start trading on specific stock
run_live_trading(symbol='SBIN', exchange='NSE')
```

### Best Practices:

1. **Start Small**
   - Begin with liquid stocks (SBIN, RELIANCE)
   - Trade only 1-2 stocks initially

2. **Monitor Daily**
   - Check positions morning and evening
   - Review trades weekly

3. **Keep Logs**
   - All trades are printed to console
   - Save logs: `python ema_algo_trading.py > trading_log.txt`

4. **Set Alerts**
   - Email/SMS for every trade execution
   - Notifications for system errors

---

## ⚠️ Risk Management

### Capital Allocation (₹10,000 Capital)

```
Total Capital: ₹10,000
Risk per Trade: 2% = ₹200
Maximum Positions: 2-3 at a time
Keep Buffer: ₹2,000 (for margin calls)
Trading Capital: ₹8,000
```

### Position Sizing Formula

The algo automatically calculates position size:
```
Risk Amount = Capital × Risk%
Position Size = Risk Amount / (Entry Price - Stop Loss)
```

**Example:**
- Capital: ₹10,000
- Risk: 2% = ₹200
- Entry: ₹100
- Stop Loss: ₹98
- Risk per share: ₹2
- Quantity: 200 / 2 = 100 shares

### Stop Loss Rules

1. **Never disable stop-loss**
2. **Never move stop-loss against position**
3. **Exit immediately if SL hit**
4. **Use only 2% risk per trade**

### Daily Loss Limit

```
Maximum Daily Loss: 6% of capital = ₹600
After 3 consecutive losses: Stop trading for the day
Weekly Review: Adjust if needed
```

---

## 🔍 Strategy Parameters

### Current Settings:

```python
EMA Periods: 9, 15
RSI Period: 14
RSI Overbought: >70 (avoid longs)
RSI Oversold: <30 (avoid shorts)
MACD: 12, 26, 9
Volume Threshold: 1.2x average
Risk-Reward: 1:2
Stop Loss: Recent swing low/high
```

### Customization:

You can adjust these in the code:

```python
# In calculate_rsi() function
rsi = self.calculate_rsi(data, period=14)  # Change period

# In generate_signal() function
rsi_ok = rsi_current < 70  # Change threshold

# In calculate_stop_loss_target() function
target = current_price + (risk * 2)  # Change RR ratio
```

---

## 📊 Best Stocks for This Strategy

### Recommended (High Liquidity):

**Large Cap:**
- RELIANCE
- TCS
- INFY
- SBIN
- HDFCBANK
- ICICIBANK
- WIPRO
- LT

**Mid Cap:**
- VOLTAS
- HAVELLS
- DIXON
- TATAELXSI

### Avoid:
- Penny stocks
- Low volume stocks (<1 lakh daily volume)
- Very volatile stocks (±5% daily swings)
- Illiquid options

---

## 🕐 Trading Hours

### Optimal Trading Times:

**Morning Session (9:15 AM - 11:00 AM)**
- Best liquidity
- Clear trends
- Most signals

**Avoid:**
- 11:00 AM - 2:00 PM (choppy, low volume)

**Evening Session (2:30 PM - 3:15 PM)**
- Some opportunities
- Less reliable

**Auto-Trading Schedule:**
```python
# Only trade during market hours
MARKET_OPEN = "09:15"
MARKET_CLOSE = "15:30"
AVOID_START = "11:00"
AVOID_END = "14:00"
```

---

## 🛠️ Troubleshooting

### Common Issues:

**1. API Connection Failed**
```
Error: Invalid API credentials
Solution: 
- Verify API key and secret
- Check 2FA/TOTP settings
- Ensure account is active
```

**2. No Signals Generated**
```
Possible Reasons:
- Market is sideways (EMAs flat)
- RSI in extreme zones
- Volume too low
- Not near support/resistance

Solution: This is normal, wait for proper setup
```

**3. Too Many False Signals**
```
Solution:
- Increase volume threshold
- Tighten RSI filters
- Add trend filter (check higher timeframe)
```

**4. Stop Loss Hit Frequently**
```
Solution:
- Increase stop-loss buffer
- Trade only trending markets
- Check if spreads are too wide
```

**5. Position Size Too Small**
```
Reason: Stop-loss too wide
Solution:
- Tighten stop-loss
- Increase capital
- Trade lower-priced stocks
```

---

## 📈 Performance Tracking

### Metrics to Track:

```
Win Rate: Winning trades / Total trades
Average Win: Total profit / Winning trades
Average Loss: Total loss / Losing trades
Profit Factor: Total profit / Total loss
Max Drawdown: Largest peak-to-trough decline
Risk-Reward Ratio: Average win / Average loss
```

### Monthly Review:

Create a trading journal:
```
Date | Stock | Entry | Exit | P&L | % | Notes
-------------------------------------------
12/12 | SBIN | 620 | 625 | +500 | +0.8% | Perfect setup
13/12 | TCS | 3500 | 3480 | -200 | -0.57% | False signal
```

---

## 📞 Support & Resources

### Angel One Support
- Email: support@angelbroking.com
- Phone: 1800-123-9555
- API Help: smartapi@angelbroking.com

### Zerodha Support
- Email: support@zerodha.com
- Phone: 080-40402020
- Developer Forum: tradingqna.com

### Learning Resources
- Zerodha Varsity: https://zerodha.com/varsity/
- Investopedia: https://www.investopedia.com/
- TradingView: https://www.tradingview.com/

---

## ⚖️ Legal Disclaimer

**IMPORTANT:**

1. This is an educational tool
2. Trading involves substantial risk
3. Past performance ≠ future results
4. Start with paper trading
5. Only risk capital you can afford to lose
6. Consult a financial advisor
7. Comply with all SEBI regulations
8. Maintain tax records of all trades

**The creator is not responsible for any trading losses.**

---

## 🔄 Updates & Maintenance

### Regular Maintenance:

**Daily:**
- Check system logs
- Verify API connection
- Review executed trades

**Weekly:**
- Analyze performance
- Adjust parameters if needed
- Backup trade logs

**Monthly:**
- Full strategy review
- Update historical data
- Optimize parameters

---

## 📝 Next Steps

1. ✅ Install Python and packages
2. ✅ Open broker account (Angel One recommended)
3. ✅ Get API credentials
4. ✅ Download historical data
5. ✅ Run backtests
6. ✅ Start paper trading
7. ✅ Monitor for 2-4 weeks
8. ✅ Go live with small capital
9. ✅ Scale up gradually

---

**Questions?**

Review the code comments in `ema_algo_trading.py` for detailed explanations.

Good luck with your algo trading journey! 🚀

Remember: "Plan your trade, trade your plan."
