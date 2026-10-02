#!/usr/bin/env bash
set -euo pipefail
python3 "$(dirname "${BASH_SOURCE[0]}")/test_fresh_reader.py"
