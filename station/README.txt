Station firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

Files:

- station-S00.uf2 ... station-S99.uf2 - ready-to-flash station firmware
  images. Every image shares one universal code and carries its station number
  in a single data byte.
- flash.sh - copies the selected station image to the XIAO UF2 bootloader
  drive.

Flash:

1. Connect the station board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run flash.sh with the station number from 0 to 99:

   ./flash.sh 42

The station number is part of the flashed firmware image. There is no runtime
station-number configuration step and no persistent station-number file.

If multiple UF2 drives are mounted, run:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh 42
