#!/usr/bin/env bash
# Shōmen engine bootstrap — stages fonts + one engine into /home/claude so the scripts run unmodified.
# usage: bash setup.sh v2   (v2 = HUD v2: call-ups / national team / results, 4 deliverables per athlete)
#        bash setup.sh v1   (v1 = HUD v1: HOJE / AMANHÃ event-day stories, glitch still)
set -e
R="$(cd "$(dirname "$0")" && pwd)"
V="${1:-v2}"
mkdir -p /home/claude/fonts
cp -n "$R"/fonts/*.ttf /home/claude/fonts/ 2>/dev/null || cp "$R"/fonts/*.ttf /home/claude/fonts/
cp "$R"/engine/${V}-hud/*.py /home/claude/
python3 - <<'PY'
import importlib.util, sys
missing=[m for m in ("cv2","numpy","PIL") if importlib.util.find_spec(m) is None]
print("python deps:", "ok" if not missing else "MISSING "+" ".join(missing))
PY
command -v ffmpeg >/dev/null && echo "ffmpeg: ok" || echo "ffmpeg: MISSING"
echo "fonts: $(ls /home/claude/fonts/Tomorrow-*.ttf | wc -l) Tomorrow + $(ls /home/claude/fonts/GeistMono-*.ttf | wc -l) Geist Mono in /home/claude/fonts"
echo "engine: ${V}-hud staged in /home/claude ($(ls "$R"/engine/${V}-hud/*.py | xargs -n1 basename | tr '\n' ' '))"
echo "specs: $R/specs/ (hud-spec.md · hud-v2-deltas.md · swiss-spec.md)"
