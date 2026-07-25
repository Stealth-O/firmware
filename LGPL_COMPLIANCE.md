# LGPL Release Requirements

The public firmware statically links components distributed under the GNU
Lesser General Public License, version 2.1 or later. This release therefore
ships corresponding source, application object files, rebuild instructions,
and exact relinking tools. These materials let a recipient replace the
LGPL-covered components without requiring Stealth-O application source.

## Covered Build Families

The XIAO/station family is built with Seeeduino nRF52 Arduino core `1.1.12`.
Its LGPL-covered build inputs include the core, selected XIAO board variant,
and SPI library. Corresponding source is in
`lgpl-compliance/source.tar.gz`; relocatable compiler arguments are in
`lgpl-compliance/core-spi-compile-commands.json`.

The T096 family is built from untagged upstream `main` snapshot
`53b3d4a126bd144f94642203605031dd0aa93354` in the Heltec mirror. The
immutable mirror tag `stealth-o-t096-audit-2026-07-20` resolves to that exact
commit. The snapshot's `platform.txt` reports `1.6.0`; that value is upstream
platform metadata, not a release tag identifying this later snapshot. Its
`untagged-main` classification means no upstream tag outside the declared
`stealth-o-` mirror namespace points at this commit in the audited local mirror
tag set; it does not make a claim about an unfetched remote. Validation rejects
shallow repositories and requires the known upstream tag `1.7.0` to resolve to
`d45d40df192eb155df3c1f809387591d515383ab`, preserving an offline tag/history
anchor for the audit. Its LGPL-covered build inputs include the core, selected
`HT-n5262G` board variant, SPI library, and TinyGPS++ `1.0.2`. Corresponding
source is in `lgpl-compliance/source-t096.tar.gz`; relocatable compiler
arguments are in
`lgpl-compliance/t096-core-spi-tinygps-compile-commands.json`.

The root `LICENSE` history is explicit in the mirror: commit
`d2a9a9d94e7d353ff0be6ff6f12729987be8e093` added LGPL-2.1 on 2024-07-15,
commit `4d07cb994509aaaa641df898374ced2a59dc0a9e` removed the file on
2024-12-17, and commit `3f65fec81c8f9b1e3abf6f70dede1526e5524bca` added GPL-3.0 on
2024-12-20. The complete current GPL-3.0 text is preserved verbatim as
`source/hardware/LICENSE` in the T096 source archive. The adjacent
`source/hardware/STEALTH-O-LICENSING-NOTE.txt` explains that repository-level
context without deleting, changing, or attempting to supersede any upstream
notice. The captured T096 compile manifest contains 64 direct source
compilation units; every one is independently checked against its file-level
license header. Plain GPL-only, AGPL, unknown, or missing compiled-source
license classifications stop the release unless a narrowly pinned audited
exception applies.

The selected `HT-n5262G/variant.cpp` is byte-for-byte identical to the 44-line
`HT-n5262/variant.cpp` present at commit
`7e1e40cb07452e2b43de9d1177d2d5e64ccbd8e9` on 2024-07-15; both have
SHA-256 `e5265f6f9f0ad1937c0d913aeeef83be48ef30109d733344c27e4e476a55acd4`.
The current `HT-n5262G/variant.h` contains its own explicit
LGPL-2.1-or-later file-level notice. These facts document the audited source
history; they do not amend or replace upstream terms.

The release workflow pins and verifies both the current file and historical Git
blob directly, proves the historical commit is an ancestor of the selected
snapshot, and requires the two files to be byte-identical. It also requires the
XIAO and T096 ARM CryptoCell CC310 archives to match each other and the audited SHA-256
`97dc648d44520e47252f62c402a71f976e36d7b3aef99235bbdc4de79a928577`.
The verified archive is copied freshly into `lgpl-compliance/tool-libraries`;
both hashes are recorded in the applicable provenance documents.
The descriptor separately declares the selected `variant.h` and requires the
semantic file-level license classifier to return exactly
`LGPL-2.1-or-later`. Its path,
required classification, and actual classification are recorded in T096
provenance; removing or changing that file-level grant stops the release.

