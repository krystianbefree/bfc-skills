"""
Ładowanie i walidacja `dashboard.config.yaml`.

Config jest jedynym miejscem, które zmieniasz budując panel pod swój biznes -
kod adapterów nigdy nie zawiera nazw etapów ani progów.

Ścieżki są env-overridable, bo silnik jest kopiowany do projektu użytkownika:
  * DASHBOARD_CONFIG        - ścieżka do configu (domyślnie ./dashboard.config.yaml)
  * DASHBOARD_PROJECT_ROOT  - katalog projektu (domyślnie CWD) - .env i skan .claude
  * DASHBOARD_DATA          - katalog na cache i kopie zapasowe (domyślnie <engine>/data)
Bazę plików sejfu Obsidiana bierzemy z klucza `sejf` w configu, NIE z PROJECT_ROOT.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv

# Katalog projektu użytkownika: .env, skan lokalnych .claude. Env-overridable.
PROJECT_ROOT = Path(os.getenv("DASHBOARD_PROJECT_ROOT") or Path.cwd()).resolve()
# Katalog samego silnika - fallback dla danych cache/backup.
ENGINE_DIR = Path(__file__).resolve().parent
# Cache i kopie zapasowe. Nie idą do sejfu ani do repo pluginu.
DATA_DIR = Path(os.getenv("DASHBOARD_DATA") or (ENGINE_DIR / "data")).resolve()

# Adaptery nie mogą liczyć na to, że ktoś załadował .env. Robimy to raz.
load_dotenv(PROJECT_ROOT / ".env", override=True)


def _config_path() -> Path:
    return Path(os.getenv("DASHBOARD_CONFIG") or (Path.cwd() / "dashboard.config.yaml"))


class Config:
    """Cienka nakładka na słownik z configu - z domyślnymi wartościami."""

    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw

    # ── dostęp ogólny ────────────────────────────────────────────────────
    def get(self, path: str, default: Any = None) -> Any:
        """Pobiera wartość po ścieżce z kropkami, np. `signals.dni_bez_kontaktu`."""
        node: Any = self.raw
        for part in path.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    # ── skróty najczęściej używane ───────────────────────────────────────
    @property
    def owner(self) -> Dict[str, Any]:
        return self.raw.get("owner", {})

    @property
    def stages(self) -> List[Dict[str, str]]:
        """Etapy lejka pozyskiwania."""
        return self.get("pipeline.stages", [])

    @property
    def stage_ids(self) -> List[str]:
        return [s["id"] for s in self.stages]

    def stage_label(self, stage_id: str) -> str:
        for s in self.stages:
            if s["id"] == stage_id:
                return s["label"]
        return stage_id

    def source_enabled(self, name: str) -> bool:
        return bool(self.get(f"sources.{name}.enabled", False))

    def source_ttl(self, name: str) -> int:
        """TTL cache w minutach. 0 = czytaj zawsze na świeżo."""
        return int(self.get(f"sources.{name}.ttl_minutes", 0) or 0)

    # ── ścieżki ──────────────────────────────────────────────────────────
    def path(self, relative: str) -> Path:
        """Ścieżka względem katalogu projektu (dla skanu .claude, skryptów)."""
        return PROJECT_ROOT / relative

    @property
    def sejf(self) -> Path:
        """Baza sejfu Obsidiana - z klucza `sejf` w configu."""
        base = self.get("sejf")
        if not base:
            raise FileNotFoundError(
                "Brak klucza `sejf` w configu. Ustaw ścieżkę bazową sejfu Obsidiana."
            )
        return Path(str(base)).expanduser()

    def sejf_path(self, relative: str) -> Path:
        """Ścieżka pliku MD w sejfie, względem bazy `sejf`."""
        return self.sejf / str(relative)


@lru_cache(maxsize=1)
def load_config(path: Optional[str] = None) -> Config:
    """Wczytuje config raz na proces (serwer restartuje się przy zmianie w dev)."""
    cfg_path = Path(path) if path else _config_path()
    if not cfg_path.exists():
        raise FileNotFoundError(
            f"Brak pliku konfiguracyjnego: {cfg_path}. "
            "Skopiuj dashboard.config.example.yaml i wskaż go przez DASHBOARD_CONFIG."
        )
    with cfg_path.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return Config(raw)


def reload_config() -> Config:
    """Czyści cache i wczytuje config ponownie - używane przez endpoint /api/reload."""
    load_config.cache_clear()
    return load_config()


def env(name: str, default: str = "") -> str:
    """Zmienna środowiskowa z .env."""
    return os.getenv(name, default) or default
