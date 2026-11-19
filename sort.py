#!/usr/bin/env python3
"""Sort built kernel modules into their partition directories."""

import re
import shutil
import sys
from pathlib import Path

DIST_DIR = Path(sys.argv[1])
CONFIG_DIR = Path("kernels/6.6")

def read_module_list(path: Path) -> list[str]:
    """Return module names from a .modules.load file, or [] if it's missing."""
    if not path.is_file():
        return []
    return path.read_text().split()


def main() -> None:
    # Modules that belong to the dlkm partitions are moved out of dist.
    for partition in ("system_dlkm", "vendor_dlkm"):
        dest = Path("dist/" + partition)
        dest.mkdir(exist_ok=True)
        for name in read_module_list(CONFIG_DIR / f"{partition}.modules.load"):
            src = DIST_DIR / name
            if src.is_file():
                shutil.move(src, dest)

    # Ramdisk list: normal list first, then recovery extras, no duplicates,
    # order preserved.
    ramdisk_modules = list(dict.fromkeys(
        read_module_list(CONFIG_DIR / "vendor_ramdisk.modules.load")
        + read_module_list(CONFIG_DIR / "vendor_ramdisk.modules.load.recovery")
    ))

    ramdisk_dir = Path("dist/vendor_ramdisk")
    ramdisk_dir.mkdir(exist_ok=True)
    for name in ramdisk_modules:
        if (src := DIST_DIR / name).is_file():
            shutil.move(src, ramdisk_dir)
        elif (src := Path("system_dlkm") / name).is_file():
            shutil.copy(src, ramdisk_dir)
        elif (src := Path("vendor_dlkm") / name).is_file():
            shutil.copy(src, ramdisk_dir)
        else:
            print(f"Missing: {name}")

    # Anything left over goes to misc.
    misc_dir = Path("dist/misc")
    misc_dir.mkdir(exist_ok=True)
    for ko in list(DIST_DIR.glob("*.ko")):
        shutil.move(ko, misc_dir)


if __name__ == "__main__":
    main()
