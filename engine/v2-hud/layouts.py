import math, numpy as np
import hud
from hud import *
from PIL import Image

CFG = {
 'aguiar': dict(first='ANDRÉ ', last='AGUIAR', hero='CONVOCADO', cat='JUNIOR +76 KG', key=GREEN, alt=RED,
                photo='/mnt/user-data/uploads/1000133289.jpg', mask='/home/claude/and_mask.png', crop=(504, 3413, 1700, 3792),
                caps='CONVOCADO', probe='CONVOCADO'),
 'goncalves': dict(first='LEONOR ', last='GONÇALVES', hero='CONVOCADA', cat='JUNIOR -53 KG', key=RED, alt=GREEN,
                photo='/home/claude/leo3_src.jpg', mask='/home/claude/leo3_mask.png', crop=(620, 3900, 152, 1656),
                caps='CONVOCADA', probe='CONVOCADA'),
}
COMMON = dict(event='WKF WORLD CHAMPIONSHIPS', loc='POLÓNIA 2026', date='14–18 OUT 2026', where='POLÓNIA', cheer='PARABÉNS!', hash='#TEAMSHOMEN', disc='KUMITE',
              l1='SHM // CALL-UP', l2='REF. WCH-POL-26 / KUMITE', l3='SELEÇÃO NACIONAL — TEAM SHOMEN', desc='ATLETA // TEAM SHOMEN',
              sel='SELEÇÃO NACIONAL // PORTUGAL', status='STATUS // CONVOCATÓRIA', conf='CONFIRMADO', standby='CONVOCATÓRIA // BIELSKO-BIALA PL',
              foot='SHOMEN © 2026', coord=(49.8224, 19.0584))

def A(t0, t1, kind='fade', **k): d = dict(t0=t0, t1=t1, kind=kind); d.update(k); return d
def drift(per, amp, ph=0):
    return lambda t: (0, amp * math.sin(2 * math.pi * t / per + ph), 1, None)
def sdrift(n, sdir):
    def f(t):
        d = math.sin(2 * math.pi * t / 6 + n) * (10 + 6 * n); return sdir[0] * d, sdir[1] * d, 1, None
    return f

# ---------------- shared HUD pieces ----------------
def tricolour(c, x, y, w, h=4, anchor='r'):
    x0 = x - w if anchor == 'r' else x
    c.rect(x0, y, x0 + w * 0.40, y + h, fill=GREEN); c.rect(x0 + w * 0.40, y, x0 + w * 0.955, y + h, fill=RED); c.rect(x0 + w * 0.955, y, x0 + w, y + h, fill=YELLOW)
def cells(c, x, y, n, cw, ch, gap, col, k=None, anchor='l'):
    """segmented status bar; k = number of lit cells (None = all)"""
    tot = n * cw + (n - 1) * gap; x0 = x - tot if anchor == 'r' else x
    for i in range(n):
        lit = (k is None) or (i < k)
        xx = x0 + i * (cw + gap)
        c.poly([(xx + 3, y), (xx + cw, y), (xx + cw - 3, y + ch), (xx, y + ch)], fill=(col + (255,)) if lit else None, outline=(col + (90,)) if not lit else None, w=1)
def barcode(c, x, y, w, h, seed=5, col=(255, 255, 255, 60)):
    rng = np.random.default_rng(seed); xx = x
    while xx < x + w:
        bw = int(rng.choice([1, 1, 2, 3, 4])); c.rect(xx, y, xx + bw, y + h, fill=col); xx += bw + int(rng.choice([2, 3, 4, 6]))
def dotmatrix(c, x, y, n, m, step, col, lit):
    for i in range(n):
        for j in range(m):
            on = (i * m + j) in lit
            c.circle(x + j * step, y + i * step, 2.2 if on else 1.4, fill=(col + (255,)) if on else (255, 255, 255, 55))

