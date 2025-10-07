import streamlit as st
import pandas as pd
from datetime import datetime

# ========== CẤU HÌNH TRANG ==========
st.set_page_config(page_title="Pending Jobs Tracker", layout="wide")
st.title("📋 Pending Warranty Jobs Tracker")

# ========== ĐỌC FILE TĨNH ==========
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("streamlit_proc.xlsx")
    except FileNotFoundError:
        st.error("❌ Không tìm thấy file 'streamlit_proc.xlsx'. Hãy upload file Excel vào cùng thư mục với app.py.")
        st.stop()

    # Chuẩn hóa dữ liệu ngày
    df['assigned_time_tat'] = pd.to_datetime(df['assigned_time_tat'], errors='coerce')
    # Thêm số ngày pending
    today = pd.Timestamp(datetime.now().date())
    df['Pending_Days'] = (today - df['assigned_time_tat']).dt.days
    return df

df = load_data()

# ========== BỘ LỌC ==========
st.sidebar.header("🔍 Bộ lọc")
asc_list = sorted(df['asc_account_name'].dropna().unique().tolist())
selected_asc = st.sidebar.selectbox("Chọn trạm bảo hành", ["Tất cả"] + asc_list)

status_list = sorted(df['sub_status'].dropna().unique().tolist())
selected_status = st.sidebar.multiselect("Chọn trạng thái", status_list, default=status_list)

keyword = st.sidebar.text_input("Nhập từ khóa (model, mô tả, mã ca...)")

# ========== LỌC DỮ LIỆU ==========
filtered = df.copy()
if selected_asc != "Tất cả":
    filtered = filtered[filtered['asc_account_name'] == selected_asc]

if selected_status:
    filtered = filtered[filtered['sub_status'].isin(selected_status)]

if keyword:
    keyword_lower = keyword.lower()
    filtered = filtered[
        filtered.apply(lambda row: keyword_lower in str(row).lower(), axis=1)
    ]

# ========== HIỂN THỊ THỐNG KÊ ==========
st.subheader("📊 Thống kê tổng quan")
col1, col2, col3 = st.columns(3)
col1.metric("Tổng số ca", len(filtered))
col2.metric("Số trạm", len(filtered['asc_account_name'].unique()))
col3.metric("Pending trung bình (ngày)", round(filtered['Pending_Days'].mean(), 1) if not filtered.empty else 0)

# ========== CẢNH BÁO MÀU ==========
def color_pending(val):
    if pd.isna(val):
        return ''
    if val > 10:
        color = 'background-color: #ff4d4d; color: white;'  # đỏ
    elif val > 5:
        color = 'background-color: #ffd633;'  # vàng
    else:
        color = ''
    return color

# ========== HIỂN THỊ BẢNG ==========
st.subheader("📑 Danh sách Pending Jobs")
if filtered.empty:
    st.warning("⚠️ Không có dữ liệu phù hợp với bộ lọc.")
else:
    styled_df = filtered.style.applymap(color_pending, subset=['Pending_Days'])
    st.dataframe(styled_df, use_container_width=True, height=600)

    # ========== EXPORT ==========
    def to_excel(df):
        from io import BytesIO
        output = BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()

    excel_data = to_excel(filtered)
    st.download_button(
        label="⬇️ Tải kết quả lọc (Excel)",
        data=excel_data,
        file_name="pending_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
