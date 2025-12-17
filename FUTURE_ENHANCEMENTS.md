# Multi-User & Options Trading Enhancement Plan

## 🔐 MULTI-USER SUPPORT

### Current Issues:
- Single shared configuration database
- No user authentication
- No user isolation
- All users see same data

### Required Changes:

#### 1. User Authentication System
```python
# Add to requirements.txt
streamlit-authenticator>=0.2.3
bcrypt>=4.0.1

# Database schema
users_table:
  - user_id (primary key)
  - username (unique)
  - email (unique)
  - password_hash
  - created_at
  - is_active
```

#### 2. Per-User Configuration
```python
# Update config_manager.py to support user_id
def get_config(self, user_id, key, default=None):
    # Fetch config specific to user_id

# Database schema
user_config_table:
  - config_id (primary key)
  - user_id (foreign key)
  - key
  - value
  - updated_at
```

#### 3. Per-User Trading Data
```python
# Update database_handler.py
trades_table:
  - trade_id (primary key)
  - user_id (foreign key)  # NEW!
  - symbol
  - entry_price
  - exit_price
  - ...
```

#### 4. Session Management
```python
# In app.py
import streamlit_authenticator as stauth

# Initialize authenticator
authenticator = stauth.Authenticate(
    credentials,
    cookie_name='ema_bot',
    key='trading_bot_key',
    cookie_expiry_days=30
)

# Login widget
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # User is logged in
    user_id = get_user_id(username)
    # All operations use user_id
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

### Architecture for Multi-User:

```
User 1 Login → User 1 Config → User 1 Bot Instance → User 1 Trades
User 2 Login → User 2 Config → User 2 Bot Instance → User 2 Trades
User 3 Login → User 3 Config → User 3 Bot Instance → User 3 Trades
```

### Implementation Complexity:
- **Time Required:** 3-5 days
- **Difficulty:** Medium
- **Database Changes:** Significant
- **Files to Modify:** 6-8 files

---

## 📊 OPTIONS TRADING FOR NIFTY 50 F&O

### Current Limitations:
- ❌ Only single stock monitoring
- ❌ No options support
- ❌ No multi-symbol scanning
- ❌ No strike price selection

### Your Requirements:

#### 1. Real-Time Multi-Stock Scanning
```
Scan all 50 Nifty F&O stocks simultaneously
↓
Generate EMA signals for each
↓
When signal found → Trade options for that stock
```

#### 2. Option Selection Logic
```
Signal: BUY on RELIANCE at ₹2,500
↓
Fetch options chain
↓
Find nearest Call strike (2,500 or 2,520)
↓
Place Call option order
```

#### 3. Required Components

**A. Multi-Symbol Scanner**
```python
class MultiSymbolScanner:
    def __init__(self, symbols_list):
        # Monitor 50 stocks simultaneously
        self.symbols = symbols_list  # Nifty 50 F&O stocks

    def scan_all_symbols(self):
        signals = []
        for symbol in self.symbols:
            # Fetch data for each stock
            df = fetch_market_data(symbol)

            # Generate signal
            signal = strategy.generate_signal(df)

            if signal:
                signals.append({
                    'symbol': symbol,
                    'signal': signal,
                    'price': current_price
                })

        return signals
```

**B. Options Chain Fetcher**
```python
class OptionsChainFetcher:
    def get_options_chain(self, symbol, expiry):
        # Fetch from NSE/broker API
        # Returns all strikes with CE/PE data

    def find_nearest_strike(self, current_price, option_type='CE'):
        # Round to nearest strike
        # Example: 2,487 → 2,500 (if strikes are 100 apart)

    def get_option_symbol(self, symbol, strike, expiry, option_type):
        # Format: RELIANCE24DEC2500CE
        return f"{symbol}{expiry}{strike}{option_type}"
```

**C. Option Trading Module**
```python
class OptionsTrader:
    def place_option_order(self, symbol, strike, option_type, quantity):
        # Place option order via Angel One API
        # Handle F&O specific parameters (lot size, etc.)

    def calculate_lot_size(self, symbol):
        # Get F&O lot size from static data
        lot_sizes = {
            'RELIANCE': 250,
            'TCS': 125,
            'INFY': 300,
            # ... all 50 stocks
        }
        return lot_sizes.get(symbol, 1)
