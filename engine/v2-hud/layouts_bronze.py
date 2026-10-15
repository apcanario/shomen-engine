"""Leonor — bronze-medal bout, WKF Cadet/Junior/U21 Worlds, Bielsko-Biała, Sat 17 Oct 2026.
Palette (Pedro, 15 Oct): red dominant > green > gold highlights; BRONZE word in bronze. Glitch FX on (graphics + photo only).
Story = variant C (slashes TR, logo TL, status TR, vertical BRONZE right strip, 1-line name, highlight bar, Seleção left / cheer right).
Square = variant SQ-C' (logo TR, hero stack TL, athlete right, slashes bottom-right, card, hash left / cheer right).
"""
import math, numpy as np, cv2
import hud, layouts
from hud import *
from layouts import A, drift, sdrift, tricolour, cells, barcode, dotmatrix, add_common_dynamics, top_slashes, label_stack, logo, status_block, underline, cheer_amb, COMMON
from PIL import Image, ImageDraw

BRONZE = (200, 134, 74)
GOLD = YELLOW
COMMON.update(dict(event='WKF CADET, JUNIOR & U21 WORLD CHAMPIONSHIPS', loc='BIELSKO-BIAŁA 2026', date='SÁBADO · 17 OUT', where='BIELSKO-BIAŁA',
                   cheer="LET'S GO!", hash='#TEAMSHOMEN', disc='KUMITE',
                   l1='SHM // BRONZE MEDAL BOUT', l2='REF. WCH-POL-26 / KUMITE', l3='SELEÇÃO NACIONAL — TEAM SHOMEN', desc='ATLETA // SELEÇÃO NACIONAL PORTUGAL',
                   sel='SELEÇÃO NACIONAL // PORTUGAL', status='STATUS // BRONZE MEDAL BOUT', conf='CONFIRMADO', standby='LIVE // BIELSKO-BIAŁA · 17.10.2026',
                   foot='SHOMEN © 2026', coord=(49.8224, 19.0584)))
layouts.COMMON = COMMON
CFG = {
 'leonor_bronze': dict(first='LEONOR ', last='GONÇALVES', hero='BRONZE', cat='JUNIOR -53 KG', key=RED, alt=GREEN,
                       photo='/home/claude/leo_src.jpg', mask='/home/claude/leo_mask.png', crop=(1040, 1960, 690, 1200),
                       caps='BRONZE', probe='BRONZE'),
}
import os
FX_ON = os.environ.get('SHM_FX', '1') == '1'
W_FIRST = 'Regular' if FX_ON else 'Light'

