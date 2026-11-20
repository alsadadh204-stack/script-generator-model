// Script Editor Workspace Logic

let autoSaveTimer = null;
let currentExportFormat = 'pdf';
let selectedTextSnippet = "";
let currentSelectionTarget = null;

document.addEventListener("DOMContentLoaded", () => {
  updateStats();
  setupTextSelectionListener();
});

// Calculate words, chars, estimated speaking time (140 wpm)
function updateStats() {
  const hook = document.getElementById("textareaHook")?.value || "";
  const intro = document.getElementById("textareaIntro")?.value || "";
  const main = document.getElementById("textareaMain")?.value || "";
  const outro = document.getElementById("textareaOutro")?.value || "";

  const fullText = [hook, intro, main, outro].join(" ");
  const words = fullText.trim() ? fullText.trim().split(/\s+/).length : 0;
  const chars = fullText.length;
  const minutes = Math.max(1, Math.round(words / 140));

  const wordElem = document.getElementById("wordCountLabel");
  const charElem = document.getElementById("charCountLabel");
  const timeElem = document.getElementById("readingTimeLabel");

  if (wordElem) wordElem.textContent = `${words.toLocaleString()} words`;
  if (charElem) charElem.textContent = `${chars.toLocaleString()} chars`;
  if (timeElem) timeElem.textContent = `about ${minutes} min`;
}

function handleEditorInput() {
  updateStats();
  const status = document.getElementById("saveStatusIndicator");
  if (status) {
    status.textContent = "Saving…";
    status.style.color = "var(--status-warning)";
  }

  clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(() => {
    autoSaveScript();
  }, 1200);
}

