import streamlit as st
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
    from vox_supabase_sync import get_client

# Page config
st.set_page_config(
    page_title="VOX Dashboard v8",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match Vercel design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0B0E14;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: #141721 !important;
        border-right: 1px solid #30363D;
    }
    
    .stSidebar .stMarkdown {
        color: #8B949E;
    }
    
    /* Headers */
    h1 {
        color: #FFFFFF !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin-bottom: 4px !important;
    }
    
    h2 {
        color: #FFFFFF !important;
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #FFFFFF !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    /* Caption/date */
    .stCaption {
        color: #8B949E !important;
        font-size: 14px !important;
    }
    
    /* Metric cards */
    .stMetric {
        background-color: #161B22;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #30363D;
    }
    
    .stMetric label {
        color: #8B949E !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stMetric .css-1xarl3l {
        color: #FFFFFF !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        background-color: #161B22;
        border-radius: 12px;
        border: 1px solid #30363D;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #161B22;
        color: #FFFFFF;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1C2128;
        border-color: #3B82F6;
    }
    
    /* Radio buttons in sidebar */
    .stRadio > label {
        color: #8B949E !important;
        font-size: 14px !important;
    }
    
    .stRadio > div[role="radiogroup"] > label {
        background-color: transparent !important;
        border: none !important;
        color: #8B949E !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
    }
    
    .stRadio > div[role="radiogroup"] > label:hover {
        background-color: #1C2128 !important;
        color: #FFFFFF !important;
    }
    
    .stRadio > div[role="radiogroup"] > label[data-baseweb="radio"] > div:first-child {
        background-color: #3B82F6 !important;
    }
    
    /* Alert boxes */
    .stAlert {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
    }
    
    .stAlert [data-baseweb="notification"] {
        background-color: transparent !important;
    }
    
    /* Error state */
    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid #EF4444 !important;
        border-radius: 12px !important;
    }
    
    /* Success state */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1) !important;
        border: 1px solid #22C55E !important;
        border-radius: 12px !important;
    }
    
    /* Warning state */
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid #F59E0B !important;
        border-radius: 12px !important;
    }
    
    /* Info state */
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid #3B82F6 !important;
        border-radius: 12px !important;
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background-color: #3B82F6 !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
    }
    
    /* Tables */
    .stTable {
        background-color: #161B22;
        border-radius: 12px;
        border: 1px solid #30363D;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0B0E14;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #30363D;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #3B82F6;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
sb = get_client()

# Load data
@st.cache_data(ttl=60)
def load_positions():
    try:
        response = sb.table("positions").select("*").order("live_value", desc=True).execute()
        return response.data or []
    except Exception as e:
        st.error(f"Error loading positions: {e}")
        return []

@st.cache_data(ttl=300)
def load_watchlist():
    try:
        response = sb.table("watchlist").select("*").execute()
        return response.data or []
    except:
        return []

@st.cache_data(ttl=300)
def load_plays():
    try:
        response = sb.table("plays").select("*").execute()
        return response.data or []
    except:
        return []

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
st.sidebar.markdown("<h1 style='color: #3B82F6; font-size: 24px; font-weight: 800;'>VOX</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #8B949E; font-size: 12px; margin-bottom: 24px;'>v8.0 Python</p>", unsafe_allow_html=True)

page = st.sidebar.radio("", [
    "📊 Command Center",
    "💼 Portfolio",
    "👁️ Watchlist",
    "🎯 Plays",
    "🏦 Brokers",
    "📈 Analysis"
])

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='color: #8B949E; font-size: 11px;'>© 2026 VOX Systems</p>", unsafe_allow_html=True)

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

def grade_badge(grade):
    color = grade_color(grade)
    return f"<span style='background-color: {color}20; color: {color}; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;'>{grade:.0f}</span>"

# COMMAND CENTER PAGE
if page == "📊 Command Center":
    st.title("Today's Command Center")
    st.caption(f"Live from Supabase • {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    
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
        
        # Alerts section
        st.subheader("🚨 Urgent Alerts")
        low_grade = df[df['grade'] < 50].sort_values('live_value', ascending=False)
        if not low_grade.empty:
            alert_cols = st.columns(min(3, len(low_grade.head(6))))
            for idx, (_, row) in enumerate(low_grade.head(6).iterrows()):
                with alert_cols[idx % 3]:
                    st.error(f"**{row['ticker']}** — Grade {row['grade']}\n\n${row['live_value']:,.2f}")
        else:
            st.success("✅ No urgent alerts")
        
        # Main content grid
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("🏆 Top 10 Holdings")
            top10 = df.nlargest(10, 'live_value')[['ticker', 'live_value', 'grade', 'council']].copy()
            
            # Format for display
            display_data = []
            for _, row in top10.iterrows():
                display_data.append({
                    'Ticker': row['ticker'],
                    'Value': f"${row['live_value']:,.2f}",
                    'Grade': row['grade'],
                    'Signal': grade_label(row['grade']),
                    'Council': row.get('council', 'N/A')
                })
            
            top10_df = pd.DataFrame(display_data)
            st.dataframe(
                top10_df,
                column_config={
                    'Ticker': st.column_config.TextColumn("Ticker", width="small"),
                    'Value': st.column_config.TextColumn("Value", width="medium"),
                    'Grade': st.column_config.NumberColumn("Grade", width="small"),
                    'Signal': st.column_config.TextColumn("Signal", width="medium"),
                    'Council': st.column_config.TextColumn("Council", width="small"),
                },
                use_container_width=True,
                hide_index=True
            )
        
        with col_right:
            st.subheader("📊 Grade Distribution")
            
            grade_buckets = {
                'STRONG_BUY': len(df[df['grade'] >= 75]),
                'BUY': len(df[(df['grade'] >= 60) & (df['grade'] < 75)]),
                'HOLD': len(df[(df['grade'] >= 50) & (df['grade'] < 60)]),
                'WEAK': len(df[(df['grade'] >= 30) & (df['grade'] < 50)]),
                'AVOID': len(df[df['grade'] < 30])
            }
            
            grade_df = pd.DataFrame({
                'Category': list(grade_buckets.keys()),
                'Count': list(grade_buckets.values())
            })
            
            st.bar_chart(grade_df.set_index('Category'), use_container_width=True, height=200)
            
            st.subheader("🏦 By Broker")
            if 'brokers' in df.columns:
                broker_data = []
                for _, row in df.iterrows():
                    brokers = row['brokers']
                    if isinstance(brokers, list):
                        for broker in brokers:
                            broker_data.append({'broker': broker, 'value': row['live_value']})
                    elif isinstance(brokers, str):
                        broker_data.append({'broker': brokers, 'value': row['live_value']})
                
                if broker_data:
                    broker_df = pd.DataFrame(broker_data).groupby('broker')['value'].sum().reset_index()
                    broker_df = broker_df.sort_values('value', ascending=False)
                    
                    for _, row in broker_df.iterrows():
                        st.markdown(f"**{row['broker']}**: ${row['value']:,.2f}")

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
            broker_options = []
            if 'brokers' in df.columns:
                for brokers in df['brokers']:
                    if isinstance(brokers, list):
                        broker_options.extend(brokers)
                    elif isinstance(brokers, str):
                        broker_options.append(brokers)
                broker_options = list(set(broker_options))
            
            broker_filter = st.multiselect("Broker", options=broker_options, default=[])
        
        # Filter
        filtered = df[df['grade'] >= min_grade]
        if broker_filter and 'brokers' in df.columns:
            filtered = filtered[filtered['brokers'].apply(
                lambda x: any(b in (x if isinstance(x, list) else [x]) for b in broker_filter)
            )]
        
        # Display
        display_df = filtered[['ticker', 'shares', 'live_price', 'live_value', 'grade', 'council', 'brokers']].copy()
        display_df['Signal'] = display_df['grade'].apply(grade_label)
        
        st.dataframe(
            display_df.sort_values('live_value', ascending=False),
            column_config={
                'ticker': st.column_config.TextColumn("Ticker"),
                'shares': st.column_config.NumberColumn("Shares", format="%.4f"),
                'live_price': st.column_config.NumberColumn("Price", format="$%.2f"),
                'live_value': st.column_config.NumberColumn("Value", format="$%.2f"),
                'grade': st.column_config.NumberColumn("Grade"),
                'Signal': st.column_config.TextColumn("Signal"),
                'council': st.column_config.TextColumn("Council"),
                'brokers': st.column_config.ListColumn("Brokers"),
            },
            use_container_width=True,
            hide_index=True
        )

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
    
    # eToro sync section
    st.subheader("🔄 eToro Sync")
    st.write("Click to fetch real-time data from eToro API")
    
    if st.button("🔄 Sync eToro Now", type="primary"):
        with st.spinner("Fetching from eToro API..."):
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "etoro_sync.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    st.success("✅ eToro sync complete!")
                    st.code(result.stdout)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Sync failed:\n{result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    # Binance sync section
    st.subheader("🔄 Binance Sync")
    st.write("Click to fetch real-time data from Binance API")
    
    if st.button("🔄 Sync Binance Now", type="primary"):
        with st.spinner("Fetching from Binance API..."):
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "binance_sync.py"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0:
                    st.success("✅ Binance sync complete!")
                    st.code(result.stdout)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ Sync failed:\n{result.stderr}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    st.markdown("---")
    
    brokers_list = ['eToro', 'GBM USA', 'GBM Main', 'Binance', 'Schwab', 'IBKR', 'Bitso']
    
    for broker in brokers_list:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.write(f"**{broker}**")
        
        with col2:
            if not df.empty and 'brokers' in df.columns:
                broker_value = df[df['brokers'].apply(
                    lambda x: broker in (x if isinstance(x, list) else [x]) if x else False
                )]['live_value'].sum()
                st.write(f"${broker_value:,.2f}")
            else:
                st.write("$0.00")
        
        with col3:
            if broker != 'eToro':
                if st.button("Sync", key=f"sync_{broker}"):
                    st.info(f"Syncing {broker}... (not implemented yet)")

# ANALYSIS PAGE
elif page == "📈 Analysis":
    st.title("📈 Portfolio Analysis")
    
    if not df.empty:
        # Risk analysis
        st.subheader("⚠️ Risk Analysis")
        high_risk = df[df['grade'] < 40]['live_value'].sum()
        total = df['live_value'].sum()
        risk_pct = (high_risk / total * 100) if total > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("High Risk Exposure", f"${high_risk:,.2f}")
        with col2:
            st.metric("Risk %", f"{risk_pct:.1f}%")
        
        if risk_pct > 20:
            st.error(f"⚠️ High risk exposure is {risk_pct:.1f}% — consider trimming")
        elif risk_pct > 10:
            st.warning(f"⚠️ Moderate risk exposure is {risk_pct:.1f}%")
        else:
            st.success(f"✅ Risk exposure is healthy at {risk_pct:.1f}%")
        
        # Grade distribution detail
        st.subheader("📊 Grade Distribution")
        grade_counts = df['grade'].apply(grade_label).value_counts()
        st.bar_chart(grade_counts, use_container_width=True)
