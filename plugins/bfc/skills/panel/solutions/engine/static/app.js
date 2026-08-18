/*
  Interfejs panelu - czysty JS, zero zależności i zero kroku budowania.
  Jedna funkcja renderuje jedną sekcję, a wszystkie dane pochodzą z /api/data.
*/

const state = { data: null, openKey: null, timerMode: null, timerTick: null, pomodoroFired: false, breakUntil: null, calCursor: null, calSelected: null, pomoMinutes: null };

/* ── narzędzia ─────────────────────────────────────────────────────────── */
const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (html !== undefined) node.innerHTML = html;
  return node;
};
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
const num = (n) => Number(n || 0).toLocaleString("pl-PL");
const zl = (n) => `${num(Math.round(n || 0))} zł`;
const short = (n) => (Math.abs(n) >= 1000 ? `${Math.round(n / 1000)} tys.` : num(n));

/** Polska odmiana liczebnika: 1 klient, 2 klientów, 5 klientów. */
function plural(n, one, few, many) {
  const v = Math.abs(Math.round(n));
  if (v === 1) return one;
  if (v % 10 >= 2 && v % 10 <= 4 && !(v % 100 >= 12 && v % 100 <= 14)) return few;
  return many;
}

/** Ucina tekst na granicy słowa, żeby nie zostawiać urwanych nawiasów. */
function clip(text, limit) {
  const s = String(text || "");
  if (s.length <= limit) return s;
  const cut = s.slice(0, limit);
  const space = cut.lastIndexOf(" ");
  return `${(space > limit * 0.6 ? cut.slice(0, space) : cut).replace(/[\s,;(-]+$/, "")}…`;
}

const SEV_LABEL = { ok: "ok", info: "info", warn: "uwaga", alarm: "pilne" };

function timeAgo(iso) {
  if (!iso) return "—";
  const diff = (Date.now() - new Date(iso).getTime()) / 86400000;
  if (diff < 0.04) return "przed chwilą";
  if (diff < 1) return `${Math.round(diff * 24)} godz. temu`;
  if (diff < 2) return "wczoraj";
  return `${Math.round(diff)} dni temu`;
}

function toast(message, kind = "") {
  const node = $("#toast");
  node.textContent = message;
  node.className = `toast ${kind}`;
  node.hidden = false;
  clearTimeout(node._t);
  node._t = setTimeout(() => (node.hidden = true), 3200);
}

async function api(path, body) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `Błąd ${res.status}`);
  }
  return res.json();
}

const blockData = (name) => {
  const block = state.data?.blocks?.[name];
  return block && block.ok ? block.data : null;
};

/* ── zakładki ──────────────────────────────────────────────────────────── */
function initTabs() {
  $("#tabs").addEventListener("click", (event) => {
    const tab = event.target.closest(".tab");
    if (tab) selectTab(tab.dataset.tab);
  });
  window.addEventListener("hashchange", () => selectTab(location.hash.slice(1) || "dzis"));
  selectTab(location.hash.slice(1) || "dzis");
}

function selectTab(name) {
  const tab = document.querySelector(`.tab[data-tab="${name}"]`);
  if (!tab) return;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("is-active", t === tab));
  document.querySelectorAll(".panel").forEach((p) =>
    p.classList.toggle("is-active", p.id === `panel-${name}`)
  );
  if (location.hash.slice(1) !== name) history.replaceState(null, "", `#${name}`);
  if (name === "czat") initChat().then(() => setTimeout(() => $("#chat-text")?.focus(), 80));
  if (name === "terminal") initTerminal().then(() => setTimeout(fitTerminal, 60));
}

/* ── ładowanie ─────────────────────────────────────────────────────────── */
async function load(force = false) {
  try {
    state.data = await api(`/api/data${force ? "?force=1" : ""}`);
    renderAll();
  } catch (error) {
    toast(`Nie udało się pobrać danych: ${error.message}`, "alarm");
  }
}

function renderAll() {
  const d = state.data;
  $("#owner-name").textContent = d.owner?.name ? `@${d.owner.handle || d.owner.name}` : "";
  $("#generated-at").textContent = `dane z ${new Date(d.generated_at).toLocaleTimeString("pl-PL", {
    hour: "2-digit",
    minute: "2-digit",
  })}`;

  applyTabVisibility();
  renderHealthStrip();
  renderToday();
  renderSignals();
  renderKpis();
  renderStagebar();
  renderKanban();
  renderKlienci();
  renderBiznes();
  renderTodo();
  renderKasa();
  renderToolkit();
  renderContent();
  renderStatystyki();
  renderArchiwum();
  renderSamouczek();
  renderConnectors();
  renderTopbar();
  renderTime();
  refreshCalendars();
}

/* Zakładki opcjonalne pokazujemy tylko, gdy ich źródło jest włączone w configu -
   pusta zakładka uczy, że panel jest do oglądania, nie do używania. Dziś, To-do,
   Kalendarz, Czat i Terminal mają własną logikę i zostają. */
const _TAB_BLOCK = {
  pozyskiwanie: "pozyskiwanie", klienci: "klienci", biznes: "biznes",
  kasa: "kasa", content: "tresci", zasiegi: "statystyki", archiwum: "outputy",
  czas: "timer", connectors: "connectors", toolkit: "toolkit",
};
function applyTabVisibility() {
  const blocks = state.data?.blocks || {};
  let activeHidden = false;
  document.querySelectorAll(".tab").forEach((tab) => {
    const src = _TAB_BLOCK[tab.dataset.tab];
    if (!src) return;
    const hide = !(src in blocks);
    tab.hidden = hide;
    if (hide && tab.classList.contains("is-active")) activeHidden = true;
  });
  if (activeHidden) selectTab("dzis");
}

/* ── pasek stanu ───────────────────────────────────────────────────────── */
function renderHealthStrip() {
  const health = state.data.health;
  const bad = health.filter((h) => h.severity === "alarm");
  const warn = health.filter((h) => h.severity === "warn");

  const dot = $("#health-dot");
  dot.className = `health-dot${bad.length ? " alarm" : warn.length ? " warn" : ""}`;

  const stale = health.filter((h) => (h.age_days ?? 0) >= 1).length;
  let text;
  if (bad.length) {
    text = `${bad.length} ${plural(bad.length, "źródło nie odpowiada", "źródła nie odpowiadają", "źródeł nie odpowiada")}`;
  } else if (warn.length) {
    text = `${warn.length} ${plural(warn.length, "źródło nieświeże", "źródła nieświeże", "źródeł nieświeżych")} z ${health.length}`;
  } else {
    text = `Dane aktualne we wszystkich ${health.length} źródłach`;
    if (stale) text += ` · ${stale} rzadziej odświeżanych`;
  }
  $("#health-text").textContent = text;

  const detail = $("#health-detail");
  detail.innerHTML = "";
  health.forEach((h) => {
    const pill = el("span", `hpill ${h.severity}`, `<i></i><b>${esc(h.label)}</b> ${esc(h.message)}`);
    pill.title = h.data_as_of ? `Dane z ${new Date(h.data_as_of).toLocaleString("pl-PL")}` : "";
    detail.appendChild(pill);
  });

  if ((bad.length || warn.length) && detail.hidden) toggleHealth(true);
}

function toggleHealth(force) {
  const detail = $("#health-detail");
  const open = force !== undefined ? force : detail.hidden;
  detail.hidden = !open;
  $("#health-summary").setAttribute("aria-expanded", String(open));
  $(".health-caret").textContent = open ? "zwiń" : "rozwiń";
}

/* ── dziś ──────────────────────────────────────────────────────────────── */
function renderToday() {
  const list = $("#today-list");
  list.innerHTML = "";
  state.data.today.forEach((action) => {
    const item = el("div", `item ${action.severity}`);
    item.appendChild(el("span", `sev-label sev-${action.severity}`, SEV_LABEL[action.severity] || ""));

    const body = el("div", "item-body");
    body.appendChild(el("div", "item-title", esc(action.title)));
    if (action.detail) body.appendChild(el("div", "item-detail", esc(action.detail)));
    if (action.link) {
      const link = el("a", "item-detail", esc(action.link_label || "Otwórz"));
      link.href = action.link;
      link.target = "_blank";
      link.rel = "noopener";
      body.appendChild(link);
    }
    item.appendChild(body);

    if (action.action_type) {
      const actions = el("div", "item-actions");
      const btn = el("button", "btn btn-mini", "Zrobione");
      btn.onclick = () => runAction(action);
      actions.appendChild(btn);
      item.appendChild(actions);
    }
    list.appendChild(item);
  });
}

async function runAction(action) {
  try {
    if (action.action_type === "task_status") {
      await api("/api/task/status", action.action_payload);
      toast("Odhaczone w sejfie");
    } else if (action.action_type === "queue_status") {
      await api("/api/queue/status", action.action_payload);
      toast("Zapisane w sejfie");
    }
    await load();
  } catch (error) {
    toast(error.message, "alarm");
  }
}

/* ── sygnały ───────────────────────────────────────────────────────────── */
function renderSignals() {
  const list = $("#signal-list");
  list.innerHTML = "";
  if (!state.data.signals.length) {
    list.appendChild(el("div", "empty", "Cisza. Żadne źródło nie zgłasza problemu."));
    return;
  }
  state.data.signals.forEach((signal) => {
    const item = el("div", `item ${signal.severity}`);
    item.appendChild(el("span", `sev-label sev-${signal.severity}`, SEV_LABEL[signal.severity] || ""));
    const body = el("div", "item-body");
    body.appendChild(el("div", "item-title", esc(signal.title)));
    if (signal.detail) body.appendChild(el("div", "item-detail", esc(signal.detail)));
    if (signal.link) {
      const link = el("a", "item-detail", esc(signal.link_label || "Otwórz"));
      link.href = signal.link;
      link.target = "_blank";
      link.rel = "noopener";
      body.appendChild(link);
    }
    item.appendChild(body);
    list.appendChild(item);
  });
}

