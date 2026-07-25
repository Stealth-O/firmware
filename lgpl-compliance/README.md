# LGPL Relinking Materials

Every published `station-S00.uf2` through `station-S254.uf2` shares one linked
code image; the files differ only in a single station-ID data byte. These
materials also reproduce each of the five public wristband artifacts:

- `wristband-xiao-external.uf2`
- `wristband-xiao-internal.uf2`
- `wristband-xiao-lora-external.uf2`
- `wristband-xiao-lora-internal.uf2`
- `wristband-t096-internal.uf2`

They allow a recipient to modify the LGPL-covered Seeeduino or Heltec nRF52
Arduino core, board variant, SPI library, and the Heltec core's TinyGPS++
parser, rebuild those components, and relink them with the supplied closed-source
Stealth-O application objects. `set_station_id.py` then rewrites
the station ID byte so any station image can be reproduced without recompiling
or relinking. Ordinary station IDs are `0...254`; `255` is reserved as the
wristband special-record prefix.

## Included Materials

- `source.tar.gz`: corresponding source for the LGPL core and SPI library,
  XIAO variant, and headers needed to compile them.
- `core-spi-compile-commands.json`: the code-affecting compiler arguments and
  corresponding-source include roots, rewritten to use relocatable paths.
- `source-t096.tar.gz`: corresponding source for the pinned Heltec nRF52 core,
  T096 variant, SPI library, TinyGPS++ parser, and required headers. It is
  generated from mirror commit `53b3d4a126bd144f94642203605031dd0aa93354`.
  It preserves the mirror's root GPL-3.0 `LICENSE` verbatim and places the
  project-owned `STEALTH-O-LICENSING-NOTE.txt` beside it to document that
  repository context without changing any upstream notice.
- `t096-core-spi-tinygps-compile-commands.json`: the T096 code-affecting
  compiler arguments and corresponding-source include roots, rewritten to use
  relocatable paths.
- `xiao-provenance.json` and `t096-provenance.json`: audited board, core,
  toolchain, source repository/snapshot/branch/tag, selected-variant, and CC310
  archive provenance. The T096 provenance also records the immutable mirror
  snapshot tag, upstream tag anchor, selected variant-header path and required
  versus actual license classification, and deliberately excluded
  `Heltec_nrf_lorawan` component.
- `rebuild_lgpl.py`: rebuilds `core.a`, the selected board variant, and the two
  SPI object files for either board family. TinyGPS++ is part of the T096
  `core.a` rebuild.
- `objects/*.tar.gz`: exact application and permissively licensed dependency
  objects for the station baseline and each named wristband variant.
- `objects/*.objects.txt`: original linker object order for each artifact.
- `relink.sh`: links one named object set and creates ELF, HEX, and UF2 output.
- `tool-libraries`: CMSIS-DSP and the freshly staged, exact-hash-verified ARM
  CryptoCell link library used by the original build.
- `tools/nrf52840_s140_v7.ld`: standard external-storage linker script.
- `tools/nrf52840_s140_v7_wristband_internal.ld`: fixed 256 KiB internal-journal
  linker script for both internal XIAO wristband variants.
- `tools/t096/nrf52840_s140_v6_t096_wristband_internal.ld` and
  `tools/t096/nrf52_common.ld`: fixed 256 KiB internal-journal and matching
  pinned-Heltec common linker scripts for the T096 wristband.
- `tools/uf2conv.py` and `tools/set_station_id.py`: UF2 conversion and station
  identity patching.

The Stealth-O application is supplied only as relocatable `sketch/*.o`
objects. The LoRa variant bundles also contain the linked RadioLib 7.7.1
objects under `libraries/RadioLib/`; RadioLib remains governed by its MIT
license in `../licenses/RadioLib-MIT.txt`. No Stealth-O source code is included.
The T096 image does not link or bundle Heltec's `Heltec_nrf_lorawan` library or
its precompiled `liblorawan.a`; its SX1262 driver is RadioLib.

The source generator copies the pinned CMSIS license to
`source/CMSIS/LICENSE.txt` and includes every required CMSIS header in each
applicable archive; a missing source or notice stops the release. SEGGER
RTT/SystemView units occur in both board-family compile inventories and
intermediate core archives, while the final published station, XIAO wristband,
and T096 wristband links retain no SEGGER symbols. Their source headers and
complete release notice are preserved.

