/* Decorative motion never changes readiness. Each page also works without it. */
(() => {
  "use strict";
  const preference = matchMedia("(prefers-reduced-motion: reduce)");
  const button = document.getElementById("motion-toggle");
  const canvas = document.getElementById("stars");
  let paused = false;

  function update() {
    const still = paused || preference.matches;
    document.documentElement.dataset.motionPaused = String(still);
    window.Starfield?.setPaused(still);
    if (button) {
      button.disabled = preference.matches;
      button.textContent = preference.matches ? "Reduced motion enabled" : paused ? "Resume animation" : "Pause animation";
      button.setAttribute("aria-pressed", String(still));
    }
    const frame = document.getElementById("ziggy-frame");
    if (frame?.src) frame.contentWindow?.postMessage({type: "preflight-motion", paused: still}, new URL(frame.src).origin);
  }

  button?.addEventListener("click", () => { paused = !paused; update(); });
  preference.addEventListener("change", update);
  // Launchpad can pause its cross-origin Ziggy preview as well as its own stars.
  window.addEventListener("message", event => {
    if (window.parent !== window && event.source === window.parent && event.data?.type === "preflight-motion" && typeof event.data.paused === "boolean") {
      paused = event.data.paused;
      update();
    }
  });
  document.getElementById("ziggy-frame")?.addEventListener("load", update);
  update();
  try { if (canvas) window.Starfield?.start(canvas); } catch (_) { /* Keep the visual check usable without canvas. */ }
})();