/* ── kafelki ───────────────────────────────────────────────────────────── */
function tile(label, value, note, opts = {}) {
  const node = el("div", `tile${opts.accent ? " accent" : ""}`);
  node.appendChild(el("div", "tile-label", esc(label)));
  node.appendChild(el("div", `tile-value${opts.alarm ? " alarm" : ""}`, esc(value)));
  if (note) node.appendChild(el("div", "tile-note", esc(note)));
  return node;
}

function renderKpis() {
  const box = $("#kpi-tiles");
  box.innerHTML = "";
  const kasa = blockData("kasa");
  const poz = blockData("pozyskiwanie");
  const kli = blockData("klienci");

  if (kasa && kasa.revenue_window != null) {
    box.appendChild(tile("Przychód", zl(kasa.revenue_window), kasa.source_label || `${kasa.window_days} dni`, { accent: true }));
  }
  if (poz) box.appendChild(tile("Wartość lejka", zl(poz.funnel_value), "rozmowy i oferty"));
  if (kli) box.appendChild(tile("Aktywni klienci", num(kli.active_count), kli.overdue_count ? `${kli.overdue_count} wymaga ruchu` : "", { alarm: kli.overdue_count > 0 }));
  if (poz) box.appendChild(tile("Prospekty w lejku", num(poz.total), ""));
  if (!box.children.length) box.appendChild(el("div", "empty", "Brak liczb do pokazania."));
}

function renderStagebar() {
  const bar = $("#stagebar");
  bar.innerHTML = "";
  const poz = blockData("pozyskiwanie");
  if (!poz) {
    bar.appendChild(el("div", "empty", "Brak pliku lejka."));
    return;
  }
  state.data.pipeline.stages.forEach((stage) => {
    const box = el("div", "stagebox");
    box.appendChild(el("div", "n", num(poz.counts[stage.id] || 0)));
    box.appendChild(el("div", "l", esc(stage.label)));
    if (stage.hint) box.appendChild(el("div", "h", esc(stage.hint)));
    bar.appendChild(box);
  });
}

/* ── kanban lejka ──────────────────────────────────────────────────────── */
function renderKanban() {
  const poz = blockData("pozyskiwanie");
  const board = $("#kanban");
  board.innerHTML = "";
  if (!poz) {
    board.appendChild(el("div", "empty", "Brak pliku lejka. Załóż <code>Pozyskiwanie.md</code> w sejfie."));
    return;
  }

  const summary = $("#funnel-summary");
  if (summary) {
    summary.textContent =
      `${poz.total} ${plural(poz.total, "prospekt", "prospekty", "prospektów")} w lejku · ` +
      `wartość ${zl(poz.funnel_value)} (rozmowy i oferty)`;
  }

  const stages = state.data.pipeline.stages;
  stages.forEach((stage, index) => {
    const items = poz.by_stage[stage.id] || [];
    const col = el("div", "kancol");
    col.appendChild(el("h3", "", `${esc(stage.label)}<span>${items.length}</span>`));
    if (!items.length) col.appendChild(el("div", "muted", "pusto"));
    items.forEach((item) => col.appendChild(queueCard(item, index, stages)));
    board.appendChild(col);
  });
}

function queueCard(item, index, stages) {
  const card = el("div", "kancard clickable");
  card.appendChild(el("div", "kancard-title", esc(item.title)));
  const meta = [];
  if (item.value != null) meta.push(`${num(Math.round(item.value))} zł`);
  if (item.note) meta.push(clip(item.note, 70));
  if (meta.length) card.appendChild(el("div", "kancard-meta", esc(meta.join(" · "))));
  if (item.follow_up) {
    card.appendChild(el("div", `kancard-meta${item.follow_up_overdue ? " overdue" : ""}`,
      `follow-up ${esc(item.follow_up)}${item.follow_up_overdue ? " (zaległy)" : ""}`));
  }

  const foot = el("div", "kancard-foot");
  const prev = stages[index - 1];
  const next = stages[index + 1];

  [["‹", prev], ["›", next]].forEach(([glyph, target]) => {
    const btn = el("button", "nudge", glyph);
    btn.disabled = !target;
    btn.title = target ? `Przenieś do: ${target.label}` : "Nie ma dokąd";
    btn.onclick = (event) => {
      event.stopPropagation();
      if (target) moveItem(item.key, target.label);
    };
    foot.appendChild(btn);
  });

  if (item.date) foot.appendChild(el("span", "muted", esc(item.date)));
  card.appendChild(foot);
  card.onclick = () => openQueueDetail(item.key);
  return card;
}

async function moveItem(key, stageLabel) {
  try {
    await api("/api/queue/status", { key, stage: stageLabel });
    toast(`Zapisane w sejfie: ${stageLabel}`);
    await load();
    if (state.openKey === key) closeSheet();
  } catch (error) {
    toast(error.message, "alarm");
  }
}

function openQueueDetail(key) {
  const poz = blockData("pozyskiwanie");
  const item = Object.values(poz?.by_stage || {}).flat().find((i) => i.key === key);
  if (!item) return;
  state.openKey = key;

  openSheet(item.stage_label || item.stage, item.title, [
    item.value != null ? { text: `${num(Math.round(item.value))} zł`, tone: "brand" } : null,
    item.date ? { text: item.date } : null,
    item.follow_up ? { text: `follow-up ${item.follow_up}`, tone: item.follow_up_overdue ? "alarm" : "" } : null,
  ]);

  const mover = $("#sheet-move");
  mover.appendChild(el("span", "lab", "Etap"));
  state.data.pipeline.stages.forEach((stage) => {
    const btn = el("button", `stage-btn${stage.id === item.stage ? " current" : ""}`, esc(stage.label));
    btn.disabled = stage.id === item.stage;
    btn.title = stage.hint || "";
    btn.onclick = () => moveItem(item.key, stage.label);
    mover.appendChild(btn);
  });

  const body = $("#sheet-body");
  Object.entries(item.fields || {}).forEach(([label, value]) => {
    const row = el("div", "sheet-field");
    row.appendChild(el("div", "k", esc(label)));
    row.appendChild(el("div", "v", renderMarkdown(value)));
    body.appendChild(row);
  });
  if (!Object.keys(item.fields || {}).length) {
    body.appendChild(el("div", "md", renderMarkdown(item.body_md || "Ta pozycja ma na razie samą nazwę.")));
  }
}

/* ── klienci ───────────────────────────────────────────────────────────── */
function renderKlienci() {
  const kli = blockData("klienci");
  const list = $("#klienci-list");
  list.innerHTML = "";

  const badge = $("#badge-klienci");
  if (badge) {
    const n = kli?.overdue_count || 0;
    badge.textContent = n || "";
    badge.classList.toggle("on", n > 0);
  }

  if (!kli || !kli.all.length) {
    list.appendChild(el("div", "empty", "Brak klientów. Dodaj plik w <code>Klienci/</code> w sejfie."));
    return;
  }
  $("#klienci-summary").textContent =
    `${kli.active_count} ${plural(kli.active_count, "aktywny", "aktywnych", "aktywnych")} · ${kli.all.length} łącznie` +
    (kli.overdue_count ? ` · ${kli.overdue_count} wymaga ruchu` : "");

  kli.all.forEach((client) => {
    const card = el("div", `card cliente${client.status !== "aktywny" ? " dimmed" : ""}`);

    const head = el("div", "proj-head");
    head.appendChild(el("div", "proj-name", esc(client.name)));
    head.appendChild(el("span", `pill${client.status === "aktywny" ? " brand" : ""}`, esc(client.status)));
    card.appendChild(head);

    const meta = el("div", "task-meta");
    if (client.stawka) meta.appendChild(el("span", "pill", esc(client.stawka)));
    if (client.ostatni_kontakt) {
      const stale = client.days_since_contact != null && client.days_since_contact > 21;
      meta.appendChild(el("span", `pill${stale ? " alarm" : ""}`,
        `kontakt ${esc(client.ostatni_kontakt)}${client.days_since_contact != null ? ` (${client.days_since_contact} dni)` : ""}`));
    }
    card.appendChild(meta);

    if (client.projekty.length) {
      const wrap = el("div", "cliente-block");
      wrap.appendChild(el("div", "cliente-h", "Projekty"));
      client.projekty.forEach((p) => {
        const row = el("div", "mini-row");
        row.appendChild(el("span", "mini-name", esc(p.name)));
        const pills = el("span", "mini-pills");
        if (p.etap) pills.appendChild(el("span", "pill", esc(p.etap)));
        if (p.deadline) {
          const lab = p.overdue ? `${p.deadline} (po terminie)`
            : p.days_to_deadline != null && p.days_to_deadline >= 0 ? `${p.deadline} (za ${p.days_to_deadline} dni)` : p.deadline;
          pills.appendChild(el("span", `pill${p.overdue ? " alarm" : ""}`, esc(lab)));
        }
        row.appendChild(pills);
        wrap.appendChild(row);
      });
      card.appendChild(wrap);
    }

    if (client.todos.length) {
      const wrap = el("div", "cliente-block");
      wrap.appendChild(el("div", "cliente-h", `Do zrobienia · ${client.open_todos} ${plural(client.open_todos, "otwarte", "otwarte", "otwartych")}`));
      client.todos
        .slice()
        .sort((a, b) => a.done - b.done)
        .forEach((t) => wrap.appendChild(todoRow(t, client.file)));
      card.appendChild(wrap);
    }

    list.appendChild(card);
  });
}

