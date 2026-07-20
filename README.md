# Stealth-O Firmware

This repository contains official prebuilt Stealth-O station and wristband
firmware for Seeed Studio XIAO nRF52840 boards.

## Firmware

- [station](station) contains `station-S00.uf2` through `station-S254.uf2` and a
  macOS flashing helper.
- [wristband](wristband) contains four explicit XIAO wristband profiles:
  `wristband-xiao-external.uf2`, `wristband-xiao-internal.uf2`,
  `wristband-xiao-lora-external.uf2`, and
  `wristband-xiao-lora-internal.uf2`.

Open the README in the corresponding folder before flashing. Every station
image shares one universal code image and carries an ordinary station number
from `0` to `254` in a single data byte. Value `255` is reserved as the
wristband special-record prefix and cannot be assigned to a station. Flash the
matching `station-S<ID>.uf2`; there is no runtime serial configuration.
Wristband firmware uses its stable factory-derived `device_id` and does not
require per-device serial identity setup.

The release does not use one global device version. Manifest version 2 records
each wristband variant independently, including artifact SHA-256, hardware,
storage backend, capabilities, journal format, advertisement and command
protocols, WBT2, and LoRa protocol metadata. All four variants use the
`wristband-v2` four-byte journal and WBT2 protocol version 3. The compatible
station advertisement envelope remains version 1.

The `xiao-external` and `xiao-lora-external` variants use onboard external QSPI.
The `xiao-internal` and `xiao-lora-internal` variants reserve a fixed 256 KiB
internal-flash journal. LoRa variants require a Seeed Wio-SX1262 for XIAO and
link pinned RadioLib 7.7.1 under MIT. The private receive-only LoRa receiver
firmware is deliberately not part of this public package.

Physical station `S0` is valid, but the current MVP event flow reserves it for
the `start_finish` role only. It is the physical alternative to the app's phone
station `0` and must never be assigned as an ordinary checkpoint or ghost.
Checkpoint and ghost roles use `S1...S254`. The wristband's compact log stores
only the station number, so it does not preserve whether an `S0` sample came
from the physical station or the phone station.

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
