// The page: every control calls the JSON API, and every string comes from strings.json, in English or Spanish.

const $ = (id) => document.getElementById(id);
const LANGUAGES = ["en", "es"];

let strings = {};
let language = "en";
let calendars = [];
let resultShown = false;
// Each count and each list request is numbered; an answer that is not the latest is out of date and not shown (F1).
let countRequest = 0;
let listRequest = 0;
// Language choices are stored one after another, in the order made, so the last choice made is the one kept; a
// choice overtaken before its turn is not sent, and only the latest choice's answer is shown.
let languageRequest = 0;
let languageStored = Promise.resolve();
// The guide's worked examples, as the API last counted them (SPEC, S16). They are asked for each time Help or a "How
// this is calculated" panel opens; a language switch rewrites the text from these without asking again.
let examples = null;
let guideRequest = 0;
// Help: one section per feature (SPEC, S15); three of them carry a worked example, by its role.
const HELP = [
  ["range", "total"], ["business", "business"], ["own"], ["reversed", "reversed"], ["past"], ["elections"],
  ["language"], ["demo"], ["sources"],
];

function t(key, values = {}) {
  const text = strings[language]?.[key];
  if (text === undefined) throw new Error(`missing string: ${language}.${key}`);
  return text.replace(/\{(\w+)\}/g, (_, name) => values[name] ?? "");
}

async function api(method, path, body) {
  const options = { method, headers: {} };
  if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }
  try {
    const response = await fetch(path, options);
    const text = await response.text();
    return { status: response.status, body: text ? JSON.parse(text) : null };
  } catch {
    return { status: 0, body: null };
  }
}

// The opening language when none is stored, or the stored one cannot be read (SPEC, Q16).
function browserLanguage() {
  const preferred = (navigator.languages?.[0] || navigator.language || "en").toLowerCase();
  return LANGUAGES.find((code) => preferred.startsWith(code)) || "en";
}

function errorText(answer) {
  if (answer.status === 0) return t("error_network");
  const error = answer.body?.error;
  if (!error) return t("error_network");
  return t(`error_${error.code}`, { field: error.field ? t(`field_${error.field}`) : "" });
}

function showError(text) {
  $("error").textContent = text;
  $("error").hidden = false;
}

// A storage failure takes the count off the screen too: the message says no count is shown (SPEC, AC9).
function showFailure(answer) {
  if (answer.body?.error?.code === "storage") hideResult();
  showError(errorText(answer));
}

function clearError() {
  $("error").hidden = true;
  $("error").textContent = "";
}

function calendarName(id) {
  return t(`calendar_${id}`);
}

function applyLanguage() {
  document.documentElement.lang = language;
  $("language").value = language;
  for (const element of document.querySelectorAll("[data-i18n]")) element.textContent = t(element.dataset.i18n);
  for (const element of document.querySelectorAll("[data-i18n-placeholder]")) {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  }
  document.title = t("title");
  renderOwnTitle();
  renderSources();
  renderGuide();
  for (const item of document.querySelectorAll("#own-list li")) {
    item.querySelector("button.remove").setAttribute("aria-label", t("remove_label", { day: item.dataset.day }));
  }
  if (resultShown) renderResultLabels();
}

function exampleText(role) {
  const e = examples?.find((example) => example.role === role);
  if (!e) return "";
  const known = e.known_answer;
  if (role === "total") {
    return t("example_total", {
      known, start: e.start, end: e.end, snc: e.total.start_not_counted, bc: e.total.both_counted,
    });
  }
  if (role === "business") {
    return t("example_business", {
      known, start: e.start, end: e.end, calendar: calendarName(e.calendar),
      mf_snc: e.monday_to_friday.start_not_counted, mf_bc: e.monday_to_friday.both_counted,
      excluded: e.excluded.join(", "), snc: e.business.start_not_counted, bc: e.business.both_counted,
    });
  }
  return t("example_reversed", {
    known, entered_start: e.entered.start, entered_end: e.entered.end, start: e.start, end: e.end,
  });
}

function renderGuide() {
  const list = document.createElement("dl");
  for (const [id, role] of HELP) {
    const term = document.createElement("dt");
    term.textContent = t(`help_${id}_title`);
    const text = document.createElement("dd");
    text.textContent = role && examples ? `${t(`help_${id}`)} ${exampleText(role)}` : t(`help_${id}`);
    list.append(term, text);
  }
  $("help-body").replaceChildren(list);
  for (const [panel, role] of [["how-total", "total"], ["how-business", "business"]]) {
    const formula = t(role === "total" ? "how_total" : "how_business");
    $(panel).querySelector(".how-text").textContent = examples ? `${formula} ${exampleText(role)}` : formula;
  }
}

// Help and "How this is calculated" ask the API for the worked examples each time one of them opens (SPEC, S16).
async function openGuide() {
  const request = ++guideRequest;
  const answer = await api("GET", "/api/guide");
  if (request !== guideRequest) return;
  if (answer.status === 200) {
    examples = answer.body.examples;
  } else {
    examples = null; // no example from an earlier opening stands in for one this opening could not count
    showError(errorText(answer));
  }
  renderGuide();
}

// One status message per count, in the page's language, for screen readers (SPEC, S14).
function announce() {
  const r = lastResult;
  const parts = [t("announce_result", {
    calendar: calendarName(r.calendar), start: r.start, end: r.end,
    total_snc: r.total.start_not_counted, total_bc: r.total.both_counted,
    business_snc: r.business.start_not_counted, business_bc: r.business.both_counted,
  })];
  if (r.swapped) parts.push(t("notice_swapped"));
  if (r.past_years) parts.push(t("notice_past_years"));
  $("announce").textContent = parts.join(" ");
}

