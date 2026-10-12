#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Furkan Köykıran
"""
scripts/verify_brand.py

Automated Brand System Verification Suite for fcode.
Enforces the 7 core brand invariants and the strict Transparency Contract:
1. Canonical Mark Geometry: all mark instances use the exact master coordinates without distortion.
2. Canonical Mascot Geometry: all mascot instances use the exact master coordinates of sentinel 'syn'.
3. Uniform Transforms: all scaling is uniform (sx == sy), preserving angles and proportions.
4. Zero <text> Tags: brand-critical text is strictly frozen vector path outlines.
5. Avatar Mark Placement: square and circle avatars have mathematically identical mark placement.
6. Dimension and Format Integrity: all raster and vector assets match specified dimensions and valid XML.
7. Alpha & Transparency Contract:
   - Reusable mark, wordmark, and mascot transparent exports have alpha=0 corners and >20% transparent area.
   - Transparent SVGs contain NO full-canvas background <rect>.
   - Opaque exports (*-on-dark, *-on-light, avatars, social previews) have opaque corners and explicit backgrounds.
   - Circular avatars preserve transparent corner bounds around the circular badge.
   - Favicons preserve transparency for web bookmarks, while touch icons have solid backgrounds.
   - Every filename accurately communicates its background semantics.
"""

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_DIR = os.path.join(BASE_DIR, "assets", "brand")

# Canonical coordinate invariants - Mark
CANONICAL_BRACKET = "M 172 168 L 132 168 L 132 344 L 172 344"
CANONICAL_ARROW = "M 148 238 L 168 256 L 148 274"
CANONICAL_F = "M 216 384 L 194 384 L 194 172 L 236 128 L 336 128 L 302 168 L 238 168 L 238 214 L 306 214 L 284 254 L 238 254 L 238 348 Z"
CANONICAL_SLASH_X1 = "256"
CANONICAL_SLASH_Y1 = "364"
CANONICAL_SLASH_X2 = "280"
CANONICAL_SLASH_Y2 = "304"
CANONICAL_CURSOR_X = "330"
CANONICAL_CURSOR_Y = "214"
CANONICAL_CURSOR_W = "46"
CANONICAL_CURSOR_H = "66"

# Canonical coordinate invariants - Mascot 'syn'
CANONICAL_SYN_CROWN = "M 148 112 L 172 44 L 214 96 L 256 86 L 298 96 L 340 44 L 364 112"
CANONICAL_SYN_BROW_DIVIDER = 'x1="214" y1="96" x2="298" y2="96"'
CANONICAL_SYN_BROW = 'x1="168" y1="136" x2="344" y2="136"'
CANONICAL_SYN_EYE_L_SOCKET = "M 196 168 L 164 168 L 164 248 L 196 248"
CANONICAL_SYN_EYE_L_ARROW = "M 184 194 L 210 208 L 184 222"
CANONICAL_SYN_EYE_R_SOCKET = "M 316 168 L 348 168 L 348 248 L 316 248"
CANONICAL_SYN_EYE_R_CURSOR = 'x="286" y="190" width="34" height="44"'
CANONICAL_SYN_BEAK_CHEVRON = "M 236 248 L 256 284 L 276 248"
CANONICAL_SYN_BEAK_SLASH = 'x1="256" y1="284" x2="246" y2="324"'
CANONICAL_SYN_WING_L = "M 140 316 L 100 316 L 100 428 L 152 428"
CANONICAL_SYN_WING_R = "M 372 316 L 412 316 L 412 428 L 360 428"
CANONICAL_SYN_BASELINE = 'x1="64" y1="472" x2="448" y2="472"'


def verify_svg_xml_and_no_text():
    """Invariant 1: Valid XML and zero <text> tags in brand SVGs."""
    print("Checking Invariant 1: Valid XML and Zero <text> tags in brand SVGs...")
    svg_files = [f for f in sorted(os.listdir(BRAND_DIR)) if f.endswith(".svg")]
    if not svg_files:
        raise AssertionError("No SVG files found in assets/brand/")

    for f in svg_files:
        path = os.path.join(BRAND_DIR, f)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
        except Exception as e:
            raise AssertionError(f"Invalid XML in {f}: {e}")

        text_elements = root.findall(".//{http://www.w3.org/2000/svg}text") + root.findall(".//text")
        if text_elements:
            raise AssertionError(
                f"Prohibited <text> element found in {f}. Brand SVGs must use frozen vector outlines."
            )
        print(f"  [PASS] {f}: valid XML, 0 <text> tags")