/** Wiersz to-do z checkboxem - klik zapisuje do pliku w sejfie. */
function todoRow(todo, file) {
  const done = !!todo.done;
  const row = el("div", `task${done ? " done" : ""}`);

  const check = document.createElement("input");
  check.type = "checkbox";
  check.checked = done;
  check.onchange = async () => {
    check.disabled = true;
    try {
      await api("/api/task/status", { file, key: todo.key, done: check.checked });
      await load();
    } catch (error) {
      toast(error.message, "alarm");
      check.checked = done;
      check.disabled = false;
    }
  };
  row.appendChild(check);

  const body = el("div", "item-body");
  body.appendChild(el("div", "task-text", esc(todo.text)));
  if (todo.termin) {
    const meta = el("div", "task-meta");
    meta.appendChild(el("span", `pill${todo.overdue ? " alarm" : ""}`, `termin ${esc(todo.termin)}`));
    body.appendChild(meta);
  }
  row.appendChild(body);
  return row;
}

/* ── biznes ────────────────────────────────────────────────────────────── */
function renderBiznes() {
  const biz = blockData("biznes");
  const list = $("#biznes-list");
  list.innerHTML = "";
  if (!biz || !biz.all.length) {
    list.appendChild(el("div", "empty", "Brak inicjatyw. Dodaj plik w <code>Biznes/</code> w sejfie."));
    return;
  }
  biz.all.forEach((item) => {
    const card = el("div", "card cliente");
    const head = el("div", "proj-head");
    head.appendChild(el("div", "proj-name", esc(item.name)));
    head.appendChild(el("span", "pill", esc(item.etap)));
    card.appendChild(head);

    if (item.deadline) {
      const meta = el("div", "task-meta");
      const lab = item.overdue ? `${item.deadline} (po terminie)`
        : item.days_to_deadline != null && item.days_to_deadline >= 0 ? `${item.deadline} (za ${item.days_to_deadline} dni)` : item.deadline;
      meta.appendChild(el("span", `pill${item.overdue ? " alarm" : ""}`, `deadline ${esc(lab)}`));
      card.appendChild(meta);
    }

    if (item.todos.length) {
      const wrap = el("div", "cliente-block");
      wrap.appendChild(el("div", "cliente-h", `Do zrobienia · ${item.open_todos} ${plural(item.open_todos, "otwarte", "otwarte", "otwartych")}`));
      item.todos.slice().sort((a, b) => a.done - b.done).forEach((t) => wrap.appendChild(todoRow(t, item.file)));
      card.appendChild(wrap);
    }
    list.appendChild(card);
  });
}

/* ── kasa ──────────────────────────────────────────────────────────────── */
function renderKasa() {
  const kasa = blockData("kasa");
  const big = $("#kasa-big");
  const pc = $("#kasa-perclient");
  const tx = $("#kasa-txns");
  const pend = $("#kasa-pending");
  const note = $("#kasa-note");
  [big, pc, tx, pend].forEach((n) => n && (n.innerHTML = ""));
  if (note) note.textContent = "";

  if (!kasa || kasa.zrodlo === "nie_licze") {
    if (big) big.appendChild(el("div", "empty", "Kasa wyłączona w konfiguracji."));
    if (note) note.textContent = kasa?.note || "";
    return;
  }

  const rev = kasa.revenue_window || 0;

  // ── hero: kwota + źródło + mini-liczby ──
  const box = el("div", "card kasa-card");
  box.appendChild(el("div", "tile-label", `Przychód · ostatnie ${kasa.window_days} dni`));
  box.appendChild(el("div", "kasa-amount", kasa.revenue_window != null ? zl(rev) : "brak danych"));
  const src = el("div", "kasa-src");
  src.appendChild(el("span", "src-dot", ""));
  src.appendChild(document.createTextNode(`${kasa.source_label || "faktury"} · zsynchronizowano`));
  box.appendChild(src);
  const meta = [];
  if (kasa.paid_count) meta.push(`${kasa.paid_count} ${plural(kasa.paid_count, "wpłata", "wpłaty", "wpłat")}`);
  meta.push(`lejek ${zl(kasa.funnel_value)}`);
  meta.push(`${num(kasa.active_clients)} ${plural(kasa.active_clients, "klient", "klientów", "klientów")}`);
  if (kasa.conversion != null) meta.push(`konwersja ${kasa.conversion}%`);
  box.appendChild(el("div", "kasa-meta", esc(meta.join(" · "))));
  big.appendChild(box);

  // ── przychód per klient (pasek = udział w kwocie) ──
  const per = kasa.per_client || [];
  if (!per.length) {
    pc.appendChild(el("div", "empty", "Brak wpłat w tym oknie."));
  } else {
    per.forEach((c) => {
      const share = rev ? Math.round((c.amount / rev) * 100) : 0;
      const row = el("div", "bar-row");
      row.appendChild(el("div", "bar-label", esc(c.who)));
      const track = el("div", "bar-track");
      track.appendChild(el("span", "", "")).style.width = `${share}%`;
      row.appendChild(track);
      row.appendChild(el("div", "bar-value", `${zl(c.amount)} · ${share}%`));
      pc.appendChild(row);
    });
  }

  // ── ostatnie wpłaty (opłacone) ──
  const txns = kasa.transactions || [];
  if (!txns.length) {
    tx.appendChild(el("div", "empty", "Brak wpłat."));
  } else {
    txns.forEach((t) => {
      const row = el("div", "item ok");
      row.appendChild(el("span", "sev-label sev-ok", "opłacona"));
      const body = el("div", "item-body");
      body.appendChild(el("div", "item-title", esc(t.who)));
      body.appendChild(el("div", "item-detail", esc(t.date)));
      row.appendChild(body);
      row.appendChild(el("span", "pill brand", zl(t.amount)));
      tx.appendChild(row);
    });
  }

  // ── oczekujące / zaległe faktury ──
  const pending = kasa.pending || [];
  if (!pending.length) {
    pend.appendChild(el("div", "empty", "Nic nie wisi. Wszystko opłacone."));
  } else {
    pending.forEach((p) => {
      const row = el("div", "item warn");
      row.appendChild(el("span", "sev-label sev-warn", "oczekuje"));
      const body = el("div", "item-body");
      body.appendChild(el("div", "item-title", esc(p.who)));
      body.appendChild(el("div", "item-detail", `wystawiona ${esc(p.date)}`));
      row.appendChild(body);
      row.appendChild(el("span", "pill", zl(p.amount)));
      pend.appendChild(row);
    });
    if (kasa.pending_total) {
      pend.appendChild(el("div", "kasa-meta", `Łącznie wisi: ${zl(kasa.pending_total)}`));
    }
  }

  if (note) note.textContent = kasa.note || "";
}

/* ── toolkit ───────────────────────────────────────────────────────────── */
function renderToolkit() {
  const toolkit = blockData("toolkit");
  const list = $("#toolkit-list");
  list.innerHTML = "";
  (toolkit?.tools || []).forEach((tool) => {
    const card = el("div", "card card-hover tool");
    card.innerHTML =
      `<code>${esc(tool.invoke)}</code> <span class="pill">${esc(tool.scope)}</span>` +
      `<p>${esc(tool.description || "bez opisu")}</p>`;
    card.onclick = () => {
      navigator.clipboard?.writeText(tool.invoke);
      toast(`Skopiowane: ${tool.invoke}`);
    };
    list.appendChild(card);
  });
  if (!list.children.length) list.appendChild(el("div", "empty", "Nie znalazłem komend ani skilli."));

  const health = $("#health-table");
  health.innerHTML = "";
  state.data.health.forEach((h) => {
    const row = el("div", `item ${h.severity}`);
    row.appendChild(el("span", `sev-label sev-${h.severity}`, SEV_LABEL[h.severity] || ""));
    const body = el("div", "item-body");
    body.appendChild(el("div", "item-title", esc(h.label)));
    body.appendChild(
      el("div", "item-detail", `${esc(h.message)}${h.data_as_of ? ` · dane z ${new Date(h.data_as_of).toLocaleString("pl-PL")}` : ""}`)
    );
    row.appendChild(body);
    health.appendChild(row);
  });
}

/* ── content / do nagrania ─────────────────────────────────────────────── */
function renderContent() {
  const t = blockData("tresci");
  const board = $("#content-kanban");
  if (!board) return;
  board.innerHTML = "";
  const badge = $("#badge-content");
  const open = t ? ((t.by_status["pomysł"] || []).length + (t.by_status["szkic"] || []).length) : 0;
  if (badge) { badge.textContent = open || ""; badge.classList.toggle("on", open > 0); }
  if (!t || !t.total) {
    board.appendChild(el("div", "empty", "Brak pomysłów. Dodaj je w <code>Do nagrania.md</code> w sejfie."));
    return;
  }
  (t.stages || []).forEach((st) => {
    const items = t.by_status[st] || [];
    const col = el("div", "kancol");
    col.appendChild(el("h3", "", `${_CONTENT_LABELS[st] || st}<span>${items.length}</span>`));
    col.ondragover = (e) => { e.preventDefault(); col.classList.add("drop"); };
    col.ondragleave = () => col.classList.remove("drop");
    col.ondrop = (e) => {
      e.preventDefault();
      col.classList.remove("drop");
      const key = e.dataTransfer.getData("text/plain");
      if (key) moveContent(key, st);
    };
    if (!items.length) col.appendChild(el("div", "muted", "przeciągnij tu"));
    items.forEach((it) => {
      const card = el("div", "kancard clickable");
      card.draggable = true;
      card.ondragstart = (e) => { e.dataTransfer.setData("text/plain", it.key); e.dataTransfer.effectAllowed = "move"; };
      card.appendChild(el("div", "kancard-title", esc(it.title)));
      if (it.note) card.appendChild(el("div", "kancard-meta", esc(clip(it.note, 90))));
      card.onclick = () => openContentDetail(it);
      col.appendChild(card);
    });
    board.appendChild(col);
  });
}

