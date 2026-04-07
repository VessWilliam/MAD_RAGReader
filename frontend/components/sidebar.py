import streamlit as st
from api.api_client import clear_history


def render_sidebar():
    if st.button("Clear History"):
        clear_history(st.session_state.session_id)
        st.session_state.message = []
        st.rerun()

    with st.sidebar:
        st.header("Upload PDF")
        
        upload_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        
        if upload_pdf is not None:
            st.session_state.pdf = upload_pdf

  