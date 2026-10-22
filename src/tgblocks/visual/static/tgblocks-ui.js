/* Settings shared by the three editors: theme and interface language.
 *
 * Every page loads this module before its own script, so a preference is applied
 * before the first paint and the same choice follows the user between /nodes,
 * /text and /blocks. The catalogue labels come from /api/schema already
 * translated; `TgUi.tr()` picks the right one for the current language.
 */
(function (global) {
  "use strict";

  var THEME_KEY = "tgblocks.theme";
  var LANG_KEY = "tgblocks.lang";

  var TEXT = {
    ru: {
      settings: "Настройки",
      theme: "Тема",
      dark: "тёмная",
      light: "светлая",
      language: "Язык",
      russian: "русский",
      english: "english",
      close: "Закрыть",
      note: "Выбор запоминается в этом браузере.",
      open: "Открыть файл…",
      clear: "Очистить",
      compile: "Собрать",
      snippets: "Вставить…",
      run: "▶ Запустить",
      stop: "■ Стоп",
      download: "Скачать .py",
      copy: "Копировать",
      view_nodes: "Вид: узлы",
      view_text: "Вид: текст",
      view_blocks: "Вид: блоки",
      tab_text: "Текст",
      tab_python: "Python (aiogram 3)",
      tab_logs: "Логи",
      page_nodes: "узлы",
      page_text: "текст",
      page_blocks: "блоки",
      title_nodes: "tgblocks - узлы",
      title_text: "tgblocks - текст",
      title_blocks: "tgblocks - блоки",
      status_ok_nodes: "OK · блоков: {blocks} · строк aiogram-кода: {lines}",
      status_ok_lines: "OK · строк aiogram-кода: {lines}",
      status_unlinked: " · не подключено: {count}",
      status_empty_nodes: "Пусто. Добавь блоки из меню слева.",
      status_compiled_empty: "Пусто. Перетащи блок «токен» из палитры."
    },
    en: {
      settings: "Settings",
      theme: "Theme",
      dark: "dark",
      light: "light",
      language: "Language",
      russian: "русский",
      english: "english",
      close: "Close",
      note: "The choice is remembered in this browser.",
      open: "Open file…",
      clear: "Clear",
      compile: "Compile",
      snippets: "Insert…",
      run: "▶ Run",
      stop: "■ Stop",
      download: "Download .py",
      copy: "Copy",
      view_nodes: "View: nodes",
      view_text: "View: text",
      view_blocks: "View: blocks",
      tab_text: "Text",
      tab_python: "Python (aiogram 3)",
      tab_logs: "Logs",
      page_nodes: "nodes",
      page_text: "text",
      page_blocks: "blocks",
      title_nodes: "tgblocks - nodes",
      title_text: "tgblocks - text",
      title_blocks: "tgblocks - blocks",
      status_ok_nodes: "OK · blocks: {blocks} · lines of aiogram code: {lines}",
      status_ok_lines: "OK · lines of aiogram code: {lines}",
      status_unlinked: " · not connected: {count}",
      status_empty_nodes: "Empty. Add blocks from the palette on the left.",
      status_compiled_empty: "Empty. Drag the “token” block from the palette."
    }
  };

  var LIGHT_CSS =
    ':root[data-theme="light"] {' +
    '--bg:#f4f6fb; --panel:#ffffff; --line:#d7dce8; --fg:#1a1e2b;' +
    '--muted:#5c6480; --accent:#3b6cf0; --ok:#1f8a55; --err:#c0392b;' +
    '--node:#ffffff;' +
    '--chip:#eef2fb; --chip-hover:#e2e8f7; --field:#ffffff;' +
    '--scroll:#c3cada; --log:#f7f9ff; --log-fg:#3b4360; --flyout:#eef1f8;' +
    '--tok-key:#7b3fd6; --tok-fn:#1f8a55; --tok-str:#b45309;' +
    '--tok-num:#2b5bd7; --tok-com:#7b839e; --tok-pun:#6b7280; }' +
    ':root[data-theme="light"] body { background:var(--bg); color:var(--fg); }' +
    ':root[data-theme="light"] header,' +
    ' :root[data-theme="light"] #palette,' +
    ' :root[data-theme="light"] aside {' +
    'background:var(--panel); }' +
    ':root[data-theme="light"] .pal-title, :root[data-theme="light"] .pal-hint,' +
    ' :root[data-theme="light"] .pal-item span,' +
    ' :root[data-theme="light"] .field-label {' +
    'color:var(--muted); }' +
    ':root[data-theme="light"] .port { border-color:#9aa4c0; color:#4b5563; }' +
    // Only the visible wire: the wide transparent hit area underneath must stay
    // invisible, otherwise every connection looks like a thick grey pipe.
    ':root[data-theme="light"] #wires path.wire { stroke:#9aa4c0; }' +
    ':root[data-theme="light"] #wires path.wire-hit { stroke:transparent; }' +
    ':root[data-theme="light"] .node,' +
    ' :root[data-theme="light"] .node-head,' +
    ' :root[data-theme="light"] .node-body {' +
    'background:var(--node); color:var(--fg); }' +
    ':root[data-theme="light"] .node { box-shadow:0 2px 10px rgba(20,30,60,.12); }' +
    ':root[data-theme="light"] .node-body input,' +
    ' :root[data-theme="light"] .node-body select {' +
    'background:var(--field); color:var(--fg); border-color:var(--line); }' +
    ':root[data-theme="light"] button:hover { background:var(--chip-hover); }' +
    ':root[data-theme="light"] #canvas { background:var(--bg); }' +
    ':root[data-theme="light"] .tab.active { color:var(--fg); }' +
    /* the settings panel itself */
    '#tg-settings { position:fixed; z-index:60; top:52px; right:14px; width:270px;' +
    'padding:12px; border:1px solid var(--line); border-radius:10px;' +
    'background:var(--panel); color:var(--fg); box-shadow:0 18px 40px rgba(0,0,0,.45);' +
    'font:13px/1.4 system-ui, "Segoe UI", sans-serif; }' +
    '#tg-settings h3 { margin:0 0 8px; font-size:13px; font-weight:600; }' +
    '#tg-settings .row { margin:0 0 10px; }' +
    '#tg-settings .row > span { display:block; margin:0 0 4px; color:var(--muted);' +
    'font-size:11px; text-transform:uppercase; letter-spacing:.04em; }' +
    '#tg-settings .choices { display:flex; gap:6px; flex-wrap:wrap; }' +
    '#tg-settings button { padding:5px 10px; border:1px solid var(--line);' +
    'border-radius:6px; background:transparent; color:var(--fg); cursor:pointer;' +
    'font:inherit; }' +
    '#tg-settings button.active { border-color:var(--accent); color:var(--accent); }' +
    '#tg-settings .note { color:var(--muted); font-size:11px; margin:8px 0 0; }' +
    '#tg-settings-close { float:right; padding:2px 8px; }';

  // English is the default so the tool opens in the language most people read
  // the README in; the choice is remembered per browser.
  var state = { theme: "dark", lang: "en" };

  function read() {
    try {
      var theme = global.localStorage.getItem(THEME_KEY);
      var lang = global.localStorage.getItem(LANG_KEY);
      if (theme === "light" || theme === "dark") { state.theme = theme; }
      if (lang === "en" || lang === "ru") { state.lang = lang; }
      // ?theme=light and ?lang=ru make the choice shareable (and testable) and
      // stick for the following pages.
      var query = new URLSearchParams(global.location.search);
      var forcedTheme = query.get("theme");
      var forcedLang = query.get("lang");
      if (forcedTheme === "light" || forcedTheme === "dark") {
        state.theme = forcedTheme;
        global.localStorage.setItem(THEME_KEY, forcedTheme);
      }
      if (forcedLang === "en" || forcedLang === "ru") {
        state.lang = forcedLang;
        global.localStorage.setItem(LANG_KEY, forcedLang);
      }
    } catch (error) { /* private mode: keep the defaults */ }
  }

  function write() {
    try {
      global.localStorage.setItem(THEME_KEY, state.theme);
      global.localStorage.setItem(LANG_KEY, state.lang);
    } catch (error) { /* private mode: the choice lasts one page */ }
  }

  function t(key) {
    var table = TEXT[state.lang] || TEXT.ru;
    return table[key] || TEXT.ru[key] || key;
  }

  // A translated line with {placeholders} filled in.
  function fmt(key, values) {
    var text = t(key);
    Object.keys(values || {}).forEach(function (name) {
      text = text.split("{" + name + "}").join(String(values[name]));
    });
    return text;
  }

  // Catalogue label / hint for the current language, with a graceful fallback.
  function tr(item) {    if (!item) { return ""; }
    if (state.lang === "en" && item.label_en) { return item.label_en; }
    return item.label || "";
  }

  function hint(item) {
    if (!item) { return ""; }
    if (state.lang === "en" && item.hint_en) { return item.hint_en; }
    return item.hint || "";
  }

  function choiceLabel(choice) {
    if (!choice) { return ""; }
    if (state.lang === "en" && choice.label_en) { return choice.label_en; }
    return choice.label || "";
  }

  function apply() {
    var root = document.documentElement;
    root.setAttribute("data-theme", state.theme);
    root.setAttribute("lang", state.lang);
    var elements = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < elements.length; i += 1) {
      var key = elements[i].getAttribute("data-i18n");
      var text = (TEXT[state.lang] || TEXT.ru)[key];
      if (text) { elements[i].textContent = text; }
    }
    var toggle = document.getElementById("tg-settings-button");
    if (toggle) { toggle.textContent = "\u2699 " + t("settings"); }
    if (typeof global.TgUiOnChange === "function") { global.TgUiOnChange(state); }
  }

  function panel() {
    var existing = document.getElementById("tg-settings");
    if (existing) { existing.remove(); return; }
    var box = document.createElement("div");
    box.id = "tg-settings";

    var title = document.createElement("h3");
    title.textContent = t("settings");
    var close = document.createElement("button");
    close.id = "tg-settings-close";
    close.textContent = "✕";
    close.title = t("close");
    close.addEventListener("click", function () { box.remove(); });
    title.appendChild(close);
    box.appendChild(title);

    box.appendChild(row(t("theme"), [["dark", t("dark")], ["light", t("light")]],
                        state.theme, function (value) {
      state.theme = value;
      write();
      apply();
      box.remove();
      panel();
    }));
    box.appendChild(row(t("language"), [["ru", t("russian")], ["en", t("english")]],
                        state.lang, function (value) {
      state.lang = value;
      write();
      apply();
      box.remove();
      if (typeof global.TgUiOnLanguage === "function") { global.TgUiOnLanguage(state); }
      panel();
    }));

    var note = document.createElement("p");
    note.className = "note";
    note.textContent = t("note");
    box.appendChild(note);
    document.body.appendChild(box);
  }

  function row(label, choices, current, onPick) {
    var wrap = document.createElement("div");
    wrap.className = "row";
    var caption = document.createElement("span");
    caption.textContent = label;
    wrap.appendChild(caption);
    var list = document.createElement("div");
    list.className = "choices";
    choices.forEach(function (pair) {
      var button = document.createElement("button");
      button.type = "button";
      button.textContent = pair[1];
      if (pair[0] === current) { button.className = "active"; }
      button.addEventListener("click", function () { onPick(pair[0]); });
      list.appendChild(button);
    });
    wrap.appendChild(list);
    return wrap;
  }

  function injectStyle() {
    var style = document.createElement("style");
    style.textContent = LIGHT_CSS;
    document.head.appendChild(style);
  }

  function injectButton() {
    var header = document.querySelector("header");
    if (!header || document.getElementById("tg-settings-button")) { return; }
    var button = document.createElement("button");
    button.id = "tg-settings-button";
    button.type = "button";
    button.textContent = t("settings");
    button.addEventListener("click", function (event) {
      event.stopPropagation();
      panel();
    });
    document.addEventListener("click", function (event) {
      var box = document.getElementById("tg-settings");
      if (box && !box.contains(event.target) && event.target.id !== "tg-settings-button") {
        box.remove();
      }
    });
    var links = header.querySelector("a");
    if (links) { header.insertBefore(button, links); } else { header.appendChild(button); }
  }

  function boot() {
    read();
    injectStyle();
    injectButton();
    apply();
  }

  // The preference is read as soon as this file loads: a page's own script runs
  // before DOMContentLoaded, and it asks TgUi.lang() while building its palette.
  read();
  try {
    document.documentElement.setAttribute("data-theme", state.theme);
    document.documentElement.setAttribute("lang", state.lang);
  } catch (error) { /* no document yet: boot() will do it */ }

  global.TgUi = {
    boot: boot,
    tr: tr,
    hint: hint,
    choiceLabel: choiceLabel,
    t: t,
    fmt: fmt,
    lang: function () { return state.lang; },
    theme: function () { return state.theme; }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);
