import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Quản lý Nội trú", layout="wide")
st.title("🏫 Quản lý Học sinh")

# Dòng số 10 gây lỗi binascii nếu Secrets sai
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="trangtính1", ttl=0)
    st.success("✅ Kết nối thành công!")
    st.dataframe(df)
except Exception as e:
    st.error(f"Vẫn lỗi kết nối: {e}")
    st.info("Hãy kiểm tra lại mục Secrets và Reboot app.")
