"use strict";

const stats = {
  total: document.getElementById("s-total"),
  none: document.getElementById("s-none"),
  unknown: document.getElementById("s-unknown"),
  some: document.getElementById("s-some"),
};
const error = document.getElementById("stats-error");

fetch("data/works.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((documentData) => {
    if (documentData.schema_version !== 2 || !Array.isArray(documentData.works)) {
      throw new Error("Unsupported catalogue schema");
    }
    const count = (status) => documentData.works.filter((work) => work.english.status === status).length;
    stats.total.textContent = String(documentData.works.length);
    stats.none.textContent = String(count("none"));
    stats.unknown.textContent = String(count("unknown"));
    stats.some.textContent = String(count("full") + count("partial"));
  })
  .catch(() => {
    Object.values(stats).forEach((node) => {
      node.textContent = "—";
    });
    error.hidden = false;
  });
