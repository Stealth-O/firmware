Wristband firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

These are the Stealth-O wristband-v2 builds for Seeed XIAO nRF52840 and Heltec
T096. Every variant writes journal generation 5 with four-byte physical words,
16-byte absolute GPS FULL and four-byte relative SHORT records. CONTACT has an
independent millisecond clock per station/source. TIME extends an inline delta
above 32767 ms; the session time limit is about 6.2 days. Every variant uses
WBT2 version 2 and its 23-byte header carries the generation explicitly.
External QSPI uses WBS2/superblock version 6; internal flash uses a WBJ5
version-1 descriptor in a fixed footer and automatically sized journal space.
An unknown older internal layout or changed layout starts a fresh epoch;
committed current-descriptor corruption and incompatible external storage
require explicit CLEAR. No predecessor decoder is shipped. See ../manifest.json
for this build's exact layout, recording budget and artifact SHA-256 values.

Files:

- wristband-xiao-external.uf2 - onboard external QSPI journal.
- wristband-xiao-internal.uf2 - automatically sized internal-flash journal.
- wristband-xiao-lora-external.uf2 - external QSPI plus Wio-SX1262 LoRa TX.
- wristband-xiao-lora-internal.uf2 - internal flash plus Wio-SX1262 LoRa TX.
- wristband-t096-internal.uf2 - T096 automatically sized internal journal, onboard
  UC6580 GNSS, and onboard SX1262/KCT8103L compact realtime TX. The screen is
  present but kept powered off; this release has no display UI.
- flash.sh - flashes one explicitly selected artifact.

The XIAO LoRa variants require a Seeed Wio-SX1262 and a suitable antenna.
Never transmit without the antenna. Every LoRa-capable variant sends the
dynamic Stealth-O compact realtime protocol v2 described by manifest.json.
Its implicit payload contains only radio ID and equal-width local X/Y grid
indices. Payload length, coordinate step and bits, frequency, bandwidth, SF,
CR, preamble, period, temporal-slot count and slot arrive through the EAS3 BLE
Assign command; none is compiled per event. There is no participant, station
or RSSI field and no service byte. Until XIAO gains GNSS, firmware generates synthetic X/Y every
2.5 seconds. This best-effort frame has no sender sequence, ACK, timestamp or
retry history. It is plaintext and
unauthenticated, so nearby radio equipment can observe or spoof it. All LoRa
builds link RadioLib 7.7.1 under MIT.

Radio identity capacity remains 16...1024, while a current plan uses
S = min(capacity, 64) fixed temporal phases. Radio IDs are sequential 0, 1,
2... and the independent slot index is
bitReverse(radioID % S, log2(S)); phases repeat after 64 without hopping or
rotation. Current event catalog/schema 4 uses eu868-automatic-v5 and radio-ID
allocation revision 3. Immutable eu868-automatic-v4 plans in that same
catalog/schema and allocation revision remain readable and assignable without
replanning.
Catalog/schema 3 with allocation revision 2 remains
readable only for historical events and cannot create a new Assign; its old
slot formula was floor(radioID * S / capacity). An exact schema-2 assignment
stays readable and assignable with the historical EAS2 temporal marker 0 carried
by its current EAS3 representation, which
means its original full-capacity schedule.

The scheduler does not rely on the foreground loop landing inside a narrow
start window. XIAO has a 20 ms mandatory loop sleep and T096 has 10 ms; both use
a 40 ms cooperative horizon to prefer the exact nominal tick. Nominal ticks
stay on the EAS3 fixed-phase grid regardless of actual send time, with no send
cooldown. Overdue work is attempted immediately with no expiry. Multiple missed
ticks coalesce to one latest pending snapshot rather than a catch-up backlog.

The currently audited calculator profile is `eu868-cyprus-869-525`. It keeps the
complete occupied receiver band (configured frequency plus or minus half the
bandwidth) inside `869.4–869.65 MHz` and a `10%` maximum duty cycle. Regulatory
limits are ceilings, not configured power targets. This release does not change
device power: XIAO retains raw `+14 dBm`; actual e.r.p. must include the RF path
and antenna.

T096 uses the same selected dynamic payload. A position is eligible only
when the latest checksum-valid GNGGA/GPGGA fix quality or GNRMC/GPRMC status
says valid and position age is at most 30 seconds. Firmware converts GNSS E7
to local X/Y using a WGS84 scale evaluated at the last committed runtime event
origin latitude; longitude deltas take the shortest path across the
antimeridian. Transmission follows the EAS3 period and slot. Coherent GNSS UTC
rebases only future nominal ticks; without trusted UTC the projected grid keeps
running from monotonic time without dropping pending work.
RadioLib drives the SX1262 at raw 0 dBm;
approximately 14 dBm after the onboard PA is a design target, not measured or
certified output. Compact v2 is plaintext and unauthenticated. Nearby radio
equipment can observe or spoof it, so the current firmware assumes a trusted
environment.

Every wristband accepts EAS3 over the existing BLE transfer boundary with an
explicit observation mode, signed-E7 event origin, and either a complete
transmitter configuration or the canonical radio-disabled assignment. It
replies with accepted EAA3 only after the complete 56-byte SESSION + ASSIGN
transaction is persisted. Assign needs at least 1092 free bytes: 56 for the
transaction, 12 of post-assignment headroom for contacts/service markers, and a
final 1024-byte reserve. In normal mode, accepted Assign activates GPS and journaling
and optionally LoRa; sporting time begins at the first eligible nonzero
station and S0 remains finish. BLE keeps the strongest sample in its 100 ms
window and LF has an independent 1 s window. In economy mode GPS journal writes stop
and contact windows grow as free space shrinks. GNSS/LoRa live telemetry can
continue until on-air stop.
In rawStationCapture, GPS, LF and LoRa remain off and every recognized BLE
station report is stored without aggregation. Long gaps use TIME instead of
sealing the session. Import, the final reserve or the 29-bit time limit seals
it; both normal and RAW snapshots remain readable after recording stops.
Before the accepted ACK,
LoRa-capable builds hardware-reset the
SX1262, clear realtime history, and reset current-cycle slot ownership so an
old in-flight frame cannot cross into the new assignment.

Never power or flash a LoRa profile without a suitable antenna attached. T096
hardware behavior is not established by the public build alone: GNSS, RF
output, PA control, battery behavior, storage/CLEAR, and display-off state must
pass a real-board smoke test before operational use.

Flash:

1. Connect the wristband board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run one of:

   ./flash.sh xiao-external
   ./flash.sh xiao-internal
   ./flash.sh xiao-lora-external
   ./flash.sh xiao-lora-internal
   ./flash.sh t096-internal

No public serial monitor helper is required for flashing. The wristband uses
its stable factory-derived device id, so no per-wristband number setup is
required.

The wristband accepts station IDs 0 through 190. IDs 191...255 cannot be
provisioned; generation-5 record tags are independent of station IDs. In the current event flow, S0 is finish only. EAS3
event assignment is persisted separately and is never an S0 contact. S0
represents either the physical finish station or phone finish station 0, which
the compact log
intentionally does not distinguish. Never assign S0 as an ordinary checkpoint
or ghost; checkpoint and ghost roles use S1...S190.

If multiple UF2 drives are mounted, run, for example:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh xiao-external

The helper reads Board-ID from INFO_UF2.TXT after selecting the target. XIAO
profiles accept only the pinned XIAO/XIAO Sense bootloader identifiers, while
t096-internal requires the exact `HT-n5262G` Board-ID. Plain `HT-n5262` belongs
to another board and is rejected, as is an ordinary directory or any other
incompatible target supplied through UF2_VOLUME.
