#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Stealth-O

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MAX_STATION_ID=254

usage() {
    echo "Usage: ./flash.sh <0-254>"
}

station_id_from_arg() {
    local value="$1"

    if [[ ! "${value}" =~ ^[0-9]{1,3}$ ]]; then
        echo "Station ID must be a number from 0 to ${MAX_STATION_ID}." >&2
        return 1
    fi

    local station_id=$((10#${value}))
    if [ "${station_id}" -lt 0 ] || [ "${station_id}" -gt "${MAX_STATION_ID}" ]; then
        echo "Station ID must be a number from 0 to ${MAX_STATION_ID}." >&2
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

TARGET_VOLUME="${volumes[0]}"
if [ ! -f "${TARGET_VOLUME}/INFO_UF2.TXT" ]; then
    echo "Selected target is not a mounted UF2 bootloader: ${TARGET_VOLUME}" >&2
    exit 1
fi

# Board-ID strings reported by the pinned Seeeduino nrf52 bootloaders
# (0.6.x updates ship both naming schemes). Stations are XIAO-only.
EXPECTED_BOARD_IDS=(
    "Seeed_XIAO_nRF52840"
    "Seeed_XIAO_nRF52840_Sense"
    "nRF52840-SeeedXiao-v1"
    "nRF52840-SeeedXiaoSense-v1"
)
resolved_board_id="$(
    sed -n 's/^Board-ID:[[:space:]]*//p' "${TARGET_VOLUME}/INFO_UF2.TXT" \
        | tr -d '\r' \
        | head -n 1
)"
board_id_allowed=false
for expected_board_id in "${EXPECTED_BOARD_IDS[@]}"; do
    if [ "${resolved_board_id}" = "${expected_board_id}" ]; then
        board_id_allowed=true
        break
    fi
done
if [ "${board_id_allowed}" = false ]; then
    echo "Refusing to flash station ${station_id} to Board-ID '${resolved_board_id:-missing}'." >&2
    echo "Expected one of: ${EXPECTED_BOARD_IDS[*]}" >&2
    exit 1
fi

cp -X "${UF2_PATH}" "${TARGET_VOLUME}/"
sync
echo "Flashed ${UF2_PATH} to ${TARGET_VOLUME}"
echo "Station ID: ${station_id}"
