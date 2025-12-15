"""
9-15 EMA Algo Trading Strategy
For Angel One / Zerodha
Capital: 10,000 INR
Timeframe: 5 minutes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Technical Indicators Library
try:
    import talib
except ImportError:
    print("Installing TA-Lib... Please wait")
    # You'll need to install: pip install TA-Lib

# For Angel One API
try:
    from SmartApi import SmartConnect
except ImportError:
    print("Install Angel One API: pip install smartapi-python")

# For Zerodha API (alternative)
try:
    from kiteconnect import KiteConnect
except ImportError:
    print("Install Zerodha API: pip install kiteconnect")


class EMAStrategy:
    def __init__(self, capital=10000, risk_per_trade=0.02):
        """
        Initialize the trading strategy
        
        Parameters:
        -----------
        capital : float
            Starting capital (default 10,000 INR)
        risk_per_trade : float
            Risk percentage per trade (default 2%)
        """
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.position = None  # Current position: None, 'LONG', or 'SHORT'
        self.entry_price = 0
        self.stop_loss = 0
        self.target = 0
        
    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        return data['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, data, period=14):
        """Calculate Relative Strength Index"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data):
        """Calculate MACD"""
        exp1 = data['close'].ewm(span=12, adjust=False).mean()
        exp2 = data['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    def check_volume_increase(self, data, lookback=5):
        """
        Check if current volume is higher than average
        
        Returns True if current volume > average of last 'lookback' periods
        """
        if len(data) < lookback + 1:
            return False
        
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].iloc[-lookback-1:-1].mean()
        
        return current_volume > avg_volume * 1.2  # 20% above average
    
    def find_support_resistance(self, data, window=20):
        """
        Simple support/resistance detection using pivot points
        
        Returns recent support and resistance levels
        """
        if len(data) < window:
            return None, None
        
        # Find local highs and lows
        highs = data['high'].rolling(window=window).max()
        lows = data['low'].rolling(window=window).min()
        
        resistance = highs.iloc[-1]
        support = lows.iloc[-1]
        
        return support, resistance
    
    def is_near_support_resistance(self, price, support, resistance, tolerance=0.005):
        """
        Check if price is near support or resistance level
        
        tolerance: percentage distance (0.005 = 0.5%)
        """
        if support is None or resistance is None:
            return True  # If can't determine, allow trade
        
        # Check if price is within tolerance of support or resistance
        near_support = abs(price - support) / price < tolerance
        near_resistance = abs(price - resistance) / price < tolerance
        
        return near_support or near_resistance
    
    def generate_signal(self, data):
        """
        Generate trading signals based on strategy rules
        
        Returns: 'BUY', 'SELL', or None
        """
        if len(data) < 30:  # Need enough data
            return None
        
        # Calculate indicators
        data['ema9'] = self.calculate_ema(data, 9)
        data['ema15'] = self.calculate_ema(data, 15)
        data['rsi'] = self.calculate_rsi(data)
        data['macd'], data['macd_signal'], data['macd_hist'] = self.calculate_macd(data)
        
        # Get current values
        current_price = data['close'].iloc[-1]
        ema9_current = data['ema9'].iloc[-1]
        ema15_current = data['ema15'].iloc[-1]
        ema9_prev = data['ema9'].iloc[-2]
        ema15_prev = data['ema15'].iloc[-2]
        
        rsi_current = data['rsi'].iloc[-1]
        macd_current = data['macd'].iloc[-1]
        macd_signal_current = data['macd_signal'].iloc[-1]
        
        # Check for EMA crossover
        bullish_cross = (ema9_prev <= ema15_prev) and (ema9_current > ema15_current)
        bearish_cross = (ema9_prev >= ema15_prev) and (ema9_current < ema15_current)
        
        # Volume confirmation
        volume_confirmed = self.check_volume_increase(data)
        
        # Support/Resistance check
        support, resistance = self.find_support_resistance(data)
        near_key_level = self.is_near_support_resistance(current_price, support, resistance)
        
        # BUY Signal Logic
        if bullish_cross:
            # Confirmations
            rsi_ok = rsi_current < 70  # Not overbought
            macd_ok = macd_current > macd_signal_current  # MACD bullish
            price_above_ema = current_price > ema9_current
            
            if volume_confirmed and rsi_ok and macd_ok and price_above_ema and near_key_level:
                return 'BUY'
        
        # SELL Signal Logic
        elif bearish_cross:
            # Confirmations
            rsi_ok = rsi_current > 30  # Not oversold
            macd_ok = macd_current < macd_signal_current  # MACD bearish
            price_below_ema = current_price < ema9_current
            
            if volume_confirmed and rsi_ok and macd_ok and price_below_ema and near_key_level:
                return 'SELL'
        
        return None
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk management
        
        Risk = 2% of capital per trade
        Position Size = (Capital * Risk%) / (Entry - Stop Loss)
        """
        risk_amount = self.capital * self.risk_per_trade
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return 0
        
        quantity = int(risk_amount / risk_per_share)
        
        # Ensure we can afford it
        max_quantity = int(self.capital / entry_price)
        quantity = min(quantity, max_quantity)
        
        return quantity
    
    def calculate_stop_loss_target(self, data, signal_type):
        """
        Calculate stop loss and target based on recent swing points
        
        Stop Loss: Recent swing low (for BUY) or swing high (for SELL)
        Target: 2x risk (Risk-Reward = 1:2)
        """
        current_price = data['close'].iloc[-1]
        
        if signal_type == 'BUY':
            # Stop loss at recent swing low
            swing_low = data['low'].iloc[-10:].min()
            stop_loss = swing_low * 0.998  # Slightly below swing low
            risk = current_price - stop_loss
            target = current_price + (risk * 2)  # 1:2 RR
            
        elif signal_type == 'SELL':
            # Stop loss at recent swing high
            swing_high = data['high'].iloc[-10:].max()
            stop_loss = swing_high * 1.002  # Slightly above swing high
            risk = stop_loss - current_price
            target = current_price - (risk * 2)  # 1:2 RR
        
        else:
            return None, None
        
        return stop_loss, target
    
    def check_exit_conditions(self, data):
        """
        Check if we should exit current position
        
        Exit conditions:
        1. Stop loss hit
        2. Target hit
        3. EMA crossover in opposite direction
        """
        if self.position is None:
            return False
        
        current_price = data['close'].iloc[-1]
        
        # Check stop loss and target
        if self.position == 'LONG':
            if current_price <= self.stop_loss:
                print(f"Stop Loss Hit! Exit LONG at {current_price}")
                return True
            if current_price >= self.target:
                print(f"Target Hit! Exit LONG at {current_price}")
                return True
        
        elif self.position == 'SHORT':
            if current_price >= self.stop_loss:
                print(f"Stop Loss Hit! Exit SHORT at {current_price}")
                return True
            if current_price <= self.target:
                print(f"Target Hit! Exit SHORT at {current_price}")
                return True
        
        # Check for opposite EMA crossover
        data['ema9'] = self.calculate_ema(data, 9)
        data['ema15'] = self.calculate_ema(data, 15)
        
        ema9_current = data['ema9'].iloc[-1]
        ema15_current = data['ema15'].iloc[-1]
        ema9_prev = data['ema9'].iloc[-2]
        ema15_prev = data['ema15'].iloc[-2]
        
        if self.position == 'LONG':
            bearish_cross = (ema9_prev >= ema15_prev) and (ema9_current < ema15_current)
            if bearish_cross:
                print(f"EMA Crossover Exit! Exit LONG at {current_price}")
                return True
        
        elif self.position == 'SHORT':
            bullish_cross = (ema9_prev <= ema15_prev) and (ema9_current > ema15_current)
            if bullish_cross:
                print(f"EMA Crossover Exit! Exit SHORT at {current_price}")
                return True
        
        return False
    
    def execute_trade(self, signal, data):
        """
        Execute the trade (placeholder - integrate with broker API)
        """
        current_price = data['close'].iloc[-1]
        timestamp = data['timestamp'].iloc[-1] if 'timestamp' in data.columns else datetime.now()
        
        if signal == 'BUY':
            stop_loss, target = self.calculate_stop_loss_target(data, 'BUY')
            quantity = self.calculate_position_size(current_price, stop_loss)
            
            if quantity > 0:
                self.position = 'LONG'
                self.entry_price = current_price
                self.stop_loss = stop_loss
                self.target = target
                
                print(f"\n{'='*60}")
                print(f"BUY SIGNAL EXECUTED")
                print(f"Time: {timestamp}")
                print(f"Entry Price: ₹{current_price:.2f}")
                print(f"Quantity: {quantity}")
                print(f"Stop Loss: ₹{stop_loss:.2f} (-{((current_price-stop_loss)/current_price*100):.2f}%)")
                print(f"Target: ₹{target:.2f} (+{((target-current_price)/current_price*100):.2f}%)")
                print(f"Risk Amount: ₹{abs(current_price - stop_loss) * quantity:.2f}")
                print(f"{'='*60}\n")
        
        elif signal == 'SELL':
            stop_loss, target = self.calculate_stop_loss_target(data, 'SELL')
            quantity = self.calculate_position_size(current_price, stop_loss)
            
            if quantity > 0:
                self.position = 'SHORT'
                self.entry_price = current_price
                self.stop_loss = stop_loss
                self.target = target
                
                print(f"\n{'='*60}")
                print(f"SELL SIGNAL EXECUTED")
                print(f"Time: {timestamp}")
                print(f"Entry Price: ₹{current_price:.2f}")
                print(f"Quantity: {quantity}")
                print(f"Stop Loss: ₹{stop_loss:.2f} (+{((stop_loss-current_price)/current_price*100):.2f}%)")
                print(f"Target: ₹{target:.2f} (-{((current_price-target)/current_price*100):.2f}%)")
                print(f"Risk Amount: ₹{abs(stop_loss - current_price) * quantity:.2f}")
                print(f"{'='*60}\n")
    
    def exit_trade(self, data):
        """
        Exit current position
        """
        current_price = data['close'].iloc[-1]
        timestamp = data['timestamp'].iloc[-1] if 'timestamp' in data.columns else datetime.now()
        
        if self.position:
            pnl = 0
            if self.position == 'LONG':
                pnl = (current_price - self.entry_price)
            elif self.position == 'SHORT':
                pnl = (self.entry_price - current_price)
            
            pnl_pct = (pnl / self.entry_price) * 100
            
            print(f"\n{'='*60}")
            print(f"POSITION CLOSED: {self.position}")
            print(f"Time: {timestamp}")
            print(f"Entry: ₹{self.entry_price:.2f} | Exit: ₹{current_price:.2f}")
            print(f"P&L: ₹{pnl:.2f} ({pnl_pct:+.2f}%)")
            print(f"{'='*60}\n")
            
            self.position = None
            self.entry_price = 0
            self.stop_loss = 0
            self.target = 0


# ==========================================
# Example: Backtesting with historical data
# ==========================================

def backtest_strategy(data):
    """
    Backtest the strategy on historical data
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Historical OHLCV data with columns: timestamp, open, high, low, close, volume
    """
    strategy = EMAStrategy(capital=10000, risk_per_trade=0.02)
    
    print("Starting Backtest...")
    print(f"Initial Capital: ₹{strategy.capital}")
    print(f"Risk per Trade: {strategy.risk_per_trade*100}%")
    print("="*60)
    
    for i in range(30, len(data)):
        current_data = data.iloc[:i+1].copy()
        
        # Check exit conditions first
        if strategy.position:
            if strategy.check_exit_conditions(current_data):
                strategy.exit_trade(current_data)
        
        # Generate new signals if no position
        if strategy.position is None:
            signal = strategy.generate_signal(current_data)
            if signal:
                strategy.execute_trade(signal, current_data)
    
    print("Backtest Complete!")


# ==========================================
# Live Trading Setup (Template)
# ==========================================

def setup_angel_one_api():
    """
    Setup Angel One API connection
    """
    # Your Angel One credentials
    api_key = "YOUR_API_KEY"
    client_code = "YOUR_CLIENT_CODE"
    password = "YOUR_PASSWORD"
    totp_secret = "YOUR_TOTP_SECRET"  # For 2FA
    
    # Initialize SmartConnect
    smart_api = SmartConnect(api_key=api_key)
    
    # Generate session
    # data = smart_api.generateSession(client_code, password, totp_secret)
    
    return smart_api


def fetch_live_data(smart_api, symbol, exchange, interval='FIVE_MINUTE'):
    """
    Fetch live 5-minute candle data from Angel One
    
    Parameters:
    -----------
    symbol : str
        Trading symbol (e.g., 'SBIN', 'RELIANCE')
    exchange : str
        Exchange (e.g., 'NSE', 'BSE')
    interval : str
        Timeframe ('ONE_MINUTE', 'FIVE_MINUTE', etc.)
    """
    # Implement live data fetching
    # historical_data = smart_api.getCandleData(...)
    pass


def run_live_trading(symbol='SBIN', exchange='NSE'):
    """
    Run the strategy in live trading mode
    
    WARNING: Test thoroughly in paper trading first!
    """
    # Initialize strategy
    strategy = EMAStrategy(capital=10000, risk_per_trade=0.02)
    
    # Setup API
    # smart_api = setup_angel_one_api()
    
    print(f"Starting Live Trading for {symbol}")
    print("Press Ctrl+C to stop")
    
    while True:
        try:
            # Fetch latest data
            # data = fetch_live_data(smart_api, symbol, exchange)
            
            # Check exit conditions
            # if strategy.position:
            #     if strategy.check_exit_conditions(data):
            #         strategy.exit_trade(data)
            #         # Place exit order via API
            
            # Generate signals
            # if strategy.position is None:
            #     signal = strategy.generate_signal(data)
            #     if signal:
            #         strategy.execute_trade(signal, data)
            #         # Place order via API
            
            # Wait for next candle
            time.sleep(300)  # 5 minutes
            
        except KeyboardInterrupt:
            print("\nStopping live trading...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    print("9-15 EMA Algo Trading Strategy")
    print("="*60)
    print("\nTo use this script:")
    print("1. Install required packages:")
    print("   pip install pandas numpy smartapi-python")
    print("\n2. For backtesting, prepare historical data in CSV format")
    print("   Required columns: timestamp, open, high, low, close, volume")
    print("\n3. For live trading:")
    print("   - Get Angel One API credentials")
    print("   - Update credentials in setup_angel_one_api()")
    print("   - Test in paper trading first!")
    print("="*60)
    
    # Example: Load and backtest
    # data = pd.read_csv('historical_data.csv')
    # backtest_strategy(data)
    
    # Example: Run live trading (after proper setup)
    # run_live_trading(symbol='SBIN', exchange='NSE')
