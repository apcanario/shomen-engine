"""Shomen HUD engine v2 — national-team call-up posts (Portugal palette: red / green / yellow).
Coordinates in 1x px. Layers rasterised at 2x, resized to OS (1 = video, 2 = still).
Usage: python3 hud.py <cfg> <fmt> still | test | <f0> <f1>
"""
import numpy as np, cv2, subprocess, sys, math, os, importlib
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/home/claude')
from logo import logo_rgba

# ---------------- palette ----------------
RED = (255, 42, 80); GREEN = (34, 224, 128); YELLOW = (255, 210, 63)
WHITE = (245, 246, 248); GREY = (150, 156, 168); DIM = (70, 76, 90); BG = (9, 10, 14); PANEL = (14, 16, 22)
FD = '/mnt/skills/examples/canvas-design/canvas-fonts/'
TDIR = '/home/claude/fonts'
S = 2                       # raster scale for layers
OS = 1                      # output scale (set by main)
k60 = 1 / math.tan(math.radians(60))
FPS = 30; DUR = 20; NF = FPS * DUR

def P(v): return int(round(v * S))
def sm(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def ease(t, a, b):
    x = min(1, max(0, (t - a) / (b - a))); return 1 - (1 - x) ** 3
def ease_io(t, a, b):
    x = min(1, max(0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def ease_back(t, a, b, s=1.4):
    x = min(1, max(0, (t - a) / (b - a))); x -= 1; return x * x * ((s + 1) * x + s) + 1

_fcache = {}
def T(weight, sz, sc=None):
    assert weight not in ('Thin', 'ExtraLight')
    sc = S if sc is None else sc
    key = (weight, sz, sc)
    if key not in _fcache:
        p = f'{TDIR}/Tomorrow-{weight}.ttf'
        _fcache[key] = ImageFont.truetype(p, int(sz * sc))
    return _fcache[key]
def MONO(sz, bold=False, sc=None):
    sc = S if sc is None else sc
    key = ('mono', sz, bold, sc)
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(FD + ('GeistMono-Bold.ttf' if bold else 'GeistMono-Regular.ttf'), int(sz * sc))
    return _fcache[key]
def twidth(font, text, tr=0):
    return (sum(font.getlength(c) + tr * S for c in text) - tr * S) / S
def fit(weight, text, start, maxw, tr=0, floor=10):
    sz = start
    while sz > floor:
        f = T(weight, sz)
        if twidth(f, text, tr) <= maxw: return f, sz
        sz -= 1
    return T(weight, sz), sz

# ---------------- raster context ----------------
class Ctx:
    def __init__(s, W, H):
        s.W, s.H = W, H
        s.img = Image.new('RGBA', (P(W), P(H)), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.img, 'RGBA')
    def text(s, xy, t, font, fill, tr=0, anchor='l'):
        x, y = P(xy[0]), P(xy[1]); tr = tr * S; wt = sum(font.getlength(c) + tr for c in t) - tr
        if anchor == 'r': x -= wt
        if anchor == 'c': x -= wt / 2
        for c in t: s.d.text((x, y), c, font=font, fill=fill); x += font.getlength(c) + tr
        return wt / S
    def ruler(s, x, y, n, step=8, h1=6, h2=12, col=(255, 255, 255, 90), vert=False):
        for i in range(n):
            h = h2 if i % 5 == 0 else h1
            if vert: s.d.line([(P(x), P(y + i * step)), (P(x + h), P(y + i * step))], fill=col, width=S)
            else: s.d.line([(P(x + i * step), P(y)), (P(x + i * step), P(y + h))], fill=col, width=S)
    def bracket(s, x, y, sz, corner, col, w=2):
        x, y, sz = P(x), P(y), P(sz); w = int(w * S); sx = 1 if 'l' in corner else -1; sy = 1 if 't' in corner else -1
        s.d.line([(x, y), (x + sx * sz, y)], fill=col, width=w); s.d.line([(x, y), (x, y + sy * sz)], fill=col, width=w)
    def slash(s, xt, wd, ya, yb, col, yref=0, mirror=False):
        pts = [(xt - k60 * (ya - yref), ya), (xt + wd - k60 * (ya - yref), ya), (xt + wd - k60 * (yb - yref), yb), (xt - k60 * (yb - yref), yb)]
        if mirror: pts = [(s.W - a, b) for a, b in pts]
        s.d.polygon([(P(a), P(b)) for a, b in pts], fill=col)
    def poly(s, pts, fill=None, outline=None, w=1):
        pp = [(P(a), P(b)) for a, b in pts]
        if fill: s.d.polygon(pp, fill=fill)
        if outline: s.d.line(pp + [pp[0]], fill=outline, width=int(w * S))
    def rect(s, x0, y0, x1, y1, fill=None, outline=None, w=1):
        s.d.rectangle([P(x0), P(y0), P(x1), P(y1)], fill=fill, outline=outline, width=int(w * S) if outline else 0)
    def line(s, pts, col, w=1):
        s.d.line([(P(a), P(b)) for a, b in pts], fill=col, width=max(1, int(w * S)))
    def circle(s, cx, cy, r, fill=None, outline=None, w=1):
        s.d.ellipse([P(cx - r), P(cy - r), P(cx + r), P(cy + r)], fill=fill, outline=outline, width=int(w * S) if outline else 0)
    def arc(s, cx, cy, r, a0, a1, col, w=2):
        s.d.arc([P(cx - r), P(cy - r), P(cx + r), P(cy + r)], a0, a1, fill=col, width=max(1, int(w * S)))
    def chamfer(s, x0, y0, x1, y1, ch=28, mirror=False, fill=None, outline=None, w=1):
        if not mirror: poly = [(x0, y0), (x1 - ch, y0), (x1, y0 + ch), (x1, y1), (x0 + ch, y1), (x0, y1 - ch)]
        else: poly = [(x0 + ch, y0), (x1, y0), (x1, y1 - ch), (x1 - ch, y1), (x0, y1), (x0, y0 + ch)]
        s.poly(poly, fill=fill, outline=outline, w=w)
    def layer(s, anchor=(0.5, 0.5)):
        im = s.img if OS == S else s.img.resize((s.W * OS, s.H * OS), Image.LANCZOS)
        bb = im.getbbox()
        if bb is None: return None
        a = np.array(im.crop(bb)).astype(np.float32) / 255.
        return {'rgb': a[..., :3], 'a': a[..., 3], 'x': bb[0], 'y': bb[1], 'anchor': anchor}

def comp(fr, L, dx=0, dy=0, alpha=1.0, clip=None, clipy=None, scale=None, glow=0.0):
    """composite layer onto float frame (OS scale). dx,dy in 1x px. clip=(fx0,fx1) horizontal, clipy=(fy0,fy1) vertical."""
    if L is None or alpha <= 0.003: return
    rgb, a = L['rgb'], L['a']; x = L['x']; y = L['y']
    if scale is not None and abs(scale - 1) > 1e-3:
        h, w = a.shape; nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        rgb = cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_LINEAR); a = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_LINEAR)
        ax, ay = L.get('anchor', (0.5, 0.5)); x -= (nw - w) * ax; y -= (nh - h) * ay
    if clip is not None:
        h, w = a.shape; m = np.zeros(w, np.float32); c0, c1 = int(w * clip[0]), int(w * clip[1]); m[c0:c1] = 1; a = a * m[None, :]
    if clipy is not None:
        h, w = a.shape; m = np.zeros(h, np.float32); c0, c1 = int(h * clipy[0]), int(h * clipy[1]); m[c0:c1] = 1; a = a * m[:, None]
    if glow > 0:
        # soft additive bloom of the layer (used for flashes)
        g = cv2.GaussianBlur(a * glow, (0, 0), 12 * OS)
        gx, gy = int(round(x + dx * OS)), int(round(y + dy * OS)); h, w = g.shape
        H, W = fr.shape[:2]; x0, y0 = max(0, gx), max(0, gy); x1, y1 = min(W, gx + w), min(H, gy + h)
        if x1 > x0 and y1 > y0:
            fr[y0:y1, x0:x1] += g[y0 - gy:y1 - gy, x0 - gx:x1 - gx, None] * rgb[y0 - gy:y1 - gy, x0 - gx:x1 - gx].mean(axis=(0, 1))
    x = int(round(x + dx * OS)); y = int(round(y + dy * OS)); h, w = a.shape
    H, W = fr.shape[:2]
    x0, y0 = max(0, x), max(0, y); x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0: return
    sa = a[y0 - y:y1 - y, x0 - x:x1 - x, None] * alpha; sr = rgb[y0 - y:y1 - y, x0 - x:x1 - x]
    reg = fr[y0:y1, x0:x1]; reg[:] = reg * (1 - sa) + sr * sa

# ---------------- animation helpers ----------------
def entry(t, A):
    """A = dict(t0,t1,kind,...) -> dx,dy,alpha,clip,clipy,scale"""
    if A is None: return 0, 0, 1, None, None, None
    t0, t1 = A['t0'], A['t1']; k = A.get('kind', 'fade')
    if t < t0: return 0, 0, 0, None, None, None
    e = ease(t, t0, t1)
    if k == 'fade': return 0, 0, e, None, None, None
    if k == 'slide': return (1 - e) * A.get('dx', 0), (1 - e) * A.get('dy', 0), e if A.get('fade', True) else 1, None, None, None
    if k == 'wipe':
        d = A.get('dir', 'lr')
        if d == 'lr': return 0, 0, 1, (0, e), None, None
        if d == 'rl': return 0, 0, 1, (1 - e, 1), None, None
        if d == 'tb': return 0, 0, 1, None, (0, e), None
        if d == 'bt': return 0, 0, 1, None, (1 - e, 1), None
    if k == 'slidewipe':
        d = A.get('dir', 'lr'); dx = (1 - e) * A.get('dx', 0)
        return dx, 0, e, ((0, e) if d == 'lr' else (1 - e, 1)), None, None
    if k == 'pop':
        eb = ease_back(t, t0, t1, A.get('over', 1.3)); s0 = A.get('s0', 1.35)
        return 0, 0, e, None, None, s0 + (1 - s0) * eb
    if k == 'rise':
        eb = ease(t, t0, t1); return 0, (1 - eb) * A.get('dy', 40), eb, None, None, None
    if k == 'zoomfade':
        return 0, 0, e, None, None, A.get('s0', 1.12) + (1 - A.get('s0', 1.12)) * e
    return 0, 0, e, None, None, None

# ---------------- build / render ----------------
class Post:
    def __init__(self, cfg, fmt):
        self.cfg = cfg; self.fmt = fmt
        self.W1, self.H1 = (1080, 1920) if fmt == 'story' else (1080, 1080)
        self.KEY = cfg['key']; self.ALT = cfg['alt']
        self.L = {}; self.A = {}; self.order1 = []; self.order2 = []; self.dyn = []; self.notes = []
        self.ath = None
        self.card_rect = None; self.scrim = None
        self.flash_t = None   # (t0, strength) full-frame key-colour flash + micro shake when the hero lands
        self.glows = []
    # --- layer registration ---
    def mk(self, name, fn, anim=None, text=False, anchor=(0.5, 0.5), amb=None):
        c = Ctx(self.W1, self.H1); fn(c); L = c.layer(anchor)
        if L is None: return
        L['amb'] = amb
        self.L[name] = L; self.A[name] = anim; (self.order2 if text else self.order1).append(name)
    def letters(self, name, x, y, text, font, fill, tr=0, anchor='l', t0=0, step=0.045, dur=0.42, kind='rise', dy=46, amb=None, glowflash=False):
        """one layer per glyph, staggered entry. returns total width (1x)."""
        wt = twidth(font, text, tr)
        xs = x - wt if anchor == 'r' else (x - wt / 2 if anchor == 'c' else x)
        cx = xs; i = 0
        for ch in text:
            if ch != ' ':
                cxx = cx
                self.mk(f'{name}#{i}', lambda c, cxx=cxx, ch=ch: c.text((cxx, y), ch, font, fill),
                        {'t0': t0 + i * step, 't1': t0 + i * step + dur, 'kind': kind, 'dy': dy, 's0': 1.6}, text=True, anchor=(0.5, 0.6), amb=amb)
            cx += font.getlength(ch) / S + tr; i += 1
        return wt
    def dynamic(self, fn): self.dyn.append(fn)
    # --- athlete ---
    def athlete(self, photo, mask, crop, scale, cx, top, fade, side=None, reveal=(1.0, 2.4), halo_col=None, anchor_face=(0.5, 0.14), edge_r=None):
        src = cv2.cvtColor(cv2.imread(photo), cv2.COLOR_BGR2RGB).astype(np.float32)
        msk = cv2.imread(mask, 0).astype(np.float32) / 255
        y0, y1, x0, x1 = crop; src = src[y0:y1, x0:x1]; msk = msk[y0:y1, x0:x1]
        Z = 1.06
        sc = scale * OS * Z
        nw, nh = int(src.shape[1] * sc), int(src.shape[0] * sc)
        src = cv2.resize(src, (nw, nh), interpolation=cv2.INTER_LANCZOS4 if sc > 1 else cv2.INTER_AREA); msk = cv2.resize(msk, (nw, nh), interpolation=cv2.INTER_LINEAR).clip(0, 1)
        a_ = src / 255.; a_ = np.clip((a_ - 0.5) * 1.09 + 0.515, 0, 1); a_[..., 0] *= 0.975; a_[..., 2] *= 1.03
        # side fade for frame-cut edges (source-relative fractions)
        if side:
            xs = np.linspace(0, 1, nw, dtype=np.float32); ys = np.linspace(0, 1, nh, dtype=np.float32)
            sf = np.ones(nw, np.float32)
            if side.get('l'): sf *= sm(0, side['l'], xs)
            if side.get('r'): sf *= sm(1, 1 - side['r'], xs)
            yw = sm(side.get('y0', 0.4), side.get('y1', 0.55), ys)
            msk = msk * (1 - yw[:, None] * (1 - sf[None, :]))
        self.ath = dict(rgb=np.clip(a_, 0, 1), m=msk, nw=nw, nh=nh, Z=Z, cx=cx, top=top, fade=fade, reveal=reveal, af=anchor_face,
                        cedge=bool(edge_r), halo=cv2.GaussianBlur(msk, (0, 0), 11 * OS), hcol=np.array(halo_col or self.KEY, np.float32) / 255.)
    def draw_athlete(self, fr, t, still=False):
        A = self.ath
        if A is None: return None
        H, W = fr.shape[:2]
        r0, r1 = A['reveal']; rev = ease(t, r0, r1)
        if rev <= 0: return None
        z = (1.0 + 0.06 * min(1, t / DUR)) / A['Z'] if not still else 1.0 / A['Z'] * 1.03
        w, h = int(A['nw'] * z), int(A['nh'] * z)
        rgb = cv2.resize(A['rgb'], (w, h), interpolation=cv2.INTER_AREA); m = cv2.resize(A['m'], (w, h), interpolation=cv2.INTER_AREA); hl = cv2.resize(A['halo'], (w, h), interpolation=cv2.INTER_AREA)
        bw, bh = A['nw'] / A['Z'], A['nh'] / A['Z']
        x = A['cx'] * OS - bw / 2 - (w - bw) * A['af'][0]; y = A['top'] * OS - (h - bh) * A['af'][1] + (1 - rev) * 30 * OS
        x = int(round(x)); y = int(round(y))
        yy = np.arange(H, dtype=np.float32); f0, f1 = A['fade']
        fadeY = 1 - sm(f0 * OS, f1 * OS, yy)
        y0 = max(0, y); y1 = min(H, y + h); x0 = max(0, x); x1 = min(W, x + w)
        if y1 <= y0 or x1 <= x0: return None
        fy = fadeY[y0:y1, None]
        m_ = m[y0 - y:y1 - y, x0 - x:x1 - x]; hl_ = hl[y0 - y:y1 - y, x0 - x:x1 - x]; rgb_ = rgb[y0 - y:y1 - y, x0 - x:x1 - x]
        if A.get('cedge') and x1 == W:
            cols = np.arange(x0, x1, dtype=np.float32); m_ = m_ * sm(W, W - 70 * OS, cols)[None, :]
        # scan reveal: rows above the scan line visible; bright band at the scan line
        if rev < 1:
            sy = y + rev * h * 1.05
            rows = np.arange(y0, y1, dtype=np.float32)
            vis = (1 - sm(sy - 18 * OS, sy + 4 * OS, rows))[:, None]
            band = np.exp(-((rows - sy) / (5.0 * OS)) ** 2)[:, None] * (1 - rev) ** 0.5
            al = m_ * fy * vis
            reg = fr[y0:y1, x0:x1]
            reg += (hl_ * vis * fy)[..., None] * A['hcol'] * 0.10 * rev
            reg[:] = reg * (1 - al[..., None]) + rgb_ * al[..., None]
            # scan band across the athlete silhouette (+ faint full-width line)
            reg += (band * (m_ * 0.9 + 0.08))[..., None] * A['hcol'] * 0.9
            fr[y0:y1, :] += (band * 0.05)[..., None] * A['hcol']
        else:
            al = m_ * fy
            reg = fr[y0:y1, x0:x1]
            pulse = 0.10 + (0.03 * math.sin(2 * math.pi * t / 5.0) if not still else 0)
            reg += (hl_ * fy)[..., None] * A['hcol'] * pulse
            reg[:] = reg * (1 - al[..., None]) + rgb_ * al[..., None]
        full = np.zeros((H, W), np.float32); full[y0:y1, x0:x1] = al
        return full
    # --- background ---
    def prep(self):
        H, W = self.H1 * OS, self.W1 * OS
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        def glow(cx, cy, r, col):
            dd = np.sqrt((xx - cx * OS) ** 2 + (yy - cy * OS) ** 2) / (r * OS); return (np.clip(1 - dd, 0, 1) ** 2)[..., None] * np.array(col, np.float32) / 255.
        self.BASE = np.zeros((H, W, 3), np.float32) + np.array(BG, np.float32) / 255.
        self.G = [(glow(cx, cy, r, col), st, per, ph) for cx, cy, r, col, st, per, ph in self.glows]
        c = Ctx(self.W1, self.H1)
        for x in range(0, P(self.W1), P(54)): c.d.line([(x, 0), (x, P(self.H1))], fill=(255, 255, 255, 255), width=S)
        for y in range(0, P(self.H1), P(54)): c.d.line([(0, y), (P(self.W1), y)], fill=(255, 255, 255, 255), width=S)
        im = c.img if OS == S else c.img.resize((W, H), Image.LANCZOS)
        self.GRID = np.array(im)[..., 3].astype(np.float32) / 255. * 0.045
        rng = np.random.default_rng(3)
        self.NOISE = [rng.normal(0, 0.016 if OS == 1 else 0.021, (H, W, 1)).astype(np.float32) for _ in range(6)]
        del yy, xx
    def frame(self, i, still=False):
        t = i / FPS; H, W = self.H1 * OS, self.W1 * OS
        gin = ease(t, 0.0, 1.2) if not still else 1
        fr = self.BASE.copy()
        for g, st, per, ph in self.G:
            p = st * (1 + (0.22 * math.sin(2 * math.pi * t / per + ph) if not still else 0)); fr += g * (p * gin)
        full = self.draw_athlete(fr, t, still)
        g = self.GRID * (ease(t, 0.2, 1.4) if not still else 1)
        if full is not None: g = g * (1 - full)
        fr = fr * (1 - g[..., None]) + g[..., None]
        if not still and t > 1.5:
            ph = ((t - 1.5) % 5.0) / 1.6
            if ph < 1:
                ys = int(ph * H); bnd = np.exp(-((np.arange(H) - ys) / (18.0 * OS)) ** 2).astype(np.float32) * 0.06
                fr += bnd[:, None, None] * np.array(self.KEY, np.float32) / 255.
        # pass 1 graphics
        for nm in self.order1: self._comp(fr, nm, t, still)
        # card light sweep
        if not still and self.card_rect and t > 5.8:
            X0, Y0, X1, Y1 = [v * OS for v in self.card_rect]; ph = ((t - 5.8) % 4.0) / 0.9
            if ph < 1:
                xs = X0 + ph * (X1 - X0); xs_ = np.arange(int(X0), int(X1)); bnd = np.exp(-((xs_ - xs) / (40.0 * OS)) ** 2).astype(np.float32) * 0.10
                fr[int(Y0):int(Y1), int(X0):int(X1)] += bnd[None, :, None]
        # dynamic PIL draws (graphics)
        if self.dyn:
            im = Image.fromarray((np.clip(fr, 0, 1) * 255).astype(np.uint8)).convert('RGBA'); ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov, 'RGBA')
            for fn in self.dyn: fn(d, t, still)
            im.alpha_composite(ov); fr = np.array(im.convert('RGB')).astype(np.float32) / 255.
        # pass 2 text + logo
        for nm in self.order2: self._comp(fr, nm, t, still)
        if not still and self.flash_t:
            f0, st = self.flash_t
            if f0 <= t < f0 + 0.45:
                k = 1 - (t - f0) / 0.45; fr += (k ** 2) * st * np.array(self.KEY, np.float32) / 255. * 0.5 + (k ** 3) * st * 0.08
            if f0 <= t < f0 + 0.3:
                rng = np.random.default_rng(i); k = 1 - (t - f0) / 0.3; sx, sy = int(round(rng.uniform(-5, 5) * k * OS)), int(round(rng.uniform(-4, 4) * k * OS))
                if sx or sy: fr = np.roll(fr, (sy, sx), axis=(0, 1))
        fr += self.NOISE[i % 6]
        return (np.clip(fr, 0, 1) * 255).astype(np.uint8)
    def _comp(self, fr, nm, t, still):
        L = self.L[nm]; A = self.A.get(nm)
        if still:
            dx, dy, al, cl, cly, sc = 0, 0, 1, None, None, None
        else:
            dx, dy, al, cl, cly, sc = entry(t, A)
        if al <= 0: return
        amb = L.get('amb')
        if amb and not still:
            adx, ady, aal, asc = amb(t); dx += adx; dy += ady; al *= aal
            if asc is not None: sc = (sc or 1) * asc
        gl = 0.0
        if A and A.get('flash') and not still:
            t0, t1 = A['t0'], A['t1']
            if t0 <= t < t1 + 0.5: gl = 0.9 * max(0, 1 - (t - t0) / (t1 - t0 + 0.5))
        comp(fr, L, dx, dy, al, cl, cly, sc, glow=gl)