def add_common_dynamics(post, cross, gauge_t=(1.5, 2.9), ruler=None, cellspec=None, coord_xy=None):
    KEY, ALT = post.KEY, post.ALT
    cx, cy = cross
    mono = MONO(15, sc=hud.OS); monoB = MONO(13, True, sc=hud.OS)
    def dyn(d, t, still):
        o = hud.OS; Q = lambda v: v * o
        e = 1 if still else ease(t, *gauge_t)
        if e <= 0: return
        ddx = 0 if still else 18 * math.sin(2 * math.pi * t / 7.0); ddy = 0 if still else 26 * math.sin(2 * math.pi * t / 9.0 + 0.8)
        X, Y = cx + ddx, cy + ddy
        a = int(255 * e)
        # arc gauge: key arc sweeps, outer thin ring rotates, alt segment, ticks
        sw = 250 * e; rot = 0 if still else (t * 9) % 360; rot2 = 0 if still else -(t * 5) % 360
        d.arc([Q(X - 46), Q(Y - 46), Q(X + 46), Q(Y + 46)], 135 + rot2, 135 + rot2 + sw, fill=KEY + (a,), width=max(1, int(3 * o)))
        d.arc([Q(X - 58), Q(Y - 58), Q(X + 58), Q(Y + 58)], rot, rot + 300, fill=(255, 255, 255, int(70 * e)), width=max(1, int(1.5 * o)))
        d.arc([Q(X - 66), Q(Y - 66), Q(X + 66), Q(Y + 66)], 200 - rot2 * 0.5, 240 - rot2 * 0.5, fill=ALT + (a,), width=max(1, int(4 * o)))
        for k in range(12):
            an = math.radians(k * 30 + rot * 0.3); r0, r1 = (70, 78) if k % 3 == 0 else (72, 76)
            d.line([(Q(X + r0 * math.cos(an)), Q(Y + r0 * math.sin(an))), (Q(X + r1 * math.cos(an)), Q(Y + r1 * math.sin(an)))], fill=(255, 255, 255, int(120 * e)), width=max(1, int(1.2 * o)))
        # crosshair
        d.ellipse([Q(X - 24), Q(Y - 24), Q(X + 24), Q(Y + 24)], outline=(255, 255, 255, int(120 * e)), width=max(1, int(1.2 * o)))
        for ddx_, ddy_ in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d.line([(Q(X + ddx_ * 12), Q(Y + ddy_ * 12)), (Q(X + ddx_ * 36), Q(Y + ddy_ * 36))], fill=(255, 255, 255, int(150 * e)), width=max(1, int(1.2 * o)))
        d.ellipse([Q(X - 4), Q(Y - 4), Q(X + 4), Q(Y + 4)], fill=YELLOW + (a,))
        # readouts
        if coord_xy:
            rx, ry = coord_xy; jx = COMMON['coord'][0] + (0 if still else ddx * 0.0001 + math.sin(t * 13) * 0.00004); jy = COMMON['coord'][1] + (0 if still else ddy * 0.0001 + math.cos(t * 11) * 0.00004)
            d.text((Q(rx + ddx * 0.3), Q(ry + ddy * 0.35)), f'X {jx:.4f}', font=mono, fill=GREY + (a,)); d.text((Q(rx + ddx * 0.3), Q(ry + 24 + ddy * 0.35)), f'Y {jy:.4f}', font=mono, fill=GREY + (a,))
            d.text((Q(rx + ddx * 0.3), Q(ry + 48 + ddy * 0.35)), f'ALT {int(370 + (0 if still else 6 * math.sin(t * 1.7)))} M', font=mono, fill=DIM + (a,))
        # scrolling vertical ruler
        if ruler:
            rx, ry0, ry1 = ruler; off = 0 if still else (t * 14) % 50
            for k in range(-5, 40):
                yk = ry0 + k * 10 + off
                if ry0 <= yk <= ry1:
                    idx = k - (0 if still else int((t * 14) // 50) * 5); h = 12 if idx % 5 == 0 else 6
                    d.line([(Q(rx), Q(yk)), (Q(rx + h), Q(yk))], fill=(255, 255, 255, int(80 * e)), width=max(1, int(o)))
        # segmented status cells + readout
        if cellspec:
            sx, sy, n, anchor, t0 = cellspec; cw, chh, gap = 18, 10, 4
            tot = n * cw + (n - 1) * gap; x0 = sx - tot if anchor == 'r' else sx
            k = n if still else int(np.clip((t - t0) / 0.09, 0, n))
            for i in range(n):
                xx = x0 + i * (cw + gap); lit = i < k
                blink = (not still) and i == n - 1 and lit and (t % 1.0) < 0.5
                col = KEY + (255,) if lit else KEY + (70,)
                if blink: col = YELLOW + (255,)
                pts = [(Q(xx + 3), Q(sy)), (Q(xx + cw), Q(sy)), (Q(xx + cw - 3), Q(sy + chh)), (Q(xx), Q(sy + chh))]
                if lit: d.polygon(pts, fill=col)
                else: d.polygon(pts, outline=col, width=max(1, int(o)))
            pct = 100 if still else int(100 * k / n)
            lab = f'{pct:03d}% // {COMMON["conf"]}' if pct == 100 else f'{pct:03d}% // A VERIFICAR'
            colr = (KEY if pct == 100 else GREY) + (255,)
            if anchor == 'r': d.text((Q(sx), Q(sy + 18)), lab, font=monoB, fill=colr, anchor='ra')
            else: d.text((Q(x0), Q(sy + 18)), lab, font=monoB, fill=colr)
    post.dynamic(dyn)

def bottom_decor_story(post, mirror=False):
    """footer hairline + ©, mini slashes, standby label, barcode, big alt slashes in a bottom corner"""
    KEY, ALT = post.KEY, post.ALT; fy = 1846
    def foot(c):
        c.line([(64, fy), (1016, fy)], (255, 255, 255, 50), 1)
        if not mirror: c.slash(92, 16, fy + 14, fy + 44, ALT, yref=fy); c.slash(122, 16, fy + 14, fy + 44, KEY, yref=fy); c.slash(152, 16, fy + 14, fy + 44, YELLOW, yref=fy)
        else: c.slash(92, 16, fy + 14, fy + 44, ALT, yref=fy, mirror=True); c.slash(122, 16, fy + 14, fy + 44, KEY, yref=fy, mirror=True); c.slash(152, 16, fy + 14, fy + 44, YELLOW, yref=fy, mirror=True)
    post.mk('foot', foot, A(5.4, 6.2))
    def foott(c):
        if not mirror:
            c.text((1016, fy + 20), COMMON['foot'], T('Regular', 14), GREY, tr=4, anchor='r')
            c.text((1016, 1700), COMMON['standby'], T('Medium', 14), DIM, tr=3, anchor='r')
        else:
            c.text((64, fy + 20), COMMON['foot'], T('Regular', 14), GREY, tr=4)
            c.text((64, 1700), COMMON['standby'], T('Medium', 14), DIM, tr=3)
    post.mk('foott', foott, A(5.4, 6.2), text=True)
    def deco(c):
        if not mirror:
            c.ruler(1016 - 39 * 8, 1726, 40, step=8, col=(255, 255, 255, 70))
            barcode(c, 64, 1690, 230, 26, seed=5); c.text((64, 1726), 'ID 26-WCH-POL // KUMITE', MONO(12), DIM + (255,), tr=1)
            dotmatrix(c, 340, 1698, 3, 8, 9, KEY, {0, 3, 9, 12, 14, 20, 23})
        else:
            c.ruler(64, 1726, 40, step=8, col=(255, 255, 255, 70))
            barcode(c, 1016 - 230, 1690, 230, 26, seed=9); c.text((1016, 1726), 'ID 26-WCH-POL // KUMITE', MONO(12), DIM + (255,), tr=1, anchor='r')
            dotmatrix(c, 1016 - 230 - 90, 1698, 3, 8, 9, KEY, {1, 4, 8, 13, 17, 19, 22})
    post.mk('deco', deco, A(5.6, 6.4))
    # big alt slashes in the free bottom corner (behind decor zone only, y 1640-1920+)
    sdir = np.array([k60, -1.0])
    if not mirror:
        for n, (xt, wd, col) in enumerate(((60, 52, ALT), (-30, 30, ALT), (120, 4, KEY))):
            post.mk(f'bsl{n}', lambda c, xt=xt, wd=wd, col=col: c.slash(xt, wd, 1660, 1960, col, yref=1960), A(0.5 + n * 0.12, 1.2 + n * 0.12, 'slide', dx=-220, dy=380), amb=sdrift(n + 1, -sdir))
    else:
        for n, (xt, wd, col) in enumerate(((60, 52, ALT), (-30, 30, ALT), (120, 4, KEY))):
            post.mk(f'bsl{n}', lambda c, xt=xt, wd=wd, col=col: c.slash(xt, wd, 1660, 1960, col, yref=1960, mirror=True), A(0.5 + n * 0.12, 1.2 + n * 0.12, 'slide', dx=220, dy=380), amb=sdrift(n + 1, np.array([-k60, -1.0]) * -1))

def top_slashes(post, mirror=False, key=None):
    KEY = key or post.KEY; ALT = post.ALT
    sdir = np.array([k60, -1.0]) if not mirror else np.array([-k60, -1.0])
    specs = (('sl1', 1010, 64, KEY, 0.30), ('sl2', 1110, 44, KEY, 0.42), ('sl3', 962, 5, ALT, 0.55), ('sl4', 940, 2, YELLOW, 0.65))
    for n, (nm, xt, wd, col, st) in enumerate(specs):
        post.mk(nm, lambda c, xt=xt, wd=wd, col=col: c.slash(xt, wd, -200, 250, col, mirror=mirror), A(st, st + 0.75, 'slide', dx=sdir[0] * 520, dy=sdir[1] * 520, fade=True), amb=sdrift(n, sdir))

def label_stack(post, x, anchor='l', y=96):
    post.mk('hd1', lambda c: c.text((x, y), COMMON['l1'], T('Bold', 15), WHITE, tr=3, anchor=anchor), A(0.6, 1.2, 'wipe', dir='lr' if anchor == 'l' else 'rl'), text=True)
    post.mk('hd2', lambda c: c.text((x, y + 28), COMMON['l2'], T('Medium', 14), GREY, tr=2.5, anchor=anchor), A(0.75, 1.35, 'wipe', dir='lr' if anchor == 'l' else 'rl'), text=True)
    post.mk('hd3', lambda c: c.text((x, y + 54), COMMON['l3'], T('Medium', 14), DIM, tr=2.5, anchor=anchor), A(0.9, 1.5, 'wipe', dir='lr' if anchor == 'l' else 'rl'), text=True)
    post.mk('hdr', lambda c: c.ruler(x if anchor == 'l' else x - 27 * 8, y + 90, 28), A(1.0, 1.6, 'wipe', dir='lr' if anchor == 'l' else 'rl'))

def logo(post, x, y, w):
    def _l(c):
        lg = logo_rgba(P(w)); c.img.alpha_composite(lg, (P(x), P(y)))
    post.mk('logo', _l, A(0.8, 1.6, 'zoomfade', s0=1.12), text=True)
    return w * 519 / 600

def status_block(post, x, y, anchor='l', t0=2.2):
    """STATUS label + segmented cells (dynamic) + tricolour bar"""
    post.mk('stlab', lambda c: c.text((x, y), COMMON['status'], T('Medium', 14), GREY, tr=3, anchor=anchor), A(t0 - 0.3, t0 + 0.2, 'wipe', dir='lr' if anchor == 'l' else 'rl'), text=True)
    post.mk('sttri', lambda c: tricolour(c, x, y + 62, 260, 3, anchor=anchor), A(t0 + 0.9, t0 + 1.5, 'wipe', dir='lr' if anchor == 'l' else 'rl'))
    return (x, y + 26, 12, anchor, t0)

def card_row_bar(post, X0, Y0, X1, Y1, ev_font_sz=46, mirror=False, t0=3.3):
    """chamfered card: row1 event / date+loc, row2 highlight bar (alt colour) with CATEGORIA tab + disc + category"""
    KEY, ALT = post.KEY, post.ALT; cfg = post.cfg
    def _card(c):
        c.chamfer(X0, Y0, X1, Y1, 28, mirror=mirror, fill=PANEL + (217,), outline=(255, 255, 255, 38), w=1)
        mid = Y0 + (Y1 - Y0) * 0.45
        if not mirror:
            c.rect(X0, Y0, X0 + 6, mid, fill=KEY); c.rect(X0, mid, X0 + 6, Y1 - 28, fill=ALT)
        else:
            c.rect(X0, Y0 + 28, X0 + 6, mid, fill=KEY); c.rect(X0, mid, X0 + 6, Y1, fill=ALT)
        # fine hatch in the top-right inner corner
        for k in range(0, 120, 8):
            c.line([(X1 - 40 - k, Y0 + 1), (X1 - 40 - k - 30, Y0 + 31)], (255, 255, 255, 14), 1)
    post.mk('card', _card, A(t0, t0 + 0.7, 'wipe', dir='lr'))
    post.card_rect = (X0, Y0, X1, Y1)
    post.mk('cbr', lambda c: c.bracket(X1 + 14, Y1 + 14, 22, 'br', (255, 255, 255, 170), 2) if not mirror else c.bracket(X0 - 14, Y1 + 14, 22, 'bl', (255, 255, 255, 170), 2), A(t0 + 0.5, t0 + 1.0, 'slide', dx=30 if not mirror else -30, dy=30))
    ix = X0 + 40
    locs = COMMON['date'] + ' // ' + COMMON['where']
    fev, evsz = fit('Bold', COMMON['event'], 44, 700)
    post.mk('ev', lambda c: c.text((ix, Y0 + 16), COMMON['event'], fev, WHITE), A(t0 + 0.4, t0 + 1.0, 'slide', dx=-40), text=True)
    def _loc(c):
        c.text((ix, Y0 + 62), locs, T('Light', 28), GREY, tr=2); c.text((X1 - 36, Y0 + 24), '01 / 01', MONO(14, True), DIM + (255,), tr=3, anchor='r')
        c.ruler(X1 - 36 - 22 * 7, Y0 + 52, 22, step=7, h1=5, h2=10, col=(255, 255, 255, 80))
    post.mk('loc', _loc, A(t0 + 0.6, t0 + 1.2, 'slide', dx=40), text=True)
    HX0, HY0, HX1, HY1 = ix, Y0 + 100, X1 - 36, Y0 + 168; tabw = 256
    post.mk('hbar', lambda c: c.rect(HX0, HY0, HX1, HY1, fill=ALT + (26,), outline=ALT + (255,), w=1), A(t0 + 0.8, t0 + 1.4, 'wipe', dir='lr'))
    post.mk('tab', lambda c: c.poly([(HX0, HY0), (HX0 + tabw, HY0), (HX0 + tabw - 34, HY1), (HX0, HY1)], fill=ALT + (255,)), A(t0 + 1.0, t0 + 1.6, 'slide', dx=-60))
    def _tabt(c):
        fm = T('Bold', 22); bb = fm.getbbox('CATEGORIA'); c.text((HX0 + 22, (HY0 + HY1) / 2 - (bb[1] + bb[3]) / 2 / S), 'CATEGORIA', fm, (9, 10, 14), tr=3)
    post.mk('tabt', _tabt, A(t0 + 1.0, t0 + 1.6, 'slide', dx=-60), text=True)
    def _cat(c):
        fk, _ = fit('Bold', cfg['cat'], 46, (HX1 - 24) - (HX0 + tabw + 150)); bb = fk.getbbox(cfg['cat']); c.text((HX1 - 24, (HY0 + HY1) / 2 - (bb[1] + bb[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='r')
    post.mk('cat', _cat, A(t0 + 1.3, t0 + 1.9, 'slide', dx=60), text=True)
    post.mk('kum', lambda c: c.text((HX0 + tabw + 14, (HY0 + HY1) / 2 - 11), COMMON['disc'], T('Medium', 18), ALT, tr=3), A(t0 + 1.4, t0 + 1.8), text=True)
    return Y1

def cheer_row(post, FY, left='hash', t0=4.9, cheer_sz=88, hash_sz=40, X0=64, X1=1016):
    """cheer (Black) + hashtag (SemiBold) on a shared baseline. returns baseline y (1x)"""
    KEY = post.KEY
    fh = T('SemiBold', hash_sz); hw = twidth(fh, COMMON['hash'])
    ff, _ = fit('Black', COMMON['cheer'], cheer_sz, (X1 - X0) - hw - 40); bbF = ff.getbbox(COMMON['cheer']); cb = ff.getbbox('HEN'); base = FY - bbF[1] / S + cb[3] / S
    hb = fh.getbbox(COMMON['hash'])
    if left == 'hash':
        post.mk('forca', lambda c: c.text((X1, FY - bbF[1] / S), COMMON['cheer'], ff, WHITE, anchor='r'), A(t0 + 0.2, t0 + 0.9, 'pop', s0=0.84, over=1.7, flash=True), text=True, anchor=(1.0, 0.8), amb=cheer_amb)
        post.mk('hash', lambda c: c.text((X0, base - hb[3] / S), COMMON['hash'], fh, KEY), A(t0, t0 + 0.6, 'slidewipe', dx=-80, dir='lr'), text=True)
    else:
        post.mk('forca', lambda c: c.text((X0, FY - bbF[1] / S), COMMON['cheer'], ff, WHITE), A(t0 + 0.2, t0 + 0.9, 'pop', s0=0.84, over=1.7, flash=True), text=True, anchor=(0.0, 0.8), amb=cheer_amb)
        post.mk('hash', lambda c: c.text((X1, base - hb[3] / S), COMMON['hash'], fh, KEY, anchor='r'), A(t0, t0 + 0.6, 'slidewipe', dx=80, dir='rl'), text=True)
    return base

def selecao_block(post, X0, FY, sz, X1=1016, t0=5.9, hash_sz=40):
    """SELEÇÃO NACIONAL (Light) over PORTUGAL (Black, key) + tricolour bar, hashtag right-aligned on the PORTUGAL baseline. returns baseline (1x)"""
    KEY = post.KEY
    f1, f2 = T('Light', sz), T('Black', sz); cap = f2.getbbox('HEN')[3] / S - f2.getbbox('HEN')[1] / S
    y1 = FY - f1.getbbox('SELE')[1] / S; y2 = FY + cap + 14 - f2.getbbox('PORTUGAL')[1] / S
    post.mk('sel1', lambda c: c.text((X0, y1), 'SELEÇÃO NACIONAL', f1, WHITE, tr=1), A(t0, t0 + 0.6, 'slidewipe', dx=-60, dir='lr'), text=True)
    post.letters('sel2', X0, y2, 'PORTUGAL', f2, KEY, t0=t0 + 0.25, step=0.05, dur=0.42, kind='rise', dy=34)
    base = FY + cap + 14 + cap
    post.mk('seltri2', lambda c: tricolour(c, X0, base + 16, twidth(f2, 'PORTUGAL'), 4, anchor='l'), A(t0 + 0.8, t0 + 1.3, 'wipe', dir='lr'))
    fh = T('SemiBold', hash_sz); hb = fh.getbbox(COMMON['hash'])
    post.mk('hash', lambda c: c.text((X1, base - hb[3] / S), COMMON['hash'], fh, KEY, anchor='r'), A(t0, t0 + 0.6, 'slidewipe', dx=80, dir='rl'), text=True)
    return base + 20

def cheer_amb(t):
    sc = 1.0
    for p0 in (9.0, 13.0, 17.0):
        if p0 <= t < p0 + 0.6: sc = 1 + 0.07 * math.sin(math.pi * (t - p0) / 0.6)
    return 0, 0, 1, sc

def underline(post, y, x0, x1, desc_side='l', t0=3.0):
    """4px white bar + descriptor micro on the free side"""
    post.mk('ul', lambda c: c.rect(x0, y, x1, y + 4, fill=WHITE), A(t0, t0 + 0.6, 'wipe', dir='lr' if desc_side == 'r' else 'rl'))
    if desc_side == 'l': post.mk('desc', lambda c: c.text((x0 - 22, y - 11), COMMON['desc'], T('Medium', 18), GREY, tr=3, anchor='r'), A(t0 + 0.3, t0 + 0.8), text=True)
    else: post.mk('desc', lambda c: c.text((x1 + 22, y - 11), COMMON['desc'], T('Medium', 18), GREY, tr=3), A(t0 + 0.3, t0 + 0.8), text=True)

# ======================================================================
# STORY A — André: slashes TR, logo TL, status block TR, horizontal hero on a scrim band, 1-line name, highlight bar, hash left / cheer right
# ======================================================================
def story_A(post):
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    post.glows = [(1080 * 0.95, 1920 * 0.06, 1080 * 0.95, KEY, 0.30, 4.0, 0), (1080 * 0.02, 1920 * 0.97, 1080 * 1.0, ALT, 0.22, 5.0, 1.3)]
    top_slashes(post, mirror=False)
    label_stack(post, 64, 'l')
    lh = logo(post, 84, 284, 250)
    cs = status_block(post, 1016, 300, 'r', t0=2.2)
    post.athlete(cfg['photo'], cfg['mask'], cfg['crop'], 0.50, 560, 452, (985, 1160), reveal=(1.0, 2.5), edge_r=0.06)
    add_common_dynamics(post, (104, 660), gauge_t=(1.5, 2.9), ruler=(1004, 620, 880), cellspec=cs, coord_xy=(64, 740))
    # photo-zone corner reticles
    post.mk('ret1', lambda c: c.bracket(820, 436, 26, 'tr', (255, 255, 255, 150), 2), A(1.4, 2.0, 'slide', dx=30, dy=-30))
    post.mk('ret2', lambda c: c.bracket(1016, 940, 26, 'br', (255, 255, 255, 150), 2), A(1.5, 2.1, 'slide', dx=30, dy=30))
    # ---- hero word on a scrim band ----
    SY0, SY1 = 946, 1112
    def scrim(c):
        for k in range(0, 26, 2):
            a = int(200 * (k / 26) ** 1.2)
            c.rect(0, SY0 + k, 1080, SY0 + k + 2, fill=BG + (a,)); c.rect(0, SY1 - k - 2, 1080, SY1 - k, fill=BG + (a,))
        c.rect(0, SY0 + 26, 1080, SY1 - 26, fill=BG + (200,))
        c.line([(0, SY0), (1080, SY0)], (255, 255, 255, 22), 1); c.line([(0, SY1), (1080, SY1)], (255, 255, 255, 22), 1)
    post.mk('scrim', scrim, A(2.2, 2.9, 'wipe', dir='rl'))
    fh, hsz = fit('Black', cfg['hero'], 150, 900); bb = fh.getbbox(cfg['probe']); HY = 962
    hw = post.letters('hero', 1016, HY - bb[1] / S, cfg['hero'], fh, WHITE, anchor='r', t0=2.35, step=0.05, dur=0.45, kind='rise', dy=60)
    hb = HY + (bb[3] - bb[1]) / S; post.flash_t = (2.85, 0.35)
    post.mk('heroline', lambda c: c.rect(1016 - hw + 6, hb + 14, 1016, hb + 18, fill=KEY), A(2.9, 3.5, 'wipe', dir='rl'))
    post.mk('sel', lambda c: c.text((1016, hb + 30), COMMON['sel'], T('Medium', 18), GREY, tr=3, anchor='r'), A(3.1, 3.6, 'wipe', dir='rl'), text=True)
    post.mk('seltri', lambda c: tricolour(c, 1016 - twidth(T('Medium', 18), COMMON['sel'], 3) - 24, hb + 36, 150, 4, anchor='r'), A(3.3, 3.9, 'wipe', dir='rl'))
    # hero light sweep (thin white band crossing the word once, additive, safe on text)
    def sweep(d, t, still):
        if still or not (3.0 <= t <= 3.7): return
        o = hud.OS; ph = (t - 3.0) / 0.7; x = (1016 - hw) + ph * hw
        for k in range(-3, 4):
            d.line([((x + k * 3) * o, HY * o), ((x + k * 3 + 40) * o, hb * o)], fill=(255, 255, 255, int(70 * (1 - abs(k) / 4))), width=max(1, int(2 * o)))
    post.dynamic(sweep)
    # ---- name (one line) ----
    sz = 106
    while twidth(T('Light', sz), cfg['first']) + twidth(T('Black', sz), cfg['last']) > 952: sz -= 1
    ft1, ft2 = T('Light', sz), T('Black', sz); TY = 1112
    w1 = post.letters('t1', 64, TY, cfg['first'], ft1, WHITE, t0=3.5, step=0.04, dur=0.4, kind='rise', dy=40)
    post.letters('t2', 64 + w1, TY, cfg['last'], ft2, KEY, t0=3.75, step=0.04, dur=0.4, kind='rise', dy=40)
    uy = TY + ft2.getbbox('HEN')[3] / S + 26
    underline(post, uy, 1016 - 430, 1016, desc_side='l', t0=4.1)
    Y1 = card_row_bar(post, 64, uy + 34, 1016, uy + 34 + 192, 46, mirror=False, t0=4.3)
    base = cheer_row(post, Y1 + 30, left='hash', t0=5.6)
    bottom_decor_story(post, mirror=False)
    post.notes.append(f'story A: name {sz}pt, hero {hsz}pt, cheer baseline y={base:.0f} (<=1600)')

# ======================================================================
# STORY B — Leonor: slashes TL mirrored, logo TR, status TL, vertical hero word right strip, 2-line name, chip, cheer left / hash right
# ======================================================================
def story_B(post):
    """Leonor: slashes TL mirrored, logo TR, status TL, h1 = WKF WORLD / CHAMPIONSHIPS, h2 = CONVOCADA vertical on the right strip, name h3, card (date + chip), Seleção block"""
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    post.glows = [(1080 * 0.05, 1920 * 0.06, 1080 * 0.95, KEY, 0.30, 4.0, 0), (1080 * 0.98, 1920 * 0.97, 1080 * 1.0, ALT, 0.22, 5.0, 1.3)]
    top_slashes(post, mirror=True)
    label_stack(post, 1016, 'r')
    logo(post, 746, 284, 250)
    cs = status_block(post, 64, 300, 'l', t0=2.2)
    post.athlete(cfg['photo'], cfg['mask'], cfg['crop'], 0.40, 350, 380, (830, 960), reveal=(1.0, 2.5), anchor_face=(0.7, 0.14))
    add_common_dynamics(post, (104, 540), gauge_t=(1.5, 2.9), ruler=(64, 640, 700), cellspec=cs, coord_xy=(64, 630))
    post.mk('ret1', lambda c: c.bracket(740, 368, 26, 'tr', (255, 255, 255, 150), 2), A(1.4, 2.0, 'slide', dx=30, dy=-30))
    XR = 860
    # ---- h1: WKF WORLD (Light) / CHAMPIONSHIPS (Black), fitted to the left column ----
    hsz = 84
    while twidth(T('Black', hsz), 'CHAMPIONSHIPS') > XR - 64: hsz -= 1
    fL, fB = T('Light', hsz), T('Black', hsz); capB = (fB.getbbox('HEN')[3] - fB.getbbox('HEN')[1]) / S
    H1Y = 962; H2Y = H1Y + capB + 16
    post.mk('h1a', lambda c: c.text((64, H1Y - fL.getbbox('WKF')[1] / S), 'WKF WORLD', fL, WHITE), A(2.2, 2.8, 'slidewipe', dx=-80, dir='lr'), text=True)
    post.letters('h1b', 64, H2Y - fB.getbbox('CHAMPIONSHIPS')[1] / S, 'CHAMPIONSHIPS', fB, WHITE, t0=2.35, step=0.04, dur=0.45, kind='rise', dy=60)
    post.flash_t = (2.85, 0.35)
    hb = H2Y + capB
    post.mk('heroline', lambda c: c.rect(64, hb + 16, 64 + twidth(fB, 'CHAMPIONSHIPS'), hb + 20, fill=KEY), A(2.9, 3.5, 'wipe', dir='lr'))
    # ---- h2: vertical CONVOCADA on the right strip ----
    fh = T('Black', 100); bb = fh.getbbox(cfg['probe']); wlen = twidth(fh, cfg['hero'], -1); cap = (bb[3] - bb[1]) / S
    VX1 = 1016; VY1 = 1440; VY0 = VY1 - wlen
    def vword(c):
        im = Image.new('RGBA', (P(wlen + 10), P(cap + 10)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 0
        for ch in cfg['hero']: d.text((x, -bb[1]), ch, font=fh, fill=WHITE); x += fh.getlength(ch) - 1 * S
        im = im.rotate(90, expand=True); c.img.alpha_composite(im, (P(VX1 - cap - 10), P(VY0)))
    post.mk('vword', vword, A(3.0, 3.8, 'wipe', dir='bt'), text=True)
    post.mk('vrule', lambda c: c.rect(VX1 - cap - 26, VY0, VX1 - cap - 22, VY1, fill=KEY), A(3.2, 3.9, 'wipe', dir='bt'))
    post.mk('vtag', lambda c: c.text((VX1, VY1 + 18), 'PT // ' + COMMON['where'], T('Medium', 15), GREY, tr=3, anchor='r'), A(3.8, 4.3), text=True)
    def vtri(c):
        x = VX1 - cap - 36; h = wlen
        c.rect(x, VY0, x + 3, VY0 + h * 0.40, fill=GREEN); c.rect(x, VY0 + h * 0.40, x + 3, VY0 + h * 0.955, fill=RED); c.rect(x, VY0 + h * 0.955, x + 3, VY0 + h, fill=YELLOW)
    post.mk('vtri2', vtri, A(3.6, 4.3, 'wipe', dir='bt'))
    # ---- name (h3, two lines, left) ----
    szn = 64; L1Y = hb + 52; L2Y = L1Y + szn * 1.08
    f1, f2 = T('Light', szn), T('Black', szn)
    post.letters('t1', 64, L1Y, cfg['first'].strip(), f1, WHITE, t0=3.5, step=0.045, dur=0.42, kind='rise', dy=34)
    post.letters('t2', 64, L2Y, cfg['last'], f2, KEY, t0=3.75, step=0.045, dur=0.42, kind='rise', dy=34)
    ny = L2Y + f2.getbbox('HEN')[3] / S
    post.mk('desc', lambda c: c.text((64 + twidth(f2, cfg['last']) + 26, ny - 20), COMMON['desc'], T('Medium', 18), GREY, tr=3), A(4.3, 4.8), text=True)
    # ---- mirrored card: date + index left, category chip right ----
    X0, Y0, X1, Y1 = 64, ny + 30, XR, ny + 30 + 130
    def _card(c):
        c.chamfer(X0, Y0, X1, Y1, 26, mirror=True, fill=PANEL + (217,), outline=(255, 255, 255, 38), w=1)
        mid = Y0 + (Y1 - Y0) * 0.45; c.rect(X0, Y0 + 26, X0 + 6, mid, fill=KEY); c.rect(X0, mid, X0 + 6, Y1, fill=ALT)
        for k in range(0, 100, 8): c.line([(X1 - 8 - k, Y0 + 1), (X1 - 8 - k - 30, Y0 + 31)], (255, 255, 255, 14), 1)
    post.mk('card', _card, A(4.4, 5.1, 'wipe', dir='lr')); post.card_rect = (X0, Y0, X1, Y1)
    ix = X0 + 36
    def _loc(c):
        c.text((ix, Y0 + 44), COMMON['date'] + ' // ' + COMMON['where'], T('Bold', 28), WHITE, tr=1)
        c.text((ix, Y0 + 92), '01 / 01', MONO(14, True), DIM + (255,), tr=3); c.ruler(ix + 90, Y0 + 94, 22, step=7, h1=5, h2=10, col=(255, 255, 255, 80))
    post.mk('loc', _loc, A(4.8, 5.4, 'slide', dx=-40), text=True)
    CX0, CY0, CX1, CY1 = X1 - 36 - 268, Y0 + 40, X1 - 36, Y0 + 40 + 72
    post.mk('chipl', lambda c: c.text((CX1, Y0 + 14), 'CATEGORIA // ' + COMMON['disc'], T('Medium', 15), GREY, tr=3, anchor='r'), A(5.1, 5.5), text=True)
    post.mk('chip', lambda c: c.chamfer(CX0, CY0, CX1, CY1, 14, fill=ALT + (26,), outline=ALT + (255,), w=1), A(5.2, 5.8, 'wipe', dir='lr'))
    def _chipt(c):
        fk, _ = fit('Bold', cfg['cat'], 40, 240); bb = fk.getbbox(cfg['cat']); c.text(((CX0 + CX1) / 2, (CY0 + CY1) / 2 - (bb[1] + bb[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='c')
    post.mk('chipt', _chipt, A(5.4, 6.0, 'pop', s0=1.25), text=True)
    base = selecao_block(post, 64, Y1 + 18, 52, X1=1016, t0=5.9)
    bottom_decor_story(post, mirror=True)
    post.notes.append(f'story B: h1 {hsz}pt, vertical word 100pt y {VY0:.0f}-{VY1:.0f}, name {szn}pt, selecao baseline y={base:.0f} (<=1600)')

# ======================================================================
# SQUARE A — André stacked: logo TL, hero TR, right-edge slashes, centred athlete, 1-line name, card bar row, hash left / cheer right
# ======================================================================
def square_A(post):
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    post.glows = [(1080 * 0.95, 1080 * 0.08, 1080 * 0.9, KEY, 0.28, 4.0, 0), (1080 * 0.02, 1080 * 0.97, 1080 * 0.95, ALT, 0.22, 5.0, 1.3)]
    sdir = np.array([k60, -1.0])
    for n, (nm, xt, wd, col, st) in enumerate((('sl1', 990, 64, KEY, 0.30), ('sl2', 1090, 44, KEY, 0.42), ('sl3', 942, 5, ALT, 0.55), ('sl4', 920, 2, YELLOW, 0.65))):
        post.mk(nm, lambda c, xt=xt, wd=wd, col=col: c.slash(xt, wd, -200, 98, col), A(st, st + 0.75, 'slide', dx=sdir[0] * 520, dy=sdir[1] * 520), amb=sdrift(n, sdir))
    logo(post, 56, 52, 200)
    fh, hsz = fit('Black', cfg['hero'], 150, 690); bb = fh.getbbox(cfg['probe']); HY = 116
    hw = post.letters('hero', 1024, HY - bb[1] / S, cfg['hero'], fh, WHITE, anchor='r', t0=1.6, step=0.05, dur=0.45, kind='rise', dy=50)
    hb = HY + (bb[3] - bb[1]) / S; post.flash_t = (2.1, 0.3)
    post.mk('heroline', lambda c: c.rect(1024 - hw + 6, hb + 14, 1024, hb + 18, fill=KEY), A(2.1, 2.6, 'wipe', dir='rl'))
    post.mk('sel', lambda c: c.text((1024, hb + 30), COMMON['sel'], T('Medium', 16), GREY, tr=3, anchor='r'), A(2.3, 2.8, 'wipe', dir='rl'), text=True)
    post.mk('seltri', lambda c: tricolour(c, 1024 - twidth(T('Medium', 16), COMMON['sel'], 3) - 22, hb + 35, 120, 4, anchor='r'), A(2.5, 3.0, 'wipe', dir='rl'))
    post.athlete(cfg['photo'], cfg['mask'], cfg['crop'], 0.33, 560, 250, (580, 700), reveal=(1.0, 2.3), edge_r=0.06)
    post.mk('stlab', lambda c: c.text((56, 536), COMMON['status'], T('Medium', 13), GREY, tr=3), A(1.9, 2.4, 'wipe', dir='lr'), text=True)
    add_common_dynamics(post, (110, 440), gauge_t=(1.4, 2.6), ruler=None, cellspec=(56, 562, 8, 'l', 2.2), coord_xy=None)
    post.mk('ret2', lambda c: c.bracket(1024, 560, 22, 'br', (255, 255, 255, 150), 2), A(1.5, 2.1, 'slide', dx=30, dy=30))
    post.mk('bcode', lambda c: (barcode(c, 56, 618, 150, 16, seed=3), c.text((56, 640), 'ID 26-WCH-POL', MONO(11), DIM + (255,))), A(2.4, 3.0))
    sz = 96
    while twidth(T('Light', sz), cfg['first']) + twidth(T('Black', sz), cfg['last']) > 968: sz -= 1
    ft1, ft2 = T('Light', sz), T('Black', sz); TY = 700
    w1 = post.letters('t1', 56, TY, cfg['first'], ft1, WHITE, t0=2.6, step=0.04, dur=0.4, kind='rise', dy=36)
    post.letters('t2', 56 + w1, TY, cfg['last'], ft2, KEY, t0=2.85, step=0.04, dur=0.4, kind='rise', dy=36)
    uy = TY + ft2.getbbox('HEN')[3] / S + 22
    underline(post, uy, 1024 - 380, 1024, desc_side='l', t0=3.3)
    X0, Y0, X1, Y1 = 56, uy + 26, 1024, uy + 26 + 126
    def _card(c):
        c.chamfer(X0, Y0, X1, Y1, 22, fill=PANEL + (217,), outline=(255, 255, 255, 38), w=1)
        mid = Y0 + (Y1 - Y0) * 0.45; c.rect(X0, Y0, X0 + 6, mid, fill=KEY); c.rect(X0, mid, X0 + 6, Y1 - 22, fill=ALT)
    post.mk('card', _card, A(3.5, 4.1, 'wipe', dir='lr')); post.card_rect = (X0, Y0, X1, Y1)
    ix = X0 + 34
    fev, _ = fit('Bold', COMMON['event'], 38, 560)
    post.mk('ev', lambda c: c.text((ix, Y0 + 18), COMMON['event'], fev, WHITE), A(3.9, 4.4, 'slide', dx=-40), text=True)
    post.mk('loc', lambda c: c.text((ix, Y0 + 62), COMMON['date'] + ' // ' + COMMON['where'], T('Light', 26), GREY, tr=2), A(4.1, 4.6, 'slide', dx=-40), text=True)
    post.mk('idx', lambda c: (c.text((ix, Y0 + 98), '01 / 01', MONO(11, True), DIM + (255,), tr=3), c.ruler(ix + 76, Y0 + 100, 18, step=7, h1=4, h2=8, col=(255, 255, 255, 80))), A(4.3, 4.8), text=True)
    CX0, CY0, CX1, CY1 = X1 - 34 - 300, Y0 + 40, X1 - 34, Y0 + 40 + 66
    post.mk('chipl', lambda c: c.text((CX1, CY0 - 24), 'CATEGORIA // ' + COMMON['disc'], T('Medium', 13), GREY, tr=3, anchor='r'), A(4.3, 4.7), text=True)
    post.mk('chip', lambda c: c.chamfer(CX0, CY0, CX1, CY1, 12, fill=ALT + (26,), outline=ALT + (255,), w=1), A(4.4, 5.0, 'wipe', dir='lr'))
    def _chipt(c):
        fk, _ = fit('Bold', cfg['cat'], 38, 270); bb = fk.getbbox(cfg['cat']); c.text(((CX0 + CX1) / 2, (CY0 + CY1) / 2 - (bb[1] + bb[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='c')
    post.mk('chipt', _chipt, A(4.6, 5.2, 'pop', s0=1.25), text=True)
    base = cheer_row(post, Y1 + 18, left='hash', t0=5.0, cheer_sz=58, hash_sz=34, X0=56, X1=1024)
    post.mk('foott', lambda c: c.text((1024, 1054), COMMON['foot'], T('Regular', 12), DIM, tr=4, anchor='r'), A(5.6, 6.2), text=True)
    post.notes.append(f'square A: hero {hsz}pt, name {sz}pt, cheer baseline y={base:.0f}')

def square_B(post):
    """Leonor split: athlete left, type column right — h1 WKF WORLD / CHAMPIONSHIPS, h2 CONVOCADA, name, chip, status; Seleção block bottom-left"""
    cfg = post.cfg; KEY, ALT = post.KEY, post.ALT
    post.glows = [(1080 * 0.05, 1080 * 0.06, 1080 * 0.9, KEY, 0.28, 4.0, 0), (1080 * 0.98, 1080 * 0.97, 1080 * 0.95, ALT, 0.22, 5.0, 1.3)]
    sdir = np.array([-k60, -1.0])
    for n, (nm, xt, wd, col, st) in enumerate((('sl1', 1010, 56, KEY, 0.30), ('sl2', 1100, 40, KEY, 0.42), ('sl3', 968, 5, ALT, 0.55), ('sl4', 950, 2, YELLOW, 0.65))):
        post.mk(nm, lambda c, xt=xt, wd=wd, col=col: c.slash(xt, wd, -200, 128, col, mirror=True), A(st, st + 0.75, 'slide', dx=sdir[0] * 520, dy=sdir[1] * 520), amb=sdrift(n, sdir))
    logo(post, 824, 44, 200)
    post.athlete(cfg['photo'], cfg['mask'], cfg['crop'], 0.42, 176, 150, (880, 1040), side={'r': 0.12, 'y0': 0.35, 'y1': 0.5}, reveal=(1.0, 2.3), anchor_face=(0.7, 0.14))
    XR = 1024; CW = 484
    hsz = 50
    while twidth(T('Black', hsz), 'CHAMPIONSHIPS') > CW: hsz -= 1
    fL, fB = T('Light', hsz), T('Black', hsz); capB = (fB.getbbox('HEN')[3] - fB.getbbox('HEN')[1]) / S
    H1Y = 252; H2Y = H1Y + capB + 12
    post.mk('h1a', lambda c: c.text((XR, H1Y - fL.getbbox('WKF')[1] / S), 'WKF WORLD', fL, WHITE, anchor='r'), A(1.5, 2.1, 'slidewipe', dx=60, dir='rl'), text=True)
    post.letters('h1b', XR, H2Y - fB.getbbox('CHAMPIONSHIPS')[1] / S, 'CHAMPIONSHIPS', fB, WHITE, anchor='r', t0=1.6, step=0.04, dur=0.45, kind='rise', dy=50)
    post.flash_t = (2.1, 0.3); hb = H2Y + capB
    post.mk('heroline', lambda c: c.rect(XR - twidth(fB, 'CHAMPIONSHIPS'), hb + 12, XR, hb + 16, fill=KEY), A(2.1, 2.6, 'wipe', dir='rl'))
    post.mk('loc', lambda c: c.text((XR, hb + 26), COMMON['date'] + ' // ' + COMMON['where'], T('Bold', 22), GREY, tr=1, anchor='r'), A(2.3, 2.8, 'slide', dx=40), text=True)
    # h2
    fh = T('Black', 40); bbh = fh.getbbox(cfg['probe']); HY = hb + 72
    hw = post.letters('hero', XR, HY - bbh[1] / S, cfg['hero'], fh, KEY, anchor='r', t0=2.6, step=0.04, dur=0.4, kind='rise', dy=30)
    hb2 = HY + (bbh[3] - bbh[1]) / S
    post.mk('seltri', lambda c: tricolour(c, XR, hb2 + 14, hw, 4, anchor='r'), A(3.1, 3.6, 'wipe', dir='rl'))
    # name
    szn = 52; L1Y = hb2 + 50; L2Y = L1Y + szn * 1.0
    f1, f2 = T('Light', szn), T('Black', szn)
    post.letters('t1', XR, L1Y, cfg['first'].strip(), f1, WHITE, anchor='r', t0=3.2, step=0.04, dur=0.4, kind='rise', dy=30)
    post.letters('t2', XR, L2Y, cfg['last'], f2, WHITE, anchor='r', t0=3.4, step=0.04, dur=0.4, kind='rise', dy=30)
    uy = L2Y + f2.getbbox('HEN')[3] / S + 18
    post.mk('ul', lambda c: c.rect(XR - 260, uy, XR, uy + 4, fill=WHITE), A(3.9, 4.4, 'wipe', dir='rl'))
    post.mk('desc', lambda c: c.text((XR, uy + 12), COMMON['desc'], T('Medium', 15), GREY, tr=3, anchor='r'), A(4.1, 4.6), text=True)
    CY0 = uy + 66; CX0, CX1, CY1 = XR - 300, XR, CY0 + 70
    post.mk('chipl', lambda c: c.text((XR, CY0 - 24), 'CATEGORIA // ' + COMMON['disc'], T('Medium', 14), GREY, tr=3, anchor='r'), A(4.3, 4.7), text=True)
    post.mk('chip', lambda c: c.chamfer(CX0, CY0, CX1, CY1, 14, fill=ALT + (26,), outline=ALT + (255,), w=1), A(4.4, 5.0, 'wipe', dir='rl'))
    def _chipt(c):
        fk, _ = fit('Bold', cfg['cat'], 38, 270); bb = fk.getbbox(cfg['cat']); c.text(((CX0 + CX1) / 2, (CY0 + CY1) / 2 - (bb[1] + bb[3]) / 2 / S), cfg['cat'], fk, ALT, anchor='c')
    post.mk('chipt', _chipt, A(4.6, 5.2, 'pop', s0=1.25), text=True)
    SY = CY1 + 26
    post.mk('stlab', lambda c: c.text((XR, SY), COMMON['status'], T('Medium', 13), GREY, tr=3, anchor='r'), A(4.8, 5.3, 'wipe', dir='rl'), text=True)
    add_common_dynamics(post, (640, 120), gauge_t=(1.4, 2.6), ruler=None, cellspec=(XR, SY + 26, 8, 'r', 5.1), coord_xy=None)
    base = selecao_block(post, 56, 940, 40, X1=XR, t0=5.5, hash_sz=32)
    post.mk('bcode', lambda c: (barcode(c, 56, 1050, 120, 12, seed=3), c.text((190, 1050), 'ID 26-WCH-POL // ' + COMMON['foot'], MONO(11), DIM + (255,))), A(5.8, 6.3))
    post.notes.append(f'square B: h1 {hsz}pt, name {szn}pt, status y={SY + 44:.0f}, selecao baseline y={base:.0f}')

def build(cfgname, fmt):
    cfg = dict(CFG[cfgname]); post = Post(cfg, fmt)
    if fmt == 'story': (story_A if cfgname == 'aguiar' else story_B)(post)
    else: (square_A if cfgname == 'aguiar' else square_B)(post)
    for n in post.notes: print(n, file=sys.stderr)
    return post
