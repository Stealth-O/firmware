/* Heltec T096 nRF52840 + S140 6.1.1 fixed internal-journal memory layout. */

SEARCH_DIR(.)
GROUP(-lgcc -lc -lnosys)

MEMORY
{
  FLASH (rx) : ORIGIN = 0x26000, LENGTH = 0xAD000 - 0x26000

  /* SRAM required by SoftDevice depends on the configured BLE resources. */
  RAM (rwx)  : ORIGIN = 0x20006000, LENGTH = 0x20040000 - 0x20006000
}

/* Runtime storage only: intentionally not a MEMORY region or section target. */
__wristband_journal_start = 0xAD000;
__wristband_journal_end = 0xED000;

SECTIONS
{
  . = ALIGN(4);
  .svc_data :
  {
    PROVIDE(__start_svc_data = .);
    KEEP(*(.svc_data))
    PROVIDE(__stop_svc_data = .);
  } > RAM

  .fs_data :
  {
    PROVIDE(__start_fs_data = .);
    KEEP(*(.fs_data))
    PROVIDE(__stop_fs_data = .);
  } > RAM
} INSERT AFTER .data;

INCLUDE "nrf52_common.ld"

ASSERT(
  LOADADDR(.data) + SIZEOF(.data) <= __wristband_journal_start,
  "application flash image overlaps wristband journal"
)
ASSERT(
  __wristband_journal_end - __wristband_journal_start == 0x40000,
  "wristband journal must be exactly 256 KiB"
)
ASSERT(
  ORIGIN(FLASH) + LENGTH(FLASH) == __wristband_journal_start,
  "application FLASH must end at wristband journal start"
)
ASSERT(
  (__wristband_journal_start & 0xFFF) == 0 &&
  (__wristband_journal_end & 0xFFF) == 0,
  "wristband journal must be flash-page aligned"
)
