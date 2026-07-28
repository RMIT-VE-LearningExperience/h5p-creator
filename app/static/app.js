// ── API base URL ───────────────────────────────────────────────────────
// Firebase Hosting has a hard 60s timeout for Cloud Run rewrites.
// Long-running generate calls bypass Firebase and hit Cloud Run directly.
const CLOUD_RUN_URL = "https://h5p-creator-155926758497.us-central1.run.app";
const API_BASE = (window.location.hostname.includes("web.app") ||
                  window.location.hostname.includes("firebaseapp.com"))
  ? CLOUD_RUN_URL : "";

// ── DOM refs ───────────────────────────────────────────────────────────
const fileInput        = document.getElementById("file-input");
const h5pWorkspace     = document.getElementById("h5p-workspace");
const canvasWorkspace  = document.getElementById("canvas-workspace");
const powerpointWorkspace = document.getElementById("powerpoint-workspace");
const youtubeWorkspace = document.getElementById("youtube-workspace");
const fileLabel        = document.getElementById("file-label");
const fileTags         = document.getElementById("file-tags");
const uploadSection    = document.getElementById("upload-section");
const pasteSection     = document.getElementById("paste-section");
const pasteContent     = document.getElementById("paste-content");
const subjectAreaInput = document.getElementById("subject-area");
const trainingLookupCard = document.getElementById("training-lookup-card");
const learnerCtxInput  = document.getElementById("learner-context");
const canvasStatusBadge = document.getElementById("canvas-status-badge");
const canvasBaseUrlInput = document.getElementById("canvas-base-url");
const canvasApiTokenInput = document.getElementById("canvas-api-token");
const canvasTokenToggle = document.getElementById("canvas-token-toggle");
const canvasConnectButton = document.getElementById("canvas-connect-button");
const canvasDisconnectButton = document.getElementById("canvas-disconnect-button");
const canvasConnectionStatus = document.getElementById("canvas-connection-status");
const canvasTools = document.getElementById("canvas-tools");
const canvasSearchInput = document.getElementById("canvas-search-input");
const canvasSearchButton = document.getElementById("canvas-search-button");
const canvasStatusEl = document.getElementById("canvas-status");
const canvasSearchResults = document.getElementById("canvas-search-results");
const canvasCourseDetail = document.getElementById("canvas-course-detail");
const canvasChatContext = document.getElementById("canvas-chat-context");
const canvasChatMessages = document.getElementById("canvas-chat-messages");
const canvasChatInput = document.getElementById("canvas-chat-input");
const canvasChatButton = document.getElementById("canvas-chat-button");
const canvasChatStatus = document.getElementById("canvas-chat-status");
const canvasFilesCount = document.getElementById("canvas-files-count");
const canvasFilesStatus = document.getElementById("canvas-files-status");
const canvasFilesList = document.getElementById("canvas-files-list");
const canvasFilePreview = document.getElementById("canvas-file-preview");
const canvasPreviewFilesButton = document.getElementById("canvas-preview-files");
const canvasAskFilesButton = document.getElementById("canvas-ask-files");
const canvasGenerateFilesButton = document.getElementById("canvas-generate-files");
const canvasFileActivityType = document.getElementById("canvas-file-activity-type");
const canvasPagesCount = document.getElementById("canvas-pages-count");
const canvasPagesStatus = document.getElementById("canvas-pages-status");
const canvasPagesList = document.getElementById("canvas-pages-list");
const canvasPagePreview = document.getElementById("canvas-page-preview");
const canvasPreviewPagesButton = document.getElementById("canvas-preview-pages");
const canvasSuggestVideosButton = document.getElementById("canvas-suggest-videos");
const canvasAskPagesButton = document.getElementById("canvas-ask-pages");
const powerpointCourseUrl = document.getElementById("powerpoint-course-url");
const powerpointLoadModulesButton = document.getElementById("powerpoint-load-modules-button");
const powerpointModuleCount = document.getElementById("powerpoint-module-count");
const powerpointModuleList = document.getElementById("powerpoint-module-list");
const powerpointSlideCount = document.getElementById("powerpoint-slide-count");
const powerpointAudience = document.getElementById("powerpoint-audience");
const powerpointIncludeImages = document.getElementById("powerpoint-include-images");
const powerpointGenerateButton = document.getElementById("powerpoint-generate-button");
const powerpointStatusBadge = document.getElementById("powerpoint-status-badge");
const powerpointStatus = document.getElementById("powerpoint-status");
const powerpointResult = document.getElementById("powerpoint-result");
const powerpointLoaderWrap = document.getElementById("powerpoint-loader-wrap");
const powerpointLoaderBar = document.getElementById("powerpoint-loader-bar");
const powerpointLoaderMessage = document.getElementById("powerpoint-loader-message");
const youtubeStatusBadge = document.getElementById("youtube-status-badge");
const youtubeSearchInput = document.getElementById("youtube-search-input");
const youtubeSearchButton = document.getElementById("youtube-search-button");
const youtubeStatusEl = document.getElementById("youtube-status");
const youtubeResults = document.getElementById("youtube-results");
const youtubeSelectedCount = document.getElementById("youtube-selected-count");
const youtubeChatMessages = document.getElementById("youtube-chat-messages");
const youtubeChatInput = document.getElementById("youtube-chat-input");
const youtubeChatButton = document.getElementById("youtube-chat-button");
const youtubeChatStatus = document.getElementById("youtube-chat-status");
const youtubeCanvasStatusBadge = document.getElementById("youtube-canvas-status-badge");
const youtubeCanvasBaseUrlInput = document.getElementById("youtube-canvas-base-url");
const youtubeCanvasApiTokenInput = document.getElementById("youtube-canvas-api-token");
const youtubeCanvasTokenToggle = document.getElementById("youtube-canvas-token-toggle");
const youtubeCanvasConnectButton = document.getElementById("youtube-canvas-connect-button");
const youtubeCanvasDisconnectButton = document.getElementById("youtube-canvas-disconnect-button");
const youtubeCanvasConnectionStatus = document.getElementById("youtube-canvas-connection-status");
const youtubeConnectSlide = document.getElementById("youtube-connect-slide");
const youtubeCanvasTools = document.getElementById("youtube-canvas-tools");
const youtubeCanvasCourseSearch = document.getElementById("youtube-canvas-course-search");
const youtubeCanvasCourseSearchButton = document.getElementById("youtube-canvas-course-search-button");
const youtubeCanvasSourceStatus = document.getElementById("youtube-canvas-source-status");
const youtubeCanvasCourseResults = document.getElementById("youtube-canvas-course-results");
const youtubeCanvasSourcePicker = document.getElementById("youtube-canvas-source-picker");
const youtubeCanvasCourseTitle = document.getElementById("youtube-canvas-course-title");
const youtubeCanvasModuleList = document.getElementById("youtube-canvas-module-list");
const youtubeCanvasPageList = document.getElementById("youtube-canvas-page-list");
const youtubeCanvasSuggestButton = document.getElementById("youtube-canvas-suggest-button");
const youtubeAqfLevelSelect = document.getElementById("youtube-aqf-level");
const youtubeAqfSuggestion = document.getElementById("youtube-aqf-suggestion");
const youtubeSlotPanel = document.getElementById("youtube-slot-panel");
const youtubeSlotResults = document.getElementById("youtube-slot-results");
const youtubeStepPills = [1, 2, 3].map(n => document.getElementById(`youtube-step-pill-${n}`));
const youtubeConnectSummary = document.getElementById("youtube-connect-summary");
const youtubeConnectSummaryText = document.getElementById("youtube-connect-summary-text");
const youtubeConnectChangeButton = document.getElementById("youtube-connect-change-button");
const youtubeConnectForm = document.getElementById("youtube-connect-form");
const youtubeContentSummary = document.getElementById("youtube-content-summary");
const youtubeContentSummaryText = document.getElementById("youtube-content-summary-text");
const youtubeContentChangeButton = document.getElementById("youtube-content-change-button");
const youtubeContentForm = document.getElementById("youtube-content-form");
const youtubeManualToggle = document.getElementById("youtube-manual-toggle");
const youtubeManualPanel = document.getElementById("youtube-manual-panel");
const youtubeAccountMenu = document.getElementById("youtube-account-menu");
const youtubeAccountTrigger = document.getElementById("youtube-account-trigger");
const youtubeAccountAvatar = document.getElementById("youtube-account-avatar");
const youtubeAccountName = document.getElementById("youtube-account-name");
const youtubeAccountHost = document.getElementById("youtube-account-host");
const youtubeAccountPopover = document.getElementById("youtube-account-popover");
const youtubeAccountChange = document.getElementById("youtube-account-change");
const youtubeAccountDisconnect = document.getElementById("youtube-account-disconnect");
const paraCountInput   = document.getElementById("paragraph-count");
const paraCountLabel   = document.getElementById("para-count-label");
const statusEl         = document.getElementById("status");
const generateButton   = document.getElementById("generate-button");
const loaderWrap       = document.getElementById("loader-wrap");
const loaderBar        = document.getElementById("loader-bar");
const loaderMessage    = document.getElementById("loader-message");
const activityCounter  = document.getElementById("activity-counter");
const activityCountEl  = document.getElementById("activity-count");

const MAX_ACTIVITIES = 5;
let trainingLookup = { code: "", status: "idle", product: null, error: "" };
let trainingLookupTimer = null;

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

const youtubePreviewModal = document.getElementById("youtube-preview-modal");
const youtubePreviewChannel = document.getElementById("youtube-preview-channel");
const youtubePreviewTitle = document.getElementById("youtube-preview-title");
const youtubePreviewFrame = document.getElementById("youtube-preview-frame");
const youtubePreviewTranscriptMeta = document.getElementById("youtube-preview-transcript-meta");
const youtubePreviewTranscriptBody = document.getElementById("youtube-preview-transcript-body");
const youtubePreviewClose = document.getElementById("youtube-preview-close");
const youtubePreviewOpen = document.getElementById("youtube-preview-open");
const youtubePreviewCopy = document.getElementById("youtube-preview-copy");

// ── App tabs ──────────────────────────────────────────────────────────
const WORKSPACE_PAGES = {
  "/": { workspace: "h5p", title: "H5P Creator" },
  "/h5p": { workspace: "h5p", title: "H5P Creator" },
  "/canvas": { workspace: "canvas", title: "Canvas Courses" },
  "/powerpoint": { workspace: "powerpoint", title: "Course PowerPoint" },
  "/youtube": { workspace: "youtube", title: "Video Finder" },
};

function activateWorkspace(target) {
  const page = Object.values(WORKSPACE_PAGES).find(item => item.workspace === target)
    || WORKSPACE_PAGES["/h5p"];
  h5pWorkspace.hidden = target !== "h5p";
  canvasWorkspace.hidden = target !== "canvas";
  if (powerpointWorkspace) powerpointWorkspace.hidden = target !== "powerpoint";
  if (youtubeWorkspace) youtubeWorkspace.hidden = target !== "youtube";
  document.title = `${page.title} · RMIT VE Learning Experience`;
  const appTitle = document.getElementById("app-title-text");
  const footerProduct = document.getElementById("footer-product-name");
  if (appTitle) appTitle.textContent = page.title;
  if (footerProduct) footerProduct.textContent = page.title;
  document.querySelector(".shell")?.classList.toggle("shell-wide", target === "youtube");
}

const initialPage = WORKSPACE_PAGES[window.location.pathname] || WORKSPACE_PAGES["/h5p"];
activateWorkspace(initialPage.workspace);

window.addEventListener("popstate", () => {
  const page = WORKSPACE_PAGES[window.location.pathname] || WORKSPACE_PAGES["/h5p"];
  activateWorkspace(page.workspace);
});

document.addEventListener("click", handleYouTubeEmbedCopy);

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
  input.addEventListener("input", () => {
    updateConditionalFields();
    updateActivityCounter();
  });
});

function updateConditionalFields() {
  const sortInput = document.querySelector('.type-count-input[data-type="H5P.SortParagraphs"]');
  const sortCount = sortInput ? (parseInt(sortInput.value, 10) || 0) : 0;
  paraCountLabel.style.display = sortCount > 0 ? "" : "none";
}

function updateActivityCounter() {
  const total = getExpandedTypes().length;
  activityCountEl.textContent = total;
  activityCounter.classList.toggle("at-limit", total >= MAX_ACTIVITIES);
}

