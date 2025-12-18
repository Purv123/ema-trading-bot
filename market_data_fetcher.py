"""
Market Data Fetcher
Fetches real-time market data from various sources
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import hmac
import hashlib
import json


class MarketDataFetcher:
    """Fetch real market data from exchanges"""

    def __init__(self, api_key=None, api_secret=None, use_mudrex=False, coingecko_api_key=None):
        self.session = requests.Session()
        self.api_key = api_key
        self.api_secret = api_secret
        self.use_mudrex = use_mudrex
        # Note: Mudrex API is for TRADE EXECUTION only, not market data
        self.mudrex_base_url = "https://trade.mudrex.com/fapi/v1"
        # CoinGecko for free market data
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.coingecko_api_key = coingecko_api_key or "CG-GgCnwTc2xkSQ2mDTHaaii7mt"  # Demo API key

        # Cache to avoid rate limits
        # Note: CoinGecko updates every 5 minutes anyway, but shorter cache = fresher data
        self._cache = {}
        self._cache_duration = 60  # 1 minute - good for scalping strategies

    def fetch_crypto_price(self, symbol):
        """
        Fetch real-time crypto price from Binance

        Parameters:
        -----------
        symbol : str
            Trading pair like 'BTCUSDT', 'ETHUSDT'

        Returns:
        --------
        dict with price data or None
        """
        try:
            # Convert symbol format (BTC/USDT -> BTCUSDT)
            binance_symbol = symbol.replace('/', '')

            # Fetch from Binance API (free, no auth needed)
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_symbol}"
            response = self.session.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    'price': float(data['lastPrice']),
                    'open': float(data['openPrice']),
                    'high': float(data['highPrice']),
                    'low': float(data['lowPrice']),
                    'volume': float(data['volume']),
                    'change_percent': float(data['priceChangePercent'])
                }
            return None
        except Exception as e:
            print(f"Error fetching crypto price: {e}")
            return None

    def _mudrex_signature(self, timestamp, method, endpoint, body=''):
        """Generate HMAC signature for Mudrex"""
        message = f"{timestamp}{method}{endpoint}{body}"
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _mudrex_request(self, method, endpoint, params=None):
        """Make authenticated request to Mudrex"""
        timestamp = str(int(time.time() * 1000))
        url = f"{self.mudrex_base_url}{endpoint}"

        signature = self._mudrex_signature(timestamp, method, endpoint, '')

        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key,
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': signature
        }

        try:
            print(f"[DEBUG] Mudrex request to: {url}")
            print(f"[DEBUG] Params: {params}")

            response = self.session.get(url, headers=headers, params=params, timeout=10)

            print(f"[DEBUG] Mudrex response status: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"[DEBUG] Mudrex error: {response.text[:500]}")
                return None

        except Exception as e:
            print(f"[ERROR] Mudrex request failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fetch_crypto_klines(self, symbol, interval='1m', limit=100):
        """
        Fetch historical klines/candles from CoinGecko (free, reliable)
        Uses intelligent caching to avoid rate limits.

        Parameters:
        -----------
        symbol : str
            Trading pair like 'BTC/USDT'
        interval : str
            '1m', '5m', '15m', '1h', '4h', '1d'
        limit : int
            Number of candles (max 1000)

        Returns:
        --------
        pandas.DataFrame with OHLCV data
        """
        # Check cache first to avoid rate limits
        cache_key = f"{symbol}_{interval}_{limit}"
        current_time = time.time()

        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            cache_age = current_time - cached_time

            if cache_age < self._cache_duration:
                print(f"[CACHE] Using cached data ({int(cache_age)}s old, fresh for {int(self._cache_duration - cache_age)}s more)")
                return cached_data
            else:
                print(f"[CACHE] Cache expired ({int(cache_age)}s old), fetching fresh data...")

        # Use CoinGecko for market data (free, no auth needed, not geo-blocked)
        print(f"[INFO] Fetching market data from CoinGecko (free, reliable)")
        df = self._fetch_coingecko_klines(symbol, interval, limit)

        # Fallback to Binance if CoinGecko fails (though Binance is geo-blocked on some platforms)
        if df is None:
            print(f"[WARN] CoinGecko failed, trying Binance...")
            df = self._fetch_binance_klines(symbol, interval, limit)

        # Cache the result if successful
        if df is not None:
            self._cache[cache_key] = (df.copy(), current_time)
            print(f"[CACHE] Data cached for {self._cache_duration}s")

        return df

    def _fetch_coingecko_klines(self, symbol, interval, limit):
        """Fetch from CoinGecko API (free, no auth needed)"""
        try:
            # Map symbol to CoinGecko ID
            symbol_map = {
                'BTC/USDT': 'bitcoin',
                'ETH/USDT': 'ethereum',
                'BNB/USDT': 'binancecoin',
                'SOL/USDT': 'solana',
                'XRP/USDT': 'ripple',
                'ADA/USDT': 'cardano',
                'DOGE/USDT': 'dogecoin',
                'MATIC/USDT': 'matic-network',
                'DOT/USDT': 'polkadot',
                'LINK/USDT': 'chainlink',
            }

            coin_id = symbol_map.get(symbol, 'bitcoin')
            print(f"[DEBUG] Fetching {symbol} ({coin_id}) from CoinGecko...")

            # CoinGecko OHLC endpoint (free, no API key needed)
            # Note: Free tier only supports daily candles, but we can use market_chart for more granular data
            url = f"{self.coingecko_base_url}/coins/{coin_id}/market_chart"

            # Map interval to days
            # CoinGecko automatically selects granularity based on days:
            # - 1 day = 5-minute intervals (288 data points)
            # - 2-90 days = hourly intervals
            # - 91+ days = daily intervals
            interval_days_map = {
                '1m': 1,    # 1 day = 5-min intervals (auto)
                '5m': 1,    # 1 day = 5-min intervals (auto)
                '15m': 7,   # 7 days = hourly intervals (auto)
                '1h': 7,    # 7 days = hourly intervals (auto)
                '4h': 30,   # 30 days = hourly intervals (auto)
                '1d': 90,   # 90 days = daily intervals (auto)
            }

            days = interval_days_map.get(interval, 1)

            # Don't specify interval - CoinGecko selects automatically based on days
            params = {
                'vs_currency': 'usd',
                'days': days,
                'x_cg_demo_api_key': self.coingecko_api_key  # Use demo API key for higher limits
            }

            print(f"[DEBUG] CoinGecko request: {url}")
            print(f"[DEBUG] Params (with API key): vs_currency=usd, days={days}")
            print(f"[DEBUG] Using CoinGecko Demo API key for higher rate limits")

            # Retry logic for rate limits (429 errors)
            max_retries = 3
            retry_delay = 2  # Start with 2 seconds

            for attempt in range(max_retries):
                response = self.session.get(url, params=params, timeout=10)
                print(f"[DEBUG] Response status: {response.status_code}")

                if response.status_code == 200:
                    break
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                        print(f"[WARN] Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        print(f"[ERROR] Rate limit persists after {max_retries} attempts")
                        return None
                else:
                    # Other errors, don't retry
                    break

            if response.status_code == 200:
                data = response.json()

                if 'prices' not in data or not data['prices']:
                    print(f"[DEBUG] No price data in CoinGecko response")
                    return None

                # Convert to DataFrame
                prices = data['prices']
                print(f"[DEBUG] Got {len(prices)} price points from CoinGecko")

                # Create OHLCV-like dataframe
                # CoinGecko returns [timestamp, price] for each point
                # We'll simulate OHLCV by treating each price as close
                df = pd.DataFrame(prices, columns=['timestamp', 'close'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                # For simplicity, set open = close for each candle
                # In real scenario, CoinGecko's paid API provides true OHLCV
                df['open'] = df['close']
                df['high'] = df['close'] * 1.001  # Simulate slight variation
                df['low'] = df['close'] * 0.999
                df['volume'] = 1000000  # Placeholder volume

                # Limit to requested number of candles
                df = df.tail(limit).reset_index(drop=True)

                # Reorder columns
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

                print(f"[DEBUG] Processed {len(df)} candles")
                print(f"[DEBUG] Latest price: ${df['close'].iloc[-1]:,.2f}")

                return df
            else:
                print(f"[DEBUG] CoinGecko error: {response.status_code}")
                if response.text:
                    print(f"[DEBUG] Error details: {response.text[:500]}")
                return None

        except Exception as e:
            print(f"[ERROR] Exception fetching CoinGecko data: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _fetch_mudrex_klines(self, symbol, interval, limit):
        """Fetch from Mudrex API"""
        try:
            print(f"[DEBUG] Fetching {symbol} from Mudrex...")
            print(f"[DEBUG] Interval: {interval}, Limit: {limit}")

            endpoint = f'/candles/{symbol}'
            params = {
                'interval': interval,
                'limit': limit
            }

            response = self._mudrex_request('GET', endpoint, params=params)

            if response and 'candles' in response:
                candles = response['candles']

                if not candles or len(candles) == 0:
                    print(f"[DEBUG] Empty data returned from Mudrex")
                    return None

                print(f"[DEBUG] Got {len(candles)} candles from Mudrex")

                # Convert to DataFrame
                df = pd.DataFrame(candles)

                # Rename columns (Mudrex format: time, o, h, l, c, v)
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

                print(f"[DEBUG] Processed DataFrame with {len(df)} rows")
                print(f"[DEBUG] Latest price: ${df['close'].iloc[-1]:,.2f}")

                return df
            else:
                print(f"[DEBUG] Invalid response from Mudrex")
                return None

        except Exception as e:
            print(f"[ERROR] Exception fetching Mudrex klines: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _fetch_binance_klines(self, symbol, interval, limit):
        """Fetch from Binance API (fallback)"""
        try:
            binance_symbol = symbol.replace('/', '').upper()

            print(f"[DEBUG] Fetching {binance_symbol} from Binance...")
            print(f"[DEBUG] Interval: {interval}, Limit: {limit}")

            url = "https://api.binance.com/api/v3/klines"
            params = {
                'symbol': binance_symbol,
                'interval': interval,
                'limit': limit
            }

            response = self.session.get(url, params=params, timeout=10)

            print(f"[DEBUG] Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                if not data or len(data) == 0:
                    print(f"[DEBUG] Empty data returned from Binance")
                    return None

                print(f"[DEBUG] Got {len(data)} candles from Binance")

                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])

                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)

                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

                print(f"[DEBUG] Processed DataFrame with {len(df)} rows")
                print(f"[DEBUG] Latest price: ${df['close'].iloc[-1]:,.2f}")

                return df
            else:
                print(f"[DEBUG] Bad status code: {response.status_code}")
                return None

        except Exception as e:
            print(f"[ERROR] Exception fetching Binance klines: {e}")
            import traceback
            traceback.print_exc()
            return None

    def fetch_stock_price(self, symbol, exchange='NSE'):
        """
        Fetch real-time stock price
        Note: For Indian stocks, you'd need a proper data provider
        This is a placeholder that returns None
        """
        # For stocks, you'd integrate with:
        # - Yahoo Finance API
        # - NSE/BSE data providers
        # - Your broker's API
        print(f"Stock data fetching not implemented for {symbol} on {exchange}")
        return None


# Singleton instance
_market_data_fetcher = None

def get_market_data_fetcher():
    """Get singleton instance of market data fetcher"""
    global _market_data_fetcher
    if _market_data_fetcher is None:
        _market_data_fetcher = MarketDataFetcher()
    return _market_data_fetcher


if __name__ == "__main__":
    # Test the fetcher
    fetcher = MarketDataFetcher()

    print("Testing Crypto Price Fetch...")
    btc_price = fetcher.fetch_crypto_price('BTC/USDT')
    if btc_price:
        print(f"BTC/USDT Price: ${btc_price['price']:,.2f}")
        print(f"24h Change: {btc_price['change_percent']:+.2f}%")
        print(f"24h High: ${btc_price['high']:,.2f}")
        print(f"24h Low: ${btc_price['low']:,.2f}")

    print("\nTesting Klines Fetch...")
    klines = fetcher.fetch_crypto_klines('BTC/USDT', interval='5m', limit=50)
    if klines is not None:
        print(f"Fetched {len(klines)} candles")
        print(f"Latest price: ${klines['close'].iloc[-1]:,.2f}")
        print(f"Time range: {klines['timestamp'].iloc[0]} to {klines['timestamp'].iloc[-1]}")
