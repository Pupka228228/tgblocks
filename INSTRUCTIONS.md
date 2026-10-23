# ENGLISH

# Instruction: tgblocks - DSL + visual Telegram bot constructor

Step by step: from an empty folder to a working bot. Everything has been verified on this machine
(Windows, Python 3.13). Commands are for Windows; differences for Linux/macOS are noted.

---

## 0. What exists at all

| What | Where | Why |
| --- | --- | --- |
| scaffold.py | project root | project generator: run it -> get a ready package |
| tgblocks project | C:\TGBots\tgblocks\ | already ready, usable immediately |
| DSL files | *.tg | text you write yourself |
| Visual editor | tgblocks visual | browser: nodes, blocks, and text -> the same DSL |
| Generated code | *.py after tgblocks compile | ordinary aiogram 3, edited by hand |

There are now three inputs (nodes, blocks, text), one output: all of them turn into the same
Python code.

---

## 1. What you will need

- Python 3.10+ (check: python --version).
- A terminal (PowerShell will do).
- A bot token - issued by @BotFather in Telegram (section 4).
- Internet: for pip install, for the first Blockly load from the CDN, and for the bot itself
  (access to api.telegram.org).

---

## 2. Step 1 - create the project

The project is already created in C:\TGBots\tgblocks. If you want to start from scratch or in another folder:

cd C:\TGBots\tgblocks
python scaffold.py              # will create .\tgblocks
python scaffold.py mybot        # or into the mybot folder

The script prints the tree of created files. It overwrites existing files -
do not run it over a folder where you have already made changes. The copy of the project inside
scaffold.py is rebuilt by python tools/build_scaffold.py (tests fail if it is
outdated).

---

## 3. Step 2 - install the package

### The usual path (one line)

pip install "tgblocks[runtime]"

runtime is aiogram and aiohttp-socks; without them the bot cannot run (but the code can
be built). After installation the tgblocks command works from any folder:

cd C:\Users\you\Documents\any_folder
tgblocks                      # opens the editor at 127.0.0.1:8765
tgblocks check mybot.tg

If tgblocks is not found, PATH does not see the scripts folder - then either activate
the virtual environment (...\.venv\Scripts\Activate.ps1), or run it through the module:
python -m tgblocks (always works, everywhere).

If you need the newest commit rather than the PyPI release, install directly from GitHub:

pip install "tgblocks[runtime] @ git+https://github.com/Pupka228228/tgblocks.git"

### The development path (from the project folder)

cd C:\TGBots\tgblocks
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
# cmd.exe:        .venv\Scripts\activate.bat
# Linux/macOS:    source .venv/bin/activate

pip install -e ".[dev,runtime]"      # code + editor + tests + running bots

Check that everything installed:

tgblocks --version                  # tgblocks 0.2.0
pytest -q                           # 261 passed

aiogram is needed only to actually run a bot; the compiler works without it.

> If PowerShell complains about Activate.ps1 ("running scripts is disabled"),
> run once: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned.

---

## 4. Step 3 - the first bot in DSL

Three steps: write a .tg -> check -> run.

### 4.1. Write the file

mybot.tg (indentation is exactly 4 spaces, tabs are forbidden):

bot token "PASTE_YOUR_TOKEN"
bot name "My first bot"

on /start:
    send "Hi! I am a bot."
    buttons:
        "Help" -> /help
        "About" -> /about

on /help:
    send "Commands: /start, /help, /about"
    buttons reply:
        "/start"

on message:
    when text contains "hi":
        send "Hello to you too!"
    else:
        send "I did not understand. Write /help."

### 4.2. Check without running the bot

tgblocks check mybot.tg
# OK mybot.tg: handlers=3, commands=/start, /help, message fallback=yes

tgblocks compile mybot.tg -o bot.py      # get Python code
tgblocks run mybot.tg --dry-run          # same, but to console, without running

--dry-run is the safest way to see what you get: no network, no token
required.

> The token is not written into the file. bot.py reads TG_BOT_TOKEN at startup, so
> the generated code can be committed and shown. Need a self-contained file -
> add --embed-token when building; then the token ends up inside, and such a file
> must not be committed.
>
> If the bot has a button leading to a command that does not exist, check will show
> a warning (this does not block the build).

### 4.3. What happens on an error

mybot.tg:8:10: error: expected a quoted text
   8 |     send Hello!
     |          ^
  hint: wrap the value in double quotes, for example: "Hello!"

The format is always the same: file:line:column: error: reason + the code line + hint.
The compiler never "crashes" with a traceback on syntax.

### 4.4. Option: DSL inside a .py file

Python parses a script before any installed package runs, so a file that
starts with bot token "..." is a syntax error under any pip install.
There is only one working way: keep the DSL as a string and call run() - the file stays valid
Python, python bot.py works, and so does the green Run button in PyCharm.

# bot_embedded.py
from tgblocks import run

run(
    '''
bot token "PASTE_YOUR_TOKEN"
bot name "test"

on /start:
    send "Hi!"
'''
)

python bot_embedded.py                                   # will say there is no token
$env:TG_BOT_TOKEN = "NEW_TOKEN"; python bot_embedded.py   # will start the bot

- Indentation inside the string can be anything (even "aligned to the code"): the parser removes the common shift.
- The token is taken from token=..., then from TG_BOT_TOKEN, then from the DSL.
- Code only, without running: from tgblocks import compile_string; print(compile_string(src)).
- The same engine as tgblocks run: there is no separate compiler.

Second option: keep the DSL in a file with a .py extension and run
tgblocks run bot1.py - the CLI does not look at the extension, it only cares about the text inside.
But python bot1.py will not execute such a file: for the interpreter it is not Python.

### 4.5. Text in the browser: syntax almost like Python

tgblocks visual --view text opens /text - an editor with highlighting. The language is ours, but
it looks like Python: colons and indentation work.

token("123456:ABC")
name("my bot")

on.command("/start"):
    send("Hi")
        button("Help", "/help")
        button("Site", url="https://example.com")

on.message(TEXT, "hi", "Hello"):
    send("Hello to you too!")

on.video_note():
    delete()

on.message(TEXT, ""):
    when("contains", "how are you"):
        send("Great")
    otherwise():
        send("Write /help")

Rules:

- token("..."), name("...") - at the top;
- on.command("/start"):, on.message(...):, on.photo():, on.video_note():,
  on.location():, on.new_members():, on.edited():, on.callback("/data"):,
  on.state("order"):, on.inline_query():, on.chat_member():, on.any(): -
  events (27 types in total, full list in section 8);
- filters right in the event: on.message(TEXT, chat="supergroup"),
  on.message(TEXT, from_user=123), on.message(TEXT, regex="^[0-9]+$");
- send("...") can open a block: buttons are written indented under it;
- button("Help", "/help"), button("Site", url="https://..."), button("Text"),
  button("Phone", contact=True), buttons("reply") - keyboard;
- when("hi"), when("contains", "hi"), otherwise(): - conditions;
- actions: send_photo(url, "caption"), send_document, send_video, send_poll("Question", "Yes", "No"),
  send_location(55.75, 37.61), edit_text("New text"), answer_callback("Done", alert=True),
  pin(), ban_user(123), mute_user(123, 30), delete(), typing(), delay(2), log("...");
