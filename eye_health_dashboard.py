import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# ⬛ 사용자 다크 모드 설정
st.set_page_config(page_title="눈 건강 대시보드", layout="wide")

dark_mode = st.sidebar.toggle("🌙 다크 모드", value=True)

theme_bg = "#0e0e10" if dark_mode else "#f9fbfd"
font_color = "#00BFFF"
card_bg = "#1a1a1a" if dark_mode else "#ffffff"
card_border = "#444444" if dark_mode else "#dce3ec"

# 💅 커스텀 스타일
st.markdown(f"""
    <style>
        html, body, [class*="css"] {{
            background-color: {theme_bg};
            color: {font_color};
            font-family: 'Poppins', sans-serif;
        }}
        h1, h2, h3, h4 {{
            color: {font_color};
            font-weight: 700;
        }}
        .stMetric {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 12px;
            padding: 12px;
            color: {font_color} !important;
            text-align: center;
        }}
    </style>
""", unsafe_allow_html=True)

# 📦 데이터 불러오기
@st.cache_data
def load_data():
    conn = sqlite3.connect("eye_data.db")
    df = pd.read_sql_query("SELECT * FROM eye_health ORDER BY timestamp ASC", conn)
    conn.close()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

# 📈 Plotly 그래프 함수
def plot_bar(data, y_col, title, color):
    fig = px.bar(data, x="timestamp", y=y_col, title=title, color_discrete_sequence=[color])
    fig.update_layout(
        plot_bgcolor=theme_bg,
        paper_bgcolor=theme_bg,
        font_color=font_color,
        xaxis_tickangle=-45,
        height=400,
        margin=dict(t=40, b=80, l=40, r=40),
        bargap=0.3
    )
    return fig

# ⏱️ 시간 단위 선택
RESAMPLE_RULES = {
    "1분": "1min", "5분": "5min", "30분": "30min",
    "1시간": "1H", "12시간": "12H", "1일": "1D"
}

st.title("🟦 실시간 눈 건강 모니터링")
interval_label = st.sidebar.radio("⏱ 리샘플링 간격", list(RESAMPLE_RULES.keys()))
interval = RESAMPLE_RULES[interval_label]

df = load_data()
if df.empty:
    st.error("❗ 데이터가 없습니다.")
    st.stop()

df_resampled = df.set_index("timestamp").resample(interval).mean().dropna().reset_index()
df_resampled["timestamp"] = df_resampled["timestamp"].dt.strftime("%Y-%m-%d %H:%M")

# 🔢 평균값 카드
st.subheader("📊 평균 수치")
col1, col2, col3 = st.columns(3)
with col1:
    val = max(df_resampled["blink_rate"].mean(), 0.001)
    st.metric("👁️ 평균 깜빡임", f"{val:.3f}")
with col2:
    val = max(df_resampled["fatigue"].mean(), 0.001)
    st.metric("😵 평균 피로도", f"{val:.3f}")
with col3:
    val = max(df_resampled["brightness_ratio"].mean(), 0.001)
    st.metric("💡 평균 밝기", f"{val:.3f}")

# 📊 막대 그래프들
st.subheader("📈 변화 추이")
st.plotly_chart(plot_bar(df_resampled, "blink_rate", "Blink Rate", "#00BFFF"), use_container_width=True)
st.plotly_chart(plot_bar(df_resampled, "fatigue", "Fatigue", "#3399ff"), use_container_width=True)
st.plotly_chart(plot_bar(df_resampled, "red_ratio", "Red Ratio", "#ff4d6d"), use_container_width=True)
st.plotly_chart(plot_bar(df_resampled, "yellow_ratio", "Yellow Ratio", "#ffc300"), use_container_width=True)
st.plotly_chart(plot_bar(df_resampled, "blue_ratio", "Blue Ratio", "#228be6"), use_container_width=True)
st.plotly_chart(plot_bar(df_resampled, "brightness_ratio", "Brightness Ratio", "#4dabf7"), use_container_width=True)

# 📋 데이터 테이블
with st.expander("📋 전체 데이터 보기"):
    st.dataframe(df_resampled)
