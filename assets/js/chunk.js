"use strict";

const STATUS = {
  open: ["unknown", "untranslated — claim it"],
  claimed: ["unknown", "claimed — in progress"],
  draft: ["partial", "draft — awaiting reviewer"],
  reviewed: ["full", "reviewed"],
};
const main = document.getElementById("m");

function node(tag, className, text) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
}

function safeUrl(value) {
  try {
    const parsed = new URL(value, document.baseURI);
    return parsed.origin === location.origin || parsed.protocol === "https:" ? parsed.href : null;
  } catch {
    return null;
  }
}

function addLink(parent, label, href) {
  const safe = safeUrl(href);
  if (!safe) return false;
  const link = node("a", "", label);
  link.href = safe;
  parent.appendChild(link);
  return true;
}

function renderError(id) {
  main.replaceChildren();
  main.appendChild(node("h1", "", "Chunk not found"));
  main.appendChild(node("p", "error", `No translation packet called ${id || "(none)"} could be loaded.`));
  const paragraph = main.appendChild(node("p"));
  addLink(paragraph, "See the roadmap", "../roadmap.html");
  paragraph.append(" or ");
  addLink(paragraph, "browse the repository", "https://github.com/posix4e/pergamap");
  paragraph.append(".");
}

function render(packet) {
  main.replaceChildren();
  document.title = `${packet.id} — Pergamap`;
  main.appendChild(node("p", "crumb", `Chunk ${packet.id} · ${packet.work} · Kühn ${packet.kuhn_range || ""}`));
  const heading = node("h1", "", packet.title || packet.chapter_head || packet.id);
  heading.lang = "grc";
  main.appendChild(heading);
  const [statusClass, statusLabel] = STATUS[packet.status] || ["unknown", packet.status];
  const lead = main.appendChild(node("p", "lead"));
  lead.appendChild(node("span", `chip ${statusClass}`, statusLabel));
  const translator = packet.contributors && packet.contributors.translator;
  if (translator && translator.name) lead.append(` · ${translator.name}`);

  const warning = main.appendChild(node("div", "notice medical-warning"));
  warning.setAttribute("role", "note");
  warning.appendChild(node("p", "", "Historical text only — not medical advice. Ancient remedies may be toxic or unsafe; do not prepare or use them."));

  if (packet.status === "open") {
    const notice = main.appendChild(node("div", "notice"));
    const paragraph = notice.appendChild(node("p", "", "This chunk has prepared Greek but no translation. "));
    addLink(paragraph, "Claim it in an issue", "https://github.com/posix4e/pergamap/issues");
    paragraph.append(", then follow the ");
    addLink(paragraph, "harness guide", "https://github.com/posix4e/pergamap/blob/main/HARNESS.md");
    paragraph.append(".");
  }

  const latin = packet.witnesses && packet.witnesses.kuhn_latin;
  if (latin && latin.scan_url) {
    const witness = main.appendChild(node("p", "crumb", "Witness: Kühn's facing Latin — "));
    addLink(witness, "scan", latin.scan_url);
    witness.append(` (${latin.status}).`);
  }

  packet.segments.forEach((segment) => {
    const pair = main.appendChild(node("div", "pair"));
    const greek = pair.appendChild(node("div", "grc"));
    greek.lang = "grc";
    greek.appendChild(node("span", "kp", `[${segment.kuhn}] `));
    greek.append(segment.grc);
    const english = pair.appendChild(node("div", "eng"));
    if (segment.eng) english.append(segment.eng);
    else english.appendChild(node("span", "todo", "— not yet translated —"));
    if (segment.rationale) {
      const details = english.appendChild(node("details", "trace"));
      details.appendChild(node("summary", "", "Translation rationale"));
      details.appendChild(node("div", "", segment.rationale));
    }
    if (Array.isArray(segment.refs) && segment.refs.length) {
      english.appendChild(node("p", "seg-note", `Witnesses cited: ${segment.refs.join(" · ")}`));
    }
    if (segment.notes) english.appendChild(node("p", "seg-note", segment.notes));
  });

  if (Array.isArray(packet.notes) && packet.notes.length) {
    main.appendChild(node("h2", "", "Translator's notes"));
    const list = main.appendChild(node("ul", "notes"));
    packet.notes.forEach((note) => list.appendChild(node("li", "", note)));
  }
}

const id = new URLSearchParams(location.search).get("id");
if (!id || !/^[a-z0-9][a-z0-9-]*$/.test(id)) {
  renderError(id);
} else {
  fetch(`chunks/${encodeURIComponent(id)}.json`)
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    })
    .then((packet) => {
      if (packet.schema_version !== 2 || packet.id !== id || !Array.isArray(packet.segments)) throw new Error("Invalid packet");
      render(packet);
    })
    .catch(() => renderError(id));
}