async function moveContent(key, stage) {
  try {
    await api("/api/content/status", { key, status: stage });
    toast(`Przeniesione: ${_CONTENT_LABELS[stage] || stage}`);
    await load();
  } catch (error) {
    toast(error.message, "alarm");
  }
}

const _CONTENT_LABELS = { "pomysł": "Pomysł", "szkic": "Szkic", "nagrane": "Nagrane", "opublikowane": "Opublikowane" };

function openContentDetail(it) {
  openSheet("Do nagrania", it.title, [
    { text: _CONTENT_LABELS[it.status] || it.status, tone: it.status === "opublikowane" ? "ok" : "brand" },
  ]);
  const body = $("#sheet-body");
  body.appendChild(el("div", "md", renderMarkdown(it.body || "Ta pozycja ma na razie sam tytuł. Dopisz treść w Do nagrania.md w sejfie.")));
}

/* ── archiwum outputów ─────────────────────────────────────────────────── */
function renderArchiwum() {
  const a = blockData("outputy");
  const list = $("#archiwum-list");
  if (!list) return;
  list.innerHTML = "";
  const badge = $("#badge-archiwum");
  const total = a?.total || 0;
  if (badge) { badge.textContent = total || ""; badge.classList.toggle("on", total > 0); }
  if (!a || !total) {
    list.appendChild(el("div", "empty", "Pusto. Gdy zamkniesz zadanie z Claude, efekt (cennik, oferta, tekst) wyląduje tutaj."));
    return;
  }
  (a.typy || []).forEach((typ) => {
    const items = a.by_typ[typ] || [];
    if (!items.length) return;
    list.appendChild(el("h2", "section-title", `${esc(typ)}<span class="count-soft">${items.length}</span>`));
    const grid = el("div", "grid-cards");
    items.forEach((it) => {
      const card = el("div", "card card-hover output");
      const meta = [it.klient, it.data ? new Date(it.data).toLocaleDateString("pl-PL") : ""].filter(Boolean).join(" · ");
      card.innerHTML =
        `<div class="output-title">${esc(it.title)}</div>` +
        (meta ? `<div class="output-meta">${esc(meta)}</div>` : "") +
        (it.note ? `<p class="output-note">${esc(clip(it.note, 120))}</p>` : "");
      card.onclick = () => openOutputDetail(it);
      grid.appendChild(card);
    });
    list.appendChild(grid);
  });
}

function openOutputDetail(it) {
  openSheet(`Archiwum · ${it.typ}`, it.title, [
    it.klient ? { text: it.klient, tone: "brand" } : null,
    it.data ? { text: new Date(it.data).toLocaleDateString("pl-PL"), tone: "" } : null,
  ].filter(Boolean));
  const move = $("#sheet-move");
  const copy = el("button", "btn-copy", "Kopiuj tekst");
  copy.onclick = () => {
    navigator.clipboard?.writeText(it.body || "");
    toast("Skopiowane do schowka");
  };
  move.appendChild(copy);
  const body = $("#sheet-body");
  body.appendChild(el("div", "md", renderMarkdown(it.body || "Ten output jest pusty.")));
  if (it.path) body.appendChild(el("div", "output-path", `Plik: ${esc(it.path)}`));
}

/* ── zasięgi / statystyki ──────────────────────────────────────────────── */
function renderStatystyki() {
  const s = blockData("statystyki");
  const tiles = $("#zasiegi-tiles");
  if (!tiles) return;
  tiles.innerHTML = "";
  const chart = $("#zasiegi-chart");
  const top = $("#zasiegi-top");
  chart.innerHTML = "";
  top.innerHTML = "";

  if (!s || !s.has_data) {
    tiles.appendChild(el("div", "empty", "Pusto. Wpisuj zasięgi swoich rolek w <code>Zasięgi.md</code> albo po prostu podaj je Claude - dopisze."));
    return;
  }

  tiles.appendChild(tile(`Zasięg ${s.window_days} dni`, num(s.reach_in_window), `${s.posts_in_window} ${plural(s.posts_in_window, "post", "posty", "postów")}`, { accent: true }));
  tiles.appendChild(tile("Średni zasięg", num(s.avg_reach), "na post"));
  tiles.appendChild(tile("Najlepszy post", num(s.best_reach), "zasięgu"));
  tiles.appendChild(tile("Postów łącznie", num(s.total_posts), s.days_since_last != null ? `ostatni ${s.days_since_last} dni temu` : ""));

  const series = s.reach_series || [];
  const max = Math.max(...series.map((p) => p.reach), 1);
  if (series.length) {
    series.forEach((p) => {
      const bar = el("div", "reachbar");
      bar.style.height = `${Math.max(3, (p.reach / max) * 100)}%`;
      bar.title = `${p.date}: ${num(p.reach)} zasięgu`;
      chart.appendChild(bar);
    });
  } else {
    chart.appendChild(el("div", "muted", "Dodaj daty przy postach, żeby zobaczyć trend."));
  }

  (s.top_posts || []).forEach((post) => {
    const row = el("div", "item");
    const body = el("div", "item-body");
    body.appendChild(el("div", "item-title", esc(post.title)));
    const bits = [`${num(post.reach)} zasięgu`];
    if (post.vs_avg) bits.push(`${post.vs_avg}× średniej`);
    if (post.engagement_rate != null) bits.push(`${post.engagement_rate}% zaangażowania`);
    if (post.date) bits.push(post.date.slice(0, 10));
    body.appendChild(el("div", "item-detail", esc(bits.join(" · "))));
    if (post.link) {
      const a = el("a", "item-detail", "Otwórz post");
      a.href = post.link; a.target = "_blank"; a.rel = "noopener";
      body.appendChild(a);
    }
    row.appendChild(body);
    top.appendChild(row);
  });
}

/* ── samouczek ─────────────────────────────────────────────────────────── */
const _SAMOUCZEK = [
  { label: "Dziś", src: null, cel: "Co robić dziś - najpilniejsze akcje i sygnały zebrane z całego panelu.", potrzeba: "Nic. Liczy się z pozostałych zakładek." },
  { label: "Prospecting", src: "pozyskiwanie", cel: "Lejek nowych klientów - od namierzonej firmy po wysłaną ofertę.", potrzeba: "Dodawaj firmy (sam albo mówiąc to Claude). Podłącz Gmail, żeby oferty i odpowiedzi wpadały same." },
  { label: "Klienci", src: "klienci", cel: "Obecni klienci: ich projekty i ich zadania.", potrzeba: "Opowiedz Claude, kogo masz - założy pliki klientów." },
  { label: "Biznes", src: "biznes", cel: "Praca nad Twoją firmą: własne projekty i zadania (oferta, strona, systemy).", potrzeba: "Dorzuć własne projekty i zadania." },
  { label: "To-do", src: null, cel: "Wszystkie otwarte zadania od klientów i z Biznesu w jednym miejscu.", potrzeba: "Nic - zbiera zadania z pozostałych zakładek." },
  { label: "Kasa", src: "kasa", cel: "Ile realnie wpłynęło.", potrzeba: "Podłącz Stripe (przychód na żywo) albo wpisuj kwoty w Kasa.md." },
  { label: "Content", src: "tresci", cel: "Pomysły na treści od pomysłu do publikacji (kanban).", potrzeba: "Włącza się, gdy w wywiadzie mówisz, że publikujesz. Dodawaj pomysły." },
  { label: "Zasięgi", src: "statystyki", cel: "Statystyki Twoich treści: zasięg, top posty.", potrzeba: "Wpisuj liczby w Zasięgi.md albo podawaj je Claude. (Instagram na żywo - do dołożenia.)" },
  { label: "Archiwum", src: "outputy", cel: "Gotowe efekty skończonych zadań - cenniki, oferty, teksty.", potrzeba: "Zapełnia się samo, gdy zamykasz zadania z Claude." },
  { label: "Kalendarz", src: null, cel: "Terminy i deadline'y z całego panelu, miesiąc po miesiącu.", potrzeba: "Podłącz Google Calendar, żeby wpadały też spotkania." },
  { label: "Czas", src: "timer", cel: "Timer roboczy (pomodoro albo stoper) i log czasu.", potrzeba: "Nic - działa od razu." },
  { label: "Połączenia", src: "connectors", cel: "Stan integracji: Gmail, Kalendarz, Stripe, klucze API.", potrzeba: "Podłącz to, co chcesz - reszta panelu wtedy robi więcej sama." },
  { label: "Toolkit", src: "toolkit", cel: "Skróty do skilli (research, oferta, cold-mail) i narzędzi AI klubu.", potrzeba: "Nic." },
];

function _blockHasData(src) {
  const b = state.data.blocks[src];
  if (!b || !b.ok) return false;
  const d = b.data || {};
  switch (src) {
    case "pozyskiwanie": return (d.total || 0) > 0;
    case "klienci": return (d.active_count || 0) > 0 || (d.all || 0) > 0;
    case "biznes": return (d.count || 0) > 0 || (d.all || 0) > 0;
    case "kasa": return d.revenue_window != null || (d.transactions || 0) > 0 || (d.per_client && d.per_client.length > 0);
    case "tresci": return (d.total || 0) > 0;
    case "statystyki": return !!d.has_data;
    case "outputy": return (d.total || 0) > 0;
    case "connectors": return (d.total || 0) > 0;
    case "timer": return true;
    case "toolkit": return (d.tools && d.tools.length > 0);
    default: return true;
  }
}

