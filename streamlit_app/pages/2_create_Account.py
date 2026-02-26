import streamlit as st
from ..UI import init_state
from ..api import create_account

st.set_page_config(page_title="Create Account", layout="wide")
init_state()

st.title("Create Account")

email = st.text_input("Email")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
confirm = st.text_input("Confirm Password", type="password")

if st.button("Create Account"):
    if not email or not username or not password:
        st.error("All fields are required.")
        st.stop()

    if password != confirm:
        st.error("Passwords do not match.")
        st.stop()

    if len(password) < 6:
        st.error("Password must be at least 6 characters.")
        st.stop()

    code, data, text = create_account(
        st.session_state.api_base,
        email,
        username,
        password,
    )

    if code in (200, 201):
        st.success("Account created successfully. You can login now.")
    else:
        st.error(text)