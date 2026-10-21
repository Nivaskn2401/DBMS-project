#!/bin/bash
set -e
cd "$(dirname "$0")"
echo "Starting Libra Library Management System..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Install Python 3 from https://www.python.org/downloads/macos/ and try again."
  read -r -p "Press Return to close..."
  exit 1
fi
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
