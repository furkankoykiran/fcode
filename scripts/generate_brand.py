#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 Furkan Köykıran
"""
scripts/generate_brand.py

Canonical Brand Asset Generator for fcode.
All assets are deterministically derived from:
1. Canonical mark vector geometry (bracket, arrow, angular f, slash, crimson cursor)
2. Canonical mascot vector geometry (syn: the synthesis sentinel owl)
3. Canonical frozen vector path outlines for wordmark (f, c, o, d, e)

Self-contained:
- Zero runtime font dependencies (does not require /usr/share/fonts or external files).
- Zero non-uniform scaling distortions.

Transparency Contract:
- Reusable mark, wordmark, and mascot SVG/PNG exports have genuinely transparent canvases (no background rect, alpha=0 corners).
- *-on-dark / *-on-light, social previews, and intentionally backgrounded platform assets are opaque.
- Favicons preserve transparency around glyphs.
"""

import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_DIR = os.path.join(BASE_DIR, "assets", "brand")

# Canonical Color Palette Tokens
VOID_BLACK = "#08080a"
CARBON_CHARCOAL = "#121316"
STEEL_GRAPHITE = "#4a4d52"
GRID_MUTED = "#2a2d34"
BONE_WHITE = "#f0f0f2"
SIGNAL_CRIMSON = "#ff3b30"

# Canonical Mark Geometry Coordinates (512x512 coordinate space)
CANONICAL_BRACKET = "M 172 168 L 132 168 L 132 344 L 172 344"
CANONICAL_ARROW = "M 148 238 L 168 256 L 148 274"
CANONICAL_F = "M 216 384 L 194 384 L 194 172 L 236 128 L 336 128 L 302 168 L 238 168 L 238 214 L 306 214 L 284 254 L 238 254 L 238 348 Z"
CANONICAL_SLASH = (256, 364, 280, 304)
CANONICAL_CURSOR = (330, 214, 46, 66)

# Canonical Mascot Geometry Coordinates (syn: the synthesis sentinel, 512x512 space)
SYN_CROWN = "M 148 112 L 172 44 L 214 96 L 256 86 L 298 96 L 340 44 L 364 112"
SYN_BROW_DIVIDER = (214, 96, 298, 96)
SYN_BROW = (168, 136, 344, 136)
SYN_EYE_L_SOCKET = "M 196 168 L 164 168 L 164 248 L 196 248"
SYN_EYE_L_ARROW = "M 184 194 L 210 208 L 184 222"
SYN_EYE_R_SOCKET = "M 316 168 L 348 168 L 348 248 L 316 248"
SYN_EYE_R_CURSOR = (286, 190, 34, 44)
SYN_BEAK_CHEVRON = "M 236 248 L 256 284 L 276 248"
SYN_BEAK_SLASH = (256, 284, 246, 324)
SYN_CHEEK_L = "M 136 176 L 112 264 L 140 332"
SYN_CHEEK_R = "M 376 176 L 400 264 L 372 332"
SYN_WING_L = "M 140 316 L 100 316 L 100 428 L 152 428"
SYN_WING_R = "M 372 316 L 412 316 L 412 428 L 360 428"
SYN_CHEST_V = "M 208 344 L 256 384 L 304 344"
SYN_CHEST_CENTER = (256, 384, 256, 436)
SYN_CHEST_SLASH_L = (224, 404, 240, 436)
SYN_CHEST_SLASH_R = (288, 404, 272, 436)
SYN_TALON_L = "M 180 448 L 196 460 L 212 448"
SYN_TALON_R = "M 300 448 L 316 460 L 332 448"
SYN_BASELINE = (64, 472, 448, 472)

