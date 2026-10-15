import sys
sys.path.insert(0, '/home/claude')
import hud
cfgname, fmt, mode = sys.argv[1], sys.argv[2], sys.argv[3]
hud.OS = 2 if mode == 'still' else 1
import layouts, layouts_bronze
post = layouts_bronze.build(cfgname, fmt)
post.prep()
name = f'shomen-leonor-bronze-{fmt}' + ('-glitch' if layouts_bronze.FX_ON else '')
if mode in ('still', 'test'): hud.render(post, name, mode)
else: hud.render(post, name, 'seg', int(sys.argv[3]), int(sys.argv[4]))
