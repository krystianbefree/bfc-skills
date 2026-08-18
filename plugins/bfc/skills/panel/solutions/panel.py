#!/usr/bin/env python3
"""
Launcher panelu - działa tak samo na macOS, Linux i Windows.

Jedna komenda: `python panel.py`. Skrypt sam zakłada środowisko `.venv`,
doinstalowuje zależności, jeśli ich brak, i odpala serwer na 127.0.0.1.
Nietechniczny klubowicz nie musi znać venv ani pip - to się dzieje samo.

Zmienne środowiskowe (opcjonalne):
  DASHBOARD_PORT          port (domyślnie 8765)
  DASHBOARD_CONFIG        ścieżka do dashboard.config.yaml
  DASHBOARD_PROJECT_ROOT  katalog projektu (.env, skan .claude)
  DASHBOARD_DATA          katalog na cache i kopie zapasowe
"""
from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENV = HERE / ".venv"
REQ = HERE / "requirements.txt"


def _venv_python(base: Path) -> Path:
    """Ścieżka do interpretera w venv - inna na Windows niż na POSIX."""
    if os.name == "nt":
        return base / "Scripts" / "python.exe"
    return base / "bin" / "python"


def _ensure_venv() -> Path:
    py = _venv_python(VENV)
    if not py.exists():
        print("Zakładam środowisko (.venv). Chwilę to potrwa przy pierwszym razie...")
        try:
            venv.EnvBuilder(with_pip=True).create(str(VENV))
        except Exception as exc:  # noqa: BLE001
            sys.exit(
                f"Nie udało się utworzyć .venv: {exc}\n"
                "Na Linuxie może brakować pakietu `python3-venv` "
                "(zainstaluj: sudo apt install python3-venv)."
            )

    # Czy zależności są? uvicorn + fastapi wystarczą jako papierek lakmusowy.
    check = subprocess.run(
        [str(py), "-c", "import uvicorn, fastapi, yaml, dotenv"],
        capture_output=True,
    )
    if check.returncode != 0:
        print("Instaluję zależności panelu...")
        try:
            subprocess.check_call([str(py), "-m", "pip", "install", "-q", "--upgrade", "pip"])
            subprocess.check_call([str(py), "-m", "pip", "install", "-q", "-r", str(REQ)])
        except subprocess.CalledProcessError as exc:
            sys.exit(
                f"Instalacja zależności padła (kod {exc.returncode}). "
                "Sprawdź połączenie z internetem i spróbuj ponownie."
            )
    return py


def main() -> None:
    py = _ensure_venv()
    port = os.environ.get("DASHBOARD_PORT", "8765")
    print(f"Panel: http://127.0.0.1:{port}")
    print("Zatrzymanie: Ctrl+C")

    cmd = [str(py), "-m", "uvicorn", "engine.app:app", "--host", "127.0.0.1", "--port", port]
    cmd += sys.argv[1:]  # np. --reload w dev

    # Silnik importuje pakiet `engine`, więc CWD musi widzieć katalog engine/.
    try:
        raise SystemExit(subprocess.call(cmd, cwd=str(HERE)))
    except KeyboardInterrupt:
        print("\nPanel zatrzymany.")


if __name__ == "__main__":
    main()
