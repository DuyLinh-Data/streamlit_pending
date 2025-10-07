import streamlit as st
import pandas as pd
import datetime

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="Pending Time Tracker",
    layout="wide",
)

st.title("⏱️ Theo dõi thời gian pending của các job")

# =========================
# ĐỌC FILE CÓ SẴN
# =========================
try:
    df = pd.read_excel("streamlit_proc.xlsx")
except Exception as e:
    st.error(f"Không thể đọc file dữ liệu: {e}")
    st.stop()

# =========================
# KIỂM TRA CỘT
# =========================
if "assigned_time_tat" not in df.columns:
    st.error("⚠️ Không tìm thấy cột 'assigned_time_tat' trong file dữ liệu.")
    st.stop()

# =========================
# XỬ LÝ DỮ LIỆU
# =========================
# Chuyển sang kiểu datetime
df["assigned_time_tat"] = pd.to_datetime(df["assigned_time_tat"], errors="coerce")

# Thời gian hiện tại
now = datetime.datetime.now()

# Tính thời gian pending (giờ)
df["pending_hours"] = (now - df["assigned_time_tat"]).dt.total_seconds() / 3600

# =========================
# HIỂN THỊ BẢNG VỚI THANH MÀU
# =========================

def color_scale(value):
    """
    Hàm chuyển số giờ thành màu đỏ đậm dần theo thời gian.
    Dưới 1h: xanh nhạt, 1–3h: cam, >3h: đỏ đậm.
    """
    if pd.isna(value):
        return "background-color: #f0f0f0;"
    elif value < 1:
        return "background-color: #d4edda;"  # xanh nhạt
    elif value < 3:
        return "background-color: #ffeeba;"  # vàng cam
    elif value < 6:
        return "background-color: #f8d7da;"  # hồng nhạt
    else:
        return "background-color: #dc3545; color: white;"  # đỏ đậm

st.subheader("📋 Danh sách job và thời gian pending:")

styled_df = df.style.applymap(color_scale, subset=["pending_hours"]).format({
    "pending_hours": "{:.1f} giờ"
})

st.dataframe(styled_df, use_container_width=True)

# =========================
# HIỂN THỊ THỐNG KÊ
# =========================
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("Số job", len(df))
col2.metric("Trung bình pending (giờ)", f"{df['pending_hours'].mean():.1f}")
col3.metric("Job pending > 6h", (df['pending_hours'] > 6).sum())
