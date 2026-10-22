# Публикация tgblocks на GitHub и в PyPI

Полная инструкция с нуля: от пустого аккаунта до `pip install tgblocks` у любого
человека. Всё, что нужно сделать тебе, - один раз выполнить команды из разделов 1-4,
а потом (по желанию) разделы 5-6.

---

## 0. Что понадобится

**Аккаунт GitHub** - хранить код: <https://github.com/signup>

**git** - отправлять код: <https://git-scm.com/download/win>
(при установке оставь галочки по умолчанию)

**Python 3.10 или новее** - собирать пакет: <https://www.python.org/downloads/>

**Аккаунт PyPI** - чтобы работал `pip install`: <https://pypi.org/account/register/>

Проверка, что всё стоит:

```powershell
git --version
python --version
```

---

## 1. Один раз настроить git

```powershell
git config --global user.name "Твоё Имя"
git config --global user.email "твоя_почта@example.com"
```

Почта должна совпадать с той, на которую зарегистрирован GitHub - иначе коммиты не
будут связаны с профилем.

---

## 2. Создать репозиторий на GitHub

1. Открой <https://github.com/new>.
2. **Repository name**: `tgblocks`.
3. **Public** (для приватного всё то же, но `pip install` с GitHub не сработает).
4. **НЕ** ставь галочки «Add a README», «Add .gitignore», «Choose a license» - они уже
   есть в проекте, иначе будет конфликт при первом `push`.
5. **Create repository**.

GitHub покажет адрес вида `https://github.com/Pupka228228/tgblocks.git`.

---

## 3. Отправить код (первый push)

```powershell
cd C:\TGBots\tgblocks
git status                      # должно быть "nothing to commit, working tree clean"
git log --oneline | Select-Object -First 3

git remote add origin https://github.com/Pupka228228/tgblocks.git
git branch -M main
git push -u origin main
```

Если `remote origin already exists`:

```powershell
git remote set-url origin https://github.com/Pupka228228/tgblocks.git
```

### Пароль не подойдёт - нужен токен

GitHub больше не принимает пароль аккаунта. Один раз:

1. <https://github.com/settings/tokens> → **Generate new token (classic)**.
2. Note: `tgblocks push`, Expiration: 90 days, галочка **`repo`**.
3. **Generate token**, скопируй строку `ghp_...` (она показывается один раз).
4. В окне `git push` на запрос пароля вставь этот токен, логин - обычный.

Сохранить токен в менеджере Windows, чтобы не вводить каждый раз:

```powershell
git config --global credential.helper manager
```

Альтернатива - GitHub CLI:

```powershell
winget install --id GitHub.cli
gh auth login        # выбираешь GitHub.com → HTTPS → Login with a web browser
```

### Каждый следующий раз

```powershell
git add -A
git commit -m "что изменилось"
git push
```

---

## 4. Проверить, что всё в порядке

1. Открой страницу репозитория - файлы на месте, README и `docs/demo.gif` видны.
2. Вкладка **Actions**: workflow **CI** должен стать зелёным. Он прогоняет 261 тест на
   Windows и Linux (Python 3.10, 3.11, 3.13), проверяет JS редакторов, собирает пакет и
   ставит его в чистое окружение.
3. Бейдж в README (вставь после заголовка):

```markdown
[![CI](https://github.com/Pupka228228/tgblocks/actions/workflows/ci.yml/badge.svg)](https://github.com/Pupka228228/tgblocks/actions/workflows/ci.yml)
```

Если Actions красный - открой лог: чаще всего это не установленные зависимости, а не
код; локально повтори `python -m pytest -q`.

---

## 5. Установка из GitHub (работает сразу после push)

Ничего дополнительно публиковать не нужно:

```bash
pip install "tgblocks[runtime] @ git+https://github.com/Pupka228228/tgblocks.git"
tgblocks
```

---

## 6. PyPI: чтобы работала одна строка `pip install tgblocks`

### 6.1 Аккаунт и токен

1. Регистрация: <https://pypi.org/account/register/>.
2. Включи **двухфакторную аутентификацию** (без неё токен не создать):
   Account settings → Two-factor authentication.
