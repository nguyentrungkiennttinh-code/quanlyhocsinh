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

# 1. HỌC SINH ĐĂNG KÝ
if menu == "Học sinh đăng ký":
    st.header("📝 Đăng ký ra ngoài")
    with st.form("form_dk"):
        ten = st.text_input("Họ và Tên:")
        lop = st.text_input("Lớp:")
        lydo = st.text_area("Lý do ra ngoài:")
        submit = st.form_submit_button("Gửi đơn")
        
        if submit and ten and lop:
            new_id = len(st.session_state.db_requests) + 1
            new_data = pd.DataFrame([[new_id, ten, lop, lydo, "Chờ duyệt", "Chờ duyệt", "Đang xử lý"]], 
                                    columns=["Mã Đơn", "Họ Tên", "Lớp", "Lý Do", "GVCN Duyệt", "Quản lý Duyệt", "Trạng Thái Tổng"])
            st.session_state.db_requests = pd.concat([st.session_state.db_requests, new_data], ignore_index=True)
            st.success(f"Đã gửi đơn! Mã đơn của bạn là: {new_id}")

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