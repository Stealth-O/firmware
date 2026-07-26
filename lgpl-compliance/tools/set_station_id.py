#!/usr/bin/env python3
"""Patch one ordinary station ID into a XIAO station UF2 image.

The linked station image contains exactly one ``STOSID01`` marker followed by
the station ID byte. The linked default is 190. IDs 0 through 190 are ordinary
stations. IDs 191 through 254 are journal GPS record codes and 255 is the
wristband special-record prefix, so neither is ever a valid station ID.

Usage: set_station_id.py <input.uf2> <station-id 0-190> <output.uf2>
"""

import argparse
import struct
from pathlib import Path
from typing import Dict, Optional, Sequence


MAX_STATION_ID = 190
STATION_MAGIC = b"STOSID01"
UF2_BLOCK_SIZE = 512
UF2_DATA_CAPACITY = 476
UF2_DATA_OFFSET = 32
UF2_END_MAGIC_OFFSET = 508
UF2_FAMILY_ID = 0xADA52840
UF2_FLAG_FAMILY_ID_PRESENT = 0x00002000
UF2_MAGIC_END = 0x0AB16F30
UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157


class PatchError(ValueError):
    """Raised when an image cannot be patched without ambiguity."""


def _station_id_file_offset(data: bytes) -> int:
    if not data or len(data) % UF2_BLOCK_SIZE != 0:
        raise PatchError("input is not a complete UF2 block sequence")

    byte_by_address: Dict[int, int] = {}
    file_offset_by_address: Dict[int, int] = {}
    actual_block_count = len(data) // UF2_BLOCK_SIZE
    block_numbers = set()

    for block_start in range(0, len(data), UF2_BLOCK_SIZE):
        (
            magic0,
            magic1,
            flags,
            target_address,
            payload_size,
            block_number,
            declared_block_count,
            family_id,
        ) = struct.unpack_from(
            "<8I",
            data,
            block_start,
        )
        end_magic = struct.unpack_from("<I", data, block_start + UF2_END_MAGIC_OFFSET)[0]

        if magic0 != UF2_MAGIC_START0 or magic1 != UF2_MAGIC_START1:
            raise PatchError(f"invalid UF2 start magic in block {block_start // UF2_BLOCK_SIZE}")
        if end_magic != UF2_MAGIC_END:
            raise PatchError(f"invalid UF2 end magic in block {block_start // UF2_BLOCK_SIZE}")
        if payload_size > UF2_DATA_CAPACITY:
            raise PatchError(f"invalid UF2 payload size {payload_size}")
        if declared_block_count != actual_block_count:
            raise PatchError(
                f"UF2 declares {declared_block_count} blocks but contains {actual_block_count}"
            )
        if block_number >= actual_block_count:
            raise PatchError(f"UF2 block number {block_number} is out of range")
        if block_number in block_numbers:
            raise PatchError(f"duplicate UF2 block number {block_number}")
        if not flags & UF2_FLAG_FAMILY_ID_PRESENT:
            raise PatchError("UF2 block is missing the family-ID-present flag")
        if family_id != UF2_FAMILY_ID:
            raise PatchError(f"unexpected UF2 family ID 0x{family_id:08X}")
        block_numbers.add(block_number)

        for index in range(payload_size):
            address = target_address + index
            if address in byte_by_address:
                raise PatchError(f"overlapping UF2 payload at address 0x{address:08X}")
            file_offset = block_start + UF2_DATA_OFFSET + index
            byte_by_address[address] = data[file_offset]
            file_offset_by_address[address] = file_offset

    if block_numbers != set(range(actual_block_count)):
        raise PatchError("UF2 block numbering is incomplete")

    marker_addresses = [
        address
        for address in sorted(byte_by_address)
        if all(
            byte_by_address.get(address + offset) == STATION_MAGIC[offset]
            for offset in range(len(STATION_MAGIC))
        )
    ]
    if len(marker_addresses) != 1:
        raise PatchError(f"expected exactly one station ID marker, found {len(marker_addresses)}")

    id_address = marker_addresses[0] + len(STATION_MAGIC)
    if id_address not in file_offset_by_address:
        raise PatchError("station ID byte is missing after the marker")
    return file_offset_by_address[id_address]


def patch_file(input_path: Path, output_path: Path, station_id: int) -> None:
    if input_path.resolve() == output_path.resolve():
        raise PatchError("input and output paths must differ")
    output_path.write_bytes(patch_uf2(input_path.read_bytes(), station_id))


def patch_uf2(data: bytes, station_id: int) -> bytes:
    if station_id < 0 or station_id > MAX_STATION_ID:
        raise PatchError(f"station ID must be in 0...{MAX_STATION_ID}")
    result = bytearray(data)
    result[_station_id_file_offset(data)] = station_id
    return bytes(result)


def station_id_from_uf2(data: bytes) -> int:
    return data[_station_id_file_offset(data)]


def validate_station_id(text: str) -> int:
    if not text.isascii() or not text.isdigit():
        raise PatchError("station ID must be a decimal number")
    station_id = int(text, 10)
    if station_id > MAX_STATION_ID:
        raise PatchError(
            f"station ID must be in 0...{MAX_STATION_ID}; "
            "191...254 are GPS record codes and 255 is reserved"
        )
    return station_id


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("station_id")
    parser.add_argument("output", type=Path)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _parser()
    arguments = parser.parse_args(argv)
    try:
        station_id = validate_station_id(arguments.station_id)
        patch_file(arguments.input, arguments.output, station_id)
    except (OSError, PatchError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