def render(post, name, mode, a0=0, a1=0):
    W, H = post.W1 * OS, post.H1 * OS
    if mode == 'still':
        im = Image.fromarray(post.frame(int(19.5 * FPS), still=True))
        out = f'/mnt/user-data/outputs/{name}.png'; im.save(out, optimize=True)
        # QA preview with safe zones
        pv = im.resize((W // (2 * OS), H // (2 * OS)), Image.LANCZOS).convert('RGBA'); ov = Image.new('RGBA', pv.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        if post.fmt == 'story':
            od.rectangle([0, 0, pv.width, 125], fill=(255, 230, 0, 40)); od.rectangle([0, 800, pv.width, pv.height], fill=(255, 230, 0, 40))
        else:
            od.rectangle([0, 0, pv.width, 67], fill=(255, 230, 0, 30)); od.rectangle([0, 472, pv.width, pv.height], fill=(255, 230, 0, 30))
        Image.alpha_composite(pv, ov).convert('RGB').save(f'/home/claude/qa_{name}.png')
        print('saved', out)
    elif mode == 'test':
        import time; t0 = time.time()
        ts = (0.9, 2.0, 3.4, 5.2, 9.0, 19.9)
        ims = [Image.fromarray(post.frame(int(s * FPS))) for s in ts]
        print('s/frame', (time.time() - t0) / len(ts), file=sys.stderr)
        sw = 360; sh_ = int(sw * H / W)
        sh = Image.new('RGB', (sw * len(ims), sh_)); [sh.paste(im.resize((sw, sh_), Image.LANCZOS), (sw * k, 0)) for k, im in enumerate(ims)]
        sh.save(f'/home/claude/test_{name}.png')
    else:
        out = f'/home/claude/seg_{name}_{a0:04d}.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '10', '-pix_fmt', 'yuv420p', '-r', str(FPS), out], stdin=subprocess.PIPE)
        for i in range(a0, a1): p.stdin.write(post.frame(i).tobytes())
        p.stdin.close(); p.wait(); print('wrote', out, a0, a1)

if __name__ == '__main__':
    cfgname, fmt, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    OS = 2 if mode == 'still' else 1
    import hud as _H; _H.OS = OS
    import layouts
    post = layouts.build(cfgname, fmt)
    post.prep()
    name = f'shomen-{cfgname}-convocatoria-{fmt}'
    if mode in ('still', 'test'): render(post, name, mode)
    else: render(post, name, 'seg', int(sys.argv[3]), int(sys.argv[4]))