function getTypeMix() {
  const mix = {};
  document.querySelectorAll('.type-count-input').forEach(input => {
    const count = Math.max(0, Math.min(MAX_ACTIVITIES, parseInt(input.value, 10) || 0));
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

// ── training.gov.au lookup ────────────────────────────────────────────
subjectAreaInput.addEventListener("input", () => {
  const code = normaliseTrainingCode(subjectAreaInput.value);
  if (trainingLookupTimer) clearTimeout(trainingLookupTimer);
  if (!looksLikeTrainingCode(code)) {
    trainingLookup = { code: "", status: "idle", product: null, error: "" };
    renderTrainingLookup();
    return;
  }
  trainingLookup = { code, status: "pending", product: null, error: "" };
  renderTrainingLookup();
  trainingLookupTimer = setTimeout(() => lookupTrainingProduct(code), 500);
});

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
  if (expandedTypes.length > MAX_ACTIVITIES) { setStatus(`Beta limit: max ${MAX_ACTIVITIES} activities per run. Reduce your mix and try again.`, false, true); return; }

  const total = expandedTypes.length;
  generateButton.disabled = true;
  GenerationLoader.start();

  const mix = getTypeMix();
  gtag("event", "generate_started", {
    file_count:          files.length,
    activity_types:      Object.keys(mix).join(","),
    activity_type_count: Object.keys(mix).length,
    total_activities:    total,
    content_mode:        getContentMode(),
  });

  try {
    await ensureTrainingLookupReady();
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
  if (trainingLookup.product)        data.append("training_context", formatTrainingContext(trainingLookup.product));
  if (learnerCtxInput.value.trim())  data.append("learner_context", learnerCtxInput.value.trim());

  data.append("activity_types",  JSON.stringify(types));
  data.append("content_mode",    getContentMode());
  data.append("count_per_type",  "1");
  data.append("paragraph_count", paraCountInput.value || "4");
  data.append("ai_provider",     activeAiProvider);

  // Abort if the server hasn't responded within 4 minutes
  const controller = new AbortController();
  const timeoutId  = setTimeout(() => controller.abort(), 7 * 60 * 1000);

  dbg("→ POST /activities/generate_batch", {
    ai_provider: data.get("ai_provider"),
    activity_types: data.get("activity_types"),
    content_mode: data.get("content_mode"),
    subject_area: data.get("subject_area") || "(none)",
    training_context: data.get("training_context") ? "included" : "(none)",
    files: [...(inputMode === "upload" ? fileInput.files : [])].map(f => f.name),
  });

  try {
    const response = await fetch(`${API_BASE}/activities/generate_batch`, {
      method: "POST",
      body: data,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    dbg(`← HTTP ${response.status} ${response.statusText}`);
    const payload = await readResponsePayload(response);
    if (!response.ok) {
      dbg("Error payload", payload);
      throw new Error(extractErrorMessage(payload, "Generation failed"));
    }
    const providers = [...new Set((payload.results || []).map(r => `${r.ai_provider} / ${r.ai_model}`))];
    dbg("Success", { count: (payload.results || []).length, ai_used: providers, titles: (payload.results || []).map(r => r.title) });
    GenerationLoader.finish();
    renderResults(payload);
    recordGenerated((payload.results || []).length);
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
    dbg("Exception", { name: err.name, message: err.message });
    GenerationLoader.fail();
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
    <p class="muted preview-hint" style="margin-top:10px">Blue tokens are the draggable words learners must place into blanks.</p>
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
    <p class="muted preview-hint" style="margin-top:10px">Red tokens are the words learners must type into blanks.</p>
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

// ── Course PowerPoint generator ───────────────────────────────────────
initPowerPointGenerator();

const powerpointSelectedModules = new Set();

function initPowerPointGenerator() {
  if (!powerpointGenerateButton) return;
  powerpointGenerateButton.addEventListener("click", generateCoursePowerPoint);
  if (powerpointLoadModulesButton) powerpointLoadModulesButton.addEventListener("click", loadPowerPointModules);
  if (powerpointModuleList) {
    powerpointModuleList.addEventListener("change", (e) => {
      const input = e.target.closest('input[type="checkbox"][data-module-id]');
      if (!input) return;
      if (input.checked) powerpointSelectedModules.add(input.dataset.moduleId);
      else powerpointSelectedModules.delete(input.dataset.moduleId);
      updatePowerPointModuleCount();
    });
  }
  if (powerpointCourseUrl) {
    powerpointCourseUrl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        loadPowerPointModules();
      }
    });
    powerpointCourseUrl.addEventListener("input", () => {
      powerpointSelectedModules.clear();
      if (powerpointModuleList) {
        powerpointModuleList.hidden = true;
        powerpointModuleList.innerHTML = "";
      }
      if (powerpointModuleCount) powerpointModuleCount.textContent = "No modules loaded";
    });
  }
}

async function loadPowerPointModules() {
  const courseUrl = (powerpointCourseUrl?.value || "").trim();
  if (!courseUrl) {
    setPowerPointStatus("Enter a Canvas course URL or ID.", true);
    powerpointCourseUrl?.focus();
    return;
  }
  powerpointLoadModulesButton.disabled = true;
  setPowerPointStatus("Loading course modules...");
  if (powerpointModuleList) {
    powerpointModuleList.hidden = false;
    powerpointModuleList.innerHTML = `<p class="muted">Loading modules...</p>`;
  }
  try {
    const response = await fetch(`${API_BASE}/powerpoints/course/modules?course_url=${encodeURIComponent(courseUrl)}`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Module loading failed"));
    renderPowerPointModules(payload.modules || []);
    setPowerPointStatus("");
    gtag("event", "powerpoint_modules_loaded", { module_count: (payload.modules || []).length });
  } catch (err) {
    setPowerPointStatus(err.message, true);
    if (powerpointModuleList) {
      powerpointModuleList.hidden = true;
      powerpointModuleList.innerHTML = "";
    }
  } finally {
    powerpointLoadModulesButton.disabled = false;
  }
}

function renderPowerPointModules(modules) {
  powerpointSelectedModules.clear();
  if (!powerpointModuleList) return;
  if (!modules.length) {
    powerpointModuleList.hidden = false;
    powerpointModuleList.innerHTML = `<p class="muted">No modules found for this course.</p>`;
    updatePowerPointModuleCount(0);
    return;
  }
  powerpointModuleList.hidden = false;
  powerpointModuleList.innerHTML = modules.map((module, index) => `
    <label class="powerpoint-module-row">
      <input type="checkbox" data-module-id="${escapeHtml(module.id)}">
      <span class="canvas-file-meta">
        <strong>${escapeHtml(module.name || "Untitled module")}</strong>
        <span>${escapeHtml(String(module.items_count || 0))} item${Number(module.items_count || 0) === 1 ? "" : "s"}${module.published ? "" : " · unpublished"}</span>
      </span>
    </label>
  `).join("");
  updatePowerPointModuleCount(modules.length);
}

function updatePowerPointModuleCount(total = null) {
  if (!powerpointModuleCount) return;
  const selected = powerpointSelectedModules.size;
  if (selected > 0) {
    powerpointModuleCount.textContent = `${selected} selected`;
  } else if (total != null) {
    powerpointModuleCount.textContent = `${total} loaded · all will be used unless selected`;
  } else {
    powerpointModuleCount.textContent = "All loaded modules will be used unless selected";
  }
}

async function generateCoursePowerPoint() {
  const courseUrl = (powerpointCourseUrl?.value || "").trim();
  if (!courseUrl) {
    setPowerPointStatus("Enter a Canvas course URL or ID.", true);
    powerpointCourseUrl?.focus();
    return;
  }
  const slideCount = Math.max(4, Math.min(40, parseInt(powerpointSlideCount?.value, 10) || 12));
  if (powerpointSlideCount) powerpointSlideCount.value = slideCount;

  powerpointGenerateButton.disabled = true;
  powerpointResult.hidden = true;
  powerpointResult.innerHTML = "";
  setPowerPointStatus("");
  PowerPointLoader.start();
  if (powerpointStatusBadge) powerpointStatusBadge.textContent = "Generating";

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 8 * 60 * 1000);

  try {
    const response = await fetch(`${API_BASE}/powerpoints/course`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      body: JSON.stringify({
        course_url: courseUrl,
        slide_count: slideCount,
        audience: (powerpointAudience?.value || "").trim(),
        include_images: Boolean(powerpointIncludeImages?.checked),
        selected_module_ids: [...powerpointSelectedModules].map(id => parseInt(id, 10)).filter(Number.isFinite),
      }),
    });
    clearTimeout(timeoutId);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "PowerPoint generation failed"));

    PowerPointLoader.finish();
    if (powerpointStatusBadge) powerpointStatusBadge.textContent = "Ready";
    renderPowerPointResult(payload);
    gtag("event", "powerpoint_generated", {
      slide_count: payload.slide_count || slideCount,
      include_images: Boolean(powerpointIncludeImages?.checked),
    });
  } catch (err) {
    clearTimeout(timeoutId);
    PowerPointLoader.fail();
    if (powerpointStatusBadge) powerpointStatusBadge.textContent = "Ready";
    const msg = err.name === "AbortError"
      ? "Request timed out. Try fewer slides or a smaller course."
      : err.message;
    setPowerPointStatus(msg, true);
  } finally {
    powerpointGenerateButton.disabled = false;
  }
}

function renderPowerPointResult(payload) {
  if (!powerpointResult) return;
  powerpointResult.hidden = false;
  powerpointResult.innerHTML = `
    <article class="powerpoint-download">
      <div>
        <p class="eyebrow">Generated Deck</p>
        <h3>${escapeHtml(payload.title || "Course PowerPoint")}</h3>
        <p class="muted">${escapeHtml(String(payload.slide_count || 0))} slides · ${escapeHtml(payload.ai_provider || "VAL")} / ${escapeHtml(payload.ai_model || "")}</p>
      </div>
      <button type="button" id="powerpoint-download-button">Download .pptx</button>
    </article>
  `;
  const button = document.getElementById("powerpoint-download-button");
  if (button) {
    button.addEventListener("click", () => {
      triggerBase64Download(
        payload.download_base64,
        payload.filename || `${sanitiseFilename(payload.title)}.pptx`,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
      );
      gtag("event", "powerpoint_downloaded");
    });
  }
}

function setPowerPointStatus(message, isError = false) {
  if (!powerpointStatus) return;
  powerpointStatus.textContent = message;
  powerpointStatus.style.color = isError ? "#b42318" : "";
}

const PowerPointLoader = (() => {
  const MESSAGES = [
    "Reading Canvas modules and pages",
    "Extracting course file text",
    "Condensing the course into slide structure",
    "Selecting useful visuals where available",
    "Rendering the PowerPoint deck",
  ];
  let timer = null;
  let index = 0;

  function showNext() {
    if (!powerpointLoaderMessage || !powerpointLoaderBar) return;
    powerpointLoaderMessage.textContent = MESSAGES[index % MESSAGES.length];
    powerpointLoaderBar.style.width = `${Math.min(88, 12 + index * 16)}%`;
    index++;
    timer = setTimeout(showNext, 2600);
  }

  return {
    start() {
      if (!powerpointLoaderWrap || !powerpointLoaderBar || !powerpointLoaderMessage) return;
      index = 0;
      powerpointLoaderWrap.hidden = false;
      powerpointLoaderBar.style.width = "6%";
      showNext();
    },
    finish() {
      clearTimeout(timer);
      if (!powerpointLoaderWrap || !powerpointLoaderBar || !powerpointLoaderMessage) return;
      powerpointLoaderMessage.textContent = "Done!";
      powerpointLoaderBar.style.width = "100%";
      setTimeout(() => {
        powerpointLoaderWrap.hidden = true;
        powerpointLoaderBar.style.width = "0%";
      }, 550);
    },
    fail() {
      clearTimeout(timer);
      if (!powerpointLoaderWrap || !powerpointLoaderBar) return;
      powerpointLoaderWrap.hidden = true;
      powerpointLoaderBar.style.width = "0%";
    },
  };
})();

function dbg() {}

// ── Activity counter ───────────────────────────────────────────────────
function renderActivityCount(total) {
  const wrap = document.getElementById("footer-count");
  const num  = document.getElementById("footer-count-num");
  if (!wrap || !num || total <= 0) return;
  num.textContent = total.toLocaleString();
  wrap.hidden = false;
}

(async () => {
  try {
    const res  = await fetch(`${API_BASE}/stats`);
    const data = await res.json();
    renderActivityCount(data.total_generated || 0);
  } catch { /* silent */ }
})();

async function recordGenerated(count) {
  try {
    await fetch(`${API_BASE}/stats/record`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ count }),
    });
    const num = document.getElementById("footer-count-num");
    const current = parseInt((num?.textContent || "0").replace(/,/g, ""), 10) || 0;
    renderActivityCount(current + count);
  } catch { /* silent */ }
}

// ── Generation loader ──────────────────────────────────────────────────
const GenerationLoader = (() => {
  const MESSAGES = [
    "Consulting the ghost of Benjamin Bloom",
    "Massaging learning outcomes into existence",
    "Arguing with the AI about which distractors are plausible",
    "Checking that the correct answer is actually correct",
    "Generating H5P files nobody asked for… wait, you did",
    "Converting caffeine into pedagogical content",
    "Applying Constructivist theory (and hoping for the best)",
    "Persuading a language model that education matters",
    "Adding just enough scaffolding to be SCORM-compliant",
    "Counting the blanks in Fill in the Blanks",
    "Shuffling distractors to keep learners honest",
    "Ensuring the True/False isn't obviously True",
    "Translating your document into something learners will actually read",
    "Calibrating difficulty — not too easy, not Bloom's Level 6 on day one",
    "Making drag-and-drop slightly less frustrating than real life",
    "Checking that Sort the Paragraphs is actually sortable",
    "Negotiating with the content — it resists being educational",
  ];
  const FINAL_MSG = "Almost there — the AI is just triple-checking its work";

  const STAGES = [
    [10, 1000], [22, 2000], [34, 3000], [45, 4000],
    [54, 5000], [62, 7000], [68, 9000], [73, 12000],
    [77, 15000], [80, 18000], [83, 22000], [86, 25000],
    [88, 25000], [90, 30000],
  ];

  let msgTimer = null, stageTimer = null;
  let msgIndex = 0, stageIndex = 0, finalShown = false, shuffled = [];

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function showMessage(text) {
    loaderMessage.classList.add("fading");
    setTimeout(() => {
      loaderMessage.textContent = text;
      loaderMessage.classList.remove("fading");
    }, 300);
  }

  function cycleMessage() {
    const pct = parseFloat(loaderBar.style.width) || 0;
    if (pct >= 75 && !finalShown) {
      finalShown = true;
      showMessage(FINAL_MSG);
    } else if (!finalShown) {
      showMessage(shuffled[msgIndex % shuffled.length]);
      msgIndex++;
    }
    msgTimer = setTimeout(cycleMessage, 2500);
  }

  function advanceStage() {
    if (stageIndex >= STAGES.length) return;
    const [pct, delay] = STAGES[stageIndex++];
    loaderBar.style.width = pct + "%";
    stageTimer = setTimeout(advanceStage, delay);
  }

  function cleanup() {
    clearTimeout(msgTimer);
    clearTimeout(stageTimer);
    msgTimer = stageTimer = null;
  }

  return {
    start() {
      msgIndex = stageIndex = 0;
      finalShown = false;
      shuffled = shuffle(MESSAGES);

      loaderWrap.hidden = false;
      statusEl.textContent = "";
      statusEl.style.color = "";

      loaderBar.style.transition = "none";
      loaderBar.style.width = "4%";
      requestAnimationFrame(() => { loaderBar.style.transition = ""; });

      showMessage(shuffled[0]);
      msgIndex = 1;
      msgTimer   = setTimeout(cycleMessage, 2500);
      stageTimer = setTimeout(advanceStage, 800);
    },

    finish() {
      cleanup();
      showMessage("Done!");
      loaderBar.style.transition = "width 400ms ease-out";
      loaderBar.style.width = "100%";
      setTimeout(() => {
        loaderWrap.hidden = true;
        loaderBar.style.width = "0%";
        loaderBar.style.transition = "";
      }, 600);
    },

    fail() {
      cleanup();
      loaderWrap.hidden = true;
      loaderBar.style.width = "0%";
    },
  };
})();

// ── Status helpers ─────────────────────────────────────────────────────
function setStatus(message, isGenerating = false, isError = false) {
  if (isGenerating) {
    statusEl.innerHTML = `${escapeHtml(message)}<span class="ellipsis"></span>`;
    statusEl.style.color = "";
  } else if (isError && message === "VAL_NETWORK_ERROR") {
    statusEl.style.color = "";
    statusEl.innerHTML = `
      <div class="vpn-error">
        <span class="vpn-error-icon">🔒</span>
        <div class="vpn-error-body">
          <strong>RMIT network required</strong>
          <p>The VAL API is only accessible on campus or via the RMIT VPN.<br>
             Connect to the VPN and try again.</p>
        </div>
      </div>`;
  } else {
    statusEl.textContent = message;
    statusEl.style.color = isError ? "#b42318" : "";
  }
}

