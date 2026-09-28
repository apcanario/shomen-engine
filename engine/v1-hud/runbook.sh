# HUD v1 — HOJE / AMANHÃ story (20 s video + 2x still). Run from /home/claude after `bash shomen/setup.sh v1`.
# 0. inputs: logo PNG + athlete photo in /mnt/user-data/uploads/  (PDF photo → pdfimages -png file.pdf leo)
# 1. edit CONFIG in vid.py (text, photo, crop, FX flags — FX stay False unless Pedro asked)
# 2. cut-out: edit GrabCut boxes in cut.py from a gridded preview (spec §6), then:
python3 cut.py                      # → leo_mask.png + leo_prev.jpg  (VIEW the preview before going on)
python3 vid.py test                 # → vid_test.png keyframes; stderr prints "hero text ends at y=" (≤1600) and any font FALLBACK
# 3. render (300 s limit per command, ~0.45 s/frame clean; with FX ~0.26 s/frame → 2 segments of 300)
timeout 285 python3 vid.py 0 200
timeout 285 python3 vid.py 200 400
timeout 285 python3 vid.py 400 600
# 4. encode
printf "file seg_0000.mp4\nfile seg_0200.mp4\nfile seg_0400.mp4\n" > list.txt
timeout 290 ffmpeg -y -loglevel error -f concat -i list.txt -c:v libx264 -preset fast -b:v 9M -maxrate 13M -bufsize 18M \
  -pix_fmt yuv420p -profile:v high -r 30 -movflags +faststart /mnt/user-data/outputs/shomen-<athlete>-<WHEN>-story.mp4
# FX on: -b:v 11M -maxrate 15M -bufsize 22M and suffix -vhs
# 4b. still: python3 compose_still.py → 2x PNG + qa.png (safe-zone bands)
# 5. verify: ffprobe duration/size/fps; pull 3 frames (2.0 s, ~8 s, 19.5 s) and view them
