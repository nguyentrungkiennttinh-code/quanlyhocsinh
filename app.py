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
            # Chuyển Secrets sang dict
            info = dict(st.secrets["gcp_service_account"])
            
            # --- ĐOẠN SỬA QUAN TRỌNG: Xử lý lỗi "Incorrect padding" ---
            # Tự động thay thế các ký tự thoát dòng nếu có để đảm bảo định dạng Base64 chuẩn
            if "private_key" in info:
                info["private_key"] = info["private_key"].replace("\\n", "\n")
            # --------------------------------------------------------

            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
            client = gspread.authorize(creds)
            
            # Tên file Google Sheet phải khớp chính xác tuyệt đối
            sh = client.open("Quản lý nội trú") 
            return sh.get_worksheet(0)
        else:
            st.error("Chưa cấu hình Secrets trên Streamlit Cloud!")
            st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        st.info("Kiểm tra lại: 1. Đã chia sẻ File cho Email Bot chưa? 2. Định dạng private_key trong Secrets đã đúng chưa?")
        st.stop()

# Khởi tạo kết nối
worksheet = get_worksheet()

def load_data():
    try:
        # Lấy toàn bộ dữ liệu từ Sheet
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

def get_now_vn():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz).strftime("%H:%M %d/%m/%Y")

# 2. GIAO DIỆN CHÍNH
st.set_page_config(page_title="Quản lý Nội trú", layout="wide")
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>HỆ THỐNG QUẢN LÝ NỘI TRÚ THPT HÀ GIANG</h2>", unsafe_allow_html=True)

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
LIST_LOP = ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "12A1", "12A2", "12A3", "12A4", "12A5", "12A6"]

# --- XỬ LÝ NỘI DUNG TỪNG TRANG ---
if st.session_state.page == "HỌC SINH":
    st.subheader("📝 Học sinh đăng ký xin nghỉ")
    with st.form("form_dk", clear_on_submit=True):
        ten = st.text_input("Họ và tên học sinh:")
        lop = st.selectbox("Lớp:", LIST_LOP)
        loai = st.radio("Loại hình:", ["Về cuối tuần", "Ra ngoài trong ngày", "Đi khám bệnh"], horizontal=True)
        lydo = st.text_input("Lý do cụ thể:")
        if st.form_submit_button("GỬI ĐƠN XÁC NHẬN", use_container_width=True):
            if ten and lydo:
                # Ghi dữ liệu: Cột H (Trạng thái) = Chờ GVCN duyệt, Cột I (Thời gian vào) = Chưa vào
