"""
Kraken WebSocket Client for Real-Time Market Data
Provides true 1-second price updates for scalping strategies
"""

import websocket
import json
import threading
import time
import pandas as pd
from datetime import datetime
from collections import deque
import logging

logger = logging.getLogger(__name__)


class KrakenWebSocket:
    """
    Real-time market data from Kraken WebSocket
    Updates every second - perfect for scalping!
    """

    def __init__(self, symbol='BTC/USDT'):
        self.symbol = symbol
        self.ws = None
        self.thread = None
        self.running = False

        # Convert symbol format: BTC/USDT -> XBT/USDT (Kraken uses XBT for Bitcoin)
        # Keep the slash - Kraken WebSocket expects "XBT/USDT" format
        self.kraken_symbol = symbol.replace('BTC', 'XBT')

        # Store recent trades to build candles
        self.recent_trades = deque(maxlen=1000)
        self.current_price = None
        self.last_update = None

        # Candle building (1-minute candles)
        self.candles = []
        self.current_candle = None

        logger.info(f"🚀 Initializing Kraken WebSocket for {symbol}")

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)

            # Log subscription confirmations and system messages
            if isinstance(data, dict):
                if data.get('event') == 'subscriptionStatus':
                    if data.get('status') == 'subscribed':
                        logger.info(f"✅ Successfully subscribed to {data.get('pair')} {data.get('subscription', {}).get('name')}")
                    else:
                        logger.warning(f"⚠️ Subscription status: {data}")
                elif data.get('event') == 'error':
                    logger.error(f"❌ Kraken error: {data.get('errorMessage')}")
                return

            # Kraken sends different message types
            if isinstance(data, list) and len(data) > 1:
                channel_name = data[-2] if len(data) > 2 else None

                # Ticker updates
                if channel_name == 'ticker':
                    ticker_data = data[1]

                    # Extract price (last trade price)
                    if 'c' in ticker_data:  # 'c' = close/last price
                        price = float(ticker_data['c'][0])
                        self.current_price = price
                        self.last_update = time.time()

                        # Add to recent trades
                        self.recent_trades.append({
                            'price': price,
                            'timestamp': datetime.now()
                        })

                        # Build candles
                        self._update_candle(price)

                        print(f"[WS] {self.symbol}: ${price:,.2f}", end='\r')

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(f"Message was: {message[:200]}")

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        logger.warning(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.running = False

    def _on_open(self, ws):
        """Handle WebSocket connection open"""
        logger.info(f"✅ WebSocket connected to Kraken")

        # Subscribe to ticker for the symbol
        subscribe_message = {
            "event": "subscribe",
            "pair": [self.kraken_symbol],
            "subscription": {
                "name": "ticker"
            }
        }

        ws.send(json.dumps(subscribe_message))
        logger.info(f"📡 Subscribed to {self.kraken_symbol} ticker feed")

    def _update_candle(self, price):
        """Build 1-minute candles from tick data"""
        now = datetime.now()
        current_minute = now.replace(second=0, microsecond=0)

        if self.current_candle is None or self.current_candle['timestamp'] != current_minute:
            # New candle
            if self.current_candle is not None:
                # Save completed candle
                self.candles.append(self.current_candle)

                # Keep only last 500 candles
                if len(self.candles) > 500:
                    self.candles.pop(0)

            # Start new candle
            self.current_candle = {
                'timestamp': current_minute,
                'open': price,
                'high': price,
                'low': price,
                'close': price,
                'volume': 0
            }
        else:
            # Update current candle
            self.current_candle['high'] = max(self.current_candle['high'], price)
            self.current_candle['low'] = min(self.current_candle['low'], price)
            self.current_candle['close'] = price

    def start(self):
        """Start WebSocket connection in background thread"""
        if self.running:
            logger.warning("WebSocket already running")
            return

        self.running = True

        # WebSocket URL for Kraken
        ws_url = "wss://ws.kraken.com"

        # Create WebSocket connection
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )

        # Run in background thread
        self.thread = threading.Thread(target=self.ws.run_forever)
        self.thread.daemon = True
        self.thread.start()

        logger.info("🔄 WebSocket thread started")

        # Wait for initial connection
        time.sleep(2)

    def stop(self):
        """Stop WebSocket connection"""
        self.running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("⏹️ WebSocket stopped")

    def get_current_price(self):
        """Get the most recent price"""
        if self.current_price is None:
            return None

        # Check if data is stale (no update in 10 seconds)
        if self.last_update and (time.time() - self.last_update) > 10:
            logger.warning("WebSocket data is stale (no updates in 10s)")
            return None

        return self.current_price

    def get_candles(self, limit=100):
        """
        Get recent 1-minute candles as DataFrame

        Returns:
        --------
        pandas.DataFrame with OHLCV data
        """
        if not self.candles:
            return None

        # Get last N candles
        recent_candles = self.candles[-limit:] if len(self.candles) > limit else self.candles

        if not recent_candles:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(recent_candles)

        # Ensure proper data types
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)

        return df

    def is_connected(self):
        """Check if WebSocket is connected and receiving data"""
        if not self.running:
            return False

        if self.last_update is None:
            return False

        # Check if data is fresh (updated within last 10 seconds)
        return (time.time() - self.last_update) < 10


if __name__ == "__main__":
    # Test the WebSocket client
    logging.basicConfig(level=logging.INFO)

    print("Testing Kraken WebSocket...")

    ws_client = KrakenWebSocket('BTC/USDT')
    ws_client.start()

    print("\nReceiving real-time prices... (Ctrl+C to stop)\n")

    try:
        # Run for 60 seconds to collect data
        for i in range(60):
            time.sleep(1)

            price = ws_client.get_current_price()
            if price:
                print(f"[{i+1}s] Current BTC price: ${price:,.2f}")

            # Show candles after 30 seconds
            if i == 30:
                candles = ws_client.get_candles(limit=10)
                if candles is not None:
                    print("\n--- Recent Candles ---")
                    print(candles[['timestamp', 'open', 'high', 'low', 'close']].tail())
                    print()

    except KeyboardInterrupt:
        print("\n\nStopping...")

    finally:
        ws_client.stop()
        print("WebSocket test complete!")
