"""Leonor — BRONZE MEDAL WON, WKF Cadet/Junior/U21 Worlds, Bielsko-Biała, Sat 17 Oct 2026.
"Window" build (Pedro, 17 Oct): no cut-out — the full photo is the background, the HUD and text are a window onto it.
Photo fills the frame from the top, dissolves into the panel colour through a fluid vertical gradient, text sits on the gradient.
Palette: flag ratio (red > green > gold), BRONZE in bronze. FX off (SHM_FX=1 would enable glitch via layouts_bronze.make_fx).
Story  = variant W-S: slashes TL (mirrored), label stack TR, logo TR, status TL, lean rows (no card panel), Seleção 1 line left, cheer right.
3:4    = variant W-P: slashes TR, logo TL, label stack TL, status TR, stack RIGHT-aligned, vertical CAMPEONATO DO MUNDO on the LEFT strip,
         chamfered card, cheer left / hash right.
"""
import math, os, sys, numpy as np, cv2
import hud, layouts
from hud import *
from layouts import A, sdrift, tricolour, barcode, dotmatrix, add_common_dynamics, top_slashes, label_stack, logo, status_block, cheer_amb, COMMON
from PIL import Image, ImageDraw

BRONZE = (200, 134, 74)
GOLD = YELLOW
COMMON.update(dict(event='WKF CADET, JUNIOR & U21 WORLD CHAMPIONSHIPS', loc='BIELSKO-BIAŁA 2026', date='SÁBADO · 17 OUT', where='BIELSKO-BIAŁA',
                   cheer='PARABÉNS!', hash='#TEAMSHOMEN', disc='KUMITE', place='3.º LUGAR',
                   l1='SHM // WORLD BRONZE MEDALLIST', l2='REF. WCH-POL-26 / KUMITE', l3='SELEÇÃO NACIONAL — TEAM SHOMEN', desc='ATLETA // SELEÇÃO NACIONAL PORTUGAL',
                   sel='SELEÇÃO NACIONAL // PORTUGAL', status='STATUS // MEDALHA DE BRONZE', conf='CONFIRMADO', standby='RESULTADO // BIELSKO-BIAŁA · 17.10.2026',
                   foot='SHOMEN © 2026', coord=(49.8224, 19.0584)))
layouts.COMMON = COMMON
CFG = {
 'leonor_medal': dict(first='LEONOR ', last='GONÇALVES', hero='BRONZE', cat='JUNIOR -53 KG', key=RED, alt=GREEN,
                      photo='/home/claude/leo_src.jpg', caps='BRONZE', probe='BRONZE'),
}
FX_ON = os.environ.get('SHM_FX', '0') == '1'
W_FIRST = 'Regular' if FX_ON else 'Light'

