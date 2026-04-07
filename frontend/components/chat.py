import streamlit as st
from core.streaming import get_stream


def render_chat():
    if "message" not in st.session_state:
        st.session_state.message = []

    chat_container = st.container()

    # Scrollable chat wrapper
    with chat_container:
        for msg in st.session_state.message:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])


def handle_input(prompt):
    # Save user message
    st.session_state.message.append({"role": "user", "content": prompt})

    # Render user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response (streaming)
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

    # Save assistant response
    st.session_state.message.append({"role": "assistant", "content": response})
