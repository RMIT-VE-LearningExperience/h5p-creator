// ── DOM refs ───────────────────────────────────────────────────────────
const fileInput        = document.getElementById("file-input");
const fileLabel        = document.getElementById("file-label");
const fileTags         = document.getElementById("file-tags");
const uploadSection    = document.getElementById("upload-section");
const pasteSection     = document.getElementById("paste-section");
const pasteContent     = document.getElementById("paste-content");
const subjectAreaInput = document.getElementById("subject-area");
const learnerCtxInput  = document.getElementById("learner-context");
const paraCountInput   = document.getElementById("paragraph-count");
const paraCountLabel   = document.getElementById("para-count-label");
const statusEl         = document.getElementById("status");
const generateButton   = document.getElementById("generate-button");

const resultsTitleEl    = document.getElementById("results-title");
const resultsCountBadge = document.getElementById("results-count-badge");
const resultsGrid       = document.getElementById("results-grid");
const startOverButton   = document.getElementById("start-over-button");

const previewModal        = document.getElementById("preview-modal");
const previewModalType    = document.getElementById("preview-modal-type");
const previewModalTitle   = document.getElementById("preview-modal-title");
const previewModalBody    = document.getElementById("preview-modal-body");
const previewModalClose   = document.getElementById("preview-modal-close");
const previewModalCancel  = document.getElementById("preview-modal-cancel");
const previewModalDownload = document.getElementById("preview-modal-download");


