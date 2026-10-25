#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
PYTHON="$REPO_ROOT/koubo-roughcut/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  echo "Python environment not found: $PYTHON" >&2
  echo "Create the environment and install requirements first. See README.md." >&2
  read -r -p "Press Return to close..."
  exit 1
fi

"$PYTHON" "$SCRIPT_DIR/launch_review.py"
status=$?
if [[ $status -ne 0 ]]; then read -r -p "Press Return to close..."; fi
exit "$status"
