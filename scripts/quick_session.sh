#!/usr/bin/env bash
# Convenience wrapper for run-once with the example personas.
# Usage:  ./scripts/quick_session.sh [turns]
set -euo pipefail

TURNS="${1:-8}"
ma-engine run-once \
  --m-spec data/personas/m.json \
  --a-spec data/personas/a.json \
  --turns "$TURNS"

