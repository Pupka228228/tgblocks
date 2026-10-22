/* One bot, three pictures of it.
 *
 * Every editor page (nodes.html, blocks.html, text.html) loads this module: it
 * owns the single project document behind all of them, so an edit made in one
 * view shows up in the others instead of being reset on the next switch.
 *
 * The document lives on the server as {rev, text, layout}:
 *   text   - the bot itself, in the text syntax: the only source of truth
 *   layout - where the blocks sit on the canvas (never invalidates a view)
 *   rev    - bumped on every text change; editors poll it to notice each other
 *
 * A save carries the revision it was based on. If another view saved in the
 * meantime the server refuses it (conflict) and this module reloads the fresh
 * text, so two open views can never silently overwrite each other.
 */
(function (global) {
  "use strict";

  var NAME_KEY = "tgblocks.bot";
  var POLL_MS = 1200;
  var SAVE_MS = 700;

  var state = {
    name: "",
    rev: 0,
    text: "",
    layout: {},
    draft: null,      // the node canvas as the user left it (may be unfinished)
    dirty: false,     // local changes waiting to be sent
    busy: false,      // a save is in flight
    editing: false    // the user is mid-gesture: never reload underneath them
  };

  var saveTimer = null;
  var pending = null;
  var pollTimer = null;
  var reloadHook = null;
  var statusHook = null;

  function currentName() {
    return global.localStorage.getItem(NAME_KEY) || "bot1";
  }

  function setName(name) {
    state.name = name;
    global.localStorage.setItem(NAME_KEY, name);
  }

  function status(text, kind) {
    if (statusHook) { statusHook(text, kind); }
  }

  function projectUrl(name) {
    return "/api/project?name=" + encodeURIComponent(name || state.name);
  }

  // ------------------------------------------------------------------ loading
  async function load(name) {
    var target = name || currentName();
    var response = await fetch(projectUrl(target));
    var data = await response.json();
    if (!data.ok) { throw new Error(data.error || "не удалось открыть бота"); }
    setName(data.name || target);
    state.rev = data.rev || 0;
    state.text = data.text || "";
    state.layout = data.layout || {};
    state.draft = data.draft || null;
    state.dirty = false;
    pending = null;
    clearTimeout(saveTimer);
    return {
      name: state.name, rev: state.rev, text: state.text,
      layout: state.layout, draft: state.draft
    };
  }

  // ------------------------------------------------------------------- saving
  function queue(payload) {
    pending = payload;
    state.dirty = true;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, SAVE_MS);
  }

  function saveText(text) {
    if (typeof text !== "string") { return; }
    // An empty string is a legitimate edit ("Очистить"): the server bumps the
    // revision and every other view forgets the bot too.
    queue({ text: text });
  }

  function saveBoard(board) {
    // The server turns the board into the shared text and keeps its positions.
    queue({
      nodes: {
        nodes: board.nodes, counter: board.counter,
        rootId: board.rootId, manual: board.manual
      }
    });
  }

  async function apply(data, note) {
    state.rev = data.rev;
    state.text = data.text;
    state.dirty = false;
    if (reloadHook) {
      await reloadHook({ rev: data.rev, text: data.text, draft: data.draft || null });
    }
    if (note) { status(note, "ok"); }
  }

  async function flush() {
    clearTimeout(saveTimer);
    if (!pending || !state.name) { return; }
    var payload = pending;
    pending = null;
    payload.baseRev = state.rev;
    state.busy = true;
    try {
      var response = await fetch(projectUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      var data = await response.json();
      if (data.ok) {
        state.rev = data.rev;
        state.text = data.text;
        if (data.incomplete) {
          // A half-built canvas: it is kept as a draft, the bot text is not a
          // bot yet, so stay dirty and say nothing alarming.
          state.dirty = true;
          status("Доска сохранена черновиком: для бота нужен токен и событие.");
          return;
        }
        state.dirty = false;
        return;
      }
      if (data.conflict) {
        await apply(data, "Бот изменён в другом виде - показал свежую версию.");
        return;
      }
      if (data.incomplete) {
        state.dirty = true;
        status(data.error || "доска ещё не собрана в бота");
        return;
      }
      if (data.lossy) {
        // This view cannot express part of the bot: refuse quietly-but-clearly
        // and stop polling from reloading the canvas over the user's work.
        state.dirty = true;
        status(data.error, "error");
        return;
      }
      state.dirty = false;
      status(data.detail || data.error || "не сохранилось", "error");
    } catch (error) {
      // The edit stays in the editor; the next change retries the save.
      state.dirty = true;
      status("Нет связи с сервером: " + error, "error");
    } finally {
      state.busy = false;
    }
  }

  // -------------------------------------------------------------- live reload
  async function poll() {
    if (!state.name || state.busy || state.dirty || state.editing) { return; }
    try {
      var response = await fetch("/api/rev?name=" + encodeURIComponent(state.name));
      var data = await response.json();
      if (!data.ok || data.rev === state.rev) { return; }
      var fresh = await load(state.name);
      await apply(fresh, "Показал версию из другого вида.");
    } catch (error) {
      /* server is gone: stay quiet and keep working locally */
    }
  }

  function startPolling() {
    if (pollTimer) { return; }
    pollTimer = setInterval(poll, POLL_MS);
  }

  // ------------------------------------------------------------- page leaving
  function flushForUnload() {
    // Called from pagehide/beforeunload: the pending edit must reach the server
    // even though this page is about to disappear.
    clearTimeout(saveTimer);
    if (!pending || !state.name) { return; }
    var payload = pending;
    pending = null;
    payload.baseRev = state.rev;
    var body = JSON.stringify(payload);
    var url = projectUrl();
    try {
      if (global.navigator.sendBeacon && global.navigator.sendBeacon(url, body)) { return; }
    } catch (error) { /* fall through to a keepalive fetch */ }
    try {
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
        keepalive: true
      });
    } catch (error) { /* nothing else can be done while unloading */ }
  }

  // --------------------------------------------------------------------- hooks
  function configure(options) {
    options = options || {};
    reloadHook = options.reload || null;
    statusHook = options.status || null;
    if (!options.manualPolling) { startPolling(); }
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") { flushForUnload(); }
  });
  global.addEventListener("pagehide", flushForUnload);

  global.TgProject = {
    configure: configure,
    load: load,
    saveText: saveText,
    saveBoard: saveBoard,
    flush: flush,
    poll: poll,
    setName: setName,
    currentName: currentName,
    setEditing: function (value) { state.editing = !!value; },
    getState: function () {
      return {
        name: state.name, rev: state.rev, text: state.text,
        draft: state.draft, dirty: state.dirty
      };
    }
  };
})(window);
