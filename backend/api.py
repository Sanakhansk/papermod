from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import shutil

from .main import run_pipeline, run_pipeline_single_pdf


app = FastAPI(title="PaperMind API")

# ----------------------------------
# CORS (important for HTML frontend)
# ----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------
# Request Schema (OLD MODE)
# ----------------------------------
class AnalyzeRequest(BaseModel):
    collection: str


# ----------------------------------
# Health Check
# ----------------------------------
@app.get("/")
def health():
    return {"status": "PaperMind API running"}


# ----------------------------------
# OLD: Batch / Challenge Mode
# ----------------------------------
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    """
    Existing batch pipeline.
    Reads PDFs from disk (Challenge_1b).
    """
    base_dir = "Challenge_1b"

    if not os.path.exists(os.path.join(base_dir, req.collection)):
        return {"error": "Collection not found"}

    result = run_pipeline(base_dir, req.collection)
    return result


# ----------------------------------
# NEW: Frontend PDF Upload Mode
# ----------------------------------
@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    """
    Frontend integration endpoint.
    - Receives single PDF from browser
    - Calls API-friendly pipeline
    - Returns JSON response
    """

    temp_dir = tempfile.mkdtemp()
    pdf_path = os.path.join(temp_dir, file.filename)

    try:
        # Save uploaded PDF temporarily
        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        # Call new API-friendly pipeline
        result = run_pipeline_single_pdf(pdf_path)
        return result

    finally:
        # Clean temp files
        shutil.rmtree(temp_dir)
