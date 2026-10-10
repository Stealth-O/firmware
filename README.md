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
from `0` to `190` in a single data byte. IDs `191...255` are not provisionable;
generation-5 journal record tags are independent of station IDs. Flash the matching
`station-S<ID>.uf2`; there is no runtime serial configuration.
Wristband firmware uses its stable factory-derived `device_id` and does not
require per-device serial identity setup.

The release uses one compatibility epoch, Product Version 2. Manifest schema
revision 16 records each wristband variant independently, including artifact
SHA-256, hardware, storage layout, capabilities, journal format, advertisement
and command protocols, WBT2, and LoRa metadata. All five variants use
`wristband-v2` journal generation 5: four-byte physical words, 16-byte absolute
GPS FULL records and four-byte relative SHORT records. CONTACT timestamps use
independent millisecond clocks per station/source; TIME extends the 32767 ms
inline delta up to the 29-bit session time limit (about 6.2 days).
WBT2 protocol version 2 carries the generation in its 23-byte header.
External QSPI uses magic `WBS2`, superblock version 6. Internal flash uses the
fixed-footer `WBJ5` descriptor version 1 and a layout calculated from the linked
image. No predecessor decoder is shipped. Unknown older internal layouts or a
changed layout start a fresh epoch automatically; a damaged committed current
descriptor fails closed until explicit `CLEAR`. External incompatible storage
also requires `CLEAR`. Advertisement and command protocol versions remain 2.

The linked C protocol library exposes ABI revision 8 independently; this native
interface revision is neither a Product Version nor an on-wire marker.

All wristband variants accept the runtime BLE Assign command `EAS3`. It carries
an explicit `normal` / `rawStationCapture` observation mode, the signed-E7 event
origin, and either a complete dynamic LoRa transmitter configuration or a
canonical radio-disabled assignment. Accepted means the complete 56-byte
SESSION + ASSIGN transaction was persisted before `EAA3` status `0`: one
four-byte SESSION and 52 bytes of ASSIGN. Admission requires 1092 free bytes,
including the 1024-byte final reserve and 12 bytes of post-assignment
headroom for subsequent contacts and service markers. The manifest records this
command, CRC, acknowledgement, reserve, observation modes, coordinate step
`100...1500 cm`, radio-ID and journal boundary contract.
In `rawStationCapture`, GPS, LF and LoRa stay off and every recognized BLE
report is stored without aggregation. A long observation gap uses TIME and
does not seal the session. Import, the final reserve or the 29-bit time limit
stops recording; the snapshot remains readable. Before Assign, station
detection may drive local indication but does not append station records.
Normal mode keeps the strongest BLE sample per window and throttles LF
independently. Below the economy threshold GPS journal writes stop, and progressively
longer contact windows preserve the final reserve. GNSS and LoRa may continue
serving live telemetry until on-air stop. RAW stops at the reserve
without coalescing its observations.

The `xiao-external` and `xiao-lora-external` variants use onboard external QSPI.
Each internal profile starts its journal at the first 4096-byte page above the
linked flash image and ends at `0xED000`; the last page holds metadata. The
manifest includes this build's exact capacity, data bytes, recording budget,
addresses, profile, ELF hash and completed-artifact hash. The generator checks
the report against the selected variant, adjacent ELF and actual UF2 input,
rejecting swapped profiles, stale UF2 files and reports without an artifact
binding. Build the profile again to regenerate an old report. XIAO LoRa
variants require a Seeed Wio-SX1262; the T096
artifact uses its onboard UC6580, SX1262, and KCT8103L PA.
All LoRa builds link pinned RadioLib 7.7.1 under MIT and emit the selected
plaintext, unauthenticated compact realtime v2 payload. Its dynamic implicit
payload contains only `radioID + X + Y`; the plan fixes payload bytes, equal X/Y
bit widths, grid step, frequency, bandwidth, SF, CR, preamble, period,
temporal-slot count and slot. Current event catalog/schema `4` uses automatic
revision `eu868-automatic-v5` and radio-ID allocation revision `3`: Assign
issues sequential IDs `0, 1, 2...`, while the fixed temporal phase is
`bitReverse(radioID % temporalSlotCount, log2(temporalSlotCount))`. Radio
identity capacity remains `16...1024`, while
`temporalSlotCount = min(capacity, 64)`. Phases repeat after 64 with no hopping
or rotation, so `k` and `k + 64` deliberately share a phase. Immutable
`eu868-automatic-v4` plans in the same catalog/schema and allocation revision
remain readable and assignable without replanning. Catalog/schema `3`,
allocation revision `2` remains readable only for historical events and
cannot create a new Assign; its old phase formula was
`floor(radioID * temporalSlotCount / capacity)`. Exact schema `2` assignments
remain readable and assignable with historical temporal marker `0`, which means
their original full-capacity grid.
XIAO uses synthetic local X/Y and a boot-relative engineering clock; T096
converts fresh UC6580 GNSS E7 coordinates to X/Y relative to the runtime event
origin. XIAO's `20 ms` and T096's `10 ms` foreground sleeps are bracketed by a
`40 ms` cooperative horizon which prefers the exact nominal tick. The EAS3
period/slot grid never shifts after an actual send, and there is no send
cooldown: overdue work is attempted immediately with no expiry, while multiple
missed ticks coalesce to the latest pending snapshot. T096 disciplines future
ticks from coherent GNSS UTC and continues the projected grid monotonically
while UTC is unavailable. Use this telemetry only in the currently assumed
trusted environment.
The T096 screen is present but kept powered off by this firmware. The private
receive-only LoRa receiver firmware is deliberately not part of this public
package.

The currently audited calculator profile is `eu868-cyprus-869-525` and confines
all selected receiver configurations to the `869.4–869.65 MHz` non-specific
SRD band.
The regulatory values recorded in the manifest, `500 mW e.r.p.` and `10%`
maximum duty cycle, are ceilings rather than configured targets. XIAO remains
at raw `+14 dBm`; T096 remains at raw `0 dBm` before its external PA, with an
unverified target near `+14 dBm`. Actual e.r.p. depends on the complete RF path
and antenna and must be measured before operational use.

Physical station `S0` is valid, but the current event flow reserves it for the
finish-only role. Event assignment is persisted separately and is never an S0
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