- dialogues: state("order") at the top, set_state("order") in the handler, clear_state();
- Ctrl+Enter - build, the error comes with a line number and a caret;
- the "Insert..." button in the header opens a palette of ready-made calls: it is built from
  the same catalogue as the blocks in the other views, so it contains everything the
  compiler can do.

### 4.6. Three visual views and running the bot from the browser

tgblocks                       # /nodes  - blocks and wires
tgblocks --view text           # /text   - text editor
tgblocks --view blocks         # /blocks - Blockly
tgblocks --port 9000           # another port

In the header of each view there are Run and Stop, and the Logs tab shows
the output of the live process (Start polling, network errors, 401). If the token is already set in the
"Bot" block or in TG_BOT_TOKEN, the button does not ask for it again. The code is written
to a temporary folder and run as a separate process - you do not need to close the editor.

Settings (on the right in the header, present in all three views):

- Theme - dark or light;
- Language - Russian or English (English by default). Everything switches:
  buttons, block and field names, hints, list values. The choice is remembered in
  the browser, so all three views open in the same language.

Links can be given with settings right away: http://127.0.0.1:8765/nodes?theme=light&lang=ru

All three views show the same document: a change is visible in the other tabs within a second, and "Clear" in any view clears the bot everywhere.

/nodes:

- blocks are added from the menu on the left and do not connect themselves - they appear free;
- a connection is created by dragging from a node's dot to another node;
- each connection has a cross in the middle - delete the connection, the blocks stay in place;
- nodes are moved with the mouse as a whole, the background is pan, the wheel is zoom, the layout is manual;
- "Open file..." shows the normal Windows file dialog: the selected .json
  (block project) or .txt/.tg (code) opens in the editor;
- one bot - one file: nodes and text are stored in it together, so switching
  views does not lose work (each view has its own part of the file);
- at the bottom right you can see how many blocks are not connected to "Bot".

About event filters. The "Event" block has received from (which chat) and
only from user with ID. But "only these texts" and "text matches the pattern"
fields are not shown: the same thing is more clearly done by the "Condition" block
(when text == "hi"). If such a filter came from the text view, the node
shows it as a separate grey chip with a cross - the value is not lost and can be
removed in one click.

## 5. Step 4 - run a real bot

### 5.1. Get the token

1. In Telegram open @BotFather -> /newbot.
2. Come up with a name and username (ends with bot).
3. BotFather will send a string like 123456789:AAH... - this is the token.

### 5.2. Substitute the token

Three ways, in descending order of convenience:

# 1) with a flag - nothing is written to the file (safe)
tgblocks run mybot.tg --token 123456789:AAH...

# 2) with an environment variable (current window only)
$env:TG_BOT_TOKEN = "123456789:AAH..."
tgblocks run mybot.tg

# 3) right in the DSL - replace "PASTE_YOUR_TOKEN" with the real token

### 5.3. Install aiogram and run

pip install -e ".[runtime]"
tgblocks run mybot.tg
# starting mybot.tg (Ctrl+C to stop)
# INFO:aiogram.dispatcher:Start polling

The bot runs as long as the window is open. Stop it with Ctrl+C.

Then write to the bot in Telegram: /start, /help, any message with the word "hi".

Important about the network. If you see TelegramNetworkError: Cannot connect to host
api.telegram.org - this is a block/lack of access to Telegram, not a code error. You need access to
api.telegram.org (system-level VPN/proxy or
your own aiohttp session in bot.py). The error 401 Unauthorized is the opposite -
the token is wrong or revoked via BotFather.

## 6. Step 5 - visual constructor (two views)

tgblocks                          # editor at 127.0.0.1:8765 (nodes by default)
tgblocks --view text              # straight to the text view
tgblocks --view blocks            # straight to Blockly
tgblocks --port 9000              # another port
tgblocks --no-browser             # do not open the browser

The visual subcommand can be omitted: without arguments tgblocks always opens
the editor, and the flags (--port, --view, --no-browser) work without it too. The command
works from any folder after pip install.

If the editor is already running, a repeated tgblocks does not fail with a port error: the same
version - it simply opens the same editor; an old version or another program on the port -
it starts on the next free port and prints one address to open. To get port 8765 back,
close the old window (Ctrl+C).

The addresses are constant, the switcher is a link in the header:

| Address | What is there |
| --- | --- |
| http://127.0.0.1:8765/nodes | rectangles and wires (default) |
| http://127.0.0.1:8765/blocks | Blockly palette, as in the first version |

### 6.1. Nodes - what it can do

1. On the left is a palette built from the capability catalogue: "Base" (Bot, Event),
   "Messages", "Media", "Keyboard", "Logic", "States", "Moderation", "Service".
   A new action appears in the palette by itself, without editing the page.
2. Adding in context: first select a node, then click a block in the palette -
   the new block is inserted inside the selected one (event -> into the bot, action -> into the event).
3. Wires with the mouse: drag from the blue dot on the right (entrance into the container) or from the bottom (next
   in the chain) onto another block - the editor checks whether this is allowed, and rearranges.
4. Dragging with the mouse: drag a node by any place except input fields and buttons
   (title, margins, empty part). After the first drag the layout
   becomes manual, "Arrange" returns it to automatic.
5. Pan: drag the empty background - the field moves with the mouse. There are no scrollbars.
6. Zoom: mouse wheel (zoom to cursor), minus, 100%, plus, "Fit" buttons -
   fit all nodes into the window. Limits 25-250%.
7. Right panel: drag the divider between the field and the panel to change the width;
   double-click the divider - return to 440 px.
8. Functionality: undo Ctrl+Z, redo Ctrl+Y, duplicate Ctrl+D,
   delete Delete, build Ctrl+Enter.
9. Project: "Save" gives bot.json, "Open" loads it back.
10. Result: "Copy" puts into the clipboard what is open (DSL or Python),
    "Download .tg" / "Download .py" - files, "Build" - forced build.
11. Everything works offline: neither Blockly nor a CDN is needed.

### 6.2. Blocks - the old view

The Bot / Events / Actions / Logic palette, blocks nest into "slots", on the right the same
DSL and Python tabs. Blockly loads from unpkg.com: without the internet the page will say
"Blockly could not be loaded from the CDN" - then just use /nodes.

### 6.3. Common to both

- Token, events, send, buttons, when/else are assembled into the same DSL;
- an error is shown with a line number: editor.tg:7:5: error: ...;
- the server listens only on 127.0.0.1, no account is needed, stop with Ctrl+C.

## 7. Step 6 - take the Python code and live with it

tgblocks compile mybot.tg -o bot.py
python bot.py                      # if TG_BOT_TOKEN is set in the environment

bot.py is ordinary aiogram 3: imports, Dispatcher, decorators, asyncio.run.
It can be:

- read and edited by hand (add your own @dp.message(...) next to it);
- committed to git, deployed to a VPS, to Docker, to any Python hosting;
- run without tgblocks at all - the package is only needed for compilation.

A subtlety: the generated bot.py does not contain the token (unless it was built with
--embed-token), so it can be safely committed. .gitignore still
ignores bot.py - in case someone builds it with an embedded token.

## 8. DSL reference

### Directives

