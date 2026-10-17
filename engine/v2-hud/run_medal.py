"""Runner — Leonor bronze MEDAL WON (window build). usage: python3 run_medal.py <story|portrait> <still|test|f0 f1>"""
import sys
sys.path.insert(0, '/home/claude')
import hud
fmt, mode = sys.argv[1], sys.argv[2]
hud.OS = 2 if mode == 'still' else 1
import layouts, layouts_medal
post = layouts_medal.build('leonor_medal', fmt)
post.prep()
name = f'shomen-leonor-bronze-medal-{fmt}' + ('-glitch' if layouts_medal.FX_ON else '')
if mode in ('still', 'test'):
    hud.render(post, name, mode)
    if mode == 'still' and fmt == 'portrait':
        from PIL import Image, ImageDraw
        im = Image.open(f'/mnt/user-data/outputs/{name}.png'); pv = im.resize((540, 720), Image.LANCZOS).convert('RGBA')
        ov = Image.new('RGBA', pv.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        od.rectangle([0, 0, 540, 30], fill=(255, 230, 0, 40)); od.rectangle([0, 690, 540, 720], fill=(255, 230, 0, 40))
        Image.alpha_composite(pv, ov).convert('RGB').save(f'/home/claude/qa_{name}.png')
else:
    hud.render(post, name, 'seg', int(sys.argv[2]), int(sys.argv[3]))
