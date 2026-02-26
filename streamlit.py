import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Ready KB", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None


def auth_headers():
    if not st.session_state.token:
        return {}
    return {"Authorization": f"Bearer {st.session_state.token}"}


st.title("AI Ready Knowledge - Phase 1")

with st.sidebar:
    st.header("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        r = requests.post(f"{API_BASE}/auth/login", data={"username": username, "password": password})
        if r.status_code == 200:
            st.session_state.token = r.json()["access_token"]
            st.success("Logged in")
        else:
            st.error(r.text)

    if st.button("Logout"):
        st.session_state.token = None
        st.info("Logged out")

if not st.session_state.token:
    st.warning("Please login first.")
    st.stop()

st.subheader("Upload File")
uploaded = st.file_uploader("Choose a file")

if uploaded and st.button("Upload"):
    files = {"uploaded": (uploaded.name, uploaded.getvalue(), uploaded.type)}
    r = requests.post(f"{API_BASE}/files/upload", headers=auth_headers(), files=files)
    if r.status_code in (200, 201):
        st.success("Uploaded")
        st.json(r.json())
    else:
        st.error(r.text)

st.subheader("My Files")
r = requests.get(f"{API_BASE}/files", headers=auth_headers())
if r.status_code == 200:
    data = r.json()
    st.write(f"Count: {len(data)}")
    for f in data:
        col1, col2, col3 = st.columns([5, 2, 2])
        with col1:
            st.write(f"#{f['id']} - {f['original_name']} ({f['size_bytes']} bytes)")
        with col2:
            if st.button(f"Download #{f['id']}"):
                dl = requests.get(f"{API_BASE}/files/{f['id']}/download", headers=auth_headers())
                if dl.status_code == 200:
                    st.download_button(
                        label=f"Save {f['original_name']}",
                        data=dl.content,
                        file_name=f["original_name"],
                    )
                else:
                    st.error(dl.text)
        with col3:
            if st.button(f"Delete #{f['id']}"):
                d = requests.delete(f"{API_BASE}/files/{f['id']}", headers=auth_headers())
                if d.status_code == 204:
                    st.success("Deleted. Refresh page.")
                else:
                    st.error(d.text)
else:
    st.error(r.text)