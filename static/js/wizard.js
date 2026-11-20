// Wizard Multi-step Logic for ScriptForge AI / Scriptly AI

let wizardState = {
  currentStep: 2, // 2 = Requirements, 3 = AI Options, 5 = Review Outline, 6 = Writing Script
  title: "Why Small Ports Win",
  topic: "How regional ports compete with mega-hubs",
  description: "An explainer for supply chain beginners.",
  audience: "Students",
  platform: "youtube",
  duration: "8 min",
  tone: "Informative",
  language: "English",
  keyPoints: "",
  model: "claude-3-5-sonnet",
  creativity: "Balanced",
  length: "Medium",
  useKb: true,
  kbId: null,
  outline: [],
  generatedScriptId: null,
  isStreaming: false
};

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  const titleInput = document.getElementById("scriptTitle");
  if (titleInput) wizardState.title = titleInput.value;

  const kbSelect = document.getElementById("knowledgeBaseSelect");
  if (kbSelect && kbSelect.value) {
    wizardState.kbId = kbSelect.value;
  }
});

function goToStep(step) {
  // Save current step data
  readStepData();

  // Hide all panes
  document.getElementById("wizardStepRequirements").style.display = "none";
  document.getElementById("wizardStepAIOptions").style.display = "none";
  document.getElementById("wizardStepReviewOutline").style.display = "none";
  document.getElementById("wizardStepWriting").style.display = "none";

  const progressFill = document.getElementById("wizardProgressBar");
  const stepIndicator = document.getElementById("stepIndicatorLabel");
  const stepName = document.getElementById("stepNameLabel");

  wizardState.currentStep = step;

  if (step === 2) {
    document.getElementById("wizardStepRequirements").style.display = "block";
    progressFill.style.width = "25%";
    stepIndicator.textContent = "Step 2 of 8";
    stepName.textContent = "Requirements";
  } else if (step === 3) {
    document.getElementById("wizardStepAIOptions").style.display = "block";
    progressFill.style.width = "40%";
    stepIndicator.textContent = "Step 3 of 8";
    stepName.textContent = "AI options";
  } else if (step === 5) {
    document.getElementById("wizardStepReviewOutline").style.display = "block";
    progressFill.style.width = "65%";
    stepIndicator.textContent = "Step 5 of 8";
    stepName.textContent = "Review outline";
    renderOutlineBeats();
  } else if (step === 6) {
    document.getElementById("wizardStepWriting").style.display = "block";
    progressFill.style.width = "85%";
    stepIndicator.textContent = "Step 6 of 8";
    stepName.textContent = "Writing your script";
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function wizardPrevStep() {
  if (wizardState.currentStep === 2) {
    window.location.href = "/create/";
  } else if (wizardState.currentStep === 3) {
    goToStep(2);
  } else if (wizardState.currentStep === 5) {
    goToStep(3);
  } else if (wizardState.currentStep === 6) {
    goToStep(5);
  }
}

function readStepData() {
  const t = document.getElementById("scriptTitle");
  if (t) wizardState.title = t.value.trim() || "Untitled Script";

  const top = document.getElementById("scriptTopic");
  if (top) wizardState.topic = top.value.trim();

  const desc = document.getElementById("scriptDescription");
  if (desc) wizardState.description = desc.value.trim();

  const aud = document.getElementById("scriptAudience");
  if (aud) wizardState.audience = aud.value.trim() || "General Audience";

  const plat = document.getElementById("scriptPlatform");
  if (plat) wizardState.platform = plat.value;

  const dur = document.getElementById("scriptDuration");
  if (dur) wizardState.duration = dur.value.trim() || "8 min";

  const lang = document.getElementById("scriptLanguage");
  if (lang) wizardState.language = lang.value.trim() || "English";

  const kp = document.getElementById("scriptKeyPoints");
  if (kp) wizardState.keyPoints = kp.value.trim();
}

function selectTone(tone, btn) {
  wizardState.tone = tone;
  document.querySelectorAll(".tone-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}

function toggleMoreOptions() {
  const content = document.getElementById("moreOptionsContent");
  content.style.display = content.style.display === "none" ? "block" : "none";
}

function selectModel(model, element) {
  wizardState.model = model;
  document.querySelectorAll(".radio-card").forEach(c => c.classList.remove("selected"));
  element.classList.add("selected");
}

function updateCreativity(val) {
  let label = "Balanced";
  if (val < 30) label = "Focused & Precise";
  else if (val > 70) label = "Highly Creative";
  document.getElementById("creativityDisplay").textContent = label;
  wizardState.creativity = label;
}

function selectLength(len, btn) {
  wizardState.length = len;
  document.querySelectorAll(".length-btn").forEach(b => b.classList.remove("active-solid"));
  btn.classList.add("active-solid");
}

function toggleKbOptions(checked) {
  wizardState.useKb = checked;
  const selectGroup = document.getElementById("kbSelectGroup");
  if (selectGroup) {
    selectGroup.style.display = checked ? "block" : "none";
  }
}

function updateKbSubtitle(selectElem) {
  const subtitle = document.getElementById("kbSubtitle");
  if (subtitle && selectElem.options[selectElem.selectedIndex]) {
    subtitle.textContent = selectElem.options[selectElem.selectedIndex].text;
    wizardState.kbId = selectElem.value;
  }
}

// Outline Generation Request (Step 3 -> Step 5)
async function requestOutlineGeneration() {
  readStepData();
  const btn = document.getElementById("btnAnalyzeRequest");
  if (btn) btn.innerHTML = "Analyzing with Claude...";

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const response = await fetch("/api/wizard/outline/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        title: wizardState.title,
        topic: wizardState.topic,
        description: wizardState.description,
        audience: wizardState.audience,
        platform: wizardState.platform,
        duration: wizardState.duration,
        tone: wizardState.tone,
        more_options: wizardState.keyPoints,
        model: wizardState.model,
        knowledge_base_id: wizardState.useKb ? wizardState.kbId : null
      })
    });

    const data = await response.json();
    if (btn) btn.innerHTML = "Analyse request";

    if (data.status === "success") {
      wizardState.outline = data.outline;
      const sumText = document.getElementById("outlineSummaryText");
      if (sumText) sumText.textContent = data.summary;
      goToStep(5);
    } else {
      alert("Error generating outline: " + (data.message || "Unknown error"));
    }
  } catch (err) {
    if (btn) btn.innerHTML = "Analyse request";
    console.error("Outline error:", err);
    // Graceful fallback outline
    wizardState.outline = [
      { step: 1, title: "Hook", description: "Open with a surprising comparison" },
      { step: 2, title: "Introduction", description: "Why small ports matter" },
      { step: 3, title: "Main content", description: "Three regional ports, one lesson each" },
      { step: 4, title: "Engagement", description: "Ask viewers to pick a port" },
      { step: 5, title: "Conclusion", description: "Recap the three lessons" },
      { step: 6, title: "Call to action", description: "Subscribe for the next case study" }
    ];
    goToStep(5);
  }
}

