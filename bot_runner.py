"""
Bot Runner - Manages background trading bot execution
Handles starting, stopping, and monitoring the trading bot
"""

import os
import sys
import subprocess
import signal
import time
import logging
from datetime import datetime
from pathlib import Path
from config_manager import ConfigManager


class BotRunner:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.pid_file = 'bot.pid'
        self.log_file = 'bot.log'
        self.status_file = 'bot_status.txt'

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def is_running(self):
        """Check if bot is currently running"""
        if not os.path.exists(self.pid_file):
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process is actually running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                return True
            except OSError:
                # Process doesn't exist, clean up stale PID file
                os.remove(self.pid_file)
                return False
        except:
            return False

    def get_bot_pid(self):
        """Get the PID of the running bot"""
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
            except:
                return None
        return None

    def start_paper_trading(self):
        """Start paper trading in background"""
        if self.is_running():
            self.logger.warning("Bot is already running")
            return False, "Bot is already running"

        try:
            market_config = self.config_manager.get_market_config()
            trading_config = self.config_manager.get_trading_config()

            self.logger.info("="*60)
            self.logger.info("STARTING PAPER TRADING BOT")
            self.logger.info("="*60)
            self.logger.info(f"Market Type: {market_config['market_type']}")

            if market_config['market_type'] == 'stocks':
                symbol = market_config['symbol']
                exchange = market_config['exchange']
                self.logger.info(f"Symbol: {symbol}")
                self.logger.info(f"Exchange: {exchange}")
            else:
                symbol = market_config['symbol']
                self.logger.info(f"Pair: {symbol}")

            self.logger.info(f"Capital: {trading_config['capital']}")
            self.logger.info(f"Risk per Trade: {trading_config['risk_per_trade']*100}%")
            self.logger.info("="*60)

            # Create bot script command
            if market_config['market_type'] == 'stocks':
                cmd = [
                    sys.executable,
                    'paper_trading_runner.py',
                    '--symbol', market_config['symbol'],
                    '--exchange', market_config['exchange'],
                    '--capital', str(trading_config['capital']),
                    '--risk', str(trading_config['risk_per_trade'])
                ]
            else:
                cmd = [
                    sys.executable,
                    'paper_trading_runner.py',
                    '--symbol', market_config['symbol'],
                    '--capital', str(trading_config['capital']),
                    '--risk', str(trading_config['risk_per_trade']),
                    '--crypto'
                ]

            # Start the bot process
            process = subprocess.Popen(
                cmd,
                stdout=open('bot_output.log', 'w'),
                stderr=subprocess.STDOUT,
                start_new_session=True  # Detach from parent
            )

            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Update status
            self.update_status('running', 'paper')

            self.logger.info(f"Bot started with PID: {process.pid}")
            return True, f"Paper trading bot started successfully (PID: {process.pid})"

        except Exception as e:
            self.logger.error(f"Error starting bot: {str(e)}")
            return False, f"Error starting bot: {str(e)}"

    def start_live_trading(self):
        """Start live trading in background"""
        if self.is_running():
            self.logger.warning("Bot is already running")
            return False, "Bot is already running"

        try:
            market_config = self.config_manager.get_market_config()
            trading_config = self.config_manager.get_trading_config()

            self.logger.info("="*60)
            self.logger.info("STARTING LIVE TRADING BOT - REAL MONEY!")
            self.logger.info("="*60)
            self.logger.info(f"Market Type: {market_config['market_type']}")

            # Create appropriate command based on market type
            if market_config['market_type'] == 'stocks':
                cmd = [
                    sys.executable,
                    'live_trading_runner.py',
                    '--stocks',
                    '--symbol', market_config['symbol'],
                    '--exchange', market_config['exchange'],
                    '--capital', str(trading_config['capital'])
                ]
            else:
                cmd = [
                    sys.executable,
                    'live_trading_runner.py',
                    '--crypto',
                    '--symbol', market_config['symbol'],
                    '--capital', str(trading_config['capital'])
                ]

            # Start the bot process
            process = subprocess.Popen(
                cmd,
                stdout=open('bot_output.log', 'w'),
                stderr=subprocess.STDOUT,
                start_new_session=True
            )

            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))

            # Update status
            self.update_status('running', 'live')

            self.logger.info(f"Live trading bot started with PID: {process.pid}")
            return True, f"Live trading bot started (PID: {process.pid})"

        except Exception as e:
            self.logger.error(f"Error starting live bot: {str(e)}")
            return False, f"Error: {str(e)}"

    def stop_bot(self):
        """Stop the running bot"""
        if not self.is_running():
            return False, "No bot is currently running"

        try:
            pid = self.get_bot_pid()

            self.logger.info(f"Stopping bot (PID: {pid})...")

            # Send SIGTERM for graceful shutdown
            os.kill(pid, signal.SIGTERM)

            # Wait for process to stop (max 10 seconds)
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except OSError:
                    # Process has stopped
                    break

            # If still running, force kill
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass  # Already stopped

            # Clean up
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)

            self.update_status('stopped', '')

            self.logger.info("Bot stopped successfully")
            return True, "Bot stopped successfully"

        except Exception as e:
            self.logger.error(f"Error stopping bot: {str(e)}")
            return False, f"Error: {str(e)}"

    def get_status(self):
        """Get current bot status"""
        if self.is_running():
            try:
                with open(self.status_file, 'r') as f:
                    lines = f.readlines()
                    mode = lines[1].strip() if len(lines) > 1 else 'unknown'
                    return 'running', mode
            except:
                return 'running', 'unknown'
        else:
            return 'stopped', ''

    def update_status(self, status, mode):
        """Update bot status file"""
        with open(self.status_file, 'w') as f:
            f.write(f"{status}\n")
            f.write(f"{mode}\n")
            f.write(f"{datetime.now()}\n")

    def get_logs(self, lines=50):
        """Get recent log entries"""
        if not os.path.exists(self.log_file):
            return []

        try:
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except:
            return []

    def get_output_logs(self, lines=50):
        """Get bot output logs"""
        output_file = 'bot_output.log'
        if not os.path.exists(output_file):
            return []

        try:
            with open(output_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except:
            return []

    def clear_logs(self):
        """Clear all log files"""
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
            if os.path.exists('bot_output.log'):
                os.remove('bot_output.log')
            self.setup_logging()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing logs: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the bot runner
    runner = BotRunner()

    print("Bot Runner Test")
    print("="*60)
    print(f"Is running: {runner.is_running()}")

    status, mode = runner.get_status()
    print(f"Status: {status}")
    print(f"Mode: {mode}")

    logs = runner.get_logs(10)
    print(f"\nRecent logs ({len(logs)} lines):")
    for log in logs:
        print(log.strip())
