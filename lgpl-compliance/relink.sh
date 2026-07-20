#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ARM_GCC_DIR="${HOME}/Library/Arduino15/packages/Seeeduino/tools/arm-none-eabi-gcc/9-2019q4"
ARM_GCC_DIR="${ARM_GCC_DIR:-${DEFAULT_ARM_GCC_DIR}}"
CORE_ARCHIVE=""
DEVICE="${1:-}"
LINKER_SCRIPT="nrf52840_s140_v7.ld"
OUTPUT_DIR="${SCRIPT_DIR}/output"
SPI_DIR=""
TEMP_DIR=""

case "${DEVICE}" in
    station|wristband-xiao-external|wristband-xiao-lora-external)
        ;;
    wristband-xiao-internal|wristband-xiao-lora-internal)
        LINKER_SCRIPT="nrf52840_s140_v7_wristband_internal.ld"
        ;;
    *)
        echo "Usage: ./relink.sh station|wristband-xiao-external|wristband-xiao-internal|wristband-xiao-lora-external|wristband-xiao-lora-internal [options]"
        echo "Options:"
        echo "  --arm-gcc-dir PATH"
        echo "  --core-a PATH"
        echo "  --output-dir PATH"
        echo "  --spi-dir PATH"
        exit 1
        ;;
esac
shift

while [ "$#" -gt 0 ]; do
    case "$1" in
        --arm-gcc-dir)
            ARM_GCC_DIR="$2"
            shift 2
            ;;
        --core-a)
            CORE_ARCHIVE="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --spi-dir)
            SPI_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

cleanup() {
    if [ -n "${TEMP_DIR}" ] && [ -d "${TEMP_DIR}" ]; then
        rm -rf "${TEMP_DIR}"
    fi
}

trap cleanup EXIT

GXX="${ARM_GCC_DIR}/bin/arm-none-eabi-g++"
OBJCOPY="${ARM_GCC_DIR}/bin/arm-none-eabi-objcopy"

if [ ! -x "${GXX}" ] || [ ! -x "${OBJCOPY}" ]; then
    echo "GNU Arm toolchain not found: ${ARM_GCC_DIR}" >&2
    exit 1
fi
if [ ! -f "${SCRIPT_DIR}/tools/${LINKER_SCRIPT}" ]; then
    echo "Linker script not found: ${SCRIPT_DIR}/tools/${LINKER_SCRIPT}" >&2
    exit 1
fi

TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/stealth-o-relink.XXXXXX")"
tar -xzf "${SCRIPT_DIR}/objects/${DEVICE}.tar.gz" -C "${TEMP_DIR}"

if [ -z "${CORE_ARCHIVE}" ]; then
    CORE_ARCHIVE="${TEMP_DIR}/core/core.a"
fi
if [ ! -f "${CORE_ARCHIVE}" ]; then
    echo "Core archive not found: ${CORE_ARCHIVE}" >&2
    exit 1
fi

objects=()
while IFS= read -r object_path; do
    if [[ "${object_path}" == libraries/SPI/* ]] && [ -n "${SPI_DIR}" ]; then
        replacement="${SPI_DIR}/$(basename "${object_path}")"
        if [ ! -f "${replacement}" ]; then
            echo "SPI object not found: ${replacement}" >&2
            exit 1
        fi
        objects+=("${replacement}")
    else
        objects+=("${TEMP_DIR}/${object_path}")
    fi
done < "${SCRIPT_DIR}/objects/${DEVICE}.objects.txt"

mkdir -p "${OUTPUT_DIR}"
ELF_PATH="${OUTPUT_DIR}/${DEVICE}.elf"
HEX_PATH="${OUTPUT_DIR}/${DEVICE}.hex"
MAP_PATH="${OUTPUT_DIR}/${DEVICE}.map"
UF2_PATH="${OUTPUT_DIR}/${DEVICE}.uf2"

"${GXX}" \
    -L"${TEMP_DIR}" \
    -Ofast \
    -Wl,--gc-sections \
    -L"${SCRIPT_DIR}/tools" \
    -T"${LINKER_SCRIPT}" \
    -Wl,-Map,"${MAP_PATH}" \
    -mcpu=cortex-m4 \
    -mthumb \
    -mfloat-abi=hard \
    -mfpu=fpv4-sp-d16 \
    -u \
    _printf_float \
    -Wl,--cref \
    -Wl,--check-sections \
    -Wl,--gc-sections \
    -Wl,--unresolved-symbols=report-all \
    -Wl,--warn-common \
    -Wl,--warn-section-align \
    -Wl,--wrap=malloc \
    -Wl,--wrap=free \
    --specs=nano.specs \
    --specs=nosys.specs \
    -o "${ELF_PATH}" \
    "${objects[@]}" \
    -Wl,--start-group \
    -L"${SCRIPT_DIR}/tool-libraries" \
    -larm_cortexM4lf_math \
    -lm \
    "${CORE_ARCHIVE}" \
    -lnrf_cc310_0.9.13-no-interrupts \
    -lnrf_cc310_0.9.13-no-interrupts \
    -Wl,--end-group

"${OBJCOPY}" -O ihex "${ELF_PATH}" "${HEX_PATH}"
python3 "${SCRIPT_DIR}/tools/uf2conv.py" \
    -f 0xADA52840 \
    -c \
    -o "${UF2_PATH}" \
    "${HEX_PATH}"

echo "Created:"
echo "  ${ELF_PATH}"
echo "  ${HEX_PATH}"
echo "  ${UF2_PATH}"
