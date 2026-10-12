# fcode Visual Identity and Design System Specification

```
|=-----------------------------------------------------------------------------------=|
|  SPEC: VISUAL-FOUNDATION-V1.3  |  STATUS: CANONICAL  |  AUTH: fcode CORE           |
|=-----------------------------------------------------------------------------------=|
```

---

## 1. Aesthetic Direction and Principles

`fcode` is designed for developers who care about technical depth, command-line ergonomics, and direct machine agency. Modern developer tooling often surrounds simple tasks with bloated web wrappers, noisy interfaces, and speculative animations. `fcode` takes the opposite approach.

The visual system is built on five core principles:

1. **Monospace Purity:** Structural character framing, aligned columns, and fixed-width typography over decorative embellishment.
2. **Radical Reduction:** Removing unnecessary lines and visual noise as true progress. Every pixel and glyph serves an explicit communicative purpose.
3. **Native Fidelity:** Treating typography, contrast, and layout as precision engineering rather than marketing decoration.
4. **Industrial Precision:** Mathematical grid logic, engineering calipers, coordinate registration marks, and disciplined negative space.
5. **High-Contrast Chiaroscuro:** Deep void black backgrounds paired with crisp bone white linework and a single signal crimson accent.

### Boundaries
* No generic AI gradients: No pastel purple or cyan fades, glossy spheres, or soft squircle cards.
* No cyberpunk clichés: No simulated matrix rain, skull illustrations, or fake hacker clutter.
* No speculative hardware claims: The design reflects an autonomous software development harness, not a fictional compiler.

---

## 2. Color System

A strict five-token palette with high contrast and zero chromatic noise.

```
+-------------------+-------------------+-------------------+-------------------+-------------------+
|    VOID BLACK     |  CARBON CHARCOAL  |    STEEL GRAY     |    BONE WHITE     |  SIGNAL CRIMSON   |
|      #08080A      |      #121316      |      #4A4D52      |      #F0F0F2      |      #FF3B30      |
|  [Canvas Base]    | [Surface Panels]  | [Grid / Caliper]  |  [Type / Vector]  |  [Cursor Accent]  |
+-------------------+-------------------+-------------------+-------------------+-------------------+
```

### Color Tokens
| Name | Hex | Semantic Role | Contrast (vs Void Black) |
| :--- | :--- | :--- | :--- |
| **Void Black** | `#08080A` | Primary canvas, terminal background, negative space | Base (1:1) |
| **Carbon Charcoal** | `#121316` | Elevated cards, hardware surfaces, modal backgrounds | 1.2:1 |
| **Steel Graphite** | `#4A4D52` | Coordinate axes, dimension ticks, structural dividers | 4.8:1 (AA Large) |
| **Bone White** | `#F0F0F2` | Primary headlines, monospaced vector linework, readouts | 18.2:1 (AAA) |
| **Signal Crimson** | `#FF3B30` | Defiant block cursor (`█`), reduction cuts, alert states | 6.4:1 (AAA) |

---

## 3. Typography System

The typography is engineered for legibility, fixed-grid alignment, and technical authority.

### Monospace (Primary Engine)
* **Recommended Typefaces:** Berkeley Mono, JetBrains Mono, IBM Plex Mono, or Cascadia Code.
* **System Fallback Stack:** `ui-monospace, SFMono-Regular, "Roboto Mono", Menlo, Monaco, Consolas, monospace`.
* **Characteristics:** Slashed zero (`0`), sharp brackets (`[`, `]`), angular serifs on `f` and `l`.

### Display and Section Framing
* **Recommended Typefaces:** High-contrast grotesque sans-serif in uppercase (Inter, Helvetica Neue, Chivo Mono).
* **Letterspacing:** `+0.12em` to `+0.2em` wide tracking for section tags and coordinate headers.
* **Usage:** Status readouts, coordinates, and phase indicators (for example: `[STATUS: PRE-CODE]`).

---

## 4. Canonical Mark Geometry

The primary emblem combines five distinct geometric components into a single vector mark:
1. **The Left Bracket (`[`):** Command-line boundary framing the entry.
2. **The Prompt Arrow (`>`):** Directional prompt symbol indicating ready input.
3. **The Angular `f`:** Stylized asymmetric glyph with razor-sharp diagonal cuts.
4. **The Command Slash (`/`):** Trailing prompt separator.
5. **The Signal Crimson Cursor (`█`):** Solid block cursor representing active intent.

```
       [_.                                       ._]
       +-------------------------------------------+
       |   +--+                                    |
       |   |  |   /======================\         |
       |   | >|  /   /-------------------/         |
       |   |  | /   /                              |
       |   +--+ |  +-------------\    +----+       |
       |        |  |  +----------/    |    |  (CURSOR)
       |        |  |  |               |    |       |
       |        |  |  \---------\     +----+       |
       |        \  \------------/       /          |
       |         \_____________________/           |
       +-------------------------------------------+
       [_.                                       ._]
```

### Mathematical Source of Truth
All mark instances derive from [`assets/brand/fcode-mark-master.svg`](assets/brand/fcode-mark-master.svg) defined in a 512x512 coordinate space:

* **Bracket:** `M 172 168 L 132 168 L 132 344 L 172 344` (stroke-width 14, square cap)
* **Prompt Arrow:** `M 148 238 L 168 256 L 148 274` (stroke-width 14, square cap)
* **Angular f:** `M 216 384 L 194 384 L 194 172 L 236 128 L 336 128 L 302 168 L 238 168 L 238 214 L 306 214 L 284 254 L 238 254 L 238 348 Z` (stroke-width 14)
* **Slash:** Line from `(256, 364)` to `(280, 304)` (stroke-width 14)
* **Crimson Cursor:** Rectangle at `x="330" y="214" width="46" height="66" fill="#ff3b30"`

### Deterministic Wordmark Outlines
Brand-critical typography in [`assets/brand/fcode-wordmark-master.svg`](assets/brand/fcode-wordmark-master.svg) is frozen into vector path outlines. It does not depend on system fonts. Every variant derives from this master file via uniform scaling and translation.

---

## 5. Canonical Mascot: syn (The Synthesis Sentinel)

Developer tools earn cultural resonance when they possess an authentic, memorable companion. `syn` is an original sentinel owl constructed entirely from terminal character geometry and command-line syntax.

```
                  /\        /\
                 /  \______/  \
                |   [ >  [ █ ] |
                |      \/      |
                [  \  |  /  ]
                ======---======
```

### Anatomical Grammar
* **Ear Tufts / Crown Crest:** Angular horn paths cut from terminal caret points (`M 148 112 L 172 44 L 214 96 L 256 86 L 298 96 L 340 44 L 364 112`).
* **Left Eye:** Prompt input bracket `[ >` (`M 196 168 L 164 168 L 164 248 L 196 248` with prompt chevron `M 184 194 L 210 208 L 184 222`). Represents active intent ingestion.
* **Right Eye:** Active execution socket `[ █ ]` holding a solid signal crimson block cursor at `(286, 190)` with dimensions `34x44`. Represents prompt synthesis and AST compilation.
* **Beak:** Command chevron `M 236 248 L 256 284 L 276 248` bisected by a crimson prompt slash line from `(256, 284)` to `(246, 324)`.
* **Wings:** Rigid terminal boundary brackets `[` and `]` on left (`M 140 316 L 100 316 L 100 428 L 152 428`) and right (`M 372 316 L 412 316 L 412 428 L 360 428`).
* **Chest Shield:** Synthesizer matrix chevron `M 208 344 L 256 384 L 304 344` with structural dividers.
* **Perch:** Dashed monospaced terminal baseline rule from `(64, 472)` to `(448, 472)`.

### Operational Role
In the runtime architecture, `syn` serves as the visible agent state indicator:
* **Idle / Listening:** Block cursor eye pulses at 1.0 Hz cadence.
* **Synthesizing:** Beak slash and cursor eye illuminate during AST resolution.
* **Swarm Execution:** Wings frame active worktree status indicators.
* **Verification Pass:** Signal crimson switches to verification green before completion.

---

## 6. The Transparency Contract

To eliminate asset friction across dark mode, light mode, website documentation, and social embeds, `fcode` enforces a strict, programmatic Transparency Contract:

### Rules of Canvas Transparency
1. **Reusable Transparent Exports:** Standalone marks, wordmarks, and mascot assets (`*-transparent.svg`, `*-transparent.png`, `fcode-mark.svg`, `fcode-wordmark.svg`, `fcode-mascot.svg`) MUST have genuinely transparent canvases.
2. **Zero SVG Background Rects:** Transparent SVGs must contain no full-canvas background rect elements.
3. **Corner Alpha Invariant:** Transparent PNG exports must have `alpha = 0` across all four corner pixels and maintain over 20% transparent area.
4. **Opaque Ground Variants:** Variants tagged `*-on-dark` or `*-on-light` must contain explicit, solid background rects (`#08080A` or `#F0F0F2`).
5. **Circular Avatars:** Avatars with circular badges preserve transparent corner bounds outside the circular mask for seamless integration into host platforms.
6. **Filename Semantics:** Every asset filename must communicate its background contract unambiguously.

---

## 7. Asset Generation and Verification Tooling

Brand integrity is guaranteed by automated code rather than manual export pipelines:

* **Generator Script:** [`scripts/generate_brand.py`](scripts/generate_brand.py) generates all derivative SVGs, PNGs, avatars, favicons, and motion assets directly from master vector geometry.
* **Verification Suite:** [`scripts/verify_brand.py`](scripts/verify_brand.py) tests all seven core invariants:
  1. **Canonical Mark Geometry:** Exact coordinate matches for all 5 mark elements.
  2. **Canonical Mascot Geometry:** Exact coordinate matches for `syn` anatomical components.
  3. **Uniform Transforms:** Prohibits non-uniform aspect scaling.
  4. **Zero `<text>` Tags:** Guarantees frozen vector outlines across all SVGs.
  5. **Avatar Placement Parity:** Exact coordinate and scale match between square and circular avatars.
  6. **Dimension and Format Integrity:** Pixel-perfect dimensions and valid XML.
  7. **Transparency and Alpha Contract:** Automated corner alpha checks, transparent area ratio verification, and background rect validation.

---

## 8. Usage Rules, Clear Space, and Motion Language

### Clear Space
The minimum clear space surrounding the mark must equal at least half the width of the prompt bracket on all sides. No text, decorative borders, or third-party marks may intrude into this zone.

### Avatars
* **Square Mark Profile (GitHub organizations, Slack):** [`assets/brand/fcode-avatar-square.png`](assets/brand/fcode-avatar-square.png) (1024x1024).
* **Circular Mark Profile (Discord, X):** [`assets/brand/fcode-avatar-circle.png`](assets/brand/fcode-avatar-circle.png) (1024x1024).
* **Mascot Avatar Profile:** [`assets/brand/fcode-mascot-avatar.png`](assets/brand/fcode-mascot-avatar.png) (1024x1024).

### Motion Cadence
Terminal motion is strictly digital with zero spring physics or interpolation blur:
* **Cadence:** Exactly 1.0 Hz (1000ms loop).
* **Duty Cycle:** 500ms cursor visible (`#FF3B30`), 500ms cursor hidden.
* **Easing:** `step-end` instantaneous transition.
* **Reference Asset:** [`assets/brand/fcode-motion-pulse.gif`](assets/brand/fcode-motion-pulse.gif) and [`assets/brand/fcode-motion-pulse.svg`](assets/brand/fcode-motion-pulse.svg).

---

## 9. Inventory of Brand Assets

All official brand assets reside in [`assets/brand/`](assets/brand/):

### Master Definitions
* [`fcode-mark-master.svg`](assets/brand/fcode-mark-master.svg): Canonical master vector mark on transparent canvas (512x512).
* [`fcode-wordmark-master.svg`](assets/brand/fcode-wordmark-master.svg): Canonical master wordmark lockup on transparent canvas (800x400).
* [`fcode-mascot-master.svg`](assets/brand/fcode-mascot-master.svg): Canonical master mascot vector (`syn`) on transparent canvas (512x512).