// ── Utilities ──────────────────────────────────────────────────────────
function triggerBase64Download(base64, filename, mimeType = "application/zip") {
  const bytes = Uint8Array.from(atob(base64), c => c.charCodeAt(0));
  const blob  = new Blob([bytes], { type: mimeType });
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

function normaliseTrainingCode(value) {
  return String(value || "").replace(/[^A-Za-z0-9]/g, "").toUpperCase();
}

function looksLikeTrainingCode(value) {
  return /^[A-Z0-9]{5,14}$/.test(value || "") && /[0-9]/.test(value || "");
}

async function ensureTrainingLookupReady() {
  const code = normaliseTrainingCode(subjectAreaInput.value);
  if (!looksLikeTrainingCode(code)) return;
  if (trainingLookup.product && trainingLookup.code === code) return;
  if (trainingLookupTimer) {
    clearTimeout(trainingLookupTimer);
    trainingLookupTimer = null;
  }
  await lookupTrainingProduct(code);
}

async function lookupTrainingProduct(code) {
  trainingLookup = { code, status: "loading", product: null, error: "" };
  renderTrainingLookup();
  try {
    const response = await fetch(`${API_BASE}/activities/training-product/${encodeURIComponent(code)}`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "training.gov.au lookup failed"));
    if (normaliseTrainingCode(subjectAreaInput.value) !== code) return;
    trainingLookup = { code, status: "ready", product: payload, error: "" };
    if (payload.title && subjectAreaInput.value.trim().toUpperCase() === code) {
      subjectAreaInput.value = `${payload.code} ${payload.title}`;
    }
  } catch (err) {
    if (normaliseTrainingCode(subjectAreaInput.value) !== code) return;
    trainingLookup = { code, status: "error", product: null, error: err.message };
  }
  renderTrainingLookup();
}

function renderTrainingLookup() {
  if (!trainingLookupCard) return;
  const { status, product, error, code } = trainingLookup;
  if (status === "idle") {
    trainingLookupCard.hidden = true;
    trainingLookupCard.innerHTML = "";
    return;
  }
  trainingLookupCard.hidden = false;
  if (status === "pending" || status === "loading") {
    trainingLookupCard.className = "training-lookup-card loading";
    trainingLookupCard.textContent = status === "loading"
      ? `Checking training.gov.au for ${code}...`
      : `Will check training.gov.au for ${code}`;
    return;
  }
  if (status === "error") {
    trainingLookupCard.className = "training-lookup-card error";
    trainingLookupCard.textContent = `Could not fetch ${code}; generation will still use your typed subject.`;
    dbg("training.gov.au lookup failed", { code, error });
    return;
  }
  trainingLookupCard.className = "training-lookup-card ready";
  const unitCount = product.units && product.units.length ? `${product.units.length} units found` : "";
  trainingLookupCard.innerHTML = `
    <strong>${escapeHtml(product.code)} ${escapeHtml(product.title || "")}</strong>
    <span>${escapeHtml(product.product_type || "training product")}${unitCount ? ` · ${escapeHtml(unitCount)}` : ""}</span>
  `;
}

function formatTrainingContext(product) {
  const lines = [
    `Code: ${product.code || ""}`,
    `Title: ${product.title || ""}`,
    `Type: ${product.product_type || "training product"}`,
    `Source: ${product.source_url || ""}`,
  ];
  if (product.usage_recommendation) lines.push(`Usage recommendation: ${product.usage_recommendation}`);
  if (product.summary) lines.push("", "Summary:", product.summary);
  if (product.units && product.units.length) {
    lines.push("", "Units of competency:");
    product.units.slice(0, 80).forEach(unit => {
      lines.push(`- ${unit.code}: ${unit.title}${unit.essential ? ` [${unit.essential}]` : ""}`);
    });
  }
  return lines.join("\n").trim();
}

// ── Canvas course reader ───────────────────────────────────────────────
let canvasReady = false;
const canvasCourseContext = new Map();
const canvasSelectedFiles = new Set();
const canvasSelectedPages = new Set();
let canvasCurrentCourseId = null;
let canvasCurrentCourseName = "";
let canvasSessionCredentials = null;

const canvasConnectionViews = [
  {
    workspace: "canvas",
    baseUrl: canvasBaseUrlInput,
    apiToken: canvasApiTokenInput,
    tokenToggle: canvasTokenToggle,
    connectButton: canvasConnectButton,
    disconnectButton: canvasDisconnectButton,
    badge: canvasStatusBadge,
    status: canvasConnectionStatus,
    tools: canvasTools,
  },
  {
    workspace: "youtube",
    baseUrl: youtubeCanvasBaseUrlInput,
    apiToken: youtubeCanvasApiTokenInput,
    tokenToggle: youtubeCanvasTokenToggle,
    connectButton: youtubeCanvasConnectButton,
    disconnectButton: youtubeCanvasDisconnectButton,
    badge: youtubeCanvasStatusBadge,
    status: youtubeCanvasConnectionStatus,
    tools: youtubeCanvasTools,
  },
];

initCanvasConnections();
initCanvasReader();

function initCanvasConnections() {
  canvasConnectionViews.forEach(view => {
    if (!view.connectButton || !view.baseUrl || !view.apiToken) return;
    view.connectButton.addEventListener("click", () => connectCanvas(view));
    view.disconnectButton?.addEventListener("click", disconnectCanvas);
    view.tokenToggle?.addEventListener("click", () => {
      const showing = view.apiToken.type === "text";
      view.apiToken.type = showing ? "password" : "text";
      view.tokenToggle.textContent = showing ? "Show" : "Hide";
      view.tokenToggle.setAttribute("aria-label", `${showing ? "Show" : "Hide"} API token`);
    });
    view.apiToken.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        connectCanvas(view);
      }
    });
  });

  const activeView = canvasConnectionViews.find(view => view.workspace === initialPage.workspace);
  if (activeView) refreshCanvasStatus(activeView);
}

function canvasCredentialHeaders(credentials = canvasSessionCredentials) {
  if (!credentials) return {};
  return {
    "X-Canvas-Base-URL": credentials.baseUrl,
    "X-Canvas-API-Token": credentials.apiToken,
  };
}

async function canvasFetch(path, options = {}, credentials = canvasSessionCredentials) {
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...canvasCredentialHeaders(credentials),
    },
  });
}

async function connectCanvas(view) {
  const credentials = {
    baseUrl: view.baseUrl.value.trim().replace(/\/$/, ""),
    apiToken: view.apiToken.value.trim(),
  };
  if (!credentials.baseUrl || !credentials.apiToken) {
    setCanvasConnectionStatus(view, "Enter both your Canvas institution URL and API token.", true);
    return;
  }

  view.connectButton.disabled = true;
  setCanvasConnectionStatus(view, "Checking access...");
  try {
    const response = await canvasFetch("/canvas/status", {}, credentials);
    const payload = await readResponsePayload(response);
    if (!response.ok || !payload.connected) {
      throw new Error(extractErrorMessage(payload, "Could not connect to Canvas"));
    }
    canvasSessionCredentials = credentials;
    canvasConnectionViews.forEach(item => {
      if (item.baseUrl) item.baseUrl.value = credentials.baseUrl;
      if (item.apiToken) item.apiToken.value = "";
    });
    setCanvasConnected(payload);
    gtag("event", "canvas_user_connected", { canvas_host: new URL(credentials.baseUrl).hostname });
  } catch (err) {
    canvasSessionCredentials = null;
    setCanvasConnectionStatus(view, err.message, true);
    setCanvasDisconnected();
  } finally {
    view.connectButton.disabled = false;
  }
}

function disconnectCanvas() {
  canvasSessionCredentials = null;
  canvasReady = false;
  canvasCourseContext.clear();
  canvasSelectedFiles.clear();
  canvasSelectedPages.clear();
  canvasCurrentCourseId = null;
  canvasCurrentCourseName = "";
  canvasConnectionViews.forEach(view => {
    if (view.apiToken) view.apiToken.value = "";
    if (view.status) view.status.textContent = "Disconnected. The session token has been cleared.";
  });
  setCanvasDisconnected();
  resetYouTubeCanvasSource();
}

function setCanvasConnected(payload) {
  canvasReady = true;
  const name = payload.user?.name || "Canvas user";
  canvasConnectionViews.forEach(view => {
    if (view.badge) {
      view.badge.textContent = "Connected";
      view.badge.classList.add("canvas-badge-ready");
      view.badge.classList.remove("canvas-badge-off");
    }
    if (view.tools) view.tools.hidden = false;
    if (view.disconnectButton) view.disconnectButton.hidden = view.workspace === "youtube";
    if (view.connectButton) view.connectButton.textContent = "Reconnect";
    setCanvasConnectionStatus(view, `Connected as ${name}.`);
  });
  if (canvasSearchButton) canvasSearchButton.disabled = false;
  const host = canvasSessionCredentials ? new URL(canvasSessionCredentials.baseUrl).hostname : "";
  setYoutubeConnectSummary(`Connected as ${name}${host ? ` · ${host}` : ""}.`);
  updateYouTubeAccountProfile(payload);
  updateYoutubeStepIndicator(youtubeContentChosen ? 3 : 2);
}

function setCanvasDisconnected() {
  canvasConnectionViews.forEach(view => {
    if (view.badge) {
      view.badge.textContent = "Not connected";
      view.badge.classList.remove("canvas-badge-ready");
      view.badge.classList.add("canvas-badge-off");
    }
    if (view.tools) view.tools.hidden = true;
    if (view.disconnectButton) view.disconnectButton.hidden = true;
    if (view.connectButton) view.connectButton.textContent = "Connect";
  });
  if (canvasSearchButton) canvasSearchButton.disabled = true;
  resetYoutubeConnectSummary();
  resetYouTubeAccountProfile();
  updateYoutubeStepIndicator(1);
}

function setCanvasConnectionStatus(view, message, isError = false) {
  if (!view?.status) return;
  view.status.textContent = message;
  view.status.style.color = isError ? "#b42318" : "";
}

function initCanvasReader() {
  if (!canvasSearchButton || !canvasSearchInput) return;
  canvasSearchButton.addEventListener("click", runCanvasSearch);
  canvasSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      runCanvasSearch();
    }
  });
  canvasSearchResults.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-course-id]");
    if (!btn) return;
    loadCanvasCourse(btn.dataset.courseId);
  });
  if (canvasChatButton) {
    canvasChatButton.addEventListener("click", askCanvasChat);
  }
  if (canvasChatInput) {
    canvasChatInput.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        askCanvasChat();
      }
    });
  }
  if (canvasFilesList) {
    canvasFilesList.addEventListener("change", (e) => {
      const input = e.target.closest('input[type="checkbox"][data-file-id]');
      if (!input) return;
      if (input.checked) canvasSelectedFiles.add(input.dataset.fileId);
      else canvasSelectedFiles.delete(input.dataset.fileId);
      updateCanvasFileActions();
    });
  }
  if (canvasPagesList) {
    canvasPagesList.addEventListener("change", (e) => {
      const input = e.target.closest('input[type="checkbox"][data-page-url]');
      if (!input) return;
      if (input.checked) canvasSelectedPages.add(input.dataset.pageUrl);
      else canvasSelectedPages.delete(input.dataset.pageUrl);
      updateCanvasPageActions();
    });
  }
  if (canvasPreviewFilesButton) canvasPreviewFilesButton.addEventListener("click", previewSelectedCanvasFiles);
  if (canvasAskFilesButton) canvasAskFilesButton.addEventListener("click", askValAboutSelectedFiles);
  if (canvasGenerateFilesButton) canvasGenerateFilesButton.addEventListener("click", generateH5PFromSelectedFiles);
  if (canvasPreviewPagesButton) canvasPreviewPagesButton.addEventListener("click", previewSelectedCanvasPages);
  if (canvasSuggestVideosButton) canvasSuggestVideosButton.addEventListener("click", suggestVideosForSelectedCanvasPages);
  if (canvasAskPagesButton) canvasAskPagesButton.addEventListener("click", askValAboutSelectedPages);
  updateCanvasChatContext();
  updateCanvasFileActions();
  updateCanvasPageActions();
}

async function refreshCanvasStatus(view) {
  try {
    const response = await canvasFetch("/canvas/status");
    const payload = await readResponsePayload(response);
    if (response.ok && payload.connected) {
      setCanvasConnected(payload);
    } else {
      setCanvasDisconnected();
      setCanvasConnectionStatus(view, "Enter your Canvas details to begin.");
    }
  } catch (err) {
    canvasReady = false;
    setCanvasDisconnected();
    setCanvasConnectionStatus(view, "Canvas connection could not be checked.", true);
  }
}