| Entry | Meaning |
| --- | --- |
| bot token "123456:ABC" | required, exactly once |
| bot name "Name" | optional, cosmetic |
| bot proxy "socks5://127.0.0.1:1080" | optional, proxy for api.telegram.org |
| bot webhook "https://example.com/hook" | optional: instead of polling the bot raises a webhook |
| bot webhook_path "/hook" | path, /webhook by default |
| bot webhook_secret "secret" | secret for verifying Telegram requests |
| state order | declare a dialogue step (FSM) |

### Events

| Entry | Meaning |
| --- | --- |
| on /start: | handler for the /start command (letters, digits, _) |
| on message: | any text (on text: - the same thing) |
| on message "hi", "hello": | only these exact texts (case matters) |
| on photo: / on sticker: / on voice: / on video: / on video_note: / on audio: / on document: / on animation: / on location: / on contact: / on poll: / on dice: | the corresponding message type |
| on new_members: / on left_member: / on pinned: / on web_app_data: | service chat messages |
| on edited: | edited message |
| on any: | any message, registered last |
| on callback: / on callback "/menu": | inline button press: any or with exact data |
| on state order: | a message while the user is at the order step |
| on inline_query: | inline mode (@bot query) |
| on chat_member: / on my_chat_member: | a member changed / the bot was added or removed |
| on poll_answer: / on channel_post: | poll answer / channel post |

Filters can be added to any event: chat=group, chat=supergroup,
chat=channel, chat=private, from_user=123, regex="^[0-9]+$". Example:
on message chat=supergroup regex="spam":

### Actions inside an event

| Entry | Meaning |
| --- | --- |
| send "Text" | reply with text; \n - line break, \" - quote |
| send_photo "url" "caption" | photo by link or file_id (same for send_document, send_video, send_animation, send_audio, send_voice, send_sticker) |
| send_poll "Question" "Yes" "No" | poll |
| send_location 55.75 37.61 | geolocation |
| send_contact "+100" "Name" | contact |
| send_dice "Dice" | dice or another emoji interactive |
| edit_text "New text" | rewrite the message on which the button was pressed |
| answer_callback "Done" / answer_callback "Error" alert | pop-up hint above the button |
| delete | delete the message |
| pin / pin silent / unpin | pin / unpin |
| ban_user / ban_user 123 / unban_user 123 / mute_user 123 30 | moderation; without an ID - the message author |
| set_state order / clear_state | dialogue step: remember / forget |
| delay 2 / typing / log "text" / pass | pause, "typing...", write to log, empty action |
| inline_result "Title" "Text" | answer to an inline query |
| buttons: | inline keyboard for the send message directly above |
| buttons reply: | reply keyboard (buttons send their label as text) |
| "Help" -> /help | inline button, calls a command (works via callback) |
| "Site" -> url "https://..." | inline link button |
| "App" -> web_app "https://..." | Web App button |
| "Phone" -> contact | reply button: request phone |
| "Where am I" -> location | reply button: request location |
| "Just text" | reply keyboard row (without ->) |

### Conditions

when text == "hi":        # exact match (case matters)
when text != "stop":
when text contains "price":    # substring, case does not matter
when text startswith "buy":  # starts with, case does not matter
when text endswith "?":       # ends with, case does not matter
else:                         # branch of the previous when at the same indentation

when can be nested inside each other and combined: several when in a row are
independent checks (unlike elif), else refers only to the nearest when
above.

### Formatting

- indentation - 4 spaces per level, tabs are forbidden;
- comments - whole line only: # text;
- inline comments after code (send "hi"  # note) are not supported;
- a BOM at the start of the file (some editors add it) is allowed.

## 9. CLI commands

| Command | What it does |
| --- | --- |
| tgblocks | open the visual editor (same as tgblocks --view text, tgblocks --port 9000) |
| tgblocks bot.tg | build and run the bot from a file (same as tgblocks run bot.tg) |
| tgblocks --version | version |
| tgblocks check bot.tg | parse only + summary |
| tgblocks compile bot.tg | code to stdout |
| tgblocks compile bot.tg -o bot.py | code to file (without the token - see --embed-token) |
| tgblocks compile bot.tg --embed-token | write the token from .tg into the file |
| tgblocks run bot.tg --dry-run | code to stdout, without running |
| tgblocks run bot.tg | run the bot (aiogram + token required) |
| tgblocks run bot.tg --token ... | run with the token from a flag |
| tgblocks visual | node editor at 127.0.0.1:8765 |
| tgblocks visual --view blocks | same server, but / opens Blockly |
| tgblocks visual --port 9000 --no-browser | another port, no auto-open |
| tgblocks visual --host 0.0.0.0 --allow-remote | expose the editor to the network (only deliberately: it can run code) |
| python -m tgblocks ... | the same without an installed script |

## 10. Common errors -> what to do

| Message | Cause and fix |
| --- | --- |
| tabs are not allowed for indentation | a tab in the indentation. Replace with 4 spaces |
| expected a quoted text / ... button label | missing quotes around the text |
| expected an indented block | after on /start: there are no indented lines |
| unexpected indentation | the line is shifted to the wrong level |
| 'else' without 'when' | else: without a when ...: above |
| unknown statement: 'dance' | typo/unknown command; the list of allowed ones is in hint |
| the bot token is missing | no bot token "..." |
| the bot has no handlers | not a single on ...: |
| duplicate handler for /start | one command described twice; merge and branch via when |
| this handler would never run: line N already handles the same messages | two identical events in a row; the second will not fire - merge them (synonyms message/text, callback filters and message types count as the same) |
| warning: button "..." calls /x, but no `on /x:` block exists | the button leads nowhere; add a handler or fix the command |
| invalid event 'foo' | event not from the list: /command, message, photo, sticker, voice, video, video_note, audio, document, animation, location, contact, poll, dice, callback, state, inline_query, any |
| buttons must follow a send statement | buttons: comes first; there must be a send before it |
| reply buttons cannot have a target | remove -> ... from the reply button |
| URL buttons must start with http | the link has no https:// |
| no bot token. Use --token... | no token passed and the DSL has the PASTE_YOUR_TOKEN placeholder |
| aiogram is not installed | pip install -e ".[runtime]" |
| cannot bind 127.0.0.1:8765 | the port is taken by another program: the command will itself suggest a free address. If it is a second tgblocks - it simply opens the already running editor |
| Blockly could not be loaded from the CDN | no access to unpkg.com; use /nodes |
| TelegramNetworkError ... api.telegram.org | no access to Telegram (block/network) |
| 401 Unauthorized | the token is wrong or revoked in BotFather |

If the error is about .venv\Scripts\Activate.ps1 - see Set-ExecutionPolicy in step 2.

## 10.5. If it does not connect: api.telegram.org and a proxy

Symptom:

aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host api.telegram.org:443
aiogram.exceptions.TelegramNetworkError: HTTP Client says - ClientConnectorError ...

or OSError: [WinError 121] The semaphore timeout period has expired. This is not a code error and not
the token: the network does not let you reach api.telegram.org (it is blocked in Russia). The token has nothing to do with it.

Two working ways:

1. System-wide VPN - after enabling it, the bot runs without changes.
2. Proxy - a line is added to the DSL, a call in the text editor:

   bot token "123456:ABC"
   bot proxy "socks5://127.0.0.1:1080"

   proxy("socks5://127.0.0.1:1080")

   socks5://, socks4://, http://, https:// work. The proxy can be not written in
   the file, but set in the environment: TG_PROXY=socks5://127.0.0.1:1080.

   For a socks proxy you need a package: pip install aiohttp-socks (it is already included in
   pip install -e ".[runtime]").

   What exactly to enter. In the proxy field - only the address itself, one line, without
   quotes and without JSON: socks5://208.102.51.6:58208. If you have a card like
   {"proxy": "...", "protocol": "socks5", "ip": "...", "port": ..., "anonymity": ...},
   take from it only the value of proxy; the rest are service fields, the bot does not need
   them. With a login and password: socks5://user:pass@host:port.

3. Check the proxy before running - by the same path the bot will take (SOCKS5 ->
   TLS -> api.telegram.org):

   tgblocks proxy socks5://208.102.51.6:58208
   tgblocks proxy                      # will take TG_PROXY from the environment

   The answer OK ... works - the proxy is suitable; the command immediately prints the lines for all
   three views. FAIL ... no connection - the proxy is dead, closed in your network or does not
   allow 443: from free lists this happens more often than working ones.

In nodes, the "Bot" block has a proxy field - fill it in if you need a proxy.

If the proxy is not up or is wrong, the bot now writes a clear message instead of a sheet of
traceback:

No connection to api.telegram.org (Couldn't connect to proxy 127.0.0.1:9).
Most likely Telegram is blocked in this network. Options:
  1) enable VPN for the whole system;
  2) specify a proxy: bot proxy "socks5://127.0.0.1:1080" or TG_PROXY=...
     and install the package: pip install aiohttp-socks