function renderOwnTitle() {
  $("own-title").textContent = t("own_title", { name: calendarName($("calendar").value) });
}

function renderSources() {
  const list = $("sources-list");
  list.replaceChildren();
  for (const calendar of calendars) {
    const block = document.createElement("div");
    block.className = "calendar-sources";
    block.dataset.calendar = calendar.id;
    const heading = document.createElement("h3");
    heading.textContent = calendarName(calendar.id);
    const checked = document.createElement("p");
    checked.className = "checked";
    checked.textContent = t("checked", { date: calendar.checked });
    const items = document.createElement("ul");
    for (const source of calendar.sources) {
      const item = document.createElement("li");
      // The official title stays as published, in its own language; the words around it are the page's (Q21).
      const [before, after] = t(`source_${source.key.toLowerCase()}`, { title: "{title}" }).split("{title}");
      const link = document.createElement("a");
      link.href = source.url;
      link.textContent = source.title;
      item.append(before, link, `${after} (${t("retrieved", { date: source.retrieved })})`);
      items.append(item);
    }
    block.append(heading, checked, items);
    list.append(block);
  }
}

let lastResult = null;

function renderResultLabels() {
  $("active-calendar").textContent = t("active_calendar", { name: calendarName(lastResult.calendar) });
  $("range").textContent = t("range", { start: lastResult.start, end: lastResult.end });
  $("note-business-days").hidden = language !== "es";
  announce();
}

function renderResult(result) {
  lastResult = result;
  resultShown = true;
  $("total-snc").textContent = result.total.start_not_counted;
  $("total-bc").textContent = result.total.both_counted;
  $("business-snc").textContent = result.business.start_not_counted;
  $("business-bc").textContent = result.business.both_counted;
  $("notice-swapped").hidden = !result.swapped;
  $("notice-past-years").hidden = !result.past_years;
  $("note-local-elections").hidden = result.calendar !== "mx";
  renderResultLabels();
  $("result").hidden = false;
}

function hideResult() {
  resultShown = false;
  lastResult = null;
  $("result").hidden = true;
  $("announce").textContent = "";
}

async function count() {
  const request = ++countRequest;
  const query = new URLSearchParams({
    calendar: $("calendar").value,
    start: $("start").value.trim(),
    end: $("end").value.trim(),
  });
  const answer = await api("GET", `/api/count?${query}`);
  if (request !== countRequest) return;
  if (answer.status === 200) {
    clearError();
    renderResult(answer.body);
  } else {
    hideResult();
    showError(errorText(answer));
  }
}

async function loadHolidays() {
  const request = ++listRequest;
  const calendar = $("calendar").value;
  renderOwnTitle();
  const list = $("own-list");
  list.replaceChildren(); // no list stays on screen under another calendar's title
  $("own-empty").hidden = true;
  const answer = await api("GET", `/api/holidays?calendar=${calendar}`);
  if (request !== listRequest) return;
  if (answer.status !== 200) {
    showFailure(answer);
    return;
  }
  for (const day of answer.body.holidays) {
    const item = document.createElement("li");
    item.dataset.day = day;
    const label = document.createElement("span");
    label.textContent = day;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "remove";
    remove.dataset.i18n = "remove_button";
    remove.textContent = t("remove_button");
    remove.setAttribute("aria-label", t("remove_label", { day }));
    remove.addEventListener("click", () => removeHoliday(calendar, day));
    item.append(label, " ", remove);
    list.append(item);
  }
  $("own-empty").hidden = answer.body.holidays.length > 0;
}

async function afterListChange() {
  await loadHolidays();
  if (resultShown) await count();
}

async function addHoliday() {
  const answer = await api("POST", "/api/holidays", { calendar: $("calendar").value, day: $("new-day").value.trim() });
  if (answer.status === 201) {
    clearError();
    $("new-day").value = "";
    await afterListChange();
  } else {
    showFailure(answer);
  }
}

async function removeHoliday(calendar, day) {
  const answer = await api("DELETE", `/api/holidays/${calendar}/${day}`);
  if (answer.status === 204) {
    clearError();
    await afterListChange();
  } else {
    showFailure(answer);
  }
}

function switchLanguage(chosen) {
  const request = ++languageRequest;
  language = chosen;
  applyLanguage();
  languageStored = languageStored.then(async () => {
    if (request !== languageRequest) return;
    const answer = await api("PUT", "/api/language", { language: chosen });
    if (request !== languageRequest) return;
    if (answer.status === 200) clearError();
    else showError(t("error_language_not_stored"));
  });
}

async function start() {
  strings = await (await fetch("/static/strings.json")).json();
  const [config, catalog, stored, health] = await Promise.all([
    api("GET", "/api/config"),
    api("GET", "/api/calendars"),
    api("GET", "/api/language"),
    api("GET", "/api/status"),
  ]);
  calendars = catalog.status === 200 ? catalog.body.calendars : [];
  const storedLanguage = stored.status === 200 ? stored.body.language : null;
  language = LANGUAGES.includes(storedLanguage) ? storedLanguage : browserLanguage();
  $("demo-notice").hidden = !(config.status === 200 && config.body.live_demo);
  applyLanguage();
  if (health.status !== 200) showError(errorText(health)); // the database cannot be read: say so before any count

  $("count-form").addEventListener("submit", (event) => {
    event.preventDefault();
    count();
  });
  $("add-form").addEventListener("submit", (event) => {
    event.preventDefault();
    addHoliday();
  });
  $("calendar").addEventListener("change", afterListChange);
  $("language").addEventListener("change", () => switchLanguage($("language").value));
  for (const panel of ["help", "how-total", "how-business"]) {
    $(panel).addEventListener("toggle", () => {
      if ($(panel).open) openGuide();
    });
  }
  await loadHolidays();
  document.body.dataset.ready = "true";
}

start();