async function runCanvasSearch() {
  if (!canvasReady) return;
  const query = canvasSearchInput.value.trim();
  if (query.length < 2) {
    setCanvasStatus("Enter at least 2 characters or a Canvas course ID.", true);
    return;
  }
  const directCourseId = extractCanvasCourseId(query);
  if (directCourseId) {
    await loadCanvasCourse(directCourseId);
    return;
  }

  canvasSearchButton.disabled = true;
  setCanvasStatus("Searching Canvas...");
  canvasSearchResults.innerHTML = "";
  canvasCourseDetail.hidden = true;
  try {
    const response = await canvasFetch(`/canvas/courses/search?q=${encodeURIComponent(query)}&limit=20`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Canvas search failed"));
    (payload.results || []).forEach(course => {
      if (course.id) canvasCourseContext.set(String(course.id), course);
    });
    renderCanvasSearchResults(payload.results || []);
    updateCanvasChatContext();
    setCanvasStatus((payload.results || []).length ? "" : "No matching courses found.");
    gtag("event", "canvas_course_search", { result_count: (payload.results || []).length });
  } catch (err) {
    setCanvasStatus(err.message, true);
  } finally {
    canvasSearchButton.disabled = !canvasReady;
  }
}

function renderCanvasSearchResults(courses) {
  canvasSearchResults.innerHTML = courses.map(course => `
    <article class="canvas-result">
      <div>
        <strong>${escapeHtml(course.name)}</strong>
        <span>${escapeHtml(canvasCourseMeta(course))}</span>
      </div>
      <button type="button" class="secondary" data-course-id="${escapeHtml(course.id)}">Read</button>
    </article>
  `).join("");
}

async function loadCanvasCourse(courseId) {
  setCanvasStatus(`Reading Canvas course ${courseId}...`);
  canvasCourseDetail.hidden = false;
  canvasCourseDetail.innerHTML = `<p class="muted">Loading course details...</p>`;
  try {
    const response = await canvasFetch(`/canvas/courses/${encodeURIComponent(courseId)}`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Could not read Canvas course"));
    if (payload.course?.id) canvasCourseContext.set(String(payload.course.id), payload);
    canvasCurrentCourseId = payload.course?.id || courseId;
    canvasCurrentCourseName = payload.course?.name || "";
    renderCanvasCourse(payload);
    renderCanvasPages(payload.pages || []);
    loadCanvasFiles(canvasCurrentCourseId);
    updateCanvasChatContext();
    setCanvasStatus("");
    gtag("event", "canvas_course_read", { course_id: String(courseId) });
  } catch (err) {
    canvasCourseDetail.hidden = true;
    setCanvasStatus(err.message, true);
  }
}

function renderCanvasPages(pages) {
  canvasSelectedPages.clear();
  if (canvasPagesCount) canvasPagesCount.textContent = `${pages.length} page${pages.length === 1 ? "" : "s"}`;
  if (!canvasPagesList) return;
  canvasPagesList.innerHTML = pages.map(page => `
    <label class="canvas-page-row">
      <input type="checkbox" data-page-url="${escapeHtml(page.url || "")}">
      <span class="canvas-file-meta">
        <strong>${escapeHtml(page.title || page.url || "Untitled page")}</strong>
        <span>${escapeHtml(page.url || "")}${page.published ? "" : " · unpublished"}</span>
      </span>
    </label>
  `).join("");
  if (canvasPagePreview) {
    canvasPagePreview.hidden = true;
    canvasPagePreview.innerHTML = "";
  }
  setCanvasPagesStatus(pages.length ? "" : "No Canvas pages were found in this course.");
  updateCanvasPageActions();
}

async function loadCanvasFiles(courseId) {
  if (!courseId || !canvasFilesList) return;
  canvasSelectedFiles.clear();
  updateCanvasFileActions();
  setCanvasFilesStatus("Loading readable course files...");
  canvasFilesList.innerHTML = "";
  canvasFilePreview.hidden = true;
  canvasFilePreview.innerHTML = "";
  try {
    const response = await canvasFetch(`/canvas/courses/${encodeURIComponent(courseId)}/files?limit=150`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Could not list Canvas files"));
    renderCanvasFiles(payload.results || []);
    setCanvasFilesStatus((payload.results || []).length ? "" : "No PDFs, PowerPoints, or Word documents were found in this course.");
  } catch (err) {
    setCanvasFilesStatus(err.message, true);
  }
}

function renderCanvasFiles(files) {
  if (canvasFilesCount) canvasFilesCount.textContent = `${files.length} file${files.length === 1 ? "" : "s"}`;
  canvasFilesList.innerHTML = files.map(file => `
    <label class="canvas-file-row">
      <input type="checkbox" data-file-id="${escapeHtml(file.id)}">
      <span class="canvas-file-icon">${escapeHtml((file.extension || "?").toUpperCase())}</span>
      <span class="canvas-file-meta">
        <strong>${escapeHtml(file.display_name || file.filename || "Untitled file")}</strong>
        <span>${escapeHtml(formatFileSize(file.size))}${file.updated_at ? ` · ${escapeHtml(formatCanvasDate(file.updated_at))}` : ""}</span>
      </span>
    </label>
  `).join("");
  updateCanvasFileActions();
}

function updateCanvasFileActions() {
  const count = canvasSelectedFiles.size;
  const hasSelection = count > 0;
  if (canvasPreviewFilesButton) canvasPreviewFilesButton.disabled = !hasSelection;
  if (canvasAskFilesButton) canvasAskFilesButton.disabled = !hasSelection;
  if (canvasGenerateFilesButton) canvasGenerateFilesButton.disabled = !hasSelection;
}

function updateCanvasPageActions() {
  const hasSelection = canvasSelectedPages.size > 0;
  if (canvasPreviewPagesButton) canvasPreviewPagesButton.disabled = !hasSelection;
  if (canvasSuggestVideosButton) canvasSuggestVideosButton.disabled = !hasSelection;
  if (canvasAskPagesButton) canvasAskPagesButton.disabled = !hasSelection;
}

async function previewSelectedCanvasFiles() {
  const fileIds = getSelectedCanvasFileIds();
  if (!fileIds.length) return;
  setCanvasFilesStatus("Extracting text from selected files...");
  canvasFilePreview.hidden = false;
  canvasFilePreview.innerHTML = `<p class="muted">Parsing selected files...</p>`;
  try {
    const payload = await postCanvasFiles("/canvas/files/preview", { file_ids: fileIds });
    canvasFilePreview.innerHTML = (payload.files || []).map(file => `
      <details class="canvas-file-preview-item" open>
        <summary>${escapeHtml(file.filename)} <span>${(file.character_count || 0).toLocaleString()} chars</span></summary>
        <pre>${escapeHtml(file.text || "No readable text found.")}</pre>
      </details>
    `).join("");
    setCanvasFilesStatus("");
  } catch (err) {
    setCanvasFilesStatus(err.message, true);
  }
}

async function askValAboutSelectedFiles() {
  const question = canvasChatInput.value.trim();
  if (!question) {
    setCanvasChatStatus("Type a question in the chat box first.", true);
    canvasChatInput.focus();
    return;
  }
  const fileIds = getSelectedCanvasFileIds();
  if (!fileIds.length) return;
  appendCanvasChatMessage("user", question);
  canvasChatInput.value = "";
  canvasAskFilesButton.disabled = true;
  setCanvasChatStatus("Asking VAL about selected files...");
  try {
    const payload = await postCanvasFiles("/canvas/files/chat", { question, file_ids: fileIds });
    appendCanvasChatMessage("assistant", payload.answer || "");
    setCanvasChatStatus("");
  } catch (err) {
    setCanvasChatStatus(err.message, true);
  } finally {
    updateCanvasFileActions();
  }
}

async function generateH5PFromSelectedFiles() {
  const fileIds = getSelectedCanvasFileIds();
  if (!fileIds.length) return;
  canvasGenerateFilesButton.disabled = true;
  setCanvasFilesStatus("Generating H5P from selected Canvas files...");
  try {
    const payload = await postCanvasFiles("/canvas/files/generate", {
      file_ids: fileIds,
      activity_type: canvasFileActivityType.value || "H5P.QuestionSet",
      content_mode: "shared",
      pass_percentage: 100,
      paragraph_count: parseInt(paraCountInput.value, 10) || 4,
    });
    renderResults(payload);
    recordGenerated((payload.results || []).length);
    activateWorkspace("h5p");
    window.history.pushState({}, "", "/h5p");
    goToStep(2);
    setCanvasFilesStatus("");
  } catch (err) {
    setCanvasFilesStatus(err.message, true);
  } finally {
    updateCanvasFileActions();
  }
}

async function previewSelectedCanvasPages() {
  const pageUrls = getSelectedCanvasPageUrls();
  if (!pageUrls.length || !canvasCurrentCourseId) return;
  setCanvasPagesStatus("Reading selected Canvas pages...");
  canvasPagePreview.hidden = false;
  canvasPagePreview.innerHTML = `<p class="muted">Loading page text...</p>`;
  try {
    const payload = await postCanvasFiles("/canvas/pages/preview", {
      course_id: canvasCurrentCourseId,
      course_name: canvasCurrentCourseName,
      page_urls: pageUrls,
    });
    canvasPagePreview.innerHTML = (payload.pages || []).map(page => `
      <details class="canvas-file-preview-item" open>
        <summary>${escapeHtml(page.title || page.url)} <span>${(page.character_count || 0).toLocaleString()} chars</span></summary>
        <pre>${escapeHtml(page.text || "No readable text found.")}</pre>
      </details>
    `).join("");
    setCanvasPagesStatus("");
  } catch (err) {
    setCanvasPagesStatus(err.message, true);
  }
}

async function suggestVideosForSelectedCanvasPages() {
  const pageUrls = getSelectedCanvasPageUrls();
  if (!pageUrls.length || !canvasCurrentCourseId) return;
  setCanvasPagesStatus("Reading page content and searching YouTube...");
  canvasPagePreview.hidden = false;
  canvasPagePreview.innerHTML = `<p class="muted">Finding video suggestions...</p>`;
  canvasSuggestVideosButton.disabled = true;
  try {
    const payload = await postCanvasFiles("/canvas/pages/youtube", {
      course_id: canvasCurrentCourseId,
      course_name: canvasCurrentCourseName,
      page_urls: pageUrls,
    });
    canvasPagePreview.innerHTML = renderCanvasVideoSuggestions(payload.pages || []);
    setCanvasPagesStatus("");
    gtag("event", "canvas_page_youtube_suggestions", { page_count: pageUrls.length });
  } catch (err) {
    setCanvasPagesStatus(err.message, true);
  } finally {
    updateCanvasPageActions();
  }
}

function renderCanvasVideoSuggestions(pages) {
  if (!pages.length) return `<p class="muted">No page content was available to search from.</p>`;
  return pages.map(page => `
    <section class="canvas-video-suggestion-group">
      <div class="canvas-video-suggestion-header">
        <strong>${escapeHtml(page.title || page.url || "Canvas page")}</strong>
        ${(page.search_queries || []).length
          ? `<span>${escapeHtml((page.search_queries || []).slice(0, 2).join(" | "))}</span>`
          : ""}
      </div>
      ${(page.embedded_youtube_links || []).length
        ? `<div class="canvas-embedded-links">
            <p class="muted">Embedded YouTube links found in Canvas:</p>
            ${(page.embedded_youtube_links || []).map(link => `
              <a href="${escapeHtml(link.watch_url || link.url)}" target="_blank" rel="noopener">${escapeHtml(link.watch_url || link.url)}</a>
            `).join("")}
          </div>`
        : ""}
      ${(page.videos || []).length
        ? `<div class="canvas-video-suggestions">
            ${(page.videos || []).map(video => renderCanvasVideoSuggestion(video)).join("")}
          </div>`
        : `<p class="muted">No YouTube suggestions were returned for this page.</p>`}
    </section>
  `).join("");
}

function renderCanvasVideoSuggestion(video) {
  return `
    <article class="canvas-video-suggestion">
      ${renderYouTubePreview(video)}
      <span class="youtube-video-meta">
        <strong>${escapeHtml(video.title || "Untitled video")}</strong>
        <span>${escapeHtml(formatYouTubeMeta(video))}</span>
        ${video.search_query ? `<span>Search: ${escapeHtml(video.search_query)}</span>` : ""}
        <span>${escapeHtml((video.description || "").slice(0, 180))}${(video.description || "").length > 180 ? "..." : ""}</span>
        ${renderYouTubeVideoActions(video)}
      </span>
    </article>
  `;
}

async function askValAboutSelectedPages() {
  const question = canvasChatInput.value.trim();
  if (!question) {
    setCanvasChatStatus("Type a question in the chat box first.", true);
    canvasChatInput.focus();
    return;
  }
  const pageUrls = getSelectedCanvasPageUrls();
  if (!pageUrls.length || !canvasCurrentCourseId) return;
  appendCanvasChatMessage("user", question);
  canvasChatInput.value = "";
  canvasAskPagesButton.disabled = true;
  setCanvasChatStatus("Asking VAL about selected pages...");
  try {
    const payload = await postCanvasFiles("/canvas/pages/chat", {
      course_id: canvasCurrentCourseId,
      course_name: canvasCurrentCourseName,
      page_urls: pageUrls,
      question,
    });
    appendCanvasChatMessage("assistant", payload.answer || "");
    setCanvasChatStatus("");
  } catch (err) {
    setCanvasChatStatus(err.message, true);
  } finally {
    updateCanvasPageActions();
  }
}

async function postCanvasFiles(path, body) {
  const response = await canvasFetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await readResponsePayload(response);
  if (!response.ok) throw new Error(extractErrorMessage(payload, "Canvas file action failed"));
  return payload;
}

function getSelectedCanvasFileIds() {
  return [...canvasSelectedFiles].map(id => parseInt(id, 10)).filter(Number.isFinite);
}

function getSelectedCanvasPageUrls() {
  return [...canvasSelectedPages].filter(Boolean);
}

function setCanvasFilesStatus(message, isError = false) {
  if (!canvasFilesStatus) return;
  canvasFilesStatus.textContent = message;
  canvasFilesStatus.style.color = isError ? "#b42318" : "";
}

function setCanvasPagesStatus(message, isError = false) {
  if (!canvasPagesStatus) return;
  canvasPagesStatus.textContent = message;
  canvasPagesStatus.style.color = isError ? "#b42318" : "";
}

function formatFileSize(bytes) {
  const n = Number(bytes);
  if (!Number.isFinite(n) || n <= 0) return "size unknown";
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${Math.round(n / 1024)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

function renderCanvasCourse(payload) {
  const course = payload.course || {};
  const summary = payload.summary || {};
  canvasCourseDetail.innerHTML = `
    <div class="canvas-course-title">
      <div>
        <p class="result-card-type">${escapeHtml(course.course_code || "Canvas course")}</p>
        <h3>${escapeHtml(course.name || "Untitled course")}</h3>
        <p class="muted">${escapeHtml(canvasCourseMeta(course))}</p>
      </div>
    </div>
    <div class="canvas-summary-grid">
      ${canvasStat("Students", course.total_students)}
      ${canvasStat("Modules", `${summary.published_modules || 0}/${summary.modules || 0}`)}
      ${canvasStat("Items", summary.module_items)}
      ${canvasStat("Assignments", `${summary.published_assignments || 0}/${summary.assignments || 0}`)}
      ${canvasStat("Sections", summary.sections)}
      ${canvasStat("Pages", summary.pages)}
    </div>
    ${renderCanvasList("Teachers", payload.teachers, t => t.display_name)}
    ${renderCanvasList("Sections", payload.sections, s => `${s.name}${s.total_students != null ? ` (${s.total_students})` : ""}`)}
    ${renderCanvasList("Modules", payload.modules, m => `${m.name}${m.items_count ? ` (${m.items_count} items)` : ""}${m.published ? "" : " [unpublished]"}`)}
    ${renderCanvasList("Assignments", payload.assignments, a => `${a.name}${a.points_possible != null ? ` - ${a.points_possible} pts` : ""}${a.due_at ? ` - due ${formatCanvasDate(a.due_at)}` : ""}`)}
    ${renderCanvasList("Pages", payload.pages, p => `${p.title}${p.published ? "" : " [unpublished]"}`)}
    ${renderCanvasList("Discussions", payload.discussions, d => `${d.title}${d.posted_at ? ` - ${formatCanvasDate(d.posted_at)}` : ""}`)}
    ${renderCanvasList("Quizzes", payload.quizzes, q => `${q.title}${q.due_at ? ` - due ${formatCanvasDate(q.due_at)}` : ""}`)}
  `;
}

function renderCanvasList(title, items, getText) {
  const list = Array.isArray(items) ? items : [];
  if (!list.length) return "";
  return `
    <details class="canvas-detail-group" open>
      <summary>${escapeHtml(title)} <span>${list.length}</span></summary>
      <ul>
        ${list.slice(0, 30).map(item => `<li>${escapeHtml(getText(item) || "")}</li>`).join("")}
      </ul>
    </details>
  `;
}

function canvasStat(label, value) {
  return `
    <div class="stat">
      <strong>${escapeHtml(value == null || value === "" ? "0" : value)}</strong>
      <span>${escapeHtml(label)}</span>
    </div>
  `;
}

function canvasCourseMeta(course) {
  const parts = [
    course.id ? `ID ${course.id}` : "",
    course.course_code || "",
    course.term?.name || "",
    course.workflow_state || "",
  ].filter(Boolean);
  return parts.join(" · ");
}

function extractCanvasCourseId(value) {
  const text = String(value || "").trim();
  const urlMatch = text.match(/\/courses\/(\d+)/i);
  if (urlMatch) return urlMatch[1];
  if (/^\d+$/.test(text)) return text;
  return "";
}

function formatCanvasDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function setCanvasStatus(message, isError = false) {
  canvasStatusEl.textContent = message;
  canvasStatusEl.style.color = isError ? "#b42318" : "";
}

function updateCanvasChatContext() {
  const count = canvasCourseContext.size;
  if (canvasChatContext) {
    canvasChatContext.textContent = `${count} course${count === 1 ? "" : "s"}`;
  }
  if (canvasChatButton) canvasChatButton.disabled = count === 0;
}

async function askCanvasChat() {
  const question = canvasChatInput.value.trim();
  if (!question) {
    setCanvasChatStatus("Ask a question first.", true);
    canvasChatInput.focus();
    return;
  }
  const courses = [...canvasCourseContext.values()].map(course => {
    const courseId = course.course?.id || course.id;
    if (canvasCurrentCourseId && String(courseId) === String(canvasCurrentCourseId) && canvasSelectedPages.size) {
      return { ...course, selected_page_urls: getSelectedCanvasPageUrls() };
    }
    return course;
  });
  if (!courses.length) {
    setCanvasChatStatus("Search for or read at least one Canvas course first.", true);
    return;
  }

  appendCanvasChatMessage("user", question);
  canvasChatInput.value = "";
  canvasChatButton.disabled = true;
  setCanvasChatStatus("Asking VAL...");
  try {
    const response = await canvasFetch("/canvas/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, courses }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "VAL chat failed"));
    appendCanvasChatMessage("assistant", payload.answer || "");
    setCanvasChatStatus("");
    gtag("event", "canvas_course_chat", { course_count: courses.length });
  } catch (err) {
    setCanvasChatStatus(err.message, true);
  } finally {
    updateCanvasChatContext();
  }
}

function appendCanvasChatMessage(role, text) {
  if (!canvasChatMessages) return;
  const empty = canvasChatMessages.querySelector(":scope > .muted");
  if (empty) empty.remove();
  const article = document.createElement("article");
  article.className = `canvas-chat-message ${role}`;
  article.innerHTML = `
    <strong>${role === "user" ? "You" : "VAL"}</strong>
    <p>${escapeHtml(text).replace(/\n/g, "<br>")}</p>
  `;
  canvasChatMessages.appendChild(article);
  canvasChatMessages.scrollTop = canvasChatMessages.scrollHeight;
}

function setCanvasChatStatus(message, isError = false) {
  if (!canvasChatStatus) return;
  canvasChatStatus.textContent = message;
  canvasChatStatus.style.color = isError ? "#b42318" : "";
}

// ── YouTube video search ───────────────────────────────────────────────
let youtubeReady = false;
const youtubeSelectedVideos = new Map();
let youtubeLatestResults = [];
let youtubeCanvasCourseContext = null;
const videoSlotState = new Map();
let youtubeContentChosen = false;
let youtubeAqfSuggestionRequestId = 0;

initYouTubeSearch();

function updateYoutubeStepIndicator(step) {
  youtubeStepPills.forEach((pill, i) => {
    if (!pill) return;
    const n = i + 1;
    pill.classList.toggle("active", n === step);
    pill.classList.toggle("done", n < step);
  });
  updateYouTubeFlowSlides(step);
}

function updateYouTubeFlowSlides(step = 1) {
  if (youtubeConnectSlide) youtubeConnectSlide.hidden = step !== 1;
  if (youtubeCanvasTools) youtubeCanvasTools.hidden = step !== 2;
  if (youtubeSlotPanel) youtubeSlotPanel.hidden = step !== 3;
  if (youtubeManualToggle) youtubeManualToggle.hidden = !canvasReady;
  if (!canvasReady && youtubeManualPanel) youtubeManualPanel.hidden = true;
}

function showYouTubeAccountMenu(open) {
  if (!youtubeAccountPopover || !youtubeAccountTrigger) return;
  youtubeAccountPopover.hidden = !open;
  youtubeAccountTrigger.setAttribute("aria-expanded", String(open));
}

function updateYouTubeAccountProfile(payload) {
  const name = payload?.user?.name || "Canvas user";
  const host = canvasSessionCredentials ? new URL(canvasSessionCredentials.baseUrl).hostname : "Connected";
  if (youtubeAccountMenu) youtubeAccountMenu.hidden = false;
  if (youtubeAccountName) youtubeAccountName.textContent = name;
  if (youtubeAccountHost) youtubeAccountHost.textContent = host;
  if (youtubeAccountAvatar) youtubeAccountAvatar.textContent = (name.trim()[0] || "C").toUpperCase();
}

function resetYouTubeAccountProfile() {
  if (youtubeAccountMenu) youtubeAccountMenu.hidden = true;
  showYouTubeAccountMenu(false);
}

function setYoutubeConnectSummary(text) {
  if (youtubeConnectSummaryText) youtubeConnectSummaryText.textContent = text;
  if (youtubeConnectSummary) youtubeConnectSummary.hidden = false;
  if (youtubeConnectForm) youtubeConnectForm.hidden = true;
}

function resetYoutubeConnectSummary() {
  if (youtubeConnectSummary) youtubeConnectSummary.hidden = true;
  if (youtubeConnectForm) youtubeConnectForm.hidden = false;
}

function setYoutubeContentSummary(text) {
  if (youtubeContentSummaryText) youtubeContentSummaryText.textContent = text;
  if (youtubeContentSummary) youtubeContentSummary.hidden = false;
}

function resetYoutubeContentSummary() {
  if (youtubeContentSummary) youtubeContentSummary.hidden = true;
}

function initYouTubeSearch() {
  if (!youtubeSearchButton || !youtubeSearchInput) return;
  youtubeSearchButton.addEventListener("click", runYouTubeSearch);
  youtubeSearchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      runYouTubeSearch();
    }
  });
  if (youtubeResults) {
    youtubeResults.addEventListener("change", (e) => {
      const input = e.target.closest('input[type="checkbox"][data-video-id]');
      if (!input) return;
      const video = youtubeLatestResults.find(item => item.id === input.dataset.videoId);
      if (input.checked && video) youtubeSelectedVideos.set(video.id, video);
      else youtubeSelectedVideos.delete(input.dataset.videoId);
      updateYouTubeSelection();
    });
    youtubeResults.addEventListener("click", (e) => {
      const previewButton = e.target.closest("[data-preview-youtube]");
      if (previewButton) {
        openYouTubePreviewModal(previewButton, e);
        return;
      }
      const copyButton = e.target.closest("[data-copy-youtube-embed]");
      if (copyButton) {
        handleYouTubeEmbedCopy(e);
        return;
      }
      const link = e.target.closest("a[data-video-link]");
      if (link) gtag("event", "youtube_video_opened", { video_id: link.dataset.videoLink });
    });
  }
  if (youtubeChatButton) youtubeChatButton.addEventListener("click", askValAboutSelectedVideos);
  if (youtubeCanvasCourseSearchButton) {
    youtubeCanvasCourseSearchButton.addEventListener("click", runYouTubeCanvasCourseSearch);
  }
  if (youtubeCanvasCourseSearch) {
    youtubeCanvasCourseSearch.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        runYouTubeCanvasCourseSearch();
      }
    });
  }
  if (youtubeCanvasCourseResults) {
    youtubeCanvasCourseResults.addEventListener("click", (e) => {
      const button = e.target.closest("button[data-youtube-canvas-course-id]");
      if (button) loadYouTubeCanvasCourse(button.dataset.youtubeCanvasCourseId);
    });
  }
  if (youtubeCanvasSuggestButton) {
    youtubeCanvasSuggestButton.addEventListener("click", suggestVideoSlotsFromCanvasContent);
  }
  if (youtubeSlotResults) {
    youtubeSlotResults.addEventListener("change", (e) => {
      const input = e.target.closest("input[data-slot-video-id]");
      if (input) handleVideoSlotSelectionChange(input);
    });
    youtubeSlotResults.addEventListener("click", (e) => {
      const scrollButton = e.target.closest("[data-slot-scroll]");
      if (scrollButton) {
        const carousel = scrollButton.closest(".video-slot-carousel-wrap")?.querySelector("[data-slot-carousel]");
        if (carousel) carousel.scrollBy({ left: Number(scrollButton.dataset.slotScroll) * carousel.clientWidth * 0.8, behavior: "smooth" });
        return;
      }
      const youtubePreviewButton = e.target.closest("[data-preview-youtube]");
      if (youtubePreviewButton) {
        openYouTubePreviewModal(youtubePreviewButton, e);
        return;
      }
      const toggleButton = e.target.closest("[data-slot-toggle]");
      if (toggleButton) {
        toggleVideoSlotCard(toggleButton.closest(".video-slot-card"));
        return;
      }
      const htmlToggleButton = e.target.closest("[data-slot-html-toggle]");
      if (htmlToggleButton) {
        toggleVideoSlotHtmlSource(htmlToggleButton.closest(".video-slot-card"));
        return;
      }
      const previewButton = e.target.closest("[data-preview-slot]");
      if (previewButton) {
        previewVideoSlot(previewButton.closest(".video-slot-card"));
        return;
      }
      const pushButton = e.target.closest("[data-push-slot]");
      if (pushButton) {
        pushVideoSlot(pushButton.closest(".video-slot-card"));
        return;
      }
      const revertButton = e.target.closest("[data-revert-slot]");
      if (revertButton) {
        revertVideoSlot(revertButton.closest(".video-slot-card"));
        return;
      }
      const refineButton = e.target.closest("[data-refine-slot-search]");
      if (refineButton) {
        refineVideoSlotSearch(refineButton.closest(".video-slot-card"));
        return;
      }
      const copyButton = e.target.closest("[data-copy-youtube-embed]");
      if (copyButton) handleYouTubeEmbedCopy(e);
    });
  }
  if (youtubeChatInput) {
    youtubeChatInput.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        askValAboutSelectedVideos();
      }
    });
  }
  if (canvasPagePreview) {
    canvasPagePreview.addEventListener("click", (e) => {
      const previewButton = e.target.closest("[data-preview-youtube]");
      if (previewButton) {
        openYouTubePreviewModal(previewButton, e);
        return;
      }
      const copyButton = e.target.closest("[data-copy-youtube-embed]");
      if (copyButton) handleYouTubeEmbedCopy(e);
    });
  }
  if (youtubePreviewClose) youtubePreviewClose.addEventListener("click", closeYouTubePreviewModal);
  if (youtubePreviewModal) {
    youtubePreviewModal.addEventListener("click", (e) => {
      if (e.target === youtubePreviewModal) closeYouTubePreviewModal();
    });
    youtubePreviewModal.addEventListener("close", resetYouTubePreviewModal);
  }
  if (youtubePreviewCopy) {
    youtubePreviewCopy.addEventListener("click", async () => {
      const videoId = youtubePreviewCopy.dataset.videoId || "";
      const title = youtubePreviewCopy.dataset.videoTitle || "YouTube video";
      if (!videoId) return;
      await copyYouTubeEmbedCode(videoId, title, youtubePreviewCopy);
    });
  }
  if (youtubeAccountTrigger) {
    youtubeAccountTrigger.addEventListener("click", (e) => {
      e.stopPropagation();
      showYouTubeAccountMenu(youtubeAccountPopover?.hidden !== false);
    });
  }
  if (youtubeAccountChange) {
    youtubeAccountChange.addEventListener("click", () => {
      showYouTubeAccountMenu(false);
      resetYoutubeConnectSummary();
      updateYoutubeStepIndicator(1);
    });
  }
  if (youtubeAccountDisconnect) {
    youtubeAccountDisconnect.addEventListener("click", () => {
      showYouTubeAccountMenu(false);
      disconnectCanvas();
    });
  }
  document.addEventListener("click", (e) => {
    if (youtubeAccountMenu && !youtubeAccountMenu.contains(e.target)) {
      showYouTubeAccountMenu(false);
    }
  });
  if (youtubeConnectChangeButton) {
    youtubeConnectChangeButton.addEventListener("click", () => {
      resetYoutubeConnectSummary();
      updateYoutubeStepIndicator(1);
    });
  }
  if (youtubeContentChangeButton) {
    youtubeContentChangeButton.addEventListener("click", () => {
      resetYoutubeContentSummary();
      updateYoutubeStepIndicator(2);
    });
  }
  if (youtubeManualToggle && youtubeManualPanel) {
    youtubeManualToggle.addEventListener("click", () => {
      const expanded = !youtubeManualPanel.hidden;
      youtubeManualPanel.hidden = expanded;
      youtubeManualToggle.setAttribute("aria-expanded", String(!expanded));
      youtubeManualToggle.textContent = expanded ? "Or search YouTube directly ›" : "Hide manual YouTube search ‹";
    });
  }
  updateYoutubeStepIndicator(canvasReady ? (youtubeContentChosen ? 3 : 2) : 1);
  refreshYouTubeStatus();
  updateYouTubeSelection();
}

