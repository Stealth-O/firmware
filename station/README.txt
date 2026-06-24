Station firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

Files:

- station.uf2 - ready-to-flash station firmware.
- flash.sh - copies station.uf2 to the XIAO UF2 bootloader drive.
- monitor.sh - opens the station serial monitor at 115200 baud.

Flash:

1. Connect the station board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run:

   ./flash.sh

Configure station number:

1. After flashing, wait for the board to reboot.
2. Run:

   ./monitor.sh

3. Type a command and press Enter:

   i42

This saves station number 42 and automatically restarts the station as S42.
Use any number from 0 to 99.

Useful commands:

- i - print identity.
- i42 - save station number 42 and restart as S42.
- s - print status.
- b - print battery.

If multiple serial devices are connected, run:

SERIAL_PORT=/dev/cu.usbmodemXXXX ./monitor.sh

If multiple UF2 drives are mounted, run:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh
