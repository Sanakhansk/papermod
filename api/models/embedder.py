# models/embedder.py

from sentence_transformers import SentenceTransformer

# Load MiniLM once and reuse
model = SentenceTransformer("all-MiniLM-L6-v2")
