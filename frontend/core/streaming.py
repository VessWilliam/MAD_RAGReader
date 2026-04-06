from api.api_client import stream_answer

def get_stream(prompt, session_id):
    full_response = ""

    for token in stream_answer(prompt, session_id):

        if token == "[DONE]":
            break

        if token.startswith("[ERROR]"):
            yield token
            return

        full_response += token
        yield full_response
