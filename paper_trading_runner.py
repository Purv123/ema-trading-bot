"""
Paper Trading Runner
Executes paper trading bot with configured parameters
"""

import argparse
import sys
import time
import logging
from datetime import datetime
from paper_trading import run_paper_trading
from config_manager import ConfigManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for paper trading runner"""
    parser = argparse.ArgumentParser(description='Paper Trading Bot Runner')
    parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    parser.add_argument('--exchange', type=str, default='NSE', help='Exchange (for stocks)')
    parser.add_argument('--capital', type=float, required=True, help='Trading capital')
    parser.add_argument('--risk', type=float, required=True, help='Risk per trade (as decimal)')
    parser.add_argument('--crypto', action='store_true', help='Crypto mode')

    args = parser.parse_args()

    logger.info("="*80)
    logger.info("PAPER TRADING BOT STARTED")
    logger.info("="*80)
    logger.info(f"Symbol: {args.symbol}")
    if not args.crypto:
        logger.info(f"Exchange: {args.exchange}")
    logger.info(f"Capital: {args.capital}")
    logger.info(f"Risk per Trade: {args.risk*100}%")
    logger.info(f"Mode: {'Crypto' if args.crypto else 'Stocks'}")
    logger.info("="*80)

    try:
        # Run paper trading
        if args.crypto:
            logger.info(f"Starting crypto paper trading for {args.symbol}")
            logger.info("Note: Crypto paper trading simulation")
            # For crypto, we'll simulate paper trading
            simulate_paper_trading(args.symbol, args.capital, args.risk, crypto=True)
        else:
            logger.info(f"Starting stock paper trading for {args.symbol} on {args.exchange}")
            run_paper_trading(
                symbol=args.symbol,
                exchange=args.exchange,
                capital=args.capital
            )

    except KeyboardInterrupt:
        logger.info("\nPaper trading stopped by user")
    except Exception as e:
        logger.error(f"Error in paper trading: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Paper trading session ended")


def simulate_paper_trading(symbol, capital, risk, crypto=False):
    """
    Simulate paper trading for demonstration
    In real implementation, this would connect to actual data sources
    """
    from ema_algo_trading import EMAStrategy
    import pandas as pd
    import numpy as np

    logger.info(f"Initializing paper trading simulation...")

    strategy = EMAStrategy(capital=capital, risk_per_trade=risk)

    # Simulation loop
    iteration = 0
    max_iterations = 1000  # Run for a while

    logger.info("Starting trading simulation...")
    logger.info("Monitoring market data and generating signals...")

    while iteration < max_iterations:
        try:
            iteration += 1

            # Simulate waiting for new candle
            if iteration % 10 == 0:
                logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring {symbol}... "
                          f"(Iteration {iteration})")
                logger.info(f"  Current Position: {strategy.position if strategy.position else 'None'}")
                logger.info(f"  Capital: ${capital:,.2f}")

            # In a real implementation, you would:
            # 1. Fetch real market data
            # 2. Update strategy with new candle
            # 3. Check for entry/exit signals
            # 4. Execute trades

            time.sleep(30)  # Wait 30 seconds between iterations

        except KeyboardInterrupt:
            logger.info("Stopping paper trading...")
            break
        except Exception as e:
            logger.error(f"Error in simulation loop: {str(e)}")
            time.sleep(60)

    logger.info("Paper trading simulation ended")


if __name__ == "__main__":
    main()
