#!/bin/bash
set -euo pipefail
mkdir -p /run/preflight
nohup /opt/venv/bin/python /opt/preflight/supervise.py \
  >> /run/preflight/supervisor.log 2>&1 < /dev/null &
# Warm the editor and gate lab creation on every required port.
for attempt in $(seq 1 90); do
  ready=true
  for endpoint in 5000/healthz 8080/ 8090/ziggy 8092/ziggy 8233/; do
    if ! curl --fail --silent --max-time 2 --output /dev/null "http://127.0.0.1:${endpoint}"; then ready=false; fi
  done
  if [ "$ready" = true ]; then exit 0; fi
  sleep 1
done
echo "Pre-flight services did not become ready. Check /run/preflight/*.log." >&2
tail -n 12 /run/preflight/supervisor.log /run/preflight/editor.log /run/preflight/temporal.log >&2
exit 1
