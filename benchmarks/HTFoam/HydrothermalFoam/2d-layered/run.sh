#!/bin/sh
# Run a fresh copy; source inputs and previous results are never cleaned.
exec python3 "$(dirname "$0")/../../run.py" --case 2d-layered "$@"
