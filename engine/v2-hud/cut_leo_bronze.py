import cv2, numpy as np
src = cv2.imread('/home/claude/leo_src.jpg'); h, w = src.shape[:2]
mask = np.full((h, w), cv2.GC_BGD, np.uint8)
mask[1100:2570, 700:1170] = cv2.GC_PR_FGD
# carve empty corners above the shoulders
mask[1100:1330, 700:850] = cv2.GC_BGD; mask[1100:1330, 1030:1170] = cv2.GC_BGD
mask[1100:1150, 700:1170] = cv2.GC_BGD
# sure foreground: face, torso core, fist, legs
mask[1170:1300, 900:985] = cv2.GC_FGD
mask[1360:1760, 830:1080] = cv2.GC_FGD
mask[1440:1480, 790:840] = cv2.GC_FGD
mask[1800:2250, 830:1060] = cv2.GC_FGD
bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
cv2.grabCut(src, mask, None, bg, fg, 10, cv2.GC_INIT_WITH_MASK)
m = ((mask == 1) | (mask == 3)).astype(np.uint8) * 255
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, 4]); m = ((lab == k) * 255).astype(np.uint8)
m = cv2.erode(m, np.ones((3, 3), np.uint8)); m = cv2.GaussianBlur(m, (0, 0), 1.6)
cv2.imwrite('/home/claude/leo_mask.png', m)
prev = (src.astype(float) * (m[..., None] / 255) + np.array([60, 20, 120]) * (1 - m[..., None] / 255)).astype(np.uint8)
cv2.imwrite('/home/claude/leo_prev.jpg', cv2.resize(prev[1050:2600, 600:1300], None, fx=0.6, fy=0.6))
ys, xs = np.where(m > 128); print('bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
