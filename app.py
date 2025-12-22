import streamlit as st
import pandas as pd

# --- CẤU HÌNH HỆ THỐNG ---
PASS_GVCN = "gv123"
PASS_QUANLY = "admin123"

if 'db_requests' not in st.session_state:
    st.session_state.db_requests = pd.DataFrame(columns=[
        "Mã Đơn", "Họ Tên", "Lớp", "Loại Ra Ngoài", "Lý Do/Người Đón", "CCCD Người Đón", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái"
    ])

st.set_page_config(page_title="Hệ thống Quản lý Nội trú", layout="wide")
st.title("🏫 Quản lý Học sinh Ra ngoài & Về quê")

st.sidebar.header("DANH MỤC")
menu = st.sidebar.selectbox("Vai trò:", ["Học sinh đăng ký", "Giáo viên chủ nhiệm", "Quản lý HS/ Ban Giám Hiệu"])

# 1. GIAO DIỆN HỌC SINH
if menu == "Học sinh đăng ký":
    st.header("📝 Đăng ký Ra ngoài / Về quê")
    with st.form("form_dang_ky"):
        col1, col2 = st.columns(2)
        with col1:
            ten = st.text_input("Họ và Tên học sinh:")
            lop = st.selectbox("Chọn Lớp:", ["10A1", "10A2", "10A3","10A4","10A5","10A6","11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        with col2:
            loai_hinh = st.selectbox("Loại hình ra ngoài:", 
                                    ["Ra ngoài trong ngày", "Đi khám / Ốm nằm viện", "Về nhà cuối tuần"])
        
        # Logic hiển thị thông tin người đón
        chi_tiet = ""
        cccd = ""
        if loai_hinh == "Về nhà cuối tuần":
            nguoi_don = st.radio("Phương thức về nhà:", 
                                 ["Bố đón", "Mẹ đón", "Ông đón", "Bà đón", "Người thân khác đón", "Tự đi xe khách về"], 
                                 horizontal=True)
            
            if nguoi_don != "Tự đi xe khách về":
                col_a, col_b = st.columns(2)
                with col_a:
                    ten_nguoi_don = st.text_input("Họ tên người đón (Không bắt buộc):")
                with col_b:
                    cccd = st.text_input("Số CCCD người đón (Không bắt buộc):")
                chi_tiet = f"{nguoi_don}: {ten_nguoi_don}"
            else:
                chi_tiet = "Tự đi xe khách"
        else:
            chi_tiet = st.text_area("Lý do cụ thể:")

        submit = st.form_submit_button("Gửi đơn đăng ký")
        
        if submit and ten:
            new_id = len(st.session_state.db_requests) + 1
            new_row = pd.DataFrame([[new_id, ten, lop, loai_hinh, chi_tiet, cccd, "Chờ duyệt", "Chờ duyệt", "Đang xử lý"]], 
                                   columns=st.session_state.db_requests.columns)
            st.session_state.db_requests = pd.concat([st.session_state.db_requests, new_row], ignore_index=True)
            st.success(f"✅ Đã gửi đơn thành công! Mã đơn của bạn là: {new_id}")
# 2. PHẦN GIÁO VIÊN
elif menu == "Giáo viên chủ nhiệm":
    st.header("👨‍🏫 Xác nhận của GVCN")
    pw = st.text_input("Mật khẩu Giáo viên:", type="password")
    if pw == PASS_GVCN:
        lop_chon = st.selectbox("Lớp quản lý:", ["10A1", "10A2", "10A3","10A4","10A5","10A6","11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        df = st.session_state.db_requests
        df_filter = df[(df["Lớp"] == lop_chon) & (df["GVCN Duyệt"] == "Chờ duyệt")]
        st.dataframe(df_filter, use_container_width=True)
        
        id_duyet = st.number_input("Mã đơn xác nhận:", step=1, min_value=0)
        if st.button("Xác nhận Đơn"):
            if id_duyet in df_filter["Mã Đơn"].values:
                st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_duyet, "GVCN Duyệt"] = "Đã xác nhận"
                st.success("Đã xác nhận thành công!")
                st.rerun()

# 3. PHẦN QUẢN LÝ / BGH
elif menu == "Quản lý HS/ Ban Giám Hiệu":
    st.header("🛡️ Phê duyệt của Ban Giám Hiệu")
    pw_ad = st.text_input("Mật khẩu Quản lý:", type="password")
    if pw_ad == PASS_QUANLY:
        df_all = st.session_state.db_requests
        # Hiển thị đơn đã qua bước GVCN
        df_admin = df_all[(df_all["GVCN Duyệt"] == "Đã xác nhận") & (df_all["Quản lý Duyệt"] == "Chờ duyệt")]
        st.dataframe(df_admin, use_container_width=True)
        
        id_ql = st.number_input("Mã đơn phê duyệt:", step=1, min_value=0)
        if st.button("🚀 CẤP PHÉP CHÍNH THỨC"):
            if id_ql in df_admin["Mã Đơn"].values:
                st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_ql, "Quản lý Duyệt"] = "ĐÃ DUYỆT"
                st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_ql, "Trạng Thái"] = "Hợp lệ"
                st.success(f"Đã phê duyệt đơn {id_ql}")
                st.rerun()
    elif pw_ad != "":
        st.error("Mật khẩu không đúng!")