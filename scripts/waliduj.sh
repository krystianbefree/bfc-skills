#!/usr/bin/env bash
# Walidacja repo bfc-skills. Odpalaj przed kazdym pushem.
set -euo pipefail
exec python3 "$(dirname "$0")/waliduj.py" "$@"
