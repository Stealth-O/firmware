/* Heltec T096 nRF52840 + S140 6.1.1 automatic internal-journal memory layout. */

SEARCH_DIR(.)
GROUP(-lgcc -lc -lnosys)

MEMORY
{
  FLASH (rx) : ORIGIN = 0x26000, LENGTH = 0xEB000 - 0x26000

  /* SRAM required by SoftDevice depends on the configured BLE resources. */
  RAM (rwx)  : ORIGIN = 0x20006000, LENGTH = 0x20040000 - 0x20006000
}

/* Runtime storage only: intentionally not a MEMORY region or section target. */
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

/* Include initializers loaded from flash into RAM, not just executable text.
 * The post-link gate independently checks every loadable ELF section. */
__wristband_application_start = ORIGIN(FLASH);
__wristband_flash_image_end = MAX(
  LOADADDR(.data) + SIZEOF(.data),
  MAX(SIZEOF(.svc_data) ? LOADADDR(.svc_data) + SIZEOF(.svc_data) : 0,
      SIZEOF(.fs_data) ? LOADADDR(.fs_data) + SIZEOF(.fs_data) : 0)
);
__wristband_journal_start = ALIGN(__wristband_flash_image_end, 0x1000);

ASSERT(
  __wristband_flash_image_end <= __wristband_journal_start,
  "application flash image overlaps wristband journal"
)
ASSERT(
  __wristband_journal_start <= __wristband_journal_end - 0x2000,
  "wristband journal needs a data page and a metadata page"
)
ASSERT(
  (__wristband_journal_start & 0xFFF) == 0 &&
  (__wristband_journal_end & 0xFFF) == 0,
  "wristband journal must be flash-page aligned"
)
