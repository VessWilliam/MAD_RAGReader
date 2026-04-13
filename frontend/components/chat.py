import streamlit as st
from core.streaming import get_stream


def render_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def handle_input(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        box = st.empty()
        response = ""

        try:
            for partial in get_stream(prompt, st.session_state.session_id):
                response = partial
                box.markdown(response + "▌")
        except Exception as e:
            st.error(str(e))

        box.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})