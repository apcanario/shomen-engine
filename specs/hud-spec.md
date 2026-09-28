# Shōmen — Glitch Post (Sci-Fi HUD System)

**Purpose:** Locked spec for Shōmen's dark sci-fi HUD posts — match-day / countdown / result announcements, static or animated. When Pedro supplies **(1) logo PNG, (2) athlete photo, (3) content**, this file supplies everything else. No re-deriving, no format questions. Build, `present_files`, done.

**Style in one line:** near-black interface, fine grid, chamfered panels, tick rulers, crosshair, diagonal slashes. **White does the talking; red and blue are highlights only (~10% of surface).** Precise, geometric, dynamic but minimal.

**Relationship to `shomen-social-templates.md`:** that file is the Swiss-grid system (season recaps, light + dark grunge). This file is the HUD system (event-day energy: AMANHÃ / HOJE / results / price index). Pick by content, not by mood:

| Content | System |
|---|---|
| "Competes today / tomorrow", live results, medal alerts, call-ups, product/price drops | **Glitch Post (this file)** |
| Season recap, career stats, long-form achievement lists | Swiss templates |

**Storage:** Warm. **Version:** 1.4 — 18 Sep 2026. Derived from the André Aguiar (HOJE), Leonor Gonçalves (AMANHÃ + HOJE) stills and the Leonor HOJE 20 s story animation.

---

## 1. Inputs

1. **Logo** — white Shōmen mark + wordmark, transparent PNG (`1000123820.png`, 2880×2496). Always forced to pure white (`rgb = 255`, keep alpha). Never recoloured red/blue in this system.
2. **Photo** — any resolution, any background. Claude cuts the athlete out (§6). Action shots and portraits both work. Below ~1500 px on the long edge the upscale gets soft — say so once, ship anyway.
3. **Content model:**

```
athlete:     "LEONOR GONÇALVES"          → first name white, surname in key colour
when:        "HOJE" | "AMANHÃ" | date    → the time hero
event:       "WKF YOUTH LEAGUE"
location:    "GUADALAJARA 2026"
category:    "JUNIOR -53 KG"             → reproduce exactly as given
cheer:       "LET'S GO!"               → brand cheer as of 18 Sep 2026 (was "FORÇA!"); caps
hashtag:     "#TEAMSHOMEN"
```

