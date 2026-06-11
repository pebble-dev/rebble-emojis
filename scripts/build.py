#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Build all Rebble emoji assets in one go.

Runs:
  1. pbf_repack  → build/EMOJI18.pbf
  2. pbf_repack  → build/EMOJI24.pbf
  3. generate_readme → build/preview/**  +  README.md

Usage:
    python scripts/build.py            # build everything
    python scripts/build.py --fonts    # build .pbf files only
    python scripts/build.py --preview  # regenerate previews + README only
"""

import argparse
import os
import sys

# Make sure sibling scripts are importable
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import json
import pbf_repack
import generate_readme


def build_fonts(base_dir: str) -> bool:
    """Build EMOJI18.pbf and EMOJI24.pbf. Returns True on success."""
    build_dir = os.path.join(base_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    ok = True
    for size in ("18", "24"):
        manifest_path = os.path.join(base_dir, "src", f"emoji{size}", "font.json")
        output_path = os.path.join(build_dir, f"EMOJI{size}.pbf")

        if not os.path.exists(manifest_path):
            print(f"Error: manifest not found: {manifest_path}", file=sys.stderr)
            ok = False
            continue

        with open(manifest_path) as f:
            manifest = json.load(f)
        manifest["_manifest_path"] = manifest_path

        print(f"\n── Building EMOJI{size}.pbf ──")
        pbf_repack.build_pbf(manifest, output_path)

    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Rebble emoji assets")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--fonts",
        action="store_true",
        help="Only build the .pbf font binaries (skip preview/README update)",
    )
    group.add_argument(
        "--preview",
        action="store_true",
        help="Only regenerate preview images and update README.md (skip font build)",
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(SCRIPTS_DIR)

    do_fonts = not args.preview
    do_preview = not args.fonts

    success = True

    if do_fonts:
        if not build_fonts(base_dir):
            success = False

    if do_preview:
        print("\n── Generating previews and updating README.md ──")
        result = generate_readme.main()
        if result != 0:
            success = False

    if success:
        print("\n✓ Build complete.")
    else:
        print("\n✗ Build finished with errors.", file=sys.stderr)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
