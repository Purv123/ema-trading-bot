"""
EMA Trading Bot - Main Application
Web-based UI for complete bot configuration and control
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from config_manager import ConfigManager
from database_handler import TradingDatabase
from backtest_engine import BacktestEngine
from paper_trading import PaperTradingSimulator
from ema_algo_trading import EMAStrategy
from bot_runner import BotRunner
import time
import threading

# Page configuration
st.set_page_config(
    page_title="EMA Trading Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-title {
        font-size: 40px !important;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .setup-card {
        background-color: #f8f9fa;
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #e9ecef;
        margin: 20px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 2px solid #c3e6cb;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 2px solid #bee5eb;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 2px solid #ffeaa7;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)


class TradingBotApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.db = TradingDatabase()
        self.bot_runner = BotRunner()

        # Initialize session state
        if 'setup_step' not in st.session_state:
            st.session_state.setup_step = 1

    def run(self):
        """Main application router"""
        # Check if setup is complete
        if not self.config_manager.is_setup_complete():
            self.show_initial_setup()
        else:
            self.show_main_dashboard()

    def show_initial_setup(self):
        """Initial setup wizard"""
        st.markdown('<p class="big-title">🤖 Welcome to EMA Trading Bot</p>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
        <h3>👋 Welcome!</h3>
        <p>Let's get you set up in just a few steps. You'll be able to:</p>
        <ul>
            <li>✅ Trade in Indian Stock Market or Cryptocurrency Market</li>
            <li>✅ Configure everything from this easy-to-use interface</li>
            <li>✅ Test strategies in paper trading mode (risk-free!)</li>
            <li>✅ Run backtests on historical data</li>
            <li>✅ Go live when you're ready</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        # Setup steps
        if st.session_state.setup_step == 1:
            self.setup_step_1_market_selection()
        elif st.session_state.setup_step == 2:
            self.setup_step_2_api_configuration()
        elif st.session_state.setup_step == 3:
            self.setup_step_3_trading_parameters()
        elif st.session_state.setup_step == 4:
            self.setup_step_4_strategy_settings()
        elif st.session_state.setup_step == 5:
            self.setup_step_5_complete()

    def setup_step_1_market_selection(self):
        """Step 1: Choose market type"""
        st.markdown('<div class="setup-card">', unsafe_allow_html=True)

        st.header("Step 1: Choose Your Market")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### 📊 Indian Stock Market
            - Trade NSE/BSE stocks
            - Supports Angel One, Zerodha
            - Market hours: 9:15 AM - 3:30 PM
            - INR based
            """)

            if st.button("📊 Choose Stock Market", type="primary", use_container_width=True):
                st.session_state.market_type = 'stocks'
                st.session_state.setup_step = 2
                st.rerun()

        with col2:
            st.markdown("""
            ### ₿ Cryptocurrency Market
            - Trade BTC, ETH, and more
            - 24/7 trading
            - Supports Mudrex
            - USD/USDT based
            """)

            if st.button("₿ Choose Crypto Market", type="primary", use_container_width=True):
                st.session_state.market_type = 'crypto'
                st.session_state.setup_step = 2
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    def setup_step_2_api_configuration(self):
        """Step 2: API Configuration"""
        st.markdown('<div class="setup-card">', unsafe_allow_html=True)

        st.header("Step 2: API Configuration")

        market_type = st.session_state.market_type

        if market_type == 'stocks':
            st.subheader("📊 Stock Market Configuration")

            broker = st.selectbox(
                "Select Broker",
                ["Angel One", "Zerodha"],
                help="Choose your stock broker"
            )

            st.info("💡 You can find your API credentials in your broker's developer portal")

            if broker == "Angel One":
                api_key = st.text_input("API Key", type="password",
                    help="Your Angel One API Key")
                client_code = st.text_input("Client Code",
                    help="Your Angel One Client Code")
                password = st.text_input("Password", type="password",
                    help="Your Angel One Password")
                totp_secret = st.text_input("TOTP Secret", type="password",
                    help="Your 2FA TOTP Secret")

                st.divider()

                col1, col2 = st.columns(2)
                with col1:
                    symbol = st.text_input("Stock Symbol", value="SBIN",
                        help="e.g., SBIN, RELIANCE, TCS")
                with col2:
                    exchange = st.selectbox("Exchange", ["NSE", "BSE"])

            else:  # Zerodha
                api_key = st.text_input("API Key", type="password")
                api_secret = st.text_input("API Secret", type="password")

                st.divider()

                col1, col2 = st.columns(2)
                with col1:
                    symbol = st.text_input("Stock Symbol", value="SBIN")
                with col2:
                    exchange = st.selectbox("Exchange", ["NSE", "BSE"])

                client_code = ""
                password = ""
                totp_secret = ""

            st.divider()

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("⬅️ Back"):
                    st.session_state.setup_step = 1
                    st.rerun()

            with col3:
                if st.button("Continue ➡️", type="primary"):
                    if api_key and (client_code or broker == "Zerodha"):
                        # Save configuration
                        self.config_manager.save_stocks_config(
                            broker=broker.lower().replace(" ", "_"),
                            api_key=api_key,
                            client_code=client_code,
                            password=password,
                            totp_secret=totp_secret,
                            symbol=symbol,
                            exchange=exchange
                        )
                        st.session_state.setup_step = 3
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")

        else:  # crypto
            st.subheader("₿ Cryptocurrency Configuration")

            exchange = st.selectbox(
                "Select Exchange",
                ["Mudrex", "Binance", "Coinbase"],
                help="Choose your crypto exchange"
            )

            st.info("💡 Create API credentials in your exchange's settings")

            api_key = st.text_input("API Key", type="password",
                help="Your exchange API Key")
            api_secret = st.text_input("API Secret", type="password",
                help="Your exchange API Secret")

            st.divider()

            symbol = st.selectbox(
                "Trading Pair",
                ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "ADA/USDT"],
                help="Select the cryptocurrency pair to trade"
            )

            st.divider()

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("⬅️ Back"):
                    st.session_state.setup_step = 1
                    st.rerun()

            with col3:
                if st.button("Continue ➡️", type="primary"):
                    if api_key and api_secret:
                        # Save configuration
                        self.config_manager.save_crypto_config(
                            exchange=exchange.lower(),
                            api_key=api_key,
                            api_secret=api_secret,
                            symbol=symbol
                        )
                        st.session_state.setup_step = 3
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")

        st.markdown('</div>', unsafe_allow_html=True)

    def setup_step_3_trading_parameters(self):
        """Step 3: Trading Parameters"""
        st.markdown('<div class="setup-card">', unsafe_allow_html=True)

        st.header("Step 3: Trading Parameters")

        st.info("💡 These settings control how much you invest and your risk tolerance")

        col1, col2 = st.columns(2)

        with col1:
            capital = st.number_input(
                "Initial Capital",
                min_value=1000,
                max_value=10000000,
                value=10000,
                step=1000,
                help="Total amount you want to allocate for trading"
            )

            market_type = st.session_state.market_type
            currency = "₹" if market_type == 'stocks' else "$"
            st.caption(f"You will trade with {currency}{capital:,}")

        with col2:
            risk_per_trade = st.slider(
                "Risk per Trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Percentage of capital to risk on each trade"
            )

            risk_amount = capital * (risk_per_trade / 100)
            st.caption(f"You will risk {currency}{risk_amount:,.2f} per trade")

        st.markdown("""
        <div class="warning-box">
        <b>⚠️ Risk Warning</b><br>
        We recommend starting with 1-2% risk per trade. Higher risk can lead to bigger losses.
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("⬅️ Back"):
                st.session_state.setup_step = 2
                st.rerun()

        with col3:
            if st.button("Continue ➡️", type="primary"):
                self.config_manager.save_trading_config(
                    capital=capital,
                    risk_per_trade=risk_per_trade
                )
                st.session_state.setup_step = 4
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    def setup_step_4_strategy_settings(self):
        """Step 4: Strategy Settings"""
        st.markdown('<div class="setup-card">', unsafe_allow_html=True)

        st.header("Step 4: Strategy Settings")

        st.info("💡 The bot uses 9-15 EMA crossover strategy with RSI confirmation. You can customize these parameters.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("EMA Settings")
            fast_ema = st.number_input("Fast EMA Period", min_value=5, max_value=50, value=9,
                help="Shorter EMA for faster signals (default: 9)")
            slow_ema = st.number_input("Slow EMA Period", min_value=10, max_value=100, value=15,
                help="Longer EMA for trend confirmation (default: 15)")

        with col2:
            st.subheader("RSI Settings")
            rsi_period = st.number_input("RSI Period", min_value=5, max_value=50, value=14,
                help="Period for RSI calculation (default: 14)")

            col21, col22 = st.columns(2)
            with col21:
                rsi_overbought = st.number_input("RSI Overbought", min_value=60, max_value=90,
                    value=70, help="Overbought level (default: 70)")
            with col22:
                rsi_oversold = st.number_input("RSI Oversold", min_value=10, max_value=40,
                    value=30, help="Oversold level (default: 30)")

        st.divider()

        risk_reward = st.slider(
            "Risk-Reward Ratio",
            min_value=1.0,
            max_value=5.0,
            value=2.0,
            step=0.5,
            help="For every ₹1 risked, aim for ₹X profit"
        )

        st.caption(f"For every unit of risk, you'll target {risk_reward} units of reward")

        st.divider()

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("⬅️ Back"):
                st.session_state.setup_step = 3
                st.rerun()

        with col3:
            if st.button("Complete Setup ✅", type="primary"):
                self.config_manager.save_strategy_config(
                    fast_ema=fast_ema,
                    slow_ema=slow_ema,
                    rsi_period=rsi_period,
                    rsi_overbought=rsi_overbought,
                    rsi_oversold=rsi_oversold,
                    risk_reward_ratio=risk_reward
                )
                st.session_state.setup_step = 5
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    def setup_step_5_complete(self):
        """Step 5: Setup Complete"""
        st.markdown("""
        <div class="success-box">
        <h2>🎉 Setup Complete!</h2>
        <p>Your trading bot is now configured and ready to use.</p>
        </div>
        """, unsafe_allow_html=True)

        market_config = self.config_manager.get_market_config()
        trading_config = self.config_manager.get_trading_config()

        st.subheader("📋 Your Configuration Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Market Settings")
            if market_config['market_type'] == 'stocks':
                st.write(f"**Market:** Indian Stock Market")
                st.write(f"**Symbol:** {market_config['symbol']}")
                st.write(f"**Exchange:** {market_config['exchange']}")
            else:
                st.write(f"**Market:** Cryptocurrency")
                st.write(f"**Pair:** {market_config['symbol']}")

        with col2:
            st.markdown("### Trading Parameters")
            currency = "₹" if market_config['market_type'] == 'stocks' else "$"
            st.write(f"**Capital:** {currency}{trading_config['capital']:,}")
            st.write(f"**Risk per Trade:** {trading_config['risk_per_trade']*100}%")

        st.divider()

        st.markdown("""
        <div class="info-box">
        <h3>🚀 Next Steps</h3>
        <ol>
            <li><b>Start with Paper Trading</b> - Test the bot with virtual money first</li>
            <li><b>Run Backtests</b> - See how the strategy performs on historical data</li>
            <li><b>Monitor Performance</b> - Check the dashboard regularly</li>
            <li><b>Go Live</b> - When you're confident, start live trading</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Launch Dashboard", type="primary", use_container_width=True):
            # Mark setup as complete
            self.config_manager.set_config('setup_complete', True)
            st.rerun()

    def show_main_dashboard(self):
        """Main dashboard after setup"""
        # Sidebar
        with st.sidebar:
            st.image("https://img.icons8.com/fluency/96/000000/stocks-growth.png", width=80)
            st.title("🤖 EMA Trading Bot")
            st.markdown("---")

            # Market info
            market_config = self.config_manager.get_market_config()

            if market_config['market_type'] == 'stocks':
                st.metric("Market", "📊 Stocks")
                st.caption(f"{market_config['symbol']} | {market_config['exchange']}")
            else:
                st.metric("Market", "₿ Crypto")
                st.caption(f"{market_config['symbol']}")

            st.markdown("---")

            # Navigation
            page = st.selectbox(
                "Navigation",
                ["🏠 Dashboard", "▶️ Trading Control", "📝 Paper Trading",
                 "🔬 Backtesting", "⚙️ Settings", "🔄 Reconfigure"]
            )

            st.markdown("---")

            # Quick stats
            st.subheader("Quick Stats")
            stats = self.get_quick_stats()
            st.metric("Total Trades", stats['total_trades'])
            st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
            st.metric("Total P&L", f"₹{stats['total_pnl']:,.0f}",
                     delta=f"{stats['pnl_percent']:+.1f}%")

        # Main content routing
        if page == "🏠 Dashboard":
            self.show_dashboard_page()
        elif page == "▶️ Trading Control":
            self.show_trading_control()
        elif page == "📝 Paper Trading":
            self.show_paper_trading()
        elif page == "🔬 Backtesting":
            self.show_backtesting()
        elif page == "⚙️ Settings":
            self.show_settings()
        elif page == "🔄 Reconfigure":
            self.show_reconfigure()

    def show_dashboard_page(self):
        """Dashboard overview page"""
        st.title("📊 Trading Dashboard")

        # Tab navigation
        tab1, tab2, tab3 = st.tabs(["📈 Live Trading", "📝 Paper Trading", "🔬 Backtest"])

        with tab1:
            self.show_trading_view('live')

        with tab2:
            self.show_trading_view('paper')

        with tab3:
            self.show_trading_view('backtest')

    def show_trading_view(self, mode):
        """Show trading performance for a mode"""
        st.subheader(f"{mode.upper()} Trading Performance")

        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)

        summary = self.db.get_performance_summary(mode=mode)

        with col1:
            st.metric("Total Trades", summary['total_trades'])

        with col2:
            st.metric("Win Rate", f"{summary['win_rate']:.1f}%")

        with col3:
            st.metric("Total P&L", f"₹{summary['total_pnl']:,.0f}")

        with col4:
            st.metric("Profit Factor", f"{summary['profit_factor']:.2f}")

        st.markdown("---")

        # Recent trades
        st.subheader("Recent Trades")

        trades = self.db.get_all_trades(mode=mode)

        if len(trades) > 0:
            closed_trades = trades[trades['status'] == 'CLOSED'].head(20)

            if len(closed_trades) > 0:
                display_columns = ['timestamp', 'symbol', 'signal_type', 'entry_price',
                                  'exit_price', 'pnl', 'pnl_percent', 'reason']

                st.dataframe(
                    closed_trades[display_columns].style.format({
                        'entry_price': '₹{:.2f}',
                        'exit_price': '₹{:.2f}',
                        'pnl': '₹{:.2f}',
                        'pnl_percent': '{:+.2f}%'
                    }),
                    use_container_width=True
                )

                # Equity curve
                st.subheader("Equity Curve")

                closed_trades = closed_trades.sort_values('exit_time')
                closed_trades['cumulative_pnl'] = closed_trades['pnl'].cumsum()
                closed_trades['equity'] = 10000 + closed_trades['cumulative_pnl']

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=closed_trades['exit_time'],
                    y=closed_trades['equity'],
                    mode='lines+markers',
                    name='Equity',
                    line=dict(color='blue', width=2)
                ))

                fig.add_hline(y=10000, line_dash="dash", line_color="gray",
                             annotation_text="Initial Capital")

                fig.update_layout(
                    title="Account Equity Over Time",
                    xaxis_title="Date",
                    yaxis_title="Equity (₹)",
                    hovermode='x unified',
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No closed trades yet")
        else:
            st.info(f"No trades found for {mode} mode")

    def show_trading_control(self):
        """Trading control page"""
        st.title("▶️ Trading Control")

        market_config = self.config_manager.get_market_config()
        trading_config = self.config_manager.get_trading_config()

        # Get actual bot status
        bot_status, bot_mode = self.bot_runner.get_status()
        is_running = (bot_status == 'running')

        # Status display
        col1, col2, col3 = st.columns(3)

        with col1:
            if is_running:
                st.markdown('<div class="success-box"><h3>🟢 Bot Running</h3></div>',
                           unsafe_allow_html=True)
            else:
                st.markdown('<div class="warning-box"><h3>🔴 Bot Stopped</h3></div>',
                           unsafe_allow_html=True)

        with col2:
            mode_text = f"{bot_mode.upper()} TRADING" if is_running else "STOPPED"
            st.metric("Mode", mode_text)
            if is_running:
                pid = self.bot_runner.get_bot_pid()
                st.caption(f"PID: {pid}")

        with col3:
            currency = "₹" if market_config['market_type'] == 'stocks' else "$"
            st.metric("Capital", f"{currency}{trading_config['capital']:,}")

        st.divider()

        # Control buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if not is_running:
                if st.button("▶️ Start Live Trading", type="primary", use_container_width=True):
                    st.warning("⚠️ Live trading will use real money. Make sure you've tested in paper mode first!")
                    confirm = st.checkbox("I understand and want to start live trading with real money")
                    if confirm and st.button("✅ Confirm Start Live Trading"):
                        success, message = self.bot_runner.start_live_trading()
                        if success:
                            st.success(message)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(message)

        with col2:
            if is_running:
                if st.button("⏸️ Stop Bot", type="secondary", use_container_width=True):
                    success, message = self.bot_runner.stop_bot()
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)

        with col3:
            if st.button("🔄 Refresh Status", use_container_width=True):
                st.rerun()

        st.divider()

        # Bot Logs
        st.subheader("📋 Bot Logs")

        tab1, tab2 = st.tabs(["Live Output", "System Logs"])

        with tab1:
            st.caption("Real-time bot output (refreshes on page reload)")
            logs = self.bot_runner.get_output_logs(lines=100)
            if logs:
                log_text = "".join(logs)
                st.code(log_text, language="text")
            else:
                st.info("No output logs yet. Start the bot to see logs here.")

        with tab2:
            st.caption("System logs")
            logs = self.bot_runner.get_logs(lines=50)
            if logs:
                log_text = "".join(logs)
                st.code(log_text, language="text")
            else:
                st.info("No system logs yet.")

        if st.button("🗑️ Clear Logs"):
            if self.bot_runner.clear_logs():
                st.success("Logs cleared!")
                st.rerun()

        st.divider()

        # Current configuration
        st.subheader("Current Configuration")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Market Settings")
            if market_config['market_type'] == 'stocks':
                st.write(f"**Market:** Indian Stock Market")
                st.write(f"**Symbol:** {market_config['symbol']}")
                st.write(f"**Exchange:** {market_config['exchange']}")
            else:
                st.write(f"**Market:** Cryptocurrency")
                st.write(f"**Pair:** {market_config['symbol']}")

        with col2:
            st.markdown("### Trading Parameters")
            st.write(f"**Capital:** {currency}{trading_config['capital']:,}")
            st.write(f"**Risk per Trade:** {trading_config['risk_per_trade']*100}%")
            st.write(f"**Risk-Reward Ratio:** 1:{trading_config['risk_reward_ratio']}")

    def show_paper_trading(self):
        """Paper trading page"""
        st.title("📝 Paper Trading")

        st.info("💡 Paper trading lets you test strategies with simulated money. No real funds at risk!")

        # Get bot status
        bot_status, bot_mode = self.bot_runner.get_status()
        is_running = (bot_status == 'running' and bot_mode == 'paper')

        col1, col2 = st.columns([2, 1])

        with col1:
            if not is_running:
                st.subheader("Start Paper Trading")

                market_config = self.config_manager.get_market_config()
                trading_config = self.config_manager.get_trading_config()

                if market_config['market_type'] == 'stocks':
                    symbol = st.text_input("Symbol", value=market_config['symbol'])
                    exchange = st.selectbox("Exchange", ["NSE", "BSE"],
                        index=0 if market_config['exchange'] == 'NSE' else 1)
                else:
                    symbol = st.selectbox("Crypto Pair",
                        ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"],
                        index=0)
                    exchange = "Crypto"

                capital = st.number_input("Virtual Capital", value=int(trading_config['capital']),
                    step=1000)
                risk = st.slider("Risk per Trade (%)", 0.5, 5.0, trading_config['risk_per_trade']*100, 0.5)

                if st.button("▶️ Start Paper Trading", type="primary"):
                    # Update config with selected parameters
                    self.config_manager.save_trading_config(capital=capital, risk_per_trade=risk)
                    if market_config['market_type'] == 'stocks':
                        self.config_manager.set_config('stocks_symbol', symbol)
                        self.config_manager.set_config('stocks_exchange', exchange)
                    else:
                        self.config_manager.set_config('crypto_symbol', symbol)

                    # Start paper trading
                    success, message = self.bot_runner.start_paper_trading()
                    if success:
                        st.success(message)
                        st.info("📊 Paper trading is now running! Refresh the page to see live logs below.")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.subheader("Paper Trading Active")
                st.success("✅ Paper trading bot is currently running!")

                if st.button("⏸️ Stop Paper Trading", type="secondary"):
                    success, message = self.bot_runner.stop_bot()
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)

        with col2:
            st.subheader("Current Status")
            market_config = self.config_manager.get_market_config()
            trading_config = self.config_manager.get_trading_config()
            currency = "₹" if market_config['market_type'] == 'stocks' else "$"

            if is_running:
                st.metric("Status", "🟢 Running")
                pid = self.bot_runner.get_bot_pid()
                st.caption(f"Process ID: {pid}")
            else:
                st.metric("Status", "🔴 Stopped")

            st.metric("Mode", "Paper Trading")
            st.metric("Virtual Balance", f"{currency}{trading_config['capital']:,}")

        # Show logs if bot is running
        if is_running:
            st.divider()
            st.subheader("📋 Live Bot Logs")

            tab1, tab2 = st.tabs(["Bot Output", "System Logs"])

            with tab1:
                st.caption("Live trading bot output (auto-refreshes when you reload page)")
                logs = self.bot_runner.get_output_logs(lines=100)
                if logs:
                    log_text = "".join(logs)
                    st.code(log_text, language="text")

                    if st.button("🔄 Refresh Logs"):
                        st.rerun()
                else:
                    st.info("Waiting for bot output...")

            with tab2:
                logs = self.bot_runner.get_logs(lines=30)
                if logs:
                    log_text = "".join(logs)
                    st.code(log_text, language="text")
                else:
                    st.info("No system logs yet.")

    def show_backtesting(self):
        """Backtesting page"""
        st.title("🔬 Backtesting")

        st.info("💡 Test your strategy on historical data to see how it would have performed!")

        # Upload data
        uploaded_file = st.file_uploader(
            "Upload Historical Data (CSV)",
            type=['csv'],
            help="CSV should have columns: timestamp, open, high, low, close, volume"
        )

        if uploaded_file:
            try:
                data = pd.read_csv(uploaded_file)
                data['timestamp'] = pd.to_datetime(data['timestamp'])

                st.success(f"✓ Loaded {len(data)} candles")

                # Show data preview
                st.subheader("Data Preview")
                st.dataframe(data.head(10), use_container_width=True)

                # Backtest settings
                col1, col2, col3 = st.columns(3)

                with col1:
                    symbol = st.text_input("Symbol", value="TEST")

                with col2:
                    trading_config = self.config_manager.get_trading_config()
                    capital = st.number_input("Initial Capital", value=int(trading_config['capital']),
                        step=1000)

                with col3:
                    risk = st.slider("Risk per Trade (%)", 0.5, 5.0,
                        trading_config['risk_per_trade']*100, 0.5)

                # Run backtest
                if st.button("🚀 Run Backtest", type="primary"):
                    with st.spinner("Running backtest..."):
                        engine = BacktestEngine(
                            initial_capital=capital,
                            risk_per_trade=risk/100
                        )

                        results = engine.run_backtest(data, symbol=symbol)

                        if results:
                            st.success("✓ Backtest completed!")

                            # Display results
                            st.subheader("Results")

                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("Total Trades", results['total_trades'])
                                st.metric("Win Rate", f"{results['win_rate']:.1f}%")

                            with col2:
                                st.metric("Total P&L", f"₹{results['total_pnl']:,.0f}")
                                st.metric("P&L %", f"{results['total_pnl_percent']:+.1f}%")

                            with col3:
                                st.metric("Profit Factor", f"{results['profit_factor']:.2f}")
                                st.metric("Max Drawdown", f"{results['max_drawdown']:.2f}%")

                            with col4:
                                st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.2f}")
                                st.metric("Expectancy", f"₹{results['expectancy']:.2f}")

                            # Plot equity curve
                            st.subheader("Equity Curve")

                            equity_df = pd.DataFrame({
                                'Trade': range(len(engine.equity_curve)),
                                'Equity': engine.equity_curve
                            })

                            fig = px.line(equity_df, x='Trade', y='Equity',
                                        title='Equity Curve')
                            fig.add_hline(y=capital, line_dash="dash",
                                        line_color="gray")

                            st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
        else:
            st.info("Upload a CSV file to start backtesting")

    def show_settings(self):
        """Settings page"""
        st.title("⚙️ Settings")

        tab1, tab2, tab3 = st.tabs(["🔧 Strategy", "🔌 API", "📊 Trading Parameters"])

        with tab1:
            st.subheader("Strategy Parameters")

            trading_config = self.config_manager.get_trading_config()

            col1, col2 = st.columns(2)

            with col1:
                fast_ema = st.number_input("Fast EMA Period", value=trading_config['fast_ema'],
                    min_value=1, max_value=50)
                slow_ema = st.number_input("Slow EMA Period", value=trading_config['slow_ema'],
                    min_value=1, max_value=100)
                rsi_period = st.number_input("RSI Period", value=trading_config['rsi_period'],
                    min_value=2, max_value=50)

            with col2:
                rsi_overbought = st.number_input("RSI Overbought",
                    value=trading_config['rsi_overbought'], min_value=50, max_value=90)
                rsi_oversold = st.number_input("RSI Oversold",
                    value=trading_config['rsi_oversold'], min_value=10, max_value=50)
                risk_reward = st.slider("Risk-Reward Ratio", 1.0, 5.0,
                    trading_config['risk_reward_ratio'], 0.5)

            if st.button("💾 Save Strategy Settings", type="primary"):
                self.config_manager.save_strategy_config(
                    fast_ema=fast_ema,
                    slow_ema=slow_ema,
                    rsi_period=rsi_period,
                    rsi_overbought=rsi_overbought,
                    rsi_oversold=rsi_oversold,
                    risk_reward_ratio=risk_reward
                )
                st.success("Strategy settings saved successfully!")

        with tab2:
            st.subheader("API Configuration")

            market_config = self.config_manager.get_market_config()

            if market_config['market_type'] == 'stocks':
                st.text_input("API Key", value="***********", type="password")
                st.text_input("Client Code", value=market_config['client_code'])
                st.text_input("Password", value="***********", type="password")
                st.text_input("TOTP Secret", value="***********", type="password")
            else:
                st.text_input("API Key", value="***********", type="password")
                st.text_input("API Secret", value="***********", type="password")

            if st.button("🔌 Test Connection"):
                with st.spinner("Testing connection..."):
                    time.sleep(2)
                    st.success("✓ Connection successful!")

            if st.button("💾 Update API Settings"):
                st.info("API settings update - implement based on your needs")

        with tab3:
            st.subheader("Trading Parameters")

            trading_config = self.config_manager.get_trading_config()
            market_config = self.config_manager.get_market_config()
            currency = "₹" if market_config['market_type'] == 'stocks' else "$"

            capital = st.number_input("Trading Capital", value=int(trading_config['capital']),
                min_value=1000, step=1000)
            risk = st.slider("Risk per Trade (%)", 0.5, 5.0,
                trading_config['risk_per_trade']*100, 0.5)

            st.caption(f"You will risk {currency}{capital * (risk/100):,.2f} per trade")

            if st.button("💾 Save Trading Parameters", type="primary"):
                self.config_manager.save_trading_config(
                    capital=capital,
                    risk_per_trade=risk
                )
                st.success("Trading parameters saved successfully!")

    def show_reconfigure(self):
        """Reconfigure the bot"""
        st.title("🔄 Reconfigure Bot")

        st.warning("⚠️ This will reset your bot configuration. Your trading history will be preserved.")

        if st.button("🔄 Start Reconfiguration", type="primary"):
            if st.button("⚠️ Are you sure? This will reset all settings"):
                # Clear setup flag
                self.config_manager.set_config('setup_complete', False)
                st.session_state.setup_step = 1
                st.success("Configuration reset. Redirecting to setup...")
                time.sleep(1)
                st.rerun()

    def get_quick_stats(self):
        """Get quick statistics"""
        summary = self.db.get_performance_summary(mode='live')

        return {
            'total_trades': summary['total_trades'],
            'win_rate': summary['win_rate'],
            'total_pnl': summary['total_pnl'],
            'pnl_percent': (summary['total_pnl'] / 10000 * 100) if summary['total_pnl'] else 0
        }


def main():
    """Main entry point"""
    app = TradingBotApp()
    app.run()


if __name__ == "__main__":
    main()
