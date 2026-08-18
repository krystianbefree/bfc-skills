"""
Terminal Claude Code wewnątrz panelu.

Serwer podnosi pseudoterminal (PTY), odpala w nim Claude Code w katalogu
projektu i przekazuje bajty w obie strony przez WebSocket. Efekt jest ten sam,
co w terminalu VS Code - łącznie z pytaniami o uprawnienia, bo to pełna sesja
interaktywna, a nie tryb headless.

Bezpieczeństwo:
  * serwer słucha wyłącznie na 127.0.0.1,
  * uruchamiamy **wyłącznie** komendę z configu, nigdy tego, co przyjdzie z sieci,
  * sprawdzamy nagłówek `Origin` - WebSocket nie podlega polityce same-origin,
    więc bez tego dowolna strona otwarta w przeglądarce mogłaby dostać terminal.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import signal
import struct
import subprocess
from pathlib import Path
from typing import List, Optional

from loguru import logger

# PTY, fcntl i termios istnieją tylko na systemach POSIX (macOS, Linux). Na
# Windows sam ich import wywaliłby cały serwer już na starcie - a panel ma tam
# działać, tylko bez zakładki Terminal. Dlatego importujemy je warunkowo, a
# TerminalSession na nie-POSIX rzuca czytelny błąd zamiast kłaść import.
_POSIX = os.name == "posix"
if _POSIX:
    import fcntl
    import pty
    import termios

from engine.config import PROJECT_ROOT, Config

# Rozszerzenie VS Code trzyma binarkę tutaj; numer wersji rośnie z każdą
# aktualizacją, więc bierzemy najnowszy katalog zamiast zaszywać ścieżkę.
_VSCODE_EXT_GLOB = ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude"


def child_env(cfg: Config) -> dict:
    """
    Czyste środowisko dla uruchamianego Claude Code.

    Jeśli panel wystartował z wnętrza sesji Claude Code, środowisko jest pełne
    zmiennych `CLAUDE_CODE_*`. Dziecko bierze je za oznakę sesji potomnej
    i kończy działanie od razu. Dlatego czyścimy je zawsze.

    Klucz `ANTHROPIC_API_KEY` też zdejmujemy: w czacie wymusiłby rozliczanie po
    API zamiast normalnej subskrypcji. Włączysz go z powrotem przez `chat.use_api_key`.
    """
    env = os.environ.copy()

    for name in list(env):
        if name == "CLAUDECODE" or name.startswith(("CLAUDE_CODE_", "CLAUDE_AGENT_SDK_")):
            del env[name]
    for name in ("CLAUDE_PID", "CLAUDE_EFFORT"):
        env.pop(name, None)

    if not cfg.get("chat.use_api_key", False):
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("ANTHROPIC_AUTH_TOKEN", None)

    return env


def resolve_command(cfg: Config) -> List[str]:
    """Znajduje binarkę Claude Code: config -> PATH -> rozszerzenie VS Code."""
    configured = cfg.get("terminal.command")
    if configured:
        return configured if isinstance(configured, list) else [str(configured)]

    on_path = shutil.which("claude")
    if on_path:
        return [on_path]

    candidates = sorted(Path.home().glob(_VSCODE_EXT_GLOB))
    if candidates:
        return [str(candidates[-1])]

    raise RuntimeError(
        "Nie znalazłem Claude Code. Zainstaluj CLI (`npm i -g @anthropic-ai/claude-code`) "
        "albo wskaż ścieżkę w `terminal.command` w dashboard.config.yaml."
    )


def origin_allowed(origin: Optional[str], cfg: Config, port: int) -> bool:
    """
    Wpuszczamy tylko panel z tej maszyny.

    Obsidian osadza panel w webview, które potrafi nie wysłać `Origin` albo
    podać `app://obsidian.md` - oba przypadki są na liście dozwolonych.
    """
    if origin is None or origin == "null":
        return bool(cfg.get("terminal.allow_missing_origin", True))

    allowed = {
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}",
        "app://obsidian.md",
        "capacitor://obsidian.md",
    }
    allowed.update(cfg.get("terminal.allowed_origins", []) or [])
    return origin in allowed


class TerminalSession:
    """Jedna sesja: proces w PTY plus mostek do WebSocketu."""

    def __init__(self, command: List[str], cwd: Path, cols: int = 100, rows: int = 30,
                 env: Optional[dict] = None) -> None:
        self.command = command
        self.cwd = cwd
        self.env = env
        self.master_fd: Optional[int] = None
        self.proc: Optional[subprocess.Popen] = None
        self._cols = cols
        self._rows = rows

    def start(self) -> None:
        if not _POSIX:
            raise RuntimeError(
                "Terminal w panelu działa tylko na macOS i Linux. Na Windows "
                "korzystaj z zakładki Czat albo odpal Claude Code w osobnym oknie."
            )
        master, slave = pty.openpty()
        self.master_fd = master
        self.resize(self._rows, self._cols)

        env = self.env or os.environ.copy()
        env.setdefault("TERM", "xterm-256color")
        env["COLUMNS"] = str(self._cols)
        env["LINES"] = str(self._rows)
        env.pop("BROWSER", None)

        self.proc = subprocess.Popen(
            self.command,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            cwd=str(self.cwd),
            env=env,
            preexec_fn=os.setsid,
            close_fds=True,
        )
        os.close(slave)
        os.set_blocking(master, False)
        logger.info(f"Terminal: {' '.join(self.command)} (pid {self.proc.pid})")

    def resize(self, rows: int, cols: int) -> None:
        self._rows, self._cols = max(1, rows), max(1, cols)
        if self.master_fd is None:
            return
        packed = struct.pack("HHHH", self._rows, self._cols, 0, 0)
        try:
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, packed)
        except OSError as exc:
            logger.debug(f"Terminal: zmiana rozmiaru nie wyszła: {exc}")

    def write(self, data: str) -> None:
        if self.master_fd is None:
            return
        try:
            os.write(self.master_fd, data.encode("utf-8"))
        except OSError as exc:
            logger.debug(f"Terminal: zapis nie wyszedł: {exc}")

    def stop(self) -> None:
        """Ubija całą grupę procesów - sam SIGTERM na pid zostawiłby dzieci."""
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                self.proc.wait(timeout=1.5)
            except (ProcessLookupError, subprocess.TimeoutExpired):
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass
            except OSError:
                pass
        if self.master_fd is not None:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
            self.master_fd = None
        logger.info("Terminal: sesja zamknięta")


async def pump_output(session: TerminalSession, send) -> None:
    """Przepisuje wyjście PTY do WebSocketu przez `add_reader` na deskryptorze."""
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue = asyncio.Queue()
    fd = session.master_fd
    if fd is None:
        return

    def on_readable() -> None:
        try:
            data = os.read(fd, 65536)
        except BlockingIOError:
            return
        except OSError:
            queue.put_nowait(None)
            return
        queue.put_nowait(data if data else None)

    loop.add_reader(fd, on_readable)
    try:
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            await send(chunk.decode("utf-8", errors="replace"))
    finally:
        try:
            loop.remove_reader(fd)
        except (OSError, ValueError):
            pass


def default_cwd(cfg: Config) -> Path:
    configured = cfg.get("terminal.cwd")
    return cfg.path(configured) if configured else PROJECT_ROOT
