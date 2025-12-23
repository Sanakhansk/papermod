# **Approach Explanation – Adobe Hackathon Round 1B**

**Theme:** Persona-Driven Document Intelligence

---

## **Problem Statement**

Given:

* **3 collections of related PDFs** (e.g., Travel Planning, Adobe Acrobat Learning, Recipe Collection).
* **An input JSON** specifying:

  * `persona` (e.g., Travel Planner)
  * `job_to_be_done` (e.g., Plan a 4-day trip for 10 college friends).

The goal is to:

1. Identify **top relevant sections** across multiple PDFs.
2. Extract **fine-grained subsections** for detailed insights.
3. Output a **structured JSON** with:

   * Metadata (persona, job, input files)
   * Ranked sections (title, page number, importance)
   * Subsection-level analysis (highly relevant snippets).

---

## **Design Principles**

✔ **Lightweight:** CPU-only, model size ≤ 200MB, runtime < 60s per collection.
✔ **Accurate:** Semantic similarity-based, not keyword-driven.
✔ **Structured:** Output conforms to Adobe’s expected JSON schema.

---

## **Pipeline Overview**

### **Step 1: Input Parsing & Loading**

* Read `challenge1b_input.json` for persona and job-to-be-done.
* Load PDFs from `Collection/PDFs/` using **PyMuPDF** (`page.get_text("blocks")`).

---

### **Step 2: Chunk Extraction & Cleaning**

* Extract **block-level text chunks**.
* Filter noise: remove empty strings and fragments shorter than 50 characters.
* Represent as:

```python
Chunk(document="file.pdf", page_number=2, text="Actual content")
```

---

### **Step 3: Semantic Relevance Scoring**

* **Model:** `sentence-transformers/all-MiniLM-L6-v2` (\~90MB, CPU-friendly).
* Create a **query**:

```
"{persona}. Task: {job_to_be_done}"
```

* Compute **embeddings** for query and all chunks.
* Rank chunks by **cosine similarity**.

---

### **Step 4: Diversity Control**

* Select top 20 ranked chunks.
* Apply **max-2-per-document** rule to avoid single-document dominance.
* Keep **top 10 sections** for final output.
  *(Future: Implement **MMR** for improved diversity.)*

---

### **Step 5: Subsection Refinement**

* For each top section:

  * Split text into smaller subsections (\~300 chars).
  * Rank by semantic similarity.
  * Keep **top 3 refined chunks** per section.

---

### **Step 6: JSON Output Formatting**

* **Metadata:** input documents, persona, job, timestamp.
* **Extracted Sections:**

  * Title = first meaningful line (non-bullet).
  * Page number + importance rank.
* **Subsection Analysis:**

  * Group refined chunks with relevance scores.

---

## **Strengths**

✅ Fully **offline**, CPU-optimized pipeline.
✅ **Persona-aware semantic ranking** ensures contextually relevant output.
✅ Matches Adobe’s **structured JSON format**.

---

## **Future Enhancements**

✔ **MMR-based diversity** for more balanced selection.
✔ **LLM-driven summarization** for human-like summaries.
✔ **Interactive dashboard** for visualization and review.

---

### **Author:** Riddhi Sharma

**Hackathon:** Adobe India – Understand Your Document (Round 1B)

