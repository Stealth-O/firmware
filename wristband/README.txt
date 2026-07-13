Wristband firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

Files:

- wristband.uf2 - ready-to-flash wristband firmware.
- flash.sh - copies wristband.uf2 to the XIAO UF2 bootloader drive.

Flash:

1. Connect the wristband board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run:

   ./flash.sh

No public serial monitor helper is required for flashing. The wristband uses
its stable factory-derived device id, so no per-wristband number setup is
required.

The wristband accepts station IDs 0 through 254. Value 255 is reserved for its
special-record format and is never a station ID. In the current MVP event flow,
S0 has the start_finish role only: it represents either the physical
start/finish station or phone station 0, which the compact log intentionally
does not distinguish. Never assign S0 as an ordinary checkpoint or ghost;
checkpoint and ghost roles use S1...S254.

If multiple UF2 drives are mounted, run:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh
