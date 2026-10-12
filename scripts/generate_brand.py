#!/usr/bin/env python3
"""
scripts/generate_brand.py

Canonical Brand Asset Generator for fcode.
All assets are deterministically derived from:
1. Canonical mark vector geometry (bracket, arrow, angular f, slash, crimson cursor)
2. Canonical mascot vector geometry (syn: the synthesis sentinel owl)
3. Frozen TrueType vector outlines for wordmark letters (f, c, o, d, e)

Transparency Contract:
- Reusable mark, wordmark, and mascot SVG/PNG exports have genuinely transparent canvases (no background rect, alpha=0 corners).
- *-on-dark / *-on-light, social previews, and intentionally backgrounded platform assets are opaque.
- Favicons preserve transparency around glyphs.
- Zero runtime font dependencies. Zero non-uniform distortions.
"""

import os
import shutil
import struct
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


def extract_wordmark_vector_paths(target_height=76.0, start_x=340.0, baseline_y=228.0):
    """
    Extract frozen vector outlines for letters 'f', 'c', 'o', 'd', 'e'
    directly from system TrueType font without external dependencies.
    """
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    with open(font_path, "rb") as f:
        data = f.read()

    num_tables = struct.unpack(">H", data[4:6])[0]
    tables = {
        data[12 + i * 16 : 16 + i * 16].decode("latin1"): struct.unpack(
            ">I", data[20 + i * 16 : 24 + i * 16]
        )[0]
        for i in range(num_tables)
    }
    head_off = tables["head"]
    index_to_loc_format = struct.unpack(
        ">h", data[head_off + 50 : head_off + 52]
    )[0]
    loca_off = tables["loca"]
    glyf_off = tables["glyf"]

    def get_glyph_offset(gid):
        if index_to_loc_format == 0:
            off1 = struct.unpack(">H", data[loca_off + gid * 2 : loca_off + (gid + 1) * 2])[0] * 2
            off2 = struct.unpack(">H", data[loca_off + (gid + 1) * 2 : loca_off + (gid + 2) * 2])[0] * 2
        else:
            off1 = struct.unpack(">I", data[loca_off + gid * 4 : loca_off + (gid + 1) * 4])[0]
            off2 = struct.unpack(">I", data[loca_off + (gid + 1) * 4 : loca_off + (gid + 2) * 4])[0]
        return glyf_off + off1, off2 - off1

    def parse_glyph(gid, x_offset):
        off, length = get_glyph_offset(gid)
        if length == 0:
            return ""
        num_contours = struct.unpack(">h", data[off : off + 2])[0]
        if num_contours <= 0:
            return ""
        end_pts = [
            struct.unpack(">H", data[off + 10 + i * 2 : off + 12 + i * 2])[0]
            for i in range(num_contours)
        ]
        ins_len = struct.unpack(
            ">H", data[off + 10 + num_contours * 2 : off + 12 + num_contours * 2]
        )[0]
        p = off + 12 + num_contours * 2 + ins_len
        num_points = end_pts[-1] + 1
        flags = []
        while len(flags) < num_points:
            flag = data[p]
            p += 1
            flags.append(flag)
            if flag & 8:
                repeat = data[p]
                p += 1
                flags.extend([flag] * repeat)
        x_coords = []
        cur_x = 0
        for flag in flags:
            if flag & 2:
                val = data[p]
                p += 1
                cur_x += val if (flag & 16) else -val
            elif not (flag & 16):
                cur_x += struct.unpack(">h", data[p : p + 2])[0]
                p += 2
            x_coords.append(cur_x)
        y_coords = []
        cur_y = 0
        for flag in flags:
            if flag & 4:
                val = data[p]
                p += 1
                cur_y += val if (flag & 32) else -val
            elif not (flag & 32):
                cur_y += struct.unpack(">h", data[p : p + 2])[0]
                p += 2
            y_coords.append(cur_y)

        scale = target_height / 1556.0
        path_d = []
        pt_idx = 0
        for end_pt in end_pts:
            pts = []
            while pt_idx <= end_pt:
                sx = round(x_offset + x_coords[pt_idx] * scale, 2)
                sy = round(baseline_y - y_coords[pt_idx] * scale, 2)
                pts.append((sx, sy, bool(flags[pt_idx] & 1)))
                pt_idx += 1
            if not pts:
                continue
            n = len(pts)
            start_i = 0
            if not pts[0][2]:
                if pts[-1][2]:
                    start_i = n - 1
                else:
                    mid_x = round((pts[0][0] + pts[-1][0]) / 2, 2)
                    mid_y = round((pts[0][1] + pts[-1][1]) / 2, 2)
                    pts = [(mid_x, mid_y, True)] + pts
                    n = len(pts)
            pts = pts[start_i:] + pts[:start_i]
            path_d.append(f"M {pts[0][0]} {pts[0][1]}")
            i = 1
            while i < n:
                curr = pts[i]
                if curr[2]:
                    path_d.append(f"L {curr[0]} {curr[1]}")
                    i += 1
                else:
                    nxt = pts[(i + 1) % n]
                    if nxt[2]:
                        path_d.append(f"Q {curr[0]} {curr[1]} {nxt[0]} {nxt[1]}")
                        i += 2
                    else:
                        mid_x = round((curr[0] + nxt[0]) / 2, 2)
                        mid_y = round((curr[1] + nxt[1]) / 2, 2)
                        path_d.append(f"Q {curr[0]} {curr[1]} {mid_x} {mid_y}")
                        i += 1
            path_d.append("Z")
        return " ".join(path_d)

    gids = [("f", 73), ("c", 70), ("o", 82), ("d", 71), ("e", 72)]
    adv = 1233.0 * (target_height / 1556.0)
    paths = [
        parse_glyph(gid, round(start_x + i * adv, 2))
        for i, (ch, gid) in enumerate(gids)
    ]
    cursor_x = round(start_x + len(gids) * adv + 10, 1)
    return " ".join(paths), cursor_x, adv


WORDMARK_PATH_800X400, WORDMARK_CURSOR_X_800X400, _ = extract_wordmark_vector_paths(
    target_height=76.0, start_x=340.0, baseline_y=228.0
)


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
    paths_1280, cursor_x_1280, _ = extract_wordmark_vector_paths(
        target_height=100.0, start_x=530.0, baseline_y=360.0
    )
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
  <path d="{paths_1280}" fill="{BONE_WHITE}" />
  <rect x="{cursor_x_1280}" y="264.0" width="34" height="96.0" fill="{SIGNAL_CRIMSON}" />
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
    """Renders PNG using ImageMagick PNG32 for strict 8-bit RGBA channels."""
    cmd = ["convert"]
    if bg:
        cmd.extend(["-background", bg])
    cmd.append(src_svg)
    if resize:
        cmd.extend(["-resize", resize])
    cmd.append(f"PNG32:{dst_png}")
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
    print("Rendering raster assets with ImageMagick PNG32...")

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
        ["convert", social_svg_path, "-quality", "95", os.path.join(BRAND_DIR, "fcode-social-preview-1280x640.jpg")],
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
            ["convert", p16, p32, "-colors", "256", os.path.join(BRAND_DIR, "favicon.ico")],
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
                ["convert", "-delay", "50", "-loop", "0", p1.name, p2.name, os.path.join(BRAND_DIR, "fcode-motion-pulse.gif")],
                check=True,
            )

    print("All brand assets successfully generated with verified transparency contract!")


if __name__ == "__main__":
    main()
