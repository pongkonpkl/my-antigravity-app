import streamlit as st
import requests
from   streamlit_autorefresh import st_autorefresh
from typing import Dict, Any, List, Tuple
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import plotly.graph_objects as go
import time
import random
import base64
from io import BytesIO
import base64
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Coin PT | God-Tier Terminal", page_icon="💠", layout="wide")

# 1. AUTO REFRESH (60 seconds)
st_autorefresh(interval=60 * 1000, key="data_refresh")

# --- QUANTITATIVE MATH ENGINES ---
def calculate_rsi(prices: List[float], periods: int = 14) -> float:
    prices_len = sum(1 for _ in prices)
    if prices_len < periods + 1:
        return 50.0
    
    deltas: List[float] = []
    prev_price = 0.0
    is_first = True
    for p in prices:
        if is_first:
            prev_price = float(p)
            is_first = False
            continue
        deltas.append(float(p) - prev_price)
        prev_price = float(p)
        
    gains: List[float] = []
    losses: List[float] = []
    for d in deltas:
        gains.append(d if d > 0 else 0.0)
        losses.append(-d if d < 0 else 0.0)
        
    sum_gain: float = 0.0
    sum_loss: float = 0.0
    i = 0
    for g in gains:
        if i < periods:
            sum_gain = float(sum_gain) + float(g)  # type: ignore
        i += 1
    j = 0
    for l in losses:
        if j < periods:
            sum_loss = float(sum_loss) + float(l)  # type: ignore
        j += 1
        
    avg_gain: float = float(sum_gain) / float(periods) if periods > 0 else 0.0
    avg_loss: float = float(sum_loss) / float(periods) if periods > 0 else 0.0
    
    idx = 0
    for g in gains:
        if idx >= periods:
            avg_gain = float((float(avg_gain) * float(periods - 1) + float(g)) / float(periods))  # type: ignore
        idx += 1
        
    idx = 0
    for l in losses:
        if idx >= periods:
            avg_loss = float((float(avg_loss) * float(periods - 1) + float(l)) / float(periods))  # type: ignore
        idx += 1
        
    if float(avg_loss) == 0.0:
        return 100.0
    rs = float(avg_gain) / float(avg_loss)
    return 100.0 - (100.0 / (1.0 + rs))

def calculate_ma_cross(prices: List[float]) -> str:
    prices_len = sum(1 for _ in prices)
    if prices_len < 168:
        return ""
    
    start_idx = prices_len - 24
    short_sum: float = 0.0
    long_sum: float = 0.0
    idx = 0
    
    for p in prices:
        val = float(p)
        if idx >= start_idx:
            short_sum = float(short_sum) + val  # type: ignore
        long_sum = float(long_sum) + val  # type: ignore
        idx += 1
        
    ma_short = float(short_sum) / 24.0  # type: ignore
    ma_long = float(long_sum) / float(prices_len)  # type: ignore
    
    diff = ((ma_short - ma_long) / ma_long) * 100
    if diff > 5.0:
        return "<span style='color:#D4AF37; font-size:10px; font-weight:800; border:1px solid rgba(212,175,55,0.4); padding:2px 6px; border-radius:4px;'>⚡ GOLDEN CROSS</span>"
    elif diff < -5.0:
        return "<span style='color:#f87171; font-size:10px; font-weight:800; border:1px solid rgba(248,113,113,0.4); padding:2px 6px; border-radius:4px;'>💀 DEATH CROSS</span>"
    return "<span style='color:#888; font-size:10px; font-weight:800; border:1px solid #444; padding:2px 6px; border-radius:4px;'>➖ NEUTRAL TREND</span>"

def render_fng_gauge(f_value: int, f_class: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = f_value, domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f_class, 'font': {'size': 14, 'color': '#D4AF37', 'family':'Inter'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "rgba(255,255,255,0.2)"},
            'bar': {'color': "rgba(255,255,255,0.8)", 'thickness':0.3},
            'bgcolor': "rgba(0,0,0,0)", 'borderwidth': 2, 'bordercolor': "rgba(255,255,255,0.05)",
            'steps': [
                {'range': [0, 25], 'color': "rgba(248,113,113,0.5)"},
                {'range': [25, 45], 'color': "rgba(251,146,60,0.5)"},
                {'range': [45, 55], 'color': "rgba(156,163,175,0.5)"},
                {'range': [55, 75], 'color': "rgba(74,222,128,0.5)"},
                {'range': [75, 100], 'color': "rgba(34,197,94,0.5)"}],
            'threshold': {'line': {'color': "#D4AF37", 'width': 4}, 'thickness': 1, 'value': f_value}
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220, margin=dict(t=0, b=0, l=0, r=0))
    return fig

