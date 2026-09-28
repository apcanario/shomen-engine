# Shōmen — Social Post Templates

**Purpose:** Locked spec for Shōmen Instagram athlete/announcement posts. When Pedro asks for a Shōmen image, he supplies only **(1) the logo PNG, (2) the photo, (3) the content**. Everything else — grid, type, colour, rhythm, grunge treatment — is defined here. No re-deriving from scratch, no asking for format preferences.

**Sibling spec:** `shomen-glitch-post.md` — the dark sci-fi HUD system for event-day posts (HOJE / AMANHÃ / results), static and animated. This file stays the system for season recaps and stat-heavy posts. Route by content.

**Style lineage:** Swiss / International Typographic Style (Müller-Brockmann). Rigid grid, heavy/regular weight contrast, generous negative space, no decoration. The anti-thesis of current flat-corporate social design. Dark mode adds a post-modern / risograph-grunge layer *over* an intact Swiss system — never a demolition of it.

---

## 1. What Pedro provides (the only inputs)

1. **Logo** — Shōmen S mark, PNG. Ideally the solid-fill version (`1000099860.png` = red fill on transparent works; the mark gets recoloured per skin anyway).
2. **Photo** — athlete photo, any resolution. Claude crops to the block ratio.
3. **Content** — name, subtitle, the red headline stats, the footer stats. See §6 content model.

If Pedro doesn't specify skin → produce **both light and dark**. If he doesn't specify format → default **1:1 (feed)**; offer story/portrait after.

---

## 2. Formats

| Format | Dimensions | Use |
|--------|-----------|-----|
| **Feed square** | 1080 × 1080 | Default. Instagram feed. |
| **Feed portrait** | 1080 × 1440 (3:4) | Max feed real estate. |
| **Story** | 1080 × 1920 (9:16) | Stories/Reels cover. Adds a large bold title band above the name block. |

All three share the same grid, type scale, colour, and rhythm engine. They read as one system, not three separate posts.

---

## 3. Grid & layout constants

- **Side margin (M):** 72px (all formats)
- **Inner width:** canvas width − 2M
- **Vertical rhythm (G):** **30px** — one constant between *every* element, and equal to the top and bottom margin. Non-negotiable: uniform spacing is the whole point. Do not hand-tune per-block gaps.
- **Photo height:** the free variable. It absorbs slack so the rhythm closes exactly to canvas height. Never fix photo height first.

### Rhythm engine (mandatory method)

Positions are computed from **real ink bounds**, not font-box metrics. Font boxes carry internal padding that lies — an 80pt name looks like it has dead air above it if placed by box-top. Measure the actual rendered pixel top/bottom of each string (`getbbox` on a probe render) and space by G between ink-bottom → ink-top.

Vertical band order (square/portrait):
1. Top rule (3px)
2. Name (heavy)
3. Subtitle (regular, tracked)
4. Photo block
5. Red headline stat
6. Red stat 2
7. Red stat 3
8. Divider (2px)
9. Footer labels (bold, tracked, 3 columns)
10. Footer values (regular, 3 columns)

Total vertical G-units = 11 (top margin + 9 inter-band gaps + bottom margin). `photo_h = canvas_h − 11·G − Σ(other band ink heights)`.

Story format inserts a **title band** (2 lines, heavy ~112pt) between the top rule and the name, still on the same G rhythm.

---

## 4. Typography

**Font:** **Tomorrow** (Google Fonts) — Shōmen's brand typeface as of 17 Sep 2026, replacing Work Sans. Use the weight range for contrast: **Name → ExtraBold (800)**, headline stat → Bold (700), stats 2–3 → SemiBold (600), subtitle + footer values → Light (300), footer labels → Bold (700). In the table below read "Bold" as the heavy weight listed here and "Regular" as Light. **Dark/grunge skin: cap at Bold (700)** — ExtraBold/Black still turn to mush under grain and torn edges; never simulate weight with stroke. The TTFs are not bundled and project knowledge rejects `.ttf` — follow the font resolution order in `shomen-glitch-post.md` §3.2 (npm `@fontsource/tomorrow` if network is on → chat-uploaded zip → Work Sans). **Fallback:** Work Sans (`/mnt/skills/examples/canvas-design/canvas-fonts/WorkSans-Bold.ttf` + `-Regular.ttf`) — state the fallback on delivery.

| Element | Font | Size | Notes |
|---------|------|------|-------|
| Story title | Bold | 112 | 2 lines, e.g. "Resumo de uma / época de ouro" |
| Athlete name | Bold | 100 (portrait/story) · 80 (square) | One line if it fits inner width; else stack |
| Subtitle | Regular | 26 | Tracked +7px letter-spacing, uppercase |
| Red headline stat | Bold | 48 | The single most important achievement |
| Red stats 2–3 | Bold | 40 | Second-tier international results |
| Footer labels | Bold | 24 | Tracked +3px, uppercase |
| Footer values | Regular | 30 | Sentence case |

