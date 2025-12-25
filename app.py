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
        return pd.DataFrame(columns=[
            "Mã Đơn", "Họ Tên", "Lớp", "Loại Hình", "Chi Tiết Người Đón", 
            "CCCD Người Đón", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái"
        ])

st.title("🏫 Quản lý Nội trú")

df_existing = load_data()

with st.form("form_dang_ky", clear_on_submit=True):
    ten = st.text_input("Họ và Tên học sinh:")
    lop = st.selectbox("Chọn Lớp:", ["10A1", "11A1", "12A1"])
    loai_hinh = st.selectbox("Loại hình:", ["Ra ngoài", "Về quê"])
    chi_tiet = st.text_area("Lý do:")
    
    if st.form_submit_button("Gửi đơn"):
        if not ten:
            st.error("Vui lòng nhập họ tên!")
        else:
            new_id = int(pd.to_numeric(df_existing["Mã Đơn"]).max() + 1) if not df_existing.empty else 1
            new_row = pd.DataFrame([{
                "Mã Đơn": new_id, "Họ Tên": ten, "Lớp": lop, "Loại Hình": loai_hinh,
                "GVCN Duyệt": "Chờ duyệt", "Quản lý Duyệt": "Chờ duyệt", "Trạng Thái": "Đang xử lý"
            }])
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(worksheet=SHEET_NAME, data=updated_df)
            st.success("✅ Thành công!")
            st.cache_data.clear()
