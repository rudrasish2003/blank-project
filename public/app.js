const API = "http://localhost:8000";

async function fetchJSON(url, opts = {}) {
  const headers = { ...(opts.headers || {}), "X-Actor": "dashboard" };
  const r = await fetch(url, { ...opts, headers });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else e.setAttribute(k, v);
  });
  children.forEach((c) => e.appendChild(c));
  return e;
}

function speak(lines = []) {
  try {
    const utterance = new SpeechSynthesisUtterance(lines.join("\n"));
    utterance.lang = "en-IN";
    utterance.rate = 1.0;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
  } catch (e) {
    console.warn("Speech synthesis unavailable", e);
  }
}

function fleetCard(v, status) {
  const diag = status?.diagnosis || {};
  const analysis = status?.analysis || {};
  const pitch = status?.customer_pitch?.voice_script || [];
  const sched = status?.scheduling || {};
  const comp = diag?.top_component || "n/a";
  const risk = diag?.risk ?? 0.0;
  const priority = diag?.priority || "n/a";
  const eta = diag?.eta_days ?? "n/a";

  const suggestions = (sched?.slots || []).slice(0, 3).map((s) =>
    el("button", { class: "slot", "data-slot": s }, [document.createTextNode(new Date(s).toLocaleString())])
  );

  const card = el("div", { class: "card" }, [
    el("div", { class: "card-head" }, [
      el("h3", {}, [document.createTextNode(`${v.id} — ${v.owner} (${v.city})`)]),
      el("span", { class: `pill ${priority.toLowerCase()}` }, [document.createTextNode(priority)])
    ]),
    el("div", { class: "row" }, [
      el("div", { class: "col" }, [
        el("p", {}, [document.createTextNode(`Top risk: ${comp.replace("_", " ")} (risk ${risk})`)]),
        el("p", {}, [document.createTextNode(`ETA: ${eta} days`)]),
        el("p", {}, [document.createTextNode(`Anomaly score: ${analysis?.anomaly_score ?? 0}`)])
      ]),
      el("div", { class: "col" }, [
        el("p", { class: "subhead" }, [document.createTextNode("Voice Agent Script")]),
        el("ul", {}, pitch.map((line) => el("li", {}, [document.createTextNode(line)]))),
        el("button", { class: "speak" }, [document.createTextNode("Play Voice Script")])
      ])
    ]),
    el("div", { class: "row" }, [
      el("div", { class: "col" }, [
        el("p", { class: "subhead" }, [document.createTextNode("Suggested Slots")]),
        el("div", { class: "slots" }, suggestions)
      ])
    ])
  ]);

  // Voice TTS
  card.querySelector("button.speak").addEventListener("click", () => speak(pitch));

  // Booking handlers
  card.querySelectorAll("button.slot").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const slot = btn.getAttribute("data-slot");
      const center = sched?.center_id || "BLR_IND";
      try {
        const resp = await fetchJSON(`${API}/schedule/book`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ vehicle_id: v.id, center_id: center, slot })
        });
        alert(`Booked: ${resp.booking.center_name} @ ${new Date(resp.booking.slot).toLocaleString()}`);
        renderBookings();
      } catch (e) {
        alert(`Booking failed: ${e.message}`);
      }
    });
  });

  return card;
}

async function renderFleet() {
  const vehicles = await fetchJSON(`${API}/vehicles`);
  const status = await fetchJSON(`${API}/status`);
  const container = document.getElementById("fleet");
  container.innerHTML = "";
  vehicles.forEach((v) => {
    const s = status[v.id] || {};
    container.appendChild(fleetCard(v, s));
  });
}

async function simulateTelemetry() {
  const vehicles = ["VHC-01", "VHC-03", "VHC-07", "VHC-10"];
  for (const vid of vehicles) {
    const payload = {
      rpm: 2500,
      brake_pad_wear: vid === "VHC-07" || vid === "VHC-10" ? 0.6 : 0.35,
      battery_voltage: 12.4,
      coolant_temp: vid === "VHC-10" ? 105 : 92,
      vibration: 4.5,
      ambient_humidity: 70,
      mileage_km: 32000,
      duty_cycle_factor: 0.6
    };
    await fetchJSON(`${API}/telemetry/${vid}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }
  await renderFleet();
}

async function renderBookings() {
  const container = document.getElementById("bookings");
  const bookings = await fetchJSON(`${API}/bookings`);
  container.innerHTML = "";
  bookings.forEach((b) => {
    container.appendChild(
      el("div", { class: "item" }, [
        document.createTextNode(`${b.vehicle_id} → ${b.center_name} @ ${new Date(b.slot).toLocaleString()}`)
      ])
    );
  });
}

async function renderInsights() {
  const container = document.getElementById("insights");
  const data = await fetchJSON(`${API}/insights/manufacturing`);
  container.innerHTML = "";
  if (!data.ok) {
    container.appendChild(el("div", { class: "item warn" }, [document.createTextNode(`Insights blocked by UEBA`)]));
    return;
  }
  data.insights.forEach((i) => {
    container.appendChild(
      el("div", { class: "item" }, [
        el("strong", {}, [document.createTextNode(i.component)]),
        document.createTextNode(
          ` — predicted ${i.predicted_issue_count}, avg anomaly ${i.avg_anomaly_score}. Recommendation: ${i.recommendation}`
        )
      ])
    );
  });
}

async function renderUEBA() {
  const container = document.getElementById("ueba");
  const logs = await fetchJSON(`${API}/ueba/logs`);
  container.innerHTML = "";
  logs.slice(-25).reverse().forEach((l) => {
    container.appendChild(
      el("div", { class: `item ${l.ok ? "" : "warn"}` }, [
        document.createTextNode(`${new Date(l.ts).toLocaleString()} — [${l.subject}] ${l.agent} :: ${l.action} (${l.ok ? "ok" : "blocked"})`)
      ])
    );
  });
}

async function renderForecast() {
  const container = document.getElementById("forecast");
  const data = await fetchJSON(`${API}/forecast/centers`);
  container.innerHTML = "";
  if (!data.ok) {
    container.appendChild(el("div", { class: "item warn" }, [document.createTextNode(`Forecast blocked by UEBA`)]));
    return;
  }
  data.centers.forEach((c) => {
    container.appendChild(
      el("div", { class: "item" }, [
        el("strong", {}, [document.createTextNode(c.center_id)]),
        document.createTextNode(
          ` — near-term: ${c.near_term}, medium: ${c.medium_term}, low: ${c.low_term} (as of ${new Date(c.generated_at).toLocaleString()})`
        )
      ])
    );
  });
}

function wireEvents() {
  document.getElementById("refreshFleet").addEventListener("click", renderFleet);
  document.getElementById("simulate").addEventListener("click", simulateTelemetry);
  document.getElementById("refreshInsights").addEventListener("click", renderInsights);
  document.getElementById("refreshUEBA").addEventListener("click", renderUEBA);
  document.getElementById("refreshForecast").addEventListener("click", renderForecast);
}

async function init() {
  wireEvents();
  await renderFleet();
  await renderForecast();
  await renderBookings();
  await renderInsights();
  await renderUEBA();
}

init();