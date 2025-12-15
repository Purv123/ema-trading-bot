"""
Angel One API Integration for 9-15 EMA Strategy
Complete implementation with live data fetching and order placement
"""

from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from ema_algo_trading import EMAStrategy


class AngelOneTrading:
    def __init__(self, api_key, client_code, password, totp_secret):
        """
        Initialize Angel One trading connection
        
        Parameters:
        -----------
        api_key : str
            Your Angel One API key
        client_code : str
            Your Angel One client code
        password : str
            Your Angel One password
        totp_secret : str
            Your TOTP secret for 2FA
        """
        self.api_key = api_key
        self.client_code = client_code
        self.password = password
        self.totp_secret = totp_secret
        self.smart_api = None
        self.auth_token = None
        self.feed_token = None
        self.websocket = None
        
    def login(self):
        """
        Login to Angel One and generate session
        """
        try:
            # Initialize SmartConnect
            self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Generate TOTP
            totp = pyotp.TOTP(self.totp_secret)
            totp_code = totp.now()
            
            # Generate session
            data = self.smart_api.generateSession(
                self.client_code,
                self.password,
                totp_code
            )
            
            if data['status']:
                self.auth_token = data['data']['jwtToken']
                self.feed_token = data['data']['feedToken']
                print("✓ Successfully logged in to Angel One")
                print(f"Session valid until: {data['data'].get('sessionExpiry', 'N/A')}")
                return True
            else:
                print(f"✗ Login failed: {data['message']}")
                return False
                
        except Exception as e:
            print(f"✗ Login error: {str(e)}")
            return False
    
    def get_symbol_token(self, symbol, exchange='NSE'):
        """
        Get token for a symbol (required for API calls)
        
        You'll need to download the symbol master from Angel One
        or use their search API
        """
        # Common symbols (add more as needed)
        symbol_tokens = {
            'NSE': {
                'SBIN': '3045',
                'RELIANCE': '2885',
                'TCS': '11536',
                'INFY': '1594',
                'HDFCBANK': '1333',
                'ICICIBANK': '4963',
                'WIPRO': '3787',
                'LT': '11483',
            }
        }
        
        return symbol_tokens.get(exchange, {}).get(symbol, None)
    
    def fetch_historical_data(self, symbol, exchange='NSE', interval='FIVE_MINUTE', 
                             from_date=None, to_date=None):
        """
        Fetch historical candle data
        
        Parameters:
        -----------
        symbol : str
            Trading symbol (e.g., 'SBIN')
        exchange : str
            Exchange ('NSE', 'BSE')
        interval : str
            'ONE_MINUTE', 'FIVE_MINUTE', 'FIFTEEN_MINUTE', 'ONE_HOUR', 'ONE_DAY'
        from_date : datetime
            Start date
        to_date : datetime
            End date
        
        Returns:
        --------
        pandas.DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Get symbol token
            token = self.get_symbol_token(symbol, exchange)
            if not token:
                print(f"✗ Token not found for {symbol}")
                return None
            
            # Default date range: last 7 days
            if not to_date:
                to_date = datetime.now()
            if not from_date:
                from_date = to_date - timedelta(days=7)
            
            # Format dates
            from_date_str = from_date.strftime("%Y-%m-%d %H:%M")
            to_date_str = to_date.strftime("%Y-%m-%d %H:%M")
            
            # Fetch data
            params = {
                "exchange": exchange,
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_date_str,
                "todate": to_date_str
            }
            
            historical_data = self.smart_api.getCandleData(params)
            
            if historical_data['status']:
                # Convert to DataFrame
                data = historical_data['data']
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # Convert timestamp
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Convert to numeric
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col])
                
                print(f"✓ Fetched {len(df)} candles for {symbol}")
                return df
            else:
                print(f"✗ Failed to fetch data: {historical_data['message']}")
                return None
                
        except Exception as e:
            print(f"✗ Error fetching data: {str(e)}")
            return None
    
    def get_live_price(self, symbol, exchange='NSE'):
        """
        Get current market price (LTP)
        """
        try:
            token = self.get_symbol_token(symbol, exchange)
            if not token:
                return None
            
            params = {
                "mode": "LTP",
                "exchangeTokens": {
                    exchange: [token]
                }
            }
            
            quote = self.smart_api.getMarketData(params)
            
            if quote['status'] and quote['data']:
                ltp = quote['data']['fetched'][0]['ltp']
                return float(ltp)
            else:
                return None
                
        except Exception as e:
            print(f"✗ Error fetching live price: {str(e)}")
            return None
    
    def place_order(self, symbol, exchange, quantity, order_type='BUY', 
                    order_variety='NORMAL', price=None, trigger_price=None):
        """
        Place an order
        
        Parameters:
        -----------
        symbol : str
            Trading symbol
        exchange : str
            'NSE' or 'BSE'
        quantity : int
            Number of shares
        order_type : str
            'BUY' or 'SELL'
        order_variety : str
            'NORMAL', 'STOPLOSS', 'AMO'
        price : float
            Limit price (None for market order)
        trigger_price : float
            Trigger price for stop-loss orders
        
        Returns:
        --------
        Order ID if successful, None otherwise
        """
        try:
            token = self.get_symbol_token(symbol, exchange)
            if not token:
                return None
            
            # Build order params
            order_params = {
                "variety": order_variety,
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": order_type,
                "exchange": exchange,
                "ordertype": "MARKET" if not price else "LIMIT",
                "producttype": "INTRADAY",  # Change to 'DELIVERY' for positional
                "duration": "DAY",
                "quantity": str(quantity)
            }
            
            if price:
                order_params["price"] = str(price)
            
            if trigger_price:
                order_params["triggerprice"] = str(trigger_price)
                order_params["ordertype"] = "STOPLOSS_LIMIT"
            
            # Place order
            order_response = self.smart_api.placeOrder(order_params)
            
            if order_response['status']:
                order_id = order_response['data']['orderid']
                print(f"✓ Order placed successfully: {order_type} {quantity} {symbol}")
                print(f"  Order ID: {order_id}")
                return order_id
            else:
                print(f"✗ Order failed: {order_response['message']}")
                return None
                
        except Exception as e:
            print(f"✗ Error placing order: {str(e)}")
            return None
    
    def place_stop_loss_order(self, symbol, exchange, quantity, order_type, 
                             stop_price, limit_price=None):
        """
        Place a stop-loss order
        
        Parameters:
        -----------
        stop_price : float
            Trigger price
        limit_price : float
            Limit price (if None, uses stop_price)
        """
        if not limit_price:
            limit_price = stop_price
        
        return self.place_order(
            symbol=symbol,
            exchange=exchange,
            quantity=quantity,
            order_type=order_type,
            order_variety='STOPLOSS',
            price=limit_price,
            trigger_price=stop_price
        )
    
    def cancel_order(self, order_id, variety='NORMAL'):
        """
        Cancel an existing order
        """
        try:
            cancel_response = self.smart_api.cancelOrder(order_id, variety)
            
            if cancel_response['status']:
                print(f"✓ Order {order_id} cancelled successfully")
                return True
            else:
                print(f"✗ Cancel failed: {cancel_response['message']}")
                return False
                
        except Exception as e:
            print(f"✗ Error cancelling order: {str(e)}")
            return False
    
    def get_positions(self):
        """
        Get current open positions
        """
        try:
            positions = self.smart_api.position()
            
            if positions['status']:
                return positions['data']
            else:
                return []
                
        except Exception as e:
            print(f"✗ Error fetching positions: {str(e)}")
            return []
    
    def get_order_book(self):
        """
        Get order book
        """
        try:
            orders = self.smart_api.orderBook()
            
            if orders['status']:
                return orders['data']
            else:
                return []
                
        except Exception as e:
            print(f"✗ Error fetching orders: {str(e)}")
            return []
    
    def logout(self):
        """
        Logout from Angel One
        """
        try:
            if self.smart_api:
                self.smart_api.terminateSession(self.client_code)
                print("✓ Logged out successfully")
        except Exception as e:
            print(f"✗ Logout error: {str(e)}")


# ==========================================
# Live Trading Implementation
# ==========================================

def run_live_trading_angel_one(api_key, client_code, password, totp_secret,
                               symbol='SBIN', exchange='NSE', capital=10000):
    """
    Run live trading with Angel One
    
    Parameters:
    -----------
    api_key : str
        Your Angel One API key
    client_code : str
        Your Angel One client code
    password : str
        Your Angel One password
    totp_secret : str
        Your TOTP secret
    symbol : str
        Stock symbol to trade
    exchange : str
        Exchange ('NSE' or 'BSE')
    capital : float
        Trading capital
    """
    
    # Initialize Angel One connection
    angel = AngelOneTrading(api_key, client_code, password, totp_secret)
    
    # Login
    if not angel.login():
        print("Failed to login. Exiting...")
        return
    
    # Initialize strategy
    strategy = EMAStrategy(capital=capital, risk_per_trade=0.02)
    
    print(f"\n{'='*60}")
    print(f"Starting Live Trading")
    print(f"Symbol: {symbol} | Exchange: {exchange}")
    print(f"Capital: ₹{capital}")
    print(f"Risk per Trade: {strategy.risk_per_trade*100}%")
    print(f"{'='*60}\n")
    
    # Track orders
    entry_order_id = None
    sl_order_id = None
    target_order_id = None
    
    try:
        while True:
            current_time = datetime.now()
            
            # Check if market is open (9:15 AM to 3:30 PM)
            if current_time.hour < 9 or (current_time.hour == 9 and current_time.minute < 15):
                print("Market not open yet. Waiting...")
                time.sleep(60)
                continue
            
            if current_time.hour >= 15 and current_time.minute >= 30:
                print("Market closed. Stopping for today...")
                break
            
            # Avoid choppy mid-day period
            if 11 <= current_time.hour < 14:
                print("Mid-day period - low volume. Skipping...")
                time.sleep(300)
                continue
            
            # Fetch latest data
            to_date = datetime.now()
            from_date = to_date - timedelta(days=2)
            
            data = angel.fetch_historical_data(
                symbol=symbol,
                exchange=exchange,
                interval='FIVE_MINUTE',
                from_date=from_date,
                to_date=to_date
            )
            
            if data is None or len(data) < 30:
                print("Insufficient data. Waiting...")
                time.sleep(300)
                continue
            
            # Check exit conditions first
            if strategy.position:
                should_exit = strategy.check_exit_conditions(data)
                
                if should_exit:
                    # Exit position
                    current_price = data['close'].iloc[-1]
                    quantity = strategy.calculate_position_size(strategy.entry_price, strategy.stop_loss)
                    
                    if strategy.position == 'LONG':
                        order_id = angel.place_order(
                            symbol=symbol,
                            exchange=exchange,
                            quantity=quantity,
                            order_type='SELL'
                        )
                    elif strategy.position == 'SHORT':
                        order_id = angel.place_order(
                            symbol=symbol,
                            exchange=exchange,
                            quantity=quantity,
                            order_type='BUY'
                        )
                    
                    if order_id:
                        # Cancel pending SL and target orders
                        if sl_order_id:
                            angel.cancel_order(sl_order_id, 'STOPLOSS')
                        if target_order_id:
                            angel.cancel_order(target_order_id, 'LIMIT')
                        
                        strategy.exit_trade(data)
                        
                        # Reset order IDs
                        entry_order_id = None
                        sl_order_id = None
                        target_order_id = None
            
            # Generate signals if no position
            if strategy.position is None:
                signal = strategy.generate_signal(data)
                
                if signal:
                    current_price = data['close'].iloc[-1]
                    stop_loss, target = strategy.calculate_stop_loss_target(data, signal)
                    quantity = strategy.calculate_position_size(current_price, stop_loss)
                    
                    if quantity > 0:
                        # Place entry order
                        if signal == 'BUY':
                            entry_order_id = angel.place_order(
                                symbol=symbol,
                                exchange=exchange,
                                quantity=quantity,
                                order_type='BUY'
                            )
                            
                            if entry_order_id:
                                # Place stop-loss order
                                sl_order_id = angel.place_stop_loss_order(
                                    symbol=symbol,
                                    exchange=exchange,
                                    quantity=quantity,
                                    order_type='SELL',
                                    stop_price=stop_loss
                                )
                                
                                # Place target order
                                target_order_id = angel.place_order(
                                    symbol=symbol,
                                    exchange=exchange,
                                    quantity=quantity,
                                    order_type='SELL',
                                    price=target
                                )
                                
                                strategy.execute_trade(signal, data)
                        
                        elif signal == 'SELL':
                            entry_order_id = angel.place_order(
                                symbol=symbol,
                                exchange=exchange,
                                quantity=quantity,
                                order_type='SELL'
                            )
                            
                            if entry_order_id:
                                # Place stop-loss order
                                sl_order_id = angel.place_stop_loss_order(
                                    symbol=symbol,
                                    exchange=exchange,
                                    quantity=quantity,
                                    order_type='BUY',
                                    stop_price=stop_loss
                                )
                                
                                # Place target order
                                target_order_id = angel.place_order(
                                    symbol=symbol,
                                    exchange=exchange,
                                    quantity=quantity,
                                    order_type='BUY',
                                    price=target
                                )
                                
                                strategy.execute_trade(signal, data)
            
            # Wait for next candle (5 minutes)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for next candle...")
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n\nStopping live trading...")
        
        # Close any open positions
        if strategy.position:
            print("Closing open position...")
            positions = angel.get_positions()
            # Add position closing logic here
    
    except Exception as e:
        print(f"\n✗ Error in live trading: {str(e)}")
    
    finally:
        # Logout
        angel.logout()
        print("Trading session ended.")


if __name__ == "__main__":
    # ==========================================
    # CONFIGURATION - UPDATE THESE VALUES
    # ==========================================
    
    API_KEY = "YOUR_ANGEL_ONE_API_KEY"
    CLIENT_CODE = "YOUR_CLIENT_CODE"
    PASSWORD = "YOUR_PASSWORD"
    TOTP_SECRET = "YOUR_TOTP_SECRET"
    
    SYMBOL = "SBIN"  # Stock to trade
    EXCHANGE = "NSE"
    CAPITAL = 10000  # Trading capital in INR
    
    # ==========================================
    # RUN LIVE TRADING
    # ==========================================
    
    # WARNING: Test in paper trading first!
    # Uncomment the line below to start live trading
    
    # run_live_trading_angel_one(
    #     api_key=API_KEY,
    #     client_code=CLIENT_CODE,
    #     password=PASSWORD,
    #     totp_secret=TOTP_SECRET,
    #     symbol=SYMBOL,
    #     exchange=EXCHANGE,
    #     capital=CAPITAL
    # )
    
    print("Please update your API credentials before running.")
    print("Make sure to test in paper trading first!")
