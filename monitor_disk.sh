#!/usr/bin/env bash
set -euo pipefail

cd /root/hutter/paq8px

TS=$(date -Is)

OUT=$(ls -lh final_netcup_enwik9.paq8 2>/dev/null || echo 'no_output')
DISK=$(df -h /root | tail -1)
UP=$(uptime -p 2>/dev/null || uptime)

printf '%s | %s | %s | %s\n' "$TS" "$OUT" "$DISK" "$UP" >> disk_history.log
