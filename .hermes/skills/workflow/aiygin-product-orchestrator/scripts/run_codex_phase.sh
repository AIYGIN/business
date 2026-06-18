#!/usr/bin/env bash
set -euo pipefail

# Render a phase prompt and run Codex in the target repository.
# Usage:
#   run_codex_phase.sh <repo-dir> <phase> [render_prompt.py args...]
# Example:
#   run_codex_phase.sh ~/git/bff bff-issue-draft --business-url https://github.com/AIYGIN/business/issues/1 --input-file /tmp/delegation.md

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <repo-dir> <phase> [render_prompt.py args...]" >&2
  exit 2
fi

REPO_DIR="$1"
PHASE="$2"
shift 2

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="$(mktemp -t aiygin-${PHASE}.XXXXXX.md)"
trap 'rm -f "$PROMPT_FILE"' EXIT

python3 "$SCRIPT_DIR/render_prompt.py" --phase "$PHASE" "$@" > "$PROMPT_FILE"

cd "$REPO_DIR"
command -v codex >/dev/null || { echo "codex CLI が見つかりません" >&2; exit 1; }
command -v gh >/dev/null || { echo "gh CLI が見つかりません" >&2; exit 1; }
gh auth status >/dev/null

# Codex は対話 CLI なので、Hermes から呼ぶ場合は terminal(..., pty=true) でこの script を実行する。
codex exec --full-auto "$(<"$PROMPT_FILE")"