// ── Step navigation ────────────────────────────────────────────────────
function goToStep(n) {
  document.querySelectorAll(".step-panel").forEach((panel, i) => {
    panel.hidden = i + 1 !== n;
  });
  document.querySelectorAll(".step").forEach((step, i) => {
    step.classList.toggle("active", i + 1 === n);
    step.classList.toggle("done",   i + 1 < n);
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// ── Input mode (upload / paste) ────────────────────────────────────────
let inputMode = "upload";

document.querySelectorAll(".input-mode-tab").forEach(tab => {
  tab.addEventListener("click", () => {
    inputMode = tab.dataset.mode;
    document.querySelectorAll(".input-mode-tab").forEach(t =>
      t.classList.toggle("active", t === tab)
    );
    uploadSection.hidden = inputMode !== "upload";
    pasteSection.hidden  = inputMode !== "paste";
  });
});

// ── File input ─────────────────────────────────────────────────────────
fileInput.addEventListener("change", updateFileTags);

function updateFileTags() {
  const files = [...fileInput.files];
  if (!files.length) {
    fileLabel.textContent = "Choose documents";
    fileTags.innerHTML = "";
    return;
  }
  fileLabel.textContent = files.length === 1
    ? files[0].name
    : `${files.length} files selected`;
  fileTags.innerHTML = files
    .map(f => `<span class="file-tag">${escapeHtml(f.name)}</span>`)
    .join("");
}

// ── Type mix inputs → show para count when Sort Paragraphs > 0 ────────
document.querySelectorAll('.type-count-input').forEach(input => {
  input.addEventListener("input", updateConditionalFields);
});

function updateConditionalFields() {
  const sortInput = document.querySelector('.type-count-input[data-type="H5P.SortParagraphs"]');
  const sortCount = sortInput ? (parseInt(sortInput.value, 10) || 0) : 0;
  paraCountLabel.style.display = sortCount > 0 ? "" : "none";
}

function getTypeMix() {
  const mix = {};
  document.querySelectorAll('.type-count-input').forEach(input => {
    const count = Math.max(0, Math.min(10, parseInt(input.value, 10) || 0));
    if (count > 0) mix[input.dataset.type] = count;
  });
  return mix;
}

function getExpandedTypes() {
  const expanded = [];
  Object.entries(getTypeMix()).forEach(([type, count]) => {
    for (let i = 0; i < count; i++) expanded.push(type);
  });
  return expanded;
}

function getContentMode() {
  const el = document.querySelector('input[name="content-mode"]:checked');
  return el ? el.value : "shared";
}

// ── Generate button ────────────────────────────────────────────────────
generateButton.addEventListener("click", async () => {
  const files = [...fileInput.files];

  if (inputMode === "upload" && !files.length) {
    setStatus("Upload at least one document first.", false, true); return;
  }
  if (inputMode === "paste" && !pasteContent.value.trim()) {
    setStatus("Paste some content first.", false, true); return;
  }

  const expandedTypes = getExpandedTypes();
  if (!expandedTypes.length) { setStatus("Set at least one activity type above 0.", false, true); return; }

  const total = expandedTypes.length;
  setStatus(`Generating ${total} activit${total === 1 ? "y" : "ies"}`, true);
  generateButton.disabled = true;

  const mix = getTypeMix();
  gtag("event", "generate_started", {
    file_count:          files.length,
    activity_types:      Object.keys(mix).join(","),
    activity_type_count: Object.keys(mix).length,
    total_activities:    total,
    content_mode:        getContentMode(),
  });

  try {
    await runBatchGenerate(files, expandedTypes);
  } finally {
    generateButton.disabled = false;
  }
});

// ── Start over ─────────────────────────────────────────────────────────
startOverButton.addEventListener("click", () => {
  gtag("event", "start_over");
  fileInput.value = "";
  updateFileTags();
  setStatus("");
  goToStep(1);
});

// ── Core generate flow ─────────────────────────────────────────────────
async function runBatchGenerate(files, types) {
  const data = new FormData();

  if (inputMode === "upload") {
    files.forEach(f => data.append("files", f));
  } else {
    data.append("text_content", pasteContent.value.trim());
  }

  if (subjectAreaInput.value.trim()) data.append("subject_area",    subjectAreaInput.value.trim());
  if (learnerCtxInput.value.trim())  data.append("learner_context", learnerCtxInput.value.trim());

  data.append("activity_types",  JSON.stringify(types));
  data.append("content_mode",    getContentMode());
  data.append("count_per_type",  "1");
  data.append("paragraph_count", paraCountInput.value || "4");
  data.append("ai_provider",     "openai");

  // Abort if the server hasn't responded within 4 minutes
  const controller = new AbortController();
  const timeoutId  = setTimeout(() => controller.abort(), 4 * 60 * 1000);

  try {
    const response = await fetch("/activities/generate_batch", {
      method: "POST",
      body: data,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Generation failed"));

    renderResults(payload);
    const resultTypes = (payload.results || []).map(r => r.activity_type);
    gtag("event", "generate_completed", {
      activity_count: resultTypes.length,
      activity_types: [...new Set(resultTypes)].join(","),
    });
    goToStep(2);
  } catch (err) {
    clearTimeout(timeoutId);
    const isTimeout = err.name === "AbortError";
    const msg = isTimeout
      ? "Request timed out — try fewer activities per type or a smaller document."
      : err.message;
    gtag("event", "generate_failed", {
      error_type:    isTimeout ? "timeout" : "server_error",
      error_message: msg.slice(0, 100),
    });
    setStatus(msg, false, true);
  }
}

// ── Render results ─────────────────────────────────────────────────────
function renderResults(payload) {
  const results = payload.results || [];

  resultsTitleEl.textContent    = `${results.length} activit${results.length === 1 ? "y" : "ies"} generated`;
  resultsCountBadge.textContent = results.length;

  resultsGrid.innerHTML = results.map((r, i) => `
    <article class="result-card">
      <div class="result-card-info">
        <div class="result-card-type">${escapeHtml(friendlyActivityType(r.activity_type))}</div>
        <div class="result-card-title">${escapeHtml(r.title)}</div>
      </div>
      <div class="result-card-actions">
        <button class="preview-btn secondary" data-index="${i}">Preview</button>
        <button class="result-download-btn" data-index="${i}">Download .h5p</button>
      </div>
    </article>
  `).join("");

  resultsGrid.onclick = (e) => {
    const btn = e.target.closest("button[data-index]");
    if (!btn) return;
    const item = results[parseInt(btn.dataset.index, 10)];
    if (!item) return;

    if (btn.classList.contains("preview-btn")) {
      openPreviewModal(item);
    } else {
      gtag("event", "activity_downloaded", { activity_type: item.activity_type, source: "card" });
      triggerBase64Download(
        item.download_base64,
        item.filename || `${sanitiseFilename(item.title)}.h5p`,
      );
    }
  };
}

// ── Preview modal ──────────────────────────────────────────────────────

let _previewDownloadItem = null;

function openPreviewModal(item) {
  previewModalType.textContent  = friendlyActivityType(item.activity_type);
  previewModalTitle.textContent = item.title;
  previewModalBody.innerHTML    = buildPreviewBody(item);
  _previewDownloadItem = item;

  // Wire up reveal buttons (GuessTheAnswer)
  previewModalBody.querySelectorAll(".reveal-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = document.getElementById(btn.dataset.target);
      if (!target) return;
      target.hidden = !target.hidden;
      btn.textContent = target.hidden ? "Reveal answer" : "Hide answer";
    });
  });

  gtag("event", "activity_previewed", { activity_type: item.activity_type });
  previewModal.showModal();
}

previewModalClose.addEventListener("click",   () => previewModal.close());
previewModalCancel.addEventListener("click",  () => previewModal.close());
previewModalDownload.addEventListener("click", () => {
  if (!_previewDownloadItem) return;
  gtag("event", "activity_downloaded", { activity_type: _previewDownloadItem.activity_type, source: "modal" });
  triggerBase64Download(
    _previewDownloadItem.download_base64,
    _previewDownloadItem.filename || `${sanitiseFilename(_previewDownloadItem.title)}.h5p`,
  );
  previewModal.close();
});

// Close on backdrop click
previewModal.addEventListener("click", (e) => {
  if (e.target === previewModal) previewModal.close();
});

// ── Preview body builders ──────────────────────────────────────────────

function buildPreviewBody(item) {
  switch (item.activity_type) {
    case "H5P.QuestionSet": return buildQuestionSetPreview(item.questions);
    case "H5P.SortParagraphs": return buildSortParagraphsPreview(item.paragraphs);
    default: return buildPreviewFields(item.preview_fields, item.activity_type);
  }
}

function buildQuestionSetPreview(questions) {
  if (!questions || !questions.length) return "<p class='muted'>No questions available.</p>";
  return questions.map((q, i) => `
    <div class="preview-question">
      <p class="preview-question-text"><strong>Q${i + 1}.</strong> ${escapeHtml(stripHtml(q.question_html))}</p>
      <ul class="preview-answer-list">
        ${q.answers.map(a => `
          <li class="${a.correct ? "answer-correct" : ""}">
            ${a.correct
              ? '<span class="answer-tick">✓</span>'
              : '<span class="answer-tick muted">✗</span>'}
            ${escapeHtml(a.text)}
          </li>`).join("")}
      </ul>
    </div>
  `).join("");
}

function buildSortParagraphsPreview(paragraphs) {
  if (!paragraphs || !paragraphs.length) return "<p class='muted'>No paragraphs available.</p>";
  return `
    <p class="muted preview-hint">Correct order (top → bottom):</p>
    <ol class="preview-paragraph-list">
      ${paragraphs.map(p => `<li>${escapeHtml(stripHtml(p.text_html))}</li>`).join("")}
    </ol>
  `;
}

function buildPreviewFields(fields, contentType) {
  if (!fields || !fields.length) return "<p class='muted'>No preview available.</p>";

  switch (contentType) {
    case "H5P.TrueFalse":     return buildTrueFalsePreview(fields);
    case "H5P.DragText":      return buildDragTextPreview(fields);
    case "H5P.Blanks":        return buildBlanksPreview(fields);
    case "H5P.GuessTheAnswer": return buildGuessTheAnswerPreview(fields);
    case "H5P.Summary":       return buildSummaryPreview(fields);
    case "H5P.MultiChoice":   return buildMultiChoicePreview(fields);
    default:                  return buildGenericFieldsPreview(fields);
  }
}

function buildTrueFalsePreview(fields) {
  const question = fields.find(f => f.label === "Question")?.value || "";
  const correct  = fields.find(f => f.label === "Correct answer")?.value || "True";
  return `
    <p class="preview-question-text">${escapeHtml(question)}</p>
    <div class="tf-pills">
      <span class="tf-pill ${correct === "True"  ? "tf-correct" : ""}">True</span>
      <span class="tf-pill ${correct === "False" ? "tf-correct" : ""}">False</span>
    </div>
  `;
}

function buildDragTextPreview(fields) {
  const instructions = fields.find(f => f.label === "Instructions")?.value || "";
  const textField    = fields.find(f => f.label?.includes("draggable"))?.value || "";
  const rendered     = parseAsteriskSyntax(escapeHtml(textField), "drag-token");
  return `
    ${instructions ? `<p class="muted preview-hint">${escapeHtml(instructions)}</p>` : ""}
    <p class="preview-cloze-text">${rendered}</p>
    <p class="muted preview-hint" style="margin-top:10px">Teal chips are the draggable words learners must place into blanks.</p>
  `;
}

function buildBlanksPreview(fields) {
  const instructions = fields.find(f => f.label === "Instructions")?.value || "";
  const text         = fields.find(f => f.label?.includes("blanks"))?.value || "";
  // text still has *answer* markers — parse them
  const rendered     = parseAsteriskSyntax(escapeHtml(text), "blank-token");
  return `
    ${instructions ? `<p class="muted preview-hint">${escapeHtml(instructions)}</p>` : ""}
    <p class="preview-cloze-text">${rendered}</p>
    <p class="muted preview-hint" style="margin-top:10px">Amber tokens are the words learners must type into blanks.</p>
  `;
}

function buildGuessTheAnswerPreview(fields) {
  const question = fields.find(f => f.label === "Question")?.value || "";
  const answer   = fields.find(f => f.label?.includes("revealed"))?.value || "";
  const uid = "gta-" + Math.random().toString(36).slice(2);
  return `
    <p class="preview-question-text">${escapeHtml(question)}</p>
    <button class="reveal-btn secondary" data-target="${uid}" style="margin-top:12px">Reveal answer</button>
    <div id="${uid}" class="reveal-answer" hidden>
      <p>${escapeHtml(answer)}</p>
    </div>
  `;
}

function buildSummaryPreview(fields) {
  const intro = fields.find(f => f.label === "Introduction")?.value || "";
  const groups = {};
  fields.filter(f => f.label !== "Introduction").forEach(f => {
    const m = f.label.match(/Statement (\d+)/);
    if (!m) return;
    const n = m[1];
    if (!groups[n]) groups[n] = { correct: null, distractors: [] };
    if (f.label.includes("correct")) groups[n].correct = f.value;
    else groups[n].distractors.push(f.value);
  });
  const groupHtml = Object.values(groups).map(g => `
    <div class="summary-group">
      <p class="summary-correct">${escapeHtml(g.correct || "")}</p>
      ${g.distractors.map(d => `<p class="summary-distractor">${escapeHtml(d)}</p>`).join("")}
    </div>
  `).join("");
  return `
    ${intro ? `<p class="muted preview-hint">${escapeHtml(intro)}</p>` : ""}
    ${groupHtml}
  `;
}

function buildMultiChoicePreview(fields) {
  const question = fields.find(f => f.label === "Question")?.value || "";
  const answers  = fields.filter(f => f.label.startsWith("Answer"));
  return `
    <p class="preview-question-text">${escapeHtml(question)}</p>
    <ul class="preview-answer-list">
      ${answers.map(a => {
        const correct = a.label.includes("✓");
        return `
          <li class="${correct ? "answer-correct" : ""}">
            <span class="answer-tick ${correct ? "" : "muted"}">${correct ? "✓" : "✗"}</span>
            ${escapeHtml(a.value)}
          </li>`;
      }).join("")}
    </ul>
  `;
}

function buildGenericFieldsPreview(fields) {
  return `
    <dl class="preview-fields">
      ${fields.map(f => `
        <dt>${escapeHtml(f.label)}</dt>
        <dd>${escapeHtml(f.value)}</dd>
      `).join("")}
    </dl>
  `;
}

// ── Shared utility: asterisk syntax → styled tokens ────────────────────
function parseAsteriskSyntax(escapedText, tokenClass) {
  // Input is already HTML-escaped; unescape *…* markers then re-escape token text
  return escapedText.replace(/\*([^*]+)\*/g, (_, inner) => {
    const word = inner.split(/[/:]/)[0].trim();
    return `<span class="${tokenClass}">${word}</span>`;
  });
}

// ── Status helpers ─────────────────────────────────────────────────────
function setStatus(message, isGenerating = false, isError = false) {
  if (isGenerating) {
    statusEl.innerHTML = `${escapeHtml(message)}<span class="ellipsis"></span>`;
    statusEl.style.color = "";
  } else {
    statusEl.textContent = message;
    statusEl.style.color = isError ? "#b42318" : "";
  }
}

// ── Utilities ──────────────────────────────────────────────────────────
function triggerBase64Download(base64, filename) {
  const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
  const blob  = new Blob([bytes], { type: "application/zip" });
  const url   = URL.createObjectURL(blob);
  const a     = document.createElement("a");
  a.href      = url;
  a.download  = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function sanitiseFilename(title) {
  return (title || "activity").replace(/[^\w\-]/g, "_").slice(0, 50) || "activity";
}

function stripHtml(html) {
  return String(html).replace(/<[^>]+>/g, "").trim();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&",  "&amp;")
    .replaceAll("<",  "&lt;")
    .replaceAll(">",  "&gt;")
    .replaceAll('"',  "&quot;")
    .replaceAll("'",  "&#39;");
}

function friendlyActivityType(value) {
  const names = {
    "H5P.QuestionSet":        "Quiz (Multiple Choice)",
    "H5P.MultiChoice":        "Multiple Choice",
    "H5P.TrueFalse":          "True / False",
    "H5P.DragText":           "Drag the Words",
    "H5P.Blanks":             "Fill in the Blanks",
    "H5P.GuessTheAnswer":     "Guess the Answer",
    "H5P.SortParagraphs":     "Sort the Paragraphs",
    "H5P.Summary":            "Summary",
    "H5P.CoursePresentation": "Presentation",
  };
  return names[value] || value || "—";
}

async function readResponsePayload(response) {
  const ct = response.headers.get("content-type") || "";
  if (ct.includes("application/json")) return response.json();
  const text = await response.text();
  try { return JSON.parse(text); }
  catch { return { detail: text || response.statusText }; }
}

function extractErrorMessage(payload, fallback) {
  if (payload && typeof payload.detail  === "string" && payload.detail.trim())  return payload.detail;
  if (payload && typeof payload.message === "string" && payload.message.trim()) return payload.message;
  return fallback;
}

// ── Feedback widget ────────────────────────────────────────────────────
const feedbackToggle   = document.getElementById("feedback-toggle");
const feedbackPanel    = document.getElementById("feedback-panel");
const feedbackName     = document.getElementById("feedback-name");
const feedbackText     = document.getElementById("feedback-text");
const feedbackSubmit   = document.getElementById("feedback-submit");
const feedbackFormWrap = document.getElementById("feedback-form-wrap");
const feedbackThanks   = document.getElementById("feedback-thanks");

feedbackToggle.addEventListener("click", () => {
  const opening = feedbackPanel.hidden;
  feedbackPanel.hidden = !opening;
  feedbackToggle.classList.toggle("active", opening);
  if (opening) {
    gtag("event", "feedback_opened");
    feedbackText.focus();
  }
});

// Close panel when clicking outside
document.addEventListener("click", (e) => {
  if (!feedbackPanel.hidden &&
      !feedbackPanel.contains(e.target) &&
      !feedbackToggle.contains(e.target)) {
    feedbackPanel.hidden = true;
    feedbackToggle.classList.remove("active");
  }
});

feedbackSubmit.addEventListener("click", async () => {
  const message = feedbackText.value.trim();
  if (!message) { feedbackText.focus(); return; }

  gtag("event", "feedback_submitted");
  feedbackSubmit.disabled = true;
  feedbackSubmit.textContent = "Sending…";

  try {
    await fetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: feedbackName.value.trim(), message }),
    });
  } catch { /* best-effort */ }

  feedbackFormWrap.hidden = true;
  feedbackThanks.hidden   = false;

  setTimeout(() => {
    feedbackPanel.hidden        = true;
    feedbackToggle.classList.remove("active");
    feedbackFormWrap.hidden     = false;
    feedbackThanks.hidden       = true;
    feedbackName.value          = "";
    feedbackText.value          = "";
    feedbackSubmit.disabled     = false;
    feedbackSubmit.textContent  = "Send feedback";
  }, 2500);
});
