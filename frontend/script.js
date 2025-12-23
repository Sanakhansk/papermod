console.log("SCRIPT LOADED");

/* =========================
   PDF.js WORKER
========================= */
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

document.addEventListener("DOMContentLoaded", () => {
  const pdfInput = document.getElementById("pdfInput");
  const canvas = document.getElementById("pdfPreview");
  const ctx = canvas.getContext("2d");
  const previewText = document.getElementById("previewText");
  const submitBtn = document.getElementById("submitBtn");
  const resultsDiv = document.getElementById("results");
  const themeToggle = document.getElementById("themeToggle");

  /* =========================
     THEME TOGGLE (SAFE TEXT)
  ========================= */
  const savedTheme = localStorage.getItem("theme") || "dark";
  document.body.setAttribute("data-theme", savedTheme);
  updateThemeButton(savedTheme);

  themeToggle.onclick = () => {
    const currentTheme = document.body.getAttribute("data-theme");
    const nextTheme = currentTheme === "dark" ? "light" : "dark";

    document.body.setAttribute("data-theme", nextTheme);
    localStorage.setItem("theme", nextTheme);
    updateThemeButton(nextTheme);
  };

  function updateThemeButton(theme) {
    themeToggle.textContent = theme === "dark"
      ? "Light mode"
      : "Dark mode";
  }

  /* =========================
     PDF PREVIEW
  ========================= */
  pdfInput.addEventListener("change", () => {
    const file = pdfInput.files[0];
    if (!file) return;

    previewText.style.display = "none";

    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const typedArray = new Uint8Array(reader.result);
        const pdf = await pdfjsLib.getDocument(typedArray).promise;
        const page = await pdf.getPage(1);

        const viewport = page.getViewport({ scale: 1 });
        const scale = canvas.parentElement.clientWidth / viewport.width;
        const scaledViewport = page.getViewport({ scale });

        canvas.width = scaledViewport.width;
        canvas.height = scaledViewport.height;

        await page.render({
          canvasContext: ctx,
          viewport: scaledViewport
        }).promise;
      } catch (err) {
        console.error("PDF preview error:", err);
      }
    };

    reader.readAsArrayBuffer(file);
  });

  /* =========================
     SUBMIT → BACKEND
  ========================= */
  submitBtn.onclick = async () => {
    const file = pdfInput.files[0];
    if (!file) {
      alert("Upload a PDF first");
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Processing...";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/parse", {
        method: "POST",
        body: formData
      });

      const data = await response.json();
      renderResults(data);
    } catch (err) {
      alert("Failed to parse PDF");
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit";
    }
  };

  /* =========================
     RENDER RESULTS
  ========================= */
  function renderResults(data) {
    resultsDiv.innerHTML = "";

    if (!data.extracted_sections || data.extracted_sections.length === 0) {
      resultsDiv.innerHTML =
        '<div class="empty-results">No sections extracted.</div>';
      return;
    }

    data.extracted_sections.forEach(sec => {
      const div = document.createElement("div");
      div.className = "result-item";

      div.innerHTML = `
        <div class="result-title">
          ${sec.importance_rank}. ${sec.section_title}
        </div>
        <div class="result-meta">
          ${sec.document} - Page ${sec.page_number}
        </div>
      `;

      resultsDiv.appendChild(div);
    });
  }
});
