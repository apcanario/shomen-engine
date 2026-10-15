"""Shōmen logo from the brand SVG (Drive: 'Shomen - Logo (Red).svg', single path, M/L/H/V/Z only).
logo_rgba(width, color) -> RGBA PIL image, mark + wordmark, given target width (px). Rendered white in HUD."""
import re, numpy as np
from PIL import Image, ImageDraw
from matplotlib.path import Path as _MP

SVG = '/home/claude/assets/shomen-logo.svg'
_d = re.search(r'd="([^"]+)"', open(SVG).read()).group(1)
_tok = re.findall(r'[MLHVZ]|-?\d*\.?\d+', _d)
POLYS = []; cur = []; x = y = 0.0; i = 0
while i < len(_tok):
    c = _tok[i]
    if c == 'M': x, y = float(_tok[i + 1]), float(_tok[i + 2]); cur = [(x, y)]; i += 3
    elif c == 'L': x, y = float(_tok[i + 1]), float(_tok[i + 2]); cur.append((x, y)); i += 3
    elif c == 'H': x = float(_tok[i + 1]); cur.append((x, y)); i += 2
    elif c == 'V': y = float(_tok[i + 1]); cur.append((x, y)); i += 2
    elif c == 'Z':
        if len(cur) > 2: POLYS.append(cur)
        cur = []; i += 1
    else: i += 1
LW, LH = 960.0, 832.0
# nesting depth -> outer (even depth) or hole (odd depth)
_paths = [_MP(p) for p in POLYS]
DEPTH = [sum(1 for j, q in enumerate(_paths) if j != k and q.contains_point(POLYS[k][0])) for k in range(len(POLYS))]

def logo_rgba(width, color=(255, 255, 255)):
    SS = 4; sc = width * SS / LW; w, h = int(round(LW * sc)), int(round(LH * sc))
    im = Image.new('L', (w, h), 0); d = ImageDraw.Draw(im)
    for pts, dp in zip(POLYS, DEPTH):
        if dp % 2 == 0: d.polygon([(px * sc, py * sc) for px, py in pts], fill=255)
    for pts, dp in zip(POLYS, DEPTH):
        if dp % 2 == 1: d.polygon([(px * sc, py * sc) for px, py in pts], fill=0)
    im = im.resize((max(1, w // SS), max(1, h // SS)), Image.LANCZOS)
    a = np.array(im); out = np.zeros((a.shape[0], a.shape[1], 4), np.uint8); out[..., :3] = color; out[..., 3] = a
    return Image.fromarray(out)

if __name__ == '__main__':
    lg = logo_rgba(600); bg = Image.new('RGBA', lg.size, (9, 10, 14, 255)); bg.alpha_composite(lg); bg.convert('RGB').save('/home/claude/logo_vec_test.png'); print(lg.size, len(POLYS), DEPTH)
