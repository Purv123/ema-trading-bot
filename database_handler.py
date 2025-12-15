"""
Database Handler for Trading Bot
Stores trades, positions, and performance metrics
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json


class TradingDatabase:
    def __init__(self, db_path='trading_data.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Create database tables"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_id TEXT UNIQUE,
                timestamp DATETIME,
                symbol TEXT,
                exchange TEXT,
                asset_type TEXT,
                signal_type TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                stop_loss REAL,
                target REAL,
                pnl REAL,
                pnl_percent REAL,
                status TEXT,
                entry_time DATETIME,
                exit_time DATETIME,
                holding_time_minutes INTEGER,
                reason TEXT,
                mode TEXT,
                indicators TEXT
            )
        ''')
        
        conn.commit()
        self.close()
    
    def insert_trade(self, trade_data):
        """Insert a new trade record"""
        conn = self.connect()
        cursor = conn.cursor()
        
        if 'trade_id' not in trade_data:
            trade_data['trade_id'] = f"TRD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if 'indicators' in trade_data and isinstance(trade_data['indicators'], dict):
            trade_data['indicators'] = json.dumps(trade_data['indicators'])
        
        columns = ', '.join(trade_data.keys())
        placeholders = ', '.join(['?' for _ in trade_data])
        
        query = f"INSERT OR REPLACE INTO trades ({columns}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, list(trade_data.values()))
            conn.commit()
            print(f"✓ Trade saved: {trade_data.get('trade_id')}")
        except sqlite3.Error as e:
            print(f"✗ Error saving trade: {e}")
        finally:
            self.close()
    
    def get_all_trades(self, mode=None):
        """Get all trades"""
        conn = self.connect()
        
        query = "SELECT * FROM trades"
        params = []
        
        if mode:
            query += " WHERE mode = ?"
            params.append(mode)
        
        query += " ORDER BY entry_time DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        self.close()
        
        return df
    
    def get_performance_summary(self, mode='live'):
        """Get overall performance summary"""
        trades = self.get_all_trades(mode=mode)
        trades = trades[trades['status'] == 'CLOSED']
        
        if len(trades) == 0:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0
            }
        
        total_trades = len(trades)
        winning_trades = len(trades[trades['pnl'] > 0])
        losing_trades = len(trades[trades['pnl'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = trades['pnl'].sum()
        
        winning_pnl = trades[trades['pnl'] > 0]['pnl']
        losing_pnl = trades[trades['pnl'] < 0]['pnl']
        
        avg_win = winning_pnl.mean() if len(winning_pnl) > 0 else 0
        avg_loss = losing_pnl.mean() if len(losing_pnl) > 0 else 0
        
        total_wins = winning_pnl.sum() if len(winning_pnl) > 0 else 0
        total_losses = abs(losing_pnl.sum()) if len(losing_pnl) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }
