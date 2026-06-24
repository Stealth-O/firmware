Wristband firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

Files:

- wristband.uf2 - ready-to-flash wristband firmware.
- flash.sh - copies wristband.uf2 to the XIAO UF2 bootloader drive.
- monitor.sh - opens the wristband serial monitor at 115200 baud.

Flash:

1. Connect the wristband board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run:

   ./flash.sh

Configure wristband number:

1. After flashing, wait for the board to reboot.
2. Run:

   ./monitor.sh

3. Type a command and press Enter:

   i7

This saves wristband number 7 and automatically restarts the wristband as W7.
Use any number from 0 to 99.

Useful commands:

- i - print identity.
- i7 - save wristband number 7 and restart as W7.
- s - print status.
- c - clear stored logs.
- p - dump stored log.
- b - toggle backup mode.

If multiple serial devices are connected, run:

SERIAL_PORT=/dev/cu.usbmodemXXXX ./monitor.sh

If multiple UF2 drives are mounted, run:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh
