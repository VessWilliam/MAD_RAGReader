import requests
from config import API_URL


def stream_answer(prompt, session_id):
    with requests.post(
        f"{API_URL}/ask",
        json={"query": prompt},
        headers={"session-id": session_id},
        stream=True,
        timeout=60,
    ) as response:

        for line in response.iter_lines():
            if not line:
                continue

            if line.startswith(b"data: "):
                yield line[len(b"data: ") :].decode("utf-8")


def clear_history(session_id):
    response = requests.post(
        f"{API_URL}/clear",
        headers={"session-id": session_id},
    )
    return response.status_code == 200