Text language is **PT-PT**. Reproduce supplied text **exactly** (spacing included — flag suspected typos after delivery, don't silently fix). Spec document language is English.

**Defaults when unspecified:** FX (glitch / VHS / matrix rain) → **OFF**, see §8.4. Format → 9:16 story. Several posts in one request → each must use a **different layout variant** (§5). Static unless animation is asked for.

---

## 2. Formats

| Format | Canvas | Render | Use |
|---|---|---|---|
| **Story** | 1080 × 1920 (9:16) | 2× (2160×3840) PNG · 1× for video | Stories, Reels cover |
| **Feed square** | 1080 × 1080 (1:1) | 2× (2160×2160) | Feed post |
| Feed portrait | 1080 × 1350 (4:5) | 2× | Optional, max feed real estate |

All coordinates in this document are **1× px**. Code multiplies by `S=2` for stills.

### 2.1 Instagram safe zones (story) — hard rule

| Zone | y-range | What may live there |
|---|---|---|
| Top UI (avatar, progress bars) | 0 – 250 | **Decor only**: slashes, micro-labels, tick rulers |
| **Hero band** | **260 – 1600** | Logo, athlete face, time hero, name, card, cheer, hashtag |
| Bottom UI (reply bar, share) | 1600 – 1920 | **Decor only**: footer rule, © line, small slashes, standby label |

Every hero string must have its ink bottom ≤ **y 1600** and ink top ≥ **y 260**. Script prints the last hero baseline — check it. Animated elements may *cross* the unsafe zones on entry but must *rest* inside the hero band.

### 2.2 Feed square safe area

No UI overlay, but the profile grid crops to the centre (3:4 on current IG, 1:1 legacy). Keep logo + name + time hero inside the central **1080 × 810** band (y 135–945) so the grid thumbnail still reads. Side margin 56.

---

## 3. Design tokens

### 3.1 Colour

| Token | Hex | Use |
|---|---|---|
| `BG` | `#090A0E` | Canvas |
| `PANEL` | `#0E1016` @ 85% | Card fill |
| `BORDER` | white @ 15% | 1 px panel border |
| `WHITE` | `#F5F6F8` | Primary text, logo |
| `GREY` | `#969CA8` | Secondary text, micro-labels |
| `DIM` | `#464C5A` | Tertiary labels, standby text |
| `RED` | `#FF2A50` | Key colour A — live / today / urgency |
| `BLUE` | `#54C8FF` | Key colour B — countdown / tomorrow / data |
| `GRID` | white @ 4–4.5% | 54 px square grid |

**Key-colour semantics:** each post has ONE key colour and one alt.
- **RED key** → HOJE, live, results. Surname red, hashtag red, big slashes red, thin companion line blue.
- **BLUE key** → AMANHÃ, countdowns, announcements. Surname blue, hashtag blue, big slashes blue, thin companion line red.
- The category highlight bar is **always blue** (it is "data"). The live dot and crosshair centre are **always red**.

**Glows:** two soft radial glows, squared falloff, additive.
- Key-colour glow in the corner where the big slashes are (radius ≈ 0.95·W, strength 0.24–0.30).
- Alt-colour glow in the diagonally opposite corner (radius ≈ 1.0·W, strength 0.20–0.24).

**Grain:** gaussian σ ≈ 5.5 (8-bit) on stills; σ ≈ 4 (0.016 float) on video, cycled from a pool of 6 pre-generated noise frames.

### 3.2 Typography — Tomorrow (Google Fonts), Light → Black

**Family:** [Tomorrow](https://fonts.google.com/specimen/Tomorrow) — 9 weights, plus italics. **Allowed range: 300 Light → 900 Black. Thin (100) and ExtraLight (200) are banned** — they don't survive a phone screen, video compression or grain (`LEONOR` in ExtraLight was barely legible, 18 Sep 2026). The point of the family is still **weight contrast**: pair Light with Black, skip the middle. If Light still reads weak at the rendered size (small type, busy photo behind it, VHS/grain pass), step up to Regular 400 — legibility beats contrast.

| Role | Weight | Size (story) | Size (1:1) | Notes |
|---|---|---|---|---|
| Time hero (`HOJE`, `AMANHÃ`) | **900 Black** | **150** (was 168) | 120–140 | White. Caps. Tight tracking (−1%). |
| Athlete first name | **300 Light** (400 Regular if it reads weak) | 96–120 | 80–96 | White. The light half of the pair. Never below 300. |
| Athlete surname | **800 ExtraBold / 900 Black** | same as first name | same | Key colour. The heavy half. |
| Cheer (`FORÇA!` / `LET'S GO!`) | 900 Black | **88** (was 100) | 84 | White |
| Hashtag | 600 SemiBold | **40** (was 46) | 40 | Key colour |
| Event name | 700 Bold | 46–52 | 40 | White caps |
| Location | 300 Light (400 Regular with FX on) | **34** (was 28) | 26 | Grey, tracked +2 |
| Category value | 700 Bold | 40–50 | 38 | Blue |
| Tab label (`CATEGORIA`) | 700 Bold | **22** (tab 256 wide) | 19 | Dark `#090A0E` on blue, tracked +3 |
| Micro-labels **next to hero content** (`DIA DE COMPETIÇÃO`, `ATLETA // TEAM SHOMEN`, `KUMITE`) | 500 Medium | **18** | 16–17 | Caps, tracked +3, grey / blue. 14 was unreadable on a phone. |
| Micro-labels in decor zones (label stack, standby) | 500 Medium | 14–15 | 15 | Caps, tracked +3 to +4, grey/dim |
| Micro-label lead line (`SHM // MATCH DAY`) | 700 Bold | 15 | 13 | White |
| Footer © | 400 Regular | 15 | 13 | Tracked +4 |
| **Numeric readouts** (coords, `01 / 01`, animated digits) | **Geist Mono** Regular/Bold | 14–15 | 13 | Exception — Tomorrow's figures aren't tabular; animated numbers jitter horizontally without a mono face. |

Rules:
- **Scale balance (18 Sep 2026):** small text went up, hero text came down slightly — but keep the jumps obvious (≈150 / 120 / 88 / 46 / 34 / 18). If everything converges on the same size the HUD goes flat.
- **Never** two adjacent hero strings at the same weight. Name = Light + Black. Card = Bold + Light. 
- **Weight floor: 300 Light.** No Thin, no ExtraLight, anywhere, any size. The engine's `T()` helper rejects them.
- Italics (Tomorrow has them for every weight) are allowed for ONE element per post max — best on the time hero in animated versions, since the slant echoes the 60° slashes. Default: upright.
- Tracking is applied glyph-by-glyph (draw char, advance by `getlength + tracking`). No spacing arg.
- Vertical placement by **ink bounds** (`font.getbbox`), not font boxes. For baseline alignment of strings with diacritics/cedillas, measure a diacritic-free probe (`FORA!` for `FORÇA!`, `GONALVES` for `GONÇALVES`).
- No brush, script, grunge, handwritten or "martial arts" fonts. Ever.

**Font files — environment note.** Project knowledge rejects `.ttf` uploads, the sandbox ships without Tomorrow, and network is off by default. Resolution order at build time:
1. **npm (needs sandbox network egress enabled, package managers allowed):** `cd /home/claude && npm pack @fontsource/tomorrow && tar xf fontsource-tomorrow-*.tgz` → files in `package/files/tomorrow-latin-<weight>-normal.woff2` (+ `-italic`). Convert for PIL: `pip install fonttools brotli --break-system-packages`, then `TTFont(f).flavor=None; save('Tomorrow-<weight>.ttf')`. Use the `latin` subset (covers PT-PT diacritics). Setting: claude.ai → Settings → Capabilities → Code execution and file creation → **Allow network egress** ON, allowlist "Package managers only" is enough (npm + PyPI). Account-level; applies to new chats.
2. **Chat upload:** Pedro attaches `Tomorrow.zip` (or the TTFs) to the build request → `/mnt/user-data/uploads/`. Chat uploads accept binaries that project knowledge doesn't.
3. **Fallback:** Work Sans Bold + Regular (`/mnt/skills/examples/canvas-design/canvas-fonts/`) — state the fallback in one line on delivery. Never block a build on the font.
Geist Mono lives in the same bundled folder.

*History:* v1.0 stills + video (André, Leonor) were rendered in Work Sans Bold/Regular + Geist Mono, because Tomorrow wasn't available. Anything rebuilt from now on uses Tomorrow.

---

## 4. Graphic element library

Only these adornments exist. **No** icons, illustrations, brush strokes, ink splatter, kanji decoration, gradients on text, drop shadows. The athlete photo is the single pictorial element.

| Element | Spec |
|---|---|
| **Grid** | 54 px squares, 1 px, white 4–4.5%. **Masked off the athlete** (`alpha × (1 − athlete_alpha)`). |
| **Diagonal slashes** | Parallelograms at **60°** from horizontal (`dx = dy / tan 60°`). Set of four: big (64 wide), medium (44 wide, partly off-canvas), thin companion line (5 wide, alt colour), white hairline (1.5 wide, 78% alpha). Live in a corner, run from the edge inward, end before the hero band content. **Never overlap a title.** |
| **Mini slashes** | Two 16-wide, 30-tall slashes (blue + red) at the footer start. |
| **L-brackets** | Two-stroke corners, 3 px stroke / 32–34 long around the logo (red top-left, blue bottom-right). 2 px / 22–26 long, white 60–67%, outside one card corner and optionally at photo-zone corners. |
| **Tick rulers** | 1 px ticks every 7–10 px, short 5–6 / long 10–12 every 5th. Horizontal under label stacks; vertical along a free edge. White 27–35%. |
| **Crosshair** | r=24 circle (white 47%), four arms from 12→36 (white 59%), r=4 red centre dot. With two mono readouts `X 20.6597` / `Y -103.3496` (event-city coordinates — look them up per event). **Never on the athlete's face or body.** |
| **Chamfered card** | 45° chamfer of 28–30 px on two opposite corners (default top-right + bottom-left; mirrored variant top-left + bottom-right). Panel fill + 1 px border. **6 px accent bar** on the left edge, split 50/50 key colour over alt colour. |
| **Highlight bar** | 72–84 tall. Blue 1 px outline, blue 10% fill. Solid blue **angled tab** on the left (230 wide, right edge slanted 34–36 px) with dark label. Optional small blue mono descriptor right of tab. Value right-aligned, blue, bold. |
| **Chamfered chip** | Alternative container for the category: blue outline + 10% fill, 14 px chamfers, label above in grey micro. |
| **Underline bar** | 4 px white, 360–430 long, under the name. Descriptor micro-label (`ATLETA // TEAM SHOMEN`) sits beside it on the free side. |
| **Live dot** | r=6 red circle before `DIA DE COMPETIÇÃO`. HOJE posts only. |
| **Vertical word** | Time hero rotated 90° (reads bottom→top) on a free edge strip, 4 px key-colour rule alongside, tiny `T-24H` tag at its foot. |
| **Footer** | Hairline (white 20%) at y=1846, `SHOMEN © 2026` tracked, optional standby label + ruler at y≈1700–1726 (`ON TATAMI // GUADALAJARA MX`, `STANDBY // …`). |

**Micro-label vocabulary** (invented HUD filler — always list them on delivery so Pedro can veto): `SHM // MATCH DAY`, `SHM // COUNTDOWN`, `SHM // RESULT`, `REF. YL-GDL-26 / KUMITE` (pattern: `REF. <EVENT>-<CITY>-<YY> / <DISCIPLINE>`), `LIVE — TEAM SHOMEN`, `T-24H — TEAM SHOMEN`, `ATLETA // TEAM SHOMEN`, `DIA DE COMPETIÇÃO`, `CATEGORIA`, `KUMITE` / `KATA`, `01 / 01`. Micro-labels that are real words are PT-PT; system codes stay Latin/English.

---

## 5. Layout

### 5.1 Story (9:16) — band map

```
y    0 ─ 250   DECOR   corner slashes · label stack · ruler
y  270 ─ 530   HEADER  logo (250–260 wide) + brackets · time hero OR crosshair on the opposite side
y  430 ─ 1180  PHOTO   athlete cut-out, fades to BG at the bottom
y 1010 ─ 1260  NAME    one or two lines, sits on the faded part of the photo
y 1270 ─ 1285  RULE    underline bar + descriptor
y 1300 ─ 1510  CARD    event · location · category
y 1500 ─ 1600  CHEER   FORÇA! + hashtag, shared baseline
y 1600 ─ 1920  DECOR   standby label · ruler · footer rule · © · mini/bottom slashes
```

Side margin **64**. Logo inset 84 so the brackets land on the margin.

### 5.2 Story variants

**Variant R — "LIVE" (red key, HOJE).** Reference: Leonor HOJE.
- Slashes top-right. Label stack + ruler top-left (in decor zone).
- Logo top-left. **Time hero top-right**, right-aligned, 168 pt; 4 px red underline beneath; live dot + `DIA DE COMPETIÇÃO`.
- Athlete centred (cx 540, head-top ≈ 505). Crosshair + readouts mid-left (≈104, 640). Vertical ruler on the right edge.
- Name on **one line**, auto-fit to 952 wide. Underline bar on the **right** half, descriptor to its left.
- Card standard chamfer. Row 1: event left / location right. Row 2: full-width highlight bar (tab `CATEGORIA` + `KUMITE` + value).
- Cheer row mirrored: hashtag left, `FORÇA!` right.
- Footer: mini slashes left, © right.

**Variant B — "COUNTDOWN" (blue key, AMANHÃ).** Reference: Leonor AMANHÃ.
- Slashes **top-left, mirrored** (x → 1080 − x). Label stack top-right, right-aligned.
- Logo **top-right**. Crosshair + readouts top-left under the slashes; vertical ruler on the left edge.
- Athlete shifted left (cx ≈ 455, head-top ≈ 430).
- **Time hero as vertical word** on the right strip (x ≈ 900–1016, starts y ≈ 566 — clear of the logo bracket), 150 pt, blue rule alongside.
- Name on **two lines**, left-aligned, 118 pt. Photo fade must finish before the first line (fade 870→1050) — white type on a white gi is the classic failure.
- Underline bar left, descriptor right.
- Card **mirrored chamfer**, shorter (176). Left: index + ruler, event, location. Right: category in a **chamfered chip** with `CATEGORIA` micro above.
- Cheer row: `FORÇA!` left, hashtag right.
- Bottom decor: red slashes bottom-right, © left, standby label + ruler left.

**Variant H — "HERO CARD" (action shot).** Reference: André Aguiar HOJE.
- Photo used **with its background** (arena crushed to ~20% luminance, 75% desaturated, cool tint ×[0.9, 0.95, 1.15], edge-faded), athlete kept full colour on top via the mask.
- Slashes top-right, logo top-left with label stack / ruler / crosshair to its right.
- Name one line over the fade. Card carries **the time hero as the "price"** (right-aligned, 104 pt) with `DIA DE COMPETIÇÃO` unit label; event + location left; highlight bar below.
- ⚠ Built before the safe-zone rule: logo sits at y 84. When rebuilding, shift header to y ≥ 270 and compress.

**Rules for making new variants** (when >2 posts go out together, or to avoid repetition):
1. Flip the slash corner (4 options) and put the logo in the adjacent free top corner.
2. Move the time hero: top-opposite-logo / vertical strip left or right / inside the card as the "price".
3. Name: 1 line vs 2 lines; left- vs right-aligned.
4. Category container: highlight bar vs chip.
5. Swap cheer/hashtag sides. Swap key colour **only** if semantics allow (§3.1).
6. Athlete cx: 455 / 540 / 625 — always away from the vertical word, never under the logo.
Change **at least three** of these six between sibling posts.

### 5.3 Feed square (1:1) — band map

1080×1080 has no room for the full story stack. Drop the standby decor, shrink the photo, keep the hierarchy.

```
y   40 ─ 250   HEADER   logo (200 wide) one corner · time hero (Black, 120–140) opposite corner
               slashes tucked into the time-hero corner, ending above it, or in the logo-opposite bottom corner
y  150 ─ 760   PHOTO    athlete cut-out, head-top ≈ 170, fade 600→760
y  700 ─ 800   NAME     ONE line, auto-fit to 968 (margin 56), Light + Black pair
y  812 ─ 826   RULE     underline + descriptor
y  842 ─ 990   CARD     single row: event (Bold) + location (Light) left · category chip right
y  1000 ─ 1050 FOOT     hashtag left (SemiBold 34) · FORÇA! right (Black 56) — or footer © if cheer is dropped
```

**Square layout options:**
- **SQ-A (stacked, default):** as mapped above. Athlete centred.
- **SQ-B (split):** athlete occupies the **right 55%** (cx ≈ 760, fades left + bottom); all type stacked in a left column 56→540: logo, time hero, name on two lines, chip, hashtag. Slashes bottom-right behind the fade. Best for portraits with clean shoulders.
- **SQ-C (vertical word):** SQ-A with the time hero rotated on the left edge strip and the logo alone top-right. Best for long words (`AMANHÃ`, `RESULTADO`).

Square drops: standby label, bottom ruler, second bracket pair, `01 / 01` index. Keeps: grid, glows, one slash set, crosshair (small, in a free corner), card accent bar.

---

## 6. Photo pipeline

1. **Extract** — JPG/PNG direct. From PDF: `pdfimages -png file.pdf out` (gets the embedded original, not a page raster).
2. **Locate** — downscale, overlay a 500 px coordinate grid, `view` it, read real pixel coordinates. **Never estimate coordinates from the chat preview** — it is scaled (this cost a full re-run once).
3. **Segment — OpenCV GrabCut** (no rembg/mediapipe models offline):
   - Work at 0.25× for large photos, 1× for ≤1800 px.
   - `GC_BGD` everywhere → `GC_PR_FGD` in the athlete's bounding rect → carve obvious empty sub-rects back to `GC_BGD` → `GC_FGD` boxes on face, torso core, each glove.
   - 8–10 iterations, `GC_INIT_WITH_MASK`. Then: open 3×3, close 5–7, **keep largest connected component**, optional 3×3 erode, upscale cubic, gaussian blur σ 1.6 (1× source) – 4 (4× upscaled mask).
   - Review on a flat coloured backdrop before composing.
4. **Grade** — contrast ×1.08–1.10 about 0.5 (+0.02 lift for dim indoor shots), R×0.97, B×1.02–1.04 (cool the whites toward the HUD). Stays full colour. Never duotone.
5. **Place & fade** — scale so shoulders span ~55–65% of canvas width; vertical smoothstep fade to BG over ~180–250 px ending **above the first name line**. With-background variant (H) also fades top and sides.
6. **Rim halo** — mask blurred σ≈22–26 px (2×) × key colour × 0.10, added behind the athlete.
7. **Grid mask** — grid alpha × (1 − athlete alpha).

---

## 7. Build — static

- Script: `/home/claude/compose_*.py`, PIL + numpy + cv2. `S=2`, helper `P(v)=round(v*S)`.
- Order: numpy background (BG + glows) → athlete composite → to PIL RGBA → grid layer → vector/HUD elements (draw semi-transparent shapes on a separate RGBA layer and `alpha_composite`; PIL's direct draw doesn't blend alpha on RGB) → type → grain → save PNG `optimize=True`.
- Helpers worth keeping verbatim: `text(xy, s, font, fill, tr, anchor)` (glyph-wise tracking, l/r anchor), `ruler()`, `bracket(x, y, size, corner, colour, w)`, `slash(xt, width, y0, y1, colour, mirror, yref)`, `card(x0,y0,x1,y1, mirror)`, `crosshair(cx, cy)`.
- **QA before shipping:** render a 540×960 preview with translucent yellow bands over y 0–250 and 1600–1920; confirm no hero text touches them, no white-on-white, nothing collides with brackets. Then zoom-crop any tight junction at full res.
- Output: `/mnt/user-data/outputs/shomen-<athlete>-<WHEN>.png` → `present_files`.
- Working script: `compose_still.py` in `shomen-glitch-engine.md` (2× still of variant R, reuses the video engine's layer block). Optional glitch pass: §8.4.

---

## 8. Build — animated (story, 20 s)

**Deliverable:** 1080×1920, 30 fps, 20 s (600 frames), H.264 High, yuv420p, `+faststart`, ~9–10 Mbps (≈22 MB), no audio.

### 8.1 Engine

**Working code lives in `shomen-glitch-engine.md`** (cut-out script + full animation script + runbook). Start from it.

- Render **every element as its own layer**: draw on a transparent 2× RGBA canvas → LANCZOS down to 1× → crop to bbox → store `{rgb, a, x, y, anchor}` as float32.
- `comp(frame, layer, dx, dy, alpha, clip=(f0,f1), scale)` composites onto a float32 frame with bounds clipping. `clip` = horizontal wipe (fraction of layer width). `scale` resizes about the layer's `anchor`.
- Easing: cubic ease-out `1 − (1−x)³` for entries. Ambient motion = sines with **co-prime-ish periods** (4, 5, 6, 7, 9 s) so nothing visibly loops.
- Athlete: pre-scale the cut-out to the **max zoom** once, resize *down* per frame (`INTER_AREA`); anchor the zoom near the face (0.5, 0.15).
- Small per-frame dynamics (coordinate digits, scrolling ruler) are drawn directly on the 1× frame with PIL.
- Grain: pool of 6 noise frames, cycled.

### 8.2 Timeline (reference: Leonor HOJE)

| t (s) | Element | Motion |
|---|---|---|
| 0.0–1.2 | Glows | Fade up from black |
| 0.2–1.4 | Grid | Fade in |
| 0.3–1.35 | Slashes ×4 | Slide in **along their own 60° axis** from off-canvas (520 px), staggered 0.12 s |
| 0.6–1.6 | Label stack, ruler | Left→right wipes, staggered 0.15 s |
| 0.8–1.6 | Logo | Fade + scale 1.12→1.0 |
| 1.2–1.9 | Logo brackets | Converge diagonally from 40 px out |
| 1.0–2.2 | Athlete | Fade + rise 50 px |
| 1.4–2.0 | Crosshair + readouts | Fade in |
| 1.6–2.3 | Time hero | Slide 120 px from the right + wipe |
| 2.0–2.6 | Hero underline | Grows from the right |
| 2.3–2.9 | `DIA DE COMPETIÇÃO` | Wipe |
| 2.4–3.3 | Name | First name from left, surname from right (140 px), 0.2 s stagger |
| 3.0–3.8 | Underline / descriptor | Grow / fade |
| 3.3–4.0 | Card | Wipe open left→right; corner bracket settles from 30 px out |
| 3.7–4.5 | Event / location | Slide 40 px from opposite sides |
| 4.1–5.2 | Highlight bar → tab → label → value | Wipe, slide 60 px, fade, slide 60 px |
| 4.9–5.5 | Hashtag | Slide + wipe from left |
| 5.1–5.7 | Cheer | Pop: scale 1.35→1.0 + fade |
| 5.4–6.2 | Footer | Fade |

**Ambient, 6–20 s:**
- Athlete slow zoom 1.00→1.06 across the full 20 s.
- Glow pulse: key ±22% @ 4 s, alt ±25% @ 5 s.
- Slashes drift ±10–28 px along their axis @ 6 s, phase-offset per slash.
- Crosshair Lissajous drift (±18 px @ 7 s, ±26 px @ 9 s); readout digits follow + micro-jitter.
- Vertical ruler scrolls 14 px/s.
- Live dot: blink 1 Hz, alpha 0.25→1, scale 1→1.35.
- Full-frame blue scan line, top→bottom in 1.6 s, every 5 s, 6% peak.
- Card light sweep, 0.9 s, every 4 s, 10% peak.
- ~~Glitch on the time hero~~ — **removed 18 Sep 2026.** Text is never glitched (§8.4, hard rule 13). Chromatic offset exists only inside the opt-in FX pass, on graphics and photo.
- Cheer pulse at 9 / 13 / 17 s: scale 1→1.07→1 over 0.6 s.

**Variant B (AMANHÃ) animation deltas:** vertical word wipes **bottom→top**; replace live dot with a `T-24H` label that ticks (`T-23:59:58…` in Geist Mono); slashes enter from top-left.

**Square animated:** same engine, 10–15 s, drop scan line frequency to every 6 s, no standby decor.

### 8.3 Sandbox constraints (learned the hard way)

- **300 s hard limit per command**, and background processes die when the command returns. Render in **segments of 200 frames** (`python3 vid.py 0 200`, `200 400`, `400 600`, each wrapped in `timeout 285`) — ~0.45 s/frame on the single core.
- Segments: `libx264 -preset ultrafast -crf 10` (near-lossless intermediates, ~160 MB each). Final: concat demuxer → `-preset fast -b:v 9M -maxrate 13M -bufsize 18M -profile:v high -pix_fmt yuv420p -movflags +faststart`.
- Don't wait on `pgrep -f script.py` inside the same shell line — it matches itself and never exits.
- Animated grain inflates CRF encodes (~90 MB at CRF 17). Use bitrate-capped final encode.
- Verify with `ffprobe` (duration, size, fps, frame count) and extract 3 frames (entry, a glitch frame, end) for a visual check. Claude can't watch motion — say so, and name the effect most likely to need toning down.

### 8.4 FX pass — glitch, VHS grain, matrix rain (**opt-in only**)

**Default: OFF.** The clean HUD is the house look. These effects are built and documented, and are switched on **only when Pedro asks for them in the request** ("com glitch", "VHS", "matrix", "grão VHS"…). Never add them on initiative, never "a little bit by default". If asked for one, don't assume the others — `glitch` ≠ `rain`. The standard fine grain (§3.1) is not part of this pass and stays on always.

**The absolute rule: FX never touch text or the logo.** Not displaced, not RGB-split, not scan-lined, not streak-grained. Enforced structurally, not by careful placement:

> **Two-pass compositing.** Pass 1 = background, glows, rain, athlete, grid, slashes, brackets, rulers, crosshair, card, bars, footer graphics → **FX applied here**. Pass 2 = logo + every text layer, composited **on top, after** the FX. Mixed layers must be split into a graphic half and a text half (done for the `CATEGORIA` tab and the footer).

Also protected: **the athlete's face.** No displaced slice crosses it (story variant R: y 470–840); a soft elliptical mask restores the clean face after any burst; the tracking band loses its displacement over those rows. Mild chroma bleed / grain on the face is acceptable, tearing is not.

**Flags (engine CONFIG):** `FX_VHS`, `FX_RAIN` (video) · `FX_GLITCH` (still). All `False` in the file.

| Effect | Flag | Spec |
|---|---|---|
| **Slice displacement + RGB split** | `FX_VHS` / `FX_GLITCH` | Horizontal bands, 3–50 px tall, shifted ±10–90 px (≤ ±24 inside the card), R/B channels rolled ±3–10 px. Zones: top decor, shoulders/gi below the face, card, bottom decor. **Video:** bursts of 3–7 bands at 0.35 (boot), 6.6, 8.0, 10.7, 13.5, 16.2, 18.0 s, 4–6 frames each; between bursts a single thin band on ~12% of frames. Never in the last 1.5 s — the end frame must be clean-ish for the cover. **Still:** ~18 hand-placed bands, seeded. |
| **Chroma bleed** | `FX_VHS` | Constant: R +2 px, B −2 px. |
| **Scanlines** | `FX_VHS` / `FX_GLITCH` | Every other row ×0.90 (video 1×); 4-row pattern ×0.93/×0.965 (still 2×). ±2% luma wobble on video. |
| **VHS streak grain** | `FX_VHS` | Gaussian σ 0.10 blurred 11×1 horizontally, pool of 6, ×1.6 during bursts. Base fine grain drops to ×0.6 so the total doesn't mud. |
| **Tracking band** | `FX_VHS` | 46 px band rolling top→bottom at 170 px/s (one pass ≈ 16 s): rows jittered ±14 px in 3 px groups + white noise 10%. Displacement = 0 over the face rows. |
| **Head-switching noise** | `FX_VHS` | Bottom 36 px (decor zone): progressive skew + noise. |
| **Matrix rain** | `FX_RAIN` | Falling columns of `0-9 A-F < > / + = : * #` in **Geist Mono Bold 17**, 18×26 px cells, 55% of columns active, speeds 5–15 rows/s, trails 8–24 cells, white head + **BLUE** trail. **Never green** — the system has two colours. **No katakana/kanji** (rule 8). Additive, behind the athlete (she occludes it), strong on boot (80%) settling to 38% by 3 s; attenuated to 15% behind name/card (y 940–1120 fade), back to 70% in the bottom decor. Video only. |
| **Corruption bars** | `FX_GLITCH` | Still only: ~16 short solid ticks (2–8 px tall, 30–220 long) in red / blue / white at 35–85%, in empty zones, with exclusion boxes over face and logo. |
| **Pixel-sort smear** | `FX_GLITCH` | Still only: 20 px tall, 180 px long, fading, off one shoulder edge. |

**Type under FX:** Light loses against scanlines and grain. With any FX flag on, first name and location step up to **Regular 400** (engine does this automatically).

**Encode:** streak grain eats bitrate — final encode at `-b:v 11M -maxrate 15M -bufsize 22M` (≈27 MB) instead of 9M. Render cost ≈ 0.26 s/frame → two segments of 300 frames fit the 300 s limit.

**Naming:** FX deliverables carry a suffix — `…-story-vhs.mp4`, `…-glitch.png` — and never overwrite the clean version.

**On delivery:** Claude can't watch motion. Name the three things most likely to need toning down: streak grain on skin, the tracking band reading as a defect, rain density in the first 2 s.

---

## 9. Hard rules

1. White does the talking. Red + blue ≤ ~10% of surface combined.
2. One key colour per post, chosen by semantics (§3.1), never by taste.
3. Hero text rests inside y 260–1600 on stories. No exceptions.
4. Text never sits on a slash. Slashes never cross the title, the logo or the athlete's face.
5. Crosshair, rulers and brackets never touch the athlete's face.
6. No white type over un-faded white gi. Move the fade, not the type.
7. Supplied text reproduced exactly; invented micro-labels listed on delivery.
8. Adornments limited to §4 (plus the opt-in FX of §8.4 when requested). No icons, illustrations, brush, splatter, kanji decoration, text gradients, drop shadows.
9. Logo pure white, never recoloured, never glitched. In rendered **text**, the brand is written `SHOMEN` (no macron) — avoids glyph-coverage problems; the macron lives only in the logo artwork.
10. Tomorrow weights: **Light (300) → Black (900) only** — Thin and ExtraLight banned. Pair Light with Black. Geist Mono only for numeric readouts.
11. Sibling posts differ on ≥3 of the 6 variant axes (§5.2).
12. **FX are opt-in.** Glitch, VHS grain and matrix rain (§8.4) are OFF unless Pedro asks for them in the request — stills and video alike.
13. **FX never touch text or the logo** — two-pass compositing, text last. Never tear the athlete's face. Rain is palette blue, never green.
14. This spec overrides the project's HTML design system (DM Sans / `#0a0a0c`) and the Swiss template's type rules — different medium, different system.

---

## 10. Reference builds

| Date | Piece | Variant | Notes |
|---|---|---|---|
| 17 Sep 2026 | André Aguiar — HOJE — Junior +76 kg | H | Action shot w/ crushed arena bg. Pre-safe-zone header. Work Sans. |
| 17 Sep 2026 | Leonor Gonçalves — AMANHÃ — Junior −53 kg | B | Vertical word, two-line name, chip. Work Sans. |
| 17 Sep 2026 | Leonor Gonçalves — HOJE — Junior −53 kg | R | Still + 20 s animation. Work Sans. |
| 18 Sep 2026 | Leonor Gonçalves — HOJE — Tomorrow rebuild | R | 20 s animation (clean + VHS/matrix variant, §8.4) + 2× glitch still — the FX reference builds. First name rendered ExtraLight in the videos — **superseded**, rebuild with Light. |
| 18 Sep 2026 | Leonor HOJE story — VHS v2 | R | Rebalanced type scale, Regular first name, FX on. **Current reference.** |
| 18 Sep 2026 | André Aguiar + Leonor Gonçalves — 1:1 roster post | SQ-duo | Blue key (announcement). Logo top-centre between the two heads, label stack top-left, slashes top-right, crosshair between athletes, names in two columns (Regular + Black) with category chips, card = `EM COMPETIÇÃO` tab + location + event as Black hero. Athlete looking sideways goes on the side that makes him look **into** the frame — never flip a photo (gi lettering). FX on. |

Event: WKF Youth League Guadalajara 2026 (crosshair coords 20.6597, −103.3496).

---

*v1.4 — 18 September 2026 (type scale rebalanced; duo 1:1 reference). v1.3 — 18 September 2026 (§8.4 FX pass: glitch / VHS / matrix rain, opt-in only, never on text; HOJE text glitch removed from the default timeline). v1.2 — 18 September 2026 (weight floor: Light 300; Thin/ExtraLight banned after the Leonor HOJE rebuild). v1.1 — 18 September 2026 (engine file reference, font sourcing via npm, SHOMEN without macron in text, cheer → LET'S GO!). v1.0 — 17 September 2026.*