# ---------------- window post: full-bleed photo background with gradient scrim ----------------
class WindowPost(Post):
    def __init__(self, cfg, fmt):
        super().__init__(cfg, fmt)
        if fmt == 'portrait': self.W1, self.H1 = 1080, 1440
        self.ph = None
    def photo(self, path, crop, scale, anchor, scrim, top_scrim=0.42, reveal=(0.25, 1.5), zoom=0.05):
        """crop=(y0,y1,x0,x1) source px; scale = frame px (1x) per source px; anchor=(x,y) frame 1x point held fixed under zoom;
        scrim=((ya,yb,smax),(yc,yd)) 1x: ya->yb ramps to smax, yc->yd ramps to 1.0; top_scrim darkens y 0..260 for the header labels."""
        o = hud.OS
        src = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB).astype(np.float32)
        y0, y1, x0, x1 = crop; src = src[y0:y1, x0:x1]
        sc = scale * o; nw, nh = int(round(src.shape[1] * sc)), int(round(src.shape[0] * sc))
        src = cv2.resize(src, (nw, nh), interpolation=cv2.INTER_AREA) / 255.
        src = np.clip((src - 0.5) * 1.07 + 0.51, 0, 1); src[..., 0] *= 0.985; src[..., 2] *= 1.02   # mild grade, natural colour
        H = self.H1 * o; yy = np.arange(H, dtype=np.float32)
        (ya, yb, smax), (yc, yd) = scrim
        s = sm(ya * o, yb * o, yy) * smax; s = np.maximum(s, sm(yc * o, yd * o, yy))
        s = np.maximum(s, top_scrim * (1 - sm(0, 260 * o, yy)))
        self.ph = dict(img=np.clip(src, 0, 1), nw=nw, nh=nh, x0=0, y0=0, ax=anchor[0], ay=anchor[1], s=s, reveal=reveal, zoom=zoom)
    def draw_athlete(self, fr, t, still=False):
        A = self.ph
        if A is None: return None
        o = hud.OS; H, W = fr.shape[:2]
        r0, r1 = A['reveal']; rev = 1.0 if still else ease(t, r0, r1)
        if rev <= 0: return None
        z = 1.015 if still else 1.0 + A['zoom'] * ease_io(t, 0, DUR)
        w, h = int(A['nw'] * z), int(A['nh'] * z)
        rgb = cv2.resize(A['img'], (w, h), interpolation=cv2.INTER_LINEAR if z > 1 else cv2.INTER_AREA)
        AX, AY = A['ax'] * o, A['ay'] * o
        x = int(round(AX - (AX - A['x0'] * o) * z)); y = int(round(AY - (AY - A['y0'] * o) * z))
        y0 = max(0, y); y1 = min(H, y + h); x0 = max(0, x); x1 = min(W, x + w)
        if y1 <= y0 or x1 <= x0: return None
        rgb_ = rgb[y0 - y:y1 - y, x0 - x:x1 - x]
        rows = np.arange(y0, y1, dtype=np.float32)
        al = (1 - A['s'][y0:y1])[:, None]
        if rev < 1:
            sy = rev * H * 1.04
            vis = 1 - sm(sy - 22 * o, sy + 6 * o, rows)
            al = al * vis[:, None]
            band = (np.exp(-((rows - sy) / (6.0 * o)) ** 2) * (1 - rev) ** 0.5)[:, None]
            reg = fr[y0:y1, x0:x1]
            reg[:] = reg * (1 - al[..., None]) + rgb_ * al[..., None]
            reg += band[..., None] * np.array(BRONZE, np.float32) / 255. * 0.7
            fr[y0:y1, :] += (band * 0.06)[..., None] * np.array(WHITE, np.float32) / 255.
        else:
            reg = fr[y0:y1, x0:x1]
            reg[:] = reg * (1 - al[..., None]) + rgb_ * al[..., None]
        full = np.zeros((H, W), np.float32); full[y0:y1, x0:x1] = al * 0.92
        return full

def hsweep_fn(post, HY, cb, x0, hw, t0=3.3):
    def hsweep(d, t, still):
        if still or not (t0 <= t <= t0 + 0.7): return
        o = hud.OS; ph = (t - t0) / 0.7; x = x0 + ph * hw
        for k in range(-3, 4):
            d.line([((x + k * 3) * o, HY * o), ((x + k * 3 + 40) * o, cb * o)], fill=(255, 255, 255, int(70 * (1 - abs(k) / 4))), width=max(1, int(2 * o)))
    post.dynamic(hsweep)

def place_tag(post, x, y, anchor, t0):
    """'// 3.º LUGAR' gold micro next to the date"""
    post.mk('place', lambda c: c.text((x, y), '// ' + COMMON['place'], T('Bold', 20), GOLD, tr=3, anchor=anchor), A(t0, t0 + 0.5), text=True)

