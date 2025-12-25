import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CẤU HÌNH HỆ THỐNG ---
PASS_GVCN = "gv123"
PASS_QUANLY = "admin123"

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Hàm đọc dữ liệu mới nhất từ Sheets (Không dùng bộ nhớ đệm để đồng bộ tức thì)
def load_data():
    try:
        df = conn.read(worksheet="Trang tính1", ttl=0)
        return df.dropna(how="all")
    except:
        # Nếu Sheets trống, tạo khung dữ liệu chuẩn
        return pd.DataFrame(columns=[
            "Mã Đơn", "Họ Tên", "Lớp", "Loại Hình", "Chi Tiết Người Đón", 
            "CCCD Người Đón", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái"
        ])

st.set_page_config(page_title="Quản lý Nội trú", layout="wide")
st.title("🏫 Quản lý Học sinh Ra ngoài & Về quê")

# Menu điều hướng
st.sidebar.header("DANH MỤC")
menu = st.sidebar.selectbox("Chọn vai trò:", ["Học sinh đăng ký", "Giáo viên chủ nhiệm", "Quản lý HS/ Ban Giám Hiệu"])

# 1. GIAO DIỆN HỌC SINH
if menu == "Học sinh đăng ký":
    st.header("📝 Đăng ký Ra ngoài / Về quê")
    with st.form("form_dang_ky"):
        col1, col2 = st.columns(2)
        with col1:
            ten = st.text_input("Họ và Tên học sinh:")
            lop = st.selectbox("Chọn Lớp:", ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        with col2:
            loai_hinh = st.selectbox("Loại hình ra ngoài:", ["Ra ngoài trong ngày", "Đi khám / Ốm nằm viện", "Về nhà cuối tuần"])
        
        chi_tiet = ""
        cccd = ""
        if loai_hinh == "Về nhà cuối tuần":
            st.markdown("---")
            nguoi_don = st.selectbox("Ai đón bạn?", ["Bố đón", "Mẹ đón", "Ông đón", "Bà đón", "Người thân khác đón", "Tự đi xe khách về"])
            if nguoi_don != "Tự đi xe khách về":
                c1, c2 = st.columns(2)
                with c1: ten_don = st.text_input("Họ tên người đón (Nếu có):")
                with c2: cccd_val = st.text_input("Số CCCD người đón (Nếu có):")
                chi_tiet = f"{nguoi_don}: {ten_don}"
                cccd = cccd_val
            else:
                chi_tiet = "Tự đi xe khách về"
        else:
            chi_tiet = st.text_area("Lý do cụ thể:")

        if st.form_submit_button("Gửi đơn đăng ký") and ten:
            df_existing = load_data()
            new_id = len(df_existing) + 1
            new_row = pd.DataFrame([[new_id, ten, lop, loai_hinh, chi_tiet, cccd, "Chờ duyệt", "Chờ duyệt", "Đang xử lý"]], 
                                   columns=df_existing.columns)
            
            # Lưu trực tiếp lên Google Sheets
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(worksheet="Trang tính1", data=updated_df)
            st.success(f"✅ Gửi đơn thành công! Mã đơn: {new_id}")

# 2. GIAO DIỆN GIÁO VIÊN
elif menu == "Giáo viên chủ nhiệm":
    st.header("👨‍🏫 Xác nhận của GVCN")
    pw = st.text_input("Mật khẩu Giáo viên:", type="password")
    if pw == PASS_GVCN:
        lop_ql = st.selectbox("Lớp quản lý:", ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        df = load_data() # Đọc dữ liệu từ Sheets
        df_show = df[(df["Lớp"] == lop_ql) & (df["GVCN Duyệt"] == "Chờ duyệt")]
        
        st.dataframe(df_show, use_container_width=True)
        id_gv = st.number_input("Mã đơn xác nhận:", step=1, min_value=0)
        
        if st.button("Xác nhận Đơn"):
            if id_gv in df_show["Mã Đơn"].values:
                df.loc[df["Mã Đơn"] == id_gv, "GVCN Duyệt"] = "Đã xác nhận"
                conn.update(worksheet="Trang tính1", data=df) # Cập nhật Sheets
                st.success(f"Đã xác nhận thành công đơn số {id_gv}!")
                st.rerun()

# 3. GIAO DIỆN QUẢN LÝ / BGH
elif menu == "Quản lý HS/ Ban Giám Hiệu":
    st.header("🛡️ Phê duyệt của Ban Giám Hiệu")
    pw_ad = st.text_input("Mật khẩu Quản lý:", type="password")
    if pw_ad == PASS_QUANLY:
        df_all = load_data()
        st.subheader("📋 Đơn đang chờ phê duyệt")
        df_admin = df_all[(df_all["GVCN Duyệt"] == "Đã xác nhận") & (df_all["Quản lý Duyệt"] == "Chờ duyệt")]
        st.dataframe(df_admin, use_container_width=True)
        
        id_ql = st.number_input("Mã đơn phê duyệt:", step=1, min_value=0)
        if st.button("🚀 CẤP PHÉP CHÍNH THỨC"):
            if id_ql in df_admin["Mã Đơn"].values:
                df_all.loc[df_all["Mã Đơn"] == id_ql, "Quản lý Duyệt"] = "ĐÃ DUYỆT"
                df_all.loc[df_all["Mã Đơn"] == id_ql, "Trạng Thái"] = "Hợp lệ"
                conn.update(worksheet="Trang tính1", data=df_all) # Cập nhật Sheets
                st.success(f"Đã duyệt đơn số {id_ql}")
                st.rerun()
        
        st.markdown("---")
        st.subheader("📥 Xuất dữ liệu báo cáo")
        if not df_all.empty:
            csv = df_all.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📩 Tải toàn bộ danh sách (File Excel/CSV)",
                data=csv,
                file_name="danh_sach_cap_phep.csv",
                mime="text/csv",
            )