## 11. Token security

- Do not commit the token to git. The examples have PASTE_YOUR_TOKEN - leave it that way.
- Best of all: --token at startup or TG_BOT_TOKEN in the environment/secrets of CI,
  and in .tg - a placeholder.
- If the token leaked - BotFather -> /revoke and a new token.
- The visual editor does not send the token anywhere: it lives in the browser, it only goes
  to your own 127.0.0.1.

## 12. Where everything is

tgblocks\
|-- scaffold.py              project generator (in one file)
|-- pyproject.toml           package name, version, dependencies, console script
|-- README.md                documentation (English + Russian block)
|-- INSTRUCTION.md           this file
|-- examples\hello.tg        a short example
|-- examples\full.tg         a bot that uses everything at once
|-- examples\features.txt    the same set in text syntax
|-- tools\
|   |-- build_scaffold.py    rebuilds the built-in copy of the project in scaffold.py
|   |-- check_javascript.py  checks the JS syntax in all pages
|-- tests\                   tests: golden code, fake Telegram, editors, security
|-- src\tgblocks\
    |-- model.py             capability catalogue: each action and event - once
    |-- cli.py               check / compile / run / visual
    |-- runner.py            run() and compile_string() - DSL as a string from .py
    |-- textlang.py          "Python-like" syntax -> the same AST
    |-- convert.py           AST <-> text, <-> node board, <-> Blockly XML
    |-- dsl\parser.py        DSL -> AST, errors with line numbers
    |-- dsl\codegen.py       AST -> aiogram 3 (helpers on demand)
    |-- visual\
        |-- server.py        local HTTP server (/api/compile, /api/schema, /nodes...)
        |-- static\nodes.html    rectangles + wires, no CDN
        |-- static\blocks.html   Blockly (palette from the catalogue, CDN)
        |-- static\text.html     text editor + "Insert..." palette
        |-- static\tgblocks-project.js  one project document for three views

The chain: node board / Blockly workspace -> (server) AST -> canonical text ->
codegen.py -> bot.py. The model.py catalogue is the single source of truth: parsers,
converters, the generator and all three editors read it, so new capabilities do not
diverge between views.

## 13. Limitations (for honesty)

- no payments, scenes and arbitrary callback data for buttons: a button leads to a command
  or to a link;
- one handler per filter: two identical on message: are rejected, branch via
  when;
- inline mode can do one thing: answer with an article (inline_result);
- the editors do not pick up manual Python edits: the source of truth is the DSL text;
- scaffold.py stores a copy of the project: python tools/build_scaffold.py rebuilds it,
  and tests/test_scaffold.py fails if the copy is out of date;
- the Windows path in the examples - for Linux/macOS the venv activation is different (see step 2).




# **РУССКИЙ**

# Инструкция: tgblocks - DSL + визуальный конструктор Telegram-ботов

Пошагово: от пустой папки до работающего бота. Всё проверено на этой машине
(Windows, Python 3.13). Команды для Windows; для Linux/macOS отличия указаны.

---

## 0. Что вообще есть

| Что | Где | Зачем |
| --- | --- | --- |
| `scaffold.py` | корень проекта | генератор проекта: запустил → получил готовый пакет |
| Проект `tgblocks` | `C:\TGBots\tgblocks\` | уже готов, можно пользоваться сразу |
| DSL-файлы | `*.tg` | текст, который ты пишешь сам |
| Визуальный редактор | `tgblocks visual` | браузер: узлы, блоки и текст → тот же DSL |
| Готовый код | `*.py` после `tgblocks compile` | обычный aiogram 3, правится руками |

Входов теперь три (узлы, блоки, текст), выход один: все они превращаются в один и тот
же Python-код.

---

## 1. Что понадобится

- Python **3.10+** (проверить: `python --version`).
- Терминал (PowerShell подойдёт).
- Токен бота - его выдаёт **@BotFather** в Telegram (раздел 4).
- Интернет: для `pip install`, для первой загрузки Blockly с CDN и для самого бота
  (доступ к `api.telegram.org`).

---

## 2. Шаг 1 - создать проект

Проект уже создан в `C:\TGBots\tgblocks`. Если хочешь с нуля или в другой папке:

```powershell
cd C:\TGBots\tgblocks
python scaffold.py              # создаст .\tgblocks
python scaffold.py mybot        # или в папку mybot
```

Скрипт печатает дерево созданных файлов. Существующие файлы он перезаписывает -
не запускай его поверх папки, где ты уже что-то правил. Копию проекта внутри
`scaffold.py` пересобирает `python tools/build_scaffold.py` (тесты падают, если она
устарела).

---

## 3. Шаг 2 - установить пакет

### Обычный путь (одна строка)

```powershell
pip install "tgblocks[runtime]"
```

`runtime` - это `aiogram` и `aiohttp-socks`, без них бота не запустить (но собрать
код можно). После установки команда `tgblocks` работает **из любой папки**:

```powershell
cd C:\Users\ты\Documents\любая_папка
tgblocks                      # открывает редактор 127.0.0.1:8765
tgblocks check mybot.tg
```

Если `tgblocks` не находится, PATH не видит папку скриптов - тогда либо активируй
виртуальное окружение (`...\.venv\Scripts\Activate.ps1`), либо запускай через модуль:
`python -m tgblocks` (работает всегда и везде).

Если нужен самый свежий коммит, а не релиз с PyPI, ставится прямо с GitHub:

```powershell
pip install "tgblocks[runtime] @ git+https://github.com/Pupka228228/tgblocks.git"
```

### Путь для разработки (из папки проекта)

```powershell
cd C:\TGBots\tgblocks
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # PowerShell
# cmd.exe:        .venv\Scripts\activate.bat
# Linux/macOS:    source .venv/bin/activate

