"""
Market Data Fetcher
Fetches real-time market data from various sources
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time


class MarketDataFetcher:
    """Fetch real market data from exchanges"""

    def __init__(self):
        self.session = requests.Session()

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

    def fetch_crypto_klines(self, symbol, interval='1m', limit=100):
        """
        Fetch historical klines/candles from Binance

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
        try:
            # Convert symbol format
            binance_symbol = symbol.replace('/', '')

            # Fetch klines from Binance
            url = f"https://api.binance.com/api/v3/klines"
            params = {
                'symbol': binance_symbol,
                'interval': interval,
                'limit': limit
            }

            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Parse klines data
                df = pd.DataFrame(data, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                    'taker_buy_quote', 'ignore'
                ])

                # Convert types
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)

                # Keep only needed columns
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

                return df

            return None

        except Exception as e:
            print(f"Error fetching klines: {e}")
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
