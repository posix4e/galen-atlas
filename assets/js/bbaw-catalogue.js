"use strict";

let records = [];
let query = "";
let activeFilter = "all";

const body = document.querySelector("#bbaw-table tbody");
const search = document.getElementById("bbaw-q");
const count = document.getElementById("bbaw-count");
const buttons = [...document.querySelectorAll(".controls button")];

function node(tag, className, text) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text !== undefined) result.textContent = text;
  return result;
}

function otherTranslations(record) {
  return Object.entries(record.translation_columns)
    .filter(([language, listed]) => language !== "english" && listed)
    .map(([language]) => language)
    .join(", ");
}

function addRow(record) {
  const row = document.createElement("tr");
  row.appendChild(node("td", "", record.id));
  const title = row.appendChild(node("td"));
  title.appendChild(node("strong", "", record.title));
  row.appendChild(node("td", "", record.kuhn || "—"));
  const english = record.translation_columns.english;
  const englishCell = row.appendChild(document.createElement("td"));
  if (english) {
    englishCell.appendChild(node("span", "chip full", "listed"));
  } else {
    englishCell.appendChild(node("span", "chip unknown", "column empty"));
  }
  row.appendChild(node("td", "bbaw-other", otherTranslations(record) || "—"));
  body.appendChild(row);
}

function apply() {
  const normalized = query.toLocaleLowerCase();
  const shown = records.filter((record) => {
    const hasEnglish = record.translation_columns.english;
    if (activeFilter === "english" && !hasEnglish) return false;
    if (activeFilter === "no-english" && hasEnglish) return false;
    const haystack = `${record.title} ${record.kuhn}`.toLocaleLowerCase();
    return !normalized || haystack.includes(normalized);
  });
  body.replaceChildren();
  shown.forEach(addRow);
  count.textContent = `${shown.length} of ${records.length} BBAW records shown.`;
}

buttons.forEach((button) => button.addEventListener("click", () => {
  activeFilter = button.dataset.f;
  buttons.forEach((item) => {
    const active = item === button;
    item.classList.toggle("on", active);
    item.setAttribute("aria-pressed", String(active));
  });
  apply();
}));

search.addEventListener("input", () => {
  query = search.value.trim();
  apply();
});

fetch("data/bbaw-galen-translations.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((catalogue) => {
    records = catalogue.records;
    document.getElementById("record-total").textContent = String(records.length);
    document.getElementById("english-total").textContent = String(
      records.filter((record) => record.translation_columns.english).length
    );
    document.getElementById("retrieved-on").textContent = catalogue.retrieved_on;
    apply();
  })
  .catch((error) => {
    count.textContent = `The BBAW snapshot could not be loaded (${error.message}). `;
    count.classList.add("error");
    const link = node("a", "", "Open the JSON snapshot directly.");
    link.href = "data/bbaw-galen-translations.json";
    count.appendChild(link);
  });
