#!/usr/bin/env python3
"""Rebuild the LGPL-covered core, board variant, and SPI components."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


FAMILIES = {
    "heltec-t096": {
        "manifest": "t096-core-spi-tinygps-compile-commands.json",
        "source_archive": "source-t096.tar.gz",
    },
    "seeeduino-xiao": {
        "manifest": "core-spi-compile-commands.json",
        "source_archive": "source.tar.gz",
    },
}


def expand(value, replacements):
    for key, replacement in replacements.items():
        value = value.replace("${" + key + "}", str(replacement))
    return value


def main():
    script_dir = Path(__file__).resolve().parent
    default_toolchain = (
        Path.home()
        / "Library/Arduino15/packages/Seeeduino/tools/"
        / "arm-none-eabi-gcc/9-2019q4"
    )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--arm-gcc-dir",
        default=os.environ.get("ARM_GCC_DIR", default_toolchain),
        type=Path,
    )
    parser.add_argument("--build-dir", default=script_dir / "rebuilt", type=Path)
    parser.add_argument(
        "--family", choices=sorted(FAMILIES), default="seeeduino-xiao"
    )
    parser.add_argument("--source-dir", default=script_dir / "source", type=Path)
    args = parser.parse_args()

    family = FAMILIES[args.family]
    manifest_path = script_dir / family["manifest"]
    if not args.source_dir.is_dir():
        raise SystemExit(
            f"Source directory not found: {args.source_dir}\n"
            f"Extract {family['source_archive']} before rebuilding."
        )
    if not manifest_path.is_file():
        raise SystemExit(f"Compile manifest not found: {manifest_path}")

    ar_path = args.arm_gcc_dir / "bin/arm-none-eabi-ar"
    if not ar_path.is_file():
        raise SystemExit(f"GNU Arm toolchain not found: {args.arm_gcc_dir}")

    if args.build_dir.exists():
        shutil.rmtree(args.build_dir)
    args.build_dir.mkdir(parents=True)

    replacements = {
        "ARM_GCC_DIR": args.arm_gcc_dir.resolve(),
        "BUILD_DIR": args.build_dir.resolve(),
        "SOURCE_DIR": args.source_dir.resolve(),
    }
    entries = json.loads(manifest_path.read_text(encoding="utf-8"))
    source_hardware_dir = (args.source_dir.resolve() / "hardware").as_posix()
    path_remap_flags = [
        f"-ffile-prefix-map={source_hardware_dir}=arduino-core",
        f"-fmacro-prefix-map={source_hardware_dir}=arduino-core",
    ]

    outputs_by_component = {"core": [], "spi": [], "variant": []}
    for entry in entries:
        component = entry.get("component")
        if component is None:
            legacy_output = entry["arguments"][entry["arguments"].index("-o") + 1]
            if "/libraries/SPI/" in legacy_output:
                component = "spi"
            elif legacy_output.endswith("/core/variant.cpp.o"):
                component = "variant"
            else:
                component = "core"
        if component not in outputs_by_component:
            raise SystemExit(f"Unknown compile component: {component!r}")
        command = [expand(value, replacements) for value in entry["arguments"]]
        command[1:1] = path_remap_flags
        output_index = command.index("-o") + 1
        output_path = Path(command[output_index])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(command, check=True)
        outputs_by_component[component].append(output_path)

    core_objects = sorted(outputs_by_component["core"])
    if not core_objects:
        raise SystemExit("No core objects were built.")
    if len(outputs_by_component["variant"]) > 1:
        raise SystemExit("At most one board variant object may be built.")
    if args.family == "heltec-t096" and len(outputs_by_component["variant"]) != 1:
        raise SystemExit("The T096 rebuild requires exactly one board variant object.")

    core_archive = args.build_dir / "core.a"
    subprocess.run(
        [str(ar_path), "rcs", str(core_archive), *map(str, core_objects)],
        check=True,
    )
    print(f"Built {core_archive}")
    for variant_object in outputs_by_component["variant"]:
        print(f"Built {variant_object}")
    for spi_object in sorted(outputs_by_component["spi"]):
        print(f"Built {spi_object}")


if __name__ == "__main__":
    main()