pip install -e ".[dev,runtime]"      # код + редактор + тесты + запуск ботов
```

Проверка, что всё встало:

```powershell
tgblocks --version                  # tgblocks 0.2.0
pytest -q                           # 261 passed
```

`aiogram` нужен только чтобы реально запускать бота, компилятор работает и без него.

> Если PowerShell ругается на `Activate.ps1` («выполнение сценариев отключено»),
> один раз выполни: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

---

## 4. Шаг 3 - первый бот на DSL

Три шага: написать `.tg` → проверить → запустить.

### 4.1. Написать файл

`mybot.tg` (отступы - **ровно 4 пробела**, табы запрещены):

```
bot token "PASTE_YOUR_TOKEN"
bot name "Мой первый бот"

on /start:
    send "Привет! Я бот."
    buttons:
        "Помощь" -> /help
        "О боте" -> /about

on /help:
    send "Команды: /start, /help, /about"
    buttons reply:
        "/start"

on message:
    when text contains "привет":
        send "И тебе привет!"
    else:
        send "Не понял. Напиши /help."
```

### 4.2. Проверить, не запуская бота

```powershell
tgblocks check mybot.tg
# OK mybot.tg: handlers=3, commands=/start, /help, message fallback=yes

tgblocks compile mybot.tg -o bot.py      # получить Python-код
tgblocks run mybot.tg --dry-run          # то же, но в консоль, без запуска
```

`--dry-run` - самый безопасный способ посмотреть, что получится: ни сети, ни токена
не требуется.

> **Токен в файл не пишется.** `bot.py` читает `TG_BOT_TOKEN` при запуске, поэтому
> сгенерированный код можно коммитить и показывать. Нужен самодостаточный файл -
> добавь `--embed-token` при сборке; тогда токен окажется внутри, и такой файл
> коммитить нельзя.
>
> Если в боте есть кнопка, ведущая на команду, которой нет, `check` покажет
> предупреждение (сборку это не блокирует).

### 4.3. Что происходит при ошибке

```
mybot.tg:8:10: error: expected a quoted text
   8 |     send Привет!
     |          ^
  hint: wrap the value in double quotes, for example: "Hello!"
```

Формат всегда один: `файл:строка:столбец: error: причина` + строка кода + `hint`.
Компилятор никогда не «падает» трейсбеком на синтаксисе.

### 4.4. Вариант: DSL внутри `.py`-файла

Python разбирает скрипт раньше, чем запускается любой установленный пакет, поэтому файл,
который *начинается* с `bot token "..."`, - синтаксическая ошибка при любом `pip install`.
Рабочий способ один: держать DSL строкой и вызвать `run()` - файл остаётся валидным
Python, работает `python bot.py` и зелёная кнопка Run в PyCharm.

```python
# bot_embedded.py
from tgblocks import run

run(
    '''
bot token "PASTE_YOUR_TOKEN"
bot name "test"

on /start:
    send "Hi!"
'''
)
```

```powershell
python bot_embedded.py                                   # скажет, что нет токена
$env:TG_BOT_TOKEN = "НОВЫЙ_ТОКЕН"; python bot_embedded.py # запустит бота
```

- Отступы внутри строки могут быть любыми (даже «под код»): парсер убирает общий сдвиг.
- Токен берётся из `token=...`, затем из `TG_BOT_TOKEN`, затем из DSL.
- Только код, без запуска: `from tgblocks import compile_string; print(compile_string(src))`.
- Тот же движок, что у `tgblocks run`: отдельного компилятора нет.

Второй вариант: держать DSL в файле с расширением `.py` и запускать
`tgblocks run bot1.py` - CLI не смотрит на расширение, ему важен текст внутри.
Но `python bot1.py` такой файл не выполнит: для интерпретатора это не Python.

### 4.5. Текст в браузере: синтаксис почти как Python

`tgblocks visual --view text` открывает `/text` - редактор с подсветкой. Язык наш, но
выглядит как Python: двоеточия и отступы работают.

```
token("123456:ABC")
name("мой бот")

on.command("/start"):
    send("Привет")
        button("Помощь", "/help")
        button("Сайт", url="https://example.com")

on.message(TEXT, "привет", "Привет"):
    send("И тебе привет!")

on.video_note():
    delete()

on.message(TEXT, ""):
    when("contains", "как дела"):
        send("Отлично")
    otherwise():
        send("Напиши /help")
```

Правила:

- `token("...")`, `name("...")` - сверху;
- `on.command("/start"):`, `on.message(...):`, `on.photo():`, `on.video_note():`,
  `on.location():`, `on.new_members():`, `on.edited():`, `on.callback("/data"):`,
  `on.state("order"):`, `on.inline_query():`, `on.chat_member():`, `on.any():` -
  события (всего 27 типов, полный список - в разделе 8);
- фильтры прямо в событии: `on.message(TEXT, chat="supergroup")`,
  `on.message(TEXT, from_user=123)`, `on.message(TEXT, regex="^[0-9]+$")`;
- `send("...")` может открыть блок: кнопки пишутся **с отступом под ним**;
- `button("Помощь", "/help")`, `button("Сайт", url="https://...")`, `button("Текст")`,
  `button("Телефон", contact=True)`, `buttons("reply")` - клавиатура;
- `when("hi")`, `when("contains", "hi")`, `otherwise():` - условия;
- действия: `send_photo(url, "подпись")`, `send_document`, `send_video`, `send_poll("Вопрос", "Да", "Нет")`,
  `send_location(55.75, 37.61)`, `edit_text("Новый текст")`, `answer_callback("Готово", alert=True)`,
  `pin()`, `ban_user(123)`, `mute_user(123, 30)`, `delete()`, `typing()`, `delay(2)`, `log("…")`;
- диалоги: `state("order")` сверху, `set_state("order")` в обработчике, `clear_state()`;
- `Ctrl+Enter` - собрать, ошибка приходит с номером строки и кареткой;
- кнопка **«Вставить…»** в шапке открывает палитру готовых вызовов: она строится из
  того же каталога, что и блоки в других видах, поэтому в ней есть всё, что умеет
  компилятор.

### 4.6. Три визуальных вида и запуск бота из браузера

```
tgblocks                       # /nodes  - блоки и связи
tgblocks --view text           # /text   - текстовый редактор
tgblocks --view blocks         # /blocks - Blockly
tgblocks --port 9000           # другой порт
```

В шапке каждого вида есть `▶ Запустить` и `■ Стоп`, а вкладка **Логи** показывает
вывод живого процесса (`Start polling`, ошибки сети, `401`). Если токен уже стоит в
блоке «Бот» или в `TG_BOT_TOKEN`, кнопка не спрашивает его повторно. Код пишется
во временную папку и запускается отдельным процессом - редактор можно не закрывать.

**⚙ Настройки** (справа в шапке, есть во всех трёх видах):

- **Тема** - тёмная или светлая;
- **Язык** - русский или английский (по умолчанию английский). Переключается всё:
  кнопки, названия блоков и полей, подсказки, значения списков. Выбор запоминается в
  браузере, поэтому все три вида открываются на том же языке.

Ссылки можно давать сразу с настройками: `http://127.0.0.1:8765/nodes?theme=light&lang=ru`.

Все три вида показывают **один и тот же документ**: изменение видно в остальных
вкладках за секунду, а «Очистить» в любом виде очищает бота везде.

`/nodes`:

- блоки добавляются из меню слева и **не связываются сами** - они появляются свободно;
- связь создаётся перетаскиванием от точки узла к другому узлу;
- у каждой связи в середине есть `✕` - удалить связь, блоки остаются на месте;
- узлы двигаются мышью целиком, фон - панорама, колесо - масштаб, раскладка ручная;
- **«Открыть файл…»** показывает обычный проводник Windows: выбранный `.json`
  (проект блоков) или `.txt`/`.tg` (код) открывается в редакторе;
- один бот - один файл: узлы и текст хранятся в нём вместе, поэтому переключение
  видов не теряет работу (у каждого вида своя часть файла);
- внизу справа видно, сколько блоков не подключено к «Бот».

**Про фильтры события.** В блоке «Событие» есть `получено` (какой чат) и
`только от пользователя с ID`. А «только эти тексты» и «текст подходит под шаблон»
поля **не показывают**: то же самое нагляднее делает блок «Условие»
(`when text == "привет"`). Если такой фильтр пришёл из текстового вида, узел
показывает его отдельной серой плашкой с `✕` - значение не теряется и его можно
убрать в один клик.


## 5. Шаг 4 - запустить настоящего бота

### 5.1. Взять токен

1. В Telegram открой **@BotFather** → `/newbot`.
2. Придумай имя и username (заканчивается на `bot`).
3. BotFather пришлёт строку вида `123456789:AAH...` - это и есть токен.

### 5.2. Подставить токен

Три способа, по убыванию удобства:

```powershell
# 1) флагом - ничего не записывается в файл (безопасно)
tgblocks run mybot.tg --token 123456789:AAH...

# 2) переменной окружения (только для текущего окна)
$env:TG_BOT_TOKEN = "123456789:AAH..."
tgblocks run mybot.tg

# 3) прямо в DSL - замени "PASTE_YOUR_TOKEN" на реальный токен
```

### 5.3. Установить aiogram и запустить

```powershell
pip install -e ".[runtime]"
tgblocks run mybot.tg
# starting mybot.tg (Ctrl+C to stop)
# INFO:aiogram.dispatcher:Start polling
```

Бот работает, пока открыто окно. Остановить - `Ctrl+C`.

Дальше пиши боту в Telegram: `/start`, `/help`, любое сообщение со словом «привет».

> **Важно про сеть.** Если видишь `TelegramNetworkError: Cannot connect to host
> api.telegram.org` - это блокировка/отсутствие доступа к Telegram, а не ошибка
> кода. Нужен доступ к `api.telegram.org` (VPN/прокси на уровне системы или
> собственный `aiohttp`-сеанс в `bot.py`). Ошибка `401 Unauthorized` - наоборот,
> токен неверный или отозван через BotFather.

---

## 6. Шаг 5 - визуальный конструктор (два вида)

```powershell
tgblocks                          # редактор на 127.0.0.1:8765 (по умолчанию узлы)
tgblocks --view text              # сразу текстовый вид
tgblocks --view blocks            # сразу Blockly
tgblocks --port 9000              # другой порт
tgblocks --no-browser             # не открывать браузер
```

Подкоманду `visual` можно не писать: без аргументов `tgblocks` всегда открывает
редактор, а флаги (`--port`, `--view`, `--no-browser`) работают и без неё. Команда
работает из любой папки после `pip install`.

Если редактор уже запущен, повторный `tgblocks` не падает с ошибкой порта: та же
версия - просто откроет тот же редактор; старая версия или чужая программа на порту -
запустится на следующем свободном порту и напечатает **один адрес**, который надо
открыть. Чтобы вернуть себе порт 8765, закрой старое окно (`Ctrl+C`).

Адреса постоянные, переключатель - ссылка в шапке:

| Адрес | Что там |
| --- | --- |
| `http://127.0.0.1:8765/nodes` | прямоугольники и связи (по умолчанию) |
| `http://127.0.0.1:8765/blocks` | Blockly-палитра, как в первой версии |

### 6.1. Узлы - что умеет

1. Слева палитра, собранная из каталога возможностей: «Основа» (Бот, Событие),
   «Сообщения», «Медиа», «Клавиатура», «Логика», «Состояния», «Модерация», «Сервис».
   Новое действие появляется в палитре само, без правки страницы.
2. **Добавление в контекст:** сначала выбери узел, потом кликни блок в палитре -
   новый блок вставится внутрь выбранного (событие → в бота, действие → в событие).
3. **Связи мышью:** тяни от синей точки справа (вход в контейнер) или снизу (следующий
   по цепочке) на другой блок - редактор проверит, можно ли так, и переставит.
4. **Перетаскивание мышью:** тяни узел за любое место, кроме полей ввода и кнопок
   (заголовок, отступы, пустая часть). После первого перетаскивания раскладка
   становится ручной, «Разложить» возвращает автоматическую.
5. **Панорама:** тяни пустой фон - поле едет вместе с мышью. Полос прокрутки нет.
6. **Масштаб:** колесо мыши (зум к курсору), кнопки `−`, `100%`, `+`, «Вписать» -
   вписать все узлы в окно. Пределы 25-250%.
7. **Правая панель:** тяни разделитель между полем и панелью, чтобы менять ширину;
   двойной клик по разделителю - вернуть 440 px.
8. **Функционал:** отмена `Ctrl+Z`, повтор `Ctrl+Y`, дублирование `Ctrl+D`,
   удаление `Delete`, собрать `Ctrl+Enter`.
9. **Проект:** «Сохранить» отдаёт `bot.json`, «Открыть» загружает его обратно.
10. **Результат:** «Копировать» кладёт в буфер то, что открыто (DSL или Python),
    «Скачать .tg» / «Скачать .py» - файлы, «Собрать» - принудительная сборка.
11. Всё работает офлайн: ни Blockly, ни CDN не нужны.

### 6.2. Блоки - старый вид

Палитра **Bot / Events / Actions / Logic**, блоки вкладываются в «пазы», справа те же
вкладки DSL и Python. Blockly грузится с unpkg.com: без интернета страница скажет
«Blockly could not be loaded from the CDN» - тогда просто используй `/nodes`.

### 6.3. Общее для обоих

- Токен, события, send, кнопки, when/else собираются в один и тот же DSL;
- ошибка показывается с номером строки: `editor.tg:7:5: error: ...`;
- сервер слушает только `127.0.0.1`, аккаунт не нужен, остановка - `Ctrl+C`.

---

## 7. Шаг 6 - забрать Python-код и жить с ним

```powershell
tgblocks compile mybot.tg -o bot.py
python bot.py                      # если TG_BOT_TOKEN задан в окружении
```

`bot.py` - это обычный aiogram 3: импорты, `Dispatcher`, декораторы, `asyncio.run`.
Его можно:

- читать и править руками (добавить свои `@dp.message(...)` рядом);
- коммитить в git, деплоить на VPS, в Docker, в любой хостинг Python;
- запускать без `tgblocks` вообще - пакет нужен только для компиляции.

Тонкость: сгенерированный `bot.py` **не содержит токена** (если не собрать его с
`--embed-token`), поэтому его можно спокойно коммитить. `.gitignore` всё равно
игнорирует `bot.py` - на случай, если кто-то соберёт с встроенным токеном.

---

## 8. Справочник DSL

### Директивы

| Запись | Смысл |
| --- | --- |
| `bot token "123456:ABC"` | обязательна, ровно один раз |
| `bot name "Имя"` | необязательно, косметика |
| `bot proxy "socks5://127.0.0.1:1080"` | необязательно, прокси для api.telegram.org |
| `bot webhook "https://example.com/hook"` | необязательно: вместо polling бот поднимает webhook |
| `bot webhook_path "/hook"` | путь, по умолчанию `/webhook` |
| `bot webhook_secret "секрет"` | секрет для проверки запросов Telegram |
| `state order` | объявить шаг диалога (FSM) |

### События

| Запись | Смысл |
| --- | --- |
| `on /start:` | обработчик команды `/start` (буквы, цифры, `_`) |
| `on message:` | любой текст (`on text:` - то же самое) |
| `on message "привет", "здравствуй":` | только эти точные тексты (регистр важен) |
| `on photo:` / `on sticker:` / `on voice:` / `on video:` / `on video_note:` / `on audio:` / `on document:` / `on animation:` / `on location:` / `on contact:` / `on poll:` / `on dice:` | соответствующий тип сообщения |
| `on new_members:` / `on left_member:` / `on pinned:` / `on web_app_data:` | служебные сообщения чата |
| `on edited:` | изменённое сообщение |
| `on any:` | любое сообщение, регистрируется последним |
| `on callback:` / `on callback "/menu":` | нажатие inline-кнопки: любое или с точными данными |
| `on state order:` | сообщение, пока пользователь на шаге `order` |
| `on inline_query:` | inline-режим (`@бот запрос`) |
| `on chat_member:` / `on my_chat_member:` | участник изменился / бота добавили или убрали |
| `on poll_answer:` / `on channel_post:` | ответ на опрос / пост в канале |

Фильтры можно добавлять к любому событию: `chat=group`, `chat=supergroup`,
`chat=channel`, `chat=private`, `from_user=123`, `regex="^[0-9]+$"`. Пример:
`on message chat=supergroup regex="спам":`.

### Действия внутри события

| Запись | Смысл |
| --- | --- |
| `send "Текст"` | ответить текстом; `\n` - перенос строки, `\"` - кавычка |
| `send_photo "url" "подпись"` | фото по ссылке или `file_id` (так же `send_document`, `send_video`, `send_animation`, `send_audio`, `send_voice`, `send_sticker`) |
| `send_poll "Вопрос" "Да" "Нет"` | опрос |
| `send_location 55.75 37.61` | геолокация |
| `send_contact "+100" "Имя"` | контакт |
| `send_dice "🎲"` | кубик или другой эмодзи-интерактив |
| `edit_text "Новый текст"` | переписать сообщение, на котором нажали кнопку |
| `answer_callback "Готово"` / `answer_callback "Ошибка" alert` | всплывающая подсказка над кнопкой |
| `delete` | удалить сообщение |
| `pin` / `pin silent` / `unpin` | закрепить / открепить |
| `ban_user` / `ban_user 123` / `unban_user 123` / `mute_user 123 30` | модерация; без ID - автор сообщения |
| `set_state order` / `clear_state` | шаг диалога: запомнить / забыть |
| `delay 2` / `typing` / `log "текст"` / `pass` | пауза, «печатает…», запись в лог, пустое действие |
| `inline_result "Заголовок" "Текст"` | ответ на inline-запрос |
| `buttons:` | inline-клавиатура к сообщению из `send` **прямо выше** |
| `buttons reply:` | reply-клавиатура (кнопки отправляют свою подпись как текст) |
| `"Помощь" -> /help` | inline-кнопка, вызывает команду (работает через callback) |
| `"Сайт" -> url "https://..."` | inline-кнопка-ссылка |
| `"Приложение" -> web_app "https://..."` | кнопка Web App |
| `"Телефон" -> contact` | reply-кнопка: запросить телефон |
| `"Где я" -> location` | reply-кнопка: запросить геолокацию |
| `"Просто текст"` | строка reply-клавиатуры (без `->`) |

### Условия

```
when text == "привет":        # точное совпадение (регистр важен)
when text != "стоп":
when text contains "цена":    # подстрока, регистр не важен
when text startswith "купи":  # начинается с, регистр не важен
when text endswith "?":       # заканчивается на, регистр не важен
else:                         # ветка предыдущего when на том же отступе
```

`when` можно вкладывать друг в друга и комбинировать: несколько `when` подряд - это
независимые проверки (в отличие от `elif`), `else` относится только к ближайшему
`when` выше.

### Форматирование

- отступ - **4 пробела** на уровень, табы запрещены;
- комментарии - только целой строкой: `# текст`;
- строчные комментарии после кода (`send "hi"  # note`) не поддерживаются;
- BOM в начале файла (его добавляют некоторые редакторы) допускается.

---

## 9. Команды CLI

| Команда | Что делает |
| --- | --- |
| `tgblocks` | открыть визуальный редактор (так же `tgblocks --view text`, `tgblocks --port 9000`) |
| `tgblocks bot.tg` | собрать и запустить бота из файла (то же, что `tgblocks run bot.tg`) |
| `tgblocks --version` | версия |
| `tgblocks check bot.tg` | только разбор + сводка |
| `tgblocks compile bot.tg` | код в stdout |
| `tgblocks compile bot.tg -o bot.py` | код в файл (без токена - см. `--embed-token`) |
| `tgblocks compile bot.tg --embed-token` | вписать токен из `.tg` в файл |
| `tgblocks run bot.tg --dry-run` | код в stdout, без запуска |
| `tgblocks run bot.tg` | запуск бота (нужен aiogram + токен) |
| `tgblocks run bot.tg --token ...` | запуск с токеном из флага |
| `tgblocks visual` | редактор узлов на `127.0.0.1:8765` |
| `tgblocks visual --view blocks` | тот же сервер, но `/` открывает Blockly |
| `tgblocks visual --port 9000 --no-browser` | другой порт, без автооткрытия |
| `tgblocks visual --host 0.0.0.0 --allow-remote` | открыть редактор в сеть (только осознанно: он умеет запускать код) |
| `python -m tgblocks ...` | то же самое без установленного скрипта |

---

## 10. Частые ошибки → что делать

