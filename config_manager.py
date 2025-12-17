"""
Configuration Manager
Handles saving and loading bot configuration from database
"""

import json
import os
from datetime import datetime
import sqlite3


class ConfigManager:
    def __init__(self, db_path='bot_config.db'):
        """Initialize configuration manager"""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize configuration database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create config table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def get_config(self, key, default=None):
        """Get configuration value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
            result = cursor.fetchone()

            conn.close()

            if result:
                # Try to parse JSON
                try:
                    return json.loads(result[0])
                except:
                    return result[0]
            return default
        except Exception as e:
            print(f"Error getting config: {e}")
            return default

    def set_config(self, key, value):
        """Set configuration value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert value to JSON string if it's a dict or list
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value)
            else:
                value_str = str(value)

            cursor.execute('''
                INSERT INTO config (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            ''', (key, value_str, datetime.now()))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting config: {e}")
            return False

    def get_all_config(self):
        """Get all configuration as dictionary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT key, value FROM config')
            results = cursor.fetchall()

            conn.close()

            config = {}
            for key, value in results:
                try:
                    config[key] = json.loads(value)
                except:
                    config[key] = value

            return config
        except Exception as e:
            print(f"Error getting all config: {e}")
            return {}

    def delete_config(self, key):
        """Delete configuration value"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM config WHERE key = ?', (key,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting config: {e}")
            return False

    def clear_all_config(self):
        """Clear all configuration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM config')

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing config: {e}")
            return False

    def is_setup_complete(self):
        """Check if initial setup is complete"""
        market_type = self.get_config('market_type')
        return market_type is not None

    def get_market_config(self):
        """Get market-specific configuration"""
        market_type = self.get_config('market_type', 'stocks')

        if market_type == 'stocks':
            return {
                'market_type': 'stocks',
                'broker': self.get_config('stocks_broker', 'angel_one'),
                'api_key': self.get_config('stocks_api_key', ''),
                'client_code': self.get_config('stocks_client_code', ''),
                'password': self.get_config('stocks_password', ''),
                'totp_secret': self.get_config('stocks_totp_secret', ''),
                'symbol': self.get_config('stocks_symbol', 'SBIN'),
                'exchange': self.get_config('stocks_exchange', 'NSE'),
            }
        else:  # crypto
            return {
                'market_type': 'crypto',
                'exchange': self.get_config('crypto_exchange', 'mudrex'),
                'api_key': self.get_config('crypto_api_key', ''),
                'api_secret': self.get_config('crypto_api_secret', ''),
                'symbol': self.get_config('crypto_symbol', 'BTC/USDT'),
            }

    def get_trading_config(self):
        """Get trading parameters"""
        return {
            'capital': float(self.get_config('trading_capital', 10000)),
            'risk_per_trade': float(self.get_config('trading_risk', 2.0)) / 100,
            'fast_ema': int(self.get_config('strategy_fast_ema', 9)),
            'slow_ema': int(self.get_config('strategy_slow_ema', 15)),
            'rsi_period': int(self.get_config('strategy_rsi_period', 14)),
            'rsi_overbought': int(self.get_config('strategy_rsi_overbought', 70)),
            'rsi_oversold': int(self.get_config('strategy_rsi_oversold', 30)),
            'risk_reward_ratio': float(self.get_config('strategy_risk_reward', 2.0)),
        }

    def save_stocks_config(self, broker, api_key, client_code, password, totp_secret, symbol, exchange):
        """Save stock market configuration"""
        self.set_config('market_type', 'stocks')
        self.set_config('stocks_broker', broker)
        self.set_config('stocks_api_key', api_key)
        self.set_config('stocks_client_code', client_code)
        self.set_config('stocks_password', password)
        self.set_config('stocks_totp_secret', totp_secret)
        self.set_config('stocks_symbol', symbol)
        self.set_config('stocks_exchange', exchange)

    def save_crypto_config(self, exchange, api_key, api_secret, symbol):
        """Save crypto market configuration"""
        self.set_config('market_type', 'crypto')
        self.set_config('crypto_exchange', exchange)
        self.set_config('crypto_api_key', api_key)
        self.set_config('crypto_api_secret', api_secret)
        self.set_config('crypto_symbol', symbol)

    def save_trading_config(self, capital, risk_per_trade):
        """Save trading parameters"""
        self.set_config('trading_capital', capital)
        self.set_config('trading_risk', risk_per_trade)

    def save_strategy_config(self, fast_ema, slow_ema, rsi_period, rsi_overbought,
                            rsi_oversold, risk_reward_ratio):
        """Save strategy parameters"""
        self.set_config('strategy_fast_ema', fast_ema)
        self.set_config('strategy_slow_ema', slow_ema)
        self.set_config('strategy_rsi_period', rsi_period)
        self.set_config('strategy_rsi_overbought', rsi_overbought)
        self.set_config('strategy_rsi_oversold', rsi_oversold)
        self.set_config('strategy_risk_reward', risk_reward_ratio)
