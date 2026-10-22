# `tgblocks proxy` and the proxy checker behind it.
#
# The network itself is not touched here: the SOCKS5/HTTP handshakes are checked
# byte for byte against a scripted socket, so the test says exactly which bytes
# the bot sends and how each refusal is reported to the user.

import socket
import ssl
import struct
from types import SimpleNamespace

import pytest

from tgblocks.cli import main
from tgblocks.network import ProxyError, check_proxy, parse_proxy, proxy_hint


# ------------------------------------------------------------------- the string
@pytest.mark.parametrize(
    "url,scheme,host,port,user,password",
    [
        ("socks5://208.102.51.6:58208", "socks5", "208.102.51.6", 58208, None, None),
        ("socks5://127.0.0.1", "socks5", "127.0.0.1", 1080, None, None),
        ("socks4://10.0.0.1:9050", "socks4", "10.0.0.1", 9050, None, None),
        ("http://proxy.local:3128", "http", "proxy.local", 3128, None, None),
        ("https://proxy.local:8443", "https", "proxy.local", 8443, None, None),
        ("socks5://user:p%40ss@host:1080", "socks5", "host", 1080, "user", "p@ss"),
    ],
)
def test_parse_proxy_accepts_what_the_bot_accepts(url, scheme, host, port, user, password):
    assert parse_proxy(url) == (scheme, host, port, user, password)


@pytest.mark.parametrize(
    "url,fragment",
    [
        ("", "пустая"),
        ("208.102.51.6:58208", "схема"),
        ("ftp://host:21", "схема"),
        ("socks5://", "хост"),
    ],
)
def test_parse_proxy_explains_a_wrong_string(url, fragment):
    with pytest.raises(ProxyError) as info:
        parse_proxy(url)
    assert fragment in str(info.value)


def test_proxy_hint_shows_the_line_for_each_editor():
    text = proxy_hint("socks5://1.2.3.4:1080")
    assert 'bot proxy "socks5://1.2.3.4:1080"' in text
    assert 'proxy("socks5://1.2.3.4:1080")' in text
    assert "TG_PROXY=socks5://1.2.3.4:1080" in text


# ---------------------------------------------------------- the handshakes
class FakeSocket:
    """A stream: replies are concatenated and handed out size by size."""

    def __init__(self, replies):
        self.buffer = b"".join(replies)
        self.sent = b""
        self.closed = False

    def sendall(self, data):
        self.sent += data

    def recv(self, size):
        chunk, self.buffer = self.buffer[:size], self.buffer[size:]
        return chunk

    def settimeout(self, value):
        self.timeout = value

    def close(self):
        self.closed = True


def fake_network(monkeypatch, sock, tls_reply=b"HTTP/1.1 400 Bad Request\r\n\r\n"):
    def create_connection(address, timeout=None):
        sock.address = address
        return sock

    class FakeTLS(FakeSocket):
        def __init__(self):
            super().__init__([])

        def recv(self, size):
            return tls_reply[:size]

    tls = FakeTLS()
    context = SimpleNamespace(
        wrap_socket=lambda raw, server_hostname=None: tls
    )
    monkeypatch.setattr(socket, "create_connection", create_connection)
    monkeypatch.setattr(ssl, "create_default_context", lambda: context)
    return sock, tls


def test_socks5_handshake_is_exactly_what_the_bot_sends(monkeypatch):
    sock = FakeSocket([
        b"\x05\x00",              # method: no auth
        b"\x05\x00\x00\x01",      # connect granted
    ])
    fake_network(monkeypatch, sock)

    works, message, _ = check_proxy("socks5://1.2.3.4:1080", timeout=3)

    assert works is True, message
    assert sock.address == ("1.2.3.4", 1080)
    expected = (b"\x05\x01\x00"
                b"\x05\x01\x00\x03" + bytes([len("api.telegram.org")])
                + b"api.telegram.org" + (443).to_bytes(2, "big"))
    assert sock.sent.startswith(expected)


