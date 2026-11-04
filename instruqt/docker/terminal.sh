#!/bin/bash
set -euo pipefail
printf '\033[2J\033[H\033[1;32m'
cat <<'BANNER'
        .   *       .         *
     *      ZIGGY ONLINE     .
       .       (o o)     *
              /|___|\
             / |   | \

  Your terminal is receiving live output.
  No commands needed. Just look at the clock.
  Return to Launchpad and confirm when it ticks.

BANNER
printf '\033[0m'
while true; do
  printf '\r  Radio clock: %s UTC   ' "$(date -u +%H:%M:%S)"
  sleep 1
done
