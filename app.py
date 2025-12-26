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
        
        # Kiểm tra nếu cấu hình trong Streamlit Secrets (Bảo mật hơn)
        if "gcp_service_account" in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        else:
            # Nếu không có Secrets thì dùng file local key.json
            creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
            
        client = gspread.authorize(creds)
        sh = client.open("Quản lý nội trú") 
        return sh.get_worksheet(0)
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Google Sheets: {e}")
        st.info("Mẹo: Đảm bảo bạn đã chia sẻ quyền 'Editor' cho email dịch vụ trong file JSON.")
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

LIST_LOP = [f"{k}A{i}" for k in [10, 11, 12] for i in range(1, 7)]

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
    pw = st.text_input("Mật khẩu GVCN:", type="password")
    if pw == "gv123":
        chon_lop = st.selectbox("Chọn lớp bạn chủ nhiệm:", LIST_LOP)
        df = load_data()
        if not df.empty:
            df_gv = df[(df['Trạng Thái'] == 'Chờ GVCN duyệt') & (df['Lớp'] == chon_lop)]
            if not df_gv.empty:
                for i, row in df_gv.iterrows():
                    with st.container(border=True):
                        st.write(f"👤 **{row['Họ Tên']}** | Đơn: {row['Loại Hình']}")
                        if st.button(f"Duyệt cho {row['Họ Tên']}", key=f"gv_{i}"):
                            next_st = "Chờ BGH duyệt" if row['Loại Hình'] == "Về cuối tuần" else "Chờ QLHS duyệt"
                            # i + 2 vì dòng 1 là tiêu đề và gspread tính index từ 1
                            worksheet.update_cell(i + 2, 8, next_st)
                            st.rerun()
            else: st.info(f"Lớp {chon_lop} hiện không có đơn chờ duyệt.")

# --- 3. BGH DUYỆT ---
elif st.session_state.page == "BGH":
    st.subheader("🏛️ Ban Giám Hiệu phê duyệt (Về cuối tuần)")
    if st.text_input("Mật khẩu BGH:", type="password") == "bgh123":
        df = load_data()
        if not df.empty:
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

# --- 4. BQLHS DUYỆT ---
elif st.session_state.page == "QLHS":
    st.subheader("📋 Ban Quản lý học sinh (Duyệt & Báo cáo)")
    if st.text_input("Mật khẩu QLHS:", type="password") == "qlhs123":
        df = load_data()
        with st.expander("📊 Tải dữ liệu báo cáo"):
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Tải danh sách tổng hợp (CSV)", data=csv, file_name="bao_cao.csv")
        
        st.divider()
        if not df.empty:
            df_ql = df[(df['Loại Hình'] != 'Về cuối tuần') & (df['Trạng Thái'] == 'Chờ QLHS duyệt')]
            if not df_ql.empty:
                for i, row in df_ql.iterrows():
                    with st.container(border=True):
                        st.write(f"🏥 **{row['Họ Tên']}** ({row['Lớp']}) xin {row['Loại Hình']}")
                        if st.button("BQLHS Phê duyệt", key=f"ql_{i}"):
                            worksheet.update_cell(i + 2, 8, "Đã cấp phép")
                            st.rerun()
            else: st.info("Không có đơn ra ngoài nào chờ duyệt.")

# --- 5. TỰ QUẢN ---
elif st.session_state.page == "TUQUAN":
    st.subheader("🛡️ Đội Tự quản trực cổng")
    if st.text_input("Mật khẩu Tự quản:", type="password") == "tuquan123":
        tab_ra, tab_vao = st.tabs(["🚪 XÁC NHẬN RA", "🏠 XÁC NHẬN VÀO"])
        df = load_data()
        if not df.empty:
            with tab_ra:
                df_ra = df[df['Trạng Thái'] == 'Đã cấp phép']
                for i, row in df_ra.iterrows():
                    with st.container(border=True):
                        st.write(f"✅ **{row['Họ Tên']}** ({row['Lớp']})")
                        if st.button("XÁC NHẬN CHO RA", key=f"out_{i}"):
                            worksheet.update_cell(i + 2, 8, "Đang ở ngoài")
                            st.rerun()
            with tab_vao:
                df_vao = df[(df['Trạng Thái'] == 'Đang ở ngoài')]
                for i, row in df_vao.iterrows():
                    with st.container(border=True):
                        st.write(f"🔔 **{row['Họ Tên']}** - Lớp {row['Lớp']}")
                        if st.button("XÁC NHẬN ĐÃ VÀO TRƯỜNG", key=f"in_{i}"):
                            worksheet.update_cell(i + 2, 9, get_now_vn())
                            worksheet.update_cell(i + 2, 8, "Đã vào trường")
                            st.rerun()
