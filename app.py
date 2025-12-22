import streamlit as st
import pandas as pd
import os

# --- CẤU HÌNH ---
FILE_LUU_TRU = "du_lieu_ra_ngoai.xlsx"
PASS_GVCN = "gv123"
PASS_QUANLY = "admin123"

st.set_page_config(page_title="Quản lý học sinh ra ngoài", layout="wide")
st.title("🏫 Quản lý Học sinh Ra ngoài Hàng tuần")

# --- HÀM LƯU VÀ ĐỌC DỮ LIỆU ---
def load_data():
    if os.path.exists(FILE_LUU_TRU):
        try:
            return pd.read_excel(FILE_LUU_TRU)
        except:
            pass
    return pd.DataFrame(columns=[
        "Mã Đơn", "Tên Học Sinh", "Lớp", "Loại Đơn", "Ngày Đi", "Ngày Về", 
        "Hình Thức/Người Đón", "Thông tin bổ sung", "CCCD/Ghi chú",
        "Lý Do", "GVCN Duyệt", "Quản Lý Duyệt", "Trạng Thái Tổng"
    ])

def save_data(df):
    df.to_excel(FILE_LUU_TRU, index=False)

if 'db_requests' not in st.session_state:
    st.session_state.db_requests = load_data()

DANH_SACH_LOP = ["10A1", "10A2", "10A3","10A4","10A5","10A6","11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A1","12A2","12A3","12A4","12A5"]
# Cập nhật thêm lựa chọn Khám bệnh
LOAI_DON = ["Ra ngoài một lúc rồi vào", "Về nghỉ cuối tuần/Về nhà", "Đi khám bệnh / Ốm đi nằm viện"]
NGUOI_DON_LIST = ["Bố", "Mẹ", "Ông", "Bà", "Người thân khác", "Tự về bằng xe khách"]

# --- MENU ---
menu = st.sidebar.selectbox("VAI TRÒ:", ["Học sinh (Đăng ký)", "Giáo viên chủ nhiệm", "Quản lý HS / Ban Giám Hiệu"])

# 1. GIAO DIỆN HỌC SINH
if menu == "Học sinh (Đăng ký)":
    st.header("📝 Phiếu đăng ký ra ngoài")
    
    with st.form("form_hocsinh"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📍 Thông tin cơ bản")
            name = st.text_input("Họ và tên học sinh:")
            grade = st.selectbox("Lớp:", DANH_SACH_LOP)
            loai_don_chon = st.radio("Mục đích ra ngoài:", LOAI_DON)
            d_out = st.date_input("Ngày đi:", format="DD/MM/YYYY")
            d_in = st.date_input("Ngày về dự kiến:", format="DD/MM/YYYY")
            
        with col2:
            st.subheader("🔍 Chi tiết di chuyển & Đón tiếp")
            reason = st.text_area("Lý do cụ thể (Ghi rõ tình trạng ốm, ra ngoài làm gì...):")
            
            hinh_thuc_final = "N/A"
            info_bo_sung = ""
            ghi_chu_cccd = ""
            
            if loai_don_chon == "Về nghỉ cuối tuần/Về nhà":
                hinh_thuc_final = st.selectbox("Ai đón bạn hoặc phương tiện:", NGUOI_DON_LIST)
                if hinh_thuc_final != "Tự về bằng xe khách":
                    ghi_chu_cccd = st.text_input(f"Số CCCD của {hinh_thuc_final.lower()}:")
            
            elif loai_don_chon == "Đi khám bệnh / Ốm đi nằm viện":
                info_bo_sung = st.text_input("Tên bệnh viện / Phòng khám:")
                hinh_thuc_final = st.selectbox("Người đưa đi/đón:", ["Nhà trường đưa đi", "Gia đình đón đi", "Tự đi"])
                if hinh_thuc_final == "Gia đình đón đi":
                    ghi_chu_cccd = st.text_input("Tên người thân & Số CCCD:")

        if st.form_submit_button("GỬI ĐƠN ĐĂNG KÝ"):
            if name and reason:
                new_id = len(st.session_state.db_requests) + 1
                new_row = {
                    "Mã Đơn": new_id, "Tên Học Sinh": name, "Lớp": grade,
                    "Loại Đơn": loai_don_chon,
                    "Ngày Đi": d_out.strftime("%d/%m/%Y"), "Ngày Về": d_in.strftime("%d/%m/%Y"),
                    "Hình Thức/Người Đón": hinh_thuc_final,
                    "Thông tin bổ sung": info_bo_sung,
                    "CCCD/Ghi chú": ghi_chu_cccd,
                    "Lý Do": reason, "GVCN Duyệt": "Chờ duyệt", 
                    "Quản Lý Duyệt": "Chờ duyệt", "Trạng Thái Tổng": "Chờ GVCN duyệt"
                }
                st.session_state.db_requests = pd.concat([st.session_state.db_requests, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db_requests)
                st.success(f"Gửi đơn thành công! Mã đơn: {new_id}")
            else:
                st.error("Vui lòng điền Họ tên và Lý do.")

# 2. GIAO DIỆN GIÁO VIÊN (Giữ nguyên logic bảo mật)
elif menu == "Giáo viên chủ nhiệm":
    st.header("👨‍🏫 Khu vực Giáo viên")
    pw = st.text_input("Mật khẩu Giáo viên:", type="password")
    if pw == PASS_GVCN:
        lop = st.selectbox("Chọn lớp quản lý:", DANH_SACH_LOP)
        df = st.session_state.db_requests
        df_lop = df[(df["Lớp"] == lop) & (df["GVCN Duyệt"] == "Chờ duyệt")]
        st.dataframe(df_lop)
        id_d = st.number_input("Mã đơn duyệt:", step=1, min_value=0)
        if st.button("✅ DUYỆT ĐƠN"):
            if id_d in df_lop["Mã Đơn"].values:
                st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_d, "GVCN Duyệt"] = "Đã xác nhận"
                save_data(st.session_state.db_requests)
                st.rerun()


# 3. GIAO DIỆN QUẢN LÝ
elif menu == "Quản lý HS/ Ban Giám Hiệu":
    st.header("🛡️ Khu vực Quản lý HS / Ban Giám Hiệu")
    pw_a = st.text_input("Mật khẩu Quản lý:", type="password")
    if pw_a == PASS_QUANLY:
        df = st.session_state.db_requests
        # Lọc đơn: GVCN đã xác nhận và Quản lý chưa duyệt
        df_loc = df[(df["GVCN Duyệt"] == "Đã xác nhận") & (df["Quản lý Duyệt"] == "Chờ duyệt")]
        st.dataframe(df_loc)
            
        id_f = st.number_input("Mã đơn cấp phép:", step=1, min_value=0)
        if st.button("🚀 CẤP PHÉP CHÍNH THỨC"):
            if id_f in df["Mã Đơn"].values:
                st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_f, "Quản lý Duyệt"] = "ĐÃ DUYỆT"
                st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_f, "Trạng Thái Tổng"] = "Hợp lệ"
                save_data(st.session_state.db_requests)
                st.success(f"Đã cấp phép thành công cho mã đơn {id_f}!")
                st.rerun()
            else:
                st.error("Mã đơn không tồn tại hoặc không nằm trong danh sách chờ!")
            
        st.download_button("📩 Tải báo cáo Excel", df.to_csv(index=False).encode('utf-8-sig'), "danh_sach.csv", "text/csv")