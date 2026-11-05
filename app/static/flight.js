/* Real pages load in the guest's browser; confirmations describe what the guest sees. */
(() => {
  "use strict";
  let token, socket, retryTimer, echoTimer, reconnects = 0, stopped = false;
  let renderedRevision = -1;
  const error = document.getElementById("error");
  const connection = document.getElementById("connection");
  const storageKey = `temporal-preflight:${location.host}`;

  function serviceUrl(port, path = "/") {
    const url = new URL(location.href);
    // Instruqt documents host-port[u|s]-participant.env.play.instruqt.com.
    if (/^workshop-5000[us]?-.+\.env\.play\.instruqt\.com$/.test(url.hostname)) {
      url.hostname = url.hostname.replace(/^workshop-5000[us]?-/, `workshop-${port}-`);
    } else if (["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)) {
      url.port = String(port);
    } else {
      throw new Error("This preview URL is not an Instruqt sandbox or local preview. Open the native Instruqt tabs.");
    }
    url.pathname = path;
    url.search = "";
    url.hash = "";
    return url;
  }

  function showError(message) { error.hidden = false; error.textContent = message; }

  async function api(path, body) {
    const response = await fetch(path, {
      method: body === undefined ? "GET" : "POST",
      headers: { "Content-Type": "application/json", ...(token ? {"X-Flight-Session": token} : {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(8000), cache: "no-store"
    });
    if (!response.ok) {
      const failure = new Error("The check could not save your answer. Check your connection and reload this page to try again.");
      failure.status = response.status;
      throw failure;
    }
    return path === "/api/report" ? response.text() : response.json();
  }

  const ORDER = ["ziggy", "editor", "terminal", "temporal"];
  const NAMES = {ziggy: "Browser image", editor: "Code editor", terminal: "Terminal", temporal: "Temporal UI"};
  let answers = {}, current = "intro", completed = false;
  const frames = {
    ziggy: () => serviceUrl(8090, "/ziggy"),
    editor: () => { const url = serviceUrl(8080); url.searchParams.set("folder", "/root/preflight"); return url; },
    temporal: () => serviceUrl(8233, "/namespaces/default/workflows")
  };

  function show(step) {
    current = step;
    document.querySelectorAll("[data-step]").forEach(section => { section.hidden = section.dataset.step !== step; });
    document.getElementById("progress").hidden = !ORDER.includes(step);
    ORDER.forEach((key, index) => {
      const dot = document.querySelector(`[data-dot="${key}"]`);
      dot.dataset.state = key === step ? "current" : answers[key] === "yes" ? "yes" : answers[key] === "issue" ? "issue" : "todo";
      if (key === step) dot.setAttribute("aria-current", "step"); else dot.removeAttribute("aria-current");
    });
    // Load each preview only when its step opens, so a failure belongs to that step.
    const frame = document.querySelector(`[data-step="${step}"] iframe`);
    if (frame && !frame.src && frames[step]) {
      try { frame.src = frames[step](); } catch (err) { showError(err.message); }
    }
    if (step === "done") renderDone();
    window.scrollTo(0, 0);
    const heading = document.querySelector(`[data-step="${step}"] h1`);
    if (heading) { heading.tabIndex = -1; heading.focus({preventScroll: true}); }
  }

  function renderDone() {
    const results = document.getElementById("results");
    results.replaceChildren(...ORDER.map(key => {
      const item = document.createElement("li");
      const value = answers[key];
      item.dataset.answer = value || "none";
      item.textContent = `${value === "yes" ? "✓" : value === "issue" ? "✗" : "–"} ${NAMES[key]}: ${value === "yes" ? "visible" : value === "issue" ? "not accessible" : "not answered"}`;
      return item;
    }));
    const pass = ORDER.every(key => answers[key] === "yes");
    document.getElementById("done-pass").hidden = !pass;
    document.getElementById("done-fail").hidden = pass;
    document.getElementById("done-title").textContent = pass ? "All four checks passed." : "Pre-flight finished with problems.";
  }

  function firstOpenStep() {
    const open = ORDER.find(key => !answers[key]);
    if (!open) return "done";
    return open === ORDER[0] ? "intro" : open;
  }

  function render(state) {
    if (state.revision < renderedRevision) return;
    renderedRevision = state.revision;
    answers = state.checks;
    completed = Boolean(state.completed_at);
    for (const [key, value] of Object.entries(state.checks)) {
      const section = document.querySelector(`[data-step="${key}"]`);
      section.dataset.answer = value;
      section.querySelector(".help").hidden = value !== "issue";
      section.querySelector("[data-next]").hidden = !value;
      for (const button of section.querySelectorAll("[data-answer]")) button.setAttribute("aria-pressed", String(button.dataset.answer === value));
    }
  }

  function connectionStatus(text, status) { connection.textContent = text; connection.dataset.status = status; }

  function connect() {
    clearTimeout(echoTimer);
    const url = new URL("/ws", location.href);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    connectionStatus("Checking live connection…", "waiting");
    socket = new WebSocket(url);
    const timeout = setTimeout(() => socket.close(), 6000);
    let watchdog;
    socket.onopen = () => socket.send(JSON.stringify({session: token}));
    socket.onmessage = event => {
      const state = JSON.parse(event.data);
      clearTimeout(echoTimer);
      clearTimeout(watchdog);
      watchdog = setTimeout(() => socket.close(), 12000);
      if (state.connection) {
        clearTimeout(timeout);
        reconnects = 0;
        connectionStatus("✓ Live connection works", "completed");
        render(state);
        // Keep the connection exercised while the guest looks at the other tabs.
        echoTimer = setTimeout(() => {
          if (socket.readyState === WebSocket.OPEN) socket.send(JSON.stringify({echo: state.nonce}));
        }, 3000);
      } else {
        socket.send(JSON.stringify({echo: state.nonce}));
      }
    };
    socket.onerror = () => socket.close();
    socket.onclose = () => {
      clearTimeout(timeout);
      clearTimeout(watchdog);
      clearTimeout(echoTimer);
      connectionStatus("! Live connection interrupted", "failed");
      if (!stopped && reconnects++ < 3) retryTimer = setTimeout(connect, 2000);
      else if (!stopped) showError("The live connection is blocked or unavailable. Your IT team may need to allow secure WebSockets to Instruqt. You can still view your readiness report below. Reload this page after the issue is resolved.");
    };
  }

  document.querySelectorAll(".answers button").forEach(button => button.addEventListener("click", async () => {
    const card = button.closest("[data-check]");
    const buttons = card.querySelectorAll("button");
    buttons.forEach(item => item.disabled = true);
    button.textContent = "Saving…";
    try {
      render(await api("/api/confirm", {check: card.dataset.check, value: button.dataset.answer}));
      document.getElementById("report-panel").hidden = true;
      error.hidden = true;
      // A yes moves straight on; a problem stays put so the guest can read the help.
      if (button.dataset.answer === "yes") goNext(card.dataset.check);
      else if (current === "done") renderDone();
    } catch (err) { showError(err.message); }
    finally { buttons.forEach(item => item.disabled = false); button.textContent = button.dataset.label; }
  }));

  function goNext(key) {
    const index = ORDER.indexOf(key);
    show(index === ORDER.length - 1 ? "done" : ORDER[index + 1]);
  }
  function goBack(step) {
    const index = ORDER.indexOf(step);
    show(step === "done" ? ORDER[ORDER.length - 1] : index === 0 ? "intro" : ORDER[index - 1]);
  }
  document.querySelectorAll("[data-next]").forEach(button => button.addEventListener("click", () => goNext(button.closest("[data-step]").dataset.step)));
  document.querySelectorAll("[data-back]").forEach(button => button.addEventListener("click", () => goBack(button.closest("[data-step]").dataset.step)));
  document.getElementById("start").addEventListener("click", () => show("ziggy"));
  document.getElementById("restart").addEventListener("click", () => show("intro"));

  document.getElementById("report-button").addEventListener("click", async () => {
    try {
      document.getElementById("report").value = await api("/api/report");
      document.getElementById("report-panel").hidden = false;
      document.getElementById("report").focus();
    } catch (err) { showError(err.message); }
  });
  document.getElementById("copy-report").addEventListener("click", async () => {
    const report = document.getElementById("report");
    try {
      await navigator.clipboard.writeText(report.value);
      document.getElementById("copy-status").textContent = "Copied.";
    } catch (_) {
      report.focus(); report.select();
      document.getElementById("copy-status").textContent = "Copy is restricted. Use your browser’s Copy command on the selected text.";
    }
  });
  window.addEventListener("pagehide", () => { stopped = true; clearTimeout(retryTimer); clearTimeout(echoTimer); socket?.close(); });

  async function start() {
    document.querySelectorAll(".answers button").forEach(button => button.dataset.label = button.textContent);
    try {
      // Exercise the second architecture-page port too; the guest sees one Ziggy step.
      const image = document.createElement("img");
      image.alt = ""; image.hidden = true;
      image.src = serviceUrl(8092, "/assets/brand/ziggy-peek.png");
      document.body.append(image);
    } catch (err) { showError(err.message); }
    try { token = sessionStorage.getItem(storageKey); } catch (_) { /* Storage is optional. */ }
    try {
      let state;
      try { state = await api("/api/session", {}); }
      catch (err) { if (!token || err.status !== 404) throw err; token = null; state = await api("/api/session", {}); }
      token = state.session;
      try { sessionStorage.setItem(storageKey, token); } catch (_) { /* Keep this flight in memory. */ }
      render(state);
      document.querySelectorAll(".answers button, #report-button, #start").forEach(button => button.disabled = false);
      show(firstOpenStep());
      connect();
    } catch (err) { showError(err.message); }

  }
  start();
})();
