# Can this proxy reach api.telegram.org?
#
# A bot behind a blocked network needs a proxy that actually tunnels HTTPS to
# Telegram. "The proxy is in the list" is not the same thing: most free SOCKS
# entries are dead, closed, or do not allow port 443. This module performs the
# same three steps the bot will: connect, ask for api.telegram.org:443, then do a
# real TLS handshake - so the answer is about the bot, not about a ping.

from __future__ import annotations

import base64
import socket
import ssl
import time
from typing import Optional, Tuple
from urllib.parse import unquote, urlsplit

TARGET = "api.telegram.org"
TARGET_PORT = 443
DEFAULT_PORTS = {"socks5": 1080, "socks4": 1080, "http": 8080, "https": 8080}
SCHEMES = tuple(DEFAULT_PORTS)


class ProxyError(Exception):
    """The proxy string itself is wrong (not a network problem)."""


def parse_proxy(url: str) -> Tuple[str, str, int, Optional[str], Optional[str]]:
    """`socks5://user:pass@host:1080` -> (scheme, host, port, user, password)."""
    text = (url or "").strip()
    if not text:
        raise ProxyError("пустая строка прокси")
    if "://" not in text:
        raise ProxyError(
            "нужна схема: socks5://, socks4://, http:// или https:// - "
            "например socks5://127.0.0.1:1080, а не {0!r}".format(text[:40])
        )
    parts = urlsplit(text)
    scheme = parts.scheme.lower()
    if scheme not in SCHEMES:
        raise ProxyError(
            "неизвестная схема {0!r}: подходят {1}".format(scheme, ", ".join(SCHEMES))
        )
    if not parts.hostname:
        raise ProxyError("в адресе нет хоста: {0!r}".format(text[:60]))
    port = parts.port or DEFAULT_PORTS[scheme]
    user = unquote(parts.username) if parts.username else None
    password = unquote(parts.password) if parts.password else None
    return scheme, parts.hostname, port, user, password


def _recv_exactly(sock: socket.socket, size: int) -> bytes:
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise OSError("прокси закрыл соединение")
        data += chunk
    return data


def _socks5(sock: socket.socket, user: Optional[str], password: Optional[str]) -> None:
    methods = b"\x00\x02" if user else b"\x00"
    sock.sendall(b"\x05" + bytes([len(methods)]) + methods)
    version, method = _recv_exactly(sock, 2)
    if version != 5:
        raise OSError("это не SOCKS5 (ответ {0!r})".format(bytes([version, method])))
    if method == 0x02:
        name = (user or "").encode()
        secret = (password or "").encode()
        sock.sendall(b"\x01" + bytes([len(name)]) + name + bytes([len(secret)]) + secret)
        if _recv_exactly(sock, 2)[1] != 0:
            raise OSError("прокси не принял логин/пароль")
    elif method != 0x00:
        raise OSError("прокси требует способ входа, которого нет в строке")
    name = TARGET.encode()
    sock.sendall(b"\x05\x01\x00\x03" + bytes([len(name)]) + name
                 + TARGET_PORT.to_bytes(2, "big"))
    reply = _recv_exactly(sock, 4)
    if reply[1] != 0:
        reasons = {1: "общий сбой", 2: "соединения запрещены", 3: "сеть недоступна",
                   4: "хост недоступен", 5: "соединение отклонено", 6: "TTL истёк",
                   7: "команда не поддержана", 8: "тип адреса не поддержан"}
        raise OSError("прокси не пустил к {0}: {1}".format(
            TARGET, reasons.get(reply[1], "код {0}".format(reply[1]))))


def _socks4(sock: socket.socket, user: Optional[str]) -> None:
    import struct

    address = socket.gethostbyname(TARGET)
    sock.sendall(b"\x04\x01" + struct.pack(">H", TARGET_PORT)
                 + socket.inet_aton(address) + (user or "").encode() + b"\x00")
    reply = _recv_exactly(sock, 8)
    if reply[1] != 0x5A:
        raise OSError("SOCKS4 не пустил к {0}".format(TARGET))


def _http_connect(sock: socket.socket, scheme: str,
                  user: Optional[str], password: Optional[str]) -> None:
    request = "CONNECT {0}:{1} HTTP/1.1\r\nHost: {0}:{1}\r\n".format(TARGET, TARGET_PORT)
    if user:
        token = base64.b64encode("{0}:{1}".format(user, password or "").encode()).decode()
        request += "Proxy-Authorization: Basic {0}\r\n".format(token)
    request += "\r\n"
    sock.sendall(request.encode())
    answer = b""
    while b"\r\n\r\n" not in answer:
        chunk = sock.recv(1)
        if not chunk:
            raise OSError("прокси закрыл соединение до ответа")
        answer += chunk
    status = answer.split(b"\r\n")[0].decode(errors="replace")
    if " 200" not in status:
        raise OSError("прокси отказал: {0}".format(status))


def check_proxy(url: str, timeout: float = 8.0) -> Tuple[bool, str, float]:
    """Return (works, message, seconds) for a proxy URL the bot could use."""
    scheme, host, port, user, password = parse_proxy(url)
    started = time.time()

    def took() -> float:
        return time.time() - started

    try:
        sock = socket.create_connection((host, port), timeout=timeout)
    except OSError as error:
        return False, "нет соединения с прокси {0}:{1} ({2})".format(
            host, port, error or "таймаут"), took()

    try:
        sock.settimeout(timeout)
        if scheme == "socks5":
            _socks5(sock, user, password)
        elif scheme == "socks4":
            _socks4(sock, user)
        else:
            _http_connect(sock, scheme, user, password)

        context = ssl.create_default_context()
        tls = context.wrap_socket(sock, server_hostname=TARGET)
        try:
            tls.sendall(b"GET / HTTP/1.1\r\nHost: " + TARGET.encode()
                        + b"\r\nConnection: close\r\nUser-Agent: tgblocks\r\n\r\n")
            data = tls.recv(64)
        finally:
            tls.close()
        if not data.startswith(b"HTTP/"):
            return False, "туннель есть, но Telegram ответил странно: {0!r}".format(
                data[:40]), took()
        status = data.split(b"\r\n")[0].decode(errors="replace")
        return True, "работает: {0}".format(status), took()
    except ssl.SSLError as error:
        return False, "TLS не поднялся ({0}): прокси вряд ли пускает HTTPS".format(
            error.reason or error), took()
    except OSError as error:
        return False, str(error), took()
    finally:
        try:
            sock.close()
        except OSError:
            pass


def proxy_hint(url: str) -> str:
    # Ready-to-paste lines for all three editors, so a working proxy is easy to
    # put where it belongs.
    return "\n".join([
        'бот:    bot proxy "{0}"'.format(url),
        'текст:  proxy("{0}")'.format(url),
        "узлы:   поле proxy в блоке «Бот»",
        "без файла: TG_PROXY={0}".format(url),
    ])