async function refreshYouTubeStatus() {
  try {
    const response = await fetch(`${API_BASE}/youtube/status`);
    const payload = await readResponsePayload(response);
    youtubeReady = Boolean(payload.configured);
    youtubeStatusBadge.textContent = youtubeReady ? "Connected" : "Not configured";
    youtubeStatusBadge.classList.toggle("canvas-badge-ready", youtubeReady);
    youtubeStatusBadge.classList.toggle("canvas-badge-off", !youtubeReady);
    youtubeStatusEl.textContent = youtubeReady
      ? "Search public YouTube videos without exposing the API key."
      : "Set YOUTUBE_API_KEY on the server to enable YouTube search.";
    youtubeSearchButton.disabled = !youtubeReady;
    updateYouTubeCanvasSuggestButton();
  } catch {
    youtubeReady = false;
    youtubeStatusBadge.textContent = "Unavailable";
    youtubeStatusBadge.classList.add("canvas-badge-off");
    youtubeStatusEl.textContent = "YouTube status could not be checked.";
    youtubeSearchButton.disabled = true;
    updateYouTubeCanvasSuggestButton();
  }
}

async function runYouTubeCanvasCourseSearch() {
  if (!canvasReady) {
    setYouTubeCanvasSourceStatus("Connect your Canvas account first.", true);
    return;
  }
  const query = (youtubeCanvasCourseSearch?.value || "").trim();
  if (query.length < 2) {
    setYouTubeCanvasSourceStatus("Enter a course name, code, URL, or ID.", true);
    return;
  }
  const directCourseId = extractCanvasCourseId(query);
  if (directCourseId) {
    await loadYouTubeCanvasCourse(directCourseId);
    return;
  }

  youtubeCanvasCourseSearchButton.disabled = true;
  setYouTubeCanvasSourceStatus("Searching Canvas courses...");
  youtubeCanvasCourseResults.innerHTML = "";
  youtubeCanvasSourcePicker.hidden = true;
  try {
    const response = await canvasFetch(`/canvas/courses/search?q=${encodeURIComponent(query)}&limit=20`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Canvas search failed"));
    renderYouTubeCanvasCourseResults(payload.results || []);
    setYouTubeCanvasSourceStatus((payload.results || []).length ? "" : "No matching courses found.");
  } catch (err) {
    setYouTubeCanvasSourceStatus(err.message, true);
  } finally {
    youtubeCanvasCourseSearchButton.disabled = false;
  }
}

function renderYouTubeCanvasCourseResults(courses) {
  youtubeCanvasCourseResults.innerHTML = courses.map(course => `
    <article class="canvas-result">
      <div>
        <strong>${escapeHtml(course.name || "Untitled course")}</strong>
        <span>${escapeHtml(canvasCourseMeta(course))}</span>
      </div>
      <button type="button" class="secondary" data-youtube-canvas-course-id="${escapeHtml(course.id)}">Choose</button>
    </article>
  `).join("");
}

async function loadYouTubeCanvasCourse(courseId) {
  setYouTubeCanvasSourceStatus(`Reading Canvas course ${courseId}...`);
  youtubeCanvasSourcePicker.hidden = true;
  setYouTubeAqfSuggestion("");
  try {
    const response = await canvasFetch(`/canvas/courses/${encodeURIComponent(courseId)}`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Could not read Canvas course"));
    youtubeCanvasCourseContext = payload;
    renderYouTubeCanvasSources(payload);
    suggestYouTubeAqfLevel(payload);
    setYouTubeCanvasSourceStatus("");
  } catch (err) {
    setYouTubeCanvasSourceStatus(err.message, true);
  }
}

function renderYouTubeCanvasSources(payload) {
  const course = payload.course || {};
  const modules = (payload.modules || []).filter(module =>
    (module.items || []).some(item => item.type === "Page" && item.page_url)
  );
  const pages = payload.pages || [];
  youtubeCanvasCourseTitle.textContent = course.name || "Canvas course";
  youtubeCanvasModuleList.innerHTML = modules.length
    ? modules.map(module => {
        const pageCount = (module.items || []).filter(item => item.type === "Page" && item.page_url).length;
        return `<label class="canvas-source-option">
          <input type="checkbox" data-youtube-canvas-module-id="${escapeHtml(module.id)}">
          <span><strong>${escapeHtml(module.name || "Untitled module")}</strong><small>${pageCount} readable page${pageCount === 1 ? "" : "s"}</small></span>
        </label>`;
      }).join("")
    : `<p class="muted">No modules with readable pages.</p>`;
  youtubeCanvasPageList.innerHTML = pages.length
    ? pages.map(page => `<label class="canvas-source-option">
        <input type="checkbox" data-youtube-canvas-page-url="${escapeHtml(page.url || "")}">
        <span><strong>${escapeHtml(page.title || page.url || "Untitled page")}</strong><small>${page.published ? "Published" : "Unpublished"}</small></span>
      </label>`).join("")
    : `<p class="muted">No readable course pages.</p>`;
  youtubeCanvasCourseResults.innerHTML = "";
  youtubeCanvasSourcePicker.hidden = false;
  updateYouTubeCanvasSuggestButton();
}

function updateYouTubeCanvasSuggestButton() {
  if (!youtubeCanvasSuggestButton) return;
  youtubeCanvasSuggestButton.disabled = !youtubeReady || !canvasReady || !youtubeCanvasCourseContext;
  youtubeCanvasSuggestButton.title = !youtubeReady ? "YouTube search is not configured on this server" : "";
}

function currentAqfLevel() {
  const raw = youtubeAqfLevelSelect ? youtubeAqfLevelSelect.value : "";
  const parsed = parseInt(raw, 10);
  return Number.isFinite(parsed) ? parsed : null;
}

function aqfSearchModifier(level) {
  if (!level) return "";
  if (level <= 2) return "introductory basics";
  if (level <= 4) return "beginner practical";
  if (level <= 6) return "applied professional";
  if (level <= 8) return "advanced professional";
  return "expert research";
}

function searchQueryForAqf(query) {
  const level = currentAqfLevel();
  const modifier = aqfSearchModifier(level);
  if (!modifier) return query;
  const lower = query.toLowerCase();
  if (["introductory", "beginner", "basics", "applied", "professional", "advanced", "expert", "research"]
    .some(term => lower.includes(term))) {
    return query;
  }
  return `${query} ${modifier}`;
}

function setYouTubeAqfSuggestion(text) {
  if (youtubeAqfSuggestion) youtubeAqfSuggestion.textContent = text;
}

function setYouTubeAqfSuggestionRich(label, reason) {
  if (!youtubeAqfSuggestion) return;
  const reasonHtml = reason
    ? `<span class="youtube-aqf-reason" title="${escapeHtml(reason)}">${escapeHtml(reason)}</span>`
    : "";
  youtubeAqfSuggestion.innerHTML =
    `<strong>Suggested: ${escapeHtml(label)}</strong>${reasonHtml}`;
}

async function suggestYouTubeAqfLevel(payload) {
  if (!youtubeAqfLevelSelect || !payload?.course?.id) return;
  const requestId = ++youtubeAqfSuggestionRequestId;
  setYouTubeAqfSuggestion("Suggesting AQF level...");
  try {
    const response = await canvasFetch("/canvas/courses/aqf-suggestion", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: payload.course.id,
        course_name: payload.course.name || "",
      }),
    });
    const suggestion = await readResponsePayload(response);
    if (requestId !== youtubeAqfSuggestionRequestId) return;
    if (!response.ok) throw new Error(extractErrorMessage(suggestion, "AQF suggestion failed"));
    const level = parseInt(suggestion.aqf_level, 10);
    if (Number.isFinite(level) && level >= 1 && level <= 10 && !currentAqfLevel()) {
      youtubeAqfLevelSelect.value = String(level);
    }
    const label = suggestion.aqf_label || youtubeAqfLevelSelect.selectedOptions[0]?.textContent || "AQF level";
    setYouTubeAqfSuggestionRich(label, suggestion.reason || "");
  } catch (err) {
    if (requestId !== youtubeAqfSuggestionRequestId) return;
    setYouTubeAqfSuggestion("Choose an AQF level to tune the video search, or leave it unspecified.");
  }
}

