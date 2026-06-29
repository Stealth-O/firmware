#!/usr/bin/env python3
"""Patch the station id byte into a station UF2 image.

The station firmware keeps its id in a single data byte tagged by an 8-byte
magic, so every station ships the same linked code image. This tool finds that
byte and rewrites it, turning the relinked base image (id 0) into any station
image without recompiling or relinking. That is how a recipient reproduces every
published station-SNN.uf2 from the LGPL relink output.

Usage: set_station_id.py <input.uf2> <station-id 0-99> <output.uf2>
"""
import struct
import sys

STATION_MAGIC = b"STOSID01"
UF2_BLOCK_SIZE = 512
UF2_DATA_OFFSET = 32
UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157


def main():
    if len(sys.argv) != 4:
        sys.exit("Usage: set_station_id.py <input.uf2> <station-id 0-99> <output.uf2>")
    input_path, id_text, output_path = sys.argv[1], sys.argv[2], sys.argv[3]
    if not id_text.isdigit() or int(id_text) > 99:
        sys.exit("Station id must be a number from 0 to 99.")
    station_id = int(id_text)

    buffer = bytearray(open(input_path, "rb").read())

    # Map every flash byte to its offset inside the UF2 file so the magic can be
    # located even across block boundaries and patched in place.
    byte_by_addr = {}
    file_offset_by_addr = {}
    for block_start in range(0, len(buffer), UF2_BLOCK_SIZE):
        block = buffer[block_start:block_start + UF2_BLOCK_SIZE]
        if len(block) < UF2_DATA_OFFSET:
            continue
        magic0, magic1, _flags, target_addr, payload_size = struct.unpack("<5I", block[:20])
        if magic0 != UF2_MAGIC_START0 or magic1 != UF2_MAGIC_START1:
            continue
        for index in range(payload_size):
            addr = target_addr + index
            byte_by_addr[addr] = block[UF2_DATA_OFFSET + index]
            file_offset_by_addr[addr] = block_start + UF2_DATA_OFFSET + index

    magic_addrs = [
        addr for addr in byte_by_addr
        if all(byte_by_addr.get(addr + offset) == STATION_MAGIC[offset]
               for offset in range(len(STATION_MAGIC)))
    ]
    if len(magic_addrs) != 1:
        sys.exit(f"expected exactly one station id marker, found {len(magic_addrs)}")

    id_addr = magic_addrs[0] + len(STATION_MAGIC)
    if id_addr not in file_offset_by_addr:
        sys.exit("station id byte is missing from the image")
    buffer[file_offset_by_addr[id_addr]] = station_id

    with open(output_path, "wb") as output:
        output.write(buffer)


if __name__ == "__main__":
    main()
