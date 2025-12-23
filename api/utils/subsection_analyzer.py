# utils/subsection_analyzer.py

from typing import List, Dict, Any
from sentence_transformers import util
from models.embedder import model
import numpy as np
import re

def split_text_into_chunks(text: str, max_length: int = 300) -> List[str]:
    """
    Split text into semi-coherent chunks (roughly paragraph/sentence level).
    Merges smaller chunks to fit under max_length.
    """
    chunks = re.split(r'(?<=[.?!])\s+', text)

    merged = []
    buffer = ""
    for chunk in chunks:
        if len(buffer) + len(chunk) < max_length:
            buffer += " " + chunk
        else:
            if buffer:
                merged.append(buffer.strip())
            buffer = chunk
    if buffer:
        merged.append(buffer.strip())

    return merged

def analyze_subsections(
    section_text: str,
    persona_text: str,
    job_text: str,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Break section into smaller chunks and rank by relevance to persona + job.
    """
    chunks = split_text_into_chunks(section_text)

    if not chunks:
        return []

    combined_query = f"{persona_text.strip()} {job_text.strip()}"
    query_embedding = model.encode(combined_query, convert_to_tensor=True)
    chunk_embeddings = model.encode(chunks, convert_to_tensor=True)

    scores = util.cos_sim(query_embedding, chunk_embeddings)[0].cpu().numpy()

    ranked = sorted(zip(chunks, scores), key=lambda x: -x[1])

    return [
        {
            "refined_text": chunk,
            "score": float(score)
        }
        for chunk, score in ranked[:top_k]
    ]
