# LGPL Release Requirements

The current firmware build uses the Seeed Studio nRF52 Arduino core and SPI
library under LGPL-2.1-or-later. The firmware is statically linked.

The current release provides these materials in `lgpl-compliance`. For future
UF2 releases, regenerate and verify that directory. The private release
workflow refuses to produce a package when relinking with either the supplied
objects or rebuilt LGPL components does not reproduce the published UF2
images. The applicable requirements include, at minimum:

1. Include a prominent notice that LGPL-covered components are used.
2. Include the complete LGPL license text.
3. Provide the complete corresponding source for the LGPL-covered libraries,
   including any Stealth-O modifications to those libraries.
4. Provide the application object files and relinking materials needed to
   link a modified LGPL library into a working firmware image.
5. Provide the scripts, build configuration, dependency versions, and
   instructions reasonably necessary to perform that relinking.
6. Do not prohibit modification for the recipient's own use or reverse
   engineering performed to debug those modifications.
7. Preserve every additional license and attribution required by the other
   third-party components listed in THIRD_PARTY_NOTICES.txt.

The proprietary Stealth-O source code does not need to be published merely
because it links to an LGPL library, provided the release satisfies the LGPL
requirements for relinking and all other applicable terms.

This checklist describes the current build based on Seeeduino nRF52 core
version 1.1.12. Re-audit the dependencies whenever the toolchain or linked
libraries change.

`SHA256SUMS` covers every regular release file except the checksum manifest
itself. It detects accidental changes but is not a cryptographic signature of
publisher identity.

This document is operational guidance, not legal advice.
