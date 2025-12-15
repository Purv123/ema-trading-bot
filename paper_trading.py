"""
Paper Trading Simulator
Test strategies without risking real money
"""

import pandas as pd
from datetime import datetime
from ema_algo_trading import EMAStrategy
from database_handler import TradingDatabase


class PaperTradingSimulator:
    def __init__(self, initial_capital=10000, risk_per_trade=0.02):
        """
        Initialize paper trading simulator
        
        Parameters:
        -----------
        initial_capital : float
            Starting capital
        risk_per_trade : float
            Risk percentage per trade
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.strategy = EMAStrategy(capital=initial_capital, risk_per_trade=risk_per_trade)
        self.db = TradingDatabase()
        self.current_trade = None
        
    def fetch_live_data(self, symbol, exchange='NSE'):
        """
        Fetch live market data
        Override this with actual data fetching in production
        """
        # This is a placeholder - integrate with your data source
        # For now, return None
        return None
    
    def execute_paper_trade(self, signal, data, symbol, exchange='NSE', asset_type='STOCK'):
        """
        Execute a paper trade (simulated)
        
        Parameters:
        -----------
        signal : str
            'BUY' or 'SELL'
        data : pandas.DataFrame
            Market data
        symbol : str
            Trading symbol
        exchange : str
            Exchange name
        asset_type : str
            'STOCK' or 'CRYPTO'
        """
        current_price = data['close'].iloc[-1]
        stop_loss, target = self.strategy.calculate_stop_loss_target(data, signal)
        quantity = self.strategy.calculate_position_size(current_price, stop_loss)
        
        if quantity <= 0:
            print("⚠️ Quantity too small to trade")
            return False
        
        # Calculate trade cost
        trade_value = current_price * quantity
        
        if trade_value > self.capital:
            print(f"⚠️ Insufficient capital: Need ₹{trade_value:.2f}, Have ₹{self.capital:.2f}")
            return False
        
        # Create trade record
        trade_id = f"PAPER_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        trade_data = {
            'trade_id': trade_id,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': symbol,
            'exchange': exchange,
            'asset_type': asset_type,
            'signal_type': signal,
            'entry_price': current_price,
            'exit_price': None,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'target': target,
            'pnl': 0,
            'pnl_percent': 0,
            'status': 'OPEN',
            'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'exit_time': None,
            'holding_time_minutes': 0,
            'reason': None,
            'mode': 'paper',
            'indicators': {
                'ema9': float(data['ema9'].iloc[-1]) if 'ema9' in data else None,
                'ema15': float(data['ema15'].iloc[-1]) if 'ema15' in data else None,
                'rsi': float(data['rsi'].iloc[-1]) if 'rsi' in data else None,
                'macd': float(data['macd'].iloc[-1]) if 'macd' in data else None,
            }
        }
        
        # Update capital
        self.capital -= trade_value
        
        # Save to database
        self.db.insert_trade(trade_data)
        
        # Update strategy state
        self.strategy.position = 'LONG' if signal == 'BUY' else 'SHORT'
        self.strategy.entry_price = current_price
        self.strategy.stop_loss = stop_loss
        self.strategy.target = target
        
        self.current_trade = trade_data
        
        print(f"\n{'='*60}")
        print(f"📝 PAPER TRADE EXECUTED: {signal}")
        print(f"Symbol: {symbol}")
        print(f"Entry: ₹{current_price:.2f} | Quantity: {quantity}")
        print(f"Stop Loss: ₹{stop_loss:.2f} | Target: ₹{target:.2f}")
        print(f"Capital Remaining: ₹{self.capital:.2f}")
        print(f"{'='*60}\n")
        
        return True
    
    def exit_paper_trade(self, data, reason='TARGET/SL'):
        """
        Exit current paper trade
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Current market data
        reason : str
            Exit reason
        """
        if not self.current_trade:
            return False
        
        exit_price = data['close'].iloc[-1]
        entry_price = self.current_trade['entry_price']
        quantity = self.current_trade['quantity']
        
        # Calculate P&L
        if self.current_trade['signal_type'] == 'BUY':
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        pnl_percent = (pnl / (entry_price * quantity)) * 100
        
        # Calculate holding time
        entry_time = datetime.strptime(self.current_trade['entry_time'], '%Y-%m-%d %H:%M:%S')
        exit_time = datetime.now()
        holding_time = int((exit_time - entry_time).total_seconds() / 60)
        
        # Update trade record
        trade_update = {
            'exit_price': exit_price,
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'status': 'CLOSED',
            'exit_time': exit_time.strftime('%Y-%m-%d %H:%M:%S'),
            'holding_time_minutes': holding_time,
            'reason': reason
        }
        
        # Update capital
        self.capital += (entry_price * quantity) + pnl
        
        # Save to database
        conn = self.db.connect()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in trade_update.keys()])
        query = f"UPDATE trades SET {set_clause} WHERE trade_id = ?"
        
        cursor.execute(query, list(trade_update.values()) + [self.current_trade['trade_id']])
        conn.commit()
        self.db.close()
        
        # Reset strategy state
        self.strategy.position = None
        self.strategy.entry_price = 0
        self.strategy.stop_loss = 0
        self.strategy.target = 0
        
        print(f"\n{'='*60}")
        print(f"📝 PAPER TRADE CLOSED: {self.current_trade['signal_type']}")
        print(f"Entry: ₹{entry_price:.2f} | Exit: ₹{exit_price:.2f}")
        print(f"P&L: ₹{pnl:.2f} ({pnl_percent:+.2f}%)")
        print(f"Reason: {reason}")
        print(f"Capital: ₹{self.capital:.2f} (Initial: ₹{self.initial_capital:.2f})")
        print(f"{'='*60}\n")
        
        self.current_trade = None
        
        return True
    
    def get_account_status(self):
        """Get current account status"""
        open_trades = self.db.get_all_trades(mode='paper')
        open_trades = open_trades[open_trades['status'] == 'OPEN']
        
        used_capital = sum([row['entry_price'] * row['quantity'] 
                           for _, row in open_trades.iterrows()])
        
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.capital,
            'used_capital': used_capital,
            'available_capital': self.capital,
            'total_equity': self.capital + used_capital,
            'pnl': (self.capital + used_capital) - self.initial_capital,
            'pnl_percent': ((self.capital + used_capital - self.initial_capital) / 
                           self.initial_capital * 100),
            'open_positions': len(open_trades)
        }


def run_paper_trading(symbol='SBIN', exchange='NSE', capital=10000):
    """
    Run paper trading mode
    
    Parameters:
    -----------
    symbol : str
        Trading symbol
    exchange : str
        Exchange
    capital : float
        Initial capital
    """
    simulator = PaperTradingSimulator(initial_capital=capital)
    
    print(f"\n{'='*60}")
    print(f"📝 PAPER TRADING MODE")
    print(f"Symbol: {symbol} | Exchange: {exchange}")
    print(f"Initial Capital: ₹{capital}")
    print(f"This is simulated trading - No real money involved!")
    print(f"{'='*60}\n")
    
    import time
    
    try:
        while True:
            # In production, fetch real market data
            # For now, this is a placeholder
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring {symbol}...")
            
            # Here you would:
            # 1. Fetch live data
            # 2. Check for signals
            # 3. Execute paper trades
            # 4. Monitor positions
            
            time.sleep(300)  # Wait 5 minutes
            
    except KeyboardInterrupt:
        print("\n\nStopping paper trading...")
        
        # Show final account status
        status = simulator.get_account_status()
        print(f"\n{'='*60}")
        print("PAPER TRADING SESSION SUMMARY")
        print(f"{'='*60}")
        print(f"Initial Capital: ₹{status['initial_capital']:,.2f}")
        print(f"Final Equity: ₹{status['total_equity']:,.2f}")
        print(f"Total P&L: ₹{status['pnl']:+,.2f} ({status['pnl_percent']:+.2f}%)")
        print(f"Open Positions: {status['open_positions']}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    run_paper_trading(symbol='SBIN', exchange='NSE', capital=10000)