async function suggestVideoSlotsFromCanvasContent() {
  if (!youtubeCanvasCourseContext || !youtubeReady || !canvasReady) return;
  const course = youtubeCanvasCourseContext.course || {};
  const moduleIds = [...youtubeCanvasModuleList.querySelectorAll("[data-youtube-canvas-module-id]:checked")]
    .map(input => parseInt(input.dataset.youtubeCanvasModuleId, 10))
    .filter(Number.isFinite);
  const pageUrls = [...youtubeCanvasPageList.querySelectorAll("[data-youtube-canvas-page-url]:checked")]
    .map(input => input.dataset.youtubeCanvasPageUrl)
    .filter(Boolean);

  let resolvedPageUrls = pageUrls;
  if (moduleIds.length) {
    const modulePageUrls = (youtubeCanvasCourseContext.modules || [])
      .filter(module => moduleIds.includes(module.id))
      .flatMap(module => (module.items || []).filter(item => item.type === "Page" && item.page_url).map(item => item.page_url));
    resolvedPageUrls = [...new Set([...resolvedPageUrls, ...modulePageUrls])];
  }
  if (!resolvedPageUrls.length) {
    resolvedPageUrls = (youtubeCanvasCourseContext.pages || []).map(page => page.url).filter(Boolean);
  }
  if (!resolvedPageUrls.length) {
    setYouTubeCanvasSourceStatus("No readable Canvas pages were found for that selection.", true);
    return;
  }

  youtubeCanvasSuggestButton.disabled = true;
  setYouTubeCanvasSourceStatus("Reading Canvas content and finding relevant videos...");
  try {
    const response = await canvasFetch("/canvas/pages/video-slots", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: course.id,
        course_name: course.name || "",
        page_urls: resolvedPageUrls.slice(0, 10),
        aqf_level: currentAqfLevel(),
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Video suggestions failed"));
    const pages = payload.pages || [];
    renderVideoSlots(course.id, pages);
    const slotCount = pages.reduce((sum, page) => sum + (page.slots || []).length, 0);
    setYouTubeCanvasSourceStatus(
      slotCount
        ? `${slotCount} video slot${slotCount === 1 ? "" : "s"} found across ${pages.length} Canvas page${pages.length === 1 ? "" : "s"}.`
        : "No video slots or suggestions were found for the selected Canvas content."
    );
    youtubeContentChosen = true;
    const aqfLabel = youtubeAqfLevelSelect?.selectedOptions[0]?.textContent || "";
    setYoutubeContentSummary(
      `Course: ${course.name || "Untitled"} · ${pages.length} page${pages.length === 1 ? "" : "s"}` +
      (aqfLabel && aqfLabel !== "Not specified" ? ` · ${aqfLabel}` : "")
    );
    updateYoutubeStepIndicator(3);
    if (youtubeSlotPanel) youtubeSlotPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    gtag("event", "youtube_canvas_video_slots", { page_count: pages.length, slot_count: slotCount });
  } catch (err) {
    setYouTubeCanvasSourceStatus(err.message, true);
  } finally {
    updateYouTubeCanvasSuggestButton();
  }
}

function renderVideoSlotCarouselItems(videos) {
  return videos.map(video => `
    <label class="video-slot-carousel-item">
      <input type="checkbox" data-slot-video-id="${escapeHtml(video.id)}">
      <span class="video-slot-carousel-check" aria-hidden="true"></span>
      ${renderYouTubeThumb(video)}
      <span class="video-slot-carousel-meta">
        <strong>${escapeHtml(video.title || "Untitled video")}</strong>
        <span class="video-slot-carousel-sub">${escapeHtml(formatYouTubeMeta(video))}</span>
      </span>
      <span class="video-slot-carousel-icons">
        <a href="${escapeHtml(video.url || "")}" target="_blank" rel="noopener" class="yt-icon-action" title="Open on YouTube" aria-label="Open on YouTube">↗</a>
        <button type="button" class="yt-icon-action youtube-embed-copy" data-copy-youtube-embed="${escapeHtml(video.id || "")}" data-video-title="${escapeHtml(video.title || "YouTube video")}" title="Copy embed code" aria-label="Copy embed code">&lt;/&gt;</button>
      </span>
    </label>
  `).join("") || `<p class="muted">No candidate videos were found for this slot.</p>`;
}

function renderVideoSlots(courseId, pages) {
  videoSlotState.clear();
  const cards = [];
  pages.forEach(page => {
    (page.slots || []).forEach(slot => {
      const key = `${page.url}::${slot.index}`;
      videoSlotState.set(key, {
        courseId,
        pageUrl: page.url,
        slotIndex: slot.index,
        videosById: new Map((slot.videos || []).map(video => [video.id, video])),
        selected: new Set(),
        preview: null,
        revertRevisionId: null,
        alreadyFilled: Boolean(slot.already_filled),
      });
      const description = slot.original_description_text || "";
      cards.push(`
        <article class="video-slot-card" data-slot-key="${escapeHtml(key)}">
          <button type="button" class="video-slot-header" data-slot-toggle aria-expanded="false">
            <span class="video-slot-header-text">
              <strong>${escapeHtml(page.title || page.url || "Canvas page")}</strong>
              ${slot.already_filled ? `<span class="video-slot-flag">Currently has a video · pick a replacement</span>` : ""}
            </span>
            <span class="video-slot-badge" data-slot-badge>Needs a video</span>
          </button>
          <div class="video-slot-body" data-slot-body hidden>
            ${description ? `<p class="video-slot-original">${escapeHtml(description)}</p>` : ""}

            <div class="video-slot-carousel-wrap">
              <button type="button" class="video-slot-arrow video-slot-arrow-prev" data-slot-scroll="-1" aria-label="Scroll left">&lsaquo;</button>
              <div class="video-slot-carousel" data-slot-carousel>
                ${renderVideoSlotCarouselItems(slot.videos || [])}
              </div>
              <button type="button" class="video-slot-arrow video-slot-arrow-next" data-slot-scroll="1" aria-label="Scroll right">&rsaquo;</button>
            </div>

            <div class="video-slot-refine">
              <input type="text" data-slot-context placeholder="Refine these results — add context (e.g. shorter, a specific brand, more about PPE)">
              <button type="button" class="secondary" data-refine-slot-search>Refine</button>
              <span class="status" data-slot-refine-status></span>
            </div>

            <div class="video-slot-actionbar">
              <button type="button" class="video-slot-primary" data-preview-slot disabled>Preview update</button>
              <button type="button" class="video-slot-primary" data-push-slot hidden>Push to Canvas</button>
              <span class="video-slot-done" data-slot-done hidden>Pushed ✓ <button type="button" class="video-slot-undo" data-revert-slot>Undo</button></span>
              <span class="status" data-slot-status></span>
            </div>

            <div class="video-slot-preview-wrap" data-slot-preview-wrap hidden>
              <iframe class="video-slot-preview-frame" data-slot-preview-frame sandbox="allow-scripts allow-same-origin allow-popups" title="Canvas update preview"></iframe>
            </div>

            <details class="video-slot-details">
              <summary>Details</summary>
              <p class="muted" data-slot-search-used>Search used: ${escapeHtml(slot.search_query || "(none)")}</p>
              <button type="button" class="video-slot-html-toggle" data-slot-html-toggle aria-expanded="false">View HTML source</button>
              <div class="video-slot-preview" data-slot-preview hidden></div>
            </details>
          </div>
        </article>
      `);
    });
  });
  youtubeSlotResults.innerHTML = cards.join("") || `<p class="muted">No video slots or suggestions were found for the selected Canvas content.</p>`;
  if (youtubeSlotPanel) youtubeSlotPanel.hidden = false;
}

function toggleVideoSlotCard(card) {
  if (!card) return;
  const toggleButton = card.querySelector("[data-slot-toggle]");
  const body = card.querySelector("[data-slot-body]");
  if (!toggleButton || !body) return;
  const expanded = toggleButton.getAttribute("aria-expanded") === "true";
  toggleButton.setAttribute("aria-expanded", String(!expanded));
  body.hidden = expanded;
}

function toggleVideoSlotHtmlSource(card) {
  if (!card) return;
  const toggleButton = card.querySelector("[data-slot-html-toggle]");
  const sourceEl = card.querySelector("[data-slot-preview]");
  if (!toggleButton || !sourceEl) return;
  const expanded = toggleButton.getAttribute("aria-expanded") === "true";
  toggleButton.setAttribute("aria-expanded", String(!expanded));
  toggleButton.textContent = expanded ? "View HTML source" : "Hide HTML source";
  sourceEl.hidden = expanded;
}

function setVideoSlotBadge(card, text) {
  const badge = card.querySelector("[data-slot-badge]");
  if (badge) badge.textContent = text;
}

function selectionBadgeText(state) {
  const n = state.selected.size;
  if (!n) return "Needs a video";
  return `${n} selected`;
}

// Reset the action bar to the pre-preview state (used on selection change, refine,
// and after a revert): only the "Preview update" primary is shown, enabled iff a
// video is selected. Push button, done state, and the rendered preview are hidden.
function resetVideoSlotActions(card, state) {
  state.preview = null;
  const previewButton = card.querySelector("[data-preview-slot]");
  const pushButton = card.querySelector("[data-push-slot]");
  const doneEl = card.querySelector("[data-slot-done]");
  const previewWrap = card.querySelector("[data-slot-preview-wrap]");
  const statusEl = card.querySelector("[data-slot-status]");
  if (previewButton) {
    previewButton.hidden = false;
    previewButton.disabled = state.selected.size === 0;
  }
  if (pushButton) pushButton.hidden = true;
  if (doneEl) doneEl.hidden = true;
  if (previewWrap) previewWrap.hidden = true;
  if (statusEl) {
    statusEl.textContent = "";
    statusEl.style.color = "";
  }
  setVideoSlotBadge(card, selectionBadgeText(state));
}

function handleVideoSlotSelectionChange(input) {
  const card = input.closest(".video-slot-card");
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state) return;
  const videoId = input.dataset.slotVideoId;
  if (input.checked) state.selected.add(videoId);
  else state.selected.delete(videoId);
  resetVideoSlotActions(card, state);
}