function renderSamouczek() {
  const list = $("#samouczek-list");
  if (!list) return;
  list.innerHTML = "";
  _SAMOUCZEK.forEach((t) => {
    let cls, dot, stan;
    if (t.src === null) { cls = "ok"; dot = "s-ok"; stan = "działa"; }
    else if (!(t.src in state.data.blocks)) { cls = "off"; dot = "s-off"; stan = "wyłączone"; }
    else if (_blockHasData(t.src)) { cls = "ok"; dot = "s-ok"; stan = "działa"; }
    else { cls = "wait"; dot = "s-wait"; stan = "czeka na Ciebie"; }

    const row = el("div", `samo-row ${cls}`);
    row.appendChild(el("span", `samo-dot ${dot}`, "●"));
    const body = el("div", "samo-body");
    const head = el("div", "samo-head");
    head.appendChild(el("span", "samo-name", esc(t.label)));
    head.appendChild(el("span", "samo-stan", esc(stan)));
    body.appendChild(head);
    body.appendChild(el("div", "samo-cel", esc(t.cel)));
    if (cls !== "ok") body.appendChild(el("div", "samo-potrzeba", `Żeby ożyła: ${esc(t.potrzeba)}`));
    row.appendChild(body);
    list.appendChild(row);
  });
}

/* ── połączenia (1:1 z src/dashboard) ──────────────────────────────────── */
function renderConnectors() {
  const conn = blockData("connectors");
  const groups = [
    ["claudeai", conn?.claude_ai, "conn-claudeai", "count-claudeai"],
    ["mcp", conn?.mcp, "conn-mcp", "count-mcp"],
    ["api", conn?.api, "conn-api", "count-api"],
  ];

  const badge = $("#badge-connectors");
  if (badge) {
    const problems = conn?.problem_count || 0;
    badge.textContent = problems || "";
    badge.classList.toggle("on", problems > 0);
  }

  groups.forEach(([, items, listId, countId]) => {
    const list = $(`#${listId}`);
    if (!list) return;
    list.innerHTML = "";
    const rows = items || [];
    const active = rows.filter((r) => r.severity === "ok").length;
    const count = $(`#${countId}`);
    if (count) count.textContent = rows.length ? `${active}/${rows.length} aktywnych` : "";

    if (!rows.length) {
      list.appendChild(el("div", "empty", "Nic tu nie ma."));
      return;
    }
    rows.forEach((row) => {
      const item = el("div", `item ${row.severity}`);
      item.appendChild(el("span", `sev-label sev-${row.severity}`, esc(row.status)));
      const body = el("div", "item-body");
      body.appendChild(el("div", "item-title", esc(row.label)));
      const bits = [row.message];
      if (row.uzycie) bits.push(row.uzycie);
      body.appendChild(el("div", "item-detail", esc(bits.filter(Boolean).join(" · "))));
      item.appendChild(body);
      if (row.env) item.appendChild(el("span", "pill", esc(row.env)));
      list.appendChild(item);
    });
  });
}

/* ── timer (1:1 z src/dashboard) ───────────────────────────────────────── */
const mmss = (seconds) => {
  const s = Math.max(0, Math.round(seconds));
  return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
};

function hhmm(seconds) {
  const total = Math.round((seconds || 0) / 60);
  const h = Math.floor(total / 60);
  const m = total % 60;
  return h ? `${h} h ${m} min` : `${m} min`;
}

