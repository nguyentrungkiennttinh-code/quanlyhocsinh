import streamlit as st
import pandas as pd
import os

# --- CẤU HÌNH ---
FILE_LUU_TRU = "du_lieu_ra_ngoai.xlsx"
PASS_GVCN = "gv123"
PASS_QUANLY = "admin123"

# Khởi tạo dữ liệu mẫu nếu chưa có
if 'db_requests' not in st.session_state:
    st.session_state.db_requests = pd.DataFrame(columns=["Mã Đơn", "Họ Tên", "Lớp", "Lý Do", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái Tổng"])

# Giao diện chính
st.set_page_config(page_title="Quản lý Học sinh", layout="centered")
st.title("🏫 Quản lý Học sinh Ra ngoài")

# Thanh Menu bên trái
st.sidebar.header("DANH MỤC")
menu = st.sidebar.selectbox("Chọn vai trò:", ["Học sinh đăng ký", "Giáo viên chủ nhiệm", "Quản lý HS/ Ban Giám Hiệu"])

# 1. PHẦN DÀNH CHO HỌC SINH
if menu == "Học sinh đăng ký":
    st.header("📝 Đăng ký xin ra ngoài")
    with st.form("form_hoc_sinh"):
        ten = st.text_input("Họ và Tên học sinh:")
        # Thêm danh sách lớp để học sinh chọn
        lop = st.selectbox("Chọn Lớp:", ["10A1", "10A2", "10A3","10A4","10A5","10A6","11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        lydo = st.text_area("Lý do cụ thể:")
        btn_gui = st.form_submit_button("Gửi đơn đăng ký")
        
        if btn_gui and ten:
            new_id = len(st.session_state.db_requests) + 1
            new_row = pd.DataFrame([[new_id, ten, lop, lydo, "Chờ duyệt", "Chờ duyệt", "Đang xử lý"]], 
                                   columns=st.session_state.db_requests.columns)
            st.session_state.db_requests = pd.concat([st.session_state.db_requests, new_row], ignore_index=True)
            st.success(f"✅ Đã gửi đơn thành công! Mã đơn của bạn là: {new_id}")

# 2. GIÁO VIÊN CHỦ NHIỆM
elif menu == "Giáo viên chủ nhiệm":
    st.header("👨‍🏫 Khu vực Giáo viên")
    pw = st.text_input("Mật khẩu Giáo viên:", type="password")
    if pw == PASS_GVCN:
        st.write("Danh sách đơn cần xác nhận:")
        st.dataframe(st.session_state.db_requests[st.session_state.db_requests["GVCN Duyệt"] == "Chờ duyệt"])
        id_gv = st.number_input("Nhập Mã Đơn để xác nhận:", step=1, min_value=0)
        if st.button("Xác nhận đơn"):
            st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_gv, "GVCN Duyệt"] = "Đã xác nhận"
            st.success("Đã xác nhận thành công!")
            st.rerun()

# 3. QUẢN LÝ / BAN GIÁM HIỆU
elif menu == "Quản lý HS/ Ban Giám Hiệu":
    st.header("🛡️ Khu vực Quản lý / BGH")
    pw_a = st.text_input("Mật khẩu Quản lý:", type="password")
    if pw_a == PASS_QUANLY:
        st.success("Chào sếp! Dưới đây là các đơn đã có xác nhận của GVCN:")
        df = st.session_state.db_requests
        df_show = df[df["GVCN Duyệt"] == "Đã xác nhận"]
        st.dataframe(df_show)
        
        id_ql = st.number_input("Nhập Mã Đơn để cấp phép chính thức:", step=1, min_value=0)
        if st.button("🚀 CẤP PHÉP"):
            st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_ql, "Quản lý Duyệt"] = "ĐÃ DUYỆT"
            st.session_state.db_requests.loc[st.session_state.db_requests["Mã Đơn"] == id_ql, "Trạng Thái Tổng"] = "Hợp lệ"
            st.success(f"Đã duyệt đơn số {id_ql}!")
            st.rerun()
    elif pw_a != "":
        st.error("Sai mật khẩu rồi bạn ơi!")