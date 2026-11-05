#!/bin/sh
# Run a fresh copy; pass --output DIR (see the benchmark README).
exec python3 "$(dirname "$0")/../../../run.py" --case v2 "$@"
