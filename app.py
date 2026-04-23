import streamlit as st

# Phải có set_page_config trước khi switch_page
st.set_page_config(layout="wide")

# Tự động chuyển hướng sang trang chủ trong thư mục pages/
st.switch_page("pages/1_Trang_Chu.py")