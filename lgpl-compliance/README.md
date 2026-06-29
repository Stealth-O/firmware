# LGPL Relinking Materials

Every published `station-S00.uf2` through `station-S99.uf2` shares one identical
linked code image; they differ only in a single station-id data byte. These
materials relink that universal station image (which reproduces `station-S00.uf2`)
and the `wristband.uf2` file, and `set_station_id.py` rewrites the id byte so any
`station-SNN.uf2` can be reproduced without recompiling or relinking.

They allow a recipient to modify the LGPL-covered Seeeduino nRF52 Arduino
core or SPI library, rebuild those components, relink them with the
closed-source Stealth-O application object, and then patch the relinked image to
any station number.

## Included Materials

- `source.tar.gz`: corresponding source for the LGPL core and SPI library,
  plus headers needed to compile them.
- `core-spi-compile-commands.json`: the original compiler arguments, rewritten
  to use relocatable paths.
- `rebuild_lgpl.py`: rebuilds `core.a` and the two SPI object files.
- `objects/*.tar.gz`: application and permissively licensed dependency object
  files for each firmware image.
- `objects/*.objects.txt`: original linker object order.
- `relink.sh`: links the objects and creates ELF, HEX, and UF2 output.
- `tool-libraries`: CMSIS-DSP and ARM CryptoCell link libraries used by the
  original build.
- `tools`: linker script, UF2 conversion utility, and `set_station_id.py`,
  which rewrites the station-id byte to turn the relinked base image into any
  `station-SNN.uf2`.

The Stealth-O application is supplied only as `station.ino.cpp.o` or
`wristband.ino.cpp.o`. No Stealth-O source code is included.

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

## Reproduce The Published Images

The default relink uses the original core and SPI objects:

```bash
cd lgpl-compliance
./relink.sh station
./relink.sh wristband
```

The generated UF2 files are written to `output/`. `output/station.uf2` is the
universal station image and is byte-for-byte identical to `station-S00.uf2`.

Reproduce any other published station image by patching its id byte:

```bash
python3 tools/set_station_id.py output/station.uf2 42 output/station-S42.uf2
```

The result is byte-for-byte identical to the published `station-S42.uf2`.

## Modify And Rebuild LGPL Components

Extract the corresponding source:

```bash
tar -xzf source.tar.gz
```

Edit files under:

```text
source/hardware/cores/nRF5
source/hardware/libraries/SPI
```

Rebuild the LGPL components:

```bash
python3 rebuild_lgpl.py
```

Relink the station with the modified core:

```bash
./relink.sh station \
  --core-a rebuilt/core.a
```

`output/station.uf2` is the universal image with your modified core; patch it to
the station number you need:

```bash
python3 tools/set_station_id.py output/station.uf2 42 output/station-S42.uf2
```

Relink the wristband with the modified core and SPI objects:

```bash
./relink.sh wristband \
  --core-a rebuilt/core.a \
  --spi-dir rebuilt/libraries/SPI
```

The source and object materials are provided solely under their applicable
licenses. Stealth-O permissions are described in the repository root
`LICENSE.txt`.
