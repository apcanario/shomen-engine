"""PARABÉNS PORTUGAL — compact futurist HUD, Swiss grid. Static 3:4 (1080x1440), no photo.
Each athlete = a row of three tiles/buttons (name · category · result): one cut corner, fill = medal colour at ~5%,
stroke = medal colour at ~80%, 2 px. Glitch on graphics only (still bands + ticks), text untouched. Grid guides visible.
Pedro, 17 Oct 2026: "HUD futurista mas compacta … tiles/buttons … Grelha. Suíço mas moderno."
"""
import sys, math, numpy as np
import hud, layouts
from hud import *
from layouts import A, tricolour, barcode, dotmatrix, top_slashes, cells, COMMON
from PIL import Image, ImageDraw

SILVER = (198, 204, 214); SILVER_T = (214, 219, 228)     # tile stroke / text
BRONZE = (200, 134, 74);  BRONZE_T = (222, 160, 96)      # bronze text lifted for contrast on the tint
GOLD = YELLOW; LITE = (226, 229, 236)
MEDALS = [
    ('ÍSIS MATOS', ('KUMITE', 'JUNIOR FEMININO · -48 KG'), 'PRATA', SILVER, SILVER_T),
    ('VASCO MATEUS', ('KATA', 'JÚNIOR MASCULINO'), 'PRATA', SILVER, SILVER_T),
    ('DANIEL CIUNTU', ('KUMITE', 'CADETE MASCULINO · +70 KG'), 'PRATA', SILVER, SILVER_T),
    ('MADALENA SANTOS', ('KUMITE', 'CADETE FEMININO · +61 KG'), 'BRONZE', BRONZE, BRONZE_T),
    ('LEONOR GONÇALVES', ('KUMITE', 'JUNIOR FEMININO · -53 KG'), 'BRONZE', BRONZE, BRONZE_T),
]
import os
JOAO = os.environ.get('SHM_JOAO', '1') == '1'
if JOAO: MEDALS.append(('JOÃO VIEIRA', ('KATA', 'MASCULINO U21'), 'BRONZE', BRONZE, BRONZE_T))
NS = sum(1 for m in MEDALS if m[2] == 'PRATA'); NB = sum(1 for m in MEDALS if m[2] == 'BRONZE'); NT = NS + NB
COMMON.update(dict(l1='SHM // PORTUGAL MEDAL TABLE', l2='REF. WCH-POL-26 / BIELSKO-BIAŁA', foot='SHOMEN © 2026'))
layouts.COMMON = COMMON
TINT_A = 13      # ~5 %
STROKE_A = 204   # ~80 %

def lum(c):
    def ch(v):
        v = v / 255.; return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])
def contrast(fg, bg):
    a, b = lum(fg), lum(bg); return (max(a, b) + 0.05) / (min(a, b) + 0.05)
def blend(fg, bg, a):
    return tuple(int(round(bg[i] * (1 - a) + fg[i] * a)) for i in range(3))

class StaticPost(Post):
    def __init__(self, cfg, fmt):
        super().__init__(cfg, fmt); self.W1, self.H1 = 1080, 1440

def tile(c, x0, y0, x1, y1, col, cut=18, fill_a=TINT_A, stroke_a=STROKE_A, corner='tr', w=2):
    """button: rectangle with ONE cut corner, tinted fill, strong stroke"""
    if corner == 'tr': pts = [(x0, y0), (x1 - cut, y0), (x1, y0 + cut), (x1, y1), (x0, y1)]
    elif corner == 'br': pts = [(x0, y0), (x1, y0), (x1, y1 - cut), (x1 - cut, y1), (x0, y1)]
    elif corner == 'bl': pts = [(x0, y0), (x1, y0), (x1, y1), (x0 + cut, y1), (x0, y1 - cut)]
    else: pts = [(x0 + cut, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0 + cut)]
    c.poly(pts, fill=col + (fill_a,), outline=col + (stroke_a,), w=w)

