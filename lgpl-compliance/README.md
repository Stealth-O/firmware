# LGPL Relinking Materials

Every published `station-S00.uf2` through `station-S254.uf2` shares one linked
code image; the files differ only in a single station-ID data byte. These
materials also reproduce each of the four public wristband artifacts:

- `wristband-xiao-external.uf2`
- `wristband-xiao-internal.uf2`
- `wristband-xiao-lora-external.uf2`
- `wristband-xiao-lora-internal.uf2`

They allow a recipient to modify the LGPL-covered Seeeduino nRF52 Arduino core
or SPI library, rebuild those components, and relink them with the supplied
closed-source Stealth-O application objects. `set_station_id.py` then rewrites
the station ID byte so any station image can be reproduced without recompiling
or relinking. Ordinary station IDs are `0...254`; `255` is reserved as the
wristband special-record prefix.

## Included Materials

- `source.tar.gz`: corresponding source for the LGPL core and SPI library,
  plus headers needed to compile them.
- `core-spi-compile-commands.json`: the original compiler arguments, rewritten
  to use relocatable paths.
- `rebuild_lgpl.py`: rebuilds `core.a` and the two SPI object files.
- `objects/*.tar.gz`: exact application and permissively licensed dependency
  objects for the station baseline and each named wristband variant.
- `objects/*.objects.txt`: original linker object order for each artifact.
- `relink.sh`: links one named object set and creates ELF, HEX, and UF2 output.
- `tool-libraries`: CMSIS-DSP and ARM CryptoCell link libraries used by the
  original build.
- `tools/nrf52840_s140_v7.ld`: standard external-storage linker script.
- `tools/nrf52840_s140_v7_wristband_internal.ld`: fixed 256 KiB internal-journal
  linker script for both internal wristband variants.
- `tools/uf2conv.py` and `tools/set_station_id.py`: UF2 conversion and station
  identity patching.

The Stealth-O application is supplied only as relocatable `sketch/*.o`
objects. The LoRa variant bundles also contain the linked RadioLib 7.7.1
objects under `libraries/RadioLib/`; RadioLib remains governed by its MIT
license in `../licenses/RadioLib-MIT.txt`. No Stealth-O source code is included.

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

Relink the station with the modified core:

```bash
./relink.sh station --core-a rebuilt/core.a
```

Relink any wristband variant with the modified core and SPI objects, for
example:

```bash
./relink.sh wristband-xiao-lora-internal \
  --core-a rebuilt/core.a \
  --spi-dir rebuilt/libraries/SPI
```

The source and object materials are provided solely under their applicable
licenses. Stealth-O permissions are described in the repository root
`LICENSE.txt`.