The T096 image does not compile, link, or redistribute Heltec's
`Heltec_nrf_lorawan` component or its precompiled `liblorawan.a`. Raw SX1262
operation uses RadioLib `7.7.1` under MIT. SEGGER RTT/SystemView compilation
units and their headers are present in both the Seeeduino and Heltec
corresponding-source and intermediate core archives. The current final station,
XIAO wristband, and T096 wristband images retain no SEGGER symbols. Their
complete redistribution notice is still included because source and
intermediate objects are distributed.

## Relinking Materials

The public `lgpl-compliance` directory contains:

- the two corresponding-source archives and relocatable compile-command files;
- provenance for the exact board cores, variants, toolchain, and excluded
  components;
- one ordered application/dependency object bundle for the station baseline
  and each of the five public wristband artifacts;
- `rebuild_lgpl.py`, which rebuilds the applicable core, variant, SPI objects,
  and TinyGPS++ for T096;
- `relink.sh`, linker scripts, link libraries, GNU Arm toolchain metadata, UF2
  conversion, and station-ID patching tools.

The supplied Stealth-O application objects are the materials needed to link a
modified LGPL library into working firmware. They are not source code and do
not change the separate terms that govern third-party objects. Complete
component notices are in `THIRD_PARTY_NOTICES.txt` and `licenses/`.

## Release Gates

The private release workflow fails closed unless it can:

1. enumerate and classify every compiled T096 source from the captured compile
   commands and independently preflight the live pinned core/SPI/variant input;
2. reject a shallow Heltec checkout, verify its immutable mirror tag and known
   upstream `1.7.0` tag anchor, and derive snapshot identity from the audited
   local mirror tag set;
3. verify the pinned T096 variant-lineage and CC310 archive SHA-256 values and
   require the declared variant header to classify as `LGPL-2.1-or-later`;
4. reject unapproved plain GPL-only, AGPL, unknown, or missing file-level
   license classifications;
5. verify the exact allowlist of linked static libraries and reject an
   unexpected archive, including `liblorawan.a`;
6. include all required corresponding source, including the pinned CMSIS
   license and headers used by the compile commands;
7. rebuild the applicable LGPL components from the published source archives;
8. exact-relink the station baseline and all five wristband artifacts with
   both the original and rebuilt LGPL objects; and
9. reproduce every published UF2 byte-for-byte.

The release scripts and normal wristband build use `SOURCE_DATE_EPOCH=0`.
Recipients seeking byte-for-byte comparison must use the same epoch and GNU
Arm Embedded Toolchain `9-2019q4`. Detailed commands are in
`lgpl-compliance/README.md`.

The exact-link matrix covers the linked-default `station-S254.uf2` baseline,
`wristband-xiao-external.uf2`, `wristband-xiao-internal.uf2`,
`wristband-xiao-lora-external.uf2`, `wristband-xiao-lora-internal.uf2`, and
`wristband-t096-internal.uf2`. Each is first relinked with the distributed
original objects and then with the LGPL components rebuilt from the matching
source archive. Both outputs must match the published UF2 byte-for-byte.
`set_station_id.py` reproducibly derives `station-S00.uf2` through
`station-S253.uf2` from the verified station baseline.

## Recipient Rights And Operational Checklist

For each release:

1. Include a prominent notice that LGPL-covered components are used.
2. Include the complete LGPL-2.1 license text.
3. Provide complete corresponding source for the LGPL-covered components,
   including any modifications to those components.
4. Provide the application objects and tooling needed to relink a modified
   LGPL component into working firmware.
5. Provide the build configuration, dependency versions, and instructions
   reasonably necessary to perform that relinking.
6. Do not prohibit modification for the recipient's own use or reverse
   engineering performed to debug those modifications.
7. Preserve every additional license and attribution required by components
   listed in `THIRD_PARTY_NOTICES.txt`.

Stealth-O permissions for the proprietary application are described in the
release root `LICENSE.txt`, including the applicable LGPL relinking and
reverse-engineering exception. Third-party source and objects remain governed
by their own licenses.

`SHA256SUMS` covers every regular release file except the checksum manifest
itself. It detects accidental changes but is not a cryptographic signature of
publisher identity.

Re-audit this document, both source inventories, linked archives, and every
dependency notice whenever a core, toolchain, board profile, or library
changes. This document is operational guidance, not legal advice.
