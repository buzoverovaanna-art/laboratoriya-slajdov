"""PDF из готовой презентации: скрытый Chrome «печатает» страницу, по одному слайду на лист 16:9.

Текст в PDF настоящий — его можно выделять и копировать. Chrome управляется напрямую (протокол
DevTools через сокет), без дополнительных библиотек. Размер листа задаём сами: если оставить
стандартный, Chrome включает телефонную раскладку и ломает вёрстку.
Сам файл работы на диске не меняется.
"""

import base64
import json
import os
import shutil
import signal
import socket
import struct
import subprocess
import tempfile
import time
import urllib.request

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W, H = 1280, 720  # размер слайда в пикселях; в PDF — лист 16:9

PRINT_CSS = """
<style id="print-pdf">
  @page { size: 1280px 720px; margin: 0; }
  html, body { height: auto !important; overflow: visible !important; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .slide { display: flex !important; height: 720px !important; overflow: hidden !important;
           break-after: page; page-break-after: always; }
  .hud, #notes, #game, #modal { display: none !important; }
  /* анимации появления: сразу конечное состояние, иначе в PDF всё прозрачное */
  *, *::before, *::after { animation-duration: 0s !important; animation-delay: 0s !important;
                           animation-fill-mode: forwards !important; transition: none !important; }
</style>
<script>
/* слайд не влезает в лист — чуть уменьшаем содержимое, чтобы ничего не обрезалось */
addEventListener('load', () => document.querySelectorAll('.slide').forEach(sl => {
  const wrap = sl.querySelector('.wrap');
  if (wrap) wrap.style.zoom = '';
  let z = 1;
  while (wrap && sl.scrollHeight > sl.clientHeight + 1 && z > 0.5) { z -= 0.03; wrap.style.zoom = z; }
}));
</script>
"""


def chrome_available() -> bool:
    return os.path.isfile(CHROME)


class _DevTools:
    """Минимальный клиент протокола DevTools: веб-сокет на стандартных средствах Python."""

    def __init__(self, ws_url: str):
        host_port, path = ws_url[len("ws://"):].split("/", 1)
        host, port = host_port.split(":")
        self.sock = socket.create_connection((host, int(port)), timeout=90)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET /{path} HTTP/1.1\r\nHost: {host_port}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise OSError("Chrome закрыл соединение")
            buf += chunk
        head, self.buf = buf.split(b"\r\n\r\n", 1)
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise OSError("Chrome не принял соединение")
        self.next_id = 0
        self.events = set()

    def _read(self, n: int) -> bytes:
        while len(self.buf) < n:
            chunk = self.sock.recv(1 << 20)
            if not chunk:
                raise OSError("Chrome закрыл соединение")
            self.buf += chunk
        data, self.buf = self.buf[:n], self.buf[n:]
        return data

    def _recv(self) -> dict:
        payload = b""
        while True:
            b1, b2 = self._read(2)
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack(">H", self._read(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", self._read(8))[0]
            data = self._read(length)
            op = b1 & 0x0F
            if op == 8:
                raise OSError("Chrome закрыл соединение")
            if op in (9, 10):  # служебные кадры «ping/pong»
                continue
            payload += data
            if b1 & 0x80:
                return json.loads(payload.decode("utf-8"))

    def _send(self, obj: dict) -> None:
        data = json.dumps(obj).encode("utf-8")
        head, n = bytearray([0x81]), len(data)
        if n < 126:
            head.append(0x80 | n)
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        head += mask
        self.sock.sendall(bytes(head) + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))

    def call(self, method: str, params: dict = None) -> dict:
        self.next_id += 1
        my_id = self.next_id
        self._send({"id": my_id, "method": method, "params": params or {}})
        while True:
            msg = self._recv()
            if "method" in msg:
                self.events.add(msg["method"])
            elif msg.get("id") == my_id:
                if "error" in msg:
                    raise OSError(f"{method}: {msg['error'].get('message')}")
                return msg.get("result", {})

    def wait_event(self, name: str, timeout: float = 60) -> None:
        end = time.time() + timeout
        while name not in self.events:
            if time.time() > end:
                raise OSError(f"не дождались события {name}")
            msg = self._recv()
            if "method" in msg:
                self.events.add(msg["method"])


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def _page_socket_url(port: int) -> str:
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=2) as r:
                for target in json.load(r):
                    if target.get("type") == "page" and target.get("webSocketDebuggerUrl"):
                        return target["webSocketDebuggerUrl"]
        except OSError:
            pass
        time.sleep(0.5)
    raise OSError("Chrome не запустился")


def make_pdf(html_path: str, pdf_path: str) -> bool:
    """Собирает PDF рядом с работой. True — получилось."""
    if not chrome_available():
        return False
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    html = html.replace('loading="lazy"', 'loading="eager"')  # иначе картинки догрузятся уже после печати
    html = html.replace("</head>", PRINT_CSS + "</head>", 1) if "</head>" in html else PRINT_CSS + html

    tmp = tempfile.mkdtemp(prefix="slides-pdf-")
    proc = None
    try:
        page = os.path.join(tmp, "print.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(html)
        port = _free_port()
        proc = subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--remote-debugging-port={port}",
             f"--user-data-dir={os.path.join(tmp, 'profile')}", f"--window-size={W},{H}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
        )
        tools = _DevTools(_page_socket_url(port))
        tools.call("Page.enable")
        tools.call("Emulation.setDeviceMetricsOverride", {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
        tools.call("Page.navigate", {"url": "file://" + page})
        tools.wait_event("Page.loadEventFired")
        time.sleep(1)  # картинки и подгонка слайдов
        result = tools.call("Page.printToPDF", {
            "paperWidth": W / 96, "paperHeight": H / 96, "printBackground": True,
            "marginTop": 0, "marginBottom": 0, "marginLeft": 0, "marginRight": 0, "preferCSSPageSize": True,
        })
        data = base64.b64decode(result["data"])
        if not data.startswith(b"%PDF"):
            return False
        tmp_pdf = os.path.join(tmp, "out.pdf")
        with open(tmp_pdf, "wb") as f:
            f.write(data)
        shutil.move(tmp_pdf, pdf_path)
        return True
    except (OSError, ValueError, KeyError, subprocess.SubprocessError):
        return False
    finally:
        if proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except OSError:
                pass
            proc.wait()
        shutil.rmtree(tmp, ignore_errors=True)
