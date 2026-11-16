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
// The guide's worked examples and the dates accepted, as the API last gave them (SPEC, S16). They are asked for each
// time Help or a "How this is calculated" panel opens; a language switch rewrites the text from these without asking
// again.
let guide = null;
let guideRequest = 0;
// Help: one section per feature (SPEC, S15), each with the worked examples it shows, by their role in /api/guide.
const HELP = [
  ["range", ["total"]], ["business", ["weekend", "business"]], ["own", ["own"]], ["reversed", ["reversed"]],
  ["past", []], ["elections", []], ["language", []], ["sources", []],
];
// The field each refused value came from, by the API's name for it (SPEC, E1).
const FIELDS = { start: "start", end: "end", day: "new-day", calendar: "calendar" };

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

function element(tag, className, text) {
  const made = document.createElement(tag);
  if (className) made.className = className;
  if (text !== undefined) made.textContent = text;
  return made;
}

function errorText(answer) {
  if (answer.status === 0) return t("error_network");
  const error = answer.body?.error;
  if (!error) return t("error_network");
  return t(`error_${error.code}`, { field: error.field ? t(`field_${error.field}`) : "" });
}

// The message shows beside the form its field belongs to, and that field is marked invalid and points to it.
function showError(text, field = null) {
  clearInvalid();
  const error = $("error");
  (field === "day" ? $("add-form") : $("count-form")).after(error);
  if (FIELDS[field]) {
    $(FIELDS[field]).setAttribute("aria-invalid", "true");
    $(FIELDS[field]).setAttribute("aria-describedby", "error");
  }
  error.textContent = text;
  error.hidden = false;
}

// A storage failure takes the count off the screen too: the message says no count is shown (SPEC, AC9).
function showFailure(answer) {
  if (answer.body?.error?.code === "storage") hideResult();
  showError(errorText(answer), answer.body?.error?.field);
}

function clearInvalid() {
  for (const id of Object.values(FIELDS)) {
    $(id).removeAttribute("aria-invalid");
    $(id).removeAttribute("aria-describedby");
  }
}

function clearError() {
  clearInvalid();
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

// A date's weekday, named by the browser in the page's language.
function weekday(day) {
  return new Intl.DateTimeFormat(language, { weekday: "long", timeZone: "UTC" }).format(new Date(`${day}T00:00:00Z`));
}

function exampleText(role) {
  const e = guide?.examples.find((example) => example.role === role);
  if (!e) return "";
  const known = e.known_answer;
  if (role === "total") {
    return t("example_total", {
      known, start: e.start, end: e.end, snc: e.total.start_not_counted, bc: e.total.both_counted,
    });
  }
  if (role === "weekend") {
    return t("example_weekend", {
      known, start: e.start, end: e.end, start_weekday: weekday(e.start), end_weekday: weekday(e.end),
      total_snc: e.total.start_not_counted, total_bc: e.total.both_counted,
      snc: e.business.start_not_counted, bc: e.business.both_counted,
    });
  }
  if (role === "own") {
    const day = e.own_holidays[0];
    return t("example_own", {
      known, day, weekday: weekday(day), start: e.start, end: e.end,
      snc: e.business.start_not_counted, bc: e.business.both_counted,
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

// Help: an introduction, the contents, then one section per feature: its text, a paragraph per blank line, and its
// worked examples once the API has counted them.
function renderGuide() {
  const contents = element("nav", "guide-contents");
  contents.setAttribute("aria-labelledby", "guide-contents-title");
  const contentsTitle = element("p", "guide-contents-title", t("help_contents"));
  contentsTitle.id = "guide-contents-title";
  const links = element("ol");
  const sections = [];
  for (const [id, roles] of HELP) {
    const title = t(`help_${id}_title`);
    const link = element("a", null, title);
    link.href = `#guide-${id}`;
    links.append(element("li"));
    links.lastChild.append(link);
    const section = element("section", "guide-section");
    section.id = `guide-${id}`;
    const heading = element("h3", null, title);
    heading.id = `guide-${id}-title`;
    section.setAttribute("aria-labelledby", heading.id);
    section.append(heading, ...t(`help_${id}`).split("\n\n").map((text) => element("p", "guide-text", text)));
    if (guide) {
      if (id === "range") section.append(element("p", "guide-example", t("help_range_dates", guide.dates)));
      for (const role of roles) section.append(element("p", "guide-example", exampleText(role)));
    }
    sections.push(section);
  }
  contents.append(contentsTitle, links);
  $("help-body").replaceChildren(element("p", "guide-intro", t("help_intro")), contents, ...sections);
  for (const [panel, role] of [["how-total", "total"], ["how-business", "business"]]) {
    $(panel).querySelector(".how-text").textContent = t(role === "total" ? "how_total" : "how_business");
    const example = $(panel).querySelector(".how-example");
    example.textContent = guide ? exampleText(role) : "";
    example.hidden = !guide;
  }
}

// Help and "How this is calculated" ask the API for the worked examples each time one of them opens (SPEC, S16).
async function openGuide() {
  const request = ++guideRequest;
  const answer = await api("GET", "/api/guide");
  if (request !== guideRequest) return;
  if (answer.status === 200) {
    guide = answer.body;
  } else {
    guide = null; // no example from an earlier opening stands in for one this opening could not count
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
    showError(errorText(answer), answer.body?.error?.field);
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
  const [catalog, stored, health] = await Promise.all([
    api("GET", "/api/calendars"),
    api("GET", "/api/language"),
    api("GET", "/api/status"),
  ]);
  calendars = catalog.status === 200 ? catalog.body.calendars : [];
  const storedLanguage = stored.status === 200 ? stored.body.language : null;
  language = LANGUAGES.includes(storedLanguage) ? storedLanguage : browserLanguage();
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