def test_socks5_with_password_sends_the_credentials(monkeypatch):
    sock = FakeSocket([b"\x05\x02", b"\x01\x00", b"\x05\x00\x00\x01"])
    fake_network(monkeypatch, sock)

    works, message, _ = check_proxy("socks5://user:secret@1.2.3.4:1080")

    assert works is True, message
    # RFC 1929: version 1, length-prefixed user name, then password.
    assert sock.sent.startswith(b"\x05\x02\x00")
    assert b"\x01\x04user\x06secret" in sock.sent


def test_socks5_refusal_is_reported_in_words(monkeypatch):
    sock = FakeSocket([b"\x05\x00", b"\x05\x05\x00\x01"])  # connection refused
    fake_network(monkeypatch, sock)

    works, message, _ = check_proxy("socks5://1.2.3.4:1080")

    assert works is False
    assert "не пустил" in message
    assert "отклонено" in message


def test_http_proxy_uses_connect_and_reports_a_refusal(monkeypatch):
    sock = FakeSocket([b"HTTP/1.1 407 Proxy Authentication Required\r\n\r\n"])
    fake_network(monkeypatch, sock)

    works, message, _ = check_proxy("http://1.2.3.4:3128")

    assert works is False
    assert "отказ" in message
    assert sock.sent.startswith(b"CONNECT api.telegram.org:443 HTTP/1.1")


def test_socks4_handshake(monkeypatch):
    sock = FakeSocket([b"\x00\x5a\x00\x00\x00\x00\x00\x00"])
    fake_network(monkeypatch, sock)
    monkeypatch.setattr(socket, "gethostbyname", lambda host: "149.154.167.220")

    works, message, _ = check_proxy("socks4://1.2.3.4:1080")

    assert works is True, message
    assert sock.sent == (b"\x04\x01" + struct.pack(">H", 443)
                         + socket.inet_aton("149.154.167.220") + b"\x00")


def test_a_dead_proxy_is_reported_without_raising(monkeypatch):
    def refuse(address, timeout=None):
        raise TimeoutError("timed out")

    monkeypatch.setattr(socket, "create_connection", refuse)

    works, message, seconds = check_proxy("socks5://208.102.51.6:58208", timeout=2)

    assert works is False
    assert "нет соединения" in message
    assert "208.102.51.6:58208" in message


# ------------------------------------------------------------------ the command
def test_proxy_command_reports_a_working_proxy(monkeypatch, capsys):
    monkeypatch.setattr("tgblocks.network.check_proxy",
                        lambda url, timeout=8.0: (True, "работает: HTTP/1.1 400", 0.4))
    code = main(["proxy", "socks5://1.2.3.4:1080"])
    out = capsys.readouterr().out
    assert code == 0
    assert "OK" in out
    assert 'bot proxy "socks5://1.2.3.4:1080"' in out


def test_proxy_command_fails_on_a_dead_proxy(monkeypatch, capsys):
    monkeypatch.setattr("tgblocks.network.check_proxy",
                        lambda url, timeout=8.0: (False, "нет соединения", 2.0))
    code = main(["proxy", "socks5://1.2.3.4:1080"])
    assert code == 1
    assert "FAIL" in capsys.readouterr().out


def test_proxy_command_explains_a_bad_string(capsys):
    code = main(["proxy", "1.2.3.4:1080"])
    assert code == 1
    assert "схема" in capsys.readouterr().err


def test_proxy_command_uses_the_environment(monkeypatch, capsys):
    monkeypatch.setenv("TG_PROXY", "socks5://9.9.9.9:1080")
    monkeypatch.setattr("tgblocks.network.check_proxy",
                        lambda url, timeout=8.0: (True, "работает", 0.1))
    code = main(["proxy"])
    assert code == 0
    assert "9.9.9.9" in capsys.readouterr().out


def test_proxy_command_without_anything_says_how(capsys, monkeypatch):
    monkeypatch.delenv("TG_PROXY", raising=False)
    code = main(["proxy"])
    assert code == 2
    assert "tgblocks proxy" in capsys.readouterr().err
