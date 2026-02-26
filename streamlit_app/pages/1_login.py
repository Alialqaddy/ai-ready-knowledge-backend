import streamlit as st
from ..UI import init_state, logout
from ..api import login

st.set_page_config(page_title="Login", layout="wide")
init_state()

st.title("Login")

if st.session_state.token:
    st.success("Already logged in.")
    if st.button("Logout"):
        logout()
        st.rerun()
    st.stop()

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    if not username or not password:
        st.error("Username and password are required.")
        st.stop()

    code, data, text = login(st.session_state.api_base, username, password)

    if code == 200 and data and "access_token" in data:
        st.session_state.token = data["access_token"]
        st.success("Login successful.")
        st.rerun()
    else:
        st.error(text)