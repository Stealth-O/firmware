# Stealth-O Firmware

This repository contains official prebuilt Stealth-O station and wristband
firmware for Seeed Studio XIAO nRF52840 boards.

## Firmware

- [station](station) contains `station-S00.uf2` through `station-S99.uf2` and a
  macOS flashing helper.
- [wristband](wristband) contains `wristband.uf2` and macOS flashing helpers.

Open the README in the corresponding folder before flashing. Every station image
shares one universal code and carries its station number from `0` to `99` in a
single data byte; flash `station-SNN.uf2` for station NN. There is no runtime
serial configuration. Wristband firmware uses its stable factory-derived
`device_id` and does not require per-device serial identity setup.

The Stealth-O firmware is proprietary software. Its source code is not
published in this repository. The permissions for downloading, installing,
and using an unmodified firmware image are described in
[LICENSE.txt](LICENSE.txt).

The flashing scripts and their device READMEs may be used, modified, and
redistributed under the MIT terms in [TOOLS_LICENSE.txt](TOOLS_LICENSE.txt).

The firmware includes third-party software under separate licenses. Those
licenses and notices are listed in
[THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) and the
[licenses](licenses) directory.

The relinking materials required for the LGPL-covered Arduino core and SPI
library are in [lgpl-compliance](lgpl-compliance). Operational release
requirements are documented in [LGPL_COMPLIANCE.md](LGPL_COMPLIANCE.md).

Copyright (c) 2026 Stealth-O. All rights reserved.
