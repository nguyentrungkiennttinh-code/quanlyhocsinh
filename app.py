import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Cài đặt trang
st.set_page_config(page_title="Quản lý Nội trú", layout="wide")

# Kết nối (Tên sheet: trangtính1)
SHEET_NAME = "trangtính1"

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=SHEET_NAME, ttl=0)
except Exception as e:
    st.error("Lỗi kết nối! Hãy kiểm tra lại mục Secrets trong App Settings.")
    st.info("Lưu ý: Bạn phải dán đúng định dạng [connections.gsheets] vào Secrets.")
    st.stop()

st.title("🏫 Hệ Thống Quản Lý Nội Trú")

# Giao diện Tabs đơn giản
tab_dk, tab_gv, tab_ql = st.tabs(["Học sinh", "Giáo viên", "Quản lý"])

with tab_dk:
    st.subheader("Đăng ký ra ngoài")
    with st.form("f_dk", clear_on_submit=True):
        ten = st.text_input("Họ tên học sinh:")
        lop = st.selectbox("Lớp:", ["10A1", "10A2", "11A1", "11A2", "12A1", "12A2"])
        ly_do = st.text_area("Lý do và thông tin người đón:")
        submit = st.form_submit_button("Gửi đơn")
        
        if submit and ten:
            new_id = len(df) + 1
            new_data = pd.DataFrame([{"Mã Đơn": new_id, "Họ Tên": ten, "Lớp": lop, "Chi Tiết Người Đón": ly_do, "GVCN Duyệt": "Chờ duyệt", "Quản lý Duyệt": "Chờ duyệt", "Trạng Thái": "Đang xử lý"}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet=SHEET_NAME, data=updated_df)
            st.success(f"Thành công! Mã đơn: {new_id}")

with tab_gv:
    st.write("Dành cho Giáo viên xác nhận...")

with tab_ql:
    st.write("Dành cho Ban giám hiệu phê duyệt...")
