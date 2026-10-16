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

function rgba(hex, alpha) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}

// Pastilla sólida (tipos del propio Pokémon) o suave (el resto), como en la ficha privada.
function pill(type, solid) {
  if (solid) {
    const node = el("span", "pill" + (type.dark ? " dark" : ""), type.label);
    node.style.background = type.color;
    return node;
  }
  const node = el("span", "pill soft", type.label);
  node.style.background = type.soft.background;
  node.style.borderColor = type.soft.border;
  return node;
}

function row(types, solid) {
  const node = el("div", "row");
  types.forEach((t) => node.appendChild(pill(t, solid)));
  return node;
}

function block(title, extra, className) {
  const node = el("div", "block" + (className ? " " + className : ""));
  const head = el("div", "section-line");
  head.appendChild(el("span", "section", title));
  if (extra) head.appendChild(extra);
  node.appendChild(head);
  return node;
}

function renderHead(card) {
  const head = el("div", "head");
  const tint = card.types.length ? card.types[0].color : "#8a90a3";
  head.style.background = `linear-gradient(180deg, ${rgba(tint, 0.2)}, ${rgba(tint, 0.04)})`;
  head.style.border = `1px solid ${rgba(tint, 0.28)}`;
  const header = el("div", "header");
  header.appendChild(el("span", "name", card.name));
  if (card.level) header.appendChild(el("span", "level", card.level));
  header.appendChild(el("span", "number", card.number));
  head.appendChild(header);
  head.appendChild(row(card.types, true));
  if (card.capture) {
    const capture = el("div", "capture" + (card.capture.color ? "" : " muted"));
    const text = el("span", "", card.capture.text);
    capture.appendChild(text);
    if (card.capture.color) {
      text.style.color = card.capture.color;
      const meter = el("div", "meter");
      const fill = el("span");
      fill.style.width = Math.min(100, card.capture.meter * 100) + "%";
      fill.style.background = card.capture.color;
      meter.appendChild(fill);
      capture.appendChild(meter);
    }
    head.appendChild(capture);
  }
  if (card.total) head.appendChild(el("div", "total", card.total));
  return head;
}

function renderCard(card) {
  const root = el("div", "card");
  root.appendChild(renderHead(card));

  if (card.versus) {
    const v = card.versus;
    const b = block(v.title, el("span", "pill verdict " + v.verdict.key, v.verdict.label), "versus " + v.verdict.key);
    [[card.labels.you, v.you], [card.labels.them, v.them]].forEach(([who, items]) => {
      const line = el("div", "line");
      line.appendChild(el("span", "who", who));
      const types = el("div", "row");
      items.forEach((t) => {
        const typed = el("span", "typed");
        typed.appendChild(pill(t));
        typed.appendChild(el("span", "mult " + t.tone, t.mult));
        types.appendChild(typed);
      });
      line.appendChild(types);
      b.appendChild(line);
    });
    v.notes.forEach((n) => b.appendChild(el("div", "note", n)));
    root.appendChild(b);
  }

  if (card.moves) {
    const b = block(card.moves.title);
    const grid = el("div", "moves");
    card.moves.items.forEach((m) => {
      grid.appendChild(pill(m.type));
      grid.appendChild(el("span", "", m.name));
      grid.appendChild(el("span", "mult " + m.tone, m.mult));
    });
    b.appendChild(grid);
    root.appendChild(b);
  }

  if (card.groups.length || card.ability_lines.length) {
    const b = block(card.labels.effects);
    card.groups.forEach((group) => {
      b.appendChild(el("div", "sub", group.title));
      group.rows.forEach((r) => {
        const line = el("div", "line");
        line.appendChild(el("span", "mult " + r.tone, r.mult));
        line.appendChild(row(r.types));
        b.appendChild(line);
      });
    });
    card.ability_lines.forEach((t) => b.appendChild(el("div", "note", t)));
    root.appendChild(b);
  }

  if (card.stats) {
    const b = block(card.stats.title);
    const grid = el("div", "stats");
    card.stats.rows.forEach((s) => {
      grid.appendChild(el("span", "label", s.label));
      grid.appendChild(el("span", "value" + (s.max ? " max" : ""), String(s.value)));
      const bar = el("div", "bar");
      const fill = el("span");
      fill.style.width = Math.min(100, (s.value / 255) * 100) + "%";
      fill.style.background = s.color;
      bar.appendChild(fill);
      grid.appendChild(bar);
    });
    grid.appendChild(el("span", "label sum", card.labels.total));
    grid.appendChild(el("span", "value sum", String(card.stats.total)));
    grid.appendChild(el("span", "sum"));
    b.appendChild(grid);
    root.appendChild(b);
  }

  if (card.evolution) {
    const b = block(card.evolution.title);
    const evo = el("div", "evo");
    card.evolution.stages.forEach((stage, i) => {
      if (i) evo.appendChild(el("span", "arrow", " → "));
      stage.forEach((s, j) => {
        if (j) evo.appendChild(el("span", "evo-stage", " / "));
        evo.appendChild(el("span", s.current ? "current" : "evo-stage", s.name));
        if (s.condition) evo.appendChild(el("span", "cond", ` (${s.condition})`));
      });
    });
    b.appendChild(evo);
    root.appendChild(b);
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
