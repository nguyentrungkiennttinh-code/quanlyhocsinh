import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Cấu hình giao diện
st.set_page_config(page_title="Quản lý Học sinh", layout="wide")
st.title("🏫 Hệ Thống Quản Lý Nội Trú")

# Tên trang tính chính xác
SHEET_NAME = "trangtính1"

# Khối kết nối (Dòng này thường gây lỗi binascii nếu Secrets sai)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=SHEET_NAME, ttl=0)
    st.success("✅ Kết nối thành công!")
except Exception as e:
    st.error(f"❌ Lỗi kết nối: {e}")
    st.info("Kiểm tra lại Secrets: Đảm bảo private_key nằm trên một dòng duy nhất và dùng ký tự \\n.")
    st.stop()

# Hiển thị dữ liệu và Form đăng ký
st.subheader("Bảng dữ liệu hiện tại")
st.dataframe(df.dropna(how="all"), use_container_width=True)

with st.expander("📝 Đăng ký ra ngoài/về quê mới"):
    with st.form("form_dang_ky"):
        ten = st.text_input("Họ và Tên:")
        lop = st.selectbox("Lớp:", ["12A1", "12A2", "11A1", "11A2", "10A1", "10A2"])
        loai = st.selectbox("Loại hình:", ["Ra ngoài trong ngày", "Về quê"])
        ly_do = st.text_area("Chi tiết lý do/Người đón:")
        
        if st.form_submit_button("Gửi đơn đăng ký"):
            if ten:
                new_id = int(df["Mã Đơn"].max() + 1) if not df.empty else 1
                new_row = pd.DataFrame([{
                    "Mã Đơn": new_id, "Họ Tên": ten, "Lớp": lop, 
                    "Loại Hình": loai, "Chi Tiết Người Đón": ly_do,
                    "GVCN Duyệt": "Chờ duyệt", "Quản lý Duyệt": "Chờ duyệt", "Trạng Thái": "Đang xử lý"
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet=SHEET_NAME, data=updated_df)
                st.cache_data.clear()
                st.success(f"Gửi đơn thành công! Mã số đơn: {new_id}")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên học sinh.")
