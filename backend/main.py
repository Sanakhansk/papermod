from extractor.loader import load_pdfs
from extractor.persona_parser import load_persona
from extractor.section_ranker import rank_sections
from extractor.summarizer import refine_subsections
from extractor.formatter import save_output

from datetime import datetime
from collections import defaultdict
import os


# =========================================================
# 1️⃣ ORIGINAL BATCH / CHALLENGE PIPELINE (UNCHANGED)
# =========================================================
def run_pipeline(base_dir, collection):
    collection_path = os.path.join(base_dir, collection)
    pdf_dir = os.path.join(collection_path, "PDFs")
    persona_path = os.path.join(collection_path, "challenge1b_input.json")
    output_path = os.path.join(collection_path, "challenge1b_output.json")

    documents = load_pdfs(pdf_dir)
    persona = load_persona(persona_path)

    persona_role = persona["persona"]
    persona_task = persona["job_to_be_done"]

    ranked_sections = rank_sections(pdf_dir, persona_role, persona_task, top_k=10)
    refined_sections = refine_subsections(
        ranked_sections, persona=persona_role, job=persona_task, top_k=3
    )

    metadata = {
        "input_documents": [doc["name"] for doc in documents],
        "persona": persona_role,
        "job_to_be_done": persona_task,
        "processing_timestamp": datetime.now().isoformat(),
    }

    extracted_sections = []
    for i, sec in enumerate(ranked_sections, 1):
        section_title = sec.heading if sec.heading else sec.text.split("\n")[0][:80]
        extracted_sections.append(
            {
                "document": sec.document,
                "section_title": section_title[:80],
                "importance_rank": i,
                "page_number": sec.page_number,
            }
        )

    grouped_subs = defaultdict(list)
    for r in refined_sections:
        grouped_subs[(r["document"], r["page_number"])].append(
            {"refined_text": r["refined_text"], "score": r["score"]}
        )

    subsection_analysis = []
    for (doc, page), subs in grouped_subs.items():
        subsection_analysis.append(
            {"document": doc, "page_number": page, "refined_chunks": subs}
        )

    output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis,
    }

    # 🔴 File output needed for challenge
    save_output(metadata, extracted_sections, subsection_analysis, output_path)

    return output


# =========================================================
# 2️⃣ NEW API-FRIENDLY PIPELINE (FOR FRONTEND)
# =========================================================
def run_pipeline_single_pdf(
    pdf_path, persona_role="general reader", persona_task="extract key sections"
):
    """
    Used by FastAPI.
    - Processes ONE PDF
    - Does NOT save any file
    - Returns JSON-compatible dict
    """

    pdf_dir = os.path.dirname(pdf_path)

    ranked_sections = rank_sections(pdf_dir, persona_role, persona_task, top_k=10)
    refined_sections = refine_subsections(
        ranked_sections, persona=persona_role, job=persona_task, top_k=3
    )

    metadata = {
        "input_document": os.path.basename(pdf_path),
        "persona": persona_role,
        "job_to_be_done": persona_task,
        "processing_timestamp": datetime.now().isoformat(),
        "mode": "api",
    }

    extracted_sections = []
    for i, sec in enumerate(ranked_sections, 1):
        section_title = sec.heading if sec.heading else sec.text.split("\n")[0][:80]
        extracted_sections.append(
            {
                "document": sec.document,
                "section_title": section_title[:80],
                "importance_rank": i,
                "page_number": sec.page_number,
            }
        )

    grouped_subs = defaultdict(list)
    for r in refined_sections:
        grouped_subs[(r["document"], r["page_number"])].append(
            {"refined_text": r["refined_text"], "score": r["score"]}
        )

    subsection_analysis = []
    for (doc, page), subs in grouped_subs.items():
        subsection_analysis.append(
            {"document": doc, "page_number": page, "refined_chunks": subs}
        )

    # 🔴 IMPORTANT: no save_output here
    return {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis,
    }
