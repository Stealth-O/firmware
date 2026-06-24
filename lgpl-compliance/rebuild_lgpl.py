#!/usr/bin/env python3

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess


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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--arm-gcc-dir",
        default=os.environ.get("ARM_GCC_DIR", default_toolchain),
        type=Path,
    )
    parser.add_argument("--build-dir", default=script_dir / "rebuilt", type=Path)
    parser.add_argument("--source-dir", default=script_dir / "source", type=Path)
    args = parser.parse_args()

    manifest_path = script_dir / "core-spi-compile-commands.json"
    if not args.source_dir.is_dir():
        raise SystemExit(
            f"Source directory not found: {args.source_dir}\n"
            "Extract source.tar.gz before rebuilding."
        )

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
    entries = json.loads(manifest_path.read_text())

    for entry in entries:
        command = [expand(value, replacements) for value in entry["arguments"]]
        output_index = command.index("-o") + 1
        Path(command[output_index]).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(command, check=True)

    core_objects = sorted((args.build_dir / "core").rglob("*.o"))
    if not core_objects:
        raise SystemExit("No core objects were built.")

    core_archive = args.build_dir / "core.a"
    subprocess.run(
        [str(ar_path), "rcs", str(core_archive), *map(str, core_objects)],
        check=True,
    )

    spi_objects = sorted((args.build_dir / "libraries/SPI").glob("*.o"))
    print(f"Built {core_archive}")
    for spi_object in spi_objects:
        print(f"Built {spi_object}")


if __name__ == "__main__":
    main()