| Сообщение | Причина и лечение |
| --- | --- |
| `tabs are not allowed for indentation` | в отступе таб. Заменить на 4 пробела |
| `expected a quoted text` / `… button label` | забыты кавычки вокруг текста |
| `expected an indented block` | после `on /start:` нет вложенных строк с отступом |
| `unexpected indentation` | строка сдвинута не на тот уровень |
| `'else' without 'when'` | `else:` без `when ...:` выше |
| `unknown statement: 'dance'` | опечатка/неизвестная команда; список допустимых - в `hint` |
| `the bot token is missing` | нет `bot token "..."` |
| `the bot has no handlers` | нет ни одного `on ...:` |
| `duplicate handler for /start` | одна команда описана дважды; объедини и ветвись через `when` |
| `this handler would never run: line N already handles the same messages` | два одинаковых события подряд; второе не сработает - объедини их (синонимы `message`/`text`, `callback`-фильтры и типы сообщений считаются одинаковыми) |
| `warning: button "…" calls /x, but no `on /x:` block exists` | кнопка ведёт в никуда; добавь обработчик или поправь команду |
| `invalid event 'foo'` | событие не из списка: `/команда`, `message`, `photo`, `sticker`, `voice`, `video`, `video_note`, `audio`, `document`, `animation`, `location`, `contact`, `poll`, `dice`, `callback`, `state`, `inline_query`, `any` |
| `buttons must follow a send statement` | `buttons:` стоит первым; перед ним должен быть `send` |
| `reply buttons cannot have a target` | у reply-кнопки убери `-> ...` |
| `URL buttons must start with http` | ссылка без `https://` |
| `no bot token. Use --token…` | не передан токен и в DSL заглушка `PASTE_YOUR_TOKEN` |
| `aiogram is not installed` | `pip install -e ".[runtime]"` |
| `cannot bind 127.0.0.1:8765` | порт занят другой программой: команда сама подскажет свободный адрес. Если это второй `tgblocks` - он просто откроет уже запущенный редактор |
| `Blockly could not be loaded from the CDN` | нет доступа к unpkg.com; используй `/nodes` |
| `TelegramNetworkError … api.telegram.org` | нет доступа к Telegram (блокировка/сеть) |
| `401 Unauthorized` | токен неверный или отозван в BotFather |

Если ошибка про `.venv\Scripts\Activate.ps1` - см. `Set-ExecutionPolicy` в шаге 2.

---

## 10.5. Если не подключается: `api.telegram.org` и прокси

Симптом:

```
aiohttp.client_exceptions.ClientConnectorError: Cannot connect to host api.telegram.org:443
aiogram.exceptions.TelegramNetworkError: HTTP Client says - ClientConnectorError ...
```

или `OSError: [WinError 121] Превышен таймаут семафора`. Это **не ошибка кода и не
токен**: сеть не пускает к `api.telegram.org` (в РФ он заблокирован). Токен тут ни при
чём.

Два рабочих способа:

1. **VPN на всю систему** - после включения бот запускается без изменений.
2. **Прокси** - в DSL добавляется строка, в текстовом редакторе вызов:

   ```
   bot token "123456:ABC"
   bot proxy "socks5://127.0.0.1:1080"
   ```

   ```python
   proxy("socks5://127.0.0.1:1080")
   ```

   Подходят `socks5://`, `socks4://`, `http://`, `https://`. Прокси можно не писать в
   файл, а задать в окружении: `TG_PROXY=socks5://127.0.0.1:1080`.

   Для socks-прокси нужен пакет: `pip install aiohttp-socks` (он уже входит в
   `pip install -e ".[runtime]"`).

   **Что именно вписывать.** В поле `proxy` - только сам адрес, одной строкой, без
   кавычек и без JSON: `socks5://208.102.51.6:58208`. Если у тебя есть карточка вида
   `{"proxy": "...", "protocol": "socks5", "ip": "...", "port": ..., "anonymity": ...}`,
   из неё берётся **только** значение `proxy`; остальное - это поля сервиса, боту они
   не нужны. С логином и паролем: `socks5://user:pass@host:port`.

3. **Проверка прокси перед запуском** - тем же путём, которым пойдёт бот (SOCKS5 →
   TLS → `api.telegram.org`):

   ```powershell
   tgblocks proxy socks5://208.102.51.6:58208
   tgblocks proxy                      # возьмёт TG_PROXY из окружения
   ```

   Ответ `OK ... работает` - прокси годится; команда сразу печатает строки для всех
   трёх видов. `FAIL ... нет соединения` - прокси мёртв, закрыт у тебя в сети или не
   пускает 443: из бесплатных списков такое встречается чаще, чем рабочее.

В узлах у блока «Бот» есть поле `proxy` - заполни его, если нужен прокси.

Если прокси не поднят или неверный, бот теперь пишет понятное сообщение вместо простыни
трейсбека:

```
Нет связи с api.telegram.org (Couldn't connect to proxy 127.0.0.1:9).
Скорее всего Telegram заблокирован в этой сети. Варианты:
  1) включить VPN для всей системы;
  2) указать прокси: bot proxy "socks5://127.0.0.1:1080" или TG_PROXY=...
     и поставить пакет: pip install aiohttp-socks
```

---

## 11. Безопасность токена

- Не коммить токен в git. В примерах стоит `PASTE_YOUR_TOKEN` - так и оставляй.
- Лучше всего: `--token` при запуске или `TG_BOT_TOKEN` в окружении/секретах CI,
  а в `.tg` - заглушка.
- Если токен утёк - BotFather → `/revoke` и новый токен.
- Визуальный редактор никуда токен не отправляет: он живёт в браузере, уходит только
  на твой же `127.0.0.1`.

---

## 12. Где что лежит

```
tgblocks\
├── scaffold.py              генератор проекта (одним файлом)
├── pyproject.toml           имя пакета, версия, зависимости, console script
├── README.md                документация (английский + русский блок)
├── INSTRUCTIONS.md            этот файл
├── examples\hello.tg        короткий пример
├── examples\full.tg         бот, который использует всё сразу
├── examples\features.txt    тот же набор в текстовом синтаксисе
├── tools\
│   ├── build_scaffold.py    пересобирает встроенную копию проекта в scaffold.py
│   └── check_javascript.py  проверяет синтаксис JS во всех страницах
├── tests\                   тесты: golden-код, фейковый Telegram, редакторы, безопасность
└── src\tgblocks\
    ├── model.py             каталог возможностей: каждое действие и событие - один раз
    ├── cli.py               check / compile / run / visual
    ├── runner.py            run() и compile_string() - DSL строкой из .py
    ├── textlang.py          синтаксис «как Python» → тот же AST
    ├── convert.py           AST ↔ текст, ↔ доска узлов, ↔ XML Blockly
    ├── dsl\parser.py        DSL → AST, ошибки с номерами строк
    ├── dsl\codegen.py       AST → aiogram 3 (helpers по требованию)
    └── visual\
        ├── server.py        локальный HTTP-сервер (/api/compile, /api/schema, /nodes…)
        ├── static\nodes.html    прямоугольники + связи, без CDN
        ├── static\blocks.html   Blockly (палитра из каталога, CDN)
        ├── static\text.html     текстовый редактор + палитра «Вставить…»
        └── static\tgblocks-project.js  один проектный документ на три вида
```

Цепочка: доска узлов / рабочая область Blockly → (сервер) AST → канонический текст →
`codegen.py` → `bot.py`. Каталог `model.py` - единственный источник правды: парсеры,
конвертеры, генератор и все три редактора читают его, поэтому новые возможности не
расходятся между видами.

---

## 13. Ограничения (для честности)

- нет платежей, сцен и произвольных callback-данных у кнопок: кнопка ведёт на команду
  или на ссылку;
- один обработчик на фильтр: два одинаковых `on message:` отклоняются, ветвись через
  `when`;
- inline-режим умеет одно: ответить статьёй (`inline_result`);
- редакторы не подхватывают ручные правки Python: источник правды - текст DSL;
- `scaffold.py` хранит копию проекта: `python tools/build_scaffold.py` её
  пересобирает, а `tests/test_scaffold.py` падает, если копия устарела;
- Windows-путь в примерах - для Linux/macOS активация venv другая (см. шаг 2).
