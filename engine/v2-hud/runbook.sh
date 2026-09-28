# HUD v2 — call-ups / national team / results. 4 deliverables per athlete from one engine.
# Run from /home/claude after `bash shomen/setup.sh v2`.
# 0. inputs: athlete photo(s) in /mnt/user-data/uploads/. Logo: logo.py vectorises logo_mask_raw.png
#    (white threshold crop of an existing post) — or point logo_rgba at the white logo PNG if Pedro uploaded it.
# 1. add/edit the athlete's CFG entry + COMMON in layouts.py (photo, mask, crop bbox, key/alt colour, hero word, category, event, coords)
# 2. cut-out: copy cut_and.py / cut_leo.py as a template, set GrabCut boxes from a gridded preview, VIEW *_prev.jpg
python3 cut_and.py
# 3. still + test
python3 hud.py <cfg> story still      # 2x PNG in outputs + qa_*.png with safe-zone bands
python3 hud.py <cfg> story test       # 6-keyframe contact sheet + s/frame
# 4. video (story ~0.16 s/frame → 2 segments; square ~0.07 s/frame → one segment 0 600)
timeout 280 python3 hud.py <cfg> story 0 300; timeout 280 python3 hud.py <cfg> story 300 600
printf "file seg_shomen-<cfg>-<slug>-story_0000.mp4\nfile seg_shomen-<cfg>-<slug>-story_0300.mp4\n" > list.txt
ffmpeg -y -loglevel error -f concat -i list.txt -c:v libx264 -preset fast -b:v 9M -maxrate 13M -bufsize 18M -pix_fmt yuv420p -profile:v high -r 30 -movflags +faststart /mnt/user-data/outputs/<name>.mp4
# squares: encode at -b:v 8M -maxrate 11M -bufsize 16M
# 5. verify with ffprobe + 3 extracted frames. Never nest a heredoc inside a heredoc when pasting.