function renderOutlineBeats() {
  const container = document.getElementById("outlineBeatsList");
  if (!container) return;
  container.innerHTML = "";

  wizardState.outline.forEach((item, index) => {
    const beatDiv = document.createElement("div");
    beatDiv.className = "outline-beat";
    beatDiv.innerHTML = `
      <div class="outline-num">${item.step || (index + 1)}</div>
      <div class="outline-content">
        <div class="outline-title" id="beatTitle_${index}">${item.title}</div>
        <div class="outline-desc" id="beatDesc_${index}">${item.description}</div>
      </div>
      <div class="outline-edit-btn" onclick="editBeat(${index})">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 20h9"></path>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
      </div>
    `;
    container.appendChild(beatDiv);
  });
}

function editBeat(index) {
  const currentTitle = wizardState.outline[index].title;
  const currentDesc = wizardState.outline[index].description;
  const newDesc = prompt(`Edit beat description for '${currentTitle}':`, currentDesc);
  if (newDesc !== null && newDesc.trim() !== "") {
    wizardState.outline[index].description = newDesc.trim();
    renderOutlineBeats();
  }
}

// Script Generation Execution (Step 5 -> Step 6)
async function startScriptWriting() {
  goToStep(6);
  wizardState.isStreaming = true;

  const hookElem = document.getElementById("liveHookText");
  const introElem = document.getElementById("liveIntroText");
  const cursor = document.getElementById("blinkingCursor");

  // Show model name
  const modelMap = {
    'claude-3-5-sonnet': 'Claude Sonnet',
    'claude-3-opus': 'Claude Opus',
    'claude-3-haiku': 'Claude Haiku'
  };
  const streamBadge = document.getElementById("streamingStatusLabel");
  if (streamBadge) streamBadge.textContent = `Streaming from ${modelMap[wizardState.model] || 'Claude'}`;

  // Start animated typing effect on UI
  const targetIntro = "Today we look at three regional ports that grew by doing less, not more.";
  let charIdx = 0;
  introElem.textContent = "";

  const typingInterval = setInterval(() => {
    if (!wizardState.isStreaming) {
      clearInterval(typingInterval);
      return;
    }
    if (charIdx < targetIntro.length) {
      introElem.textContent = targetIntro.substring(0, charIdx + 1);
      charIdx++;
    } else {
      clearInterval(typingInterval);
      if (cursor) cursor.style.display = "none";
    }
  }, 45);

  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const response = await fetch("/api/wizard/generate/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({
        title: wizardState.title,
        topic: wizardState.topic,
        description: wizardState.description,
        audience: wizardState.audience,
        platform: wizardState.platform,
        duration: wizardState.duration,
        tone: wizardState.tone,
        model: wizardState.model,
        outline: wizardState.outline,
        knowledge_base_id: wizardState.useKb ? wizardState.kbId : null
      })
    });

    const data = await response.json();
    if (data.status === "success") {
      wizardState.generatedScriptId = data.script_id;
      if (data.hook) hookElem.textContent = data.hook;
      if (data.introduction) introElem.textContent = data.introduction;
      clearInterval(typingInterval);
      if (cursor) cursor.style.display = "none";
      wizardState.isStreaming = false;
    } else {
      console.error("Generation error:", data.message);
    }
  } catch (err) {
    console.error("Generation network error:", err);
  }
}

function stopGeneration() {
  wizardState.isStreaming = false;
  const cursor = document.getElementById("blinkingCursor");
  if (cursor) cursor.style.display = "none";
  showToast("Script generation stopped.");
}

function openCompletedEditor() {
  if (wizardState.generatedScriptId) {
    window.location.href = `/editor/${wizardState.generatedScriptId}/`;
  } else {
    // If not yet persisted or fallback, redirect to first existing script or editor
    window.location.href = "/home/";
  }
}