Before packaging, every captured compiled T096 source is classified from its
file-level notice. An unapproved plain GPL-only, AGPL, unknown, or missing
classification fails closed. The selected variant's current file and pinned
historical Git blob must also have the declared SHA-256, be byte-identical, and
belong to one ancestor chain. The release separately verifies an exact
allowlist of linked static libraries, so an unexpected archive such as
`liblorawan.a` also fails closed. A fast test additionally classifies the live
pinned core/SPI/variant input without reading a previous `firmware` output.
The snapshot descriptor additionally declares the selected `variant.h` and
requires its semantic file-level license classification to be exactly
`LGPL-2.1-or-later`; T096 provenance records the header path and both required
and actual values. Snapshot validation rejects shallow repositories and
requires both the immutable mirror snapshot tag and the upstream `1.7.0` tag
anchor at `d45d40df192eb155df3c1f809387591d515383ab`. Here
`untagged-main` means no upstream exact tag identifies the selected commit in
the audited local mirror tag set, not that an unfetched remote has no such tag.

## Requirements

- GNU Arm Embedded Toolchain `9-2019q4`
- Python 3
- `tar`

On macOS with the Seeed Arduino package installed, the default toolchain path
is:

```text
~/Library/Arduino15/packages/Seeeduino/tools/arm-none-eabi-gcc/9-2019q4
```

Set `ARM_GCC_DIR` when the toolchain is elsewhere.

Byte-for-byte reproduction requires a fixed compiler clock. Export
`SOURCE_DATE_EPOCH=0` before `rebuild_lgpl.py`, any replacement-object compile,
and relinking. RadioLib embeds compiler `__DATE__` and `__TIME__`; using a
different or unset epoch can change LoRa artifact bytes even when the sources
and toolchain are otherwise identical.

## Reproduce The Published Images

The default relink uses the original core and SPI objects:

```bash
cd lgpl-compliance
./relink.sh station
./relink.sh wristband-xiao-external
./relink.sh wristband-xiao-internal
./relink.sh wristband-xiao-lora-external
./relink.sh wristband-xiao-lora-internal
./relink.sh wristband-t096-internal
```

Each generated UF2 is written under `output/` with its device ID as the file
name. `output/station.uf2` is the linked-default universal station image and is
byte-for-byte identical to `../station/station-S254.uf2`.

Reproduce any other published station image by patching its ID byte:

```bash
python3 tools/set_station_id.py output/station.uf2 42 output/station-S42.uf2
```

The result is byte-for-byte identical to the published `station-S42.uf2`.

## Modify And Rebuild LGPL Components

Extract the corresponding source and rebuild the LGPL components:

```bash
tar -xzf source.tar.gz
export SOURCE_DATE_EPOCH=0
python3 rebuild_lgpl.py
```

Relink the station with the modified core and XIAO board variant:

```bash
./relink.sh station \
  --core-a rebuilt/core.a \
  --variant-o rebuilt/core/variant.cpp.o
```

Relink any wristband variant with the modified core and SPI objects, for
example:

```bash
./relink.sh wristband-xiao-lora-internal \
  --core-a rebuilt/core.a \
  --spi-dir rebuilt/libraries/SPI \
  --variant-o rebuilt/core/variant.cpp.o
```

For the T096 family, extract its separate corresponding-source archive and
select the matching rebuild family:

```bash
mkdir -p t096-source
tar -xzf source-t096.tar.gz -C t096-source
export SOURCE_DATE_EPOCH=0
python3 rebuild_lgpl.py \
  --family heltec-t096 \
  --source-dir t096-source/source \
  --build-dir rebuilt-t096
```

Relink the T096 image with the rebuilt core, T096 variant, and SPI objects:

```bash
./relink.sh wristband-t096-internal \
  --core-a rebuilt-t096/core.a \
  --spi-dir rebuilt-t096/libraries/SPI \
  --variant-o rebuilt-t096/core/variant.cpp.o
```

The source and object materials are provided solely under their applicable
licenses. Stealth-O permissions are described in the repository root
`LICENSE.txt`.

The canonical release-level compliance statement and operational checklist is
`../LGPL_COMPLIANCE.md`.