# Canonical Wordmark Frozen Vector Paths (Self-contained, zero external font dependency)
WORDMARK_PATH_800X400 = (
    "M 376.1 168.51 L 376.1 173.3 L 392.9 173.3 L 392.9 184.29 L 376.1 184.29 L 376.1 228.0 "
    "L 361.78 228.0 L 361.78 184.29 L 348.5 184.29 L 348.5 173.3 L 361.78 173.3 L 361.78 169.49 "
    "Q 361.78 159.62 365.88 155.81 Q 369.99 152.0 381.13 152.0 L 392.9 152.0 L 392.9 162.99 "
    "L 381.71 162.99 Q 378.49 162.99 377.34 164.16 Q 376.19 165.33 376.1 168.51 Z "
    "M 452.04 225.22 Q 448.43 227.32 444.27 228.37 Q 440.12 229.42 435.34 229.42 "
    "Q 422.69 229.42 415.56 221.8 Q 408.43 214.18 408.43 200.7 Q 408.43 187.17 415.61 179.52 "
    "Q 422.79 171.88 435.44 171.88 Q 439.83 171.88 443.91 172.91 Q 447.99 173.93 452.04 176.08 "
    "L 452.04 189.17 Q 448.92 186.48 445.18 185.04 Q 441.44 183.6 437.44 183.6 "
    "Q 430.45 183.6 426.69 188.05 Q 422.93 192.49 422.93 200.7 Q 422.93 208.9 426.69 213.3 "
    "Q 430.45 217.69 437.44 217.69 Q 441.59 217.69 445.2 216.3 Q 448.82 214.91 452.04 212.08 Z "
    "M 490.54 183.6 Q 485.41 183.6 482.48 188.12 Q 479.55 192.64 479.55 200.7 "
    "Q 479.55 208.76 482.48 213.27 Q 485.41 217.79 490.54 217.79 Q 495.71 217.79 498.64 213.27 "
    "Q 501.58 208.76 501.58 200.7 Q 501.58 192.64 498.64 188.12 Q 495.71 183.6 490.54 183.6 Z "
    "M 465.24 200.7 Q 465.24 187.46 472.1 179.72 Q 478.96 171.98 490.54 171.98 "
    "Q 502.16 171.98 509.02 179.72 Q 515.89 187.46 515.89 200.7 Q 515.89 213.93 509.02 221.68 "
    "Q 502.16 229.42 490.54 229.42 Q 478.96 229.42 472.1 221.68 Q 465.24 213.93 465.24 200.7 Z "
    "M 559.3 181.06 L 559.3 152.0 L 573.57 152.0 L 573.57 228.0 L 559.3 228.0 L 559.3 219.89 "
    "Q 557.01 224.63 553.37 227.02 Q 549.73 229.42 544.8 229.42 Q 535.42 229.42 530.25 221.89 "
    "Q 525.07 214.37 525.07 200.7 Q 525.07 186.83 530.32 179.41 Q 535.57 171.98 545.29 171.98 "
    "Q 549.68 171.98 553.17 174.25 Q 556.67 176.52 559.3 181.06 Z "
    "M 539.38 200.79 Q 539.38 208.71 542.01 213.2 Q 544.65 217.69 549.29 217.69 "
    "Q 553.93 217.69 556.62 213.2 Q 559.3 208.71 559.3 200.79 Q 559.3 192.88 556.62 188.38 "
    "Q 553.93 183.89 549.29 183.89 Q 544.65 183.89 542.01 188.38 Q 539.38 192.88 539.38 200.79 Z "
    "M 634.72 225.31 Q 629.73 227.37 624.56 228.39 Q 619.38 229.42 613.61 229.42 "
    "Q 599.89 229.42 592.63 222.06 Q 585.38 214.71 585.38 200.89 Q 585.38 187.51 592.37 179.75 "
    "Q 599.35 171.98 611.42 171.98 Q 623.58 171.98 630.3 179.19 Q 637.01 186.39 637.01 199.48 "
    "L 637.01 205.29 L 599.94 205.29 Q 599.99 211.74 603.75 214.91 Q 607.51 218.08 614.98 218.08 "
    "Q 619.92 218.08 624.7 216.67 Q 629.49 215.25 634.72 212.17 Z "
    "M 622.6 194.54 Q 622.5 188.88 619.69 185.97 Q 616.89 183.06 611.42 183.06 "
    "Q 606.48 183.06 603.55 186.06 Q 600.62 189.07 600.09 194.59 Z"
)
WORDMARK_CURSOR_X_800X400 = 651.1

