#!/usr/bin/env bash
# Compatibility entry point retained from the scaffold-ingestion delivery.
# The current cumulative gate also performs the formalization-aware Step-1
# reconciliation, while still refusing to start Step 2.
set -euo pipefail
exec bash "$(cd "$(dirname "$0")" && pwd)/rebuild_step1_completion.sh"