3. Account settings → **API tokens** → **Add API token** → Name: `tgblocks`,
   Scope: **Entire account** (для первого раза) → **Add token**.
4. Скопируй `pypi-AgEIcHlwaS5vcmc...` - это пароль для загрузки.

### 6.2 Собрать и проверить

```powershell
cd C:\TGBots\tgblocks
python -m pip install --upgrade build twine
python -m build                # dist\tgblocks-0.2.0-py3-none-any.whl и .tar.gz
python -m twine check dist/*   # "PASSED" для обоих файлов
```

### 6.3 Загрузить

```powershell
python -m twine upload dist/*
```

Логин: `__token__`, пароль: сам токен `pypi-...`.

Проверка (подожди полминуты):

```powershell
pip install --upgrade "tgblocks[runtime]"
tgblocks --version
```

### 6.4 Тренировка на тестовом индексе (необязательно)

```powershell
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip install --index-url https://test.pypi.org/simple tgblocks
```

Там отдельный аккаунт (<https://test.pypi.org/account/register/>) и отдельный токен.

---

## 7. Как это ставится у любого человека

```bash
pip install "tgblocks[runtime]"     # пакет + aiogram, чтобы запускать ботов
tgblocks                            # редактор: http://127.0.0.1:8765/
tgblocks check mybot.tg
tgblocks compile mybot.tg -o bot.py
```

- без `[runtime]` ставится только компилятор и редакторы (генерация кода работает);
- `tgblocks` появляется в PATH вместе с Python; в виртуальном окружении - после
  активации. Если команда не находится: `python -m tgblocks` работает всегда.

---

## 8. Выпуск новой версии

1. Подними версию в `pyproject.toml` (`version = "0.2.1"`).
2. Допиши раздел в `CHANGELOG.md`.
3. Прогони проверки:

```powershell
python -m pytest -q
python tools/build_scaffold.py --check
python tools/check_javascript.py
python -m build
python -m twine check dist/*
```

4. Отправь код и создай релиз:

```powershell
git add -A
git commit -m "release 0.2.1"
git tag v0.2.1
git push
git push --tags
```

На GitHub: **Releases** → **Draft a new release** → выбери тег `v0.2.1` → опиши
изменения → прикрепи файлы из `dist/` → **Publish release**.

5. Загрузи в PyPI (`python -m twine upload dist/*`). Одно и то же имя версии дважды
   загрузить нельзя - всегда поднимай номер.

---

## 9. Частые проблемы

**`Authentication failed` при push** - введён пароль вместо токена.
Смотри раздел 3, нужен токен с галочкой `repo`.

**`remote origin already exists`** - remote уже привязан.
Выполни `git remote set-url origin <адрес>`.

**`Updates were rejected`** - на GitHub уже есть коммиты (например, создавал README
через сайт). Сделай `git pull --rebase origin main`, потом `git push`.

**`403` при `twine upload`** - токен без Scope «Entire account» или не включена 2FA.
Создай токен заново.

**`File already exists` на PyPI** - эта версия уже загружена.
Подними `version` в `pyproject.toml`.

**`tgblocks: command not found`** - папка скриптов Python не в PATH.
Активируй venv или запускай `python -m tgblocks`.

**`ModuleNotFoundError: aiogram`** при запуске бота - пакет поставлен без `[runtime]`.
Нужен `pip install "tgblocks[runtime]"`.

**README не показывает картинки** - файлы не попали в репозиторий.
Проверь, что `docs/editor-nodes.png`, `docs/editor-blocks.png`, `docs/editor-text.png`
и `docs/demo.gif` закоммичены, а ветка в ссылках - `main`.

---

## 10. Чек-лист перед публикацией

```powershell
python -m pytest -q                     # 261 passed
python tools/build_scaffold.py --check  # scaffold.py не отстал
python tools/check_javascript.py        # JS редакторов и его хелперы
python tools/qa_smoke.py                # эндпоинты + переходы между видами
python -m build
python -m twine check dist/*
```

И глазами: `tgblocks` открывает редактор, `⚙` переключает тему и язык,
`tgblocks check examples/full.tg` печатает сводку, `tgblocks compile examples/hello.tg
-o bot.py` даёт файл, который открывается в PyCharm без ошибок.