def verify_canonical_geometry():
    """Invariant 2: Canonical mark geometry exact coordinate match."""
    print("Checking Invariant 2: Canonical Mark Geometry exact coordinates...")
    mark_svgs = [
        "fcode-mark-master.svg",
        "fcode-mark.svg",
        "fcode-mark-transparent.svg",
        "fcode-mark-on-dark.svg",
        "fcode-mark-on-light.svg",
        "fcode-mark-light.svg",
        "fcode-wordmark-master.svg",
        "fcode-wordmark.svg",
        "fcode-wordmark-transparent.svg",
        "fcode-wordmark-on-dark.svg",
        "fcode-wordmark-on-light.svg",
        "fcode-wordmark-light.svg",
        "fcode-social-preview-1280x640.svg",
        "fcode-motion-pulse.svg",
    ]

    for f in mark_svgs:
        path = os.path.join(BRAND_DIR, f)
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()

        if CANONICAL_BRACKET not in content:
            raise AssertionError(f"{f} missing canonical bracket coordinate!")
        if CANONICAL_ARROW not in content:
            raise AssertionError(f"{f} missing canonical arrow coordinate!")
        if CANONICAL_F not in content:
            raise AssertionError(f"{f} missing canonical angular f coordinate!")
        if f'x1="{CANONICAL_SLASH_X1}" y1="{CANONICAL_SLASH_Y1}" x2="{CANONICAL_SLASH_X2}" y2="{CANONICAL_SLASH_Y2}"' not in content:
            raise AssertionError(f"{f} missing canonical slash coordinates!")
        if f'x="{CANONICAL_CURSOR_X}" y="{CANONICAL_CURSOR_Y}" width="{CANONICAL_CURSOR_W}" height="{CANONICAL_CURSOR_H}"' not in content:
            raise AssertionError(f"{f} missing canonical cursor coordinates!")

        print(f"  [PASS] {f}: exact canonical mark geometry verified")


def verify_mascot_geometry():
    """Invariant 3: Canonical mascot 'syn' geometry coordinates."""
    print("Checking Invariant 3: Canonical Mascot 'syn' Geometry exact coordinates...")
    mascot_svgs = [
        "fcode-mascot-master.svg",
        "fcode-mascot.svg",
        "fcode-mascot-transparent.svg",
        "fcode-mascot-on-dark.svg",
        "fcode-mascot-on-light.svg",
    ]

    for f in mascot_svgs:
        path = os.path.join(BRAND_DIR, f)
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()

        if CANONICAL_SYN_CROWN not in content:
            raise AssertionError(f"{f} missing canonical mascot crown crest!")
        if CANONICAL_SYN_BROW_DIVIDER not in content:
            raise AssertionError(f"{f} missing canonical mascot brow divider!")
        if CANONICAL_SYN_BROW not in content:
            raise AssertionError(f"{f} missing canonical mascot brow rule!")
        if CANONICAL_SYN_EYE_L_SOCKET not in content:
            raise AssertionError(f"{f} missing canonical mascot left bracket eye!")
        if CANONICAL_SYN_EYE_L_ARROW not in content:
            raise AssertionError(f"{f} missing canonical mascot prompt arrow eye!")
        if CANONICAL_SYN_EYE_R_SOCKET not in content:
            raise AssertionError(f"{f} missing canonical mascot right bracket eye!")
        if CANONICAL_SYN_EYE_R_CURSOR not in content:
            raise AssertionError(f"{f} missing canonical mascot cursor eye!")
        if CANONICAL_SYN_BEAK_CHEVRON not in content:
            raise AssertionError(f"{f} missing canonical mascot beak chevron!")
        if CANONICAL_SYN_BEAK_SLASH not in content:
            raise AssertionError(f"{f} missing canonical mascot beak slash!")
        if CANONICAL_SYN_WING_L not in content:
            raise AssertionError(f"{f} missing canonical mascot left wing coordinates!")
        if CANONICAL_SYN_WING_R not in content:
            raise AssertionError(f"{f} missing canonical mascot right wing coordinates!")
        if CANONICAL_SYN_BASELINE not in content:
            raise AssertionError(f"{f} missing canonical mascot baseline perch!")

        print(f"  [PASS] {f}: exact canonical mascot geometry verified")