Letter-tracking is done glyph-by-glyph (draw each char, advance by width + tracking), not via a spacing arg.

---

## 5. Colour

### Light skin
- Background: `#F4F2EE` (off-white, matches Swiss poster refs)
- Ink (name, subtitle, rule, divider, footer): `#252525` — brand dark grey, **not** pure black
- Red (headline + stats 2–3, logo): `#FF1943` — brand red
- Photo: full colour, untouched

### Dark skin (Swiss grid + grunge)
- Background: `#0E0E10` (near-black, not pure)
- Ink: `#E8E6E2` (off-white)
- Neon (headline + stats + logo + frame): `#FF2A5A` — hotter than brand red, electric but still unmistakably Shōmen
- Photo: **kept in colour**, graded — gamma lift 0.82, saturation ×0.82, warm temp (R×1.06, B×0.93), gentle sigmoid contrast, 10% original blended back. Not duotone. Athlete must read clearly against the dark bg.

**Logo:** recoloured per skin (red `#FF1943` light / neon `#FF2A5A` dark). Placed in the right dead-zone beside the red stat block, vertically centred on it, ~116px tall.

---

## 6. Content model

Pedro supplies these fields. Hierarchy is fixed — the #1 / headline achievement is always the single red headline, never a list item.

```
name:        e.g. "Leonor Gonçalves"
subtitle:    e.g. "RECAP ÉPOCA 2025/2026"   (goes uppercase, tracked)
story_title: (story only) e.g. "Resumo de uma época de ouro"  → split to 2 lines
red_headline: the #1 stat, biggest       e.g. "#1 RANKING WKF JUNIOR –53 KG"
red_2:                                    e.g. "VICE-CAMPEÃ DA EUROPA EKF"
red_3:                                    e.g. "3× OURO WKF YOUTH LEAGUE"
footer: 3 columns of {label, value}       e.g.
   CAMPEÃ / Nacional
   CAMPEÃ / Nacional de Clubes
   VENCEDORA / Taça de Portugal
```

If Pedro gives more than 3 international stats, the top one is the headline and the next two are red_2/red_3; overflow goes to a caption, not the image. If fewer footer items, keep columns balanced (2 cols centred, or 1 col left).

---

## 7. Dark-skin grunge stack (applied over the finished Swiss layout)

Order matters. Each is a layer over an intact grid:
1. **Film grain** — gaussian noise σ≈15
2. **Photocopy dust** — sparse bright (>0.9975) + dark (<0.0018) specks
3. **Horizontal streaks** — ~60 faint subtractive scan lines
4. **Crisp neon headline restamp** — re-draw the #1 stat over the grain so it stays sharp. **No chromatic/cyan ghost** (Pedro rejected it).
5. **Torn edges** — ~140 bg-coloured nibbles along borders + bigger polygon bites at the 4 corners
6. **Vignette** — soft radial darken
7. **Neon frame** — 2px inset at 10px

Identity survives because grid, hierarchy, type, and logo never move. Grunge is a finish, not a redesign.

---

## 8. Build workflow

- Script pattern: `/home/claude/compose_*.py` using PIL + numpy.
- Read `/mnt/skills/examples/canvas-design/SKILL.md` only if doing something outside this spec; for standard posts this file *is* the spec.
- Output to `/mnt/user-data/outputs/`, `present_files`, done. No postamble.
- Reference implementation last used: Leonor Gonçalves season recap (square light+dark, portrait feed, story). Same code is the template — swap inputs.

---

## 9. Hard rules

- Uniform G. No per-block hand-tuning. If a gap looks wrong, the rhythm engine is wrong, not the value.
- Dark skin: Bold (700) max. Light skin: ExtraBold (800) max. Never simulate heavier weight with stroke.
- Dark photo stays colour-graded, never greyscale/duotone.
- No cyan ghost on the headline.
- Logo recoloured per skin, never the raw gradient PNG on top of the composition.
- Name hierarchy: headline stat is always the standalone red headline.
- This spec overrides the project's default web design system (DM Sans / `#0a0a0c`) — that palette is for **HTML artifacts**, this is for **rendered brand images**. Different medium, different system.

---

*Version 1.1 — 17 September 2026. Font → Tomorrow; cross-reference to `shomen-glitch-post.md`. (v1.0 — 6 July 2026, derived from the Leonor Gonçalves recap build.)*
