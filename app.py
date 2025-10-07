import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ==== 1. Tự động refresh dashboard mỗi 30 giây ====
st_autorefresh(interval=30 * 1000, key="refresh")

st.set_page_config(page_title="Pending Jobs Dashboard", layout="wide")

st.sidebar.title("⚙️ Cài đặt Dashboard")
uploaded_file = st.sidebar.file_uploader("📂 Chọn file CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['assigned_time_tat'] = pd.to_datetime(df['assigned_time_tat'], errors='coerce')

    MAX_HOURS = st.sidebar.number_input("⏱ Thời gian tối đa (giờ)", min_value=1, value=72)

    st.title("📊 Dashboard Pending Jobs (Tự động cập nhật)")

    # Sắp xếp theo thời gian assigned
    df = df.sort_values(by='assigned_time_tat')

    for idx, row in df.iterrows():
        job_name = row['job_name']
        start_time = row['assigned_time_tat']

        if pd.isna(start_time):
            continue

        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        progress = min(elapsed_hours / MAX_HOURS, 1.0)

        # ==== Gradient màu: xanh -> vàng -> đỏ -> đỏ đậm ====
        if progress < 0.5:
            # xanh -> vàng
            r = int(progress * 2 * 255)
            g = 255
            b = 0
        elif progress < 1.0:
            # vàng -> đỏ
            r = 255
            g = int(255 - (progress - 0.5) * 2 * 255)
            b = 0
        else:
            # quá hạn -> đỏ đậm dần
            extra = min((elapsed_hours - MAX_HOURS) / MAX_HOURS, 1.0)
            r = 153
            g = int(0 + (1 - extra) * 30)
            b = int(0 + (1 - extra) * 30)

        color = f'rgb({r},{g},{b})'

        st.write(f"**{job_name}** - ⏰ Đã pending {elapsed_hours:.1f} giờ")

        # ==== Hiển thị thanh tiến trình ====
        st.markdown(f"""
        <div title="{elapsed_hours:.1f} giờ" style="
            background-color: #eee;
            border-radius: 5px;
            width: 100%;
            height: 20px;
            margin-bottom:5px;">
            <div style="
                width: {progress*100}%;
                background-color: {color};
                height: 100%;
                border-radius: 5px;">
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("📤 Vui lòng tải file CSV lên để hiển thị dashboard.")