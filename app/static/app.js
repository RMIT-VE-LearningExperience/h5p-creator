const form = document.getElementById("generator-form");
const fileInput = document.getElementById("file-input");
const fileLabel = document.getElementById("file-label");
const providerSelect = document.getElementById("ai-provider");
const modelInput = document.getElementById("model-name");
const statusEl = document.getElementById("status");
const suggestedBadge = document.getElementById("suggested-badge");
const summaryEl = document.getElementById("analysis-summary");
const suggestionsEl = document.getElementById("suggestions");
const previewEl = document.getElementById("section-preview");
const outputEl = document.getElementById("output");
const previewButton = document.getElementById("preview-button");
const breakdownBadge = document.getElementById("breakdown-badge");
const breakdownPlansEl = document.getElementById("breakdown-plans");
const providerDefaults = {
  openai: "gpt-4o-2024-08-06",
  anthropic: "claude-opus-4-1",
};

fileInput.addEventListener("change", () => {
  const [file] = fileInput.files;
  fileLabel.textContent = file ? file.name : "Choose a Word document";
});

providerSelect.addEventListener("change", () => {
  modelInput.value = providerDefaults[providerSelect.value] || "";
});

previewButton.addEventListener("click", async () => {
  await runAnalysis();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files[0];
  if (!file) {
    setStatus("Choose a Word document first.", true);
    return;
  }

  setStatus("Generating H5P file...");
  outputEl.className = "output empty";
  outputEl.textContent = "Generation in progress.";

  const data = new FormData();
  data.append("file", file);
  data.append("ai_provider", providerSelect.value);
  data.append("model", modelInput.value);
  data.append("activity_type", document.getElementById("activity-type").value);
  data.append("pass_percentage", document.getElementById("pass-percentage").value);

  try {
    const response = await fetch("/activities/generate", {
      method: "POST",
      body: data,
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) {
      throw new Error(extractErrorMessage(payload, "Generation failed"));
    }

    outputEl.className = "output";
    outputEl.innerHTML = `
      <div class="download-card">
        <strong>${escapeHtml(payload.title)}</strong>
        <p>Provider: ${escapeHtml(payload.ai_provider)}</p>
        <p>Model: ${escapeHtml(payload.ai_model)}</p>
        <p>Activity type: ${escapeHtml(friendlyActivityType(payload.content_type))}</p>
        <p>Usage: ${payload.input_tokens} input tokens, ${payload.output_tokens} output tokens</p>
        <a class="download-link" id="download-link" href="${payload.download_path}">Download ${escapeHtml(payload.filename)}</a>
      </div>
    `;
    attachDownloadLink(payload);
    setStatus("Generation complete.");
  } catch (error) {
    outputEl.className = "output empty";
    outputEl.textContent = "Generation failed.";
    setStatus(error.message, true);
  }
});

async function runAnalysis() {
  const file = fileInput.files[0];
  if (!file) {
    setStatus("Choose a Word document first.", true);
    return;
  }

  setStatus("Analyzing document structure...");
  const data = new FormData();
  data.append("file", file);

  try {
    const response = await fetch("/activities/analyze", {
      method: "POST",
      body: data,
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) {
      throw new Error(extractErrorMessage(payload, "Analysis failed"));
    }

    renderAnalysis(payload);
    setStatus("Preview ready.");
  } catch (error) {
    setStatus(error.message, true);
  }
}

function renderAnalysis(payload) {
  suggestedBadge.classList.remove("hidden");
  suggestedBadge.textContent = `Suggested: ${friendlyActivityType(payload.suggested_activity_type)}`;

  summaryEl.className = "summary";
  summaryEl.innerHTML = `
    <div class="summary-grid">
      <div class="stat"><strong>${payload.section_count}</strong><span>Sections</span></div>
      <div class="stat"><strong>${payload.estimated_question_count}</strong><span>Estimated questions</span></div>
      <div class="stat"><strong>${payload.estimated_slide_count}</strong><span>Estimated slides</span></div>
    </div>
    <p><strong>${escapeHtml(payload.title)}</strong></p>
    <p>${payload.is_large_document ? "Large document detected." : "Document size looks manageable."}</p>
  `;

  suggestionsEl.innerHTML = payload.suggestions
    .map((suggestion) => `<div class="suggestion">${escapeHtml(suggestion)}</div>`)
    .join("");

  previewEl.className = "section-preview";
  previewEl.innerHTML = payload.sections.length
    ? payload.sections.map(renderSectionCard).join("")
    : "<div class='preview-card'><p>No sections detected.</p></div>";

  renderBreakdownPlans(payload);
}

function renderSectionCard(section) {
  const paragraphs = section.sample_paragraphs.length
    ? `<ul>${section.sample_paragraphs.map((text) => `<li>${escapeHtml(text)}</li>`).join("")}</ul>`
    : "<p>No paragraph sample.</p>";

  const items = section.sample_list_items.length
    ? `<ul>${section.sample_list_items.map((text) => `<li>${escapeHtml(text)}</li>`).join("")}</ul>`
    : "<p>No list sample.</p>";

  return `
    <article class="preview-card">
      <h3>${escapeHtml(section.heading)}</h3>
      <p>Category: ${escapeHtml(section.category)}</p>
      <p>Paragraphs: ${section.paragraph_count} | Lists: ${section.list_count} | Questions: ${section.question_count}</p>
      ${paragraphs}
      ${items}
    </article>
  `;
}

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b42318" : "";
}

function renderBreakdownPlans(payload) {
  breakdownBadge.textContent = payload.breakdown_strategy === "generate-directly"
    ? "This document can be generated directly."
    : payload.breakdown_strategy === "split-by-question-groups"
      ? "Suggested split: separate quiz-focused groups."
      : "Suggested split: separate major heading groups.";

  breakdownPlansEl.className = "breakdown-plans";
  breakdownPlansEl.innerHTML = payload.breakdown_plans.length
    ? payload.breakdown_plans.map(renderBreakdownCard).join("")
    : "<div class='preview-card'><p>No breakdown plan available.</p></div>";
}

function renderBreakdownCard(plan) {
  const headings = plan.headings.length
    ? `<ul>${plan.headings.map((heading) => `<li>${escapeHtml(heading)}</li>`).join("")}</ul>`
    : "<p>No section headings found.</p>";

  return `
    <article class="preview-card breakdown-card">
      <h3>${escapeHtml(plan.title)}</h3>
      <p><strong>Suggested type:</strong> ${escapeHtml(friendlyActivityType(plan.suggested_activity_type))}</p>
      <p>${escapeHtml(plan.summary)}</p>
      <p>${escapeHtml(plan.rationale)}</p>
      <p>Sections ${plan.section_start} to ${plan.section_end} · ${plan.section_count} sections · ${plan.estimated_question_count} question blocks · ${plan.estimated_slide_count} slides</p>
      ${headings}
    </article>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function friendlyActivityType(value) {
  if (value === "H5P.MultiChoice") return "Multiple Choice";
  if (value === "H5P.QuestionSet") return "Quiz";
  if (value === "H5P.CoursePresentation") return "Presentation";
  return value;
}

function attachDownloadLink(payload) {
  const link = document.getElementById("download-link");
  if (!link || !payload.download_base64) {
    return;
  }

  const bytes = Uint8Array.from(atob(payload.download_base64), (char) => char.charCodeAt(0));
  const blob = new Blob([bytes], { type: "application/zip" });
  const objectUrl = URL.createObjectURL(blob);
  link.href = objectUrl;
  link.download = payload.filename;
}

async function readResponsePayload(response) {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text || response.statusText };
  }
}

function extractErrorMessage(payload, fallback) {
  if (payload && typeof payload.detail === "string" && payload.detail.trim()) {
    return payload.detail;
  }
  if (payload && typeof payload.message === "string" && payload.message.trim()) {
    return payload.message;
  }
  return fallback;
}