async function previewVideoSlot(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state) return;
  const videos = [...state.selected].map(id => state.videosById.get(id)).filter(Boolean);
  if (!videos.length) return;

  const previewButton = card.querySelector("[data-preview-slot]");
  const pushButton = card.querySelector("[data-push-slot]");
  const previewWrap = card.querySelector("[data-slot-preview-wrap]");
  const previewFrame = card.querySelector("[data-slot-preview-frame]");
  const previewSource = card.querySelector("[data-slot-preview]");
  const statusEl = card.querySelector("[data-slot-status]");
  previewButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Generating preview with VAL…";
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        slot_index: state.slotIndex,
        videos,
        aqf_level: currentAqfLevel(),
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Preview failed"));
    state.preview = { updatedBody: payload.updated_body, expectedUpdatedAt: payload.expected_updated_at };
    if (previewFrame) previewFrame.srcdoc = payload.preview_standalone_html || "";
    if (previewSource) previewSource.textContent = payload.preview_html || "";
    if (previewWrap) previewWrap.hidden = false;
    previewButton.hidden = true;
    if (pushButton) {
      pushButton.hidden = false;
      pushButton.disabled = false;
    }
    statusEl.textContent = "Preview ready — push when you're happy with it.";
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
    previewButton.disabled = false;
  }
}

async function pushVideoSlot(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state || !state.preview) return;
  const confirmed = window.confirm(
    `This overwrites the video section on the live Canvas page "${state.pageUrl}". You can undo it afterwards if needed. Continue?`
  );
  if (!confirmed) return;

  const pushButton = card.querySelector("[data-push-slot]");
  const doneEl = card.querySelector("[data-slot-done]");
  const revertButton = card.querySelector("[data-revert-slot]");
  const statusEl = card.querySelector("[data-slot-status]");
  pushButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Pushing update to Canvas…";
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        updated_body: state.preview.updatedBody,
        expected_updated_at: state.preview.expectedUpdatedAt,
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Push to Canvas failed"));
    state.preview = null;
    pushButton.hidden = true;
    statusEl.textContent = "";
    setVideoSlotBadge(card, "Pushed ✓");
    if (doneEl) {
      state.revertRevisionId = payload.revert_revision_id || null;
      if (revertButton) revertButton.hidden = !state.revertRevisionId;
      doneEl.hidden = false;
    }
    gtag("event", "youtube_slot_pushed_to_canvas", { page_url: state.pageUrl, slot_index: state.slotIndex });
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
    pushButton.disabled = false;
    setVideoSlotBadge(card, "Push failed");
  }
}

async function revertVideoSlot(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state || !state.revertRevisionId) return;
  const confirmed = window.confirm(
    `This restores the Canvas page "${state.pageUrl}" to the version before your last push. Continue?`
  );
  if (!confirmed) return;

  const revertButton = card.querySelector("[data-revert-slot]");
  const statusEl = card.querySelector("[data-slot-status]");
  if (revertButton) revertButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Reverting Canvas page…";
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/revert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        revision_id: state.revertRevisionId,
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Revert failed"));
    state.revertRevisionId = null;
    resetVideoSlotActions(card, state);
    statusEl.textContent = "Reverted to the previous version.";
    statusEl.style.color = "#12794b";
    gtag("event", "youtube_slot_reverted", { page_url: state.pageUrl, slot_index: state.slotIndex });
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
    if (revertButton) revertButton.disabled = false;
  }
}

async function refineVideoSlotSearch(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state) return;
  const contextInput = card.querySelector("[data-slot-context]");
  const additionalContext = (contextInput?.value || "").trim();
  const refineButton = card.querySelector("[data-refine-slot-search]");
  const statusEl = card.querySelector("[data-slot-refine-status]");
  const carousel = card.querySelector("[data-slot-carousel]");
  const searchUsedEl = card.querySelector("[data-slot-search-used]");

  refineButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Refining with VAL…";
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/refine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        slot_index: state.slotIndex,
        additional_context: additionalContext,
        aqf_level: currentAqfLevel(),
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Refine failed"));

    const videos = payload.videos || [];
    state.videosById = new Map(videos.map(video => [video.id, video]));
    state.selected.clear();
    if (carousel) {
      carousel.innerHTML = renderVideoSlotCarouselItems(videos);
      carousel.scrollLeft = 0;
    }
    if (searchUsedEl) searchUsedEl.textContent = `Search used: ${payload.search_query || "(none)"}`;
    resetVideoSlotActions(card, state);
    statusEl.textContent = videos.length ? "Updated the matches below." : "No matching videos found.";
    gtag("event", "youtube_slot_refined", { page_url: state.pageUrl, slot_index: state.slotIndex });
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
  } finally {
    refineButton.disabled = false;
  }
}

async function previewVideoSlot(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state) return;
  const videos = [...state.selected].map(id => state.videosById.get(id)).filter(Boolean);
  if (!videos.length) return;

  const previewButton = card.querySelector("[data-preview-slot]");
  const pushButton = card.querySelector("[data-push-slot]");
  const previewWrap = card.querySelector("[data-slot-preview-wrap]");
  const previewFrame = card.querySelector("[data-slot-preview-frame]");
  const previewSource = card.querySelector("[data-slot-preview]");
  const statusEl = card.querySelector("[data-slot-status]");
  previewButton.disabled = true;
  pushButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Generating preview with VAL...";
  setVideoSlotBadge(card, "Generating preview...");
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        slot_index: state.slotIndex,
        videos,
        aqf_level: currentAqfLevel(),
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Preview failed"));
    state.preview = { updatedBody: payload.updated_body, expectedUpdatedAt: payload.expected_updated_at };
    if (previewFrame) {
      previewFrame.srcdoc = payload.preview_standalone_html || "";
      previewFrame.hidden = false;
    }
    if (previewSource) previewSource.textContent = payload.preview_html || "";
    if (previewWrap) previewWrap.hidden = false;
    statusEl.textContent = "Preview ready. Review it above, then push to Canvas.";
    pushButton.disabled = false;
    setVideoSlotBadge(card, "Previewed");
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
    setVideoSlotBadge(card, "Preview failed");
  } finally {
    previewButton.disabled = false;
  }
}

async function pushVideoSlot(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state || !state.preview) return;
  const confirmed = window.confirm(
    `This overwrites the video section on the live Canvas page "${state.pageUrl}". You can revert it afterwards if needed. Continue?`
  );
  if (!confirmed) return;

  const pushButton = card.querySelector("[data-push-slot]");
  const previewButton = card.querySelector("[data-preview-slot]");
  const revertButton = card.querySelector("[data-revert-slot]");
  const statusEl = card.querySelector("[data-slot-status]");
  pushButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Pushing update to Canvas...";
  setVideoSlotBadge(card, "Pushing...");
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/apply", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        updated_body: state.preview.updatedBody,
        expected_updated_at: state.preview.expectedUpdatedAt,
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Push to Canvas failed"));
    statusEl.textContent = "Pushed to Canvas successfully.";
    statusEl.style.color = "#12794b";
    state.preview = null;
    previewButton.disabled = true;
    setVideoSlotBadge(card, "Pushed");
    if (payload.revert_revision_id && revertButton) {
      state.revertRevisionId = payload.revert_revision_id;
      revertButton.hidden = false;
      revertButton.disabled = false;
    }
    gtag("event", "youtube_slot_pushed_to_canvas", { page_url: state.pageUrl, slot_index: state.slotIndex });
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
    pushButton.disabled = false;
    setVideoSlotBadge(card, "Push failed");
  }
}

async function revertVideoSlot(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state || !state.revertRevisionId) return;
  const confirmed = window.confirm(
    `This restores the Canvas page "${state.pageUrl}" to the version before your last push. Continue?`
  );
  if (!confirmed) return;

  const revertButton = card.querySelector("[data-revert-slot]");
  const statusEl = card.querySelector("[data-slot-status]");
  revertButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Reverting Canvas page...";
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/revert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        revision_id: state.revertRevisionId,
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Revert failed"));
    statusEl.textContent = "Reverted to the previous version.";
    statusEl.style.color = "#12794b";
    state.revertRevisionId = null;
    revertButton.hidden = true;
    setVideoSlotBadge(card, "Reverted");
    gtag("event", "youtube_slot_reverted", { page_url: state.pageUrl, slot_index: state.slotIndex });
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
    revertButton.disabled = false;
  }
}

async function refineVideoSlotSearch(card) {
  if (!card) return;
  const state = videoSlotState.get(card.dataset.slotKey);
  if (!state) return;
  const textarea = card.querySelector("[data-slot-context]");
  const additionalContext = (textarea?.value || "").trim();
  const refineButton = card.querySelector("[data-refine-slot-search]");
  const statusEl = card.querySelector("[data-slot-refine-status]");
  const carousel = card.querySelector("[data-slot-carousel]");
  const searchUsedEl = card.querySelector("[data-slot-search-used]");

  refineButton.disabled = true;
  statusEl.style.color = "";
  statusEl.textContent = "Refining search with VAL...";
  try {
    const response = await canvasFetch("/canvas/pages/video-slots/refine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        course_id: state.courseId,
        page_url: state.pageUrl,
        slot_index: state.slotIndex,
        additional_context: additionalContext,
        aqf_level: currentAqfLevel(),
      }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Refine failed"));

    const videos = payload.videos || [];
    state.videosById = new Map(videos.map(video => [video.id, video]));
    state.selected.clear();
    state.preview = null;
    if (carousel) carousel.innerHTML = renderVideoSlotCarouselItems(videos);
    if (searchUsedEl) searchUsedEl.textContent = `Search used: ${payload.search_query || "(none)"}`;

    const previewWrap = card.querySelector("[data-slot-preview-wrap]");
    if (previewWrap) previewWrap.hidden = true;
    const pushButton = card.querySelector("[data-push-slot]");
    if (pushButton) pushButton.disabled = true;
    const previewButton = card.querySelector("[data-preview-slot]");
    if (previewButton) previewButton.disabled = true;

    setVideoSlotBadge(card, videos.length ? "Refined · pick a video" : "No results");
    statusEl.textContent = videos.length ? "Search refined." : "No matching videos found.";
    gtag("event", "youtube_slot_refined", { page_url: state.pageUrl, slot_index: state.slotIndex });
  } catch (err) {
    statusEl.textContent = err.message;
    statusEl.style.color = "#b42318";
  } finally {
    refineButton.disabled = false;
  }
}

function resetYouTubeCanvasSource() {
  youtubeCanvasCourseContext = null;
  if (youtubeCanvasCourseResults) youtubeCanvasCourseResults.innerHTML = "";
  if (youtubeCanvasSourcePicker) youtubeCanvasSourcePicker.hidden = true;
  if (youtubeCanvasModuleList) youtubeCanvasModuleList.innerHTML = "";
  if (youtubeCanvasPageList) youtubeCanvasPageList.innerHTML = "";
  if (youtubeCanvasSourceStatus) youtubeCanvasSourceStatus.textContent = "";
  videoSlotState.clear();
  if (youtubeSlotResults) youtubeSlotResults.innerHTML = "";
  if (youtubeSlotPanel) youtubeSlotPanel.hidden = true;
  youtubeContentChosen = false;
  resetYoutubeContentSummary();
  updateYoutubeStepIndicator(1);
  updateYouTubeCanvasSuggestButton();
}

