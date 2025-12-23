# extractor/summarizer.py

from utils.subsection_analyzer import analyze_subsections

def refine_subsections(ranked_sections, persona=None, job=None, top_k=3):
    refined = []
    for sec in ranked_sections:
        subchunks = analyze_subsections(
            sec.text,
            persona_text=persona,
            job_text=job,
            top_k=top_k
        )
        for sub in subchunks:
            refined.append({
                "document": sec.document,
                "page_number": sec.page_number,
                "refined_text": sub["refined_text"],
                "score": round(sub["score"], 4)
            })
    return refined
