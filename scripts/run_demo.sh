#!/usr/bin/env bash
# Shell helper to run the demo and display the report
set -euo pipefail
PYTHONPATH=$(pwd)
export PYTHONPATH
python demo_presentation_clean.py
if [ -f demo_report.md ]; then
  less demo_report.md
else
  echo "demo_report.md not found"
fi
