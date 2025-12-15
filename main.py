"""
Main Trading Bot Application
Orchestrates live trading, paper trading, and backtesting
"""

import argparse
import sys
from datetime import datetime
import configparser

# Import trading modules
from ema_algo_trading import EMAStrategy
from angel_one_live_trading import run_live_trading_angel_one, AngelOneTrading
from mudrex_crypto_trading import run_crypto_trading, MudrexTrading
from paper_trading import run_paper_trading, PaperTradingSimulator
from backtest_engine import BacktestEngine, load_historical_data
from database_handler import TradingDatabase


class TradingBotApp:
    def __init__(self, config_file='config.ini'):
        """
        Initialize Trading Bot Application
        
        Parameters:
        -----------
        config_file : str
            Path to configuration file
        """
        self.config = self.load_config(config_file)
        self.db = TradingDatabase()
    
    def load_config(self, config_file):
        """Load configuration from file"""
        config = configparser.ConfigParser()
        
        try:
            config.read(config_file)
            print(f"✓ Configuration loaded from {config_file}")
            return config
        except Exception as e:
            print(f"✗ Error loading config: {e}")
            print("Using default configuration")
            return None
    
    def run_live_stocks(self):
        """Run live stock trading with Angel One"""
        print("\n" + "="*60)
        print("🚀 STARTING LIVE STOCK TRADING")
        print("="*60 + "\n")
        
        if not self.config:
            print("❌ Configuration file not found. Please update config.ini")
            return
        
        # Get credentials from config
        api_key = self.config.get('ANGEL_ONE', 'API_KEY')
        client_code = self.config.get('ANGEL_ONE', 'CLIENT_CODE')
        password = self.config.get('ANGEL_ONE', 'PASSWORD')
        totp_secret = self.config.get('ANGEL_ONE', 'TOTP_SECRET')
        
        # Get trading parameters
        symbol = self.config.get('TRADING', 'SYMBOL', fallback='SBIN')
        exchange = self.config.get('TRADING', 'EXCHANGE', fallback='NSE')
        capital = float(self.config.get('TRADING', 'TOTAL_CAPITAL', fallback='10000'))
        
        # Validate credentials
        if api_key == 'your_api_key_here':
            print("❌ Please update your Angel One API credentials in config.ini")
            return
        
        # Run live trading
        run_live_trading_angel_one(
            api_key=api_key,
            client_code=client_code,
            password=password,
            totp_secret=totp_secret,
            symbol=symbol,
            exchange=exchange,
            capital=capital
        )
    
    def run_live_crypto(self):
        """Run live crypto trading with Mudrex"""
        print("\n" + "="*60)
        print("🚀 STARTING LIVE CRYPTO TRADING")
        print("="*60 + "\n")
        
        if not self.config:
            print("❌ Configuration file not found. Please update config.ini")
            return
        
        # Get credentials from config
        api_key = self.config.get('MUDREX', 'API_KEY', fallback='')
        api_secret = self.config.get('MUDREX', 'API_SECRET', fallback='')
        
        # Get trading parameters
        symbol = self.config.get('CRYPTO', 'SYMBOL', fallback='BTC/USDT')
        capital = float(self.config.get('CRYPTO', 'CAPITAL', fallback='10000'))
        risk = float(self.config.get('CRYPTO', 'RISK_PER_TRADE', fallback='0.02'))
        
        # Validate credentials
        if not api_key or api_key == 'your_mudrex_api_key':
            print("❌ Please update your Mudrex API credentials in config.ini")
            return
        
        # Run crypto trading
        run_crypto_trading(
            api_key=api_key,
            api_secret=api_secret,
            symbol=symbol,
            capital=capital,
            risk_per_trade=risk
        )
    
    def run_paper_mode(self):
        """Run paper trading mode"""
        print("\n" + "="*60)
        print("📝 STARTING PAPER TRADING MODE")
        print("="*60 + "\n")
        
        # Get trading parameters
        symbol = 'SBIN'
        exchange = 'NSE'
        capital = 10000
        
        if self.config:
            symbol = self.config.get('TRADING', 'SYMBOL', fallback='SBIN')
            exchange = self.config.get('TRADING', 'EXCHANGE', fallback='NSE')
            capital = float(self.config.get('TRADING', 'TOTAL_CAPITAL', fallback='10000'))
        
        run_paper_trading(symbol=symbol, exchange=exchange, capital=capital)
    
    def run_backtest(self, data_file):
        """Run backtest on historical data"""
        print("\n" + "="*60)
        print("🔬 STARTING BACKTEST")
        print("="*60 + "\n")
        
        # Load data
        try:
            data = load_historical_data(data_file)
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return
        
        # Get parameters
        capital = 10000
        risk = 0.02
        symbol = 'TEST'
        
        if self.config:
            capital = float(self.config.get('TRADING', 'TOTAL_CAPITAL', fallback='10000'))
            risk = float(self.config.get('TRADING', 'RISK_PER_TRADE', fallback='0.02'))
        
        # Run backtest
        engine = BacktestEngine(initial_capital=capital, risk_per_trade=risk)
        results = engine.run_backtest(data, symbol=symbol)
        
        if results:
            # Plot results
            engine.plot_results()
    
    def run_dashboard(self):
        """Launch web dashboard"""
        print("\n" + "="*60)
        print("📊 LAUNCHING DASHBOARD")
        print("="*60 + "\n")
        
        import subprocess
        subprocess.run(['streamlit', 'run', 'dashboard.py'])
    
    def show_performance(self):
        """Show performance summary"""
        print("\n" + "="*60)
        print("📈 PERFORMANCE SUMMARY")
        print("="*60 + "\n")
        
        modes = ['live', 'paper', 'backtest']
        
        for mode in modes:
            summary = self.db.get_performance_summary(mode=mode)
            
            print(f"\n{mode.upper()} MODE:")
            print(f"  Total Trades: {summary['total_trades']}")
            print(f"  Winning Trades: {summary['winning_trades']}")
            print(f"  Losing Trades: {summary['losing_trades']}")
            print(f"  Win Rate: {summary['win_rate']:.2f}%")
            print(f"  Total P&L: ₹{summary['total_pnl']:,.2f}")
            print(f"  Profit Factor: {summary['profit_factor']:.2f}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='EMA Trading Bot - Automated Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --live-stocks         # Start live stock trading
  python main.py --live-crypto         # Start live crypto trading
  python main.py --paper              # Start paper trading
  python main.py --backtest data.csv  # Run backtest
  python main.py --dashboard          # Launch web dashboard
  python main.py --performance        # Show performance summary
        """
    )
    
    parser.add_argument('--live-stocks', action='store_true',
                       help='Start live stock trading (Angel One)')
    parser.add_argument('--live-crypto', action='store_true',
                       help='Start live crypto trading (Mudrex)')
    parser.add_argument('--paper', action='store_true',
                       help='Start paper trading mode')
    parser.add_argument('--backtest', type=str, metavar='DATA_FILE',
                       help='Run backtest on historical data CSV')
    parser.add_argument('--dashboard', action='store_true',
                       help='Launch web dashboard')
    parser.add_argument('--performance', action='store_true',
                       help='Show performance summary')
    parser.add_argument('--config', type=str, default='config.ini',
                       help='Configuration file path (default: config.ini)')
    
    args = parser.parse_args()
    
    # Show banner
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           📈 EMA TRADING BOT v1.0 📈                      ║
    ║                                                           ║
    ║   Automated Trading System with 9-15 EMA Strategy        ║
    ║   Stocks + Crypto | Live + Paper + Backtest             ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Initialize app
    app = TradingBotApp(config_file=args.config)
    
    # Execute command
    if args.live_stocks:
        app.run_live_stocks()
    
    elif args.live_crypto:
        app.run_live_crypto()
    
    elif args.paper:
        app.run_paper_mode()
    
    elif args.backtest:
        app.run_backtest(args.backtest)
    
    elif args.dashboard:
        app.run_dashboard()
    
    elif args.performance:
        app.show_performance()
    
    else:
        parser.print_help()
        print("\n💡 Quick start:")
        print("   python main.py --dashboard     # Launch web interface")
        print("   python main.py --paper         # Start paper trading")
        print("\n⚠️  Before live trading:")
        print("   1. Update config.ini with your API credentials")
        print("   2. Test thoroughly in paper mode first!")


if __name__ == "__main__":
    main()