# ====================================================================== STORY W-S
def story_W(post):
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    # photo: crop x 1040-2440 (both gloves in, watermark out), full height; scale 1080/1400; anchor = face
    post.photo(cfg['photo'], (0, 2062, 1040, 2440), 1080 / 1400, anchor=(440, 480), scrim=((700, 990, 0.93), (1460, 1585)), top_scrim=0.40)
    post.glows = [(1080 * 0.02, 1920 * 0.86, 1080 * 0.9, KEY, 0.26, 4.0, 0), (1080 * 1.0, 1920 * 0.99, 1080 * 0.8, ALT, 0.20, 5.0, 1.3), (1080 * 0.55, 1920 * 0.62, 1080 * 0.42, BRONZE, 0.14, 6.0, 2.1)]
    top_slashes(post, mirror=True)
    label_stack(post, 1016, 'r')
    logo(post, 1016 - 250, 284, 250)
    cs = status_block(post, 64, 300, 'l', t0=2.2)
    add_common_dynamics(post, (120, 700), gauge_t=(1.5, 2.9), ruler=(1004, 560, 760), cellspec=cs, coord_xy=(64, 790))
    # photo-window reticles
    post.mk('ret1', lambda c: c.bracket(1016, 520, 26, 'tr', (255, 255, 255, 160), 2), A(1.4, 2.0, 'slide', dx=30, dy=-30))
    post.mk('ret2', lambda c: c.bracket(64, 905, 26, 'bl', (255, 255, 255, 160), 2), A(1.5, 2.1, 'slide', dx=-30, dy=30))
    # ---- hero stack: MEDALHA DE / BRONZE / CAMPEONATO DO MUNDO ----
    fM = T('Black', 80); capM = (fM.getbbox('HEN')[3] - fM.getbbox('HEN')[1]) / S
    MY = 940; post.letters('med', 64, MY - fM.getbbox('MEDALHA')[1] / S, 'MEDALHA DE', fM, WHITE, t0=2.3, step=0.04, dur=0.45, kind='rise', dy=50)
    mb = MY + capM
    fh, hsz = fit('Black', cfg['hero'], 140, 952); bbh = fh.getbbox(cfg['probe']); capH = (bbh[3] - bbh[1]) / S
    HY = mb + 12; hw = post.letters('hero', 64, HY - bbh[1] / S, cfg['hero'], fh, BRONZE, t0=2.7, step=0.05, dur=0.45, kind='rise', dy=60)
    post.flash_t = (3.2, 0.4); cb = HY + capH
    post.mk('cline', lambda c: c.rect(64, cb + 14, 64 + hw, cb + 18, fill=KEY), A(3.4, 4.0, 'wipe', dir='lr'))
    hsweep_fn(post, HY, cb, 64, hw, 3.3)
    fC, csz = fit('Black', 'CAMPEONATO DO MUNDO', 60, 952, tr=1); capC = (fC.getbbox('HEN')[3] - fC.getbbox('HEN')[1]) / S
    CY = cb + 24; post.letters('cdm', 64, CY - fC.getbbox('CAMPEONATO')[1] / S, 'CAMPEONATO DO MUNDO', fC, GOLD, tr=1, t0=3.6, step=0.035, dur=0.45, kind='rise', dy=40)
    ccb = CY + capC
    # ---- date + place / name ----
    fD = T('Bold', 40); DY = ccb + 18
    post.mk('date', lambda c: c.text((64, DY), COMMON['date'], fD, KEY, tr=2), A(4.5, 5.0, 'slidewipe', dx=-60, dir='lr'), text=True)
    place_tag(post, 64 + twidth(fD, COMMON['date'], 2) + 22, DY + 12, 'l', 4.9)
    db = DY + fD.getbbox('HEN')[3] / S
    sz = 60
    while twidth(T(W_FIRST, sz), cfg['first']) + twidth(T('Black', sz), cfg['last']) > 952: sz -= 1
    ft1, ft2 = T(W_FIRST, sz), T('Black', sz); TY = db + 14
    w1 = post.letters('t1', 64, TY, cfg['first'], ft1, WHITE, t0=4.8, step=0.04, dur=0.4, kind='rise', dy=40)
    post.letters('t2', 64 + w1, TY, cfg['last'], ft2, KEY, t0=5.0, step=0.04, dur=0.4, kind='rise', dy=40)
    ny = TY + ft2.getbbox('HEN')[3] / S
    post.mk('desc', lambda c: c.text((64, ny + 12), COMMON['desc'], T('Medium', 18), GREY, tr=3), A(5.4, 5.9), text=True)
    # ---- lean rows: event / location + category chip (no panel) ----
    RY = ny + 40
    post.mk('rule1', lambda c: c.rect(64, RY, 1016, RY + 1, fill=(255, 255, 255, 60)), A(5.5, 6.1, 'wipe', dir='lr'))
    fev, _ = fit('Bold', COMMON['event'], 30, 640)
    post.mk('ev', lambda c: c.text((64, RY + 16), COMMON['event'], fev, WHITE), A(5.8, 6.4, 'slide', dx=-40), text=True)
    post.mk('loc', lambda c: c.text((64, RY + 54), COMMON['loc'] + ' // ' + COMMON['date'], T('Regular', 22), GREY, tr=2), A(6.0, 6.6, 'slide', dx=-40), text=True)
    CX0, CY0, CX1, CY1 = 1016 - 290, RY + 14, 1016, RY + 14 + 62
    post.mk('chip', lambda c: c.chamfer(CX0, CY0, CX1, CY1, 12, fill=ALT + (26,), outline=ALT + (255,), w=1), A(6.2, 6.8, 'wipe', dir='rl'))
    def _chipt(c):
        fk, _ = fit('Bold', cfg['cat'], 36, 260); bb_ = fk.getbbox(cfg['cat']); c.text(((CX0 + CX1) / 2, (CY0 + CY1) / 2 - (bb_[1] + bb_[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='c')
    post.mk('chipt', _chipt, A(6.4, 7.0, 'pop', s0=1.25), text=True)
    post.mk('chipl', lambda c: c.text((CX1, CY1 + 10), 'CATEGORIA // ' + COMMON['disc'], T('Medium', 13), GREY, tr=3, anchor='r'), A(6.5, 6.9), text=True)
    RB = RY + 92
    post.mk('rule2', lambda c: c.rect(64, RB, 1016, RB + 1, fill=(255, 255, 255, 60)), A(6.3, 6.9, 'wipe', dir='lr'))
    # ---- Seleção (1 line, green) + tricolour, then cheer row: hash left / PARABÉNS! right ----
    SY = RB + 16
    fS = T('Bold', 30); selw = twidth(fS, 'SELEÇÃO NACIONAL PORTUGAL', 2)
    post.mk('sel', lambda c: c.text((64, SY), 'SELEÇÃO NACIONAL PORTUGAL', fS, ALT, tr=2), A(7.0, 7.6, 'slidewipe', dx=-60, dir='lr'), text=True)
    post.mk('seltri', lambda c: tricolour(c, 64, SY + 40, selw, 4, anchor='l'), A(7.4, 7.9, 'wipe', dir='lr'))
    base = layouts.cheer_row(post, SY + 54, left='hash', t0=7.5, cheer_sz=84, hash_sz=36, X0=64, X1=1016)
    layouts.bottom_decor_story(post, mirror=True)
    post.notes.append(f'story W-S: hero {hsz}pt, campeonato {csz}pt, name {sz}pt, rows y {RY:.0f}-{RB:.0f}, hash baseline y={base:.0f} (<=1600)')
    if FX_ON:
        import layouts_bronze
        layouts_bronze.make_fx(post, face=(440, 460, 160, 200), zones=[(0, 300), (1100, 1300), (1620, 1900)], bursts=[(0.35, 1.0), (2.9, 3.15), (8.3, 8.5), (13.5, 13.7), (18.0, 18.2)],
                               still_bands=[(40, 10, 46, 5), (212, 14, -38, 6), (1150, 6, 44, 7, 0, 300), (1648, 16, -56, 7), (1790, 24, 30, 6)], excl=[(0, 300, 1080, 1620)])

# ====================================================================== PORTRAIT W-P (3:4)
def portrait_W(post):
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    # photo: full height, 3:4 crop x 900-2446 (gloves in, watermark out); scale 1440/2062; anchor = face
    post.photo(cfg['photo'], (0, 2062, 900, 2446), 1440 / 2062, anchor=(495, 420), scrim=((520, 800, 0.93), (1330, 1440)), top_scrim=0.38)
    post.glows = [(1080 * 1.0, 1440 * 0.9, 1080 * 0.85, KEY, 0.26, 4.0, 0), (1080 * 0.0, 1440 * 1.0, 1080 * 0.7, ALT, 0.20, 5.0, 1.3), (1080 * 0.6, 1440 * 0.6, 1080 * 0.4, BRONZE, 0.12, 6.0, 2.1)]
    top_slashes(post, mirror=False)
    label_stack(post, 64, 'l')
    logo(post, 84, 284, 250)
    cs = status_block(post, 1016, 300, 'r', t0=2.2)
    add_common_dynamics(post, (960, 660), gauge_t=(1.5, 2.9), ruler=None, cellspec=cs, coord_xy=(1016 - 150, 740))
    post.mk('ret1', lambda c: c.bracket(64, 520, 26, 'tl', (255, 255, 255, 160), 2), A(1.4, 2.0, 'slide', dx=-30, dy=-30))
    post.mk('ret2', lambda c: c.bracket(1016, 780, 26, 'br', (255, 255, 255, 160), 2), A(1.5, 2.1, 'slide', dx=30, dy=30))
    # ---- vertical h2: CAMPEONATO DO MUNDO (gold), LEFT strip, reads bottom->top ----
    VWORD = 'CAMPEONATO DO MUNDO'
    fv, vsz = fit('Black', VWORD, 56, 560, tr=-1); bb = fv.getbbox('CAMPEONATO'); wlen = twidth(fv, VWORD, -1); cap = (bb[3] - bb[1]) / S
    VX0 = 64; VY1 = 1376; VY0 = VY1 - wlen
    def vword(c):
        im = Image.new('RGBA', (P(wlen + 10), P(cap + 10)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 0
        for ch in VWORD: d.text((x, -bb[1]), ch, font=fv, fill=GOLD); x += fv.getlength(ch) - 1 * S
        im = im.rotate(90, expand=True); c.img.alpha_composite(im, (P(VX0), P(VY0)))
    def vword_amb(t):
        sc = 1.0
        for p0 in (6.6, 10.7, 13.5, 16.2):
            if p0 <= t < p0 + 0.5: sc = 1 + 0.03 * math.sin(math.pi * (t - p0) / 0.5)
        return 0, 0, 1, sc
    post.mk('vword', vword, A(3.6, 4.4, 'wipe', dir='bt'), text=True, anchor=(0.5, 0.5), amb=vword_amb)
    post.mk('vrule', lambda c: c.rect(VX0 + cap + 22, VY0, VX0 + cap + 26, VY1, fill=KEY), A(3.8, 4.5, 'wipe', dir='bt'))
    def vtri(c):
        x = VX0 + cap + 34; h = wlen
        c.rect(x, VY0, x + 4, VY0 + h * 0.40, fill=GREEN); c.rect(x, VY0 + h * 0.40, x + 4, VY0 + h * 0.955, fill=RED); c.rect(x, VY0 + h * 0.955, x + 4, VY0 + h, fill=GOLD)
    post.mk('vtri', vtri, A(4.1, 4.8, 'wipe', dir='bt'))
    post.mk('vtag', lambda c: c.text((VX0, VY0 - 30), 'WCH-POL-26 // 17.10.2026', T('Medium', 14), GOLD, tr=3), A(4.7, 5.2), text=True)
    def sweep(d, t, still):
        if still or not (4.6 <= t <= 5.4): return
        o = hud.OS; ph = (t - 4.6) / 0.8; y = VY1 - ph * wlen
        for k in range(-3, 4):
            d.line([(VX0 * o, (y + k * 3) * o), ((VX0 + cap + 10) * o, (y + k * 3 - 40) * o)], fill=(255, 255, 255, int(70 * (1 - abs(k) / 4))), width=max(1, int(2 * o)))
    post.dynamic(sweep)
    XL = VX0 + cap + 80   # left edge of the right-aligned column
    XR = 1016
    # ---- hero stack right-aligned: MEDALHA DE / BRONZE ----
    fM = T('Black', 72); capM = (fM.getbbox('HEN')[3] - fM.getbbox('HEN')[1]) / S
    MY = 756; post.letters('med', XR, MY - fM.getbbox('MEDALHA')[1] / S, 'MEDALHA DE', fM, WHITE, anchor='r', t0=2.3, step=0.04, dur=0.45, kind='rise', dy=44)
    mb = MY + capM
    fh, hsz = fit('Black', cfg['hero'], 150, XR - XL); bbh = fh.getbbox(cfg['probe']); capH = (bbh[3] - bbh[1]) / S
    HY = mb + 14; hw = post.letters('hero', XR, HY - bbh[1] / S, cfg['hero'], fh, BRONZE, anchor='r', t0=2.7, step=0.05, dur=0.45, kind='rise', dy=60)
    post.flash_t = (3.2, 0.4); cb = HY + capH
    post.mk('cline', lambda c: c.rect(XR - hw, cb + 14, XR, cb + 18, fill=KEY), A(3.4, 4.0, 'wipe', dir='rl'))
    hsweep_fn(post, HY, cb, XR - hw, hw, 3.3)
    # ---- date + place (right) ----
    fD = T('Bold', 36); DY = cb + 26
    post.mk('date', lambda c: c.text((XR, DY), COMMON['date'], fD, KEY, tr=2, anchor='r'), A(4.5, 5.0, 'slidewipe', dx=60, dir='rl'), text=True)
    place_tag(post, XR - twidth(fD, COMMON['date'], 2) - 22, DY + 10, 'r', 4.9)
    db = DY + fD.getbbox('HEN')[3] / S
    # ---- name one line, right-aligned ----
    sz = 72
    while twidth(T(W_FIRST, sz), cfg['first']) + twidth(T('Black', sz), cfg['last']) > XR - XL: sz -= 1
    ft1, ft2 = T(W_FIRST, sz), T('Black', sz); TY = db + 14
    w2 = twidth(ft2, cfg['last']); w1 = twidth(ft1, cfg['first'])
    post.letters('t1', XR - w2 - w1, TY, cfg['first'], ft1, WHITE, t0=4.8, step=0.04, dur=0.4, kind='rise', dy=40)
    post.letters('t2', XR - w2, TY, cfg['last'], ft2, KEY, t0=5.0, step=0.04, dur=0.4, kind='rise', dy=40)
    ny = TY + ft2.getbbox('HEN')[3] / S
    uy = ny + 18
    post.mk('ul', lambda c: c.rect(XR - 380, uy, XR, uy + 4, fill=WHITE), A(5.3, 5.9, 'wipe', dir='rl'))
    post.mk('desc', lambda c: c.text((XR - 380 - 22, uy - 11), COMMON['desc'], T('Medium', 16), GREY, tr=3, anchor='r'), A(5.6, 6.1), text=True)
    # ---- chamfered card: event / date+loc, category chip right ----
    X0, Y0, X1, Y1 = XL, uy + 20, XR, uy + 20 + 116
    def _card(c):
        c.chamfer(X0, Y0, X1, Y1, 22, mirror=True, fill=PANEL + (217,), outline=(255, 255, 255, 38), w=1)
        mid = Y0 + (Y1 - Y0) * 0.45; c.rect(X1 - 6, Y0 + 22, X1, mid, fill=KEY); c.rect(X1 - 6, mid, X1, Y1, fill=ALT)
    post.mk('card', _card, A(5.5, 6.2, 'wipe', dir='rl')); post.card_rect = (X0, Y0, X1, Y1)
    post.mk('cbr', lambda c: c.bracket(X0 - 14, Y1 + 14, 22, 'bl', (255, 255, 255, 170), 2), A(6.0, 6.5, 'slide', dx=-30, dy=30))
    ix = X0 + 30
    fev, _ = fit('Bold', COMMON['event'], 30, X1 - ix - 320)
    post.mk('ev', lambda c: c.text((ix, Y0 + 16), COMMON['event'], fev, WHITE), A(5.9, 6.5, 'slide', dx=-40), text=True)
    post.mk('loc', lambda c: c.text((ix, Y0 + 56), COMMON['loc'] + ' // ' + COMMON['date'], T('Regular', 21), GREY, tr=2), A(6.1, 6.7, 'slide', dx=-40), text=True)
    CX0, CY0, CX1, CY1 = X1 - 34 - 270, Y0 + 30, X1 - 34, Y0 + 30 + 58
    post.mk('chipl', lambda c: c.text((CX1, CY0 - 20), 'CATEGORIA // ' + COMMON['disc'], T('Medium', 13), GREY, tr=3, anchor='r'), A(6.3, 6.7), text=True)
    post.mk('chip', lambda c: c.chamfer(CX0, CY0, CX1, CY1, 12, fill=ALT + (26,), outline=ALT + (255,), w=1), A(6.4, 7.0, 'wipe', dir='rl'))
    def _chipt(c):
        fk, _ = fit('Bold', cfg['cat'], 34, 240); bb_ = fk.getbbox(cfg['cat']); c.text(((CX0 + CX1) / 2, (CY0 + CY1) / 2 - (bb_[1] + bb_[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='c')
    post.mk('chipt', _chipt, A(6.6, 7.2, 'pop', s0=1.25), text=True)
    # ---- Seleção right (green) + tricolour · PARABÉNS! left + hash right ----
    SY = Y1 + 16
    fS = T('Bold', 26); selw = twidth(fS, 'SELEÇÃO NACIONAL PORTUGAL', 2)
    post.mk('sel', lambda c: c.text((XR, SY), 'SELEÇÃO NACIONAL PORTUGAL', fS, ALT, tr=2, anchor='r'), A(7.0, 7.6, 'slidewipe', dx=60, dir='rl'), text=True)
    post.mk('seltri', lambda c: tricolour(c, XR, SY + 36, selw, 4, anchor='r'), A(7.4, 7.9, 'wipe', dir='rl'))
    FY = SY + 50
    ff, _ = fit('Black', COMMON['cheer'], 62, (XR - XL) - 300); bbF = ff.getbbox(COMMON['cheer']); cbF = ff.getbbox('HEN'); base = FY - bbF[1] / S + cbF[3] / S
    post.mk('forca', lambda c: c.text((XL, FY - bbF[1] / S), COMMON['cheer'], ff, WHITE), A(7.8, 8.5, 'pop', s0=0.84, over=1.7, flash=True), text=True, anchor=(0.0, 0.8), amb=cheer_amb)
    fhh = T('SemiBold', 32); hb_ = fhh.getbbox(COMMON['hash'])
    post.mk('hash', lambda c: c.text((XR, base - hb_[3] / S), COMMON['hash'], fhh, KEY, anchor='r'), A(7.6, 8.2, 'slidewipe', dx=80, dir='rl'), text=True)
    # footer
    post.mk('foott', lambda c: (c.text((XR, 1408), COMMON['foot'], T('Regular', 12), DIM, tr=4, anchor='r'), c.text((XL, 1408), COMMON['standby'], T('Medium', 12), DIM, tr=3)), A(8.2, 8.8), text=True)
    post.mk('bcode', lambda c: (barcode(c, XR - 150, 232, 150, 14, seed=3), c.text((XR, 252), 'ID 26-WCH-POL // KUMITE', MONO(11), DIM + (255,), anchor='r')), A(3.4, 4.0))
    post.notes.append(f'portrait W-P: hero {hsz}pt, vertical campeonato {vsz}pt y {VY0:.0f}-{VY1:.0f}, name {sz}pt, card y {Y0:.0f}-{Y1:.0f}, cheer baseline y={base:.0f} (<=1380)')

def build(cfgname, fmt):
    cfg = dict(CFG[cfgname]); post = WindowPost(cfg, fmt)
    (story_W if fmt == 'story' else portrait_W)(post)
    for n in post.notes: print(n, file=sys.stderr)
    return post