def verify_uniform_transforms():
    """Invariant 4: All transforms on mark and mascot groups must be uniform scaling."""
    print("Checking Invariant 4: Uniform transforms only (no non-uniform stretching)...")
    for f in sorted(os.listdir(BRAND_DIR)):
        if not f.endswith(".svg"):
            continue
        path = os.path.join(BRAND_DIR, f)
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()

        transforms = re.findall(r'transform="([^"]+)"', content)
        for t in transforms:
            scales = re.findall(r'scale\(([^)]+)\)', t)
            for sc in scales:
                parts = [p.strip() for p in sc.split(",")]
                if len(parts) == 2:
                    if float(parts[0]) != float(parts[1]):
                        raise AssertionError(
                            f"Non-uniform scale {sc} found in {f} transform: {t}"
                        )
        print(f"  [PASS] {f}: transforms are uniform")


def verify_avatar_parity():
    """Invariant 5: Square and circular avatars must have identical mark scale and placement."""
    print("Checking Invariant 5: Square and Circle avatar placement parity...")
    sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
    from generate_brand import build_avatar_svg

    sq_svg = build_avatar_svg(mask="square")
    cr_svg = build_avatar_svg(mask="circle")

    sq_match = re.search(r'<g transform="([^"]+)"', sq_svg)
    cr_match = re.search(r'<g transform="([^"]+)"', cr_svg)

    if not sq_match or not cr_match:
        raise AssertionError("Avatar mark transform group not found!")

    if sq_match.group(1) != cr_match.group(1):
        raise AssertionError(
            f"Avatar mark transforms differ!\nSquare: {sq_match.group(1)}\nCircle: {cr_match.group(1)}"
        )

    print(f"  [PASS] Avatar mark transforms match identically: {sq_match.group(1)}")


def verify_raster_dimensions():
    """Invariant 6: Raster dimensions match exact pixel specifications."""
    print("Checking Invariant 6: Raster dimensions match specifications...")
    expected_dims = {
        "fcode-social-preview-1280x640.png": "1280x640",
        "fcode-social-preview-1280x640.jpg": "1280x640",
        "fcode-avatar-square.png": "1024x1024",
        "fcode-avatar-circle.png": "1024x1024",
        "fcode-mascot-avatar.png": "1024x1024",
        "fcode-mark-transparent.png": "512x512",
        "fcode-mark.png": "512x512",
        "fcode-mark-on-dark.png": "512x512",
        "fcode-mark-dark.png": "512x512",
        "fcode-mark-on-light.png": "512x512",
        "fcode-mark-light.png": "512x512",
        "fcode-mascot-transparent.png": "512x512",
        "fcode-mascot.png": "512x512",
        "fcode-mascot-on-dark.png": "512x512",
        "fcode-mascot-on-light.png": "512x512",
        "fcode-wordmark-transparent.png": "800x400",
        "fcode-wordmark.png": "800x400",
        "fcode-wordmark-on-dark.png": "800x400",
        "fcode-wordmark-dark.png": "800x400",
        "fcode-wordmark-on-light.png": "800x400",
        "fcode-wordmark-light.png": "800x400",
        "apple-touch-icon.png": "180x180",
        "favicon-32x32.png": "32x32",
        "favicon-16x16.png": "16x16",
    }

    for filename, expected in expected_dims.items():
        path = os.path.join(BRAND_DIR, filename)
        if not os.path.exists(path):
            raise AssertionError(f"Missing raster file {filename}!")

        out = subprocess.check_output(["identify", "-format", "%wx%h", path]).decode().strip()
        if out != expected:
            raise AssertionError(
                f"Dimension mismatch for {filename}: expected {expected}, got {out}"
            )
        print(f"  [PASS] {filename}: {out} (matches {expected})")

    ico_path = os.path.join(BRAND_DIR, "favicon.ico")
    if not os.path.exists(ico_path) or os.path.getsize(ico_path) == 0:
        raise AssertionError("favicon.ico is missing or empty!")
    print(f"  [PASS] favicon.ico: present ({os.path.getsize(ico_path)} bytes)")

    gif_path = os.path.join(BRAND_DIR, "fcode-motion-pulse.gif")
    if not os.path.exists(gif_path) or os.path.getsize(gif_path) == 0:
        raise AssertionError("fcode-motion-pulse.gif is missing or empty!")
    print(f"  [PASS] fcode-motion-pulse.gif: present ({os.path.getsize(gif_path)} bytes)")


