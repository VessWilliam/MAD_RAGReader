from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "pdf"


class PDFService:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def upload_pdf(self, file_bytes: bytes, filename: str) -> str:

        file_path = DATA_DIR / filename

        if file_path.exists():
            raise FileExistsError(f"File {filename} already exists.")

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return str(file_path)
