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
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
        client = gspread.authorize(creds)
        # Đảm bảo tên file Google Sheet này đã được chia sẻ quyền chỉnh sửa cho email của bot
        return client.open("Quản lý nội trú").get_worksheet(0)
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        st.stop()

worksheet = get_worksheet()

def load_data():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

def get_now_vn():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz).strftime("%H:%M %d/%m/%Y")

# 2. GIAO DIỆN
st.set_page_config(page_title="Quản lý Nội trú Hà Giang", layout="wide")
st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>HỆ THỐNG QUẢN LÝ NỘI TRÚ</h2>", unsafe_allow_html=True)

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
LIST_LOP = [f"{k}A{i}" for k in [10, 11, 12] for i in range(1, 7)]

# --- LOGIC XỬ LÝ TỪNG TRANG ---
if st.session_state.page == "HỌC SINH":
    st.subheader("📝 Đăng ký xin nghỉ")
    with st.form("form_dk", clear_on_submit=True):
        ten = st.text_input("Họ và tên:")
        lop = st.selectbox("Lớp:", LIST_LOP)
        loai = st.radio("Loại hình:", ["Về cuối tuần", "Ra ngoài", "Khám bệnh"], horizontal=True)
        lydo = st.text_input("Lý do:")
        if st.form_submit_button("GỬI ĐƠN"):
            if ten and lydo:
                worksheet.append_row([ten, lop, loai, lydo, "N/A", "N/A", "N/A", "Chờ GVCN duyệt", "Chưa vào"])
                st.success("✅ Gửi thành công!")

elif st.session_state.page == "TUQUAN":
    st.subheader("🛡️ Đội Tự quản trực cổng")
    if st.text_input("Mật khẩu Tự quản:", type="password") == "tuquan123":
        df = load_data()
        t1, t2 = st.tabs(["🚪 RA", "🏠 VÀO"])
        with t1:
            df_ra = df[df['Trạng Thái'] == 'Đã cấp phép']
            for i, row in df_ra.iterrows():
                if st.button(f"Xác nhận RA: {row['Họ Tên']}", key=f"ra_{i}"):
                    worksheet.update_cell(i + 2, 8, "Đang ở ngoài")
                    st.rerun()
        with t2:
            df_vao = df[df['Trạng Thái'] == 'Đang ở ngoài']
            for i, row in df_vao.iterrows():
                if st.button(f"Xác nhận VÀO: {row['Họ Tên']}", key=f"in_{i}"):
                    worksheet.update_cell(i + 2, 8, "Đã vào trường")
                    worksheet.update_cell(i + 2, 9, get_now_vn())
                    st.rerun()
