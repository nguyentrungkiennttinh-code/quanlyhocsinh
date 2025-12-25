import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CẤU HÌNH ---
SHEET_NAME = "Trangtính1" 

# Kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(worksheet=SHEET_NAME, ttl=0)
        return df.dropna(how="all")
    except Exception:
        # Tạo bảng trống nếu lỗi hoặc sheet mới
        return pd.DataFrame(columns=[
            "Mã Đơn", "Họ Tên", "Lớp", "Loại Hình", "Chi Tiết Người Đón", 
            "CCCD Người Đón", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái"
        ])

st.set_page_config(page_title="Quản lý Nội trú", layout="wide")
st.title("🏫 Quản lý Học sinh Ra ngoài & Về quê")

menu = st.sidebar.selectbox("Vai trò:", ["Học sinh đăng ký", "Giáo viên chủ nhiệm"])

if menu == "Học sinh đăng ký":
    st.header("📝 Đăng ký Ra ngoài / Về quê")
    with st.form("form_dang_ky", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ten = st.text_input("Họ và Tên học sinh:")
            lop = st.selectbox("Chọn Lớp:", ["10A1", "10A2", "11A1", "12A1"])
        with col2:
            loai_hinh = st.selectbox("Loại hình:", ["Ra ngoài", "Về quê"])
        
        chi_tiet = st.text_area("Lý do / Người đón:")
        cccd = st.text_input("Số CCCD người đón:")

        if st.form_submit_button("Gửi đơn đăng ký"):
            if not ten:
                st.error("Vui lòng nhập họ tên!")
            else:
                try:
                    df_existing = load_data()
                    # Tính Mã Đơn tự động
                    if not df_existing.empty:
                        new_id = int(pd.to_numeric(df_existing["Mã Đơn"], errors='coerce').max() + 1)
                    else:
                        new_id = 1
                    
                    new_row = pd.DataFrame([{
                        "Mã Đơn": new_id, "Họ Tên": ten, "Lớp": lop, 
                        "Loại Hình": loai_hinh, "Chi Tiết Người Đón": chi_tiet, 
                        "CCCD Người Đón": cccd, "GVCN Duyệt": "Chờ duyệt", 
                        "Quản lý Duyệt": "Chờ duyệt", "Trạng Thái": "Đang xử lý"
                    }])
                    
                    updated_df = pd.concat([df_existing, new_row], ignore_index=True)
                    conn.update(worksheet=SHEET_NAME, data=updated_df)
                    st.cache_data.clear() 
                    st.success(f"✅ Gửi thành công! Mã đơn: {new_id}")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
