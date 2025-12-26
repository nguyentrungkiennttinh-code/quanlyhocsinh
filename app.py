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
        # Sử dụng Secrets để bảo mật (Khuyên dùng cho Streamlit Cloud)
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        else:
            # Fallback cho chạy local nếu có file key.json
            creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
        
        client = gspread.authorize(creds)
        # Đảm bảo tên file Google Sheet chính xác 100%
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

# 2. GIAO DIỆN CHÍNH
st.set_page_config(page_title="Quản lý Nội trú Hà Giang", layout="wide")
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

# --- XỬ LÝ TRANG HỌC SINH ---
if st.session_state.page == "HỌC SINH":
    st.subheader("📝 Học sinh đăng ký xin nghỉ")
    with st.form("form_dk", clear_on_submit=True):
        ten = st.text_input("Họ và tên học sinh:")
        lop = st.selectbox("Lớp:", LIST_LOP)
        loai = st.radio("Loại hình:", ["Về cuối tuần", "Ra ngoài trong ngày", "Đi khám bệnh"], horizontal=True)
        lydo = st.text_input("Lý do cụ thể:")
        
        cach_thuc = "N/A"; nguoi_don = "N/A"; cccd = "N/A"
        if loai == "Về cuối tuần":
            st.markdown("---")
            st.info("🏠 **Thông tin đưa đón cuối tuần**")
            cach_thuc = st.radio("Hình thức di chuyển:", ["Có người thân đón", "Tự về bằng xe khách"], horizontal=True)
            if cach_thuc == "Có người thân đón":
                c1, c2 = st.columns(2)
                with c1:
                    nguoi_don = st.selectbox("Người thân đón là:", ["Bố", "Mẹ", "Ông", "Bà", "Anh/Chị", "Người thân khác"])
                with c2:
                    cccd = st.text_input("Số CCCD người đón:", placeholder="Dùng để đối chiếu tại cổng")
        
        if st.form_submit_button("GỬI ĐƠN XÁC NHẬN", use_container_width=True):
            if ten and lydo:
                worksheet.append_row([ten, lop, loai, lydo, cach_thuc, nguoi_don, cccd, "Chờ GVCN duyệt", "Chưa vào"])
                st.success("✅ Gửi thành công! Hãy báo GVCN lớp duyệt đơn.")

# --- XỬ LÝ TRANG TỰ QUẢN (Sửa lỗi Syntax hình image_95dfb5.png) ---
elif st.session_state.page == "TUQUAN":
    st.subheader("🛡️ Đội Tự quản trực cổng")
    if st.text_input("Mật khẩu Tự quản:", type="password") == "tuquan123":
        df = load_data()
        tab_ra, tab_vao = st.tabs(["🚪 XÁC NHẬN RA", "🏠 XÁC NHẬN VÀO"])
        
        with tab_ra:
            df_ra = df[df['Trạng Thái'] == 'Đã cấp phép']
            if not df_ra.empty:
                for i, row in df_ra.iterrows():
                    with st.container(border=True):
                        st.write(f"✅ **{row['Họ Tên']}** ({row['Lớp']})")
                        if st.button("XÁC NHẬN CHO RA", key=f"out_{i}"):
                            worksheet.update_cell(i + 2, 8, "Đang ở ngoài")
                            st.rerun()
        with tab_vao:
            df_vao = df[df['Trạng Thái'] == 'Đang ở ngoài']
            if not df_vao.empty:
                for i, row in df_vao.iterrows():
                    with st.container(border=True):
                        st.write(f"🔔 **{row['Họ Tên']}** - Lớp {row['Lớp']}")
                        if st.button("XÁC NHẬN ĐÃ VÀO", key=f"in_{i}"):
                            worksheet.update_cell(i + 2, 9, get_now_vn())
                            worksheet.update_cell(i + 2, 8, "Đã vào trường")
                            st.rerun()
