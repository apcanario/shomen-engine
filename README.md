# shomen-engine

Rendering engine, locked design specs and fonts for Shōmen social content. Lives on GitHub so the Claude **Karate** project can fetch it on demand instead of carrying ~130 KB of code in project knowledge on every message.

```
setup.sh              stage fonts + one engine into /home/claude   →  bash setup.sh v2
fonts/                Tomorrow Light→Black (+ italics), Geist Mono — OFL
specs/
  hud-spec.md         HUD system v1.4 — tokens, element library, layouts, photo pipeline, animation timeline, FX pass (opt-in)
  hud-v2-deltas.md    HUD v2 — Seleção palette, new element library, animation deltas, runbook
  swiss-spec.md       Swiss-grid system v1.1 — season recaps, light + dark grunge
engine/
  v1-hud/             cut.py · vid.py · compose_still.py · runbook.sh   — HOJE / AMANHÃ event-day stories
  v2-hud/             logo.py · cut_*.py · hud.py · layouts.py · runbook.sh — call-ups / national team / results, 4 deliverables per athlete
```

## Use from the Karate project

```bash
git clone --depth 1 https://github.com/apcanario/shomen-engine /home/claude/shomen
bash /home/claude/shomen/setup.sh v2      # or v1
```

Then follow `engine/<v>-hud/runbook.sh`. Read only the spec the request needs (`shomen-brand.md` in the project has the routing table).

## Rules the code enforces

- Tomorrow weights Light (300) → Black (900) only. `T()` / `F()` helpers reject Thin and ExtraLight.
- Two-pass compositing: graphics → FX → text + logo. FX can never touch text, the logo or the athlete's face.
- FX flags (`FX_VHS`, `FX_RAIN`, `FX_GLITCH`) ship **False**. Flip only when the request says so.
- Fonts are pre-converted TTFs; no npm/fonttools step needed. Scripts look in `/home/claude/fonts/` (Tomorrow) and the sandbox's bundled Geist Mono.

## Updating

When a build changes the engine (new layout, new helper, new athlete CFG), commit the changed `.py` and bump the spec's version line. Keep the specs as the source of truth for *why*; keep the code as the source of truth for *how*.