def verify_transparency_contract():
    """Invariant 7: Rigorous Transparency and Alpha Semantics Contract."""
    print("Checking Invariant 7: Transparency and Alpha Semantics Contract...")

    # 1. Transparent PNG exports must have alpha=0 corner pixels and meaningful transparency area (> 20%)
    transparent_pngs = [
        "fcode-mark-transparent.png",
        "fcode-mark.png",
        "fcode-wordmark-transparent.png",
        "fcode-wordmark.png",
        "fcode-mascot-transparent.png",
        "fcode-mascot.png",
        "favicon-32x32.png",
        "favicon-16x16.png",
    ]

    for fname in transparent_pngs:
        path = os.path.join(BRAND_DIR, fname)
        if not os.path.exists(path):
            raise AssertionError(f"Missing transparent PNG {fname}")

        corner_cmd = [
            "convert", path,
            "-format", "%[pixel:p{0,0}] %[pixel:p{w-1,0}] %[pixel:p{0,h-1}] %[pixel:p{w-1,h-1}]",
            "info:"
        ]
        corners = subprocess.check_output(corner_cmd).decode().strip().split()
        for i, c in enumerate(corners):
            if not (",0)" in c or c == "none" or ",0.0)" in c):
                raise AssertionError(
                    f"{fname}: Corner {i} is not transparent! Value: {c}"
                )

        ratio_cmd = [
            "convert", path,
            "-alpha", "extract",
            "-format", "%[fx:1.0 - mean]",
            "info:"
        ]
        ratio_str = subprocess.check_output(ratio_cmd).decode().strip()
        trans_ratio = float(ratio_str)
        if trans_ratio < 0.20:
            raise AssertionError(
                f"{fname}: Transparency ratio too low ({trans_ratio:.2%}), expected > 20% transparent canvas"
            )

        print(f"  [PASS] Transparent PNG {fname}: alpha=0 on all corners, {trans_ratio:.1%} transparent canvas")

    # 2. Circular avatar badges: transparent corner bounding box, solid opaque disc center
    circular_avatars = [
        "fcode-avatar-circle.png",
        "fcode-mascot-avatar.png",
    ]

    for fname in circular_avatars:
        path = os.path.join(BRAND_DIR, fname)
        if not os.path.exists(path):
            raise AssertionError(f"Missing circular avatar {fname}")

        # Corners must be transparent
        corner_cmd = [
            "convert", path,
            "-format", "%[pixel:p{0,0}] %[pixel:p{w-1,0}] %[pixel:p{0,h-1}] %[pixel:p{w-1,h-1}]",
            "info:"
        ]
        corners = subprocess.check_output(corner_cmd).decode().strip().split()
        for i, c in enumerate(corners):
            if not (",0)" in c or c == "none" or ",0.0)" in c):
                raise AssertionError(
                    f"{fname}: Avatar outer corner {i} is not transparent! Value: {c}"
                )

        # Center disc must be solid
        center_cmd = ["convert", path, "-format", "%[pixel:p{512,512}]", "info:"]
        center_px = subprocess.check_output(center_cmd).decode().strip()
        if ",0)" in center_px or center_px == "none":
            raise AssertionError(
                f"{fname}: Avatar center pixel is not opaque! Value: {center_px}"
            )

        print(f"  [PASS] Circular avatar {fname}: transparent canvas corners, solid badge interior")

    # 3. Opaque PNG / JPG exports must have opaque corner pixels (alpha=1)
    opaque_rasters = [
        "fcode-mark-on-dark.png",
        "fcode-mark-dark.png",
        "fcode-mark-on-light.png",
        "fcode-mark-light.png",
        "fcode-wordmark-on-dark.png",
        "fcode-wordmark-dark.png",
        "fcode-wordmark-on-light.png",
        "fcode-wordmark-light.png",
        "fcode-mascot-on-dark.png",
        "fcode-mascot-on-light.png",
        "fcode-avatar-square.png",
        "fcode-social-preview-1280x640.png",
        "fcode-social-preview-1280x640.jpg",
        "apple-touch-icon.png",
    ]

    for fname in opaque_rasters:
        path = os.path.join(BRAND_DIR, fname)
        if not os.path.exists(path):
            raise AssertionError(f"Missing opaque raster {fname}")

        corner_cmd = [
            "convert", path,
            "-format", "%[pixel:p{0,0}] %[pixel:p{w-1,0}] %[pixel:p{0,h-1}] %[pixel:p{w-1,h-1}]",
            "info:"
        ]
        corners = subprocess.check_output(corner_cmd).decode().strip().split()
        for i, c in enumerate(corners):
            if ",0)" in c or c == "none":
                raise AssertionError(
                    f"{fname}: Opaque file has unexpected transparent corner {i}! Value: {c}"
                )

        print(f"  [PASS] Opaque raster {fname}: solid corner pixels confirmed ({corners[0]})")

    # 4. Transparent SVGs must NOT contain full-canvas background rects
    transparent_svgs = [
        "fcode-mark-master.svg",
        "fcode-mark.svg",
        "fcode-mark-transparent.svg",
        "fcode-wordmark-master.svg",
        "fcode-wordmark.svg",
        "fcode-wordmark-transparent.svg",
        "fcode-mascot-master.svg",
        "fcode-mascot.svg",
        "fcode-mascot-transparent.svg",
    ]

    for fname in transparent_svgs:
        path = os.path.join(BRAND_DIR, fname)
        tree = ET.parse(path)
        root = tree.getroot()

        svg_w = root.get("width")
        svg_h = root.get("height")

        rects = root.findall("{http://www.w3.org/2000/svg}rect") + root.findall("rect")
        for r in rects:
            rw = r.get("width")
            rh = r.get("height")
            if rw in ("100%", svg_w) and rh in ("100%", svg_h):
                raise AssertionError(
                    f"Transparent SVG {fname} contains prohibited full-canvas background rect ({rw}x{rh})!"
                )

        print(f"  [PASS] Transparent SVG {fname}: zero background rects, genuinely transparent canvas")

    # 5. Opaque SVGs must contain explicit background rects
    opaque_svgs = [
        "fcode-mark-on-dark.svg",
        "fcode-mark-on-light.svg",
        "fcode-mark-light.svg",
        "fcode-wordmark-on-dark.svg",
        "fcode-wordmark-on-light.svg",
        "fcode-wordmark-light.svg",
        "fcode-mascot-on-dark.svg",
        "fcode-mascot-on-light.svg",
        "fcode-social-preview-1280x640.svg",
    ]

    for fname in opaque_svgs:
        path = os.path.join(BRAND_DIR, fname)
        tree = ET.parse(path)
        root = tree.getroot()

        svg_w = root.get("width")
        svg_h = root.get("height")

        rects = root.findall("{http://www.w3.org/2000/svg}rect") + root.findall("rect")
        has_bg = any(
            (r.get("width") in ("100%", svg_w) and r.get("height") in ("100%", svg_h))
            for r in rects
        )
        if not has_bg:
            raise AssertionError(
                f"Opaque SVG {fname} missing required full-canvas background rect!"
            )

        print(f"  [PASS] Opaque SVG {fname}: explicit full-canvas background rect confirmed")


def main():
    print("==================================================")
    print("Running fcode Brand System Verification Suite")
    print("==================================================")
    try:
        verify_svg_xml_and_no_text()
        verify_canonical_geometry()
        verify_mascot_geometry()
        verify_uniform_transforms()
        verify_avatar_parity()
        verify_raster_dimensions()
        verify_transparency_contract()
        print("==================================================")
        print("ALL BRAND INVARIANTS VERIFIED SUCCESSFULLY (100% PASS)")
        print("==================================================")
    except AssertionError as e:
        print(f"\n[FAIL] Assertion Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
