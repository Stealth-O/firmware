Station firmware

This README and the included helper scripts are licensed under the repository
root TOOLS_LICENSE.txt.

Files:

- station-S00.uf2 ... station-S254.uf2 - ready-to-flash station firmware
  images. Every image shares one universal code and carries its station number
  in a single data byte.
- flash.sh - copies the selected station image to the XIAO UF2 bootloader
  drive.

Flash:

1. Connect the station board over USB-C.
2. Press Reset twice quickly.
3. Wait for the UF2 bootloader drive to appear.
4. Run flash.sh with the station number from 0 to 254 (255 is reserved):

   ./flash.sh 42

The station number is part of the flashed firmware image. There is no runtime
station-number configuration step and no persistent station-number file.

S0 is a valid image, but the current MVP event flow reserves it for the
start_finish role only. Use it as the physical alternative to phone station 0;
never assign S0 as an ordinary checkpoint or ghost. Checkpoint and ghost roles
use S1...S254. Value 255 is reserved and is not a station image.

If multiple UF2 drives are mounted, run:

UF2_VOLUME="/Volumes/BOARDNAME" ./flash.sh 42
