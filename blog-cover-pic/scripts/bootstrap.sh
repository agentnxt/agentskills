#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$BASE_DIR/.venv"

if [ -x "$VENV_DIR/bin/python" ]; then
  echo "Virtual environment already exists at $VENV_DIR"
  exit 0
fi

echo "Creating virtual environment at $VENV_DIR ..."
python3 -m venv "$VENV_DIR"

echo "Installing Pillow ..."
"$VENV_DIR/bin/pip" install --quiet Pillow

echo "Bootstrap complete. Python: $VENV_DIR/bin/python"
