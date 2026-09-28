# Shōmen — Glitch Post Engine (reference code)

**Purpose:** Working Python for the animated HUD story defined in `shomen-glitch-post.md` (variant R — "LIVE"). Copy the three scripts out of this file into `/home/claude/`, edit the CONFIG block, run. Don't rewrite from scratch. Project knowledge can't hold `.py`/`.ttf`, hence code-in-markdown.

**Storage:** Warm. **Version:** 1.3 — 18 Sep 2026 (type scale rebalanced: micro-labels 18, location 34, tab 22 · HOJE 150, cheer 88, hashtag 40; two-pass compositing; opt-in FX flags; `compose_still.py` added; HOJE text glitch removed; weight floor Light 300). Last verified: Leonor Gonçalves HOJE, 20 s, 600 frames.

---

## Runbook

```bash
# 0. inputs: logo PNG + athlete photo in /mnt/user-data/uploads/ (PDF photo → pdfimages -png file.pdf leo)
# 1. fonts (needs network egress: package managers) — only Light→Black are converted; Thin/ExtraLight are banned by spec §3.2
cd /home/claude && mkdir -p fonts && npm pack @fontsource/tomorrow >/dev/null && tar xf fontsource-tomorrow-*.tgz
pip install fonttools brotli --break-system-packages -q
python3 - <<'PY'
from fontTools.ttLib import TTFont
W={300:'Light',400:'Regular',500:'Medium',600:'SemiBold',700:'Bold',800:'ExtraBold',900:'Black'}
for n,name in W.items():
    f=TTFont(f'package/files/tomorrow-latin-{n}-normal.woff2'); f.flavor=None; f.save(f'fonts/Tomorrow-{name}.ttf')
PY
# 2. extract scripts from this file (or paste), then:
python3 cut.py                      # → leo_mask.png + leo_prev.jpg  (VIEW the preview before going on)
python3 vid.py test                 # → vid_test.png, 4 keyframes (0.7 / 2.2 / 8.1 / 19.97 s). stderr prints "hero text ends at y=" (≤1600) and any font FALLBACK
# 3. render in 3 commands (300 s limit per command; ~0.45 s/frame)
timeout 285 python3 vid.py 0 200
timeout 285 python3 vid.py 200 400
timeout 285 python3 vid.py 400 600
# 4. final encode
printf "file seg_0000.mp4\nfile seg_0200.mp4\nfile seg_0400.mp4\n" > list.txt
timeout 290 ffmpeg -y -loglevel error -f concat -i list.txt -c:v libx264 -preset fast -b:v 9M -maxrate 13M -bufsize 18M \
  -pix_fmt yuv420p -profile:v high -r 30 -movflags +faststart /mnt/user-data/outputs/shomen-<athlete>-<WHEN>-story.mp4
# 4b. still (optional): python3 compose_still.py → 2× PNG + qa.png
# 5. verify: ffprobe duration/size/fps + pull 3 frames (2.0 s, 8.03 s glitch, 19.5 s) and view them
```

**FX (glitch / VHS / matrix rain) — OFF by default.** Spec §8.4. Flip `FX_VHS` / `FX_RAIN` in `vid.py` CONFIG or `FX_GLITCH` at the top of `compose_still.py` **only when Pedro asks for it in the request**. With FX on: render in 2 segments of 300 (`vid.py 0 300`, `300 600`, ~0.26 s/frame), final encode at `-b:v 11M -maxrate 15M -bufsize 22M`, suffix the output `-vhs` / `-glitch`. `frame()` is two-pass — graphics → `vhs()` → text + logo — so FX can't reach text. **Any new text layer goes in PASS 2; any layer mixing shapes and text must be split** (see `tab`/`tabt`, `foot`/`foott`).

**Adapting:**
- New athlete → new `PHOTO`, redo GrabCut boxes in `cut.py` from a gridded preview (spec §6), update `PHOTO_CROP` to the mask bbox (+10 px).
- Text → CONFIG block only. `fit()` auto-shrinks hero, name, event, category and cheer to their slots.
- Blue-key / AMANHÃ, mirrored layout, 1:1 → restructure the layer block + `frame()` per spec §5 and §8.2 deltas; the `Ctx` / `comp` / `mk` machinery stays.
- Static still from the same layout → `Image.fromarray(frame(599))` is 1×; for a 2× still use the compose pattern in spec §7.
- If stderr shows `FALLBACK Work Sans`, the Tomorrow TTFs weren't found in `/home/claude/fonts` — fix before the full render, or say so on delivery.

---
