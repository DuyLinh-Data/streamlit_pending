import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==== 1. Tự động refresh dashboard mỗi 30 giây ====
st_autorefresh(interval=30 * 1000, key="refresh")

st.sidebar.title("Cài đặt Dashboard")
uploaded_file = st.sidebar.file_uploader("Chọn file CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['assigned_time_tat'] = pd.to_datetime(df['assigned_time_tat'])

    # Thời gian tối đa (giờ) để hiển thị thanh tiến trình
    MAX_HOURS = st.sidebar.number_input("Thời gian tối đa (giờ)", min_value=1, value=72)

    st.title("Dashboard Pending Jobs")

    # Sắp xếp job theo thời gian assigned (từ lâu nhất đến mới nhất)
    df = df.sort_values(by='assigned_time_tat')

    for idx, row in df.iterrows():
        job_name = row['job_name']
        start_time = row['assigned_time_tat']
        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        
        # % thanh tiến trình (0 → chưa quá hạn, 1 → quá MAX_HOURS)
        progress = min(elapsed_hours / MAX_HOURS, 1.0)
        
        # Gradient màu: xanh → vàng → đỏ
        if progress < 0.5:
            color = f'rgb({int(0 + progress*2*255)},255,0)'  # từ xanh sang vàng
        else:
            color = f'rgb(255,{int(255 - (progress-0.5)*2*255)},0)'  # từ vàng sang đỏ
        
        st.write(f"**{job_name}** - Pending {elapsed_hours:.1f} giờ")
        
        # Hiển thị thanh tiến trình với tooltip
        st.markdown(f"""
        <div title="{elapsed_hours:.1f} giờ" style="background-color: #eee; border-radius: 5px; width: 100%; height: 20px; margin-bottom:5px;">
            <div style="width: {progress*100}%; background-color: {color}; height: 100%; border-radius: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Vui lòng tải file CSV lên để hiển thị dashboard.")