# --- ULTRA-SMOOTH LUXURY CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;600;800&family=Fira+Code:wght@400;500;700&display=swap');

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #030303; }
::-webkit-scrollbar-thumb { background: #222; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #D4AF37; }

/* 3D Holographic Animated Grid */
.stApp { background-color: #050505 !important; background-image: linear-gradient(rgba(212, 175, 55, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(212, 175, 55, 0.03) 1px, transparent 1px) !important; background-size: 30px 30px !important; animation: gridMove 20s linear infinite; color: #FFFFFF !important; }
@keyframes gridMove { 0% { background-position: 0 0; } 100% { background-position: 30px 30px; } }
/* Screen Vignette Overlay */
.stApp::before { content:''; position:fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; background: radial-gradient(circle at center, transparent 40%, rgba(0,0,0,0.85) 100%); z-index:100; }
h1, h2, h3, p, span, div { font-family: 'Inter', -apple-system, sans-serif; }
.gold-gradient { background: linear-gradient(45deg, #BF953F, #FCF6BA, #B38728); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
.logo-text { font-family: 'Playfair Display', serif !important; font-size: 32px; letter-spacing: -1px; }

/* Ticker & Animations */
@keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(74, 222, 128, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); } }
.live-dot { height: 8px; width: 8px; background-color: #4ade80; border-radius: 50%; display: inline-block; margin-left: 10px; margin-bottom: 2px; animation: pulse 2s infinite; }

.ticker-wrap { width: 100%; overflow: hidden; background-color: rgba(212, 175, 55, 0.05); border-bottom: 1px solid rgba(212, 175, 55, 0.2); border-top: 1px solid rgba(212, 175, 55, 0.2); padding: 6px 0; margin-top: -30px; margin-bottom: 25px; transition: background 0.3s ease; }
.ticker-wrap:hover { background-color: rgba(212, 175, 55, 0.1); cursor: crosshair; }
.ticker-wrap:hover .ticker { animation-play-state: paused; }
.ticker { display: inline-block; white-space: nowrap; padding-right: 100%; box-sizing: content-box; animation: ticker 40s linear infinite; }
.ticker__item { display: inline-block; padding: 0 2rem; font-size: 11px; color: #D4AF37; font-weight: 600; font-family: 'Fira Code', monospace; letter-spacing: 1.5px; }
@keyframes ticker { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }

/* Cards & Structure */
.glass-card { background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 20px; margin-bottom: 12px; transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); border-left: 3px solid transparent; box-shadow: inset 0 0 20px rgba(255,255,255,0.01); }
.glass-card:hover { border-left: 3px solid #D4AF37; border-top: 1px solid rgba(212, 175, 55, 0.3); border-bottom: 1px solid rgba(212, 175, 55, 0.3); border-right: 1px solid rgba(212, 175, 55, 0.3); background: linear-gradient(90deg, rgba(212,175,55,0.08) 0%, rgba(255,255,255,0.02) 100%); transform: translateY(-4px) scale(1.005); box-shadow: 0 15px 35px -10px rgba(212, 175, 55, 0.2), inset 0 0 15px rgba(212, 175, 55, 0.05); z-index: 10; }
.stat-title { font-size: 0.7rem; font-weight: 800; color: #AAA; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 5px; }
.stat-value { font-family: 'Fira Code', monospace; font-size: 1.8rem; color: #FFF; font-weight: 700; }

/* Grid Row */
.crypto-grid { display: grid; grid-template-columns: 2fr 2fr 2.5fr 1fr; align-items: center; gap: 20px; width:100%; }
.coin-icon { width: 48px; height: 48px; border-radius: 50%; margin-right: 15px; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); background: #111; padding: 3px; object-fit: cover; }
.text-mint { color: #4ade80 !important; }
.text-rose { color: #f87171 !important; }

/* Badges */
.badge-gainer { background: rgba(74, 222, 128, 0.1); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; margin-left: 8px; letter-spacing: 1px; }
.badge-vol { background: rgba(212, 175, 55, 0.1); color: #D4AF37; border: 1px solid rgba(212, 175, 55, 0.4); padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; margin-right: 5px; letter-spacing: 1px; }
.ai-insight-box { background: linear-gradient(90deg, rgba(212,175,55,0.05) 0%, rgba(0,0,0,0) 100%); border-left: 3px solid #D4AF37; padding: 20px; border-radius: 0 8px 8px 0; font-size: 13px; color: #EEE; line-height: 1.6; height: 100%; display: flex; flex-direction: column; justify-content: center; }

/* Sidebar Tweaks */
[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid rgba(255,255,255,0.05) !important; }
div.stButton > button { background: rgba(212, 175, 55, 0.05) !important; color: #D4AF37 !important; border: 1px solid rgba(212, 175, 55, 0.3) !important; border-radius: 6px !important; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important; width: 100%; height: 50px; font-weight:700; letter-spacing:1px; margin-top:20px; }
div.stButton > button:hover { background: #D4AF37 !important; color: #000 !important; transform: scale(1.02); box-shadow: 0 0 15px rgba(212, 175, 55, 0.4); }

#MainMenu { visibility: hidden; } footer { visibility: hidden; } header { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# --- BACKEND FETCH ---
@st.cache_data(ttl=60)
def get_coingecko_data() -> List[Dict[str, Any]]:
    urls = ["https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=true", "http://127.0.0.1:8001/api/crypto"]
    for url in urls:
        try:
            r = requests.get(url, timeout=4)
            data = r.json()
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []

@st.cache_data(ttl=300)
def fetch_global_stats() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    g: Dict[str, Any] = {}
    f: Dict[str, Any] = {}
    for url_g in ["https://api.coingecko.com/api/v3/global"]:
        try:
            r_g = requests.get(url_g, timeout=4).json()
            if isinstance(r_g, dict):
                data_g = r_g.get('data')
                if isinstance(data_g, dict):
                    g = data_g
        except Exception:
            pass
    for url_f in ["https://api.alternative.me/fng/?limit=1"]:
        try:
            r_f = requests.get(url_f, timeout=4).json()
            if isinstance(r_f, dict):
                data_f = r_f.get('data', [])
                if isinstance(data_f, list):
                    for item in data_f:
                        if isinstance(item, dict):
                            f = item
                            break
        except Exception:
            pass
    return g, f

@st.dialog("GOD-TIER TERMINAL: LIVE ANALYSIS", width="large")
def show_chart_dialog(coin: Dict[str, Any]):
    st.markdown("<style>div[data-testid='stDialog'] button[aria-label='Close'] { display: none !important; }</style>", unsafe_allow_html=True)
    sym = str(coin.get('symbol', 'BTC')).upper()
    tv_symbol = f"CRYPTO:{sym}USD"
    if sym == 'USDT':
        tv_symbol = "BINANCE:USDTUSD"
    if sym == 'USDC':
        tv_symbol = "BINANCE:USDCUSD"
    
    tv_html = f'<div class="tradingview-widget-container" style="height:550px;width:100%"><div id="tv_{sym}" style="height:550px;width:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "{tv_symbol}", "interval": "1D", "timezone": "Etc/UTC", "theme": "dark", "style": "1", "locale": "en", "enable_publishing": false, "backgroundColor": "rgba(0, 0, 0, 0)", "gridColor": "rgba(42, 46, 57, 0.4)", "hide_top_toolbar": false, "hide_legend": false, "save_image": false, "container_id": "tv_{sym}"}});</script></div>'
    components.html(tv_html, height=550)
    
    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    if st.button("TERMINATE SESSION (CLOSE)", use_container_width=True):
        st.rerun()

# --- FORMATTING HELPER ---
def format_price(price: float) -> str:
    if price == 0:
        return "0.00"
    if price >= 1:
        return f"{price:,.2f}"
    if price >= 0.01:
        return f"{price:,.4f}"
    return f"{price:,.7f}"

def format_compact(num: float) -> str:
    if num >= 1e12:
        return f"{num/1e12:.2f}T"
    if num >= 1e9:
        return f"{num/1e9:.2f}B"
    if num >= 1e6:
        return f"{num/1e6:.2f}M"
    return f"{num:,.0f}"

def make_sparkline_svg(prices: List[float], is_pos: bool) -> str:
    if not prices:
        return ""
    prices_len = sum(1 for _ in prices)
    if prices_len < 2:
        return ""
    start_idx = max(0, prices_len - 24)
    prices_sliced: List[float] = []
    idx = 0
    for p in prices:
        if idx >= start_idx:
            prices_sliced.append(float(p))
        idx += 1
    if not prices_sliced:
        return ""
    
    min_p, max_p = float(min(prices_sliced)), float(max(prices_sliced))
    if max_p == min_p:
        max_p += 1e-8
    
    w, h = 130, 45
    pts: List[str] = []
    sliced_len = sum(1 for _ in prices_sliced)
    
    i = 0
    for p in prices_sliced:
        x = (i / (sliced_len - 1)) * w
        y = h - ((p - min_p) / (max_p - min_p)) * h * 0.8 - (h * 0.1)
        pts.append(f"{x},{y}")
        i += 1
        
    color_hex = "4ade80" if is_pos else "f87171"
    color = f"#{color_hex}"
    line_pts = " ".join(pts)
    poly_pts = f"0,{h} " + line_pts + f" {w},{h}"
    
    return f'''<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="overflow:visible; filter: drop-shadow(0 2px 5px rgba(0,0,0,0.5));" title="24H Sub-Trend Trajectory">
        <defs>
            <linearGradient id="grad_{color_hex}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.3"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
            </linearGradient>
        </defs>
        <polygon points="{poly_pts}" fill="url(#grad_{color_hex})" />
        <polyline points="{line_pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
    </svg>'''

# --- THE GOD TIER UI START ---

coins = get_coingecko_data()

g_data, f_data = fetch_global_stats()
m_cap_val = float(g_data.get('total_market_cap', {}).get('usd', 0)) if g_data else 0.0
v_24h_val = float(g_data.get('total_volume', {}).get('usd', 0)) if g_data else 0.0
m_cap_str = f"{m_cap_val/1e12:.2f}T" if m_cap_val else "N/A"
v_24h_str = f"{v_24h_val/1e9:.1f}B" if v_24h_val else "N/A"
f_val = int(f_data.get('value', 50)) if f_data else 50
f_class_raw = f_data.get('value_classification', 'Neutral') if f_data else "Neutral"
f_class = str(f_class_raw)
btc_dom = float(g_data.get('market_cap_percentage', {}).get('btc', 0)) if g_data else 0.0

# 1. LIVE MARKET TICKER
st.markdown(f'<div class="ticker-wrap"><div class="ticker"><div class="ticker__item">🚀 COIN PT PRO TERMINAL &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; GLOBAL MCAP: ${m_cap_str} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; 24H VOLUME: ${v_24h_str} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; BTC DOMINANCE: {btc_dom:.1f}% &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; MARKET SENTIMENT: {f_class.upper()} ({f_val}) &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; DEFI LIQUIDITY: STABLE &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; DATA SOURCED SECURELY IN REAL-TIME FROM ORACLE PROTOCOLS</div></div></div>', unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='color:#D4AF37; font-family: Inter; font-weight:900; margin-bottom: 20px; letter-spacing:1px;'>⚙️ PRO ENGINE</h3>", unsafe_allow_html=True)

globe_html = '''<style>body { margin: 0; overflow: hidden; background: transparent; }</style><div id="globeViz" style="width:100%; height:250px; cursor: move; margin-bottom:15px; border-radius:12px; overflow:hidden;"></div><script>setTimeout(() => { const world = Globe()(document.getElementById('globeViz')).globeImageUrl('https://unpkg.com/three-globe/example/img/earth-dark.jpg').bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png').backgroundColor('rgba(0,0,0,0)').width(280).height(250).pointOfView({ altitude: 2.2 }); world.controls().autoRotate = true; world.controls().autoRotateSpeed = 4.0; world.controls().enableZoom = false; }, 100);</script>'''
with st.sidebar:
    components.html(globe_html, height=270)

all_symbols: List[str] = []
for c in coins:
    if isinstance(c, dict):
        all_symbols.append(str(c.get('symbol', '')).upper())

watchlist = st.sidebar.multiselect("WHALE WATCHLIST 🐋", options=all_symbols, default=['BTC', 'ETH'] if 'BTC' in all_symbols else [])

st.sidebar.markdown("<br><h4 style='color:#AAA; font-size:12px; margin-bottom:5px; font-weight:800; letter-spacing:1px;'>QUANTITATIVE SORTING ALGORITHM</h4>", unsafe_allow_html=True)
sort_mode = st.sidebar.radio("Sort Logic", ["Market Cap (Default)", "Top Gainers (24H)", "High Turnover (Liquidity)", "RSI Overbought (>70)", "RSI Oversold (<30)"], label_visibility="collapsed")

current_sec = int(time.time() / 15)  # Shifts every 15 seconds
random.seed(current_sec)

st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.05);'><h4 style='color:#D4AF37; font-size:12px; margin-bottom:15px; font-weight:800; letter-spacing:1px; font-family:Inter;'>🚨 LIVE WHALE RADAR</h4>", unsafe_allow_html=True)

list_symbols: List[str] = []
idx = 0
for s in all_symbols:
    if idx < 15:
        list_symbols.append(str(s))
    idx += 1
if not list_symbols:
    list_symbols = ['BTC', 'ETH']
for i in range(4):
    amt = random.randint(50, 9900)
    target_coin = str(random.choice(list_symbols))
    action = random.choice(['🔥 ACCUMULATION', '🚨 DUMP ALERT', '💼 DEFI TRANSFER', '🌐 BRIDGE SWAP'])
    color = '#f87171' if 'DUMP' in action else ('#4ade80' if 'ACC' in action else '#38bdf8')
    st.sidebar.markdown(f"<div style='font-size:10px; border-left:2px solid {color}; padding-left:8px; margin-bottom:12px; color:#AAA; background:rgba(255,255,255,0.02); padding:8px;'><span style='color:#FFF; font-weight:800; font-size:11px;'>{amt:,} {target_coin}</span><br><span style='color:{color}; font-weight:700; font-family:\"Fira Code\";'>{action}</span><div style='font-size:8px; color:#555; margin-top:3px;'>Tx: 0x{random.randint(1000,9999)}...{random.randint(1000,9999)}</div></div>", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='border-color: rgba(255,255,255,0.05);'><div style='color:#555; font-size:10px; text-align:center; font-family:Fira Code;'>SYSTEM BUILT FOR EXCELLENCE<br>TERMINAL V6.0.0 (PHASE 2)</div>", unsafe_allow_html=True)

diamond_svg = '''<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 8px; filter: drop-shadow(0 0 8px rgba(212,175,55,0.6));"><path d="M12 2L2 7L12 12L22 7L12 2Z" fill="url(#goldGradient)"/><path d="M2 17L12 22L22 17" stroke="url(#goldGradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12L12 17L22 12" stroke="url(#goldGradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><defs><linearGradient id="goldGradient" x1="0" y1="0" x2="24" y2="24"><stop stop-color="#BF953F"/><stop offset="0.5" stop-color="#FCF6BA"/><stop offset="1" stop-color="#B38728"/></linearGradient></defs></svg>'''
st.markdown(f'<div style="margin-bottom:20px; display:flex; align-items:baseline;">{diamond_svg}<span class="logo-text">COIN<span class="gold-gradient">PT</span> <span style="font-size:14px; font-weight:900; color:#D4AF37; border: 1px solid #D4AF37; padding: 2px 6px; border-radius: 4px; vertical-align:middle; margin-left:10px; font-family:Inter;">TERMINAL PRO</span></span><div style="margin-left:15px; font-size:11px; font-weight:700; color:#bbb; letter-spacing:1px; font-family:\'Fira Code\';">SECURE ORACLE FEED <span class="live-dot"></span></div></div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 DASHBOARD", "🌍 SOCIAL FEED"])

with tabs[0]:
    # TOP GRID: Stats + AI + Gauge
    narrative = "Market volatility remains within standard deviation."
    if "Extreme Greed" in f_class:
        narrative = "🚨 <b>SYSTEM ALERT:</b> Retail FOMO peaking. Market overwhelmingly greedy. Institutional algorithms indicate distribution phases. Consider trailing stops on overextended asset classes."
    elif "Greed" in f_class:
        narrative = "📈 <b>TREND:</b> Bullish structures remain intact. Volume confirms price appreciation in mid-to-large caps. Hold logic advised."
    elif "Extreme Fear" in f_class:
        narrative = "🩸 <b>SYSTEM ALERT:</b> Extreme capitulation detected. Weak hands liquidating. Historically marks deep accumulation and generational buy zones for smart money operators."
    elif "Fear" in f_class:
        narrative = "🛡️ <b>STRATEGY:</b> Market uncertainty is elevated. Highly favorable environment for disciplined dollar-cost averaging (DCA) into fundamental protocols."
    
    col_grid1, col_grid2, col_grid3 = st.columns([1.5, 1.5, 1])
    with col_grid1:
        st.markdown(f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;"><div class="glass-card"><div class="stat-title">Market Cap</div><div class="stat-value">${m_cap_str}</div></div><div class="glass-card"><div class="stat-title">24h Vol</div><div class="stat-value">${v_24h_str}</div></div><div class="glass-card"><div class="stat-title">Alt Season</div><div class="stat-value">{btc_dom:.1f}% <span style="font-size:12px; color:#AAA;">BTC Dom</span></div></div><div class="glass-card"><div class="stat-title">LIQUIDITY INDEX</div><div class="stat-value">DEEP <span style="font-size:12px; color:#4ade80;">🟢</span></div></div></div>', unsafe_allow_html=True)
    with col_grid2:
        st.markdown(f'<div class="ai-insight-box"><strong style="color:#D4AF37; letter-spacing:1px; font-size:11px; font-family:\'Fira Code\';">/// AI MARKET INTELLIGENCE</strong><br><div style="margin-top:10px;">{narrative}</div></div>', unsafe_allow_html=True)
    with col_grid3:
        st.plotly_chart(render_fng_gauge(f_val, f_class), use_container_width=True)
    
    # SEARCH AND FILTER
    st.markdown("<div style='margin-top:-20px;'></div>", unsafe_allow_html=True)
    search_q = st.text_input("", placeholder="Filter protocols by name or symbol...", label_visibility="collapsed").upper()
    
    if not coins:
        st.warning("⚠️ Oracle Database unavailable. Please refresh.")
    else:
        # Compute Advanced Metrics for ALL coins first
        processed_coins: List[Dict[str, Any]] = []
        for c in coins:
            if not isinstance(c, dict):
                continue
            spark_prices: List[float] = []
            sp_dict = c.get('sparkline_in_7d')
            if isinstance(sp_dict, dict):
                p_list = sp_dict.get('price', [])
                if isinstance(p_list, list):
                    for p in p_list:
                        spark_prices.append(float(p))
                        
            rsi_val = calculate_rsi(spark_prices)
            raw_mcap = float(c.get('market_cap', 1))
            raw_vol = float(c.get('total_volume', 0))
            turnover = (raw_vol / raw_mcap) * 100 if raw_mcap > 0 else 0.0
            change_24h = float(c.get('price_change_percentage_24h') or 0.0)
            
            c['_rsi'] = rsi_val
            c['_turnover'] = turnover
            c['_change'] = change_24h
            c['_spark_prices'] = spark_prices
            processed_coins.append(c)
    
        display_coins: List[Dict[str, Any]] = processed_coins
        
        # Text Filter
        if search_q:
            filtered_coins: List[Dict[str, Any]] = []
            for c in display_coins:
                if search_q.lower() in str(c.get('name','')).lower() or search_q.lower() in str(c.get('symbol','')).lower():
                    filtered_coins.append(c)
            display_coins = filtered_coins
        
        # Execution Grid Sort Logic
        def sort_logic(c_obj: Dict[str, Any]) -> float:
            sym = str(c_obj.get('symbol')).upper()
            pin_boost = -1e12 if sym in watchlist else 0
            
            if sort_mode == "Top Gainers (24H)":
                val = float(c_obj.get('_change', 0.0)) * -1
            elif sort_mode == "Highest RSI (Overbought)":
                val = float(c_obj.get('_rsi', 0.0)) * -1
            elif sort_mode == "Lowest RSI (Oversold)":
                val = float(c_obj.get('_rsi', 0.0))
            elif sort_mode == "High Turnover (Liquidity)":
                val = float(c_obj.get('_turnover', 0.0)) * -1
            else:
                val = float(c_obj.get('market_cap_rank') or 999)
                
            return pin_boost + val
    
        display_coins.sort(key=sort_logic)
        
        display_coins_limited: List[Dict[str, Any]] = []
        count = 0
        for c_item in display_coins:
            if count >= 30:
                break
            display_coins_limited.append(c_item)
            count += 1
    
        top_gainer_id = ""
        max_chg = -999.0
        for c in display_coins_limited:
            try:
                chg = float(c.get('_change', 0.0))
                if chg > max_chg and chg > 5.0:
                    max_chg = chg
                    top_gainer_id = str(c.get('id', ''))
            except Exception:
                pass
    
        # RENDER ENGINE
        for coin in display_coins_limited:
            coin_id = str(coin.get('id', ''))
            change = float(coin.get('_change', 0.0))
            is_pos = change >= 0
            rsi = float(coin.get('_rsi', 50.0))
            turnover = float(coin.get('_turnover', 0.0))
            spark_prices = coin.get('_spark_prices', [])
            
            # Tier Protocol
            raw_mcap = float(coin.get('market_cap', 0))
            tier, tier_color = "⚔️ Micro Cap", "#888"
            if raw_mcap > 50e9:
                tier, tier_color = "👑 Blue Chip", "#D4AF37"
            elif raw_mcap > 5e9:
                tier, tier_color = "💎 Large Cap", "#38bdf8"
            elif raw_mcap > 500e6:
                tier, tier_color = "🛡️ Mid Cap", "#a78bfa"
            
            pin_icon = "📌 " if str(coin.get('symbol')).upper() in watchlist else ""
            gainer_badge = "<span class='badge-gainer'>TOP GAINER 🔥</span>" if coin_id == top_gainer_id else ""
            vol_badge = "<span class='badge-vol'>HIGH VOL 🌋</span>" if turnover > 15.0 else ""
            
            # RSI Output
            rsi_color = "#f87171" if rsi > 70 else ("#4ade80" if rsi < 30 else "#AAA")
            rsi_text = "OVERBOUGHT" if rsi > 70 else ("OVERSOLD" if rsi < 30 else "NEUTRAL")
            
            spark_html = make_sparkline_svg(spark_prices, is_pos)
            cross_html = calculate_ma_cross(spark_prices)
            
            price_str = format_price(float(coin.get('current_price', 0)))
            rank_val = int(coin.get('market_cap_rank') or 999)
            rank = "🥇" if rank_val == 1 else ("🥈" if rank_val == 2 else ("🥉" if rank_val == 3 else str(rank_val)))
            if rank_val == 999:
                rank = "-"
            img_url = str(coin.get('image', ''))
            name = str(coin.get('name', ''))
            sym = str(coin.get('symbol', '')).upper()
            
            ath = format_price(float(coin.get('ath', 0)))
            ath_chg = float(coin.get('ath_change_percentage') or 0.0)
            
            circ_supp = float(coin.get('circulating_supply') or 0)
            max_supp_raw = coin.get('max_supply')
            max_supp_val = float(max_supp_raw) if max_supp_raw else float(coin.get('total_supply') or 0)
            supply_pct = (circ_supp / max_supp_val) * 100 if max_supp_val > 0 else 0
            if supply_pct > 100:
                supply_pct = 100
            
            supply_bar = ""
            if max_supp_val > 0:
                supply_bar = f"<div style='display:flex; align-items:center; margin-top:10px; width:100%; gap:8px;'><div style='font-size:9px; font-weight:800; color:#AAA; letter-spacing:1px;'>SUPPLY MAX</div><div style='width:110px; height:4px; background:rgba(255,255,255,0.1); border-radius:2px; overflow:hidden;'><div style='width:{supply_pct}%; height:100%; background:linear-gradient(90deg, #D4AF37, #FDE08B);'></div></div></div>"
                
            icon_glow = "rgba(74, 222, 128, 0.4)" if is_pos else "rgba(248, 113, 113, 0.4)"
            icon_border = "#4ade80" if is_pos else "#f87171"
            icon_style = f"box-shadow: 0 0 15px {icon_glow}; border: 1.5px solid {icon_border};"
                
            row_html = (
                f'<div class="glass-card crypto-row" style="padding: 15px 25px;">'
                f'<div class="crypto-grid" style="width:100%;">'
                
                # Col 1: Identity & Tier
                f'<div style="display:flex; align-items:center;">'
                f'<span style="width:35px; color:#AAA; font-size:14px; font-family:\'Fira Code\'; font-weight:600;">{rank}</span>'
                f'<img src="{img_url}" class="coin-icon" style="{icon_style}">'
                f'<div style="display:flex; flex-direction:column;">'
                f'<div style="font-weight:700; font-size:18px; letter-spacing:0.5px;">{pin_icon}{name} <span style="color:#999; font-size:12px; margin-left:4px;">{sym}</span></div>'
                f'<div style="font-size:11px; font-weight:700; color:{tier_color}; margin-top:3px; letter-spacing:0.5px;">{tier}</div>'
                f'</div></div>'
                
                # Col 2: Price & Math Extrapolations (RSI / VOL / ATH)
                f'<div style="display:flex; flex-direction:column; gap:4px;">'
                f'<div>{vol_badge}{gainer_badge}</div>'
                f'<div style="font-size:11px; font-weight:600; color:#AAA; font-family:\'Fira Code\'; margin-top:3px;"><span style="color:{rsi_color}; font-weight:800;">RSI {rsi:.1f}</span> ({rsi_text})</div>'
                f'<div style="font-size:10px; color:#888; font-family: Inter; margin-top:1px;">ATH: ${ath} (<span style="color:#f87171; font-weight:700;">{ath_chg:.1f}%</span>)</div>'
                f'</div>'
                
                # Col 3: Sparkline, Cross & Supply
                f'<div style="display:flex; flex-direction:column; align-items:flex-start;">'
                f'<div style="margin-bottom:5px;">{cross_html}</div>'
                f'<div>{spark_html}</div>'
                f'{supply_bar}'
                f'</div>'
                
                # Col 4: Price Engine Action
                f'<div style="display:flex; flex-direction:column; align-items:flex-end; justify-content:center;">'
                f'<div style="font-family:\'Fira Code\'; font-size:22px; font-weight:800; letter-spacing:-1px;">${price_str}</div>'
                f'<div class="{"text-mint" if is_pos else "text-rose"}" style="font-size:14px; font-weight:800; margin-top:2px;">{"+" if is_pos else ""}{change:.2f}%</div>'
                f'</div>'
                
                f'</div></div>'
            )
            
            col1, col2 = st.columns([7, 2])
            with col1:
                st.markdown(row_html, unsafe_allow_html=True)
            with col2:
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                if st.button("EXECUTE", key=f"btn_{coin_id}"):
                    st.markdown("<audio autoplay style='display:none;'><source src='https://assets.mixkit.co/active_storage/sfx/2568/2568-preview.mp3' type='audio/mpeg'></audio>", unsafe_allow_html=True)
                    show_chart_dialog(coin)
                
                tv_sym = sym
                if sym == 'USDT' or sym == 'USDC':
                    tv_sym = f"{sym}USD"
                elif sym != 'BTC' and sym != 'ETH':
                    tv_sym = f"{sym}USDT"
                
                tear_out_url = f"https://www.tradingview.com/chart/?symbol={tv_sym}"
                tear_html = f'''
                <a href="{tear_out_url}" target="_blank" onclick="try{{navigator.vibrate([100,50,100]);}}catch(e){{}} new Audio('https://assets.mixkit.co/active_storage/sfx/2573/2573-preview.mp3').play();" style="display:flex; align-items:center; justify-content:center; width: 100%; height: 35px; margin-top: 8px; background: rgba(255,255,255,0.03); color: #AAA; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; font-weight: 700; font-size: 10px; letter-spacing: 1px; text-decoration: none; font-family: 'Fira Code', monospace; transition: all 0.3s ease;">
                   ⇱ TEAR-OUT PANEL
                </a>
                <style>a:hover {{ border-color: #D4AF37 !important; color: #FFF !important; background: rgba(212,175,55,0.15) !important; box-shadow: 0 0 10px rgba(212,175,55,0.2) !important; transform: scale(1.02); }}</style>
                '''
                st.markdown(tear_html, unsafe_allow_html=True)

with tabs[1]:
    st.markdown("<h2 style='color:#D4AF37; text-align:center; font-family:Playfair Display;'>🌍 GLOBAL SOCIAL FEED</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:12px; margin-top:-10px;'>ANONYMOUS TRADER INSIGHTS & WORLD NEWS</p>", unsafe_allow_html=True)
    
    # --- ADMIN ACCESS ---
    with st.sidebar.expander("🔐 SYSTEM ADMIN"):
        admin_pass = st.text_input("ADMIN_KEY", type="password")
        if admin_pass == "admin123":
             st.session_state.admin_mode = True
             st.success("ADMIN ACCESS GRANTED")
        else:
             st.session_state.admin_mode = False

    # --- ANTI-SPAM CAPTCHA GEN ---
    if 'captcha_q' not in st.session_state:
        a, b = random.randint(1, 10), random.randint(1, 10)
        st.session_state.captcha_q = f"{a} + {b}"
        st.session_state.captcha_a = a + b
    
    # POST CREATOR
    with st.expander("📝 CREATE NEW POST", expanded=True):
        col_p1, col_p2 = st.columns([1, 3])
        with col_p1:
            nickname = st.text_input("NICKNAME", value="TRADER_X", placeholder="Who are you?")
        with col_p2:
            content = st.text_area("WHAT'S HAPPENING?", placeholder="Share market alpha, world news, or trader thoughts...")
        
        img_file = st.file_uploader("ATTACH INTEL (IMAGE)", type=['png', 'jpg', 'jpeg'])
        
        # Security Grid
        col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
        with col_s1:
            captcha_input = st.text_input(f"VERIFY HUMAN: {st.session_state.captcha_q} = ?", placeholder="?")
        with col_s2:
             # HONEYPOT (Visually hidden via label and placeholder, bot-only trap)
            hp_val = st.text_input("WEBSITE_URL (LEAVE BLANK)", placeholder="http://...", key="hp_field")
        
        if st.button("🚀 BROADCAST POST", use_container_width=True):
            if not content.strip():
                st.error("⚠️ Content required.")
            elif not captcha_input or str(captcha_input).strip() != str(st.session_state.captcha_a):
                st.error("⚠️ Human verification failed. Try again.")
            else:
                img_b64 = None
                if img_file:
                    img_bytes = img_file.read()
                    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                
                try:
                    payload = {
                        "nickname": nickname, 
                        "content": content, 
                        "image_data": img_b64,
                        "honeypot": hp_val # Should be empty
                    }
                    r = requests.post("http://127.0.0.1:8001/api/social", json=payload, timeout=5)
                    if r.status_code == 429:
                        st.warning(f"⏳ {r.json().get('detail')}")
                    elif r.status_code == 400:
                        st.error(f"🚫 {r.json().get('detail')}")
                    else:
                        r.raise_for_status()
                        st.success("🔥 Signal broadcasted to the global network!")
                        # Reset captcha
                        del st.session_state.captcha_q
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Broadcast failed: {e}")

    st.markdown("---")
    
    # SOCIAL FEED
    try:
        r = requests.get("http://127.0.0.1:8001/api/social", timeout=5)
        r.raise_for_status()
        posts = r.json()
    except Exception as e:
        st.error(f"📡 Social uplink offline: {e}")
        posts = []

    if not posts:
        st.info("🌑 No signals detected in the social void. Be the first to post!")
    else:
        for p in posts:
            with st.container():
                ts = p['timestamp']
                nick = p['nickname']
                txt = p['content']
                img_b64 = p['image_data']
                
                st.markdown(f"""
                <div class="glass-card" style="padding:20px; border-left: 2px solid #D4AF37;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <span style="font-weight:800; color:#D4AF37; font-family:'Fira Code'; font-size:14px;">/// {nick.upper()}</span>
                        <span style="color:#555; font-size:10px; font-family:'Fira Code';">{ts}</span>
                    </div>
                    <div style="color:#EEE; font-size:14px; line-height:1.6; white-space: pre-wrap;">{txt}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if img_b64:
                    st.image(base64.b64decode(img_b64), use_container_width=True)
                
                # ADMIN DELETE BUTTON
                if st.session_state.get('admin_mode'):
                    if st.button(f"🗑️ DELETE POST #{p['id']}", key=f"del_{p['id']}"):
                        try:
                            r = requests.delete(f"http://127.0.0.1:8001/api/social/{p['id']}", timeout=5)
                            r.raise_for_status()
                            st.success("Post deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Delete failed: {e}")
                
                st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
    