def build():
    post = StaticPost(dict(key=RED, alt=GREEN), 'portrait'); KEY, ALT = RED, GREEN
    post.glows = [(0, 0, 1080 * 0.7, RED, 0.24, 4, 0), (1080, 1440, 1080 * 0.7, GREEN, 0.18, 5, 1)]
    # ---- grid guides (Swiss): 4 columns, hairlines ----
    # ---- header ----
    def _logo(c):
        lg = logo_rgba(P(176)); c.img.alpha_composite(lg, (P(64), P(60)))
    post.mk('logo', _logo, A(0.8, 1.6), text=True)
    post.mk('hd1', lambda c: c.text((1016, 66), COMMON['l1'], T('Bold', 15), WHITE, tr=3, anchor='r'), A(0.6, 1.2), text=True)
    post.mk('hd2', lambda c: c.text((1016, 92), COMMON['l2'], T('Medium', 14), LITE, tr=2.5, anchor='r'), A(0.75, 1.35), text=True)
    post.mk('hd3', lambda c: c.text((1016, 118), 'WKF CADET, JUNIOR & U21 WORLD CHAMPIONSHIPS', T('Medium', 14), LITE, tr=2.5, anchor='r'), A(0.9, 1.5), text=True)
    post.mk('hd4', lambda c: c.text((1016, 144), 'BIELSKO-BIAŁA · POLÓNIA · 14–18 OUT 2026', T('Medium', 14), LITE, tr=2.5, anchor='r'), A(0.9, 1.5), text=True)
    post.mk('stat', lambda c: (cells(c, 1016, 178, 12, 16, 8, 4, KEY, anchor='r'), c.text((1016, 194), '100% // RESULTADOS FINAIS', MONO(12, True), KEY + (255,), anchor='r')), A(1.2, 1.8))
    # ---- hero (compact) ----
    f1 = T('Black', 88); bb1 = f1.getbbox('PARABÉNS'); cap1 = (bb1[3] - bb1[1]) / S
    f2 = T('Black', 104); bb2 = f2.getbbox('PORTUGAL'); cap2 = (bb2[3] - bb2[1]) / S
    HY = 262
    post.mk('h1', lambda c: c.text((64, HY - bb1[1] / S), 'PARABÉNS', f1, WHITE), A(1.4, 1.9), text=True)
    PY = HY + cap1 + 8
    post.mk('h2', lambda c: c.text((64, PY - bb2[1] / S), 'PORTUGAL', f2, KEY), A(1.7, 2.2), text=True)
    pb = PY + cap2
    post.mk('cdm', lambda c: c.text((64, pb + 18), 'CAMPEONATO DO MUNDO', T('Black', 30), GOLD, tr=2), A(2.2, 2.7), text=True)
    post.mk('tri', lambda c: tricolour(c, 1016, pb + 30, 238, 4, anchor='r'), A(2.4, 3.0))
    # ---- 2 x 3 grid: silver column left, bronze column right (+ tally tile in the free slot) ----
    TY = pb + 72
    GAPX, GAPY = 16, 14; CW = (952 - GAPX) // 2; TH = 222
    LX0, RX0 = 64, 64 + CW + GAPX
    post.mk('cols', lambda c: (c.text((LX0, TY), f'PRATA // {NS}', T('Bold', 13), SILVER_T, tr=4), c.rect(LX0, TY + 24, LX0 + CW, TY + 25, fill=SILVER + (120,)),
                               c.text((RX0, TY), f'BRONZE // {NB}', T('Bold', 13), BRONZE_T, tr=4), c.rect(RX0, TY + 24, RX0 + CW, TY + 25, fill=BRONZE + (120,))), A(2.6, 3.1), text=True)
    y = TY + 40; PAD = 22; INNER = CW - 2 * PAD
    fN = T('Bold', 40); fC1 = T('Bold', 20); fC2 = T('Regular', 22); fM = T('Bold', 18)
    def wrap(font, text, maxw, tr=0):
        words = text.split(' '); lines = []; cur = ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if twidth(font, t, tr) <= maxw or not cur: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur); return lines
    checks = []
    sil = [m for m in MEDALS if m[2] == 'PRATA']; bro = [m for m in MEDALS if m[2] == 'BRONZE']
    slots = [(LX0, j, m, i + 1) for j, (i, m) in enumerate([(k, m) for k, m in enumerate(MEDALS) if m[2] == 'PRATA'])] + \
            [(RX0, j, m, i + 1) for j, (i, m) in enumerate([(k, m) for k, m in enumerate(MEDALS) if m[2] == 'BRONZE'])]
    capN = (fN.getbbox('HEN')[3] - fN.getbbox('HEN')[1]) / S
    for x0, j, (name, (d1, d2), medal, col, colt), n in slots:
        yy = y + j * (TH + GAPY); x1 = x0 + CW
        fNn, _ = fit('Bold', name, 40, INNER, floor=34)          # shrink to 34pt before wrapping
        nlines = wrap(fNn, name, INNER); c2lines = wrap(fC2, d2, INNER, 1)
        for ln in nlines: checks.append((f'{name}/name', twidth(fNn, ln), INNER))
        for ln in c2lines: checks.append((f'{name}/cat', twidth(fC2, ln, 1), INNER))
        stack_h = 34 + len(nlines) * (capN + 10) + 22 + 30 + len(c2lines) * 30
        checks.append((f'{name}/height', stack_h, TH - 2 * PAD + 10))
        def tile_fn(c, x0=x0, x1=x1, yy=yy, name=name, d1=d1, d2=d2, medal=medal, col=col, colt=colt, n=n, nlines=nlines, c2lines=c2lines, fN=fNn):
            tile(c, x0, yy, x1, yy + TH, col, corner='tr')
            c.text((x0 + PAD, yy + PAD), f'{n:02d}', MONO(12, True), colt + (255,))
            c.text((x1 - PAD - 8, yy + PAD - 2), medal, fM, colt, tr=3, anchor='r')
            c.rect(x1 - PAD - 8 - 40, yy + PAD + 24, x1 - PAD - 8, yy + PAD + 27, fill=col + (255,))
            ty = yy + PAD + 34
            for ln in nlines:
                c.text((x0 + PAD, ty - fN.getbbox(ln)[1] / S), ln, fN, WHITE); ty += capN + 10
            ty += 10
            c.rect(x0 + PAD, ty, x0 + PAD + 28, ty + 2, fill=col + (160,)); ty += 12
            c.text((x0 + PAD, ty), d1, fC1, colt, tr=3); ty += 30
            for ln in c2lines:
                c.text((x0 + PAD, ty), ln, fC2, WHITE, tr=1); ty += 30
            c.ruler(x1 - PAD - 7 * 6, yy + TH - 16, 8, step=6, h1=4, h2=8, col=col + (170,))
        post.mk(f'tile{n}', tile_fn, A(3.0 + n * 0.15, 3.5 + n * 0.15), text=True)
    if NT < 6:
        yy6 = y + 2 * (TH + GAPY)
        def tally(c):
            tile(c, RX0, yy6, RX0 + CW, yy6 + TH, WHITE, cut=18, fill_a=8, stroke_a=120)
            c.text((RX0 + PAD, yy6 + PAD), 'TOTAL // PORTUGAL', MONO(12, True), LITE + (255,))
            f5 = T('Black', 96); bb5 = f5.getbbox('5')
            c.text((RX0 + PAD, yy6 + PAD + 30 - bb5[1] / S), str(NT), f5, WHITE)
            c.text((RX0 + PAD + twidth(f5, str(NT)) + 16, yy6 + PAD + 44), 'MEDALHAS', T('Bold', 18), GOLD, tr=4)
            c.text((RX0 + PAD + twidth(f5, str(NT)) + 16, yy6 + PAD + 72), 'CAMPEONATO DO MUNDO', T('Regular', 14), LITE, tr=2)
            by = yy6 + TH - PAD - 36
            tile(c, RX0 + PAD, by, RX0 + PAD + 120, by + 36, SILVER, cut=10)
            c.text((RX0 + PAD + 14, by + 6), str(NS), T('Black', 22), SILVER_T); c.text((RX0 + PAD + 36, by + 12), 'PRATA', T('Bold', 12), SILVER_T, tr=3)
            tile(c, RX0 + PAD + 132, by, RX0 + PAD + 262, by + 36, BRONZE, cut=10)
            c.text((RX0 + PAD + 146, by + 6), str(NB), T('Black', 22), BRONZE_T); c.text((RX0 + PAD + 168, by + 12), 'BRONZE', T('Bold', 12), BRONZE_T, tr=3)
        post.mk('tally', tally, A(3.8, 4.3), text=True)
    yb = y + 3 * TH + 2 * GAPY
    bad = [c for c in checks if c[1] > c[2]]
    post.notes.append('overlap check: ' + ('OK' if not bad else 'FAIL ' + str(bad)))
    GB = yb + 108
    def guides(c):
        for x in (64, 64 + CW, 64 + CW + GAPX, 1016):
            c.line([(x, 232), (x, GB)], (255, 255, 255, 26), 1)
        c.line([(64, 232), (1016, 232)], (255, 255, 255, 70), 1); c.line([(64, GB), (1016, GB)], (255, 255, 255, 70), 1)
        for k in range(0, 952, 34): c.line([(64 + k, 232), (64 + k, 232 + (10 if (k // 34) % 7 == 0 else 4))], (255, 255, 255, 120), 1)
    post.mk('guides', guides, A(0.4, 1.0)); post.order1.insert(0, post.order1.pop())
    # ---- footer ----
    post.mk('rulez', lambda c: c.rect(64, yb + 16, 1016, yb + 17, fill=(255, 255, 255, 70)), A(4.2, 4.6))
    fS = T('Bold', 26); selw = twidth(fS, 'SELEÇÃO NACIONAL PORTUGAL', 2)
    post.mk('sel', lambda c: c.text((64, yb + 34), 'SELEÇÃO NACIONAL PORTUGAL', fS, ALT, tr=2), A(4.8, 5.4), text=True)
    post.mk('seltri', lambda c: tricolour(c, 64, yb + 72, selw, 4, anchor='l'), A(5.2, 5.7))
    post.mk('deco', lambda c: (c.text((1016, yb + 36), f'{NT} MEDALHAS // {NS} PRATA · {NB} BRONZE', T('Bold', 15), GOLD, tr=3, anchor='r'), barcode(c, 1016 - 150, yb + 64, 150, 12, seed=3), c.text((1016, yb + 82), 'ID 26-WCH-POL // PT', MONO(11), DIM + (255,), anchor='r')), A(5.0, 5.6), text=True)
    post.mk('foott', lambda c: (c.text((1016, 1408), COMMON['foot'], T('Regular', 12), DIM, tr=4, anchor='r'), c.text((64, 1408), 'RESULTADOS // BIELSKO-BIAŁA · 14–18.10.2026', T('Medium', 12), DIM, tr=3)), A(5.6, 6.2), text=True)
    # ---- glitch: graphics only (pass 1), text drawn after; thin bands + ticks outside text boxes ----
    import layouts_bronze
    excl = [(64, HY, 1016, pb + 60), (64, TY, 1016, yb + 90), (0, 0, 1080, 230)]      # keep ticks off the hero and the tile text zones
    layouts_bronze.make_fx(post, face=(-999, -999, 1, 1), zones=[(0, 230), (1340, 1440)], bursts=[],
        still_bands=[(40, 8, 36, 5), (120, 5, -44, 7, 500, 1080), (204, 12, 22, 5, 0, 420), (int(pb) + 24, 4, 60, 8, 0, 520), (int(y) + 140, 3, -30, 6, 0, 1080),
                     (int(y) + 300, 5, 40, 7, 620, 1080), (int(y) + 452, 3, -26, 5, 0, 640), (int(y) + 560, 4, 34, 6, 300, 1080), (int(yb) + 96, 10, -52, 8, 400, 1080), (1366, 6, -70, 9, 0, 760)],
        excl=excl)
    post.notes.append(f'tiles: rows y {y:.0f}-{yb:.0f}; contrast white/silver-tint {contrast(WHITE, blend(SILVER, BG, TINT_A/255)):.1f}:1, '
                      f'silver text {contrast(SILVER_T, blend(SILVER, BG, TINT_A/255)):.1f}:1, bronze text {contrast(BRONZE_T, blend(BRONZE, BG, TINT_A/255)):.1f}:1, '
                      f'bronze text on 22-tint {contrast(BRONZE_T, blend(BRONZE, BG, 22/255)):.1f}:1')
    return post

if __name__ == '__main__':
    hud.OS = 2
    post = build(); post.prep()
    for n in post.notes: print(n, file=sys.stderr)
    name = f'shomen-portugal-medalhados-worlds2026-tiles-{NT}-glitch'
    hud.render(post, name, 'still')
    Image.open(f'/mnt/user-data/outputs/{name}.png').resize((540, 720), Image.LANCZOS).save(f'/home/claude/qa_tiles{NT}.png')
