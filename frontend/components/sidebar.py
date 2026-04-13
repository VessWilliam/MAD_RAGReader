import streamlit as st
from api.api_client import clear_history, upload_pdf_api


def render_sidebar():
    with st.sidebar:
        st.header("Clear Chat History")
        if st.button("Clear History"):
            clear_history(st.session_state.session_id)
            st.session_state.messages = []
            st.rerun()

        st.header("Upload PDF")
        if st.session_state.get("uploaded_file_done"):
            return

        upload_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if upload_pdf is None:
            return

        result = upload_pdf_api(upload_pdf)
        if result.get("success"):
            st.success("PDF uploaded successfully!")
            st.session_state.uploaded_file_done = True
        else:
            st.error("Failed to upload PDF.")
