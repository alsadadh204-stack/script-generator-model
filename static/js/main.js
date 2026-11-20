// Global ScriptForge AI / Scriptly AI JavaScript

function showToast(message, icon = "✓") {
  const toast = document.getElementById("appToast");
  const msgEl = document.getElementById("toastMessage");
  const iconEl = document.getElementById("toastIcon");

  if (!toast) return;

  if (msgEl) msgEl.textContent = message;
  if (iconEl) iconEl.textContent = icon;

  toast.classList.add("show");
  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 2600);
}

function copyToClipboard(text, customMessage = "Copied to clipboard!") {
  navigator.clipboard.writeText(text).then(() => {
    showToast(customMessage);
  }).catch(() => {
    showToast("Copy failed, please select manually.", "✕");
  });
}

// Window online / offline listeners
window.addEventListener("online", () => {
  const desktopBadge = document.getElementById("desktop-offline-badge");
  if (desktopBadge) desktopBadge.style.display = "none";
  showToast("Internet restored. Cloud sync active.");
});

window.addEventListener("offline", () => {
  const desktopBadge = document.getElementById("desktop-offline-badge");
  if (desktopBadge) desktopBadge.style.display = "flex";
  showToast("Offline. Local script drafting enabled.", "⚠");
});