# ---------------- FX: glitch (slice displacement + RGB split, scanlines) — graphics & photo only; face protected ----------------
def make_fx(post, face, zones, bursts, still_bands, excl):
    """face=(cx,cy,rx,ry) 1x; zones=[(lo,hi)] 1x y-ranges for video bands; still_bands=[(y,h,xa,xb,shift,split)] 1x"""
    W1, H1 = post.W1, post.H1
    def fx(fr, i, t, still):
        o = hud.OS; H, W = fr.shape[:2]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy, rx, ry = face
        FACE = np.clip(1.6 - np.sqrt(((xx - cx * o) / (rx * o)) ** 2 + ((yy - cy * o) / (ry * o)) ** 2) * 1.6, 0, 1)[..., None]
        clean = fr.copy()
        def band(y, h, shift, split, xa=0, xb=None):
            Y0, Y1 = max(0, int(y * o)), min(H, int((y + h) * o)); XA, XB = int(xa * o), int((xb if xb is not None else W1) * o)
            if Y1 <= Y0: return
            src = np.roll(clean[Y0:Y1], int(shift * o), axis=1); out = src.copy()
            out[..., 0] = np.roll(src[..., 0], int(split * o), axis=1); out[..., 2] = np.roll(src[..., 2], -int(split * o), axis=1)
            fr[Y0:Y1, XA:XB] = out[:, XA:XB]
        if still:
            rg = np.random.default_rng(7)
            for b in still_bands: band(*b)
            # corruption ticks: red / green / gold / white in empty zones
            n = 0
            while n < 14:
                y = int(rg.integers(20, H1 - 30)); x = int(rg.integers(0, W1 - 240)); wd = int(rg.integers(30, 220)); ht = int(rg.choice([2, 3, 4, 8]))
                if any(x < ex1 and x + wd > ex0 and y < ey1 and y + ht > ey0 for ex0, ey0, ex1, ey1 in excl): continue
                col = [RED, RED, GREEN, GOLD, WHITE][int(rg.integers(0, 5))]; a = float(rg.uniform(0.35, 0.85))
                reg = fr[int(y * o):int((y + ht) * o), int(x * o):int((x + wd) * o)]; reg[:] = reg * (1 - a) + np.array(col, np.float32) / 255. * a; n += 1
            sl = np.ones(H, np.float32); sl[::4] = 0.93; sl[1::4] = 0.965; fr *= sl[:, None, None]
            fr[:] = fr * (1 - FACE) + clean * FACE
            return fr
        rg = np.random.default_rng(1000 + i); hit = False
        inb = any(a_ <= t < b_ for a_, b_ in bursts)
        n = int(rg.integers(4, 9)) if inb else (1 if rg.random() < 0.14 else 0)
        if t > DUR - 1.5: n = 0
        for _ in range(n):
            lo, hi = zones[int(rg.integers(0, len(zones)))]
            h = int(rg.integers(3, 54 if inb else 10)); y = int(rg.integers(lo, max(lo + 1, hi - h)))
            band(y, h, int(rg.integers(-90, 90)), int(rg.integers(3, 12))); hit = True
        if hit:
            fr[:] = fr * (1 - FACE) + clean * FACE
            # RGB split on the whole frame during bursts (graphics + photo, face already restored above is re-split lightly)
            k = int(rg.integers(2, 5)) * o
            fr[..., 0] = np.roll(fr[..., 0], k, axis=1); fr[..., 2] = np.roll(fr[..., 2], -k, axis=1)
            fr[:] = fr * (1 - FACE * 0.7) + clean * FACE * 0.7
        sl = np.ones(H, np.float32); sl[::2] = 0.92; fr *= sl[:, None, None] * (1 + (0.02 * math.sin(t * 37) if inb else 0))
        return fr
    post.fx = fx