WORDMARK_PATH_1280X640 = (
    "M 577.49 281.72 L 577.49 288.02 L 599.6 288.02 L 599.6 302.48 L 577.49 302.48 L 577.49 360.0 "
    "L 558.66 360.0 L 558.66 302.48 L 541.18 302.48 L 541.18 288.02 L 558.66 288.02 L 558.66 283.01 "
    "Q 558.66 270.03 564.06 265.01 Q 569.46 260.0 584.11 260.0 L 599.6 260.0 L 599.6 274.46 "
    "L 584.88 274.46 Q 580.64 274.46 579.13 276.0 Q 577.62 277.54 577.49 281.72 Z "
    "M 677.43 356.34 Q 672.67 359.1 667.21 360.48 Q 661.75 361.86 655.45 361.86 "
    "Q 638.8 361.86 629.42 351.84 Q 620.04 341.81 620.04 324.07 Q 620.04 306.27 629.48 296.22 "
    "Q 638.93 286.16 655.58 286.16 Q 661.36 286.16 666.73 287.51 Q 672.09 288.86 677.43 291.68 "
    "L 677.43 308.91 Q 673.31 305.37 668.39 303.48 Q 663.48 301.58 658.21 301.58 "
    "Q 649.02 301.58 644.07 307.43 Q 639.12 313.28 639.12 324.07 Q 639.12 334.87 644.07 340.65 "
    "Q 649.02 346.44 658.21 346.44 Q 663.67 346.44 668.43 344.61 Q 673.19 342.78 677.43 339.05 Z "
    "M 728.07 301.58 Q 721.32 301.58 717.47 307.52 Q 713.61 313.47 713.61 324.07 "
    "Q 713.61 334.68 717.47 340.62 Q 721.32 346.57 728.07 346.57 Q 734.88 346.57 738.74 340.62 "
    "Q 742.59 334.68 742.59 324.07 Q 742.59 313.47 738.74 307.52 Q 734.88 301.58 728.07 301.58 Z "
    "M 694.78 324.07 Q 694.78 306.66 703.81 296.48 Q 712.84 286.29 728.07 286.29 "
    "Q 743.36 286.29 752.39 296.48 Q 761.42 306.66 761.42 324.07 Q 761.42 341.49 752.39 351.68 "
    "Q 743.36 361.86 728.07 361.86 Q 712.84 361.86 703.81 351.68 Q 694.78 341.49 694.78 324.07 Z "
    "M 818.56 298.24 L 818.56 260.0 L 837.32 260.0 L 837.32 360.0 L 818.56 360.0 L 818.56 349.33 "
    "Q 815.53 355.57 810.75 358.72 Q 805.96 361.86 799.47 361.86 Q 787.13 361.86 780.32 351.97 "
    "Q 773.5 342.07 773.5 324.07 Q 773.5 305.82 780.41 296.06 Q 787.32 286.29 800.11 286.29 "
    "Q 805.89 286.29 810.49 289.27 Q 815.09 292.26 818.56 298.24 Z "
    "M 792.33 324.2 Q 792.33 334.61 795.81 340.52 Q 799.28 346.44 805.38 346.44 "
    "Q 811.49 346.44 815.02 340.52 Q 818.56 334.61 818.56 324.2 Q 818.56 313.79 815.02 307.88 "
    "Q 811.49 301.97 805.38 301.97 Q 799.28 301.97 795.81 307.88 Q 792.33 313.79 792.33 324.2 Z "
    "M 917.79 356.47 Q 911.24 359.16 904.42 360.51 Q 897.61 361.86 890.03 361.86 "
    "Q 871.97 361.86 862.42 352.19 Q 852.88 342.52 852.88 324.33 Q 852.88 306.72 862.07 296.5 "
    "Q 871.26 286.29 887.14 286.29 Q 903.14 286.29 911.97 295.76 Q 920.81 305.24 920.81 322.47 "
    "L 920.81 330.12 L 872.03 330.12 Q 872.1 338.6 877.05 342.77 Q 882.0 346.95 891.83 346.95 "
    "Q 898.32 346.95 904.62 345.09 Q 910.92 343.23 917.79 339.18 Z "
    "M 901.85 315.98 Q 901.73 308.52 898.04 304.69 Q 894.34 300.87 887.14 300.87 "
    "Q 880.65 300.87 876.79 304.82 Q 872.93 308.78 872.23 316.04 Z"
)
WORDMARK_CURSOR_X_1280X640 = 936.2


def get_canonical_mark_svg_group(stroke_color=BONE_WHITE, cursor_color=SIGNAL_CRIMSON):
    """Returns the canonical mark group XML string with 5 exact components."""
    x1, y1, x2, y2 = CANONICAL_SLASH
    cx, cy, cw, ch = CANONICAL_CURSOR
    return f"""<g id="fcode-canonical-mark">
    <path id="fcode-mark-bracket" d="{CANONICAL_BRACKET}" fill="none" stroke="{stroke_color}" stroke-width="14" stroke-linecap="square" stroke-linejoin="miter" />
    <path id="fcode-mark-arrow" d="{CANONICAL_ARROW}" fill="none" stroke="{stroke_color}" stroke-width="14" stroke-linecap="square" stroke-linejoin="miter" />
    <path id="fcode-mark-f" d="{CANONICAL_F}" fill="none" stroke="{stroke_color}" stroke-width="14" stroke-linecap="square" stroke-linejoin="miter" />
    <line id="fcode-mark-slash" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="14" stroke-linecap="square" />
    <rect id="fcode-mark-cursor" x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="{cursor_color}" />
  </g>"""


