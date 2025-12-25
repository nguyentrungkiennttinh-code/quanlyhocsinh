import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Kiểm tra kết nối")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="trangtính1", ttl=0)
    st.success("Chúc mừng! Kết nối thành công.")
    st.dataframe(df)
except Exception as e:
    st.error(f"Vẫn lỗi Secrets: {e}")
    st.info("Hãy chắc chắn bạn đã dán tiêu đề [connections.gsheets] vào mục Secrets.")