```

### NSE Nifty 50 F&O Stocks (All 50):
```python
NIFTY_50_FNO = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
    'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
    'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA',
    'TITAN', 'BAJFINANCE', 'ULTRACEMCO', 'NESTLEIND', 'WIPRO',
    'HCLTECH', 'TECHM', 'POWERGRID', 'NTPC', 'M&M',
    'TATAMOTORS', 'TATASTEEL', 'ADANIPORTS', 'ONGC', 'COALINDIA',
    'BAJAJFINSV', 'JSWSTEEL', 'INDUSINDBK', 'GRASIM', 'CIPLA',
    'DRREDDY', 'BRITANNIA', 'EICHERMOT', 'APOLLOHOSP', 'DIVISLAB',
    'HEROMOTOCO', 'HINDALCO', 'BPCL', 'SHREECEM', 'TATACONSUM',
    'UPL', 'SBILIFE', 'BAJAJ-AUTO', 'HDFCLIFE', 'ADANIENT'
]
```

### Data Flow:

```
Every 5 minutes:
├─ Fetch 5-min candles for all 50 stocks
├─ Calculate EMA-9, EMA-15 for each
├─ Generate signals
│
└─ When signal found (e.g., RELIANCE BUY):
    ├─ Current Price: ₹2,487
    ├─ Find nearest strike: ₹2,500
    ├─ Fetch options chain
    ├─ Select: RELIANCE24DEC2500CE
    ├─ Calculate lot size: 250
    └─ Place order: BUY 250 qty RELIANCE24DEC2500CE
```

### Angel One API Requirements:

```python
# For Options Trading
1. Historical data API (all 50 stocks)
2. Options chain API
3. F&O order placement API
4. Symbol master (for option symbols)
5. Lot size data
```

### Implementation Complexity:

**Phase 1: Multi-Symbol Scanning**
- Time: 2-3 days
- Create scanner for 50 stocks
- Parallel data fetching
- Signal aggregation

**Phase 2: Options Chain Integration**
- Time: 3-4 days
- Fetch options data from NSE
- Strike price calculation
- Option symbol formatting

**Phase 3: Options Trading**
- Time: 3-4 days
- Angel One F&O API integration
- Lot size management
- Options order placement

**Total:** 8-11 days of development

---

## 🎯 MY RECOMMENDATIONS

### For Multi-User Support:

**Option A: Simple Authentication**
- Add login page
- Basic user separation
- Quick to implement (2-3 days)

**Option B: Full Multi-Tenant**
- Complete user isolation
- Scalable architecture
- Takes longer (5-7 days)

### For Options Trading:

**Phase 1 (Start Here):**
1. Add multi-symbol scanning
2. Test with 5 stocks first
3. Verify signal generation works

**Phase 2:**
4. Add options chain fetching
5. Implement strike selection
6. Test on paper trading

**Phase 3:**
7. Integrate with Angel One F&O API
8. Add lot size calculations
9. Live testing with small capital

---

## ❓ QUESTIONS FOR YOU

### 1. Multi-User:
- How many users do you expect? (10? 100? 1000?)
- Do users need to see each other's trades?
- Is this for personal use or a service for others?
- Do you want user signup or admin-managed accounts?

### 2. Options Trading:
- Which expiry do you want to trade? (Weekly/Monthly)
- At-the-money (ATM) or Out-of-the-money (OTM)?
- How far from ATM? (±1 strike, ±2 strikes?)
- Trade CE (calls) and PE (puts) both?
- Maximum number of simultaneous positions?

### 3. Risk Management:
- Maximum capital per option trade?
- Stop loss for options (% or points)?
- Intraday or positional?
- Max positions across all stocks?

### 4. Data Source:
- Do you have Angel One API access for F&O?
- Do you have options trading enabled?
- Any alternative data sources for NSE options?

---

## 🚀 NEXT STEPS

**If you want me to implement this:**

1. **Answer the questions above**
2. **I'll create:**
   - Multi-user authentication system
   - Multi-symbol scanner for 50 stocks
   - Options chain integration
   - Strike selection logic
   - F&O trading module
   - Updated UI for options

3. **Timeline:**
   - Multi-user: 3-5 days
   - Options trading: 8-11 days
   - Total: 2-3 weeks

**Or we can start with a simpler version:**
- Multi-symbol scanning only (no options)
- Basic user separation (no full multi-tenant)
- Test with paper trading first

Let me know your preferences and I'll build accordingly! 🚀
