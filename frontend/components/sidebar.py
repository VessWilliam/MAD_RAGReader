import streamlit as st
from api.api_client import clear_history


def render_sidebar():
    if st.button("Clear History"):
        clear_history(st.session_state.session_id)
        st.session_state.message = []
        st.rerun()
