# Stealth-O firmware release services

Firmware updates are distributed through the Stealth-O app catalogue. USB is
used only for power. First installation and bootloader replacement use SWD
with a Pico debugprobe and the project's SWD installer.

This repository provides:

* [the LGPL notice and written relink offer for app catalogue firmware](CATALOG_LGPL_OFFER.txt),
  including earlier, hidden and withdrawn releases;
* [catalogue release identities and hashes](CATALOG_LGPL_RELEASES.json);
* [historical LGPL relink materials](lgpl-compliance/) and their
  [build documentation](LGPL_COMPLIANCE.md), [third-party notices](THIRD_PARTY_NOTICES.txt)
  and [licenses](licenses/);
* the global release number allocator in `.github/workflows/allocate-release.yml`
  and its independent `registry` branch.

The historical relink archives cover the former station S00–S190 images and
five wristband variants. Their original image hashes and build manifest remain
in [the last public USB download snapshot](https://github.com/Stealth-O/firmware/tree/931dbaee5600f9e61c2bee2788368631cb76083c).
The archives and their instructions are retained for those recipients. Their
ability to generate a UF2 during relinking is not a USB installation procedure.
They do not reproduce later app catalogue binaries: use the written offer to
request materials for your exact image.

There are no current USB firmware downloads or USB flashing helpers here.
The [proprietary terms](LICENSE.txt) preserve the applicable LGPL modification
and debugging rights; the catalogue offer explicitly extends these permissions
to receiver images. Third-party materials keep their own licenses.
