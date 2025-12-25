import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CẤU HÌNH HỆ THỐNG ---
PASS_GVCN = "gv123"
PASS_QUANLY = "admin123"
SHEET_NAME = "Trangtính1" 

# Khởi tạo kết nối
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Đọc dữ liệu từ Google Sheets
        df = conn.read(worksheet=SHEET_NAME, ttl=0)
        return df.dropna(how="all")
    except Exception:
        # Nếu lỗi (Sheet trống), tạo DataFrame khung
        return pd.DataFrame(columns=[
            "Mã Đơn", "Họ Tên", "Lớp", "Loại Hình", "Chi Tiết Người Đón", 
            "CCCD Người Đón", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái"
        ])

st.set_page_config(page_title="Quản lý Nội trú", layout="wide")
st.title("🏫 Quản lý Học sinh Ra ngoài & Về quê")

menu = st.sidebar.selectbox("Chọn vai trò:", ["Học sinh đăng ký", "Giáo viên chủ nhiệm", "Quản lý HS/ Ban Giám Hiệu"])

if menu == "Học sinh đăng ký":
    st.header("📝 Đăng ký Ra ngoài / Về quê")
    with st.form("form_dang_ky", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ten = st.text_input("Họ và Tên học sinh:")
            lop = st.selectbox("Chọn Lớp:", ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        with col2:
            loai_hinh = st.selectbox("Loại hình ra ngoài:", ["Ra ngoài trong ngày", "Đi khám / Ốm nằm viện", "Về nhà cuối tuần"])
        
        chi_tiet = st.text_area("Lý do / Chi tiết người đón:")
        cccd = st.text_input("Số CCCD người đón (nếu có):")

        if st.form_submit_button("Gửi đơn đăng ký"):
            if not ten:
                st.error("Vui lòng nhập họ tên!")
            else:
                try:
                    # Tải dữ liệu hiện tại
                    df_existing = load_data()
                    
                    # Tính toán ID mới
                    if not df_existing.empty and "Mã Đơn" in df_existing.columns:
                        new_id = int(pd.to_numeric(df_existing["Mã Đơn"], errors='coerce').max() + 1)
                    else:
                        new_id = 1
                    
                    # Tạo dòng dữ liệu mới
                    new_row = pd.DataFrame([{
                        "Mã Đơn": new_id, 
                        "Họ Tên": ten, 
                        "Lớp": lop, 
                        "Loại Hình": loai_hinh, 
                        "Chi Tiết Người Đón": chi_tiet, 
                        "CCCD Người Đón": cccd, 
                        "GVCN Duyệt": "Chờ duyệt", 
                        "Quản lý Duyệt": "Chờ duyệt", 
                        "Trạng Thái": "Đang xử lý"
                    }])
                    
                    # Kết hợp và cập nhật
                    updated_df = pd.concat([df_existing, new_row], ignore_index=True)
                    conn.update(worksheet=SHEET_NAME, data=updated_df)
                    
                    # Xóa cache để hiển thị dữ liệu mới ngay lập tức
                    st.cache_data.clear() 
                    st.success(f"✅ Gửi thành công! Mã đơn: {new_id}")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
                    st.info("Hãy đảm bảo bạn đã cấp quyền 'Editor' cho Email Service Account trong Google Sheets.")
