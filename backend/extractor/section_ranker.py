# section_ranker.py
import fitz  # PyMuPDF
import os
import re
from sentence_transformers import SentenceTransformer, util
from typing import List
from dataclasses import dataclass
import numpy as np

@dataclass
class Chunk:
    document: str
    page_number: int
    text: str
    heading: str = None
    score: float = 0.0


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def embed_texts(texts: List[str]):
    return model.encode(texts, convert_to_tensor=True, normalize_embeddings=True)


def extract_chunks_from_pdf(pdf_path: str) -> List[Chunk]:
    chunks = []
    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("blocks")  # returns list of tuples
        blocks_sorted = sorted(blocks, key=lambda x: (x[1], x[0]))  # Sort by y, then x

        current_heading = None
        current_text = []

        for b in blocks_sorted:
            text = b[4].strip()
            font_size = b[6] if len(b) > 6 else 10  # Approx font size
            if not text or len(text) < 20:
                continue

            # Heuristic: Heading if font size large or all caps or < 8 words
            if font_size > 13 or (text.isupper() and len(text.split()) < 8):
                if current_text:  # Save previous section
                    chunks.append(Chunk(
                        document=os.path.basename(pdf_path),
                        page_number=page_num,
                        text="\n".join(current_text),
                        heading=current_heading
                    ))
                current_heading = text
                current_text = []
            else:
                current_text.append(text)

        # Save last section on page
        if current_text:
            chunks.append(Chunk(
                document=os.path.basename(pdf_path),
                page_number=page_num,
                text="\n".join(current_text),
                heading=current_heading
            ))

    return chunks


def apply_mmr(query_embedding, doc_embeddings, lambda_param=0.7, top_k=10):
    doc_embeddings = doc_embeddings.cpu().numpy()
    query_embedding = query_embedding.cpu().numpy()

    selected_indices = []
    remaining = list(range(len(doc_embeddings)))

    similarity_to_query = np.dot(doc_embeddings, query_embedding.T)

    while len(selected_indices) < top_k and remaining:
        if not selected_indices:
            idx = int(np.argmax(similarity_to_query[remaining]))
            selected_indices.append(remaining[idx])
            remaining.pop(idx)
        else:
            max_score = -float("inf")
            chosen_idx = None
            for i in remaining:
                relevance = similarity_to_query[i]
                diversity = max(np.dot(doc_embeddings[i], doc_embeddings[j]) for j in selected_indices)
                score = lambda_param * relevance - (1 - lambda_param) * diversity
                if score > max_score:
                    max_score = score
                    chosen_idx = i
            selected_indices.append(chosen_idx)
            remaining.remove(chosen_idx)
    return selected_indices


def rank_sections(input_dir: str, persona: str, job: str, top_k=10) -> List[Chunk]:
    query = f"{persona}. Task: {job}"

    all_chunks = []
    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            path = os.path.join(input_dir, file)
            chunks = extract_chunks_from_pdf(path)
            all_chunks.extend(chunks)

    query_embedding = embed_texts([query])
    chunk_texts = [c.text for c in all_chunks]
    chunk_embeddings = embed_texts(chunk_texts)

    # Initial scores (cosine similarity)
    scores = util.cos_sim(query_embedding, chunk_embeddings)[0].cpu().numpy()
    for i, chunk in enumerate(all_chunks):
        chunk.score = float(scores[i])
        # Boost heading relevance
        if chunk.heading:
            if any(word.lower() in chunk.heading.lower() for word in ["travel", "plan", "adventure", "tips", "guide"]):
                chunk.score += 0.05

    # Apply MMR for diversity
    mmr_indices = apply_mmr(query_embedding, chunk_embeddings, lambda_param=0.6, top_k=top_k)
    ranked_sections = [all_chunks[i] for i in mmr_indices]

    return ranked_sections
