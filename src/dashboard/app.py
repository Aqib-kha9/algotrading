import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="QuantAlgo | BTC Session Breakout",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS (PREMIUM DARK THEME)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #050505;
        color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #1f1f1f;
    }
    
    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #00ff9d !important; /* Neon Green */
    }
    div[data-testid="stMetricLabel"] {
        color: #888888;
        font-size: 0.9rem;
    }
    
    /* Custom Card Style */
    .card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    h1 {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Tables */
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
        border-radius: 5px;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #1f1f1f;
        color: #fff;
        border: 1px solid #333;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #00ff9d;
        color: #00ff9d;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------------------------------------------
@st.cache_data
def load_exchange_data(exchange):
    path = f'data/results/{exchange.lower()}_results.csv'
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_comp_data():
    comp_data = []
    for ex in ["Delta", "Exness"]:
        df = load_exchange_data(ex)
        if not df.empty:
            net_pnl = df['pnl_pct'].sum()
            win_rate = (len(df[df['pnl_pct'] > 0]) / len(df) * 100) if len(df) > 0 else 0
            comp_data.append({
                "Exchange": ex,
                "Net PnL (%)": round(net_pnl, 2),
                "Win Rate (%)": round(win_rate, 2),
                "Trades": len(df)
            })
    return pd.DataFrame(comp_data)

def to_excel(df):
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Trades')
    return output.getvalue()

# -----------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png?v=025", width=50)
st.sidebar.title("QuantAlgo Pro")
st.sidebar.caption("Institutional Grade Bot")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation", 
    ["Dashboard Overview", "Strategy DNA", "Performance Analytics", "Exchange Intelligence", "Live Operations"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
selected_exchange = st.sidebar.selectbox("Select Exchange Venue", ["Delta", "Exness"])
st.sidebar.info(f"Connected: 🟢 {selected_exchange}")

# -----------------------------------------------------------------------------
# 5. MAIN CONTENT
# -----------------------------------------------------------------------------

if menu == "Dashboard Overview":
    st.title("⚡ Executive Dashboard")
    st.markdown("Real-time overview of system health and aggregate performance.")
    
    # KPIs
    df = load_exchange_data(selected_exchange)
    if not df.empty:
        net_pnl = df['pnl_pct'].sum()
        total_trades = len(df)
        win_rate = (len(df[df['pnl_pct'] > 0]) / total_trades * 100) if total_trades > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(f"Net Profit ({selected_exchange})", f"{net_pnl:.2f}%", f"{total_trades} trades")
        with col2:
            st.metric("Win Rate", f"{win_rate:.2f}%")
        with col3:
            st.metric("Avg Trade PnL", f"{(net_pnl/total_trades):.3f}%" if total_trades > 0 else "0%")
        with col4:
            st.download_button(
                label="📥 Export to Excel",
                data=to_excel(df),
                file_name=f"{selected_exchange}_backtest_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        # Main Chart
        st.markdown(f"### 📈 Equity Growth ({selected_exchange})")
        df['cumulative_pnl'] = df['pnl_pct'].cumsum()
        fig = px.area(df, x='entry_time', y='cumulative_pnl', title=None)
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#888'},
            xaxis_showgrid=False,
            yaxis_showgrid=True,
            yaxis_gridcolor='#222',
            margin=dict(l=0, r=0, t=20, b=0),
            height=350
        )
        fig.update_traces(line_color='#00ff9d', fillcolor='rgba(0, 255, 157, 0.1)')
        st.plotly_chart(fig, width="stretch")
        
        # Recent Activity
        st.markdown("### 🕒 Recent Signals")
        st.dataframe(
            df.tail(10)[['entry_time', 'type', 'entry_price', 'exit_price', 'pnl_pct', 'reason']], 
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning(f"No backtest results found for {selected_exchange}. Please run the backtest first.")

elif menu == "Strategy DNA":
    st.title("🧬 Strategy DNA")
    st.markdown("### BTC Session Breakout v1.0")
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("""
        <div class="card">
            <h3>Core Logic</h3>
            <p>The strategy exploits volatility breakouts following the Asian market opening session.</p>
            <ul>
                <li><strong>Asset:</strong> BTCUSD</li>
                <li><strong>Data Source:</strong> Exness (5M Timeframe)</li>
                <li><strong>Session Window:</strong> 02:45 - 03:55 UTC</li>
                <li><strong>Mid-Price Logic:</strong> (Bid + Spread/2)</li>
                <li><strong>Entry:</strong> 0.05% Buffer on Session High/Low</li>
                <li><strong>Targets:</strong> TP 0.70% / SL 0.30%</li>
                <li><strong>Exit:</strong> End of day (13:40 UTC)</li>
                <li><strong>TSL:</strong> +0.40% activation, +0.20% trailing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="card">
            <h3>Parameters</h3>
            <code>Timeframe: 5m</code><br>
            <code>Stop Loss: 0.30%</code><br>
            <code>Take Profit: 0.70%</code><br>
            <code>Trailing Start: 0.40%</code><br>
            <code>Trailing Step: Breakeven/-0.20% (Buy)</code>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Graphical Logic Representation")
    # Mock visual of logic
    dates = pd.date_range("2023-01-01 08:00", periods=20, freq="5min")
    prices = [100, 101, 102, 101, 100, 102, 104, 105, 106, 105, 106, 107, 108, 108, 107, 106, 105, 104, 103, 102]
    mock_df = pd.DataFrame({'Time': dates, 'Price': prices})
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mock_df['Time'], y=mock_df['Price'], mode='lines', name='Price', line=dict(color='white')))
    # Add box for session
    fig.add_shape(type="rect",
        x0=dates[3], y0=100, x1=dates[15], y1=102,
        line=dict(color="RoyalBlue"), fillcolor="rgba(65, 105, 225, 0.2)",
    )
    fig.add_annotation(x=dates[9], y=101, text="Session Range", showarrow=False, font=dict(color="white"))
    
    fig.update_layout(
        title="Session Capture Visualization (Mock)", 
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(fig, width="stretch")

elif menu == "Performance Analytics":
    st.title("📊 Deep Dive Analytics")
    
    df = load_exchange_data(selected_exchange)
    if df.empty:
        st.error(f"No backtest data found for {selected_exchange}.")
    else:
        # Filter
        st.markdown('<div class="card">', unsafe_allow_html=True)
        days = st.slider("Filter Trade Count (Last N Trades)", 30, len(df), len(df))
        st.markdown('</div>', unsafe_allow_html=True)
        
        subset = df.tail(days) 
        
        # PnL Distribution
        fig_dist = px.histogram(subset, x="pnl_pct", nbins=50, title=f"PnL Distribution ({selected_exchange})", color_discrete_sequence=['#00ff9d'])
        fig_dist.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Streak Analysis
        st.markdown("### 🎲 Streak Analysis")
        
        # Calculate streaks
        df['win'] = df['pnl_pct'] > 0
        df['streak_id'] = (df['win'] != df['win'].shift()).cumsum()
        streaks = df.groupby(['streak_id', 'win']).size().reset_index(name='count')
        
        max_win_streak = streaks[streaks['win'] == True]['count'].max() if not streaks[streaks['win'] == True].empty else 0
        max_loss_streak = streaks[streaks['win'] == False]['count'].max() if not streaks[streaks['win'] == False].empty else 0
        
        # Current Streak
        current_streak_val = streaks.iloc[-1]['count']
        current_type = "Win" if streaks.iloc[-1]['win'] else "Loss"
        
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("Max Win Streak", f"{max_win_streak} Trades", "🚀 Momentum")
        with s2:
            st.metric("Max Loss Streak", f"{max_loss_streak} Trades", "⚠️ Risk Check", delta_color="inverse")
        with s3:
            st.metric("Current Streak", f"{current_streak_val} {current_type}s")

elif menu == "Exchange Intelligence":
    st.title("⚖️ Exchange Intelligence")
    st.markdown("Comparative analysis of strategy performance across liquidity venues.")
    
    df_comp = load_comp_data()
    if not df_comp.empty:
        best = df_comp.loc[df_comp['Net PnL (%)'].idxmax()]
        
        st.markdown(f"""
        <div class="card" style="border: 1px solid #00ff9d; background: rgba(0, 255, 157, 0.05);">
            <center>
                <h2>🏆 Recommended Venue: {best['Exchange']}</h2>
                <p>Projected Net Profit: <strong>{best['Net PnL (%)']}%</strong> | Win Rate: <strong>{best['Win Rate (%)']}%</strong></p>
            </center>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.table(df_comp)
        with col2:
            fig = px.bar(df_comp, x='Exchange', y='Net PnL (%)', color='Net PnL (%)', color_continuous_scale='Bluered_r')
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please run Phase 4 Simulation to view this data.")

elif menu == "Live Operations":
    st.title("🔴 Live Operations Center")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><h3>Active Position</h3><h1>NONE</h1></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h3>Daily PnL</h3><h1 style="color: grey;">$0.00</h1></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><h3>Next Session</h3><h1>14h 32m</h1></div>', unsafe_allow_html=True)
        
    st.markdown("### Terminal Output")
    st.code("""
    [2026-01-03 15:55:01] INFO: TradingBot Started.
    [2026-01-03 15:55:02] INFO: Connected to Binance API.
    [2026-01-03 15:55:05] INFO: Waiting for Session Start (08:15 IST)... (Currently Outside Session)
    """, language="log")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("⛔ EMERGENCY STOP", type="primary", use_container_width=True)
    with col_b:
        st.button("♻️ RESTART BOT", use_container_width=True)
