import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CẤU HÌNH ---
SHEET_NAME = "Trangtính1" 

conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet=SHEET_NAME, ttl=0)
        return df.dropna(how="all")
    except Exception:
        return pd.DataFrame(columns=["Mã Đơn", "Họ Tên", "Lớp", "Loại Hình", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái"])

st.title("🏫 Quản lý Nội trú")
menu = st.sidebar.selectbox("Vai trò:", ["Học sinh", "Giáo viên"])

if menu == "Học sinh":
    with st.form("form_dk"):
        ten = st.text_input("Họ và Tên:")
        lop = st.selectbox("Lớp:", ["10A1", "11A1", "12A1"])
        submit = st.form_submit_button("Gửi đơn")
        
        if submit:
            if not ten:
                st.error("Nhập tên!")
            else:
                df_old = load_data()
                new_id = len(df_old) + 1
                new_row = pd.DataFrame([{"Mã Đơn": new_id, "Họ Tên": ten, "Lớp": lop, "GVCN Duyệt": "Chờ", "Quản lý Duyệt": "Chờ", "Trạng Thái": "Đang xử lý"}])
                updated_df = pd.concat([df_old, new_row], ignore_index=True)
                conn.update(worksheet=SHEET_NAME, data=updated_df)
                st.success(f"Gửi thành công! Mã: {new_id}")
                st.cache_data.clear()