function setYouTubeCanvasSourceStatus(message, isError = false) {
  if (!youtubeCanvasSourceStatus) return;
  youtubeCanvasSourceStatus.textContent = message;
  youtubeCanvasSourceStatus.style.color = isError ? "#b42318" : "";
}

async function runYouTubeSearch(queryOverride) {
  if (!youtubeReady) return;
  const query = (queryOverride ?? youtubeSearchInput.value).trim();
  if (query.length < 2) {
    setYouTubeStatus("Enter at least 2 characters to search.", true);
    return;
  }
  if (queryOverride !== undefined) youtubeSearchInput.value = query;

  youtubeSearchButton.disabled = true;
  setYouTubeStatus("Searching YouTube...");
  youtubeResults.innerHTML = "";
  try {
    const searchQuery = searchQueryForAqf(query);
    const response = await fetch(`${API_BASE}/youtube/search?q=${encodeURIComponent(searchQuery)}&limit=8`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "YouTube search failed"));
    youtubeLatestResults = payload.results || [];
    renderYouTubeResults(youtubeLatestResults);
    setYouTubeStatus(youtubeLatestResults.length ? "" : "No matching videos found.");
    gtag("event", "youtube_search", { result_count: youtubeLatestResults.length });
    if (queryOverride !== undefined) youtubeResults.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    setYouTubeStatus(err.message, true);
  } finally {
    youtubeSearchButton.disabled = !youtubeReady;
  }
}

function renderYouTubeResults(videos) {
  youtubeResults.innerHTML = videos.map(video => `
    <label class="youtube-result">
      <input type="checkbox" data-video-id="${escapeHtml(video.id)}" ${youtubeSelectedVideos.has(video.id) ? "checked" : ""}>
      ${renderYouTubePreview(video)}
      <span class="youtube-video-meta">
        <strong>${escapeHtml(video.title || "Untitled video")}</strong>
        <span>${escapeHtml(formatYouTubeMeta(video))}</span>
        ${video.canvas_source ? `<span>Suggested from: ${escapeHtml(video.canvas_source)}</span>` : ""}
        <span>${escapeHtml((video.description || "").slice(0, 220))}${(video.description || "").length > 220 ? "..." : ""}</span>
        ${renderYouTubeVideoActions(video, true)}
      </span>
    </label>
  `).join("");
}

function updateYouTubeSelection() {
  const count = youtubeSelectedVideos.size;
  if (youtubeSelectedCount) youtubeSelectedCount.textContent = `${count} video${count === 1 ? "" : "s"}`;
  if (youtubeChatButton) youtubeChatButton.disabled = count === 0;
}

async function askValAboutSelectedVideos() {
  const question = youtubeChatInput.value.trim();
  if (!question) {
    setYouTubeChatStatus("Ask a question first.", true);
    youtubeChatInput.focus();
    return;
  }
  const videos = [...youtubeSelectedVideos.values()];
  if (!videos.length) {
    setYouTubeChatStatus("Select at least one video first.", true);
    return;
  }

  appendYouTubeChatMessage("user", question);
  youtubeChatInput.value = "";
  youtubeChatButton.disabled = true;
  setYouTubeChatStatus("Asking VAL about selected videos...");
  try {
    const response = await fetch(`${API_BASE}/youtube/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, videos }),
    });
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "VAL video chat failed"));
    appendYouTubeChatMessage("assistant", payload.answer || "");
    if (payload.refined_query) {
      appendYouTubeChatMessage("assistant", `Refining search: "${payload.refined_query}"...`);
      await runYouTubeSearch(payload.refined_query);
    }
    setYouTubeChatStatus("");
    gtag("event", "youtube_video_chat", { video_count: videos.length, refined: Boolean(payload.refined_query) });
  } catch (err) {
    setYouTubeChatStatus(err.message, true);
  } finally {
    updateYouTubeSelection();
  }
}

function appendYouTubeChatMessage(role, text) {
  if (!youtubeChatMessages) return;
  const empty = youtubeChatMessages.querySelector(":scope > .muted");
  if (empty) empty.remove();
  const article = document.createElement("article");
  article.className = `canvas-chat-message ${role}`;
  article.innerHTML = `
    <strong>${role === "user" ? "You" : "VAL"}</strong>
    <p>${escapeHtml(text).replace(/\n/g, "<br>")}</p>
  `;
  youtubeChatMessages.appendChild(article);
  youtubeChatMessages.scrollTop = youtubeChatMessages.scrollHeight;
}

function setYouTubeStatus(message, isError = false) {
  if (!youtubeStatusEl) return;
  youtubeStatusEl.textContent = message;
  youtubeStatusEl.style.color = isError ? "#b42318" : "";
}

function setYouTubeChatStatus(message, isError = false) {
  if (!youtubeChatStatus) return;
  youtubeChatStatus.textContent = message;
  youtubeChatStatus.style.color = isError ? "#b42318" : "";
}

function formatYouTubeMeta(video) {
  const parts = [
    video.channel_title || "",
    video.published_at ? formatCanvasDate(video.published_at) : "",
    video.duration ? formatYouTubeDuration(video.duration) : "",
    video.view_count != null ? `${Number(video.view_count).toLocaleString()} views` : "",
  ].filter(Boolean);
  return parts.join(" · ");
}

function formatYouTubeDuration(value) {
  const match = String(value).match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!match) return value;
  const hours = parseInt(match[1] || "0", 10);
  const minutes = parseInt(match[2] || "0", 10);
  const seconds = parseInt(match[3] || "0", 10);
  const paddedSeconds = String(seconds).padStart(2, "0");
  if (hours) return `${hours}:${String(minutes).padStart(2, "0")}:${paddedSeconds}`;
  return `${minutes}:${paddedSeconds}`;
}

function renderYouTubeThumb(video) {
  const videoId = String(video.id || "").trim();
  const duration = video.duration ? formatYouTubeDuration(video.duration) : "";
  const thumb = video.thumbnail_url
    ? `<img class="yt-thumb-img" src="${escapeHtml(video.thumbnail_url)}" alt="" loading="lazy">`
    : `<span class="youtube-thumb-placeholder">YT</span>`;
  const playBadge = videoId
    ? `<button type="button" class="yt-thumb-play" ${youTubePreviewButtonAttrs(video)} aria-label="Play preview" title="Play preview">▶</button>`
    : "";
  return `
    <span class="yt-thumb">
      ${thumb}
      ${playBadge}
      ${duration ? `<span class="yt-thumb-duration">${escapeHtml(duration)}</span>` : ""}
    </span>
  `;
}

function renderYouTubePreview(video) {
  const videoId = String(video.id || "").trim();
  if (!videoId) {
    return `
      <span class="youtube-preview-wrap">
        <span class="youtube-thumb-placeholder">YT</span>
      </span>
    `;
  }
  return `
    <span class="youtube-preview-wrap">
      <iframe
        src="${escapeHtml(youtubeEmbedUrl(videoId))}"
        title="${escapeHtml(video.title || "YouTube video preview")}"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowfullscreen></iframe>
    </span>
  `;
}

function youTubePreviewButtonAttrs(video) {
  return [
    `data-preview-youtube="${escapeHtml(video.id || "")}"`,
    `data-video-title="${escapeHtml(video.title || "YouTube video")}"`,
    `data-video-channel="${escapeHtml(video.channel_title || "")}"`,
    `data-video-url="${escapeHtml(video.url || "")}"`,
  ].join(" ");
}

function renderYouTubeVideoActions(video, trackOpen = false) {
  const videoId = String(video.id || "").trim();
  const title = video.title || "YouTube video";
  return `
    <span class="youtube-video-actions">
      ${videoId
        ? `<button type="button" class="youtube-preview-button" ${youTubePreviewButtonAttrs(video)}>Preview</button>`
        : ""}
      <a href="${escapeHtml(video.url)}" target="_blank" rel="noopener" ${trackOpen ? `data-video-link="${escapeHtml(videoId)}"` : ""}>Open video</a>
      ${videoId
        ? `<button type="button" class="youtube-embed-copy" data-copy-youtube-embed="${escapeHtml(videoId)}" data-video-title="${escapeHtml(title)}" title="Copy embed code" aria-label="Copy embed code">&lt;/&gt;</button>`
        : ""}
    </span>
  `;
}

async function openYouTubePreviewModal(button, event) {
  if (!youtubePreviewModal || !button) return;
  event?.preventDefault?.();
  event?.stopPropagation?.();
  const videoId = button.dataset.previewYoutube || "";
  const title = button.dataset.videoTitle || "YouTube video";
  const channel = button.dataset.videoChannel || "";
  const url = button.dataset.videoUrl || `https://www.youtube.com/watch?v=${encodeURIComponent(videoId)}`;
  if (!videoId) return;

  if (youtubePreviewTitle) youtubePreviewTitle.textContent = title;
  if (youtubePreviewChannel) youtubePreviewChannel.textContent = channel || "YouTube preview";
  if (youtubePreviewFrame) {
    youtubePreviewFrame.src = `${youtubeEmbedUrl(videoId)}?autoplay=1&rel=0`;
    youtubePreviewFrame.title = title;
  }
  if (youtubePreviewOpen) youtubePreviewOpen.href = url;
  if (youtubePreviewCopy) {
    youtubePreviewCopy.dataset.videoId = videoId;
    youtubePreviewCopy.dataset.videoTitle = title;
    youtubePreviewCopy.textContent = "Copy embed code";
    youtubePreviewCopy.classList.remove("copied");
  }
  renderYouTubeTranscriptLoading();
  youtubePreviewModal.showModal();
  loadYouTubeTranscript(videoId);
}

function closeYouTubePreviewModal() {
  if (youtubePreviewModal?.open) youtubePreviewModal.close();
}

function resetYouTubePreviewModal() {
  if (youtubePreviewFrame) youtubePreviewFrame.src = "";
}

function renderYouTubeTranscriptLoading() {
  if (youtubePreviewTranscriptMeta) youtubePreviewTranscriptMeta.textContent = "";
  if (youtubePreviewTranscriptBody) {
    youtubePreviewTranscriptBody.innerHTML = `<p class="muted">Loading transcript...</p>`;
  }
}

async function loadYouTubeTranscript(videoId) {
  if (!youtubePreviewTranscriptBody) return;
  try {
    const response = await fetch(`${API_BASE}/youtube/videos/${encodeURIComponent(videoId)}/transcript`);
    const payload = await readResponsePayload(response);
    if (!response.ok) throw new Error(extractErrorMessage(payload, "Transcript could not be loaded"));
    renderYouTubeTranscript(payload);
  } catch (err) {
    if (youtubePreviewTranscriptMeta) youtubePreviewTranscriptMeta.textContent = "";
    youtubePreviewTranscriptBody.innerHTML = `<p class="muted">${escapeHtml(err.message || "Transcript could not be loaded.")}</p>`;
  }
}

function renderYouTubeTranscript(payload) {
  const segments = payload.segments || [];
  const source = payload.is_generated ? "auto-generated" : "captions";
  if (youtubePreviewTranscriptMeta) {
    youtubePreviewTranscriptMeta.textContent = payload.available
      ? `${payload.language || "Transcript"} · ${source}`
      : "";
  }
  if (!segments.length) {
    youtubePreviewTranscriptBody.innerHTML = `<p class="muted">${escapeHtml(payload.message || "No transcript was found for this video.")}</p>`;
    return;
  }
  youtubePreviewTranscriptBody.innerHTML = segments.map(segment => `
    <p class="youtube-transcript-line">
      <span>${escapeHtml(segment.time || "")}</span>
      <button type="button" data-youtube-seek="${escapeHtml(String(segment.start ?? 0))}">${escapeHtml(segment.text || "")}</button>
    </p>
  `).join("");
  youtubePreviewTranscriptBody.querySelectorAll("[data-youtube-seek]").forEach(button => {
    button.addEventListener("click", () => {
      const seconds = Math.max(0, parseFloat(button.dataset.youtubeSeek || "0") || 0);
      const videoId = youtubePreviewCopy?.dataset.videoId || payload.video_id || "";
      if (youtubePreviewFrame && videoId) {
        youtubePreviewFrame.src = `${youtubeEmbedUrl(videoId)}?autoplay=1&rel=0&start=${Math.floor(seconds)}`;
      }
    });
  });
}

async function copyYouTubeEmbedCode(videoId, title, feedbackButton) {
  const code = youtubeEmbedCode(videoId, title);
  try {
    await navigator.clipboard.writeText(code);
    showEmbedCopied(feedbackButton);
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = code;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
    showEmbedCopied(feedbackButton);
  }
}

async function handleYouTubeEmbedCopy(event) {
  const button = event.target.closest("[data-copy-youtube-embed]");
  if (!button) return;
  event.preventDefault();
  event.stopPropagation();
  const videoId = button.dataset.copyYoutubeEmbed || "";
  const title = button.dataset.videoTitle || "YouTube video";
  await copyYouTubeEmbedCode(videoId, title, button);
}

function showEmbedCopied(button) {
  const original = button.innerHTML;
  button.innerHTML = "OK";
  button.classList.add("copied");
  setTimeout(() => {
    button.innerHTML = original;
    button.classList.remove("copied");
  }, 1200);
}

function youtubeEmbedUrl(videoId) {
  return `https://www.youtube.com/embed/${encodeURIComponent(videoId)}`;
}

function youtubeEmbedCode(videoId, title) {
  return `<iframe width="560" height="315" src="${youtubeEmbedUrl(videoId)}" title="${escapeHtmlAttribute(title)}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`;
}

function escapeHtmlAttribute(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
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

if (window.location.pathname === "/feedback") {
  feedbackPanel.hidden = false;
  feedbackToggle.classList.add("active");
  feedbackText.focus();
}

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

// ── Footer AI indicator + active provider ─────────────────────────────
let activeAiProvider = "openai"; // fallback until /info resolves
(async () => {
  const el = document.getElementById("footer-ai");
  if (!el) return;
  try {
    const res  = await fetch(`${API_BASE}/info`);
    const data = await res.json();
    activeAiProvider = data.ai_provider || "openai";
    const labels = {
      val:       "VAL · OpenAI",
      openai:    "OpenAI",
      anthropic: "Claude (Anthropic)",
    };
    const label = labels[data.ai_provider] || data.ai_provider;
    el.innerHTML = `<span class="footer-ai-dot ${data.ai_provider}"></span>${label}`;
  } catch { /* silent */ }
})();
