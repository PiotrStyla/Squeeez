#!/usr/bin/env bash
set -euo pipefail

cd /root/hutter/paq8px

TS=$(date -Is)

PID=$(pgrep -n paq8px 2>/dev/null || true)
if [ -z "$PID" ]; then
  PID=$(pidof paq8px 2>/dev/null | awk '{print $1}' || true)
fi

PINFO="no_proc"
if [ -n "$PID" ]; then
  PINFO=$(ps -p "$PID" -o etime=,pcpu=,pmem=,nlwp=,cmd= 2>/dev/null | tr -s ' ' | sed 's/^ //')
fi

PCT=$( (command -v perl >/dev/null 2>&1 && perl -0777 -pe '1 while s/.\x08//g; s/\r//g' compression.log 2>/dev/null) || (tr -d '\r' < compression.log 2>/dev/null) | grep -aoE 'Compressing\.\.\.\s*[0-9]+(\.[0-9]+)?%' | tail -1 || true )
OUTSIZE=$(stat -c %s final_netcup_enwik9.paq8 2>/dev/null || echo 0)

printf '%s | pid=%s | out_bytes=%s | %s | %s\n' "$TS" "${PID:-none}" "$OUTSIZE" "${PCT:-no_pct}" "$PINFO" >> status_history.log
