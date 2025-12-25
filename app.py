import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CẤU HÌNH HỆ THỐNG ---
PASS_GVCN = "gv123"
PASS_QUANLY = "admin123"
SHEET_NAME = "trangtính1"  # Đã sửa theo tên bạn yêu cầu

# Kết nối Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Đọc dữ liệu, ttl=0 để luôn lấy dữ liệu mới nhất
        df = conn.read(worksheet=SHEET_NAME, ttl=0)
        return df.dropna(how="all")
    except Exception:
        # Nếu Sheets trống hoặc lỗi, tạo khung dữ liệu chuẩn
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
    with st.form("form_dang_ky", clear_on_submit=True):
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

        if st.form_submit_button("Gửi đơn đăng ký"):
            if not ten:
                st.error("Vui lòng nhập họ tên!")
            else:
                try:
                    df_existing = load_data()
                    # Tự động tính Mã Đơn dựa trên giá trị lớn nhất hiện có
                    if not df_existing.empty:
                        new_id = int(pd.to_numeric(df_existing["Mã Đơn"], errors='coerce').max() + 1)
                    else:
                        new_id = 1
                    
                    new_row = pd.DataFrame([{
                        "Mã Đơn": new_id, 
                        "Họ Tên": ten, 
                        "Lớp": lop, 
                        "Loại Hình": loai_hinh, 
                        "Chi Tiết Người Đón": chi_tiet, 
                        "CCCD Người Đón": cccd, 
                        "GVCN Duyệt": "Chờ duyệt", 
                        "Quản lý Duyệt": "Chờ duyệt", 
                        "Trạng Thái": "Đang xử lý"
                    }])
                    
                    updated_df = pd.concat([df_existing, new_row], ignore_index=True)
                    conn.update(worksheet=SHEET_NAME, data=updated_df)
                    st.cache_data.clear() # Xóa cache để cập nhật dữ liệu mới
                    st.success(f"✅ Gửi đơn thành công! Mã đơn: {new_id}")
                except Exception as e:
                    st.error(f"Lỗi khi gửi đơn: {e}")

# 2. GIAO DIỆN GIÁO VIÊN
elif menu == "Giáo viên chủ nhiệm":
    st.header("👨‍🏫 Xác nhận của GVCN")
    pw = st.text_input("Mật khẩu Giáo viên:", type="password")
    if pw == PASS_GVCN:
        lop_ql = st.selectbox("Lớp quản lý:", ["10A1", "10A2", "10A3", "10A4", "10A5", "10A6", "11A1", "11A2", "11A3","11A4","11A5","11A6","12A1", "12A2","12A3","12A4","12A5"])
        df = load_data()
        df_show = df[(df["Lớp"] == lop_ql) & (df["GVCN Duyệt"] == "Chờ duyệt")]
        
        st.dataframe(df_show, use_container_width=True)
        id_gv = st.number_input("Mã đơn xác nhận:", step=1, min_value=0)
        
        if st.button("Xác nhận Đơn"):
            if not df_show.empty and id_gv in df_show["Mã Đơn"].values:
                df.loc[df["Mã Đơn"] == id_gv, "GVCN Duyệt"] = "Đã xác nhận"
                conn.update(worksheet=SHEET_NAME, data=df)
                st.success(f"Đã xác nhận thành công đơn số {id_gv}!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning("Mã đơn không đúng hoặc đơn này không thuộc lớp bạn.")

# 3. GIAO DIỆN QUẢN LÝ / BGH
elif menu == "Quản lý HS/ Ban Giám Hiệu":
    st.header("🛡️ Phê duyệt của Ban Giám Hiệu")
    pw_ad = st.text_input("Mật khẩu Quản lý:", type="password")
    if pw_ad == PASS_QUANLY:
        df_all = load_data()
        st.subheader("📋 Đơn đang chờ phê duyệt (Đã có xác nhận GVCN)")
        df_admin = df_all[(df_all["GVCN Duyệt"] == "Đã xác nhận") & (df_all["Quản lý Duyệt"] == "Chờ duyệt")]
        st.dataframe(df_admin, use_container_width=True)
        
        id_ql = st.number_input("Mã đơn phê duyệt:", step=1, min_value=0)
        if st.button("🚀 CẤP PHÉP CHÍNH THỨC"):
            if not df_admin.empty and id_ql in df_admin["Mã Đơn"].values:
                df_all.loc[df_all["Mã Đơn"] == id_ql, "Quản lý Duyệt"] = "ĐÃ DUYỆT"
                df_all.loc[df_all["Mã Đơn"] == id_ql, "Trạng Thái"] = "Hợp lệ"
                conn.update(worksheet=SHEET_NAME, data=df_all)
                st.success(f"Đã duyệt đơn số {id_ql}")
                st.cache_data.clear()
                st.rerun()
        
        st.markdown("---")
        st.subheader("📥 Xuất báo cáo")
        if not df_all.empty:
            csv = df_all.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📩 Tải danh sách CSV", data=csv, file_name="bao_cao.csv", mime="text/csv")