### Transparent Exports
* [`fcode-mark.svg`](assets/brand/fcode-mark.svg), [`fcode-mark-transparent.svg`](assets/brand/fcode-mark-transparent.svg): Mark vector on transparent canvas.
* [`fcode-mark.png`](assets/brand/fcode-mark.png), [`fcode-mark-transparent.png`](assets/brand/fcode-mark-transparent.png): 512x512 mark raster on transparent canvas.
* [`fcode-wordmark.svg`](assets/brand/fcode-wordmark.svg), [`fcode-wordmark-transparent.svg`](assets/brand/fcode-wordmark-transparent.svg): Wordmark vector on transparent canvas.
* [`fcode-wordmark.png`](assets/brand/fcode-wordmark.png), [`fcode-wordmark-transparent.png`](assets/brand/fcode-wordmark-transparent.png): 800x400 wordmark raster on transparent canvas.
* [`fcode-mascot.svg`](assets/brand/fcode-mascot.svg), [`fcode-mascot-transparent.svg`](assets/brand/fcode-mascot-transparent.svg): Mascot vector on transparent canvas.
* [`fcode-mascot.png`](assets/brand/fcode-mascot.png), [`fcode-mascot-transparent.png`](assets/brand/fcode-mascot-transparent.png): 512x512 mascot raster on transparent canvas.
* [`favicon-32x32.png`](assets/brand/favicon-32x32.png), [`favicon-16x16.png`](assets/brand/favicon-16x16.png): Web favicons with transparent backgrounds.

### Opaque Ground Exports
* [`fcode-mark-on-dark.svg`](assets/brand/fcode-mark-on-dark.svg), [`fcode-mark-on-dark.png`](assets/brand/fcode-mark-on-dark.png): 512x512 mark on Void Black with engineering grid framing.
* [`fcode-mark-on-light.svg`](assets/brand/fcode-mark-on-light.svg), [`fcode-mark-on-light.png`](assets/brand/fcode-mark-on-light.png): 512x512 mark on Bone White for light paper and documentation.
* [`fcode-wordmark-on-dark.svg`](assets/brand/fcode-wordmark-on-dark.svg), [`fcode-wordmark-on-dark.png`](assets/brand/fcode-wordmark-on-dark.png): 800x400 wordmark on Void Black.
* [`fcode-wordmark-on-light.svg`](assets/brand/fcode-wordmark-on-light.svg), [`fcode-wordmark-on-light.png`](assets/brand/fcode-wordmark-on-light.png): 800x400 wordmark on Bone White.
* [`fcode-mascot-on-dark.svg`](assets/brand/fcode-mascot-on-dark.svg), [`fcode-mascot-on-dark.png`](assets/brand/fcode-mascot-on-dark.png): 512x512 mascot on Void Black.
* [`fcode-mascot-on-light.svg`](assets/brand/fcode-mascot-on-light.svg), [`fcode-mascot-on-light.png`](assets/brand/fcode-mascot-on-light.png): 512x512 mascot on Bone White.
* [`fcode-social-preview-1280x640.png`](assets/brand/fcode-social-preview-1280x640.png), [`fcode-social-preview-1280x640.jpg`](assets/brand/fcode-social-preview-1280x640.jpg): 1280x640 GitHub social preview.
* [`apple-touch-icon.png`](assets/brand/apple-touch-icon.png): 180x180 solid iOS/macOS web clip icon.

### Profile Avatars and Animation
* [`fcode-avatar-square.png`](assets/brand/fcode-avatar-square.png): 1024x1024 square mark avatar.
* [`fcode-avatar-circle.png`](assets/brand/fcode-avatar-circle.png): 1024x1024 circular mark badge on transparent canvas.
* [`fcode-mascot-avatar.png`](assets/brand/fcode-mascot-avatar.png): 1024x1024 circular mascot badge on transparent canvas.
* [`fcode-motion-pulse.gif`](assets/brand/fcode-motion-pulse.gif): 1.0s loop terminal cursor animation.
* [`fcode-motion-pulse.svg`](assets/brand/fcode-motion-pulse.svg): Pure vector animated SVG with CSS keyframe pulse.
* [`favicon.ico`](assets/brand/favicon.ico): Multi-resolution container icon.

### Atmospheric and Concept Visuals ([`assets/atmospheric/`](assets/atmospheric/))
* [`fcode-hero-workspace.jpg`](assets/atmospheric/fcode-hero-workspace.jpg): 1920x1080 terminal UI product concept preview illustrating intent synthesis, swarm orchestration, worktree code diff, and automated test convergence.
* [`fcode-architecture-harness.jpg`](assets/atmospheric/fcode-architecture-harness.jpg): 16:9 systems engineering diagram illustrating the prompt-synthesized harness pipeline.