async function autoSaveScript(createVersion = false) {
  const title = document.getElementById("scriptTitleInput")?.value.trim() || "Untitled Script";
  const hook = document.getElementById("textareaHook")?.value || "";
  const intro = document.getElementById("textareaIntro")?.value || "";
  const main = document.getElementById("textareaMain")?.value || "";
  const outro = document.getElementById("textareaOutro")?.value || "";

  const scriptIdMatch = window.location.pathname.match(/\/editor\/(\d+)/);
  if (!scriptIdMatch) return;
  const scriptId = scriptIdMatch[1];

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const res = await fetch(`/api/editor/${scriptId}/save/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        title,
        hook,
        introduction: intro,
        main_content: main,
        call_to_action: outro,
        create_new_version: createVersion
      })
    });

    const data = await res.json();
    if (data.status === "success") {
      const status = document.getElementById("saveStatusIndicator");
      const vDisplay = document.getElementById("scriptVersionDisplay");
      if (status) {
        status.textContent = "Saved";
        status.style.color = "var(--status-success)";
      }
      if (vDisplay && data.version) {
        vDisplay.textContent = data.version;
      }
    }
  } catch (err) {
    console.error("Autosave error:", err);
  }
}

// Section navigation
function scrollToSection(sectionId, btn) {
  document.querySelectorAll(".section-tab-btn").forEach(b => b.classList.remove("active-solid"));
  btn.classList.add("active-solid");
  const target = document.getElementById(sectionId);
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    const textarea = target.querySelector("textarea");
    if (textarea) textarea.focus();
  }
}

// Floating Contextual AI Selection Popup
function setupTextSelectionListener() {
  const container = document.getElementById("editorContentContainer");
  const popup = document.getElementById("floatingAiPopup");

  document.addEventListener("selectionchange", () => {
    const activeEl = document.activeElement;
    if (activeEl && activeEl.tagName === "TEXTAREA" && activeEl.classList.contains("editor-textarea")) {
      const start = activeEl.selectionStart;
      const end = activeEl.selectionEnd;
      if (start !== end && (end - start) > 2) {
        selectedTextSnippet = activeEl.value.substring(start, end);
        currentSelectionTarget = activeEl;

        const rect = activeEl.getBoundingClientRect();
        popup.style.display = "flex";
        popup.style.top = `${activeEl.offsetTop + 30}px`;
        popup.style.left = `20px`;
        return;
      }
    }
  });

  document.addEventListener("click", (e) => {
    if (!popup.contains(e.target) && !e.target.classList.contains("editor-textarea")) {
      popup.style.display = "none";
    }
  });
}

async function triggerContextAction(action) {
  if (!selectedTextSnippet || !currentSelectionTarget) {
    showToast("Please highlight text first.");
    return;
  }

  const popup = document.getElementById("floatingAiPopup");
  popup.style.display = "none";
  showToast(`Claude is running ${action}…`);

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const res = await fetch("/api/ai/context-action/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        action: action,
        text: selectedTextSnippet
      })
    });

    const data = await res.json();
    if (data.status === "success" && data.revised_text) {
      const textarea = currentSelectionTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const val = textarea.value;

      textarea.value = val.substring(0, start) + data.revised_text + val.substring(end);
      handleEditorInput();
      showToast(`${action} applied!`);
    }
  } catch (err) {
    showToast("Error processing request.");
  }
}

// Quick rewrite section
async function quickRewriteSection(sectionKey) {
  let targetArea = null;
  if (sectionKey === 'hook') targetArea = document.getElementById("textareaHook");
  else if (sectionKey === 'introduction') targetArea = document.getElementById("textareaIntro");
  else if (sectionKey === 'main_content') targetArea = document.getElementById("textareaMain");
  else if (sectionKey === 'call_to_action') targetArea = document.getElementById("textareaOutro");

  if (!targetArea) return;

  const original = targetArea.value;
  showToast(`Claude rewriting ${sectionKey.replace('_', ' ')}…`);

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const res = await fetch("/api/ai/context-action/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        action: "Improve",
        text: original
      })
    });
    const data = await res.json();
    if (data.status === "success" && data.revised_text) {
      targetArea.value = data.revised_text;
      handleEditorInput();
      showToast("Section updated!");
    }
  } catch (err) {
    showToast("Rewrite failed.");
  }
}

// AI Drawer (Page 12)
function openAiDrawer(initialPrompt = null) {
  document.getElementById("aiDrawerOverlay").style.display = "block";
  document.getElementById("aiAssistantDrawer").classList.add("active");
  if (initialPrompt) {
    document.getElementById("aiChatInput").value = initialPrompt;
    sendAiMessage();
  }
}

function closeAiDrawer() {
  document.getElementById("aiDrawerOverlay").style.display = "none";
  document.getElementById("aiAssistantDrawer").classList.remove("active");
}

function sendQuickPrompt(promptText) {
  document.getElementById("aiChatInput").value = promptText;
  sendAiMessage();
}

async function sendAiMessage() {
  const input = document.getElementById("aiChatInput");
  const message = input.value.trim();
  if (!message) return;

  input.value = "";
  const thread = document.getElementById("aiChatThread");

  // Append user bubble
  const userBubble = document.createElement("div");
  userBubble.className = "chat-bubble-user";
  userBubble.textContent = message;
  thread.appendChild(userBubble);

  // Show typing bubble
  const typingBubble = document.createElement("div");
  typingBubble.className = "chat-bubble-ai";
  typingBubble.id = "tempTypingBubble";
  typingBubble.innerHTML = `<span style="color: var(--text-secondary); font-style: italic;">Claude is writing…</span>`;
  thread.appendChild(typingBubble);
  thread.scrollTop = thread.scrollHeight;

  const scriptIdMatch = window.location.pathname.match(/\/editor\/(\d+)/);
  const scriptId = scriptIdMatch ? scriptIdMatch[1] : 1;

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const res = await fetch("/api/ai/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        script_id: scriptId,
        message: message,
        context_section: 'hook'
      })
    });

    const data = await res.json();
    typingBubble.remove();

    if (data.status === "success") {
      const aiBubble = document.createElement("div");
      aiBubble.className = "chat-bubble-ai";

      let actionsHtml = "";
      if (data.suggested_snippet) {
        actionsHtml = `
          <div class="chat-ai-actions">
            <button type="button" class="btn-pill-sm active" style="padding: 6px 12px; font-size: 12px;" onclick="applyAiSuggestion('${escapeQuotes(data.suggested_snippet)}', 'replace_hook')">Replace hook</button>
            <button type="button" class="btn-pill-sm" style="padding: 6px 12px; font-size: 12px;" onclick="applyAiSuggestion('${escapeQuotes(data.suggested_snippet)}', 'insert_below')">Insert below</button>
          </div>
        `;
      }

      aiBubble.innerHTML = `<div>${data.reply}</div>${actionsHtml}`;
      thread.appendChild(aiBubble);
      thread.scrollTop = thread.scrollHeight;
    }
  } catch (err) {
    typingBubble.innerHTML = `<span style="color: var(--status-error);">Error reaching assistant.</span>`;
  }
}

function escapeQuotes(str) {
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function applyAiSuggestion(snippet, action) {
  const hookArea = document.getElementById("textareaHook");
  if (!hookArea) return;

  if (action === 'replace_hook') {
    hookArea.value = snippet;
    showToast("Hook replaced!");
  } else {
    hookArea.value += "\n\n" + snippet;
    showToast("Snippet inserted below!");
  }

  handleEditorInput();
  closeAiDrawer();
}

// Export Modal (Page 13)
function openExportModal() {
  document.getElementById("exportModalOverlay").style.display = "block";
  document.getElementById("exportModalSheet").style.display = "block";
}

function closeExportModal() {
  document.getElementById("exportModalOverlay").style.display = "none";
  document.getElementById("exportModalSheet").style.display = "none";
}

function selectExportFormat(format, card) {
  currentExportFormat = format;
  document.querySelectorAll(".export-option-card").forEach(c => c.classList.remove("selected"));
  card.classList.add("selected");

  const btn = document.getElementById("btnExecuteExport");
  btn.textContent = `Export as ${format.toUpperCase()}`;
}

function triggerScriptDownload(scriptId) {
  closeExportModal();
  showToast(`Building ${currentExportFormat.toUpperCase()}…`);
  window.location.href = `/editor/${scriptId}/export/${currentExportFormat}/`;
}

// Favorite Toggle
async function toggleScriptFav(scriptId) {
  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const res = await fetch(`/api/editor/${scriptId}/favorite/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      }
    });
    const data = await res.json();
    if (data.status === "success") {
      const btn = document.getElementById("btnToggleFav");
      const svg = btn.querySelector("svg");
      if (data.is_favorite) {
        svg.setAttribute("fill", "#FF7A3D");
        svg.setAttribute("stroke", "#FF7A3D");
        showToast("Added to favorites!");
      } else {
        svg.setAttribute("fill", "none");
        svg.setAttribute("stroke", "currentColor");
        showToast("Removed from favorites.");
      }
    }
  } catch (err) {
    console.error(err);
  }
}

