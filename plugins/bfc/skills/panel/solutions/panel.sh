#!/usr/bin/env bash
# Uruchamia panel dowodzenia na localhost (macOS / Linux).
# Cała logika bootstrapu (venv, zależności) siedzi w panel.py, żeby macOS i
# Windows startowały tak samo. Ten plik to tylko wygodne wejście z basha.
#
# Zmienne środowiskowe: DASHBOARD_PORT, DASHBOARD_CONFIG, DASHBOARD_PROJECT_ROOT,
# DASHBOARD_DATA - opis w panel.py.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3 || command -v python || true)"

if [ -z "$PY" ]; then
  echo "Nie znalazłem Pythona. Zainstaluj Python 3.11+ i spróbuj ponownie." >&2
  exit 1
fi

exec "$PY" "$HERE/panel.py" "$@"
