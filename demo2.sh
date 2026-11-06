#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/outbreak-explorer"
if command -v uv >/dev/null 2>&1; then
  uv venv --python 3.12 --allow-existing .venv
  uv pip install --python .venv/bin/python -r requirements.txt
else
  if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
  .venv/bin/python -m pip install -r requirements.txt
fi
exec .venv/bin/python -m streamlit run app.py "$@"