function hourOf(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

/* Krótki sygnał dźwiękowy (Web Audio, bez plików). Kontekst odblokowujemy
   przy pierwszym kliknięciu Start/Przerwa, żeby przeglądarka pozwoliła grać. */
let _audioCtx = null;
function unlockAudio() {
  try {
    _audioCtx = _audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    if (_audioCtx.state === "suspended") _audioCtx.resume();
  } catch (e) { /* brak audio - trudno */ }
}
function beep(freq = 880, ms = 160) {
  try {
    unlockAudio();
    if (!_audioCtx) return;
    const o = _audioCtx.createOscillator(), g = _audioCtx.createGain();
    o.type = "sine";
    o.frequency.value = freq;
    o.connect(g); g.connect(_audioCtx.destination);
    const t0 = _audioCtx.currentTime;
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(0.22, t0 + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + ms / 1000);
    o.start(t0);
    o.stop(t0 + ms / 1000 + 0.03);
  } catch (e) { /* ignoruj */ }
}

const RING_R = 62;
const RING_C = 2 * Math.PI * RING_R;

function timerWidget() {
  const t = blockData("timer");
  if (!t) return null;
  const run = t.running;
  const onBreak = state.breakUntil && state.breakUntil > Date.now();

  const wrap = el("div", `tw tw-timer${run ? " is-running" : ""}`);
  wrap.title = "Otwórz zakładkę Czas";
  const dot = el("span", `tw-dot${run ? " on" : ""}`, "");
  const time = el("div", "tw-time", run || onBreak ? "…" : mmss((state.pomoMinutes || t.pomodoro_minutes) * 60));
  time.id = "timer-time";
  const head = el("div", "tw-head");
  head.appendChild(dot);
  head.appendChild(time);
  wrap.appendChild(head);
  const label = onBreak ? "przerwa" : run ? (run.task_text || "bez zadania") : `dziś ${hhmm(t.today_seconds)}`;
  wrap.appendChild(el("div", "tw-foot", esc(clip(label, 30))));
  wrap.onclick = () => selectTab("czas");
  return wrap;
}

function renderTopbar() {
  const host = $("#topbar-widgets");
  if (!host) return;
  host.innerHTML = "";
  const w = timerWidget();
  if (w) host.appendChild(w);
  startTimerTick();
}

function renderTime() {
  const t = blockData("timer");
  const tab = document.querySelector('.tab[data-tab="czas"]');
  if (tab) tab.hidden = !t;
  if (!t) return;

  const run = t.running;
  const onBreak = state.breakUntil && state.breakUntil > Date.now();

  $("#clock").innerHTML = `
    <svg class="ring" viewBox="0 0 150 150" aria-hidden="true">
      <circle class="ring-bg" cx="75" cy="75" r="${RING_R}"></circle>
      <circle class="ring-fg" id="clock-ring" cx="75" cy="75" r="${RING_R}"
              stroke-dasharray="${RING_C}" stroke-dashoffset="${run || onBreak ? 0 : RING_C}"></circle>
    </svg>
    <div class="clock-time" id="clock-time">${
      run || onBreak ? "…" : mmss((state.timerMode || t.default_mode) === "stoper" ? 0 : (state.pomoMinutes || t.pomodoro_minutes) * 60)
    }</div>`;

  const taskHost = $("#clock-task");
  taskHost.innerHTML = "";
  taskHost.appendChild(el("div", "eyebrow", onBreak ? "przerwa" : run ? "pracujesz nad" : "gotowy do startu"));
  taskHost.appendChild(el("div", "clock-task-name",
    esc(onBreak ? "odpocznij" : run ? (run.task_text || "bez zadania") : "wybierz zadanie z listy poniżej")));
  if (run?.projekt) taskHost.appendChild(el("span", "pill", esc(run.projekt)));

  const controls = $("#clock-controls");
  controls.innerHTML = "";
  if (run) {
    const stop = el("button", "btn btn-primary", "Zatrzymaj i zapisz");
    stop.onclick = () => stopTimer();
    controls.appendChild(stop);
  } else if (onBreak) {
    const skip = el("button", "btn btn-ghost", "Pomiń przerwę");
    skip.onclick = () => { state.breakUntil = null; renderTime(); renderTopbar(); };
    controls.appendChild(skip);
  } else {
    const isPomo = (state.timerMode || t.default_mode) !== "stoper";
    const curMin = state.pomoMinutes || t.pomodoro_minutes;
    const modes = el("div", "tw-modes");
    if (isPomo) {
      [15, 25, 45, 60].forEach((min) => {
        const btn = el("button", `tw-mode${curMin === min ? " on" : ""}`, `${min} min`);
        btn.onclick = () => { state.pomoMinutes = min; state.timerMode = "pomodoro"; renderTime(); };
        modes.appendChild(btn);
      });
    }
    const stoperBtn = el("button", `tw-mode${!isPomo ? " on" : ""}`, "stoper");
    stoperBtn.onclick = () => { state.timerMode = isPomo ? "stoper" : "pomodoro"; renderTime(); };
    modes.appendChild(stoperBtn);
    controls.appendChild(modes);

    const start = el("button", "btn btn-primary", isPomo ? `Start ${curMin} min` : "Start stopera");
    start.onclick = () => startTimer({});
    controls.appendChild(start);

    const breakBtn = el("button", "btn btn-ghost", `Przerwa ${t.break_minutes || 5} min`);
    breakBtn.onclick = () => startBreak();
    controls.appendChild(breakBtn);
  }

  $("#clock-stats").innerHTML =
    `<span class="pill">dziś ${hhmm(t.today_seconds)}</span>` +
    `<span class="pill">tydzień ${hhmm(t.week_seconds)}</span>` +
    `<span class="pill">${t.sessions_today} ${plural(t.sessions_today, "sesja", "sesje", "sesji")} dziś</span>`;

  renderTimePicker(run);
  renderTimeSummary(t);
  renderTimeJournal(t);
  startTimerTick();
}

/** Otwarte zadania do odpalenia licznika — tu z klientów i własnego biznesu. */
function renderTimePicker(run) {
  const host = $("#clock-picker");
  host.innerHTML = "";
  const tasks = [];
  (blockData("klienci")?.all || []).forEach((c) =>
    (c.todos || []).filter((t) => !t.done).forEach((t) =>
      tasks.push({ key: t.key, text: t.text, projekt: c.name })));
  (blockData("biznes")?.all || []).forEach((b) =>
    (b.todos || []).filter((t) => !t.done).forEach((t) =>
      tasks.push({ key: t.key, text: t.text, projekt: b.name })));

  if (!tasks.length) {
    host.appendChild(el("div", "empty", "Brak otwartych zadań u klientów i w biznesie."));
    return;
  }
  tasks.slice(0, 12).forEach((task) => {
    const active = run && run.task_key === task.key;
    const row = el("div", `item${active ? " is-active" : ""}`);
    const body = el("div", "item-body");
    body.appendChild(el("div", "task-text", esc(task.text)));
    const meta = el("div", "task-meta");
    if (task.projekt) meta.appendChild(el("span", "pill", esc(task.projekt)));
    body.appendChild(meta);
    row.appendChild(body);
    const button = el("button", "btn btn-ghost tw-btn", active ? "trwa" : run ? "przełącz" : "pracuj");
    button.disabled = !!active;
    button.onclick = () => startTimer({ taskKey: task.key, taskText: task.text, projekt: task.projekt || "" });
    row.appendChild(button);
    host.appendChild(row);
  });
}

function renderTimeSummary(t) {
  const host = $("#clock-summary");
  host.innerHTML = "";
  const projects = t.per_project_week || [];
  if (!projects.length && !(t.top_tasks || []).length) {
    host.appendChild(el("div", "empty", "Jeszcze nic nie zmierzone. Odpal licznik nad zadaniem."));
    return;
  }
  if (projects.length) {
    host.appendChild(el("div", "group-head", "Projekty w tym tygodniu"));
    const max = Math.max(...projects.map((p) => p.seconds));
    projects.forEach((project) => {
      const row = el("div", "bar-row");
      row.appendChild(el("div", "bar-label", esc(project.projekt)));
      const track = el("div", "bar-track");
      track.appendChild(el("span", "", "")).style.width = `${Math.round((project.seconds / max) * 100)}%`;
      row.appendChild(track);
      row.appendChild(el("div", "bar-value", hhmm(project.seconds)));
      host.appendChild(row);
    });
  }
  if ((t.top_tasks || []).length) {
    host.appendChild(el("div", "group-head", "Zadania, które zjadły najwięcej"));
    t.top_tasks.slice(0, 6).forEach((task) => {
      const row = el("div", "bar-row");
      row.appendChild(el("div", "bar-label", esc(clip(task.text, 46))));
      row.appendChild(el("div", "bar-value", hhmm(task.seconds)));
      host.appendChild(row);
    });
  }
}

function renderTimeJournal(t) {
  const host = $("#clock-journal");
  host.innerHTML = "";
  const entries = t.today_entries || [];
  if (!entries.length) {
    host.appendChild(el("div", "empty", "Dziś jeszcze nic nie zmierzone."));
    return;
  }
  entries.forEach((entry) => {
    const row = el("div", "item");
    const body = el("div", "item-body");
    body.appendChild(el("div", "task-text", esc(entry.task_text || "bez zadania")));
    const meta = el("div", "task-meta");
    meta.appendChild(el("span", "pill brand", hhmm(entry.seconds)));
    meta.appendChild(el("span", "pill", `${hourOf(entry.start)}–${hourOf(entry.end)}`));
    if (entry.projekt) meta.appendChild(el("span", "pill", esc(entry.projekt)));
    if (entry.mode) meta.appendChild(el("span", "pill", esc(entry.mode)));
    body.appendChild(meta);
    row.appendChild(body);
    host.appendChild(row);
  });
}

async function startTimer({ taskKey = "", taskText = "", projekt = "" }) {
  const t = blockData("timer") || {};
  unlockAudio();
  try {
    await api("/api/timer/start", {
      mode: state.timerMode || t.default_mode || "pomodoro",
      task_key: taskKey, task_text: taskText, projekt,
      minutes: state.pomoMinutes || t.pomodoro_minutes || 25,
    });
    state.pomodoroFired = false;
    state.breakUntil = null;
    await load();
  } catch (error) {
    toast(error.message, "alarm");
  }
}

function startBreak() {
  const t = blockData("timer") || {};
  unlockAudio();
  state.breakUntil = Date.now() + Number(t.break_minutes || 5) * 60000;
  state.pomodoroFired = false;
  renderTime();
  renderTopbar();
}

async function stopTimer(silent = false) {
  try {
    const result = await api("/api/timer/stop", {});
    if (!silent) {
      const seconds = result?.entry?.seconds;
      toast(seconds ? `Zapisane: ${hhmm(seconds)}` : "Sesja za krótka, nie zapisuję");
    }
    await load();
  } catch (error) {
    toast(error.message, "alarm");
  }
}

function startTimerTick() {
  if (state.timerTick) clearInterval(state.timerTick);
  const t = blockData("timer");
  if (!t) return;

  const paint = () => {
    const now = Date.now();
    const bar = $("#timer-time");
    const big = $("#clock-time");
    const ring = $("#clock-ring");
    if (!bar && !big) return;

    const show = (text, progress) => {
      if (bar) bar.textContent = text;
      if (big) big.textContent = text;
      if (ring) ring.style.strokeDashoffset = String(RING_C * (1 - Math.min(1, Math.max(0, progress))));
    };

    if (state.breakUntil) {
      if (state.breakUntil > now) {
        const total = Number(t.break_minutes || 5) * 60;
        const left = (state.breakUntil - now) / 1000;
        show(mmss(left), (total - left) / total);
        return;
      }
      state.breakUntil = null;
      beep(660, 200);
      toast("Przerwa skończona.");
      renderTime();
      renderTopbar();
      return;
    }

    const run = t.running;
    if (!run) return;

    const elapsed = (now - new Date(run.started_at).getTime()) / 1000;
    if (run.mode === "pomodoro" && run.planned_minutes) {
      const total = run.planned_minutes * 60;
      const left = total - elapsed;
      show(mmss(left), elapsed / total);
      if (left <= 0 && !state.pomodoroFired) {
        state.pomodoroFired = true;
        beep(880, 170);
        setTimeout(() => beep(1175, 190), 200);
        toast("Pomodoro skończone. Weź przerwę albo lecisz dalej.");
        stopTimer(true);
      }
    } else {
      show(mmss(elapsed), (elapsed % 60) / 60);
    }
  };

  paint();
  state.timerTick = setInterval(paint, 1000);
}

/* ── to-do (agregat zadań klientów + biznesu) ──────────────────────────── */
function todoRowFull(t) {
  const done = !!t.done;
  const row = el("div", `task${done ? " done" : ""}`);
  const check = document.createElement("input");
  check.type = "checkbox";
  check.checked = done;
  check.onchange = async () => {
    check.disabled = true;
    try {
      await api("/api/task/status", { file: t.file, key: t.key, done: check.checked });
      await load();
    } catch (error) {
      toast(error.message, "alarm");
      check.checked = done;
      check.disabled = false;
    }
  };
  row.appendChild(check);
  const body = el("div", "item-body");
  body.appendChild(el("div", "task-text", esc(t.text)));
  const meta = el("div", "task-meta");
  if (t.src) meta.appendChild(el("span", "pill", esc(t.src)));
  if (t.termin) meta.appendChild(el("span", `pill${t.overdue ? " alarm" : ""}`, `termin ${esc(t.termin)}`));
  body.appendChild(meta);
  row.appendChild(body);
  return row;
}

function renderTodo() {
  const host = $("#todo-list");
  if (!host) return;
  host.innerHTML = "";

  const items = [];
  (blockData("klienci")?.all || []).forEach((c) =>
    (c.todos || []).forEach((t) => items.push({ ...t, file: c.file, src: c.name })));
  (blockData("biznes")?.all || []).forEach((b) =>
    (b.todos || []).forEach((t) => items.push({ ...t, file: b.file, src: b.name })));

  const open = items.filter((t) => !t.done);
  const badge = $("#badge-todo");
  if (badge) { badge.textContent = open.length || ""; badge.classList.toggle("on", open.length > 0); }

  if (!items.length) {
    host.appendChild(el("div", "empty", "Brak zadań. Dodawaj je w plikach klientów i biznesu w sejfie."));
    return;
  }

  const groups = [
    ["Po terminie", (t) => !t.done && t.overdue],
    ["Zaplanowane", (t) => !t.done && t.termin && !t.overdue],
    ["Bez terminu", (t) => !t.done && !t.termin],
    ["Zrobione", (t) => t.done],
  ];
  groups.forEach(([title, pred]) => {
    const rows = items.filter(pred).sort((a, b) => (a.termin || "9999").localeCompare(b.termin || "9999"));
    if (!rows.length) return;
    host.appendChild(el("div", "group-head", `${title} · ${rows.length}`));
    rows.forEach((t) => host.appendChild(todoRowFull(t)));
  });
}

/* ── kalendarz (z danych panelu) ───────────────────────────────────────── */
function ymd(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}
function parseYmd(ds) {
  const [y, m, d] = String(ds).split("-").map(Number);
  return new Date(y, (m || 1) - 1, d || 1);
}

/** Zbiera wszystko, co ma datę, z bloków panelu w mapę dzień -> [zdarzenia]. */
function calEvents() {
  const map = {};
  const add = (date, label, tone) => {
    if (!date) return;
    (map[date] = map[date] || []).push({ label, tone });
  };
  (blockData("klienci")?.all || []).forEach((c) => {
    (c.projekty || []).forEach((p) => {
      if (p.deadline) add(p.deadline, `${c.name}: ${p.name}`, p.overdue ? "alarm" : "info");
    });
    (c.todos || []).forEach((t) => {
      if (t.termin && !t.done) add(t.termin, `${c.name}: ${t.text}`, t.overdue ? "alarm" : "warn");
    });
  });
  (blockData("biznes")?.all || []).forEach((b) => {
    if (b.deadline) add(b.deadline, b.name, b.overdue ? "alarm" : "info");
    (b.todos || []).forEach((t) => {
      if (t.termin && !t.done) add(t.termin, `${b.name}: ${t.text}`, t.overdue ? "alarm" : "warn");
    });
  });
  Object.values(blockData("pozyskiwanie")?.by_stage || {}).flat().forEach((it) => {
    if (it.follow_up) add(it.follow_up, `Follow-up: ${it.title}`, it.follow_up_overdue ? "alarm" : "warn");
  });
  const kasa = blockData("kasa");
  (kasa?.transactions || []).forEach((t) => add(t.date, `Wpłata: ${t.who} (${zl(t.amount)})`, "ok"));
  (kasa?.pending || []).forEach((p) => add(p.date, `Faktura: ${p.who} (${zl(p.amount)})`, "warn"));
  return map;
}

const CAL_WD = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nd"];

function buildMonth(host, events, compact) {
  if (!host) return;
  host.innerHTML = "";
  const cur = state.calCursor || new Date();
  const y = cur.getFullYear(), m = cur.getMonth();
  const startDow = (new Date(y, m, 1).getDay() + 6) % 7;   // poniedziałek = 0
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const prevDays = new Date(y, m, 0).getDate();
  const todayStr = ymd(new Date());

  const head = el("div", "cal-head");
  const mk = (glyph, fn) => { const b = el("button", "cal-nav", glyph); b.onclick = fn; return b; };
  head.appendChild(mk("‹", () => setCal(new Date(y, m - 1, 1))));
  head.appendChild(el("div", "cal-title", esc(cur.toLocaleDateString("pl-PL", { month: "long", year: "numeric" }))));
  head.appendChild(mk("dziś", () => setCal(new Date())));
  head.appendChild(mk("›", () => setCal(new Date(y, m + 1, 1))));
  host.appendChild(head);

  const grid = el("div", `cal-grid${compact ? " compact" : ""}`);
  CAL_WD.forEach((w) => grid.appendChild(el("div", "cal-wd", w)));
  for (let i = 0; i < startDow; i++) {
    grid.appendChild(el("div", "cal-day out", `<span class="cal-num">${prevDays - startDow + 1 + i}</span>`));
  }
  for (let d = 1; d <= daysInMonth; d++) {
    const ds = `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
    const evs = events[ds] || [];
    const cell = el("div", `cal-day${ds === todayStr ? " today" : ""}${ds === state.calSelected ? " sel" : ""}`);
    cell.appendChild(el("span", "cal-num", String(d)));
    if (evs.length && compact) {
      const dots = el("div", "cal-dots");
      evs.slice(0, 4).forEach((e) => dots.appendChild(el("span", `cal-dot ${e.tone}`, "")));
      cell.appendChild(dots);
    } else if (evs.length) {
      evs.slice(0, 3).forEach((e) => cell.appendChild(el("div", `cal-ev ${e.tone}`, esc(clip(e.label, 24)))));
      if (evs.length > 3) cell.appendChild(el("div", "cal-more", `+${evs.length - 3} więcej`));
    }
    cell.onclick = () => { state.calSelected = ds; refreshCalendars(); };
    grid.appendChild(cell);
  }
  host.appendChild(grid);
}

function calDayList(host, ds, events) {
  if (!host) return;
  host.innerHTML = "";
  if (!ds) { host.appendChild(el("div", "empty", "Kliknij dzień, żeby zobaczyć, co na niego przypada.")); return; }
  const evs = events[ds] || [];
  const label = parseYmd(ds).toLocaleDateString("pl-PL", { weekday: "long", day: "numeric", month: "long" });
  if (!evs.length) { host.appendChild(el("div", "empty", `${label} - nic zaplanowane.`)); return; }
  evs.forEach((e) => {
    const item = el("div", `item ${e.tone}`);
    item.appendChild(el("span", `sev-label sev-${e.tone}`, SEV_LABEL[e.tone] || ""));
    item.appendChild(el("div", "item-body", `<div class="item-title">${esc(e.label)}</div>`));
    host.appendChild(item);
  });
}

function calUpcoming(host, events) {
  if (!host) return;
  host.innerHTML = "";
  const todayStr = ymd(new Date());
  const rows = [];
  Object.keys(events).filter((d) => d >= todayStr).sort().forEach((d) =>
    events[d].forEach((e) => rows.push({ date: d, ...e })));
  if (!rows.length) { host.appendChild(el("div", "empty", "Nic nadchodzącego.")); return; }
  rows.slice(0, 8).forEach((e) => {
    const item = el("div", `item ${e.tone}`);
    const when = e.date === todayStr ? "dziś" : parseYmd(e.date).toLocaleDateString("pl-PL", { day: "numeric", month: "short" });
    item.appendChild(el("span", "cal-when", esc(when)));
    item.appendChild(el("div", "item-body", `<div class="item-title">${esc(clip(e.label, 40))}</div>`));
    host.appendChild(item);
  });
}

function setCal(date) { state.calCursor = date; refreshCalendars(); }

function refreshCalendars() {
  if (!state.data) return;
  const ev = calEvents();
  buildMonth($("#dzis-cal"), ev, true);
  buildMonth($("#kal-grid"), ev, false);
  calDayList($("#dzis-cal-day"), state.calSelected, ev);
  calDayList($("#kal-day"), state.calSelected || ymd(new Date()), ev);
  calUpcoming($("#kal-upcoming"), ev);
}

/* ── podgląd pozycji ───────────────────────────────────────────────────── */
function renderMarkdown(text) {
  const lines = esc(text).split("\n");
  const out = [];
  let quote = [];

  const flushQuote = () => {
    if (quote.length) {
      const html = quote.join("<br>").replace(/(<br>\s*){2,}/g, "<br><br>");
      out.push(`<blockquote>${html}</blockquote>`);
      quote = [];
    }
  };

  lines.forEach((raw) => {
    const line = raw.trimEnd();
    if (line.startsWith("&gt;")) {
      const content = line.slice(4).trim();
      quote.push(content || "<br>");
      return;
    }
    flushQuote();
    if (line.trim()) out.push(`<p>${line}</p>`);
  });
  flushQuote();

  return out
    .join("")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/`{1,3}([^`]+)`{1,3}/g, "<code>$1</code>")
    .replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, label) => label || target)
    .replace(/(https?:\/\/[^\s<)]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
}

function openSheet(kind, title, metaPills) {
  $("#sheet-kind").textContent = kind;
  $("#sheet-title").textContent = title;
  const meta = $("#sheet-meta");
  meta.innerHTML = "";
  (metaPills || []).forEach((pill) => {
    if (pill) meta.appendChild(el("span", `pill ${pill.tone || ""}`, esc(pill.text)));
  });
  $("#sheet-move").innerHTML = "";
  $("#sheet-body").innerHTML = "";
  $("#overlay").hidden = false;
  document.body.style.overflow = "hidden";
}

function closeSheet() {
  $("#overlay").hidden = true;
  document.body.style.overflow = "";
  state.openKey = null;
}

/* ── czat ──────────────────────────────────────────────────────────────── */
const chat = { socket: null, busy: false, bubble: null, buffer: "", cost: 0, info: null, limit: null };

const CHAT_SUGGESTIONS = [
  "Co mam dzisiaj do zrobienia z klientami i lejkiem",
  "Który lead w lejku stoi najdłużej bez ruchu",
  "Przygotuj follow-up do firm, którym mija termin",
  "Podsumuj, u których klientów zbliżają się deadline'y",
];

function renderChatUsage() {
  const parts = [];
  if (chat.limit) {
    const label = chat.limit.window === "five_hour" ? "limit 5h" : `limit ${chat.limit.window || ""}`;
    const ok = chat.limit.status === "allowed" && !chat.limit.using_overage;
    parts.push(`${label}: ${ok ? "ok" : esc(chat.limit.status || "?")}`);
    if (chat.limit.using_overage) parts.push("poza pakietem");
  }
  if (chat.cost) parts.push(`zużycie ≈ ${chat.cost.toFixed(2)} USD`);
  $("#chat-cost").textContent = parts.join(" · ");
  $("#chat-cost").title =
    "Rozmowa idzie z Twojej subskrypcji, nie po API. Kwota to wycena zużycia, nie rachunek.";
}

function chatScrolledToBottom() {
  const log = $("#chat-log");
  return log.scrollHeight - log.scrollTop - log.clientHeight < 80;
}

function chatScroll(force) {
  const log = $("#chat-log");
  if (force || chatScrolledToBottom()) log.scrollTop = log.scrollHeight;
}

function addRow(who, cls) {
  $("#chat-empty")?.remove();
  const row = el("div", `msg-row ${cls === "me" ? "me" : ""}`);
  const bubble = el("div", `bubble ${cls}`);
  if (who) bubble.appendChild(el("div", "msg-who", esc(who)));
  row.appendChild(bubble);
  $("#chat-log").appendChild(row);
  return bubble;
}

async function initChat() {
  if (chat.info) return;
  const info = await api("/api/chat/info").catch(() => ({ enabled: false, reason: "serwer nie odpowiada" }));
  chat.info = info;

  if (!info.enabled) {
    $("#chat-log").innerHTML = `<div class="empty">${esc(info.reason || "Czat niedostępny")}</div>`;
    $("#chat-state").textContent = "niedostępny";
    $("#chat-state").className = "term-state off";
    $("#chat-send").disabled = true;
    $("#chat-text").disabled = true;
    return;
  }

  const blocked = info.disallowed_tools || [];
  $("#chat-scope").textContent = blocked.length
    ? `${info.permission_mode} · ${blocked.length} ${plural(blocked.length, "narzędzie zablokowane", "narzędzia zablokowane", "narzędzi zablokowanych")}`
    : `pełny dostęp · powłoka i pliki`;
  $("#chat-scope").title = blocked.length
    ? `Zablokowane: ${blocked.join(", ")}`
    : "Czat może to samo, co sesja w VS Code. Zawęzisz w dashboard.config.yaml → chat.disallowed_tools";

  const box = $("#chat-suggest");
  if (box) {
    CHAT_SUGGESTIONS.forEach((text) => {
      const chip = el("button", "chat-chip", esc(text));
      chip.type = "button";
      chip.onclick = () => {
        $("#chat-text").value = text;
        sendChat();
      };
      box.appendChild(chip);
    });
  }

  connectChat();
}

function connectChat() {
  if (chat.socket?.readyState === WebSocket.OPEN) return;
  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  const socket = new WebSocket(`${proto}//${location.host}/ws/chat`);
  chat.socket = socket;

  const setState = (text, tone) => {
    $("#chat-state").textContent = text;
    $("#chat-state").className = `term-state ${tone || ""}`;
  };
  setState("łączę…", "");

  socket.onopen = () => setState("gotowy", "on");
  socket.onclose = () => {
    setState("rozłączony", "off");
    chat.busy = false;
    $("#chat-send").disabled = false;
  };
  socket.onerror = () => setState("błąd połączenia", "off");
  socket.onmessage = (event) => handleChatEvent(JSON.parse(event.data));
}

function handleChatEvent(msg) {
  switch (msg.type) {
    case "start":
      chat.bubble = addRow("Claude", "claude");
      chat.buffer = "";
      chat.typing = el("div", "chat-typing", "myśli…");
      chat.bubble.appendChild(chat.typing);
      chatScroll(true);
      break;

    case "tool": {
      chat.typing?.remove();
      chat.typing = null;
      const line = el("div", "tool-line");
      line.appendChild(el("span", "tn", esc(msg.name)));
      if (msg.detail) line.appendChild(el("span", "", esc(msg.detail)));
      chat.bubble?.appendChild(line);
      chatScroll();
      break;
    }

    case "delta":
      chat.typing?.remove();
      chat.typing = null;
      chat.buffer += msg.text;
      if (!chat.textNode) {
        chat.textNode = el("div", "md", "");
        chat.bubble?.appendChild(chat.textNode);
      }
      chat.textNode.innerHTML = renderMarkdown(chat.buffer);
      chatScroll();
      break;

    case "done":
      chat.typing?.remove();
      if (!chat.buffer && msg.text) {
        chat.textNode = chat.textNode || el("div", "md", "");
        chat.bubble?.appendChild(chat.textNode);
        chat.textNode.innerHTML = renderMarkdown(msg.text);
      }
      if (msg.cost_usd) {
        chat.cost += msg.cost_usd;
        renderChatUsage();
      }
      chat.textNode = null;
      chatScroll();
      break;

    case "error": {
      chat.typing?.remove();
      const box = chat.bubble || addRow("Claude", "claude");
      box.appendChild(el("div", "item-detail", `Błąd: ${esc(msg.text)}`));
      chatScroll(true);
      break;
    }

    case "idle":
      chat.busy = false;
      $("#chat-send").disabled = false;
      $("#chat-text").focus();
      break;

    case "limit":
      chat.limit = msg;
      renderChatUsage();
      break;

    case "reset_ok":
      $("#chat-log").innerHTML = "";
      chat.cost = 0;
      renderChatUsage();
      toast("Nowa rozmowa");
      break;
  }
}

function sendChat() {
  const field = $("#chat-text");
  const text = field.value.trim();
  if (!text || chat.busy) return;
  if (chat.socket?.readyState !== WebSocket.OPEN) {
    toast("Brak połączenia z serwerem", "alarm");
    return;
  }

  addRow("Ty", "me").appendChild(el("div", "md", renderMarkdown(text)));
  chat.socket.send(JSON.stringify({ type: "message", text }));
  field.value = "";
  field.style.height = "auto";
  chat.busy = true;
  $("#chat-send").disabled = true;
  chatScroll(true);
}

/* ── terminal ──────────────────────────────────────────────────────────── */
const term = { xterm: null, fit: null, socket: null, ready: false };

function setTermState(text, tone) {
  const node = $("#term-state");
  node.textContent = text;
  node.className = `term-state ${tone || ""}`;
  const badge = $("#badge-terminal");
  badge.textContent = tone === "on" ? "●" : "";
  badge.classList.toggle("on", tone === "on");
}

async function initTerminal() {
  if (term.xterm) return;

  const info = await api("/api/terminal/info").catch(() => ({ enabled: false, reason: "serwer nie odpowiada" }));
  if (!info.enabled) {
    $("#term-host").innerHTML = `<div class="empty">${esc(info.reason || "Terminal niedostępny")}</div>`;
    setTermState("niedostępny", "off");
    $("#term-connect").disabled = true;
    $("#term-restart").disabled = true;
    return;
  }
  $("#term-cmd").textContent = info.command;

  term.xterm = new Terminal({
    fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace',
    fontSize: 13,
    lineHeight: 1.25,
    cursorBlink: true,
    theme: {
      background: "#0E0F12",
      foreground: "#F2F1EC",
      cursor: "#E2C96A",
      selectionBackground: "#33363E",
      black: "#0E0F12", brightBlack: "#5A5C64",
      red: "#E08472", brightRed: "#E08472",
      green: "#6FBE9A", brightGreen: "#6FBE9A",
      yellow: "#E2C96A", brightYellow: "#E2C96A",
      blue: "#8CB4E0", brightBlue: "#8CB4E0",
      magenta: "#C69AD6", brightMagenta: "#C69AD6",
      cyan: "#7FC7C7", brightCyan: "#7FC7C7",
      white: "#F2F1EC", brightWhite: "#FFFFFF",
    },
  });
  term.fit = new FitAddon.FitAddon();
  term.xterm.loadAddon(term.fit);
  term.xterm.open($("#term-host"));
  fitTerminal();

  term.xterm.onData((data) => {
    if (term.socket?.readyState === WebSocket.OPEN) {
      term.socket.send(JSON.stringify({ type: "input", data }));
    }
  });

  connectTerminal();
}

function fitTerminal() {
  if (!term.fit || $("#panel-terminal").classList.contains("is-active") === false) return;
  try {
    term.fit.fit();
  } catch (error) {
    return;
  }
  if (term.socket?.readyState === WebSocket.OPEN) {
    term.socket.send(JSON.stringify({
      type: "resize",
      rows: term.xterm.rows,
      cols: term.xterm.cols,
    }));
  }
}

function connectTerminal() {
  if (!term.xterm || term.socket?.readyState === WebSocket.OPEN) return;
  setTermState("łączę…", "");

  const proto = location.protocol === "https:" ? "wss:" : "ws:";
  const socket = new WebSocket(`${proto}//${location.host}/ws/terminal`);
  term.socket = socket;

  socket.onopen = () => {
    setTermState("połączony", "on");
    fitTerminal();
    term.xterm.focus();
  };
  socket.onmessage = (event) => term.xterm.write(event.data);
  socket.onclose = (event) => {
    setTermState("rozłączony", "off");
    const why = event.reason ? ` (${event.reason})` : "";
    term.xterm.write(`\r\n\x1b[90m— sesja zakończona${why} —\x1b[0m\r\n`);
  };
  socket.onerror = () => setTermState("błąd połączenia", "off");
}

function restartTerminal() {
  if (term.socket && term.socket.readyState <= WebSocket.OPEN) term.socket.close();
  term.xterm?.clear();
  setTimeout(connectTerminal, 350);
}

/* ── start ─────────────────────────────────────────────────────────────── */
$("#term-connect").onclick = connectTerminal;
$("#term-restart").onclick = restartTerminal;

$("#chat-form").addEventListener("submit", (event) => {
  event.preventDefault();
  sendChat();
});
$("#chat-reset").onclick = () => {
  if (chat.socket?.readyState === WebSocket.OPEN) chat.socket.send(JSON.stringify({ type: "reset" }));
};
$("#chat-text").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChat();
  }
});
$("#chat-text").addEventListener("input", (event) => {
  const field = event.target;
  field.style.height = "auto";
  field.style.height = `${Math.min(field.scrollHeight, 180)}px`;
});
$("#health-summary").onclick = () => toggleHealth();
$("#sheet-close").onclick = closeSheet;
$("#overlay").onclick = (event) => {
  if (event.target === $("#overlay")) closeSheet();
};
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !$("#overlay").hidden) closeSheet();
});
$("#btn-refresh").onclick = () => load(false);
$("#btn-force").onclick = async () => {
  toast("Pobieram świeże dane…");
  await load(true);
};
initTabs();
load();
setInterval(() => load(false), 300000);

window.addEventListener("resize", () => {
  clearTimeout(window._rt);
  window._rt = setTimeout(fitTerminal, 200);
});
