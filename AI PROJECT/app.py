import streamlit as st
import pandas as pd
import numpy as np
import datetime
import joblib
import plotly.graph_objects as go
import plotly.express as px

# 1. Custom Styling & Page Configuration
st.set_page_config(
    page_title="Pakistan 3-Day Weather Prediction",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glassmorphic styling
st.markdown("""
<style>
    /* Hide default Streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Adjust main content padding to account for hidden header */
    .block-container {
        padding-top: 2rem !important;
    }

    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek gradient background */
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1f2937 100%);
        color: #f8fafc;
    }
    
    /* Glassmorphism Weather Card */
    .weather-card {
        background: rgba(31, 41, 55, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 28px 24px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .weather-card:hover {
        transform: translateY(-8px);
        border-color: rgba(99, 102, 241, 0.45);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.18);
        background: rgba(31, 41, 55, 0.55);
    }
    
    /* Emojis styling */
    .weather-emoji {
        font-size: 4rem;
        margin-bottom: 12px;
        filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.25));
    }
    
    /* Date styling */
    .weather-date {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 4px;
    }
    
    /* Weather state text styling */
    .weather-state {
        font-size: 0.9rem;
        font-weight: 600;
        color: #c084fc;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    
    /* Highlighted temperature */
    .weather-temp {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 16px 0;
    }
    
    /* Generic metrics text */
    .weather-metric {
        font-size: 1rem;
        color: #94a3b8;
        margin: 6px 0;
        display: flex;
        justify-content: space-between;
        padding: 4px 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    
    .weather-metric span.val {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    /* ===========================
       SIDEBAR / CONTROL PANEL
       =========================== */

    /* Sidebar base */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06090f 0%, #0d1220 60%, #111827 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }

    /* Sidebar inner padding */
    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
    }

    /* Control Panel header */
    .sidebar-header {
        background: linear-gradient(135deg, rgba(56,189,248,0.12) 0%, rgba(129,140,248,0.12) 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar-header h2 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.5px;
    }
    .sidebar-header p {
        margin: 4px 0 0 0;
        font-size: 0.75rem;
        color: #64748b;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Section divider */
    .sb-divider {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 18px 0 12px 0;
    }
    .sb-divider span.sb-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        white-space: nowrap;
    }
    .sb-divider::before, .sb-divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.06);
    }

    /* City badge pill */
    .city-badge {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(56,189,248,0.08);
        border: 1px solid rgba(56,189,248,0.2);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 6px 0 14px 0;
    }
    .city-badge .cb-icon { font-size: 1.4rem; }
    .city-badge .cb-info { flex: 1; }
    .city-badge .cb-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f1f5f9;
        display: block;
    }
    .city-badge .cb-coords {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 2px;
        display: block;
    }

    /* Date range info card */
    .date-range-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-left: 3px solid #6366f1;
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 14px;
        font-size: 0.8rem;
    }
    .date-range-card .drc-label {
        color: #6366f1;
        font-weight: 700;
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .date-range-card .drc-dates {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .date-range-card .drc-sub {
        color: #475569;
        font-size: 0.72rem;
        margin-top: 4px;
    }

    /* Predict button override */
    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 0 !important;
        width: 100% !important;
        cursor: pointer !important;
        box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.3px;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(99,102,241,0.55) !important;
        background: linear-gradient(135deg, #818cf8 0%, #38bdf8 100%) !important;
    }

    /* Widget labels */
    section[data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
    }

    /* Select & input boxes */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stDateInput > div > div {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
    }

    /* ML insights card inside expander */
    .ml-insight-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 8px;
    }
    .ml-insight-item {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 8px 10px;
    }
    .ml-insight-item .mli-label {
        font-size: 0.65rem;
        color: #6366f1;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 3px;
    }
    .ml-insight-item .mli-val {
        font-size: 0.8rem;
        color: #e2e8f0;
        font-weight: 600;
    }
    .ml-insight-full {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 8px 10px;
        margin-top: 8px;
    }
    .ml-insight-full .mli-label {
        font-size: 0.65rem;
        color: #6366f1;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
    }
    .ml-insight-full .mli-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 4px;
    }
    .ml-insight-full .mli-tag {
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 20px;
        padding: 2px 8px;
        font-size: 0.72rem;
        color: #a5b4fc;
        font-weight: 600;
    }

    /* ===========================
       MAIN AREA
       =========================== */

    /* Metrics box */
    .metric-container {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 10px;
    }

    /* Title text gradient */
    .title-gradient {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* ── City Profile Card ── */
    .city-profile-card {
        background: linear-gradient(145deg, rgba(14,22,40,0.95) 0%, rgba(20,30,55,0.9) 100%);
        border: 1px solid rgba(56,189,248,0.18);
        border-radius: 20px;
        padding: 28px 24px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.45);
    }
    .city-profile-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 24px;
        padding-bottom: 18px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .city-profile-icon {
        font-size: 3rem;
        line-height: 1;
        filter: drop-shadow(0 0 14px rgba(56,189,248,0.4));
    }
    .city-profile-name {
        font-size: 1.7rem;
        font-weight: 800;
        color: #f1f5f9;
        line-height: 1.1;
    }
    .city-profile-region {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    .city-profile-badge {
        margin-left: auto;
        background: rgba(56,189,248,0.1);
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.72rem;
        color: #38bdf8;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        white-space: nowrap;
    }
    /* Stat tiles grid */
    .stat-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 12px;
        margin-bottom: 18px;
    }
    .stat-tile {
        background: rgba(15,23,42,0.7);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 14px 12px;
        text-align: center;
        transition: border-color 0.2s ease;
    }
    .stat-tile:hover { border-color: rgba(99,102,241,0.35); }
    .stat-tile .st-icon { font-size: 1.5rem; margin-bottom: 6px; }
    .stat-tile .st-val {
        font-size: 1.3rem;
        font-weight: 800;
        color: #f1f5f9;
        line-height: 1.1;
    }
    .stat-tile .st-lbl {
        font-size: 0.68rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    /* accent colours per tile */
    .st-hot   .st-val { color: #fb923c; }
    .st-cold  .st-val { color: #38bdf8; }
    .st-hum   .st-val { color: #34d399; }
    .st-rain  .st-val { color: #818cf8; }
    .st-wind  .st-val { color: #f472b6; }
    .st-pres  .st-val { color: #fbbf24; }
    /* Geo strip */
    .geo-strip {
        display: flex;
        justify-content: space-around;
        background: rgba(99,102,241,0.06);
        border: 1px solid rgba(99,102,241,0.14);
        border-radius: 12px;
        padding: 12px 8px;
        margin-top: 4px;
    }
    .geo-item { text-align: center; }
    .geo-item .gi-val {
        font-size: 0.95rem;
        font-weight: 700;
        color: #c7d2fe;
    }
    .geo-item .gi-lbl {
        font-size: 0.65rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    /* ── How-to guide steps ── */
    .howto-step {
        display: flex;
        align-items: flex-start;
        gap: 14px;
        background: rgba(15,23,42,0.5);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }
    .howto-step .hs-num {
        min-width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #6366f1, #38bdf8);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
        font-weight: 800;
        color: #fff;
        flex-shrink: 0;
    }
    .howto-step .hs-body {}
    .howto-step .hs-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 3px;
    }
    .howto-step .hs-desc {
        font-size: 0.8rem;
        color: #64748b;
        line-height: 1.5;
    }
    /* App title subtitle */
    .app-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin: -8px 0 24px 0;
        font-weight: 400;
    }
    
    /* Validation Table */
    .val-table-container {
        overflow-x: auto;
        margin-top: 15px;
        margin-bottom: 25px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    .val-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        font-size: 0.95rem;
    }
    .val-table th {
        background: rgba(15, 23, 42, 0.9);
        color: #e2e8f0;
        padding: 14px 18px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .val-table td {
        background: rgba(30, 41, 59, 0.4);
        color: #f1f5f9;
        padding: 12px 18px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .val-table tr:hover td {
        background: rgba(51, 65, 85, 0.5);
    }
    .val-error {
        color: #ef4444 !important;
        font-weight: 700;
    }
    .val-actual {
        color: #38bdf8 !important;
        font-weight: 600;
    }
    .val-pred {
        color: #a78bfa !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 2. Loading Cached Model and Artifacts
@st.cache_resource
def load_ml_pipeline():
    try:
        model = joblib.load('d:/AI PROJECT/weather_model.joblib')
        scaler = joblib.load('d:/AI PROJECT/scaler.joblib')
        city_encoder = joblib.load('d:/AI PROJECT/city_encoder.joblib')
        return model, scaler, city_encoder
    except Exception as e:
        st.error(f"Error loading machine learning models: {e}")
        return None, None, None

@st.cache_data
def load_weather_data():
    df = pd.read_csv("d:/AI PROJECT/pakistan_weather_2000_2024.csv")
    df['date'] = pd.to_datetime(df['date'])
    df['is_rain'] = (df['prcp'] > 0).astype(int)
    df = df.sort_values(by=['city', 'date']).reset_index(drop=True)
    return df

model, scaler, city_encoder = load_ml_pipeline()
df_weather = load_weather_data()

CITY_COORDS = {
    'Islamabad': {'latitude': 33.6844, 'longitude': 73.0479, 'elevation': 540},
    'Karachi': {'latitude': 24.8607, 'longitude': 67.0011, 'elevation': 10},
    'Lahore': {'latitude': 31.5204, 'longitude': 74.3587, 'elevation': 217},
    'Peshawar': {'latitude': 34.0151, 'longitude': 71.5249, 'elevation': 331},
    'Quetta': {'latitude': 30.1798, 'longitude': 66.9750, 'elevation': 1680},
    'Gilgit': {'latitude': 35.9208, 'longitude': 74.3089, 'elevation': 1500}
}

# 3. Sidebar Widgets

# ── Header ────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sidebar-header">
    <h2>⚙️ Control Panel</h2>
    <p>Pakistan Weather Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ── City Selection ─────────────────────────────────────────
st.sidebar.markdown("""
<div class="sb-divider"><span class="sb-label">📍 City Selection</span></div>
""", unsafe_allow_html=True)
selected_city = st.sidebar.selectbox("Select Pakistani City", list(CITY_COORDS.keys()), label_visibility="collapsed")

# City badge with coordinates
coords_sb = CITY_COORDS[selected_city]
city_emojis = {'Islamabad': '🏛️', 'Karachi': '🌊', 'Lahore': '🌹', 'Peshawar': '⛰️', 'Quetta': '🏔️', 'Gilgit': '❄️'}
st.sidebar.markdown(f"""
<div class="city-badge">
    <div class="cb-icon">{city_emojis.get(selected_city, '🏙️')}</div>
    <div class="cb-info">
        <span class="cb-name">{selected_city}</span>
        <span class="cb-coords">📍 {coords_sb['latitude']}°N, {coords_sb['longitude']}°E &nbsp;·&nbsp; ⛰ {coords_sb['elevation']}m</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Date Selection ─────────────────────────────────────────
st.sidebar.markdown("""
<div class="sb-divider"><span class="sb-label">📅 Forecast Date</span></div>
""", unsafe_allow_html=True)

# Get historical limits for the selected city
city_data = df_weather[df_weather['city'] == selected_city].sort_values('date')
min_history_date = city_data['date'].min().date()
max_history_date = city_data['date'].max().date()

# Date range info card
st.sidebar.markdown(f"""
<div class="date-range-card">
    <div class="drc-label">📊 Available Data Window</div>
    <div class="drc-dates">{min_history_date.strftime('%b %d, %Y')} &rarr; {max_history_date.strftime('%b %d, %Y')}</div>
    <div class="drc-sub">Select a date within range for validation, or beyond for future forecast</div>
</div>
""", unsafe_allow_html=True)

selected_date = st.sidebar.date_input(
    "Pick Forecast Reference Date",
    value=max_history_date,
    min_value=min_history_date + datetime.timedelta(days=7),
    max_value=datetime.date(2030, 12, 31)
)

# ── Predict Button ─────────────────────────────────────────
st.sidebar.markdown("<div style='margin: 20px 0 6px 0;'></div>", unsafe_allow_html=True)
predict_btn = st.sidebar.button("🔮  Predict 3-Day Weather", use_container_width=True)
st.sidebar.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# ── ML Model Insights ──────────────────────────────────────
st.sidebar.markdown("""
<div class="sb-divider"><span class="sb-label">🤖 ML Model Info</span></div>
""", unsafe_allow_html=True)

with st.sidebar.expander("View Model Details", expanded=False):
    st.markdown("""
<div class="ml-insight-grid">
    <div class="ml-insight-item">
        <div class="mli-label">Architecture</div>
        <div class="mli-val">Random Forest</div>
    </div>
    <div class="ml-insight-item">
        <div class="mli-label">Estimators</div>
        <div class="mli-val">100 Trees</div>
    </div>
    <div class="ml-insight-item">
        <div class="mli-label">Input Window</div>
        <div class="mli-val">7-Day Lags</div>
    </div>
    <div class="ml-insight-item">
        <div class="mli-label">Forecast Horizon</div>
        <div class="mli-val">3 Days Ahead</div>
    </div>
</div>
<div class="ml-insight-full" style="margin-top:8px;">
    <div class="mli-label">Predicted Outputs</div>
    <div class="mli-tags">
        <span class="mli-tag">🌡️ Temperature</span>
        <span class="mli-tag">💧 Humidity</span>
        <span class="mli-tag">💨 Wind Speed</span>
        <span class="mli-tag">🌧️ Rain Prob.</span>
        <span class="mli-tag">☁️ Cloud Cover</span>
    </div>
</div>
<div class="ml-insight-full">
    <div class="mli-label">Feature Groups</div>
    <div class="mli-tags">
        <span class="mli-tag">Temp Lags</span>
        <span class="mli-tag">Humidity Lags</span>
        <span class="mli-tag">Wind Lags</span>
        <span class="mli-tag">Pressure Lags</span>
        <span class="mli-tag">Geo Data</span>
        <span class="mli-tag">Calendar</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Helper logic to compute climatological normal windows for future dates
def get_climatology_window(city, target_date, full_df):
    date_range = pd.date_range(end=target_date, periods=7)
    clima_rows = []
    
    for d in date_range:
        # Match day and month across all recorded years for this city
        matches = full_df[(full_df['city'] == city) & 
                          (full_df['month'] == d.month) & 
                          (full_df['day'] == d.day)]
        if len(matches) > 0:
            mean_vals = matches[['tavg', 'tmin', 'tmax', 'humidity', 'wspd', 'prcp', 'pressure', 'cloud_cover', 'is_rain']].mean().to_dict()
        else:
            # Fallback to monthly city averages
            matches_month = full_df[(full_df['city'] == city) & (full_df['month'] == d.month)]
            if len(matches_month) > 0:
                mean_vals = matches_month[['tavg', 'tmin', 'tmax', 'humidity', 'wspd', 'prcp', 'pressure', 'cloud_cover', 'is_rain']].mean().to_dict()
            else:
                mean_vals = full_df[full_df['city'] == city][['tavg', 'tmin', 'tmax', 'humidity', 'wspd', 'prcp', 'pressure', 'cloud_cover', 'is_rain']].mean().to_dict()
        
        mean_vals['date'] = d
        mean_vals['city'] = city
        clima_rows.append(mean_vals)
        
    clima_df = pd.DataFrame(clima_rows)
    return clima_df

# Weather emoji selection function
def get_weather_emoji_and_state(rain_prob, cloud_cover, wspd):
    if rain_prob > 40:
        if wspd > 15:
            return "🌩️", "Thunderstorm"
        return "🌧️", "Rainy"
    else:
        if cloud_cover > 60:
            return "☁️", "Cloudy"
        elif cloud_cover > 25:
            return "⛅", "Partly Cloudy"
        return "☀️", "Sunny"

# 5. Main Dashboard Render
st.markdown("<h1>🌦️ <span class='title-gradient'>Pakistan Weather Intelligence</span></h1>", unsafe_allow_html=True)
st.markdown("<p class='app-subtitle'>ML-powered 3-day weather forecasting for major Pakistani cities &nbsp;·&nbsp; 2000–2024 Historical Dataset</p>", unsafe_allow_html=True)
st.markdown("---")

if not predict_btn:
    left_col, right_col = st.columns([1, 1], gap="large")

    # ── LEFT: How-To Guide ───────────────────────────────────────────────────
    with left_col:
        st.markdown("### 🧭 How to Get Your Forecast")
        st.markdown("""
<div class="howto-step">
    <div class="hs-num">1</div>
    <div class="hs-body">
        <div class="hs-title">📍 Pick a City</div>
        <div class="hs-desc">Use the <strong>City Selection</strong> dropdown in the left sidebar to choose one of the six major Pakistani cities. The city profile card on the right will update instantly.</div>
    </div>
</div>
<div class="howto-step">
    <div class="hs-num">2</div>
    <div class="hs-body">
        <div class="hs-title">📅 Choose a Reference Date</div>
        <div class="hs-desc">Select a date from the calendar picker. Dates <strong>within the historical window</strong> will also show real vs. predicted validation results so you can see exactly how accurate the model is.</div>
    </div>
</div>
<div class="howto-step">
    <div class="hs-num">3</div>
    <div class="hs-body">
        <div class="hs-title">🔮 Run the Prediction</div>
        <div class="hs-desc">Click the glowing <strong>Predict 3-Day Weather</strong> button. The ML model will use the last 7 days of weather as context and output forecasts for the next 3 days.</div>
    </div>
</div>
<div class="howto-step">
    <div class="hs-num">4</div>
    <div class="hs-body">
        <div class="hs-title">📊 Explore the Results</div>
        <div class="hs-desc">Review the <strong>forecast cards</strong> with temperature, humidity, wind speed, and rain probability. Scroll down to explore interactive <strong>Plotly charts</strong> and the validation accuracy table.</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── RIGHT: City Profile Card ─────────────────────────────────────────────
    with right_col:
        st.markdown("### 🏙️ City Profile")

        city_records  = df_weather[df_weather['city'] == selected_city]
        coords        = CITY_COORDS[selected_city]
        city_emojis_m = {'Islamabad': '🏛️', 'Karachi': '🌊', 'Lahore': '🌹',
                         'Peshawar': '⛰️', 'Quetta': '🏔️', 'Gilgit': '❄️'}
        city_regions  = {'Islamabad': 'Federal Capital · Punjab',
                         'Karachi': 'Sindh Province · Coastal City',
                         'Lahore': 'Punjab Province · Cultural Hub',
                         'Peshawar': 'Khyber Pakhtunkhwa · Gateway City',
                         'Quetta': 'Balochistan Province · Hill Station',
                         'Gilgit': 'Gilgit-Baltistan · Mountain Region'}

        avg_temp   = city_records['tavg'].mean()
        max_temp   = city_records['tmax'].max()
        min_temp   = city_records['tmin'].min()
        avg_hum    = city_records['humidity'].mean()
        rain_days  = int((city_records['prcp'] > 0).sum())
        total_days = len(city_records)
        rain_pct   = rain_days / total_days * 100
        avg_wind   = city_records['wspd'].mean()
        avg_pres   = city_records['pressure'].mean()
        data_years = f"{city_records['date'].min().year}–{city_records['date'].max().year}"

        st.markdown(f"""
<div class="city-profile-card">
    <div class="city-profile-header">
        <div class="city-profile-icon">{city_emojis_m.get(selected_city, '🏙️')}</div>
        <div>
            <div class="city-profile-name">{selected_city}</div>
            <div class="city-profile-region">{city_regions.get(selected_city, 'Pakistan')}</div>
        </div>
        <div class="city-profile-badge">📅 {data_years}</div>
    </div>
    <div class="stat-grid">
        <div class="stat-tile st-hot">
            <div class="st-icon">🌡️</div>
            <div class="st-val">{avg_temp:.1f}°C</div>
            <div class="st-lbl">Avg Temperature</div>
        </div>
        <div class="stat-tile st-hot">
            <div class="st-icon">🔥</div>
            <div class="st-val">{max_temp:.1f}°C</div>
            <div class="st-lbl">Peak Temp Ever</div>
        </div>
        <div class="stat-tile st-cold">
            <div class="st-icon">🥶</div>
            <div class="st-val">{min_temp:.1f}°C</div>
            <div class="st-lbl">Lowest Temp Ever</div>
        </div>
        <div class="stat-tile st-hum">
            <div class="st-icon">💧</div>
            <div class="st-val">{avg_hum:.0f}%</div>
            <div class="st-lbl">Avg Humidity</div>
        </div>
        <div class="stat-tile st-rain">
            <div class="st-icon">🌧️</div>
            <div class="st-val">{rain_days:,}</div>
            <div class="st-lbl">Rainy Days ({rain_pct:.0f}%)</div>
        </div>
        <div class="stat-tile st-wind">
            <div class="st-icon">💨</div>
            <div class="st-val">{avg_wind:.1f}</div>
            <div class="st-lbl">Avg Wind km/h</div>
        </div>
    </div>
    <div class="geo-strip">
        <div class="geo-item">
            <div class="gi-val">📍 {coords['latitude']}°N</div>
            <div class="gi-lbl">Latitude</div>
        </div>
        <div class="geo-item">
            <div class="gi-val">📍 {coords['longitude']}°E</div>
            <div class="gi-lbl">Longitude</div>
        </div>
        <div class="geo-item">
            <div class="gi-val">⛰ {coords['elevation']} m</div>
            <div class="gi-lbl">Elevation</div>
        </div>
        <div class="geo-item">
            <div class="gi-val">🌡 {avg_pres:.0f} hPa</div>
            <div class="gi-lbl">Avg Pressure</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

else:
    # Execute Forecast Pipeline
    target_dt = pd.to_datetime(selected_date)
    
    # Check if target date is in historical database
    is_historical = min_history_date <= target_dt.date() <= max_history_date
    
    st.subheader(f"📊 Forecast Context for {selected_city} (Target: {target_dt.strftime('%B %d, %Y')})")
    
    if is_historical:
        st.success(f"📅 Selected date is within recording range. Fetching actual 7-day observed history for predictions.")
        # Fetch actual last 7 days ending at selected_date
        selected_idx = city_data[city_data['date'] == target_dt].index[0]
        # Get matching row index in city_data
        idx_in_city = city_data.index.get_loc(selected_idx)
        observed_window = city_data.iloc[idx_in_city - 6 : idx_in_city + 1].copy()
    else:
        st.warning(f"🔮 Selected date is outside historical records. Initializing window using climatological averages.")
        observed_window = get_climatology_window(selected_city, target_dt, df_weather)
        
    # Display observed window (past 7 days)
    with st.expander("🔍 View Observational Window (Past 7 Days Input Lags)", expanded=False):
        display_obs = observed_window[['date', 'tavg', 'tmin', 'tmax', 'humidity', 'wspd', 'prcp', 'pressure', 'cloud_cover']].copy()
        display_obs['date'] = display_obs['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(display_obs.style.format(precision=2), use_container_width=True)

    # Prepare features for the ML model
    features_dict = {}
    features_dict['city_encoded'] = city_encoder.transform([selected_city])[0]
    features_dict['latitude'] = CITY_COORDS[selected_city]['latitude']
    features_dict['longitude'] = CITY_COORDS[selected_city]['longitude']
    features_dict['elevation'] = CITY_COORDS[selected_city]['elevation']
    features_dict['month'] = target_dt.month
    features_dict['day'] = target_dt.day
    features_dict['dayofweek'] = target_dt.dayofweek
    
    lag_vars = ['tavg', 'tmin', 'tmax', 'humidity', 'wspd', 'prcp', 'pressure', 'cloud_cover', 'is_rain']
    for d in range(7):
        lag_row = observed_window.iloc[6 - d]  # Index 6 is t, Index 0 is t-6
        for var in lag_vars:
            features_dict[f'{var}_lag_{d}'] = lag_row[var]
            
    # Convert to DataFrame matching model columns exactly
    feature_cols = ['city_encoded', 'latitude', 'longitude', 'elevation', 'month', 'day', 'dayofweek']
    for d in range(7):
        for var in lag_vars:
            feature_cols.append(f'{var}_lag_{d}')
            
    X_pred = pd.DataFrame([features_dict])[feature_cols]
    
    # Scale features
    num_cols = [col for col in X_pred.columns if col != 'city_encoded']
    X_pred_scaled = X_pred.copy()
    X_pred_scaled[num_cols] = scaler.transform(X_pred[num_cols])
    
    # Predict
    prediction = model.predict(X_pred_scaled)
    
    # Map predictions back to variables
    target_vars = ['tavg', 'humidity', 'wspd', 'is_rain', 'cloud_cover']
    forecasts = {}
    for h in range(1, 4):
        forecasts[h] = {}
        for var_idx, var in enumerate(target_vars):
            pred_col_idx = (h - 1) * len(target_vars) + var_idx
            pred_val = prediction[0][pred_col_idx]
            
            # Post-processing limits
            if var == 'humidity':
                pred_val = np.clip(pred_val, 0, 100)
            elif var == 'wspd':
                pred_val = np.maximum(0, pred_val)
            elif var == 'is_rain':
                pred_val = np.clip(pred_val, 0, 1) * 100  # Convert to percent
            elif var == 'cloud_cover':
                pred_val = np.clip(pred_val, 0, 100)
                
            forecasts[h][var] = pred_val

    # 6. Render Weather Cards (Columns)
    st.markdown("<h3 style='margin-top:20px;'>🌤️ 3-Day Forecast Prediction</h3>", unsafe_allow_html=True)
    
    card_cols = st.columns(3)
    forecast_dates = [target_dt + datetime.timedelta(days=h) for h in range(1, 4)]
    
    for h in range(1, 4):
        fd = forecast_dates[h-1]
        emoji, state = get_weather_emoji_and_state(forecasts[h]['is_rain'], forecasts[h]['cloud_cover'], forecasts[h]['wspd'])
        
        with card_cols[h-1]:
            st.markdown(f"""
            <div class="weather-card">
                <div class="weather-date">{fd.strftime('%A')}</div>
                <div style="font-size:0.9rem; color:#64748b; margin-bottom:12px;">{fd.strftime('%b %d, %Y')}</div>
                <div class="weather-emoji">{emoji}</div>
                <div class="weather-state">{state}</div>
                <div class="weather-temp">{forecasts[h]['tavg']:.1f}°C</div>
                <div class="weather-metric">
                    <span>💧 Humidity</span>
                    <span class="val">{forecasts[h]['humidity']:.1f}%</span>
                </div>
                <div class="weather-metric">
                    <span>💨 Wind Speed</span>
                    <span class="val">{forecasts[h]['wspd']:.1f} km/h</span>
                </div>
                <div class="weather-metric">
                    <span>🌧️ Rain Chance</span>
                    <span class="val">{forecasts[h]['is_rain']:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # 7. Visualization Section (Plotly Charts)
    st.markdown("### 📈 Weather Trends Visualization")
    
    # Prep plot data
    # Combine past 7 days observed with next 3 days predicted
    obs_dates = observed_window['date'].tolist()
    all_dates = obs_dates + forecast_dates
    
    obs_temps = observed_window['tavg'].tolist()
    pred_temps = [obs_temps[-1]] + [forecasts[h]['tavg'] for h in range(1, 4)]  # Connect the lines
    pred_dates = [obs_dates[-1]] + forecast_dates
    
    # Temperature Plotly Line Chart
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=obs_dates, y=obs_temps,
        mode='lines+markers',
        name='Observed (Past 7 Days)',
        line=dict(color='#38bdf8', width=3),
        marker=dict(size=8)
    ))
    fig_temp.add_trace(go.Scatter(
        x=pred_dates, y=pred_temps,
        mode='lines+markers',
        name='Forecasted (Next 3 Days)',
        line=dict(color='#fb923c', width=3, dash='dash'),
        marker=dict(size=8, symbol='diamond')
    ))
    fig_temp.update_layout(
        title="Temperature Trend (°C)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Temp (°C)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Humidity Plotly Bar Chart
    obs_hums = observed_window['humidity'].tolist()
    pred_hums = [forecasts[h]['humidity'] for h in range(1, 4)]
    
    fig_hum = go.Figure()
    fig_hum.add_trace(go.Bar(
        x=[d.strftime('%b %d') for d in obs_dates],
        y=obs_hums,
        name='Observed',
        marker_color='#06b6d4'
    ))
    fig_hum.add_trace(go.Bar(
        x=[d.strftime('%b %d') for d in forecast_dates],
        y=pred_hums,
        name='Forecasted',
        marker_color='#ec4899'
    ))
    fig_hum.update_layout(
        title="Humidity Comparison (%)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', title="Humidity (%)", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.plotly_chart(fig_temp, use_container_width=True)
    with col_chart2:
        st.plotly_chart(fig_hum, use_container_width=True)
        
    # Wind Speed & Rain Probability combined chart
    fig_rain_wind = go.Figure()
    pred_dates_str = [d.strftime('%A (%b %d)') for d in forecast_dates]
    pred_rain = [forecasts[h]['is_rain'] for h in range(1, 4)]
    pred_wind = [forecasts[h]['wspd'] for h in range(1, 4)]
    
    fig_rain_wind.add_trace(go.Bar(
        x=pred_dates_str, y=pred_rain,
        name='Rain Probability (%)',
        marker_color='#3b82f6',
        yaxis='y1'
    ))
    fig_rain_wind.add_trace(go.Scatter(
        x=pred_dates_str, y=pred_wind,
        mode='lines+markers',
        name='Wind Speed (km/h)',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    fig_rain_wind.update_layout(
        title="Rain Chance vs. Wind Speed Forecast",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#cbd5e1',
        margin=dict(l=40, r=40, t=40, b=40),
        xaxis=dict(showgrid=False),
        yaxis1=dict(title="Rain Probability (%)", range=[0, 100], showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
        yaxis2=dict(title="Wind Speed (km/h)", overlaying='y', side='right', showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_rain_wind, use_container_width=True)
    
    # 8. Comparison vs. Actual (If historical validation is possible)
    if is_historical:
        # Check if actual forecast rows exist in city_data
        actual_rows = city_data[city_data['date'].isin(forecast_dates)]
        
        if len(actual_rows) == 3:
            st.markdown("### 🔍 Model Validation: Actual vs. Predicted Weather")
            st.write("Since you selected a historical date, we can validate the ML model predictions directly against the actual weather recordings.")
            
            html_table = "<div class='val-table-container'><table class='val-table'>"
            html_table += "<thead><tr><th>Day</th><th>Metric</th><th>Actual Observation</th><th>Model Prediction</th><th>Absolute Error</th></tr></thead><tbody>"
            for h in range(1, 4):
                fd = forecast_dates[h-1]
                actual_row = actual_rows[actual_rows['date'] == fd].iloc[0]
                
                html_table += f"<tr><td rowspan='3' style='border-bottom: 1px solid rgba(255,255,255,0.1);'><strong>Day {h}</strong><br><span style='font-size:0.8em; color:#94a3b8;'>{fd.strftime('%b %d')}</span></td>"
                html_table += f"<td>🌡️ Temp</td><td class='val-actual'>{actual_row['tavg']:.1f} °C</td><td class='val-pred'>{forecasts[h]['tavg']:.1f} °C</td><td class='val-error'>{abs(actual_row['tavg'] - forecasts[h]['tavg']):.1f} °C</td></tr>"
                html_table += f"<tr><td>💧 Humidity</td><td class='val-actual'>{actual_row['humidity']:.0f}%</td><td class='val-pred'>{forecasts[h]['humidity']:.0f}%</td><td class='val-error'>{abs(actual_row['humidity'] - forecasts[h]['humidity']):.0f}%</td></tr>"
                html_table += f"<tr><td style='border-bottom: 1px solid rgba(255,255,255,0.1);'>💨 Wind</td><td class='val-actual' style='border-bottom: 1px solid rgba(255,255,255,0.1);'>{actual_row['wspd']:.1f} km/h</td><td class='val-pred' style='border-bottom: 1px solid rgba(255,255,255,0.1);'>{forecasts[h]['wspd']:.1f} km/h</td><td class='val-error' style='border-bottom: 1px solid rgba(255,255,255,0.1);'>{abs(actual_row['wspd'] - forecasts[h]['wspd']):.1f} km/h</td></tr>"
                
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            
            # Show mean error summary
            temp_mae = np.mean([abs(actual_rows.iloc[h]['tavg'] - forecasts[h+1]['tavg']) for h in range(3)])
            hum_mae = np.mean([abs(actual_rows.iloc[h]['humidity'] - forecasts[h+1]['humidity']) for h in range(3)])
            wspd_mae = np.mean([abs(actual_rows.iloc[h]['wspd'] - forecasts[h+1]['wspd']) for h in range(3)])
            
            col_err1, col_err2, col_err3 = st.columns(3)
            with col_err1:
                st.metric("Avg Temperature MAE", f"{temp_mae:.2f} °C")
            with col_err2:
                st.metric("Avg Humidity MAE", f"{hum_mae:.2f} %")
            with col_err3:
                st.metric("Avg Wind Speed MAE", f"{wspd_mae:.2f} km/h")
        else:
            st.info("ℹ️ Some forecast days lie outside the recorded database history. Validation metrics could not be fully calculated.")
