Wristband firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

These are the Stealth-O wristband-v2 builds for Seeed XIAO nRF52840. Every
variant uses four-byte journal records, WBT2 protocol version 3, and the same
BLE transfer contract. See ../manifest.json for the complete variant contract
and artifact SHA-256 values.

Files:

- wristband-xiao-external.uf2 - onboard external QSPI journal.
- wristband-xiao-internal.uf2 - fixed 256 KiB internal-flash journal.
- wristband-xiao-lora-external.uf2 - external QSPI plus Wio-SX1262 LoRa TX.
- wristband-xiao-lora-internal.uf2 - internal flash plus Wio-SX1262 LoRa TX.
- flash.sh - flashes one explicitly selected artifact.

The LoRa variants require a Seeed Wio-SX1262 for XIAO and a suitable antenna.
Never transmit without the antenna. They use the versioned Stealth-O LoRa
hello protocol described by manifest.json and link RadioLib 7.7.1 under MIT.
Every hello is identified by device id, storage epoch, a fresh sender boot
nonce, and sender sequence, so an ordinary reboot cannot reuse the previous
sequence namespace.

Flash:

1. Connect the wristband board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run one of:

   ./flash.sh xiao-external
   ./flash.sh xiao-internal
   ./flash.sh xiao-lora-external
   ./flash.sh xiao-lora-internal

No public serial monitor helper is required for flashing. The wristband uses
its stable factory-derived device id, so no per-wristband number setup is
required.

The wristband accepts station IDs 0 through 254. Value 255 is reserved for its
special-record format and is never a station ID. In the current MVP event flow,
S0 has the start_finish role only: it represents either the physical
start/finish station or phone station 0, which the compact log intentionally
does not distinguish. Never assign S0 as an ordinary checkpoint or ghost;
checkpoint and ghost roles use S1...S254.

If multiple UF2 drives are mounted, run, for example:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh xiao-external

The helper verifies INFO_UF2.TXT after selecting the target. An ordinary
directory is rejected even when supplied explicitly through UF2_VOLUME.
