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
        # Đảm bảo file key.json nằm cùng thư mục với file app.py
        creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
        client = gspread.authorize(creds)
        sh = client.open("Quản lý nội trú") 
        return sh.get_worksheet(0)
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

if 'page' not in st.session_state: st.session_state.page = "HỌC SINH"

# MENU ĐIỀU HƯỚNG
cols = st.columns(5)
btns = ["📝 HỌC SINH", "👨‍🏫 GVCN", "🏛️ BGH", "📋 BQLHS", "🛡️ TỰ QUẢN"]
pages = ["HỌC SINH", "GVCN", "BGH", "QLHS", "TUQUAN"]
for col, btn, pg in zip(cols, btns, pages):
    if col.button(btn, use_container_width=True): st.session_state.page = pg

st.divider()

LIST_LOP = ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3", "11A4", "11A5", "11A6", "12A1", "12A2", "12A3", "12A4", "12A5", "12A6"]

# --- 1. HỌC SINH ĐĂNG KÝ ---
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

# --- 2. GVCN DUYỆT ---
elif st.session_state.page == "GVCN":
    st.subheader("👨‍🏫 Giáo viên chủ nhiệm phê duyệt")
    if st.text_input("Mật khẩu GVCN:", type="password") == "gv123":
        chon_lop = st.selectbox("Chọn lớp bạn chủ nhiệm:", LIST_LOP)
        df = load_data()
        df_gv = df[(df['Trạng Thái'] == 'Chờ GVCN duyệt') & (df['Lớp'] == chon_lop)]
        
        if not df_gv.empty:
            for i, row in df_gv.iterrows():
                with st.container(border=True):
                    st.write(f"👤 **{row['Họ Tên']}** | Đơn: {row['Loại Hình']}")
                    if st.button(f"Duyệt cho {row['Họ Tên']}", key=f"gv_{i}"):
                        next_st = "Chờ BGH duyệt" if row['Loại Hình'] == "Về cuối tuần" else "Chờ QLHS duyệt"
                        worksheet.update_cell(i + 2, 8, next_st)
                        st.rerun()
        else: st.info(f"Lớp {chon_lop} hiện không có đơn chờ duyệt.")

# --- 3. BGH DUYỆT ---
elif st.session_state.page == "BGH":
    st.subheader("🏛️ Ban Giám Hiệu phê duyệt (Về cuối tuần)")
    if st.text_input("Mật khẩu BGH:", type="password") == "bgh123":
        df = load_data()
        df_bgh = df[(df['Loại Hình'] == 'Về cuối tuần') & (df['Trạng Thái'] == 'Chờ BGH duyệt')]
        if not df_bgh.empty:
            for i, row in df_bgh.iterrows():
                with st.container(border=True):
                    st.write(f"✅ **{row['Họ Tên']}** - Lớp {row['Lớp']}")
                    st.write(f"🚗 {row['Cách Thức']} | Người đón: {row['Người Đón']} | CCCD: {row['CCCD']}")
                    if st.button("BGH Phê duyệt", key=f"bgh_{i}"):
                        worksheet.update_cell(i + 2, 8, "Đã cấp phép")
                        st.rerun()
        else: st.info("Không có đơn về cuối tuần nào chờ duyệt.")

# --- 4. BQLHS DUYỆT & XUẤT BÁO CÁO ---
elif st.session_state.page == "QLHS":
    st.subheader("📋 Ban Quản lý học sinh (Duyệt & Báo cáo)")
    if st.text_input("Mật khẩu QLHS:", type="password") == "qlhs123":
        df = load_data()

        # --- PHẦN 1: TẢI BÁO CÁO ---
        with st.expander("📊 Tải dữ liệu tổng hợp báo cáo"):
            col_down1, col_down2 = st.columns(2)
            
            # Xuất toàn bộ danh sách (Hỗ trợ tiếng Việt Excel)
            csv_full = df.to_csv(index=False).encode('utf-8-sig')
            col_down1.download_button(
                label="📥 Tải toàn bộ danh sách (CSV)",
                data=csv_full,
                file_name=f"bao_cao_tong_hop_{datetime.now().strftime('%d_%m_%Y')}.csv",
                mime="text/csv",
            )
            
            # Xuất danh sách học sinh đang ở ngoài trường
            df_ngoai = df[df['Trạng Thái'] == 'Đang ở ngoài']
            csv_ngoai = df_ngoai.to_csv(index=False).encode('utf-8-sig')
            col_down2.download_button(
                label="🏃 Tải DS HS đang ở ngoài (CSV)",
                data=csv_ngoai,
                file_name=f"ds_hoc_sinh_dang_ngoai_{datetime.now().strftime('%Hh%M_%d_%m')}.csv",
                mime="text/csv",
            )
            st.caption("💡 Lưu ý: Mở file bằng Excel để xem định dạng tiếng Việt chuẩn nhất.")

        st.divider()

        # --- PHẦN 2: DUYỆT ĐƠN ---
        st.write("🔍 **Đơn chờ duyệt (Ra ngoài/Khám bệnh):**")
        df_ql = df[(df['Loại Hình'] != 'Về cuối tuần') & (df['Trạng Thái']
