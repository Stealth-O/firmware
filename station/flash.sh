#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Stealth-O

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
    echo "Usage: ./flash.sh <0-99>"
}

station_id_from_arg() {
    local value="$1"

    if [[ ! "${value}" =~ ^[0-9]{1,2}$ ]]; then
        echo "Station ID must be a number from 0 to 99." >&2
        return 1
    fi

    local station_id=$((10#${value}))
    if [ "${station_id}" -lt 0 ] || [ "${station_id}" -gt 99 ]; then
        echo "Station ID must be a number from 0 to 99." >&2
        return 1
    fi

    echo "${station_id}"
}

target="${1:-}"
if [ -z "${target}" ]; then
    usage
    exit 1
fi

station_id="$(station_id_from_arg "${target}")"
station_label="$(printf "S%02d" "${station_id}")"
UF2_PATH="${SCRIPT_DIR}/station-${station_label}.uf2"

if [ ! -f "${UF2_PATH}" ]; then
    echo "Missing station-${station_label}.uf2 next to flash.sh."
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
    echo "Double-press Reset on the XIAO board, wait for the drive to appear, then rerun ./flash.sh ${station_id}."
    exit 1
fi

if [ "${#volumes[@]}" -gt 1 ]; then
    echo "Multiple UF2 drives found:"
    printf '  %s\n' "${volumes[@]}"
    echo "Set UF2_VOLUME=\"/Volumes/BOARDNAME\" and rerun ./flash.sh ${station_id}."
    exit 1
fi

cp -X "${UF2_PATH}" "${volumes[0]}/"
sync
echo "Flashed ${UF2_PATH} to ${volumes[0]}"
echo "Station ID: ${station_id}"
