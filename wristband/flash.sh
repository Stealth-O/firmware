#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Stealth-O

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$#" -ne 1 ]; then
    echo "Usage: ./flash.sh <xiao-external|xiao-internal|xiao-lora-external|xiao-lora-internal>" >&2
    exit 2
fi
PROFILE="$1"

case "${PROFILE}" in
    xiao-external|xiao-internal|xiao-lora-external|xiao-lora-internal)
        ;;
    *)
        echo "Usage: ./flash.sh <xiao-external|xiao-internal|xiao-lora-external|xiao-lora-internal>" >&2
        exit 2
        ;;
esac

UF2_PATH="${SCRIPT_DIR}/wristband-${PROFILE}.uf2"
if [ ! -f "${UF2_PATH}" ]; then
    echo "Missing $(basename "${UF2_PATH}") next to flash.sh." >&2
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

TARGET_VOLUME="${volumes[0]}"
if [ ! -f "${TARGET_VOLUME}/INFO_UF2.TXT" ]; then
    echo "Selected target is not a mounted UF2 bootloader: ${TARGET_VOLUME}" >&2
    exit 1
fi

cp -X "${UF2_PATH}" "${TARGET_VOLUME}/"
sync
echo "Flashed ${UF2_PATH} to ${TARGET_VOLUME}"