def get_canonical_mascot_svg_group(stroke_color=BONE_WHITE, cursor_color=SIGNAL_CRIMSON, grid_color=STEEL_GRAPHITE):
    """Returns the canonical mascot (syn) group XML string with exact vector components."""
    bx1, by1, bx2, by2 = SYN_BROW_DIVIDER
    brx1, bry1, brx2, bry2 = SYN_BROW
    rx, ry, rw, rh = SYN_EYE_R_CURSOR
    bsx1, bsy1, bsx2, bsy2 = SYN_BEAK_SLASH
    ccx1, ccy1, ccx2, ccy2 = SYN_CHEST_CENTER
    clx1, cly1, clx2, cly2 = SYN_CHEST_SLASH_L
    crx1, cry1, crx2, cry2 = SYN_CHEST_SLASH_R
    blx1, bly1, blx2, bly2 = SYN_BASELINE

    return f"""<g id="fcode-mascot-syn">
    <!-- Horn Crest / Ear Tufts -->
    <path id="syn-crest" d="{SYN_CROWN}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />
    <line id="syn-brow-divider" x1="{bx1}" y1="{by1}" x2="{bx2}" y2="{by2}" stroke="{grid_color}" stroke-width="6" stroke-linecap="square" />

    <!-- Brow Rule -->
    <line id="syn-brow" x1="{brx1}" y1="{bry1}" x2="{brx2}" y2="{bry2}" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" />

    <!-- Left Eye: Terminal Prompt [ > -->
    <path id="syn-eye-l-socket" d="{SYN_EYE_L_SOCKET}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />
    <path id="syn-eye-l-arrow" d="{SYN_EYE_L_ARROW}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />

    <!-- Right Eye: Active Block Cursor [ █ ] -->
    <path id="syn-eye-r-socket" d="{SYN_EYE_R_SOCKET}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />
    <rect id="syn-eye-r-cursor" x="{rx}" y="{ry}" width="{rw}" height="{rh}" fill="{cursor_color}" />

    <!-- Beak: Command Chevron and Slash -->
    <path id="syn-beak-chevron" d="{SYN_BEAK_CHEVRON}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />
    <line id="syn-beak-slash" x1="{bsx1}" y1="{bsy1}" x2="{bsx2}" y2="{bsy2}" stroke="{cursor_color}" stroke-width="10" stroke-linecap="square" />

    <!-- Outer Cheek Contours -->
    <path id="syn-cheek-l" d="{SYN_CHEEK_L}" fill="none" stroke="{grid_color}" stroke-width="8" stroke-linecap="square" stroke-linejoin="miter" />
    <path id="syn-cheek-r" d="{SYN_CHEEK_R}" fill="none" stroke="{grid_color}" stroke-width="8" stroke-linecap="square" stroke-linejoin="miter" />

    <!-- Bracket Wings -->
    <path id="syn-wing-l" d="{SYN_WING_L}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />
    <path id="syn-wing-r" d="{SYN_WING_R}" fill="none" stroke="{stroke_color}" stroke-width="12" stroke-linecap="square" stroke-linejoin="miter" />

    <!-- Chest Armor & Core Synthesis Matrix -->
    <path id="syn-chest-v" d="{SYN_CHEST_V}" fill="none" stroke="{grid_color}" stroke-width="8" stroke-linecap="square" stroke-linejoin="miter" />
    <line id="syn-chest-center" x1="{ccx1}" y1="{ccy1}" x2="{ccx2}" y2="{ccy2}" stroke="{grid_color}" stroke-width="8" stroke-linecap="square" />
    <line id="syn-chest-slash-l" x1="{clx1}" y1="{cly1}" x2="{clx2}" y2="{cly2}" stroke="{grid_color}" stroke-width="6" stroke-linecap="square" />
    <line id="syn-chest-slash-r" x1="{crx1}" y1="{cry1}" x2="{crx2}" y2="{cry2}" stroke="{grid_color}" stroke-width="6" stroke-linecap="square" />

    <!-- Talons / Perch Contacts -->
    <path id="syn-talon-l" d="{SYN_TALON_L}" fill="none" stroke="{stroke_color}" stroke-width="10" stroke-linecap="square" stroke-linejoin="miter" />
    <path id="syn-talon-r" d="{SYN_TALON_R}" fill="none" stroke="{stroke_color}" stroke-width="10" stroke-linecap="square" stroke-linejoin="miter" />

    <!-- Terminal Baseline Rule -->
    <line id="syn-baseline" x1="{blx1}" y1="{bly1}" x2="{blx2}" y2="{bly2}" stroke="{grid_color}" stroke-width="6" stroke-dasharray="12,8" stroke-linecap="square" />
  </g>"""


def build_mark_svg(mode="transparent"):
    """
    Generates 512x512 mark SVG.
    Transparency contract:
    - mode="transparent": NO background rect, bone white strokes.
    - mode="on-dark": opaque Void Black background rect + technical grid + crosshairs.
    - mode="on-light": opaque Bone White background rect + dark linework + grid.
    """
    if mode == "transparent":
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  {get_canonical_mark_svg_group(stroke_color=BONE_WHITE)}
</svg>"""

    stroke_col = BONE_WHITE if mode == "on-dark" else VOID_BLACK
    bg_col = VOID_BLACK if mode == "on-dark" else BONE_WHITE
    grid_col = GRID_MUTED if mode == "on-dark" else "#d0d0d4"
    cross_col = STEEL_GRAPHITE if mode == "on-dark" else "#8a8d92"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" fill="{bg_col}" />
  <g opacity="0.6">
    <line x1="76" y1="76" x2="436" y2="76" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="76" y1="436" x2="436" y2="436" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="76" y1="76" x2="76" y2="436" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="436" y1="76" x2="436" y2="436" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="76" y1="256" x2="436" y2="256" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="256" y1="76" x2="256" y2="436" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>
  <g stroke="{cross_col}" stroke-width="2" stroke-linecap="square">
    <line x1="256" y1="20" x2="256" y2="38" />
    <line x1="247" y1="29" x2="265" y2="29" />
    <line x1="256" y1="474" x2="256" y2="492" />
    <line x1="247" y1="483" x2="265" y2="483" />
    <line x1="20" y1="256" x2="38" y2="256" />
    <line x1="29" y1="247" x2="29" y2="265" />
    <line x1="474" y1="256" x2="492" y2="256" />
    <line x1="483" y1="247" x2="483" y2="265" />
  </g>
  {get_canonical_mark_svg_group(stroke_color=stroke_col)}
</svg>"""


