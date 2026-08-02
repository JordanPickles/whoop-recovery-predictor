import sys
from pathlib import Path
import plotly.graph_objects as go
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from src.main import DataPipeline
from src.predict import OutputPrediction


st.set_page_config(
    page_title="Recovery Insight Hub",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', Helvetica, Arial, sans-serif;
        background-color: #0D1117;
        color: #FFFFFF;
    }
    .metric-label {
        font-size: 11px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #8B949E;
    }
    .metric-value {
        font-size: 72px;
        font-weight: 700;
        line-height: 1;
        color: #00D4AA;
    }
    .metric-range {
        font-size: 14px;
        color: #8B949E;
        margin-top: 4px;
    }
    .divider {
        border-top: 1px solid #21262D;
        margin: 24px 0;
    }
    .section-label {
        font-size: 11px;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #8B949E;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    pipeline = DataPipeline()
    df_processed = pipeline.pre_process_data()
    df_engineered = pipeline.feature_engineering(df_processed)

    return df_engineered

df = load_data()
predictor = OutputPrediction(df)
results = predictor.predict_recovery_score()
prediction = round(results['recovery_prediction'])
shap_groups = results['shap_group_scores']
date = results['prediction_date']

st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; padding-bottom:16px;">
    <span style="font-size:11px; letter-spacing:0.15em; text-transform:uppercase; color:#8B949E;">Recovery Insight Hub</span>
    <span style="font-size:11px; color:#8B949E;">{date}</span>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 1])

with col1:
    # Donut chart
    color = '#00D4AA' if prediction >= 67 else '#F5A623' if prediction >= 34 else '#FF4B4B'
    
    fig = go.Figure(go.Pie(
        values=[prediction, 100 - prediction],
        hole=0.75,
        marker_colors=[color, '#21262D'],
        textinfo='none',
        hoverinfo='none'
    ))
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations=[{
            'text': f'<b>{prediction}</b>',
            'x': 0.5, 'y': 0.5,
            'font': {'size': 48, 'color': color, 'family': 'Helvetica'},
            'showarrow': False
        }]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<div class="metric-label" style="text-align:center">Predicted recovery · {date}</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="section-label">Today\'s metrics</div>', unsafe_allow_html=True)
    latest = df.iloc[-1]
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("HRV", f"{latest['hrv_rmssd_milli']:.0f}ms")
        st.metric("Recovery", f"{latest['recovery_score']:.0f}")
    with m2:
        st.metric("Strain", f"{latest['cycle_strain']:.1f}")
        st.metric("RHR", f"{latest['resting_heart_rate']:.0f}bpm")
    with m3:
        st.metric("Sleep", f"{latest['total_sleep_time_hours']:.1f}h")
        st.metric("HRV 7d", f"{latest['hrv_rmssd_milli_rolling_avg_7']:.0f}ms")

# Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# SHAP section
st.markdown('<div class="section-label">What\'s driving this prediction</div>', unsafe_allow_html=True)

bars_html = ""
for group in ['Physiological', 'Training Load', 'Sleep']:
    value = float(shap_groups[group].values[0])
    color = '#00D4AA' if value > 0 else '#FF4B4B'
    bar_width = min(abs(value) / 20 * 100, 100)
    left_bar = f'<div style="background:{color}; height:4px; width:{bar_width}%;"></div>' if value < 0 else ''
    right_bar = f'<div style="background:{color}; height:4px; width:{bar_width}%;"></div>' if value > 0 else ''
    bars_html += f"""
    <div style="margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <span style="font-size:12px; color:#8B949E; text-transform:uppercase; letter-spacing:0.1em;">{group}</span>
            <span style="font-size:12px; color:{color};">{value:+.1f}</span>
        </div>
        <div style="display:flex; align-items:center; height:8px;">
            <div style="width:50%; display:flex; justify-content:flex-end; height:4px;">{left_bar}</div>
            <div style="width:2px; height:12px; background:#8B949E;"></div>
            <div style="width:50%; height:4px;">{right_bar}</div>
        </div>
    </div>
    """

st.markdown(bars_html, unsafe_allow_html=True)