# ---------------- STORY C ----------------
def story_C(post):
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    post.glows = [(1080 * 0.95, 1920 * 0.06, 1080 * 0.95, KEY, 0.32, 4.0, 0), (1080 * 0.02, 1920 * 0.97, 1080 * 1.0, ALT, 0.20, 5.0, 1.3), (1080 * 0.9, 1920 * 0.58, 1080 * 0.45, BRONZE, 0.16, 6.0, 2.1)]
    top_slashes(post, mirror=False)
    label_stack(post, 64, 'l')
    logo(post, 84, 284, 250)
    cs = status_block(post, 1016, 300, 'r', t0=2.2)
    post.athlete(cfg['photo'], cfg['mask'], cfg['crop'], 1.32, 468, 334, (830, 935), reveal=(1.0, 2.5), anchor_face=(0.5, 0.08))
    add_common_dynamics(post, (104, 700), gauge_t=(1.5, 2.9), ruler=None, cellspec=cs, coord_xy=(64, 780))
    post.mk('ret1', lambda c: c.bracket(790, 380, 26, 'tr', (255, 255, 255, 150), 2), A(1.4, 2.0, 'slide', dx=30, dy=-30))
    post.mk('ret2', lambda c: c.bracket(180, 900, 26, 'bl', (255, 255, 255, 150), 2), A(1.5, 2.1, 'slide', dx=-30, dy=30))
    # ---- vertical h2: CAMPEONATO DO MUNDO (gold), right strip ----
    VWORD = 'CAMPEONATO DO MUNDO'
    fv, vsz = fit('Black', VWORD, 72, 840, tr=-1); bb = fv.getbbox('CAMPEONATO'); wlen = twidth(fv, VWORD, -1); cap = (bb[3] - bb[1]) / S
    VX1 = 1016; VY1 = 1420; VY0 = VY1 - wlen
    def vword(c):
        im = Image.new('RGBA', (P(wlen + 10), P(cap + 10)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 0
        for ch in VWORD: d.text((x, -bb[1]), ch, font=fv, fill=GOLD); x += fv.getlength(ch) - 1 * S
        im = im.rotate(90, expand=True); c.img.alpha_composite(im, (P(VX1 - cap - 10), P(VY0)))
    def vword_amb(t):
        sc = 1.0
        for p0 in (6.6, 10.7, 13.5, 16.2):
            if p0 <= t < p0 + 0.5: sc = 1 + 0.03 * math.sin(math.pi * (t - p0) / 0.5)
        return 0, 0, 1, sc
    post.mk('vword', vword, A(3.9, 4.7, 'wipe', dir='bt'), text=True, anchor=(0.5, 0.5), amb=vword_amb)
    post.mk('vrule', lambda c: c.rect(VX1 - cap - 28, VY0, VX1 - cap - 22, VY1, fill=KEY), A(4.1, 4.8, 'wipe', dir='bt'))
    def vtri(c):
        x = VX1 - cap - 40; h = wlen
        c.rect(x, VY0, x + 4, VY0 + h * 0.40, fill=GREEN); c.rect(x, VY0 + h * 0.40, x + 4, VY0 + h * 0.955, fill=RED); c.rect(x, VY0 + h * 0.955, x + 4, VY0 + h, fill=GOLD)
    post.mk('vtri', vtri, A(4.4, 5.1, 'wipe', dir='bt'))
    post.mk('vtag', lambda c: c.text((VX1, VY0 - 34), 'WCH-POL-26 // 17.10.2026', T('Medium', 15), GOLD, tr=3, anchor='r'), A(5.0, 5.5), text=True)
    # light sweep along the vertical word (additive band, safe on text)
    def sweep(d, t, still):
        if still or not (4.9 <= t <= 5.7): return
        o = hud.OS; ph = (t - 4.9) / 0.8; y = VY1 - ph * wlen
        for k in range(-3, 4):
            d.line([((VX1 - cap - 10) * o, (y + k * 3) * o), (VX1 * o, (y + k * 3 - 40) * o)], fill=(255, 255, 255, int(70 * (1 - abs(k) / 4))), width=max(1, int(2 * o)))
    post.dynamic(sweep)
    XR = VX1 - cap - 64   # right edge of the text column
    # ---- hero stack: DISPUTA A / MEDALHA DE / BRONZE (horizontal, bronze) ----
    post.mk('pre', lambda c: c.text((64, 896), 'DISPUTA A', T('Bold', 60), WHITE, tr=3), A(2.2, 2.7, 'slidewipe', dx=-60, dir='lr'), text=True)
    fM = T('Black', 88); capM = (fM.getbbox('HEN')[3] - fM.getbbox('HEN')[1]) / S
    MY = 972; post.letters('med', 64, MY - fM.getbbox('MEDALHA')[1] / S, 'MEDALHA DE', fM, WHITE, t0=2.35, step=0.04, dur=0.45, kind='rise', dy=50)
    mb = MY + capM
    fh, hsz = fit('Black', cfg['hero'], 150, XR - 64); bbh = fh.getbbox(cfg['probe']); capH = (bbh[3] - bbh[1]) / S
    HY = mb + 16; hw = post.letters('hero', 64, HY - bbh[1] / S, cfg['hero'], fh, BRONZE, t0=2.7, step=0.05, dur=0.45, kind='rise', dy=60)
    post.flash_t = (3.2, 0.4); cb = HY + capH
    post.mk('cline', lambda c: c.rect(64, cb + 16, 64 + hw, cb + 20, fill=KEY), A(3.4, 4.0, 'wipe', dir='lr'))
    # hero light sweep across BRONZE
    def hsweep(d, t, still):
        if still or not (3.3 <= t <= 4.0): return
        o = hud.OS; ph = (t - 3.3) / 0.7; x = 64 + ph * hw
        for k in range(-3, 4):
            d.line([((x + k * 3) * o, HY * o), ((x + k * 3 + 40) * o, cb * o)], fill=(255, 255, 255, int(70 * (1 - abs(k) / 4))), width=max(1, int(2 * o)))
    post.dynamic(hsweep)
    csz = vsz
    # ---- date (red) + name (one line) ----
    fD = T('Bold', 40); DY = cb + 30
    post.mk('date', lambda c: c.text((64, DY), COMMON['date'], fD, KEY, tr=2), A(4.5, 5.0, 'slidewipe', dx=-60, dir='lr'), text=True)
    db = DY + (fD.getbbox('HEN')[3]) / S
    sz = 60
    while twidth(T(W_FIRST, sz), cfg['first']) + twidth(T('Black', sz), cfg['last']) > XR - 64: sz -= 1
    ft1, ft2 = T(W_FIRST, sz), T('Black', sz); TY = db + 12
    w1 = post.letters('t1', 64, TY, cfg['first'], ft1, WHITE, t0=4.8, step=0.04, dur=0.4, kind='rise', dy=40)
    post.letters('t2', 64 + w1, TY, cfg['last'], ft2, KEY, t0=5.0, step=0.04, dur=0.4, kind='rise', dy=40)
    ny = TY + ft2.getbbox('HEN')[3] / S
    post.mk('desc', lambda c: c.text((64, ny + 14), COMMON['desc'], T('Medium', 18), GREY, tr=3), A(5.4, 5.9), text=True)
    # ---- card: event + loc, highlight bar with CATEGORIA tab ----
    X0, Y0, X1, Y1 = 64, ny + 40, XR, ny + 40 + 156
    def _card(c):
        c.chamfer(X0, Y0, X1, Y1, 26, fill=PANEL + (217,), outline=(255, 255, 255, 38), w=1)
        mid = Y0 + (Y1 - Y0) * 0.45; c.rect(X0, Y0, X0 + 6, mid, fill=KEY); c.rect(X0, mid, X0 + 6, Y1 - 26, fill=ALT)
        for k in range(0, 100, 8): c.line([(X1 - 36 - k, Y0 + 1), (X1 - 36 - k - 30, Y0 + 31)], (255, 255, 255, 14), 1)
    post.mk('card', _card, A(5.5, 6.2, 'wipe', dir='lr')); post.card_rect = (X0, Y0, X1, Y1)
    post.mk('cbr', lambda c: c.bracket(X1 + 14, Y1 + 14, 22, 'br', (255, 255, 255, 170), 2), A(6.0, 6.5, 'slide', dx=30, dy=30))
    ix = X0 + 36
    fev, _ = fit('Bold', COMMON['event'], 34, X1 - ix - 36)
    post.mk('ev', lambda c: c.text((ix, Y0 + 16), COMMON['event'], fev, WHITE), A(5.9, 6.5, 'slide', dx=-40), text=True)
    def _loc(c):
        c.text((ix, Y0 + 54), COMMON['loc'] + ' // ' + COMMON['date'], T('Regular', 24), GREY, tr=2); c.text((X1 - 30, Y0 + 18), '01 / 01', MONO(13, True), DIM + (255,), tr=3, anchor='r')
    post.mk('loc', _loc, A(6.1, 6.7, 'slide', dx=40), text=True)
    HX0, HY0, HX1, HY1 = ix, Y0 + 92, X1 - 30, Y0 + 142; tabw = 210
    post.mk('hbar', lambda c: c.rect(HX0, HY0, HX1, HY1, fill=ALT + (26,), outline=ALT + (255,), w=1), A(6.3, 6.9, 'wipe', dir='lr'))
    post.mk('tab', lambda c: c.poly([(HX0, HY0), (HX0 + tabw, HY0), (HX0 + tabw - 26, HY1), (HX0, HY1)], fill=ALT + (255,)), A(6.5, 7.1, 'slide', dx=-60))
    def _tabt(c):
        fm = T('Bold', 20); bb_ = fm.getbbox('CATEGORIA'); c.text((HX0 + 18, (HY0 + HY1) / 2 - (bb_[1] + bb_[3]) / 2 / S), 'CATEGORIA', fm, (9, 10, 14), tr=3)
    post.mk('tabt', _tabt, A(6.5, 7.1, 'slide', dx=-60), text=True)
    def _cat(c):
        fk, _ = fit('Bold', cfg['cat'], 38, (HX1 - 20) - (HX0 + tabw + 120)); bb_ = fk.getbbox(cfg['cat']); c.text((HX1 - 20, (HY0 + HY1) / 2 - (bb_[1] + bb_[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='r')
    post.mk('cat', _cat, A(6.8, 7.4, 'slide', dx=60), text=True)
    post.mk('kum', lambda c: c.text((HX0 + tabw + 14, (HY0 + HY1) / 2 - 10), COMMON['disc'], T('Medium', 17), ALT, tr=3), A(6.9, 7.3), text=True)
    # ---- bottom row: Seleção (left, green) · cheer + hash (right) ----
    SY = Y1 + 22; szs = 42
    f1, f2 = T(W_FIRST, szs), T('Black', szs); caps = (f2.getbbox('HEN')[3] - f2.getbbox('HEN')[1]) / S
    y1 = SY - f1.getbbox('SELE')[1] / S; y2 = SY + caps + 12 - f2.getbbox('PORTUGAL')[1] / S
    post.mk('sel1', lambda c: c.text((64, y1), 'SELEÇÃO NACIONAL', f1, WHITE, tr=1), A(7.2, 7.8, 'slidewipe', dx=-60, dir='lr'), text=True)
    post.letters('sel2', 64, y2, 'PORTUGAL', f2, ALT, t0=7.4, step=0.05, dur=0.42, kind='rise', dy=34)
    base = SY + caps + 12 + caps
    post.mk('seltri', lambda c: tricolour(c, 64, base + 16, twidth(f2, 'PORTUGAL'), 4, anchor='l'), A(7.9, 8.4, 'wipe', dir='lr'))
    ff, _ = fit('Black', COMMON['cheer'], 84, 420); bbF = ff.getbbox(COMMON['cheer'])
    post.mk('forca', lambda c: c.text((1016, SY - 4 - bbF[1] / S), COMMON['cheer'], ff, WHITE, anchor='r'), A(7.6, 8.3, 'pop', s0=0.84, over=1.7, flash=True), text=True, anchor=(1.0, 0.8), amb=cheer_amb)
    fhh = T('SemiBold', 40); hb_ = fhh.getbbox(COMMON['hash'])
    post.mk('hash', lambda c: c.text((1016, base + 6 - hb_[3] / S), COMMON['hash'], fhh, KEY, anchor='r'), A(7.5, 8.1, 'slidewipe', dx=80, dir='rl'), text=True)
    layouts.bottom_decor_story(post, mirror=False)
    post.notes.append(f'story C: bronze {hsz}pt, vertical campeonato {csz}pt y {VY0:.0f}-{VY1:.0f}, name {sz}pt, card y {Y0:.0f}-{Y1:.0f}, selecao baseline y={base:.0f} (<=1600)')
    if FX_ON: make_fx(post, face=(468, 600, 150, 190),
            zones=[(0, 430), (820, 940), (1000, 1210), (1620, 1900)],
            bursts=[(0.35, 1.0), (2.9, 3.15), (6.6, 6.8), (8.3, 8.5), (10.7, 10.9), (13.5, 13.7), (16.2, 16.4), (18.0, 18.2)],
            still_bands=[(40, 10, 46, 5), (66, 4, -70, 8), (212, 14, -38, 6), (300, 6, 60, 8, 660, 1080), (420, 5, 44, 7, 0, 300), (848, 14, -24, 6), (905, 5, 52, 9), (940, 18, 14, 4),
                         (1100, 4, 64, 8, 0, 600), (1230, 6, -30, 6, 0, 500), (1648, 16, -56, 7), (1752, 5, 80, 10), (1790, 24, 30, 6), (1880, 8, -44, 8, 0, 780), (1010, 8, 40, 8), (700, 10, 28, 6, 760, 1080), (640, 5, -20, 6, 0, 230)],
            excl=[(300, 430, 640, 800), (64, 270, 360, 520), (0, 940, 900, 1600), (0, 80, 450, 220), (880, 280, 1080, 420)])

# ---------------- SQUARE C ----------------
def square_C(post):
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    post.glows = [(1080 * 0.05, 1080 * 0.06, 1080 * 0.9, KEY, 0.30, 4.0, 0), (1080 * 0.98, 1080 * 0.97, 1080 * 0.95, ALT, 0.20, 5.0, 1.3), (1080 * 0.3, 1080 * 0.18, 1080 * 0.4, BRONZE, 0.14, 6.0, 2.1)]
    # slashes bottom-right, behind the fade zone
    sdir = np.array([k60, -1.0])
    for n, (nm, xt, wd, col, st) in enumerate((('sl1', 1036, 70, KEY, 0.30), ('sl2', 1136, 44, KEY, 0.42), ('sl3', 1004, 5, ALT, 0.55), ('sl4', 984, 2, GOLD, 0.65))):
        post.mk(nm, lambda c, xt=xt, wd=wd, col=col: c.slash(xt, wd, 560, 1180, col, yref=1080), A(st, st + 0.75, 'slide', dx=-sdir[0] * 420, dy=-sdir[1] * 420), amb=sdrift(n, sdir))
    logo(post, 830, 44, 196)
    # hero stack top-left
    post.mk('pre', lambda c: c.text((56, 62), 'DISPUTA A', T('Bold', 40), WHITE, tr=2), A(1.0, 1.5, 'slidewipe', dx=-60, dir='lr'), text=True)
    fM = T('Black', 56); MY = 108; post.letters('med', 56, MY - fM.getbbox('MEDALHA')[1] / S, 'MEDALHA DE', fM, WHITE, t0=1.2, step=0.04, dur=0.4, kind='rise', dy=36)
    fh, hsz = fit('Black', cfg['hero'], 150, 640); bb = fh.getbbox(cfg['probe']); HY = MY + (fM.getbbox('HEN')[3] - fM.getbbox('HEN')[1]) / S + 14
    hw = post.letters('hero', 56, HY - bb[1] / S, cfg['hero'], fh, BRONZE, t0=1.4, step=0.05, dur=0.45, kind='rise', dy=50)
    hb = HY + (bb[3] - bb[1]) / S; post.flash_t = (1.9, 0.3)
    post.mk('heroline', lambda c: c.rect(56, hb + 14, 56 + hw, hb + 18, fill=KEY), A(1.9, 2.4, 'wipe', dir='lr'))
    fC, csz = fit('Black', 'CAMPEONATO DO MUNDO', 60, 640, tr=1); capC = (fC.getbbox('HEN')[3] - fC.getbbox('HEN')[1]) / S
    CY = hb + 34; post.letters('cdm', 56, CY - fC.getbbox('CAMPEONATO')[1] / S, 'CAMPEONATO DO MUNDO', fC, GOLD, tr=1, t0=2.0, step=0.035, dur=0.45, kind='rise', dy=40)
    cb = CY + capC
    post.mk('sel', lambda c: c.text((56, cb + 20), 'SELEÇÃO NACIONAL PORTUGAL', T('Bold', 26), ALT, tr=2), A(2.5, 3.0, 'slidewipe', dx=-60, dir='lr'), text=True)
    post.mk('seltri', lambda c: tricolour(c, 56, cb + 58, twidth(T('Bold', 26), 'SELEÇÃO NACIONAL PORTUGAL', 2), 4, anchor='l'), A(2.8, 3.3, 'wipe', dir='lr'))
    # athlete right
    post.athlete(cfg['photo'], cfg['mask'], cfg['crop'], 0.86, 790, 123, (600, 720), reveal=(1.0, 2.3), anchor_face=(0.5, 0.08), edge_r=0.06)
    post.mk('stlab', lambda c: c.text((56, 440), COMMON['status'], T('Medium', 13), GREY, tr=3), A(2.9, 3.4, 'wipe', dir='lr'), text=True)
    add_common_dynamics(post, (120, 600), gauge_t=(1.4, 2.6), ruler=None, cellspec=(56, 466, 8, 'l', 3.2), coord_xy=(230, 540))
    post.mk('ret1', lambda c: c.bracket(1024, 236, 22, 'tr', (255, 255, 255, 150), 2), A(1.5, 2.1, 'slide', dx=30, dy=-30))
    post.mk('bcode', lambda c: (barcode(c, 230, 616, 150, 16, seed=3), c.text((230, 638), 'ID 26-WCH-POL // 17.10.2026', MONO(11), DIM + (255,))), A(3.4, 4.0))
    # name one line
    sz = 92
    while twidth(T(W_FIRST, sz), cfg['first']) + twidth(T('Black', sz), cfg['last']) > 968: sz -= 1
    ft1, ft2 = T(W_FIRST, sz), T('Black', sz); TY = 712
    w1 = post.letters('t1', 56, TY, cfg['first'], ft1, WHITE, t0=2.6, step=0.04, dur=0.4, kind='rise', dy=36)
    post.letters('t2', 56 + w1, TY, cfg['last'], ft2, KEY, t0=2.85, step=0.04, dur=0.4, kind='rise', dy=36)
    uy = TY + ft2.getbbox('HEN')[3] / S + 20
    underline(post, uy, 1024 - 380, 1024, desc_side='l', t0=3.3)
    X0, Y0, X1, Y1 = 56, uy + 24, 1024, uy + 24 + 122
    def _card(c):
        c.chamfer(X0, Y0, X1, Y1, 22, fill=PANEL + (217,), outline=(255, 255, 255, 38), w=1)
        mid = Y0 + (Y1 - Y0) * 0.45; c.rect(X0, Y0, X0 + 6, mid, fill=KEY); c.rect(X0, mid, X0 + 6, Y1 - 22, fill=ALT)
    post.mk('card', _card, A(3.5, 4.1, 'wipe', dir='lr')); post.card_rect = (X0, Y0, X1, Y1)
    ix = X0 + 34
    fev, _ = fit('Bold', COMMON['event'], 34, 600)
    post.mk('ev', lambda c: c.text((ix, Y0 + 16), COMMON['event'], fev, WHITE), A(3.9, 4.4, 'slide', dx=-40), text=True)
    post.mk('date', lambda c: c.text((ix, Y0 + 58), COMMON['date'], T('Bold', 30), KEY, tr=2), A(4.1, 4.6, 'slide', dx=-40), text=True)
    post.mk('loc', lambda c: c.text((ix + twidth(T('Bold', 30), COMMON['date'], 2) + 20, Y0 + 66), '// ' + COMMON['loc'], T('Regular', 19), GREY, tr=1), A(4.2, 4.7, 'slide', dx=-40), text=True)
    CX0, CY0, CX1, CY1 = X1 - 34 - 290, Y0 + 32, X1 - 34, Y0 + 32 + 62
    post.mk('chipl', lambda c: c.text((CX1, CY0 - 22), 'CATEGORIA // ' + COMMON['disc'], T('Medium', 13), GREY, tr=3, anchor='r'), A(4.3, 4.7), text=True)
    post.mk('chip', lambda c: c.chamfer(CX0, CY0, CX1, CY1, 12, fill=ALT + (26,), outline=ALT + (255,), w=1), A(4.4, 5.0, 'wipe', dir='lr'))
    def _chipt(c):
        fk, _ = fit('Bold', cfg['cat'], 36, 260); bb_ = fk.getbbox(cfg['cat']); c.text(((CX0 + CX1) / 2, (CY0 + CY1) / 2 - (bb_[1] + bb_[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='c')
    post.mk('chipt', _chipt, A(4.6, 5.2, 'pop', s0=1.25), text=True)
    base = layouts.cheer_row(post, Y1 + 16, left='hash', t0=5.0, cheer_sz=62, hash_sz=34, X0=56, X1=1024)
    post.mk('foott', lambda c: c.text((56, 1046), COMMON['foot'], T('Regular', 12), DIM, tr=4), A(5.6, 6.2), text=True)
    post.notes.append(f'square C: hero {hsz}pt, campeonato {csz}pt, name {sz}pt, cheer baseline y={base:.0f}')
    if FX_ON: make_fx(post, face=(790, 300, 120, 140),
            zones=[(0, 40), (520, 700), (780, 860), (1000, 1080)],
            bursts=[(0.35, 1.0), (1.9, 2.1), (6.6, 6.8), (10.7, 10.9), (14.5, 14.7), (17.8, 18.0)],
            still_bands=[(30, 6, 40, 6, 0, 560), (470, 5, -60, 8, 0, 560), (520, 12, 46, 7, 0, 560), (600, 18, 28, 5), (690, 10, 36, 6), (805, 5, 60, 8), (830, 12, -22, 5), (1000, 6, -40, 7), (1030, 14, 54, 8), (1062, 5, -70, 9), (330, 4, -26, 5, 0, 560)],
            excl=[(580, 160, 1050, 720), (800, 30, 1060, 240), (40, 40, 700, 350), (40, 700, 1040, 1000), (40, 1000, 400, 1060), (560, 1000, 1040, 1060)])

def build(cfgname, fmt):
    cfg = dict(CFG[cfgname]); post = Post(cfg, fmt)
    (story_C if fmt == 'story' else square_C)(post)
    for n in post.notes: print(n, file=sys.stderr)
    return post
