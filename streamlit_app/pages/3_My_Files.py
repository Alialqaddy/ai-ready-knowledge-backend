import streamlit as st
from ..UI import init_state, require_login, auth_headers
from ..api import list_files, upload_file, download_file, delete_file

st.set_page_config(page_title="My Files", layout="wide")
init_state()
require_login()

st.title("My Files")

# Upload
st.subheader("Upload File")
uploaded = st.file_uploader("Choose a file")

if uploaded and st.button("Upload"):
    code, data, text = upload_file(
        st.session_state.api_base,
        auth_headers(),
        uploaded,
    )
    if code in (200, 201):
        st.success("File uploaded.")
        st.json(data)
        st.rerun()
    else:
        st.error(text)

# List
st.subheader("Your Files")

code, data, text = list_files(
    st.session_state.api_base,
    auth_headers(),
)

if code != 200:
    st.error(text)
    st.stop()

if not data:
    st.info("No files uploaded yet.")
    st.stop()

for f in data:
    with st.container():
        c1, c2, c3 = st.columns([5, 2, 2])

        with c1:
            st.write(f"**#{f['id']}** – {f['original_name']} ({f['size_bytes']} bytes)")

        with c2:
            if st.button(f"Download #{f['id']}"):
                d_code, content, d_text = download_file(
                    st.session_state.api_base,
                    auth_headers(),
                    f["id"],
                )
                if d_code == 200:
                    st.download_button(
                        label="Save file",
                        data=content,
                        file_name=f["original_name"],
                    )
                else:
                    st.error(d_text)

        with c3:
            if st.button(f"Delete #{f['id']}"):
                d_code, d_text = delete_file(
                    st.session_state.api_base,
                    auth_headers(),
                    f["id"],
                )
                if d_code == 204:
                    st.success("File deleted.")
                    st.rerun()
                else:
                    st.error(d_text)