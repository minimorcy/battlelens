// Ficha de BattleLens para OBS: consulta /state y dibuja las tarjetas (add-stream-mode D5).
// Todo el texto se inserta con textContent: nada del estado se interpreta como HTML.
// Sin textos propios: todos llegan traducidos en el estado (card.labels, add-english-ui D5).
"use strict";

const POLL_MS = 400;
const LEAVE_MS = 250;
const stage = document.getElementById("stage");
let lastSeq = -1;
let shown = false;

const params = new URLSearchParams(location.search);
const scale = Math.min(3, Math.max(0.5, parseFloat(params.get("scale")) || 1));
stage.style.transform = `scale(${scale})`;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

function pill(type) {
  const node = el("span", "pill" + (type.dark ? " dark" : ""), type.label);
  node.style.background = type.color;
  return node;
}

function row(types) {
  const node = el("div", "row");
  types.forEach((t) => node.appendChild(pill(t)));
  return node;
}

function renderCard(card) {
  const root = el("div", "card");
  const header = el("div", "header");
  header.appendChild(el("span", "name", card.name));
  if (card.level) header.appendChild(el("span", "level", card.level));
  header.appendChild(el("span", "number", card.number));
  root.appendChild(header);
  root.appendChild(row(card.types));

  if (card.capture) {
    const capture = el("div", "capture" + (card.capture.color ? "" : " muted"), card.capture.text);
    if (card.capture.color) capture.style.color = card.capture.color;
    root.appendChild(capture);
  }

  if (card.versus) {
    const v = card.versus;
    const title = el("div", "section-line");
    title.appendChild(el("span", "section", v.title));
    title.appendChild(el("span", "pill verdict " + v.verdict.key, v.verdict.label));
    root.appendChild(title);
    [[card.labels.you, v.you], [card.labels.them, v.them]].forEach(([who, types]) => {
      const line = el("div", "line");
      line.appendChild(el("span", "who", who));
      line.appendChild(row(types));
      root.appendChild(line);
    });
    v.notes.forEach((n) => root.appendChild(el("div", "note", n)));
  }

  if (card.moves) {
    root.appendChild(el("div", "section", card.moves.title));
    const grid = el("div", "moves");
    card.moves.items.forEach((m) => {
      grid.appendChild(pill(m.type));
      grid.appendChild(el("span", "", m.name));
      grid.appendChild(el("span", "mult " + m.tone, m.mult));
    });
    root.appendChild(grid);
  }

  card.groups.forEach((group) => {
    root.appendChild(el("div", "section", group.title));
    group.rows.forEach((r) => {
      const line = el("div", "line");
      line.appendChild(el("span", "who", r.mult));
      line.appendChild(row(r.types));
      root.appendChild(line);
    });
  });
  card.ability_lines.forEach((t) => root.appendChild(el("div", "note", t)));

  if (card.stats) {
    root.appendChild(el("div", "section", card.stats.title));
    const grid = el("div", "stats");
    card.stats.rows.forEach((s) => {
      grid.appendChild(el("span", "label", s.label));
      grid.appendChild(el("span", "value", String(s.value)));
      const bar = el("div", "bar");
      const fill = el("span");
      fill.style.width = Math.min(100, (s.value / 255) * 100) + "%";
      fill.style.background = s.color;
      bar.appendChild(fill);
      grid.appendChild(bar);
    });
    grid.appendChild(el("span", "label", card.labels.total));
    grid.appendChild(el("span", "value", String(card.stats.total)));
    root.appendChild(grid);
  } else if (card.total) {
    root.appendChild(el("div", "", card.total));
  }

  if (card.evolution) {
    root.appendChild(el("div", "section", card.evolution.title));
    root.appendChild(el("div", "", card.evolution.text));
  }
  return root;
}

function render(state) {
  stage.classList.toggle("competitive", state.mode === "competitive");
  if (!state.visible || !state.cards.length) {
    if (shown) {
      Array.from(stage.children).forEach((c) => c.classList.replace("enter", "leave"));
      setTimeout(() => { if (!shown) stage.replaceChildren(); }, LEAVE_MS);
    }
    shown = false;
    return;
  }
  stage.replaceChildren(...state.cards.map((c) => {
    const node = renderCard(c);
    node.classList.add("enter");
    return node;
  }));
  shown = true;
}

async function poll() {
  try {
    const response = await fetch("/state", { cache: "no-store" });
    if (response.ok) {
      const state = await response.json();
      if (state.seq !== lastSeq) {
        lastSeq = state.seq;
        render(state);
      }
    }
  } catch (err) {
    // BattleLens cerrado o reiniciándose: se reintenta en el siguiente ciclo.
  }
  setTimeout(poll, POLL_MS);
}

poll();
