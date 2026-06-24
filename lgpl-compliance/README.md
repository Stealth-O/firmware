# LGPL Relinking Materials

These materials correspond to the `station.uf2` and `wristband.uf2` files in
this repository.

They allow a recipient to modify the LGPL-covered Seeeduino nRF52 Arduino
core or SPI library, rebuild those components, and relink them with the
closed-source Stealth-O application object.

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
- `tools`: linker script and UF2 conversion utility.

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

The generated UF2 files are written to `output/`.

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

Relink the wristband with the modified core and SPI objects:

```bash
./relink.sh wristband \
  --core-a rebuilt/core.a \
  --spi-dir rebuilt/libraries/SPI
```

The source and object materials are provided solely under their applicable
licenses. Stealth-O permissions are described in the repository root
`LICENSE.txt`.
