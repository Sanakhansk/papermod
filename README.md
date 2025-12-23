
# **Adobe Hackathon Round 1B – Persona-Driven Document Intelligence**

## **Overview**

This project acts as an **intelligent document analyst**, designed to process multiple related PDFs, extract **persona-driven relevant sections**, and produce a structured **JSON output** with:

 **Metadata** (persona, job-to-be-done, input docs)
**Extracted Top Sections** (with importance ranking)
**Refined Subsection Analysis** (smaller, highly relevant text chunks)

The solution is optimized for **offline, CPU-only execution**, making it suitable for real-world enterprise use cases.

---

## **Project Structure**

```
Challenge_1b/
├── Collection 1/                    # Travel Planning
│   ├── PDFs/                        # South of France guides
│   ├── challenge1b_input.json       # Input config (persona + job)
│   └── challenge1b_output.json      # Output with ranked sections
├── Collection 2/                    # Adobe Acrobat Learning
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
├── Collection 3/                    # Recipe Collection
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
└── README.md
```

---

## **Architecture Diagram**

```text
Persona + Job
     │
     ▼
Input JSON  ──────────────►  PDF Loader (PyMuPDF)
                                  │
                                  ▼
                         Chunk Extraction & Cleaning
                                  │
                                  ▼
                       Embedding (MiniLM Sentence Transformer)
                                  │
                                  ▼
              ┌──────── Semantic Similarity Ranking ────────┐
              │                                              │
      Diversity Control                               Subsection Analysis
 (Top N, max-2-per-doc)                              (Top 3 refined chunks)
              │                                              │
              └──────────────────────┬───────────────────────┘
                                     ▼
                              JSON Output Generator
```

---

## **Approach**

### **1. Input Parsing**

* Read **persona** and **job-to-be-done** from `challenge1b_input.json`.
* Load all PDFs from the `PDFs/` folder.

### **2. Chunk Extraction**

* Use **PyMuPDF (fitz)** to extract **page-level text blocks**.
* Filter out **tiny or irrelevant fragments** for clean chunks.

### **3. Semantic Ranking**

* **Model:** `sentence-transformers/all-MiniLM-L6-v2` (fast, CPU-friendly).
* Combine persona & job into a **query**:

  ```
  "{persona}. Task: {job_to_be_done}"
  ```
* Compute **embeddings** for:

  * Query
  * All extracted chunks
* Rank chunks using **cosine similarity**.

### **4. Diversity Control**

* Take **top 20 chunks by relevance score**.
* Apply **max-2-per-document** rule to avoid bias.
* Keep **final top 10** for output.
  *(Future: Add MMR for better diversity control)*

### **5. Subsection Analysis**

* For each selected section:

  * Split into smaller chunks (\~300 characters).
  * Rank again using semantic similarity.
  * Keep **top-3 refined chunks** per section.

### **6. JSON Output**

* Metadata:

  * Input documents
  * Persona & job
  * Processing timestamp
* Extracted sections:

  * Document name
  * Section title
  * Page number
  * Importance rank
* Subsection analysis:

  * Refined smaller chunks with scores

---

## **Tech Stack**

* **Programming Language:** Python 3.10+
* **Libraries:**

  * `PyMuPDF (fitz)` → PDF text extraction
  * `sentence-transformers` → Embedding & ranking
  * `numpy` & `scikit-learn` → Cosine similarity
  * `json` → Structured output
* **Model:** `all-MiniLM-L6-v2` (≈120MB, CPU-friendly)
* **Runtime:** CPU-only, fully offline

---

## **Docker Setup**

### **Step 1: Build Docker Image**

```bash
docker build -t persona-driven-intelligence .
```

### **Step 2: Run Container**

```bash
docker run --rm -v $(pwd):/app persona-driven-intelligence python main.py
```

---

## **How to Run (Without Docker)**

### **Step 1: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 2: Run for All Collections**

```bash
python main.py
```

### **Outputs Generated**

```
Collection 1/challenge1b_output.json
Collection 2/challenge1b_output.json
Collection 3/challenge1b_output.json
```

---

## **Sample Output (Collection 1)**

```json
{
  "metadata": {
    "input_documents": [
      "South of France - Cities.pdf",
      "South of France - Cuisine.pdf",
      "South of France - History.pdf"
    ],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2025-07-28T20:36:01"
  },
  "extracted_sections": [
    {
      "document": "South of France - Things to Do.pdf",
      "section_title": "Coastal Adventures",
      "importance_rank": 1,
      "page_number": 2
    }
  ],
  "subsection_analysis": [
    {
      "document": "South of France - Things to Do.pdf",
      "page_number": 2,
      "refined_chunks": [
        {
          "refined_text": "The South of France is renowned for its beautiful coastline...",
          "score": 0.45
        }
      ]
    }
  ]
}
```

---

## **Future Improvements**

✔ Implement **Maximal Marginal Relevance (MMR)** for better diversity.
✔ Add **LLM-based summarization** for natural summaries.
✔ Create an **interactive dashboard** for visualization.

---

## **Author**

**Riddhi Sharma**
*Adobe Hackathon 2025 – Round 1B Submission*

---