def build_mascot_svg(mode="transparent"):
    """
    Generates 512x512 mascot SVG (syn: the synthesis sentinel).
    Transparency contract:
    - mode="transparent": NO background rect, bone white strokes.
    - mode="on-dark": opaque Void Black background rect + grid framing.
    - mode="on-light": opaque Bone White background rect + dark linework.
    """
    if mode == "transparent":
        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  {get_canonical_mascot_svg_group(stroke_color=BONE_WHITE, cursor_color=SIGNAL_CRIMSON, grid_color=STEEL_GRAPHITE)}
</svg>"""

    stroke_col = BONE_WHITE if mode == "on-dark" else VOID_BLACK
    bg_col = VOID_BLACK if mode == "on-dark" else BONE_WHITE
    grid_col = GRID_MUTED if mode == "on-dark" else "#d0d0d4"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <rect width="512" height="512" fill="{bg_col}" />
  <g opacity="0.4">
    <line x1="64" y1="64" x2="448" y2="64" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="64" y1="448" x2="448" y2="448" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="64" y1="64" x2="64" y2="448" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="448" y1="64" x2="448" y2="448" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>
  {get_canonical_mascot_svg_group(stroke_color=stroke_col, cursor_color=SIGNAL_CRIMSON, grid_color=STEEL_GRAPHITE if mode == 'on-dark' else '#8a8d92')}
</svg>"""


def build_wordmark_svg(mode="transparent", animated=False):
    """
    Generates 800x400 wordmark lockup SVG with master mark + frozen TrueType outlines.
    Transparency contract:
    - mode="transparent": NO background rect, bone white strokes.
    - mode="on-dark": opaque Void Black background rect + grid + crosshairs.
    - mode="on-light": opaque Bone White background rect + dark linework + grid.
    """
    text_col = BONE_WHITE if mode in ("transparent", "on-dark") else VOID_BLACK
    grid_col = GRID_MUTED if mode == "on-dark" else "#d0d0d4"
    cross_col = STEEL_GRAPHITE if mode == "on-dark" else "#8a8d92"

    anim_elem = ""
    if animated:
        anim_elem = """
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.501;1" dur="1s" repeatCount="indefinite" />"""

    bg_markup = ""
    grid_markup = ""
    if mode != "transparent":
        bg_col = VOID_BLACK if mode == "on-dark" else BONE_WHITE
        bg_markup = f'<rect width="800" height="400" fill="{bg_col}" />'
        grid_markup = f"""  <g opacity="0.5">
    <line x1="60" y1="60" x2="740" y2="60" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="60" y1="340" x2="740" y2="340" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="60" y1="60" x2="60" y2="340" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
    <line x1="740" y1="60" x2="740" y2="340" stroke="{grid_col}" stroke-width="1.5" stroke-dasharray="4,4" />
  </g>
  <g stroke="{cross_col}" stroke-width="2" stroke-linecap="square">
    <line x1="400" y1="16" x2="400" y2="32" />
    <line x1="392" y1="24" x2="408" y2="24" />
    <line x1="400" y1="368" x2="400" y2="384" />
    <line x1="392" y1="376" x2="408" y2="376" />
    <line x1="16" y1="200" x2="32" y2="200" />
    <line x1="24" y1="192" x2="24" y2="208" />
    <line x1="768" y1="200" x2="784" y2="200" />
    <line x1="776" y1="192" x2="776" y2="208" />
  </g>"""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" width="800" height="400">
  {bg_markup}
{grid_markup}
  <g transform="translate(210, 200) scale(0.68) translate(-256, -256)">
    {get_canonical_mark_svg_group(stroke_color=text_col)}
  </g>
  <path d="{WORDMARK_PATH_800X400}" fill="{text_col}" />
  <rect x="{WORDMARK_CURSOR_X_800X400}" y="155.0" width="26" height="73.0" fill="{SIGNAL_CRIMSON}">{anim_elem}
  </rect>
