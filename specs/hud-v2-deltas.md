# Shōmen — HUD Engine v2 (national-team call-up build, 24 Sep 2026)

**Purpose:** Working Python for the Portugal-palette call-up posts (CONVOCADO / CONVOCADA — André Aguiar, Leonor Gonçalves, WKF World Championships Poland 2026). One engine renders **all four deliverables per athlete**: 9:16 story still (2×), 1:1 feed still (2×), 20 s story video, 20 s feed video. Supersedes `shomen-glitch-engine.md` for anything built on this system; the v1 engine stays valid for the HOJE/AMANHÃ variants.

**Storage:** Warm. **Version:** 2.0 — 24 Sep 2026. Rendered clean (no VHS/glitch FX) as requested.

---

## Runbook

```bash
cd /home/claude && mkdir -p fonts && npm pack @fontsource/tomorrow >/dev/null && tar xf fontsource-tomorrow-*.tgz
pip install fonttools brotli --break-system-packages -q
python3 -c "from fontTools.ttLib import TTFont
W={300:'Light',400:'Regular',500:'Medium',600:'SemiBold',700:'Bold',800:'ExtraBold',900:'Black'}
for n,name in W.items():
    f=TTFont(f'package/files/tomorrow-latin-{n}-normal.woff2'); f.flavor=None; f.save(f'fonts/Tomorrow-{name}.ttf')"
# logo: extracted from an existing post (white threshold, crop 60:480,60:560 of the 2160 px post) and vectorised by logo.py -> logo_mask_raw.png must exist
python3 cut_and.py; python3 cut_leo.py; python3 cut_leo2.py      # GrabCut masks -> and_mask.png / leo_mask.png (VIEW the *_prev.jpg)
python3 hud.py aguiar story still      # 2x PNG in outputs + qa_*.png with safe-zone bands
python3 hud.py aguiar story test       # 6-keyframe contact sheet + s/frame
timeout 280 python3 hud.py aguiar story 0 300; timeout 280 python3 hud.py aguiar story 300 600     # ~0.16 s/frame
printf "file seg_shomen-aguiar-convocatoria-story_0000.mp4\nfile seg_shomen-aguiar-convocatoria-story_0300.mp4\n" > list.txt
ffmpeg -y -f concat -i list.txt -c:v libx264 -preset fast -b:v 9M -maxrate 13M -bufsize 18M -pix_fmt yuv420p -profile:v high -r 30 -movflags +faststart out.mp4
# squares: one segment `0 600` (~0.07 s/frame), encode at -b:v 8M -maxrate 11M -bufsize 16M
```

Args: `<aguiar|goncalves> <story|square> <still|test|f0 f1>`. New athlete → add a CFG entry in `layouts.py` (photo, mask, crop bbox, key/alt colour, hero word, category) and a cut script. Never nest a heredoc inside a heredoc when pasting these (the runbook above uses `python3 -c` for that reason).

## Design deltas vs v1 (all in `layouts.py`)
- Palette: RED `#FF2A50` (brand) + GREEN `#22E080` + YELLOW `#FFD23F` micro-accents (Portugal). One key colour per athlete (Leonor red, André green), alt colour on the category container, yellow on the hairline slash, crosshair centre, tricolour bar tail, footer mini-slash and the blinking last status cell.
- New HUD library: arc gauge around the crosshair (key arc sweeps, outer ring rotates, alt segment, 12 ticks), `STATUS // CONVOCATÓRIA` segmented cells + `100% // CONFIRMADO` readout, tricolour bar (40 / 55.5 / 4.5 green / red / yellow), barcode strip + ID label, dot matrix, scrim band behind a horizontal hero word over the photo, photo-zone reticle brackets. No brackets around the logo.
- Animation: athlete scan-reveal (key-colour line sweeps down, rows appear behind it), per-glyph cascade on hero + name, hero light sweep, full-frame flash + 0.3 s micro-shake when the hero lands, status cells fill one by one, gauge sweep, card wipe + light sweep, cheer grows in with bloom; ambient = zoom, glow pulse, slash drift, crosshair Lissajous, ruler scroll, digit jitter, 5 s scan line, cheer pulses at 9 / 13 / 17 s.
- Athlete edge handling: `side={l,r,y0,y1}` dissolves frame-cut gi edges (Leonor's portrait fills its frame); `edge_r` fades the canvas edge (André's right glove).

---
