# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

SRC = Path(r"d:\app-fix\apktool_out")
DST = Path(r"d:\app-fix\apktool_out_standalone")
OLD_PKG = "com.alensw.PicFolder"
NEW_PKG = "io.github.quickpic.gallery"


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("build", "original"))

    replacements = [
        (OLD_PKG.replace(".", "/"), NEW_PKG.replace(".", "/")),
        (OLD_PKG, NEW_PKG),
    ]

    changed_files = 0
    for p in sorted(DST.rglob("*")):
        if not p.is_file() or p.suffix not in (".smali", ".xml", ".yml", ".yaml", ".json", ".txt", ".properties"):
            continue
        text = p.read_text(encoding="utf-8")
        new_text = text
        for old_str, new_str in replacements:
            new_text = new_text.replace(old_str, new_str)
        if new_text != text:
            p.write_text(new_text, encoding="utf-8", newline="\n")
            changed_files += 1

    moved_dirs = 0
    for smali_dir in DST.glob("smali*"):
        if not smali_dir.is_dir():
            continue
        src_pkg_dir = smali_dir / Path(*OLD_PKG.split("."))
        dst_pkg_dir = smali_dir / Path(*NEW_PKG.split("."))
        if src_pkg_dir.exists():
            dst_pkg_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_pkg_dir), str(dst_pkg_dir))
            moved_dirs += 1

    print(f"Standalone package tree prepared: {changed_files} files updated, {moved_dirs} smali dirs moved.")


if __name__ == "__main__":
    main()