</svg>"""


def build_social_preview_svg():
    """Generates 1280x640 GitHub social preview SVG."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 640" width="1280" height="640">
  <rect width="1280" height="640" fill="{VOID_BLACK}" />
  <g stroke="#181a20" stroke-width="1.5">
    <line x1="160" y1="120" x2="1120" y2="120" />
    <line x1="160" y1="220" x2="1120" y2="220" />
    <line x1="160" y1="320" x2="1120" y2="320" />
    <line x1="160" y1="420" x2="1120" y2="420" />
    <line x1="160" y1="520" x2="1120" y2="520" />
    <line x1="160" y1="120" x2="160" y2="520" />
    <line x1="320" y1="120" x2="320" y2="520" />
    <line x1="480" y1="120" x2="480" y2="520" />
    <line x1="640" y1="120" x2="640" y2="520" />
    <line x1="800" y1="120" x2="800" y2="520" />
    <line x1="960" y1="120" x2="960" y2="520" />
    <line x1="1120" y1="120" x2="1120" y2="520" />
  </g>
  <g stroke="{STEEL_GRAPHITE}" stroke-width="2" stroke-linecap="square">
    <line x1="640" y1="20" x2="640" y2="44" />
    <line x1="628" y1="32" x2="652" y2="32" />
    <line x1="640" y1="596" x2="640" y2="620" />
    <line x1="628" y1="608" x2="652" y2="608" />
    <line x1="20" y1="320" x2="44" y2="320" />
    <line x1="32" y1="308" x2="32" y2="332" />
    <line x1="1236" y1="320" x2="1260" y2="320" />
    <line x1="1248" y1="308" x2="1248" y2="332" />
    <circle cx="36" cy="36" r="10" fill="none" stroke="{STEEL_GRAPHITE}" stroke-width="1.5" />
    <line x1="36" y1="22" x2="36" y2="50" stroke-width="1.5" />
    <line x1="22" y1="36" x2="50" y2="36" stroke-width="1.5" />
    <circle cx="1244" cy="36" r="10" fill="none" stroke="{STEEL_GRAPHITE}" stroke-width="1.5" />
    <line x1="1244" y1="22" x2="1244" y2="50" stroke-width="1.5" />
    <line x1="1230" y1="36" x2="1258" y2="36" stroke-width="1.5" />
    <circle cx="36" cy="604" r="10" fill="none" stroke="{STEEL_GRAPHITE}" stroke-width="1.5" />
    <line x1="36" y1="590" x2="36" y2="618" stroke-width="1.5" />
    <line x1="22" y1="604" x2="50" y2="604" stroke-width="1.5" />
    <circle cx="1244" cy="604" r="10" fill="none" stroke="{STEEL_GRAPHITE}" stroke-width="1.5" />
    <line x1="1244" y1="590" x2="1244" y2="618" stroke-width="1.5" />
    <line x1="1230" y1="604" x2="1258" y2="604" stroke-width="1.5" />
  </g>
  <g transform="translate(360, 320) scale(0.9) translate(-256, -256)">
    {get_canonical_mark_svg_group(stroke_color=BONE_WHITE)}
  </g>
  <path d="{WORDMARK_PATH_1280X640}" fill="{BONE_WHITE}" />
  <rect x="{WORDMARK_CURSOR_X_1280X640}" y="264.0" width="34" height="96.0" fill="{SIGNAL_CRIMSON}" />
</svg>"""


def build_avatar_svg(mask="square"):
    """
    Generates 1024x1024 mark avatar SVG.
    CRITICAL INVARIANT: Square and circle avatars MUST have IDENTICAL mark placement and scale!
    In circle avatar, outside the circle is transparent, inside circle is Void Black.
    """
    scale = 1.35
    clip_def = ""
    container = f'<rect width="1024" height="1024" fill="{VOID_BLACK}" />'
    clip_attr = ""
    if mask == "circle":
        clip_def = """<defs>
    <clipPath id="avatar-circle-clip">
      <circle cx="512" cy="512" r="512" />
    </clipPath>
  </defs>"""
        container = f'<circle cx="512" cy="512" r="512" fill="{VOID_BLACK}" />'
        clip_attr = ' clip-path="url(#avatar-circle-clip)"'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
  {clip_def}
  {container}
  <g transform="translate(512, 512) scale({scale}) translate(-256, -256)"{clip_attr}>
    {get_canonical_mark_svg_group(stroke_color=BONE_WHITE)}
  </g>
</svg>"""


def build_mascot_avatar_svg():
    """Generates 1024x1024 mascot profile avatar with circular mask on transparent canvas."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">
  <defs>
    <clipPath id="mascot-circle-clip">
      <circle cx="512" cy="512" r="512" />
    </clipPath>
  </defs>
  <circle cx="512" cy="512" r="512" fill="{VOID_BLACK}" />
  <g transform="translate(512, 512) scale(1.4) translate(-256, -256)" clip-path="url(#mascot-circle-clip)">
    {get_canonical_mascot_svg_group(stroke_color=BONE_WHITE, cursor_color=SIGNAL_CRIMSON, grid_color=STEEL_GRAPHITE)}
  </g>
</svg>"""


def render_png(src_svg, dst_png, bg="none", resize=None):
    """Renders PNG using ImageMagick PNG32 with -strip for strict 8-bit RGBA channels and determinism."""
    cmd = ["convert"]
    if bg:
        cmd.extend(["-background", bg])
    cmd.append(src_svg)
    if resize:
        cmd.extend(["-resize", resize])
    cmd.extend(["-strip", f"PNG32:{dst_png}"])
    subprocess.run(cmd, check=True)


