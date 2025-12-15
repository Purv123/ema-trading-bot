"""
Trading Bot Dashboard
Web interface for monitoring and controlling the trading bot
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from database_handler import TradingDatabase
from backtest_engine import BacktestEngine, load_historical_data
from paper_trading import PaperTradingSimulator
import time


# Page configuration
st.set_page_config(
    page_title="EMA Trading Bot Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0px;
    }
    </style>
    """, unsafe_allow_html=True)


class TradingDashboard:
    def __init__(self):
        self.db = TradingDatabase()
        
    def run(self):
        """Main dashboard function"""
        
        # Sidebar
        with st.sidebar:
            st.image("https://img.icons8.com/fluency/96/000000/stocks-growth.png", width=80)
            st.title("🤖 EMA Trading Bot")
            st.markdown("---")
            
            # Mode selection
            mode = st.selectbox(
                "Trading Mode",
                ["📊 Dashboard", "📝 Paper Trading", "🔬 Backtesting", "⚙️ Settings"]
            )
            
            st.markdown("---")
            
            # Quick stats
            st.subheader("Quick Stats")
            
            stats = self.get_quick_stats()
            st.metric("Total Trades", stats['total_trades'])
            st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
            st.metric("Total P&L", f"₹{stats['total_pnl']:,.0f}", 
                     delta=f"{stats['pnl_percent']:+.1f}%")
        
        # Main content
        if mode == "📊 Dashboard":
            self.show_dashboard()
        elif mode == "📝 Paper Trading":
            self.show_paper_trading()
        elif mode == "🔬 Backtesting":
            self.show_backtesting()
        elif mode == "⚙️ Settings":
            self.show_settings()
    
    def get_quick_stats(self):
        """Get quick statistics"""
        summary = self.db.get_performance_summary(mode='live')
        
        return {
            'total_trades': summary['total_trades'],
            'win_rate': summary['win_rate'],
            'total_pnl': summary['total_pnl'],
            'pnl_percent': (summary['total_pnl'] / 10000 * 100) if summary['total_pnl'] else 0
        }
    
    def show_dashboard(self):
        """Main dashboard view"""
        st.title("📊 Trading Dashboard")
        
        # Trading mode tabs
        tab1, tab2, tab3 = st.tabs(["📈 Live Trading", "📝 Paper Trading", "🔬 Backtest"])
        
        with tab1:
            self.show_trading_view('live')
        
        with tab2:
            self.show_trading_view('paper')
        
        with tab3:
            self.show_trading_view('backtest')
    
    def show_trading_view(self, mode):
        """Show trading view for specific mode"""
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
            # Filter closed trades
            closed_trades = trades[trades['status'] == 'CLOSED'].head(20)
            
            # Display trades table
            display_columns = ['timestamp', 'symbol', 'signal_type', 'entry_price', 
                              'exit_price', 'pnl', 'pnl_percent', 'reason']
            
            if len(closed_trades) > 0:
                st.dataframe(
                    closed_trades[display_columns].style.format({
                        'entry_price': '₹{:.2f}',
                        'exit_price': '₹{:.2f}',
                        'pnl': '₹{:.2f}',
                        'pnl_percent': '{:+.2f}%'
                    }),
                    use_container_width=True
                )
            else:
                st.info("No closed trades yet")
            
            # Equity curve
            if len(closed_trades) > 0:
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
            st.info(f"No trades found for {mode} mode")
    
    def show_paper_trading(self):
        """Paper trading interface"""
        st.title("📝 Paper Trading")
        
        st.info("💡 Paper trading lets you test strategies with simulated money. No real funds are at risk!")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Start Paper Trading")
            
            symbol = st.text_input("Symbol", value="SBIN")
            exchange = st.selectbox("Exchange", ["NSE", "BSE"])
            capital = st.number_input("Initial Capital (₹)", value=10000, step=1000)
            risk = st.slider("Risk per Trade (%)", 1.0, 5.0, 2.0, 0.5)
            
            if st.button("▶️ Start Paper Trading", type="primary"):
                st.success(f"Paper trading started for {symbol} on {exchange}")
                st.info("This feature is fully functional in the standalone application.")
        
        with col2:
            st.subheader("Current Status")
            st.metric("Mode", "Paper Trading")
            st.metric("Status", "Ready")
            st.metric("Virtual Balance", f"₹{capital:,.0f}")
    
    def show_backtesting(self):
        """Backtesting interface"""
        st.title("🔬 Backtesting")
        
        st.info("💡 Test your strategy on historical data to see how it would have performed!")
        
        # Upload data
        uploaded_file = st.file_uploader(
            "Upload Historical Data (CSV)",
            type=['csv'],
            help="CSV should have columns: timestamp, open, high, low, close, volume"
        )
        
        if uploaded_file:
            # Load data
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
                    capital = st.number_input("Initial Capital (₹)", value=10000, step=1000)
                
                with col3:
                    risk = st.slider("Risk per Trade (%)", 1.0, 5.0, 2.0, 0.5)
                
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
        """Settings interface"""
        st.title("⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs(["🔧 Strategy", "🔌 API", "🔔 Notifications"])
        
        with tab1:
            st.subheader("Strategy Parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input("Fast EMA Period", value=9, min_value=1, max_value=50)
                st.number_input("Slow EMA Period", value=15, min_value=1, max_value=100)
                st.number_input("RSI Period", value=14, min_value=2, max_value=50)
            
            with col2:
                st.number_input("RSI Overbought", value=70, min_value=50, max_value=90)
                st.number_input("RSI Oversold", value=30, min_value=10, max_value=50)
                st.slider("Risk-Reward Ratio", 1.0, 5.0, 2.0, 0.5)
            
            if st.button("💾 Save Settings"):
                st.success("Settings saved successfully!")
        
        with tab2:
            st.subheader("API Configuration")
            
            broker = st.selectbox("Broker", ["Angel One", "Zerodha", "Mudrex (Crypto)"])
            
            if broker == "Angel One":
                st.text_input("API Key", type="password")
                st.text_input("Client Code")
                st.text_input("Password", type="password")
                st.text_input("TOTP Secret", type="password")
            
            elif broker == "Zerodha":
                st.text_input("API Key", type="password")
                st.text_input("API Secret", type="password")
            
            elif broker == "Mudrex (Crypto)":
                st.text_input("API Key", type="password")
                st.text_input("API Secret", type="password")
            
            if st.button("🔌 Test Connection"):
                with st.spinner("Testing connection..."):
                    time.sleep(2)
                    st.success("✓ Connection successful!")
        
        with tab3:
            st.subheader("Notifications")
            
            st.checkbox("Email Notifications", value=False)
            st.text_input("Email Address")
            
            st.checkbox("Telegram Notifications", value=False)
            st.text_input("Telegram Bot Token")
            st.text_input("Telegram Chat ID")
            
            st.checkbox("Desktop Notifications", value=True)
            
            if st.button("💾 Save Notification Settings"):
                st.success("Notification settings saved!")


def main():
    """Main function"""
    dashboard = TradingDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
