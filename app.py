import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Cấu hình hằng số
SHEET_NAME = "trangtính1"

st.set_page_config(page_title="Quản lý Nội trú", layout="wide")

# Khởi tạo kết nối với xử lý lỗi hiển thị
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Thử đọc dữ liệu để kiểm tra kết nối
    df = conn.read(worksheet=SHEET_NAME, ttl=0)
    st.success("✅ Kết nối Google Sheets thành công!")
except Exception as e:
    st.error("❌ Lỗi kết nối! Hãy kiểm tra lại định dạng Secrets.")
    st.info("Đảm bảo bạn đã có dòng [connections.gsheets] trong Secrets.")
    st.stop()

st.title("🏫 Hệ Thống Quản Lý Nội Trú")
st.dataframe(df.dropna(how="all"), use_container_width=True)

# Phần form đăng ký đơn giản
with st.expander("📝 Đăng ký ra ngoài mới"):
    with st.form("form_dk"):
        ten = st.text_input("Họ và Tên:")
        lop = st.selectbox("Lớp:", ["12A1", "12A2", "11A1", "11A2", "10A1", "10A2"])
        ly_do = st.text_area("Lý do:")
        if st.form_submit_button("Gửi đơn"):
            new_row = pd.DataFrame([{"Mã Đơn": len(df)+1, "Họ Tên": ten, "Lớp": lop, "Trạng Thái": "Chờ duyệt"}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet=SHEET_NAME, data=updated_df)
            st.success("Đã lưu dữ liệu!")
            st.rerun()