def main():
    print("Generating fcode canonical brand assets...")
    os.makedirs(BRAND_DIR, exist_ok=True)

    # ==================== 1. MASTER & TRANSPARENT MARK ====================
    mark_master_svg = build_mark_svg(mode="transparent")
    mark_master_path = os.path.join(BRAND_DIR, "fcode-mark-master.svg")
    with open(mark_master_path, "w") as f:
        f.write(mark_master_svg)

    mark_trans_path = os.path.join(BRAND_DIR, "fcode-mark-transparent.svg")
    with open(mark_trans_path, "w") as f:
        f.write(mark_master_svg)

    mark_default_path = os.path.join(BRAND_DIR, "fcode-mark.svg")
    with open(mark_default_path, "w") as f:
        f.write(mark_master_svg)

    # Opaque Mark Variants
    mark_dark_path = os.path.join(BRAND_DIR, "fcode-mark-on-dark.svg")
    with open(mark_dark_path, "w") as f:
        f.write(build_mark_svg(mode="on-dark"))

    mark_light_path = os.path.join(BRAND_DIR, "fcode-mark-on-light.svg")
    with open(mark_light_path, "w") as f:
        f.write(build_mark_svg(mode="on-light"))

    # Legacy light alias
    shutil.copyfile(mark_light_path, os.path.join(BRAND_DIR, "fcode-mark-light.svg"))

    # ==================== 2. MASTER & TRANSPARENT WORDMARK ====================
    wordmark_master_svg = build_wordmark_svg(mode="transparent")
    wordmark_master_path = os.path.join(BRAND_DIR, "fcode-wordmark-master.svg")
    with open(wordmark_master_path, "w") as f:
        f.write(wordmark_master_svg)

    wordmark_trans_path = os.path.join(BRAND_DIR, "fcode-wordmark-transparent.svg")
    with open(wordmark_trans_path, "w") as f:
        f.write(wordmark_master_svg)

    wordmark_default_path = os.path.join(BRAND_DIR, "fcode-wordmark.svg")
    with open(wordmark_default_path, "w") as f:
        f.write(wordmark_master_svg)

    # Opaque Wordmark Variants
    wordmark_dark_path = os.path.join(BRAND_DIR, "fcode-wordmark-on-dark.svg")
    with open(wordmark_dark_path, "w") as f:
        f.write(build_wordmark_svg(mode="on-dark"))

    wordmark_light_path = os.path.join(BRAND_DIR, "fcode-wordmark-on-light.svg")
    with open(wordmark_light_path, "w") as f:
        f.write(build_wordmark_svg(mode="on-light"))

    # Legacy light alias
    shutil.copyfile(wordmark_light_path, os.path.join(BRAND_DIR, "fcode-wordmark-light.svg"))

    # ==================== 3. MASTER & TRANSPARENT MASCOT (syn) ====================
    mascot_master_svg = build_mascot_svg(mode="transparent")
    mascot_master_path = os.path.join(BRAND_DIR, "fcode-mascot-master.svg")
    with open(mascot_master_path, "w") as f:
        f.write(mascot_master_svg)

    mascot_trans_path = os.path.join(BRAND_DIR, "fcode-mascot-transparent.svg")
    with open(mascot_trans_path, "w") as f:
        f.write(mascot_master_svg)

    mascot_default_path = os.path.join(BRAND_DIR, "fcode-mascot.svg")
    with open(mascot_default_path, "w") as f:
        f.write(mascot_master_svg)

    # Opaque Mascot Variants
    mascot_dark_path = os.path.join(BRAND_DIR, "fcode-mascot-on-dark.svg")
    with open(mascot_dark_path, "w") as f:
        f.write(build_mascot_svg(mode="on-dark"))

    mascot_light_path = os.path.join(BRAND_DIR, "fcode-mascot-on-light.svg")
    with open(mascot_light_path, "w") as f:
        f.write(build_mascot_svg(mode="on-light"))

    # ==================== 4. SOCIAL PREVIEW & MOTION SVG ====================
    social_svg_path = os.path.join(BRAND_DIR, "fcode-social-preview-1280x640.svg")
    with open(social_svg_path, "w") as f:
        f.write(build_social_preview_svg())

    motion_svg_path = os.path.join(BRAND_DIR, "fcode-motion-pulse.svg")
    with open(motion_svg_path, "w") as f:
        f.write(build_wordmark_svg(mode="on-dark", animated=True))

    # ==================== 5. RASTER RENDERING (PNG & JPG) ====================
    print("Rendering raster assets with ImageMagick PNG32 and -strip...")

    # Transparent Mark PNGs
    render_png(mark_trans_path, os.path.join(BRAND_DIR, "fcode-mark-transparent.png"), bg="none")
    render_png(mark_trans_path, os.path.join(BRAND_DIR, "fcode-mark.png"), bg="none")

    # Opaque Mark PNGs
    render_png(mark_dark_path, os.path.join(BRAND_DIR, "fcode-mark-on-dark.png"), bg=VOID_BLACK)
    render_png(mark_light_path, os.path.join(BRAND_DIR, "fcode-mark-on-light.png"), bg=BONE_WHITE)
    # Legacy aliases
    shutil.copyfile(os.path.join(BRAND_DIR, "fcode-mark-on-dark.png"), os.path.join(BRAND_DIR, "fcode-mark-dark.png"))
    shutil.copyfile(os.path.join(BRAND_DIR, "fcode-mark-on-light.png"), os.path.join(BRAND_DIR, "fcode-mark-light.png"))

    # Transparent Wordmark PNGs
    render_png(wordmark_trans_path, os.path.join(BRAND_DIR, "fcode-wordmark-transparent.png"), bg="none")
    render_png(wordmark_trans_path, os.path.join(BRAND_DIR, "fcode-wordmark.png"), bg="none")

    # Opaque Wordmark PNGs
    render_png(wordmark_dark_path, os.path.join(BRAND_DIR, "fcode-wordmark-on-dark.png"), bg=VOID_BLACK)
    render_png(wordmark_light_path, os.path.join(BRAND_DIR, "fcode-wordmark-on-light.png"), bg=BONE_WHITE)
    # Legacy aliases
    shutil.copyfile(os.path.join(BRAND_DIR, "fcode-wordmark-on-dark.png"), os.path.join(BRAND_DIR, "fcode-wordmark-dark.png"))
    shutil.copyfile(os.path.join(BRAND_DIR, "fcode-wordmark-on-light.png"), os.path.join(BRAND_DIR, "fcode-wordmark-light.png"))

    # Transparent Mascot PNGs
    render_png(mascot_trans_path, os.path.join(BRAND_DIR, "fcode-mascot-transparent.png"), bg="none")
    render_png(mascot_trans_path, os.path.join(BRAND_DIR, "fcode-mascot.png"), bg="none")

    # Opaque Mascot PNGs
    render_png(mascot_dark_path, os.path.join(BRAND_DIR, "fcode-mascot-on-dark.png"), bg=VOID_BLACK)
    render_png(mascot_light_path, os.path.join(BRAND_DIR, "fcode-mascot-on-light.png"), bg=BONE_WHITE)

    # Mascot Profile Avatar (1024x1024, circular mask on transparent canvas)
    with tempfile.NamedTemporaryFile("w", suffix=".svg") as tmp_ma:
        tmp_ma.write(build_mascot_avatar_svg())
        tmp_ma.flush()
        render_png(tmp_ma.name, os.path.join(BRAND_DIR, "fcode-mascot-avatar.png"), bg="none")

    # Mark Avatars (1024x1024)
    with tempfile.NamedTemporaryFile("w", suffix=".svg") as tmp_sq:
        tmp_sq.write(build_avatar_svg(mask="square"))
        tmp_sq.flush()
        render_png(tmp_sq.name, os.path.join(BRAND_DIR, "fcode-avatar-square.png"), bg=VOID_BLACK)

    with tempfile.NamedTemporaryFile("w", suffix=".svg") as tmp_cr:
        tmp_cr.write(build_avatar_svg(mask="circle"))
        tmp_cr.flush()
        render_png(tmp_cr.name, os.path.join(BRAND_DIR, "fcode-avatar-circle.png"), bg="none")

    # Social Preview (1280x640)
    render_png(social_svg_path, os.path.join(BRAND_DIR, "fcode-social-preview-1280x640.png"), bg=VOID_BLACK)
    subprocess.run(
        ["convert", social_svg_path, "-strip", "-quality", "95", os.path.join(BRAND_DIR, "fcode-social-preview-1280x640.jpg")],
        check=True,
    )

    # Favicons & Touch Icons (Preserving transparency around glyph)
    icon_master_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <g transform="translate(256, 256) scale(0.9) translate(-256, -256)">
    {get_canonical_mark_svg_group(stroke_color=BONE_WHITE)}
  </g>
