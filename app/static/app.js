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
  if (resultShown) renderResultLabels();
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
      const link = document.createElement("a");
      link.href = source.url;
      link.textContent = source.title;
      item.append(link, ` (${t("retrieved", { date: source.retrieved })})`);
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
    $("own-empty").hidden = true;
    showError(errorText(answer));
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
    showError(errorText(answer));
  }
}

async function removeHoliday(calendar, day) {
  const answer = await api("DELETE", `/api/holidays/${calendar}/${day}`);
  if (answer.status === 204) {
    clearError();
    await afterListChange();
  } else {
    showError(errorText(answer));
  }
}

async function switchLanguage(chosen) {
  language = chosen;
  applyLanguage();
  const answer = await api("PUT", "/api/language", { language: chosen });
  if (answer.status === 200) clearError();
  else showError(t("error_language_not_stored"));
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
  await loadHolidays();
  document.body.dataset.ready = "true";
}

start();
