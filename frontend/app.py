import streamlit as st
from core.state import init_state
from components.chat import render_chat, handle_input
from components.sidebar import render_sidebar

st.set_page_config(page_title="MAD RAG Reader", page_icon="🤖")
init_state()

st.title("MAD RAG Reader")
st.caption("Ask questions based on your documents")

render_sidebar()
render_chat()

if prompt := st.chat_input("Ask a question..."):
    handle_input(prompt)
