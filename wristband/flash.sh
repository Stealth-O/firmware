#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Stealth-O

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UF2_PATH="${SCRIPT_DIR}/wristband.uf2"

if [ ! -f "${UF2_PATH}" ]; then
    echo "Missing wristband.uf2 next to flash.sh."
    exit 1
fi

volumes=()

if [ -n "${UF2_VOLUME:-}" ]; then
    volumes=("${UF2_VOLUME}")
else
    for volume in /Volumes/*; do
        if [ -f "${volume}/INFO_UF2.TXT" ]; then
            volumes+=("${volume}")
        fi
    done
fi

if [ "${#volumes[@]}" -eq 0 ]; then
    echo "UF2 bootloader drive not found."
    echo "Double-press Reset on the XIAO board, wait for the drive to appear, then rerun ./flash.sh."
    exit 1
fi

if [ "${#volumes[@]}" -gt 1 ]; then
    echo "Multiple UF2 drives found:"
    printf '  %s\n' "${volumes[@]}"
    echo 'Set UF2_VOLUME="/Volumes/BOARDNAME" and rerun ./flash.sh.'
    exit 1
fi

cp -X "${UF2_PATH}" "${volumes[0]}/"
sync
echo "Flashed ${UF2_PATH} to ${volumes[0]}"
