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
        sh = client.open("Quản lý nội trú") 
        return sh.get_worksheet(0)
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
st.markdown("<h2 style='text-align: center;'>HỆ THỐNG QUẢN LÝ NỘI TRÚ</h2>", unsafe_allow_html=True)

if 'page' not in st.session_state: 
    st.session_state.page = "HỌC SINH"

# MENU
cols = st.columns(5)
btns = ["📝 HỌC SINH", "👨‍🏫 GVCN", "🏛️ BGH", "📋 BQLHS", "🛡️ TỰ QUẢN"]
pages = ["HỌC SINH", "GVCN", "BGH", "QLHS", "TUQUAN"]
for col, btn, pg in zip(cols, btns, pages):
    if col.button(btn, use_container_width=True): 
        st.session_state.page = pg

LIST_LOP = ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "12A1", "12A2", "12A3", "12A4", "12A5", "12A6"]

# --- XỬ LÝ TRANG ---
if st.session_state.page == "HỌC SINH":
    with st.form("form_dk", clear_on_submit=True):
        ten = st.text_input("Họ và tên:")
        lop = st.selectbox("Lớp:", LIST_LOP)
        loai = st.radio("Loại:", ["Về cuối tuần", "Ra ngoài", "Khám bệnh"], horizontal=True)
        lydo = st.text_input("Lý do:")
        if st.form_submit_button("GỬI ĐƠN"):
            if ten and lydo:
                worksheet.append_row([ten, lop, loai, lydo, "N/A", "N/A", "N/A", "Chờ GVCN duyệt", "Chưa vào"])
                st.success("✅ Gửi thành công!")

elif st.session_state.page == "GVCN":
    if st.text_input("Mật khẩu:", type="password") == "gv123":
        df = load_data()
        if not df.empty:
            df_gv = df[df['Trạng Thái'] == 'Chờ GVCN duyệt']
            for i, row in df_gv.iterrows():
                st.write(f"👤 {row['Họ Tên']} - {row['Lớp']}")
                if st.button(f"Duyệt cho {row['Họ Tên']}", key=f"gv_{i}"):
                    next_st = "Chờ BGH duyệt" if row['Loại Hình'] == "Về cuối tuần" else "Chờ QLHS duyệt"
                    worksheet.update_cell(i + 2, 8, next_st)
                    st.rerun()

elif st.session_state.page == "TUQUAN":
    if st.text_input("Mật khẩu:", type="password") == "tuquan123":
        df = load_data()
        tab1, tab2 = st.tabs(["🚪 RA", "🏠 VÀO"])
        with tab1:
            df_ra = df[df['Trạng Thái'] == 'Đã cấp phép']
            for i, row in df_ra.iterrows():
                if st.button(f"Xác nhận RA: {row['Họ Tên']}", key=f"out_{i}"):
                    worksheet.update_cell(i + 2, 8, "Đang ở ngoài")
                    st.rerun()
        with tab2:
            df_vao = df[df['Trạng Thái'] == 'Đang ở ngoài']
            for i, row in df_vao.iterrows():
                if st.button(f"Xác nhận VÀO: {row['Họ Tên']}", key=f"in_{i}"):
                    worksheet.update_cell(i + 2, 8, "Đã vào trường")
                    worksheet.update_cell(i + 2, 9, get_now_vn())
                    st.rerun()
