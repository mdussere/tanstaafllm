#!/bin/sh
set -eu
ROOT=/home/michael/.local/share/tanstfaafllm/wyoh
exec /home/michael/.local/opt/wyoh-sway-1.10.1-test-20260926/usr/bin/sway --config "$ROOT/deploy/luna-pi/sway-vnc.conf"
