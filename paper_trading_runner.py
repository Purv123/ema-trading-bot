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
    Simulate realistic paper trading with price generation and signal detection
    """
    from ema_algo_trading import EMAStrategy
    import pandas as pd
    import numpy as np

    logger.info(f"Initializing paper trading bot...")
    logger.info(f"💰 Starting Capital: ${capital:,.2f}")
    logger.info(f"⚠️  Risk per Trade: {risk*100}%")
    logger.info("")

    strategy = EMAStrategy(capital=capital, risk_per_trade=risk)

    # Initialize price tracking
    base_price = 3000 if symbol.startswith('ETH') else 50000 if symbol.startswith('BTC') else 100
    prices = []
    timestamps = []

    # Generate initial historical data for EMA calculation
    logger.info("📊 Generating initial market data for analysis...")
    np.random.seed(int(time.time()) % 10000)

    for i in range(50):
        # Random walk for realistic price movement
        change = np.random.randn() * (base_price * 0.01)
        base_price = max(base_price + change, base_price * 0.5)
        prices.append(base_price)
        timestamps.append(datetime.now())

    logger.info(f"✅ Initialized with 50 candles. Current price: ${base_price:,.2f}")
    logger.info("")
    logger.info("="*80)
    logger.info("🤖 BOT IS NOW LIVE - Monitoring market for trading signals...")
    logger.info("="*80)
    logger.info("")

    iteration = 0
    trades_count = 0

    while iteration < 1000:
        try:
            iteration += 1
            current_time = datetime.now().strftime('%H:%M:%S')

            # Generate new realistic price (random walk)
            price_change_pct = np.random.randn() * 0.5  # 0.5% volatility
            price_change = base_price * (price_change_pct / 100)
            base_price = max(base_price + price_change, base_price * 0.8)

            prices.append(base_price)
            timestamps.append(datetime.now())

            # Keep only last 100 candles
            if len(prices) > 100:
                prices = prices[-100:]
                timestamps = timestamps[-100:]

            # Create DataFrame for analysis
            df = pd.DataFrame({
                'timestamp': timestamps,
                'close': prices,
                'open': [p * (1 + np.random.randn() * 0.001) for p in prices],
                'high': [p * (1 + abs(np.random.randn() * 0.005)) for p in prices],
                'low': [p * (1 - abs(np.random.randn() * 0.005)) for p in prices],
                'volume': [np.random.randint(1000, 10000) for _ in prices]
            })

            # Calculate indicators
            df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
            df['ema_15'] = df['close'].ewm(span=15, adjust=False).mean()

            # Calculate RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            current_price = df['close'].iloc[-1]
            ema_9 = df['ema_9'].iloc[-1]
            ema_15 = df['ema_15'].iloc[-1]
            rsi = df['rsi'].iloc[-1]

            # Log every 5 iterations (every ~2.5 minutes)
            if iteration % 5 == 0:
                logger.info(f"⏰ [{current_time}] Market Update:")
                logger.info(f"   💵 Price: ${current_price:,.2f} ({price_change:+.2f}, {price_change_pct:+.2f}%)")
                logger.info(f"   📈 EMA-9: ${ema_9:,.2f} | EMA-15: ${ema_15:,.2f}")
                logger.info(f"   📊 RSI: {rsi:.1f}")
                logger.info(f"   🎯 Position: {strategy.position if strategy.position else 'None (Looking for entry)'}")
                logger.info("")

            # Check for exit if in position
            if strategy.position:
                should_exit = strategy.check_exit_conditions(df)

                if should_exit:
                    exit_price = current_price
                    pnl = (exit_price - strategy.entry_price) if strategy.position == 'LONG' else (strategy.entry_price - exit_price)
                    pnl_pct = (pnl / strategy.entry_price) * 100

                    logger.info("🚪 EXIT SIGNAL DETECTED!")
                    logger.info(f"   Exit Price: ${exit_price:,.2f}")
                    logger.info(f"   Entry was: ${strategy.entry_price:,.2f}")
                    logger.info(f"   P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%)")

                    strategy.exit_trade(df)
                    trades_count += 1

                    logger.info(f"   ✅ Position CLOSED - Total Trades: {trades_count}")
                    logger.info("")

            # Check for entry signals
            if strategy.position is None:
                signal = strategy.generate_signal(df)

                if signal:
                    entry_price = current_price
                    stop_loss, target = strategy.calculate_stop_loss_target(df, signal)

                    logger.info("="*80)
                    logger.info(f"🎯 {'BUY' if signal == 'BUY' else 'SELL'} SIGNAL GENERATED!")
                    logger.info("="*80)
                    logger.info(f"   📍 Entry Price: ${entry_price:,.2f}")
                    logger.info(f"   🛡️  Stop Loss: ${stop_loss:,.2f} ({abs((stop_loss-entry_price)/entry_price*100):.2f}% away)")
                    logger.info(f"   🎯 Target: ${target:,.2f} ({abs((target-entry_price)/entry_price*100):.2f}% away)")
                    logger.info(f"   📊 Risk:Reward = 1:2")
                    logger.info(f"   💰 Capital at Risk: ${capital * risk:,.2f}")

                    strategy.execute_trade(signal, df)
                    trades_count += 1

                    logger.info(f"   ✅ {'LONG' if signal == 'BUY' else 'SHORT'} position OPENED")
                    logger.info("="*80)
                    logger.info("")

            # Wait 30 seconds before next iteration (simulates 30s candles)
            time.sleep(30)

        except KeyboardInterrupt:
            logger.info("")
            logger.info("⏸️  Stopping paper trading...")
            break
        except Exception as e:
            logger.error(f"❌ Error in trading loop: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            time.sleep(60)

    logger.info("")
    logger.info("="*80)
    logger.info("📊 PAPER TRADING SESSION ENDED")
    logger.info("="*80)
    logger.info(f"Total Trades Executed: {trades_count}")
    logger.info(f"Final Capital: ${capital:,.2f}")
    logger.info("")


if __name__ == "__main__":
    main()
