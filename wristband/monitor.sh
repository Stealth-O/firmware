#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Stealth-O

set -euo pipefail

BAUD_RATE="${BAUD_RATE:-115200}"
SERIAL_PORT="${SERIAL_PORT:-}"

matches=()
ports=(/dev/cu.usbmodem* /dev/cu.usbserial*)

if [ -n "${SERIAL_PORT}" ]; then
    matches=("${SERIAL_PORT}")
else
    for port in "${ports[@]}"; do
        if [ -e "${port}" ]; then
            matches+=("${port}")
        fi
    done
fi

if [ "${#matches[@]}" -eq 0 ]; then
    echo "No serial device found."
    echo "Connect the wristband over USB-C and rerun ./monitor.sh."
    exit 1
fi

if [ "${#matches[@]}" -gt 1 ]; then
    echo "Multiple serial devices found:"
    printf '  %s\n' "${matches[@]}"
    echo "Set SERIAL_PORT=/dev/cu.usbmodem... or disconnect extra devices."
    exit 1
fi

PORT="${matches[0]}"

if [ ! -e "${PORT}" ]; then
    echo "Serial device not found: ${PORT}"
    exit 1
fi

cleanup() {
    if [ -n "${reader_pid:-}" ]; then
        kill "${reader_pid}" 2>/dev/null || true
        wait "${reader_pid}" 2>/dev/null || true
    fi
    exec 3>&- 2>/dev/null || true
    exec 3<&- 2>/dev/null || true
}

trap cleanup EXIT
trap 'cleanup; exit 130' INT TERM

echo "Opening serial monitor on ${PORT} at ${BAUD_RATE} baud."
echo "Commands: i, s, c, p, b. Press Ctrl-C to exit."

stty -f "${PORT}" "${BAUD_RATE}" cs8 -cstopb -parenb raw -echo
exec 3<>"${PORT}"

cat <&3 &
reader_pid=$!

while IFS= read -r command; do
    printf '%s\n' "${command}" >&3
done
