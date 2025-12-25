import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Cấu hình tiêu đề
st.set_page_config(page_title="Kiểm tra kết nối")
st.title("🔍 Kiểm tra kết nối Google Sheets")

# Tên trang tính đã sửa theo yêu cầu của bạn
SHEET_NAME = "trangtính1"

try:
    # Khởi tạo kết nối
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Thử đọc dữ liệu
    df = conn.read(worksheet=SHEET_NAME, ttl=0)
    
    st.success("✅ Tuyệt vời! Bạn đã kết nối thành công.")
    st.write("Dưới đây là dữ liệu từ trang tính của bạn:")
    st.dataframe(df)
    
except Exception as e:
    st.error(f"❌ Vẫn còn lỗi kết nối: {e}")
    st.info("Hãy kiểm tra lại mục Secrets: Đảm bảo có dòng [connections.gsheets] và khóa private_key nằm trên một dòng duy nhất.")
