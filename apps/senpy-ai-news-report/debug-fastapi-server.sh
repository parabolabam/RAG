#!/bin/sh
set -euo pipefail

echo "Once script run, please attach your debug session here"
poetry run python -m debugpy --listen localhost:5678 --wait-for-client -m senpy_ai_news_report.main
