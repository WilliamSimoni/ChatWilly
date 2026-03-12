import hashlib

from docx import Document
from pypdf import PdfReader


def get_file_hash(filepath):
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_text(filepath):
    ext = filepath.split(".")[-1].lower()
    text = ""
    try:
        if ext == "pdf":
            reader = PdfReader(filepath)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif ext == "docx":
            doc = Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif ext == "txt":
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
    except Exception as e:
        print(f"Errore lettura {filepath}: {e}")
    return text
