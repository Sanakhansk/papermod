import os
import fitz  # PyMuPDF

def load_pdfs(folder):
    documents = []
    for filename in os.listdir(folder):
        if filename.endswith(".pdf"):
            path = os.path.join(folder, filename)
            doc = fitz.open(path)
            pages = [page.get_text("blocks") for page in doc]
            documents.append({
                "name": filename,
                "path": path,
                "doc": doc,
                "pages": pages
            })
    return documents
