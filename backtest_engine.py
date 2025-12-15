"""
Backtesting Engine
Test trading strategy on historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from ema_algo_trading import EMAStrategy
from database_handler import TradingDatabase
import matplotlib.pyplot as plt


class BacktestEngine:
    def __init__(self, initial_capital=10000, risk_per_trade=0.02):
        """
        Initialize backtesting engine
        
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
        
        self.trades = []
        self.equity_curve = []
        
    def run_backtest(self, data, symbol='TEST', exchange='NSE'):
        """
        Run backtest on historical data
        
        Parameters:
        -----------
        data : pandas.DataFrame
            Historical OHLCV data with columns: timestamp, open, high, low, close, volume
        symbol : str
            Trading symbol
        exchange : str
            Exchange name
        
        Returns:
        --------
        dict : Backtest results
        """
        print(f"\n{'='*60}")
        print(f"🔬 BACKTESTING: {symbol}")
        print(f"Data Period: {data['timestamp'].iloc[0]} to {data['timestamp'].iloc[-1]}")
        print(f"Total Candles: {len(data)}")
        print(f"Initial Capital: ₹{self.initial_capital:,.2f}")
        print(f"{'='*60}\n")
        
        # Reset
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = [self.initial_capital]
        
        # Track current trade
        current_trade = None
        
        # Iterate through data
        for i in range(30, len(data)):
            current_data = data.iloc[:i+1].copy()
            current_candle = data.iloc[i]
            
            # Check exit conditions first
            if self.strategy.position:
                should_exit = self.strategy.check_exit_conditions(current_data)
                
                if should_exit:
                    # Exit trade
                    exit_price = current_candle['close']
                    entry_price = current_trade['entry_price']
                    quantity = current_trade['quantity']
                    
                    # Calculate P&L
                    if current_trade['signal_type'] == 'BUY':
                        pnl = (exit_price - entry_price) * quantity
                    else:
                        pnl = (entry_price - exit_price) * quantity
                    
                    pnl_percent = (pnl / (entry_price * quantity)) * 100
                    
                    # Update capital
                    self.capital += pnl
                    
                    # Record trade
                    trade_record = {
                        'trade_id': f"BT_{i}",
                        'symbol': symbol,
                        'exchange': exchange,
                        'signal_type': current_trade['signal_type'],
                        'entry_time': current_trade['entry_time'],
                        'exit_time': current_candle['timestamp'],
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'quantity': quantity,
                        'stop_loss': current_trade['stop_loss'],
                        'target': current_trade['target'],
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'status': 'CLOSED',
                        'mode': 'backtest'
                    }
                    
                    self.trades.append(trade_record)
                    
                    # Save to database
                    self.db.insert_trade(trade_record)
                    
                    # Print trade
                    print(f"[{current_candle['timestamp']}] EXIT: {current_trade['signal_type']}")
                    print(f"  Entry: ₹{entry_price:.2f} | Exit: ₹{exit_price:.2f}")
                    print(f"  P&L: ₹{pnl:.2f} ({pnl_percent:+.2f}%)")
                    print(f"  Capital: ₹{self.capital:,.2f}\n")
                    
                    # Reset
                    current_trade = None
                    self.strategy.position = None
            
            # Generate new signals if no position
            if self.strategy.position is None:
                signal = self.strategy.generate_signal(current_data)
                
                if signal:
                    current_price = current_candle['close']
                    stop_loss, target = self.strategy.calculate_stop_loss_target(current_data, signal)
                    quantity = self.strategy.calculate_position_size(current_price, stop_loss)
                    
                    if quantity > 0:
                        # Enter trade
                        current_trade = {
                            'signal_type': signal,
                            'entry_time': current_candle['timestamp'],
                            'entry_price': current_price,
                            'quantity': quantity,
                            'stop_loss': stop_loss,
                            'target': target
                        }
                        
                        # Update strategy state
                        self.strategy.position = 'LONG' if signal == 'BUY' else 'SHORT'
                        self.strategy.entry_price = current_price
                        self.strategy.stop_loss = stop_loss
                        self.strategy.target = target
                        
                        print(f"[{current_candle['timestamp']}] ENTRY: {signal}")
                        print(f"  Entry: ₹{current_price:.2f} | Quantity: {quantity}")
                        print(f"  Stop Loss: ₹{stop_loss:.2f} | Target: ₹{target:.2f}\n")
            
            # Update equity curve
            if self.strategy.position:
                # Mark-to-market
                current_price = current_candle['close']
                entry_price = current_trade['entry_price']
                quantity = current_trade['quantity']
                
                if current_trade['signal_type'] == 'BUY':
                    unrealized_pnl = (current_price - entry_price) * quantity
                else:
                    unrealized_pnl = (entry_price - current_price) * quantity
                
                equity = self.capital + unrealized_pnl
            else:
                equity = self.capital
            
            self.equity_curve.append(equity)
        
        # Calculate results
        results = self.calculate_results()
        
        return results
    
    def calculate_results(self):
        """Calculate backtest results and metrics"""
        if len(self.trades) == 0:
            print("⚠️ No trades executed in backtest")
            return None
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = trades_df['pnl'].sum()
        total_pnl_percent = (self.capital - self.initial_capital) / self.initial_capital * 100
        
        winning_pnl = trades_df[trades_df['pnl'] > 0]['pnl']
        losing_pnl = trades_df[trades_df['pnl'] < 0]['pnl']
        
        avg_win = winning_pnl.mean() if len(winning_pnl) > 0 else 0
        avg_loss = losing_pnl.mean() if len(losing_pnl) > 0 else 0
        largest_win = winning_pnl.max() if len(winning_pnl) > 0 else 0
        largest_loss = losing_pnl.min() if len(losing_pnl) > 0 else 0
        
        # Profit factor
        total_wins = winning_pnl.sum() if len(winning_pnl) > 0 else 0
        total_losses = abs(losing_pnl.sum()) if len(losing_pnl) > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Risk-reward ratio
        avg_rr_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Max drawdown
        equity_curve = pd.Series(self.equity_curve)
        cumulative_max = equity_curve.expanding().max()
        drawdown = (equity_curve - cumulative_max) / cumulative_max * 100
        max_drawdown = drawdown.min()
        
        # Sharpe ratio (simplified - assumes daily returns)
        returns = equity_curve.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # Expectancy
        expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * abs(avg_loss))
        
        results = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'profit_factor': profit_factor,
            'avg_rr_ratio': avg_rr_ratio,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'expectancy': expectancy,
            'final_capital': self.capital,
            'initial_capital': self.initial_capital
        }
        
        self.print_results(results)
        
        return results
    
    def print_results(self, results):
        """Print formatted backtest results"""
        print(f"\n{'='*60}")
        print("BACKTEST RESULTS")
        print(f"{'='*60}")
        
        print(f"\n📊 TRADE STATISTICS")
        print(f"  Total Trades: {results['total_trades']}")
        print(f"  Winning Trades: {results['winning_trades']} ({results['win_rate']:.2f}%)")
        print(f"  Losing Trades: {results['losing_trades']}")
        
        print(f"\n💰 PROFIT & LOSS")
        print(f"  Initial Capital: ₹{results['initial_capital']:,.2f}")
        print(f"  Final Capital: ₹{results['final_capital']:,.2f}")
        print(f"  Total P&L: ₹{results['total_pnl']:+,.2f} ({results['total_pnl_percent']:+.2f}%)")
        print(f"  Average Win: ₹{results['avg_win']:,.2f}")
        print(f"  Average Loss: ₹{results['avg_loss']:,.2f}")
        print(f"  Largest Win: ₹{results['largest_win']:,.2f}")
        print(f"  Largest Loss: ₹{results['largest_loss']:,.2f}")
        
        print(f"\n📈 PERFORMANCE METRICS")
        print(f"  Profit Factor: {results['profit_factor']:.2f}")
        print(f"  Risk-Reward Ratio: {results['avg_rr_ratio']:.2f}")
        print(f"  Max Drawdown: {results['max_drawdown']:.2f}%")
        print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"  Expectancy: ₹{results['expectancy']:.2f}")
        
        print(f"\n{'='*60}\n")
    
    def plot_results(self, save_path='backtest_results.png'):
        """Plot equity curve and drawdown"""
        if len(self.equity_curve) == 0:
            print("No data to plot")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Equity curve
        equity = pd.Series(self.equity_curve)
        ax1.plot(equity, label='Equity', linewidth=2)
        ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', label='Initial Capital')
        ax1.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Equity (₹)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        cumulative_max = equity.expanding().max()
        drawdown = (equity - cumulative_max) / cumulative_max * 100
        ax2.fill_between(range(len(drawdown)), drawdown, 0, color='red', alpha=0.3)
        ax2.plot(drawdown, color='red', linewidth=2)
        ax2.set_title('Drawdown', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Trade Number')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✓ Chart saved: {save_path}")
        
        return fig


def load_historical_data(csv_path):
    """
    Load historical data from CSV
    
    CSV should have columns: timestamp, open, high, low, close, volume
    """
    df = pd.read_csv(csv_path)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Convert to numeric
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col])
    
    print(f"✓ Loaded {len(df)} candles from {csv_path}")
    
    return df


if __name__ == "__main__":
    # Example usage
    print("Backtesting Engine")
    print("=" * 60)
    print("\nTo run backtest:")
    print("1. Prepare historical data in CSV format")
    print("   Required columns: timestamp, open, high, low, close, volume")
    print("2. Load data: data = load_historical_data('your_data.csv')")
    print("3. Run backtest: engine.run_backtest(data, symbol='SBIN')")
    print("=" * 60)
