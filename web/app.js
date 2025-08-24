const API_BASE = (window.API_BASE || "https://YOUR-API-URL.onrender.com");

async function getTargets() {
  const r = await fetch(`${API_BASE}/targets`);
  return r.json();
}

async function getMetrics(url) {
  const r = await fetch(`${API_BASE}/metrics?url=${encodeURIComponent(url)}&minutes=60`);
  return r.json();
}

async function render() {
  const el = document.getElementById("list");
  el.innerHTML = "Loading...";
  try {
    const targets = await getTargets();
    if (!targets.length) {
      el.innerHTML = "No targets yet. (Use the Postgres version to store data.)";
      return;
    }
    const cards = await Promise.all(targets.map(async (t) => {
      const m = await getMetrics(t);
      const healthy = (m.last_status && m.last_status >= 200 && m.last_status < 400);
      return `
        <div class="card">
          <h3>${m.url}</h3>
          <div>Uptime: ${m.uptime_pct}%</div>
          <div>p95: ${m.p95_ms ? Math.round(m.p95_ms) + " ms" : "—"}</div>
          <div>Last: <span class="${healthy ? "ok" : "bad"}">${m.last_status ?? "—"}</span></div>
          <small>Updated: ${m.updatedAt ?? "—"}</small>
        </div>`;
    }));
    el.innerHTML = cards.join(""); 
  } catch (e) {
    el.innerHTML = "Failed to load.";
  }
}

render();
setInterval(render, 30000);
