#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Stealth-O

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
USAGE="Usage: ./flash.sh <xiao-external|xiao-internal|xiao-lora-external|xiao-lora-internal|t096-internal>"

if [ "$#" -ne 1 ]; then
    echo "${USAGE}" >&2
    exit 2
fi
PROFILE="$1"
EXPECTED_BOARD_IDS=()

case "${PROFILE}" in
    xiao-external|xiao-internal|xiao-lora-external|xiao-lora-internal)
        # Board-ID strings reported by the stock Seeeduino nRF52 and upstream
        # OTAFIX bootloaders.
        EXPECTED_BOARD_IDS=(
            "Seeed_XIAO_nRF52840"
            "Seeed_XIAO_nRF52840_Sense"
            "nRF52840-SeeedXiao-v1"
            "nRF52840-SeeedXiaoSense-v1"
        )
        ;;
    t096-internal)
        EXPECTED_BOARD_IDS=("HT-n5262")
        ;;
    *)
        echo "${USAGE}" >&2
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
    if [ "${PROFILE}" = "t096-internal" ]; then
        echo "Double-press Reset on the T096, wait for the drive to appear, then rerun ./flash.sh."
    else
        echo "Double-press Reset on the XIAO board, wait for the drive to appear, then rerun ./flash.sh."
    fi
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
    echo "Refusing to flash ${PROFILE} to Board-ID '${resolved_board_id:-missing}'." >&2
    echo "Expected one of: ${EXPECTED_BOARD_IDS[*]}" >&2
    exit 1
fi

cp -X "${UF2_PATH}" "${TARGET_VOLUME}/"
sync
echo "Flashed ${UF2_PATH} to ${TARGET_VOLUME}"
