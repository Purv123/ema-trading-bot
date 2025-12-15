"""
Mudrex Crypto Trading Integration
Support for Bitcoin, Ethereum, and other cryptocurrencies
"""

import requests
import hmac
import hashlib
import time
import json
from datetime import datetime, timedelta
import pandas as pd
from ema_algo_trading import EMAStrategy


class MudrexTrading:
    def __init__(self, api_key, api_secret):
        """
        Initialize Mudrex API connection
        
        Parameters:
        -----------
        api_key : str
            Your Mudrex API key
        api_secret : str
            Your Mudrex API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.mudrex.com/v1"
        
    def _generate_signature(self, timestamp, method, endpoint, body=''):
        """
        Generate HMAC signature for authenticated requests
        """
        message = f"{timestamp}{method}{endpoint}{body}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method, endpoint, params=None, body=None):
        """
        Make authenticated API request to Mudrex
        """
        timestamp = str(int(time.time() * 1000))
        url = f"{self.base_url}{endpoint}"
        
        # Prepare body
        body_str = ''
        if body:
            body_str = json.dumps(body)
        
        # Generate signature
        signature = self._generate_signature(timestamp, method, endpoint, body_str)
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key,
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': signature
        }
        
        # Make request
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=body)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"✗ API Request Error: {str(e)}")
            return None
    
    def get_account_balance(self):
        """
        Get account balance
        """
        endpoint = '/account/balance'
        response = self._make_request('GET', endpoint)
        
        if response:
            print("✓ Account Balance:")
            for currency in response.get('balances', []):
                if float(currency.get('available', 0)) > 0:
                    print(f"  {currency['currency']}: {currency['available']}")
            return response
        return None
    
    def get_markets(self):
        """
        Get available trading pairs
        """
        endpoint = '/markets'
        response = self._make_request('GET', endpoint)
        
        if response:
            print(f"✓ Available Markets: {len(response.get('markets', []))}")
            return response.get('markets', [])
        return []
    
    def fetch_historical_data(self, symbol, interval='5m', limit=500):
        """
        Fetch historical OHLCV data
        
        Parameters:
        -----------
        symbol : str
            Trading pair (e.g., 'BTC/USDT', 'ETH/USDT')
        interval : str
            Timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
        limit : int
            Number of candles to fetch (max 1000)
        
        Returns:
        --------
        pandas.DataFrame with columns: timestamp, open, high, low, close, volume
        """
        endpoint = f'/candles/{symbol}'
        params = {
            'interval': interval,
            'limit': limit
        }
        
        response = self._make_request('GET', endpoint, params=params)
        
        if response and 'candles' in response:
            # Convert to DataFrame
            candles = response['candles']
            df = pd.DataFrame(candles)
            
            # Rename columns
            df = df.rename(columns={
                'time': 'timestamp',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert to numeric
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            print(f"✓ Fetched {len(df)} candles for {symbol}")
            return df
        
        print(f"✗ Failed to fetch data for {symbol}")
        return None
    
    def get_ticker(self, symbol):
        """
        Get current price and 24h stats
        """
        endpoint = f'/ticker/{symbol}'
        response = self._make_request('GET', endpoint)
        
        if response:
            return {
                'last': float(response.get('last', 0)),
                'bid': float(response.get('bid', 0)),
                'ask': float(response.get('ask', 0)),
                'volume': float(response.get('volume', 0)),
                'high': float(response.get('high', 0)),
                'low': float(response.get('low', 0)),
            }
        return None
    
    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        """
        Place an order
        
        Parameters:
        -----------
        symbol : str
            Trading pair (e.g., 'BTC/USDT')
        side : str
            'buy' or 'sell'
        order_type : str
            'market', 'limit', 'stop_limit'
        quantity : float
            Order quantity
        price : float
            Limit price (for limit/stop_limit orders)
        stop_price : float
            Stop price (for stop_limit orders)
        
        Returns:
        --------
        Order ID if successful
        """
        endpoint = '/orders'
        
        body = {
            'symbol': symbol,
            'side': side.lower(),
            'type': order_type.lower(),
            'quantity': str(quantity)
        }
        
        if price:
            body['price'] = str(price)
        
        if stop_price:
            body['stopPrice'] = str(stop_price)
        
        response = self._make_request('POST', endpoint, body=body)
        
        if response and 'orderId' in response:
            order_id = response['orderId']
            print(f"✓ Order placed: {side.upper()} {quantity} {symbol}")
            print(f"  Order ID: {order_id}")
            return order_id
        else:
            print(f"✗ Order failed: {response.get('message', 'Unknown error')}")
            return None
    
    def cancel_order(self, order_id, symbol):
        """
        Cancel an open order
        """
        endpoint = f'/orders/{order_id}'
        body = {'symbol': symbol}
        
        response = self._make_request('DELETE', endpoint, body=body)
        
        if response:
            print(f"✓ Order {order_id} cancelled")
            return True
        else:
            print(f"✗ Failed to cancel order {order_id}")
            return False
    
    def get_open_orders(self, symbol=None):
        """
        Get all open orders
        """
        endpoint = '/orders/open'
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        response = self._make_request('GET', endpoint, params=params)
        
        if response:
            return response.get('orders', [])
        return []
    
    def get_order_status(self, order_id, symbol):
        """
        Get order status
        """
        endpoint = f'/orders/{order_id}'
        params = {'symbol': symbol}
        
        response = self._make_request('GET', endpoint, params=params)
        return response
    
    def get_positions(self):
        """
        Get current open positions
        """
        endpoint = '/positions'
        response = self._make_request('GET', endpoint)
        
        if response:
            return response.get('positions', [])
        return []


# ==========================================
# Crypto Trading Bot Implementation
# ==========================================

def run_crypto_trading(api_key, api_secret, symbol='BTC/USDT', 
                       capital=10000, risk_per_trade=0.02):
    """
    Run live crypto trading with Mudrex
    
    Parameters:
    -----------
    api_key : str
        Mudrex API key
    api_secret : str
        Mudrex API secret
    symbol : str
        Crypto pair to trade (e.g., 'BTC/USDT', 'ETH/USDT')
    capital : float
        Trading capital in USDT
    risk_per_trade : float
        Risk percentage per trade
    """
    
    # Initialize Mudrex connection
    mudrex = MudrexTrading(api_key, api_secret)
    
    # Get account balance
    balance = mudrex.get_account_balance()
    if not balance:
        print("Failed to connect to Mudrex. Check credentials.")
        return
    
    # Initialize strategy
    strategy = EMAStrategy(capital=capital, risk_per_trade=risk_per_trade)
    
    print(f"\n{'='*60}")
    print(f"Starting Crypto Trading Bot")
    print(f"Symbol: {symbol}")
    print(f"Capital: ${capital} USDT")
    print(f"Risk per Trade: {risk_per_trade*100}%")
    print(f"{'='*60}\n")
    
    # Track orders
    entry_order_id = None
    sl_order_id = None
    target_order_id = None
    
    try:
        while True:
            # Fetch latest 5-minute candles
            data = mudrex.fetch_historical_data(
                symbol=symbol,
                interval='5m',
                limit=200
            )
            
            if data is None or len(data) < 30:
                print("Insufficient data. Waiting...")
                time.sleep(60)
                continue
            
            # Check exit conditions
            if strategy.position:
                should_exit = strategy.check_exit_conditions(data)
                
                if should_exit:
                    current_price = data['close'].iloc[-1]
                    quantity = strategy.calculate_position_size(
                        strategy.entry_price,
                        strategy.stop_loss
                    ) / strategy.entry_price  # Convert to crypto quantity
                    
                    # Place exit order
                    if strategy.position == 'LONG':
                        order_id = mudrex.place_order(
                            symbol=symbol,
                            side='sell',
                            order_type='market',
                            quantity=quantity
                        )
                    elif strategy.position == 'SHORT':
                        order_id = mudrex.place_order(
                            symbol=symbol,
                            side='buy',
                            order_type='market',
                            quantity=quantity
                        )
                    
                    if order_id:
                        # Cancel SL and target orders
                        if sl_order_id:
                            mudrex.cancel_order(sl_order_id, symbol)
                        if target_order_id:
                            mudrex.cancel_order(target_order_id, symbol)
                        
                        strategy.exit_trade(data)
                        
                        # Reset
                        entry_order_id = None
                        sl_order_id = None
                        target_order_id = None
            
            # Generate new signals
            if strategy.position is None:
                signal = strategy.generate_signal(data)
                
                if signal:
                    current_price = data['close'].iloc[-1]
                    stop_loss, target = strategy.calculate_stop_loss_target(data, signal)
                    
                    # Calculate quantity in crypto
                    risk_amount = capital * risk_per_trade
                    risk_per_unit = abs(current_price - stop_loss)
                    quantity = risk_amount / risk_per_unit / current_price
                    
                    # Minimum order size check
                    min_quantity = 0.001  # Adjust based on exchange
                    if quantity < min_quantity:
                        print(f"Quantity too small: {quantity}. Skipping...")
                        time.sleep(300)
                        continue
                    
                    if signal == 'BUY':
                        # Place market buy order
                        entry_order_id = mudrex.place_order(
                            symbol=symbol,
                            side='buy',
                            order_type='market',
                            quantity=quantity
                        )
                        
                        if entry_order_id:
                            # Place stop-loss order
                            sl_order_id = mudrex.place_order(
                                symbol=symbol,
                                side='sell',
                                order_type='stop_limit',
                                quantity=quantity,
                                price=stop_loss,
                                stop_price=stop_loss
                            )
                            
                            # Place target order
                            target_order_id = mudrex.place_order(
                                symbol=symbol,
                                side='sell',
                                order_type='limit',
                                quantity=quantity,
                                price=target
                            )
                            
                            strategy.execute_trade(signal, data)
                    
                    elif signal == 'SELL':
                        # For crypto, we need to check if shorting is available
                        # Most exchanges don't support spot shorting
                        print("SHORT signal detected - Skipping (spot markets don't support shorting)")
                        print("Consider using futures if you want to short crypto")
            
            # Wait for next candle (5 minutes)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring {symbol}...")
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n\nStopping crypto trading...")
        
        # Close positions if any
        if strategy.position:
            print("Closing open positions...")
            # Add closing logic
    
    except Exception as e:
        print(f"\n✗ Error in crypto trading: {str(e)}")
        import traceback
        traceback.print_exc()


# ==========================================
# Crypto-Specific Features
# ==========================================

def get_top_crypto_pairs(mudrex):
    """
    Get top trading pairs by volume
    """
    markets = mudrex.get_markets()
    
    # Filter USDT pairs and sort by volume
    usdt_pairs = [m for m in markets if m['quote'] == 'USDT']
    usdt_pairs.sort(key=lambda x: float(x.get('volume', 0)), reverse=True)
    
    print("\nTop 10 Crypto Pairs by Volume:")
    print("-" * 60)
    for i, pair in enumerate(usdt_pairs[:10], 1):
        symbol = f"{pair['base']}/{pair['quote']}"
        volume = float(pair.get('volume', 0))
        price = float(pair.get('last', 0))
        print(f"{i}. {symbol:15} | Price: ${price:>12,.2f} | Volume: ${volume:>15,.0f}")
    
    return usdt_pairs


def scan_crypto_signals(mudrex, pairs=['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']):
    """
    Scan multiple crypto pairs for trading signals
    """
    strategy = EMAStrategy(capital=10000)
    signals_found = []
    
    print(f"\nScanning {len(pairs)} crypto pairs for signals...")
    print("=" * 60)
    
    for symbol in pairs:
        try:
            # Fetch data
            data = mudrex.fetch_historical_data(symbol, interval='5m', limit=100)
            
            if data is None or len(data) < 30:
                continue
            
            # Check for signal
            signal = strategy.generate_signal(data)
            
            if signal:
                current_price = data['close'].iloc[-1]
                ticker = mudrex.get_ticker(symbol)
                
                signals_found.append({
                    'symbol': symbol,
                    'signal': signal,
                    'price': current_price,
                    'volume_24h': ticker['volume'] if ticker else 0
                })
                
                print(f"\n🎯 {signal} SIGNAL: {symbol}")
                print(f"   Price: ${current_price:,.2f}")
                print(f"   24h Volume: ${ticker['volume']:,.0f}" if ticker else "")
        
        except Exception as e:
            print(f"Error scanning {symbol}: {str(e)}")
            continue
        
        time.sleep(1)  # Rate limiting
    
    if not signals_found:
        print("\n❌ No signals found at this time")
    else:
        print(f"\n✓ Found {len(signals_found)} trading signals")
    
    return signals_found


if __name__ == "__main__":
    print("Mudrex Crypto Trading Bot")
    print("=" * 60)
    print("\nFeatures:")
    print("- Trade BTC, ETH, and 100+ cryptocurrencies")
    print("- 24/7 trading (crypto markets never close)")
    print("- Same 9-15 EMA strategy with confirmations")
    print("- Support for 1m, 5m, 15m, 1h, 4h, 1d timeframes")
    print("\nRecommended pairs: BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT")
    print("=" * 60)
    
    # Example usage:
    # API_KEY = "your_mudrex_api_key"
    # API_SECRET = "your_mudrex_api_secret"
    # 
    # run_crypto_trading(
    #     api_key=API_KEY,
    #     api_secret=API_SECRET,
    #     symbol='BTC/USDT',
    #     capital=10000,
    #     risk_per_trade=0.02
    # )
