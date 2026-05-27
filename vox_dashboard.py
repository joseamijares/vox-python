import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import sys
import os

# Add scripts path for vox_supabase_sync (local dev)
sys.path.insert(0, '/Users/jos/.hermes/scripts')

# Try local first, then fallback to same directory
try:
    from vox_supabase_sync import get_client
except ImportError:
    # Railway deployment - module in same directory
    from vox_supabase_sync import get_client

# Page config
st.set_page_config(
    page_title="VOX Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0a0a0a;
    }
    .stMetric {
        background-color: #1a1a1a;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #333;
    }
    .stDataFrame {
        background-color: #1a1a1a;
    }
    .stSidebar {
        background-color: #111111;
    }
    h1, h2, h3 {
        color: #ffffff !important;
    }
    .stMarkdown {
        color: #cccccc;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase using existing module
sb = get_client()

# Load data
@st.cache_data(ttl=60)
def load_positions():
    response = sb.table("positions").select("*").order("live_value", desc=True).execute()
    return response.data or []

@st.cache_data(ttl=300)
def load_watchlist():
    response = sb.table("watchlist").select("*").execute()
    return response.data or []

@st.cache_data(ttl=300)
def load_plays():
    response = sb.table("plays").select("*").execute()
    return response.data or []

# Load all data
positions = load_positions()
watchlist = load_watchlist()
plays = load_plays()

# Convert to DataFrame
df = pd.DataFrame(positions)

if not df.empty:
    df['live_value'] = df['live_value'].fillna(0)
    df['grade'] = df['grade'].fillna(0)

# Sidebar
st.sidebar.title("🎯 VOX Navigation")
page = st.sidebar.radio("Go to", [
    "📊 Dashboard",
    "💼 Portfolio",
    "👁️ Watchlist",
    "🎯 Plays",
    "🏦 Brokers",
    "📈 Analysis"
])

# Grade color function
def grade_color(grade):
    if grade >= 75: return "#22c55e"
    elif grade >= 60: return "#3b82f6"
    elif grade >= 50: return "#f59e0b"
    elif grade >= 30: return "#f97316"
    else: return "#ef4444"

def grade_label(grade):
    if grade >= 75: return "STRONG_BUY"
    elif grade >= 60: return "BUY"
    elif grade >= 50: return "HOLD"
    elif grade >= 30: return "WEAK"
    else: return "AVOID"

# DASHBOARD PAGE
if page == "📊 Dashboard":
    st.title("📊 VOX Command Center")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if df.empty:
        st.warning("No positions found. Run broker sync.")
    else:
        # KPIs
        total_value = df['live_value'].sum()
        total_positions = len(df)
        avg_grade = df[df['grade'] > 0]['grade'].mean() if not df.empty else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total AUM", f"${total_value:,.2f}")
        with col2:
            st.metric("Positions", total_positions)
        with col3:
            st.metric("Avg Grade", f"{avg_grade:.1f}")
        with col4:
            strong_buy = len(df[df['grade'] >= 75])
            st.metric("Strong Buy", strong_buy)
        
        # Grade distribution
        st.subheader("📊 Grade Distribution")
        
        grade_buckets = {
            'STRONG_BUY (75+)': len(df[df['grade'] >= 75]),
            'BUY (60-74)': len(df[(df['grade'] >= 60) & (df['grade'] < 75)]),
            'HOLD (50-59)': len(df[(df['grade'] >= 50) & (df['grade'] < 60)]),
            'WEAK (30-49)': len(df[(df['grade'] >= 30) & (df['grade'] < 50)]),
            'AVOID (<30)': len(df[df['grade'] < 30])
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(grade_buckets.keys()),
            values=list(grade_buckets.values()),
            hole=.4,
            marker_colors=['#22c55e', '#3b82f6', '#f59e0b', '#f97316', '#ef4444']
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Top holdings
        st.subheader("🏆 Top 10 Holdings")
        top10 = df.nlargest(10, 'live_value')[['ticker', 'live_value', 'grade', 'brokers']]
        
        fig = go.Figure(data=[
            go.Bar(
                x=top10['ticker'],
                y=top10['live_value'],
                marker_color=[grade_color(g) for g in top10['grade']],
                text=[f"${v:,.0f}" for v in top10['live_value']],
                textposition='auto'
            )
        ])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Ticker",
            yaxis_title="Value ($)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Alerts
        st.subheader("🚨 Alerts")
        low_grade = df[df['grade'] < 50].sort_values('live_value', ascending=False)
        if not low_grade.empty:
            for _, row in low_grade.head(5).iterrows():
                st.error(f"⚠️ {row['ticker']}: Grade {row['grade']} | ${row['live_value']:,.2f}")
        else:
            st.success("✅ No low-grade alerts")

# PORTFOLIO PAGE
elif page == "💼 Portfolio":
    st.title("💼 All Positions")
    
    if df.empty:
        st.warning("No positions found")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            min_grade = st.slider("Min Grade", 0, 100, 0)
        with col2:
            broker_filter = st.multiselect(
                "Broker",
                options=df['brokers'].explode().unique() if 'brokers' in df.columns else [],
                default=[]
            )
        
        # Filter
        filtered = df[df['grade'] >= min_grade]
        if broker_filter and 'brokers' in df.columns:
            filtered = filtered[filtered['brokers'].apply(lambda x: any(b in x for b in broker_filter))]
        
        # Display
        display_df = filtered[['ticker', 'shares', 'live_price', 'live_value', 'grade', 'council', 'brokers']].copy()
        display_df['grade_color'] = display_df['grade'].apply(grade_color)
        display_df['signal'] = display_df['grade'].apply(grade_label)
        
        st.dataframe(
            display_df.sort_values('live_value', ascending=False),
            column_config={
                'ticker': st.column_config.TextColumn("Ticker"),
                'shares': st.column_config.NumberColumn("Shares", format="%.4f"),
                'live_price': st.column_config.NumberColumn("Price", format="$%.2f"),
                'live_value': st.column_config.NumberColumn("Value", format="$%.2f"),
                'grade': st.column_config.NumberColumn("Grade"),
                'signal': st.column_config.TextColumn("Signal"),
                'council': st.column_config.TextColumn("Council"),
                'brokers': st.column_config.ListColumn("Brokers"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # Portfolio by broker
        st.subheader("🏦 By Broker")
        if 'brokers' in df.columns:
            broker_data = []
            for _, row in df.iterrows():
                for broker in row['brokers']:
                    broker_data.append({'broker': broker, 'value': row['live_value']})
            
            broker_df = pd.DataFrame(broker_data).groupby('broker')['value'].sum().reset_index()
            
            fig = px.pie(broker_df, values='value', names='broker', hole=0.4)
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)

# WATCHLIST PAGE
elif page == "👁️ Watchlist":
    st.title("👁️ Watchlist")
    
    if watchlist:
        wl_df = pd.DataFrame(watchlist)
        st.dataframe(
            wl_df[['ticker', 'grade', 'council', 'entry_price', 'target_price', 'stop_loss', 'status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No watchlist items")

# PLAYS PAGE
elif page == "🎯 Plays":
    st.title("🎯 Active Plays")
    
    if plays:
        plays_df = pd.DataFrame(plays)
        st.dataframe(
            plays_df[['ticker', 'action', 'shares', 'price', 'broker', 'reason']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No active plays")

# BROKERS PAGE
elif page == "🏦 Brokers":
    st.title("🏦 Broker Status")
    
    brokers = {
        'eToro': {'status': '✅', 'value': df[df['brokers'].apply(lambda x: 'eToro' in x if isinstance(x, list) else False)]['live_value'].sum() if not df.empty else 0},
        'GBM USA': {'status': '✅', 'value': df[df['brokers'].apply(lambda x: 'GBM USA' in x if isinstance(x, list) else False)]['live_value'].sum() if not df.empty else 0},
        'Binance': {'status': '✅', 'value': df[df['brokers'].apply(lambda x: 'Binance' in x if isinstance(x, list) else False)]['live_value'].sum() if not df.empty else 0},
        'Schwab': {'status': '✅', 'value': df[df['brokers'].apply(lambda x: 'Schwab' in x if isinstance(x, list) else False)]['live_value'].sum() if not df.empty else 0},
        'IBKR': {'status': '✅', 'value': df[df['brokers'].apply(lambda x: 'IBKR' in x if isinstance(x, list) else False)]['live_value'].sum() if not df.empty else 0},
    }
    
    for broker, data in brokers.items():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(f"**{broker}**")
        with col2:
            st.write(f"{data['status']} ${data['value']:,.2f}")
        with col3:
            st.button("Sync", key=f"sync_{broker}")

# ANALYSIS PAGE
elif page == "📈 Analysis":
    st.title("📈 Portfolio Analysis")
    
    if not df.empty:
        # Grade vs Value scatter
        fig = px.scatter(
            df[df['grade'] > 0],
            x='grade',
            y='live_value',
            color='grade',
            color_continuous_scale=['red', 'orange', 'yellow', 'blue', 'green'],
            hover_data=['ticker', 'council'],
            title="Grade vs Position Value"
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk analysis
        st.subheader("⚠️ Risk Analysis")
        high_risk = df[df['grade'] < 40]['live_value'].sum()
        total = df['live_value'].sum()
        risk_pct = (high_risk / total * 100) if total > 0 else 0
        
        st.metric("High Risk Exposure", f"${high_risk:,.2f}", f"{risk_pct:.1f}% of portfolio")
        
        if risk_pct > 20:
            st.error(f"⚠️ High risk exposure is {risk_pct:.1f}% — consider trimming")
        elif risk_pct > 10:
            st.warning(f"⚠️ Moderate risk exposure is {risk_pct:.1f}%")
        else:
            st.success(f"✅ Risk exposure is healthy at {risk_pct:.1f}%")
