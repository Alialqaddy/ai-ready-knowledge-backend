import streamlit as st
from UI import init_state, logout

st.set_page_config(page_title="AI Ready KB", layout="wide")
init_state()

st.title("AI Ready Knowledge Base – Phase 1")

col1, col2 = st.columns([4, 1])
with col2:
    if st.session_state.token:
        if st.button("Logout"):
            logout()
            st.success("Logged out.")
            st.rerun()

st.markdown("""
### Available Pages:
- **Login**
- **Create Account**
- **My Files**

Use the sidebar to navigate.
""")

if not st.session_state.token:
    st.info("You are not logged in.")
else:
    st.success("You are logged in.")