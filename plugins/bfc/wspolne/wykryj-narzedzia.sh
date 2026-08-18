#!/usr/bin/env bash
# Wykrywa opcjonalne narzedzia, ktore pogłebiaja dzialanie skilli BFC.
# Wypisuje po jednej linii na narzedzie: nazwa=tak|nie
# Zawsze konczy sie kodem 0 - brak narzedzia to nie blad.

set -u

ma_firecrawl="nie"

# 1. Klient CLI w PATH.
if command -v firecrawl >/dev/null 2>&1; then
  ma_firecrawl="tak"
fi

# 2. Klucz w srodowisku.
if [ "${FIRECRAWL_API_KEY:-}" != "" ]; then
  ma_firecrawl="tak"
fi

# 3. Klucz w .env biezacego projektu. Czytamy wylacznie te jedna zmienna
#    i nigdy nie wypisujemy jej wartosci.
for plik in ".env" "${CLAUDE_PROJECT_DIR:-}/.env"; do
  [ -n "$plik" ] || continue
  [ -f "$plik" ] || continue
  if grep -qE '^[[:space:]]*(export[[:space:]]+)?FIRECRAWL_API_KEY[[:space:]]*=[[:space:]]*[^[:space:]"'"'"']' "$plik" 2>/dev/null; then
    ma_firecrawl="tak"
  fi
done

echo "firecrawl=${ma_firecrawl}"
exit 0
