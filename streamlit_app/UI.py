import streamlit as st

def init_state():
    if "api_base" not in st.session_state:
        st.session_state.api_base = "http://127.0.0.1:8000"
    if "token" not in st.session_state:
        st.session_state.token = None

def auth_headers() -> dict:
    token = st.session_state.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def require_login():
    if not st.session_state.get("token"):
        st.warning("Please login first.")
        st.stop()

def logout():
    st.session_state.token = None