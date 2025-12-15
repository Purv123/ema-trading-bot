"""
Live Trading Runner
Executes live trading bot with real money
"""

import argparse
import sys
import logging
from datetime import datetime
from config_manager import ConfigManager
from angel_one_live_trading import run_live_trading_angel_one
from mudrex_crypto_trading import run_crypto_trading

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
    """Main entry point for live trading runner"""
    parser = argparse.ArgumentParser(description='Live Trading Bot Runner')
    parser.add_argument('--stocks', action='store_true', help='Stock trading mode')
    parser.add_argument('--crypto', action='store_true', help='Crypto trading mode')
    parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
    parser.add_argument('--exchange', type=str, default='NSE', help='Exchange (for stocks)')
    parser.add_argument('--capital', type=float, required=True, help='Trading capital')

    args = parser.parse_args()

    # Load configuration
    config = ConfigManager()
    market_config = config.get_market_config()
    trading_config = config.get_trading_config()

    logger.info("="*80)
    logger.info("⚠️  LIVE TRADING BOT STARTED - REAL MONEY! ⚠️")
    logger.info("="*80)
    logger.info(f"Symbol: {args.symbol}")
    logger.info(f"Capital: {args.capital}")
    logger.info(f"Risk per Trade: {trading_config['risk_per_trade']*100}%")
    logger.info("="*80)

    try:
        if args.stocks:
            # Stock market live trading
            logger.info("Starting live stock trading with Angel One...")

            api_key = market_config.get('api_key', '')
            client_code = market_config.get('client_code', '')
            password = market_config.get('password', '')
            totp_secret = market_config.get('totp_secret', '')

            if not api_key or api_key == '':
                logger.error("API credentials not configured!")
                logger.error("Please configure your API credentials in Settings")
                return

            run_live_trading_angel_one(
                api_key=api_key,
                client_code=client_code,
                password=password,
                totp_secret=totp_secret,
                symbol=args.symbol,
                exchange=args.exchange,
                capital=args.capital
            )

        elif args.crypto:
            # Crypto live trading
            logger.info("Starting live crypto trading...")

            api_key = market_config.get('api_key', '')
            api_secret = market_config.get('api_secret', '')

            if not api_key or api_key == '':
                logger.error("API credentials not configured!")
                logger.error("Please configure your API credentials in Settings")
                return

            run_crypto_trading(
                api_key=api_key,
                api_secret=api_secret,
                symbol=args.symbol,
                capital=args.capital,
                risk_per_trade=trading_config['risk_per_trade']
            )

        else:
            logger.error("Please specify --stocks or --crypto")

    except KeyboardInterrupt:
        logger.info("\nLive trading stopped by user")
    except Exception as e:
        logger.error(f"Error in live trading: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Live trading session ended")


if __name__ == "__main__":
    main()
