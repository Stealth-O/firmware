Wristband firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

These are the Stealth-O wristband-v2 builds for Seeed XIAO nRF52840 and Heltec
T096. Every variant uses four-byte journal records, WBT2 protocol version 3,
and the same BLE transfer contract. See ../manifest.json for the complete
variant contract and artifact SHA-256 values.

Files:

- wristband-xiao-external.uf2 - onboard external QSPI journal.
- wristband-xiao-internal.uf2 - fixed 256 KiB internal-flash journal.
- wristband-xiao-lora-external.uf2 - external QSPI plus Wio-SX1262 LoRa TX.
- wristband-xiao-lora-internal.uf2 - internal flash plus Wio-SX1262 LoRa TX.
- wristband-t096-internal.uf2 - T096 fixed 256 KiB internal journal, onboard
  UC6580 GNSS, and onboard SX1262/KCT8103L compact realtime TX. The screen is
  present but kept powered off; this release has no display UI.
- flash.sh - flashes one explicitly selected artifact.

The XIAO LoRa variants require a Seeed Wio-SX1262 and a suitable antenna.
Never transmit without the antenna. Every LoRa-capable variant sends the fixed
five-byte Stealth-O compact realtime protocol v2 described by manifest.json:
runtime participant, local X/Y, one station ID, and a station RSSI level.
Participant and event origin arrive through the BLE event-start command;
neither value is compiled into the firmware. Until XIAO gains GNSS, firmware
generates synthetic X/Y every 2.5 seconds. This best-effort frame has no sender
ID, sender sequence, ACK, or retry history. It is plaintext and
unauthenticated, so nearby radio equipment can observe or spoof it. All LoRa
builds link RadioLib 7.7.1 under MIT.

All LoRa transmitter and private receiver builds use `EU868_CYPRUS_G3`:
`869.525 MHz`, `125 kHz`, `SF7`, and `CR 4/5`. The profile records the
`869.4–869.65 MHz` band, `500 mW e.r.p.` ceiling, and `10%` maximum duty cycle
for the initial Cyprus tests. Those regulatory limits are not configured
power targets. XIAO transmits at raw `+14 dBm`; actual e.r.p. must include the
RF path and antenna.

T096 uses the same five-byte compact v2 frame. A position is eligible only
when the latest checksum-valid GNGGA/GPGGA fix quality or GNRMC/GPRMC status
says valid and position age is at most 30 seconds. Firmware converts GNSS E7
to local X/Y using a WGS84 scale evaluated at the last committed runtime event
origin latitude; longitude deltas take the shortest path across the
antimeridian. The telemetry window is 10 seconds and the base schedule is at
least 15 seconds plus positive jitter. RadioLib drives the SX1262 at raw 0 dBm;
approximately 14 dBm after the onboard PA is a design target, not measured or
certified output. Compact v2 is plaintext and unauthenticated. Nearby radio
equipment can observe or spoof it, so the current firmware assumes a trusted
environment.

Every wristband accepts `EVS1` over the existing BLE transfer boundary with a
participant from 0 through 15 and signed-E7 event origin. It replies with
accepted `EVA1` only after the complete 32-byte `FD,F0...F5,EF` race-session
transaction is persisted and at least one further contact record still fits.
The terminal `EF` record defines start-relative tick zero; a journal with fewer
than nine free record slots rejects the start without appending a partial
transaction. Before the accepted ACK, LoRa-capable builds hardware-reset the
SX1262, clear realtime history, and restart the scheduler's full initial phase
so an old in-flight frame or T096 interval cannot cross into the new
race-session.

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

The wristband accepts station IDs 0 through 254. Value 255 is reserved for its
special-record format and is never a station ID. In the current event flow, S0
is finish only. START is a separate persisted command and is never an S0
contact. S0 represents either the physical finish station or phone finish
station 0, which the compact log intentionally does not distinguish. Never
assign S0 as an ordinary checkpoint or ghost; checkpoint and ghost roles use
S1...S254.

If multiple UF2 drives are mounted, run, for example:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh xiao-external

The helper verifies INFO_UF2.TXT after selecting the target. An ordinary
directory is rejected even when supplied explicitly through UF2_VOLUME.
