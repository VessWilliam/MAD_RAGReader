import requests
from config import API_URL


def upload_pdf_api(file):
    if file is None:
        return {"success": False, "message": "No file provided."}
    try:
        files = {"file": (file.name, file.getbuffer(), "application/pdf")}
        response = requests.post(f"{API_URL}/upload", files=files)
        return {"success": response.status_code == 200, "message": response.json()}
    except Exception as e:
        return {"success": False, "message": str(e)}


def stream_answer(prompt, session_id):
    try:
        with requests.post(
            f"{API_URL}/ask",
            json={"query": prompt},
            headers={"session-id": session_id},
            stream=True,
            timeout=60,
        ) as response:
            if response.status_code != 200:
                yield f"[ERROR] Server returned: {response.status_code}"
                return
            for line in response.iter_lines():
                if line and line.startswith(b"data: "):
                    yield line[len(b"data: ") :].decode("utf-8")
    except requests.exceptions.RequestException as e:
        yield f"[ERROR] {e}"


def clear_history(session_id):
    try:
        response = requests.post(f"{API_URL}/clear", headers={"session-id": session_id})
        return {"success": response.status_code == 200}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": str(e)}
