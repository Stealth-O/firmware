# Stealth-O Firmware

This repository contains official prebuilt Stealth-O station and wristband
firmware for Seeed Studio XIAO nRF52840 and Heltec T096 boards.

## Firmware

- [station](station) contains `station-S00.uf2` through `station-S190.uf2` and a
  macOS flashing helper.
- [wristband](wristband) contains four explicit XIAO wristband profiles:
  `wristband-xiao-external.uf2`, `wristband-xiao-internal.uf2`,
  `wristband-xiao-lora-external.uf2`, and
  `wristband-xiao-lora-internal.uf2`, plus the single T096 profile
  `wristband-t096-internal.uf2`.

Open the README in the corresponding folder before flashing. Every station
image shares one universal code image and carries an ordinary station number
from `0` to `190` in a single data byte. Values `191...254` are wristband
journal GPS record codes and `255` is reserved as the wristband special-record
prefix and cannot be assigned to a station. Flash the matching
`station-S<ID>.uf2`; there is no runtime serial configuration.
Wristband firmware uses its stable factory-derived `device_id` and does not
require per-device serial identity setup.

The release does not use one global device version. Manifest version 7 records
each wristband variant independently, including artifact SHA-256, hardware,
storage backend, capabilities, journal format, advertisement and command
protocols, WBT2, and LoRa protocol metadata. All five variants use the
`wristband-v2` four-byte journal generation 2, superblock version 2, and WBT2
protocol version 4 with the generation in its 23-byte header. A valid
generation-1 journal left by an earlier firmware remains downloadable
read-only until explicit `CLEAR`; it is never reinterpreted as GPS or erased
automatically. The compatible station advertisement envelope remains version
1.

All wristband variants accept the runtime BLE event-start command `EVS1` with
participant `0...15` and signed-E7 event origin. Accepted means the complete
`FD,F0...F5,EF` journal transaction was persisted and at least one subsequent
contact record remains writable before `EVA1` status `0` was emitted. The
manifest records this command, CRC, acknowledgement, reserve and journal
boundary contract without embedding a participant or geographic origin.

The `xiao-external` and `xiao-lora-external` variants use onboard external QSPI.
The `xiao-internal`, `xiao-lora-internal`, and `t096-internal` variants reserve
a fixed 256 KiB internal-flash journal. XIAO LoRa variants require a Seeed
Wio-SX1262; the T096 artifact uses its onboard UC6580, SX1262, and KCT8103L PA.
All LoRa builds link pinned RadioLib 7.7.1 under MIT and emit the same
plaintext, unauthenticated `5 B` compact realtime v2 frame. XIAO uses
synthetic local X/Y; T096 converts fresh UC6580 GNSS E7 coordinates to X/Y
relative to the runtime event origin using a latitude-aware WGS84 scale and
antimeridian-normalized longitude delta, and retains its minimum `15 s` base
schedule. Use this telemetry only in the currently assumed trusted environment.
The T096 screen is present but kept powered off by this firmware. The private
receive-only LoRa receiver firmware is deliberately not part of this public
package.

The transmitter and private receiver share the project profile
`EU868_CYPRUS_G3`: `869.525 MHz`, `125 kHz`, `SF7`, `CR 4/5`, within the
`869.4–869.65 MHz` non-specific SRD band used for the initial Cyprus tests.
The regulatory values recorded in the manifest, `500 mW e.r.p.` and `10%`
maximum duty cycle, are ceilings rather than configured targets. XIAO remains
at raw `+14 dBm`; T096 remains at raw `0 dBm` before its external PA, with an
unverified target near `+14 dBm`. Actual e.r.p. depends on the complete RF path
and antenna and must be measured before operational use.

Physical station `S0` is valid, but the current event flow reserves it for the
finish-only role. START is a separate persisted command and is never an S0
contact. Physical S0 is the alternative to the app's phone finish station `0`
and must never be assigned as an ordinary checkpoint or ghost. Checkpoint and
ghost roles use `S1...S190`. The wristband's compact log stores only the station
number, so it does not preserve whether an `S0` finish sample came from the
physical station or the phone station.

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