</svg>"""

    with tempfile.NamedTemporaryFile("w", suffix=".svg") as tmp_ic:
        tmp_ic.write(icon_master_svg)
        tmp_ic.flush()
        # Apple touch icon (180x180, square on void black)
        render_png(tmp_ic.name, os.path.join(BRAND_DIR, "apple-touch-icon.png"), bg=VOID_BLACK, resize="180x180")
        # Favicon 32x32 (transparent background)
        p32 = os.path.join(BRAND_DIR, "favicon-32x32.png")
        render_png(tmp_ic.name, p32, bg="none", resize="32x32")
        # Favicon 16x16 (transparent background)
        p16 = os.path.join(BRAND_DIR, "favicon-16x16.png")
        render_png(tmp_ic.name, p16, bg="none", resize="16x16")
        # Multi-size favicon.ico
        subprocess.run(
            ["convert", p16, p32, "-strip", "-colors", "256", os.path.join(BRAND_DIR, "favicon.ico")],
            check=True,
        )

    # Animated Motion GIF (Terminal cursor pulse: 500ms on, 500ms off)
    f1_svg = build_wordmark_svg(mode="on-dark", animated=False)
    f2_svg = f1_svg.replace(
        f'<rect x="{WORDMARK_CURSOR_X_800X400}" y="155.0" width="26" height="73.0" fill="{SIGNAL_CRIMSON}">',
        f'<rect x="{WORDMARK_CURSOR_X_800X400}" y="155.0" width="26" height="73.0" fill="{SIGNAL_CRIMSON}" opacity="0">'
    )
    with tempfile.NamedTemporaryFile("w", suffix=".svg") as t1, tempfile.NamedTemporaryFile("w", suffix=".svg") as t2:
        t1.write(f1_svg); t1.flush()
        t2.write(f2_svg); t2.flush()
        with tempfile.NamedTemporaryFile("w", suffix=".png") as p1, tempfile.NamedTemporaryFile("w", suffix=".png") as p2:
            subprocess.run(["convert", t1.name, p1.name], check=True)
            subprocess.run(["convert", t2.name, p2.name], check=True)
            subprocess.run(
                ["convert", "-delay", "50", "-loop", "0", p1.name, p2.name, "-strip", os.path.join(BRAND_DIR, "fcode-motion-pulse.gif")],
                check=True,
            )

    print("All brand assets successfully generated with verified transparency contract!")


if __name__ == "__main__":
    main()
