import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

# 1. KẾT NỐI DỮ LIỆU
def get_worksheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            # Tự động sửa lỗi xuống dòng trong key
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
            client = gspread.authorize(creds)
            # Tên file phải khớp chính xác với ảnh image_a147e6.png
            sh = client.open("Quản lý nội trú") 
            return sh.get_worksheet(0)
        else:
            st.error("Chưa cấu hình Secrets trên Streamlit Cloud!")
            st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        st.stop()

worksheet = get_worksheet()

def load_data():
    try:
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

def get_now_vn():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz).strftime("%H:%M %d/%m/%Y")

# 2. GIAO DIỆN CHÍNH
st.set_page_config(page_title="Quản lý Nội trú", layout="wide")
st.markdown("<h2 style='text-align: center;'>HỆ THỐNG QUẢN LÝ NỘI TRÚ THPT HÀ GIANG</h2>", unsafe_allow_html=True)

if 'page' not in st.session_state: 
    st.session_state.page = "HỌC SINH"

# MENU ĐIỀU HƯỚNG
cols = st.columns(5)
btns = ["📝 HỌC SINH", "👨‍🏫 GVCN", "🏛️ BGH", "📋 BQLHS", "🛡️ TỰ QUẢN"]
pages = ["HỌC SINH", "GVCN", "BGH", "QLHS", "TUQUAN"]
for col, btn, pg in zip(cols, btns, pages):
    if col.button(btn, use_container_width=True): 
        st.session_state.page = pg

st.divider()

if st.session_state.page == "HỌC SINH":
    st.subheader("📝 Học sinh đăng ký xin nghỉ")
    with st.form("form_dk", clear_on_submit=True):
        ten = st.text_input("Họ và tên học sinh:")
        lop = st.selectbox("Lớp:", ["10A1", "10A2", "11A1", "11A2", "12A1", "12A2"])
        loai = st.radio("Loại hình:", ["Về cuối tuần", "Ra ngoài trong ngày", "Đi khám bệnh"], horizontal=True)
        lydo = st.text_input("Lý do cụ thể:")
        if st.form_submit_button("GỬI ĐƠN XÁC NHẬN"):
            if ten and lydo:
                # Ghi vào Sheet: Họ Tên, Lớp, Loại Hình, Lý Do, ..., Trạng Thái, Thời gian vào
                worksheet.append_row([ten, lop, loai, lydo, "N/A", "N/A", "N/A", "Chờ GVCN duyệt", "Chưa vào"])
                st.success("✅ Gửi đơn thành công!")
            else:
                st.warning("Vui lòng điền đủ thông tin.")