// Version History Modal
async function openVersionHistoryModal(scriptId) {
  const overlay = document.getElementById("versionModalOverlay");
  const sheet = document.getElementById("versionModalSheet");
  const list = document.getElementById("versionHistoryList");

  overlay.style.display = "block";
  sheet.style.display = "block";
  list.innerHTML = `<div style="color: var(--text-secondary); text-align: center; padding: 20px;">Loading versions…</div>`;

  try {
    const res = await fetch(`/api/editor/${scriptId}/versions/`);
    const data = await res.json();
    if (data.status === "success" && data.versions.length) {
      list.innerHTML = "";
      data.versions.forEach(v => {
        const item = document.createElement("div");
        item.className = "card-surface";
        item.style.marginBottom = "8px";
        item.style.cursor = "pointer";
        item.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-weight: 600; color: var(--text-primary);">Version ${v.version}</div>
            <div style="font-size: 12px; color: var(--text-muted);">${v.created_at}</div>
          </div>
          <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px;">${v.note}</div>
        `;
        list.appendChild(item);
      });
    } else {
      list.innerHTML = `<div style="color: var(--text-secondary); text-align: center; padding: 20px;">No previous versions recorded.</div>`;
    }
  } catch (err) {
    list.innerHTML = `<div style="color: var(--status-error); text-align: center; padding: 20px;">Error loading versions.</div>`;
  }
}

function closeVersionModal() {
  document.getElementById("versionModalOverlay").style.display = "none";
  document.getElementById("versionModalSheet").style.display = "none";
}

function formatText(command) {
  showToast(`Formatting: ${command}`);
}

function openFindPrompt() {
  const term = prompt("Find text in script:");
  if (term) {
    window.find(term);
  }
}
