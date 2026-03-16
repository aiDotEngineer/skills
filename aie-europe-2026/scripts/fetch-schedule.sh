#!/usr/bin/env bash
# Fetch and display the AI Engineer Europe 2026 schedule.
# Usage: bash scripts/fetch-schedule.sh [day]
# Example: bash scripts/fetch-schedule.sh "April 9"

set -euo pipefail

BASE="https://ai.engineer/europe"
DAY="${1:-}"

if [ -n "$DAY" ]; then
  echo "=== AI Engineer Europe 2026 — $DAY ==="
  curl -s "$BASE/sessions.json" | jq --arg day "$DAY" '
    .sessions
    | map(select(.day == $day))
    | sort_by(.time)
    | .[]
    | "\(.time // "?"): \(.title // "TBA") — \(.speakers | join(", "))"
  ' -r
else
  echo "=== AI Engineer Europe 2026 — Full Schedule ==="
  for d in "April 8" "April 9" "April 10"; do
    echo ""
    echo "--- $d ---"
    curl -s "$BASE/sessions.json" | jq --arg day "$d" '
      .sessions
      | map(select(.day == $day))
      | sort_by(.time)
      | .[]
      | "\(.time // "?"): \(.title // "TBA") — \(.speakers | join(", "))"
    ' -r
  done
fi
