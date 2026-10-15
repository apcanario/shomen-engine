import cv2, numpy as np
src = cv2.imread('/home/claude/leo_src.jpg'); h, w = src.shape[:2]
hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
orange = ((H >= 2) & (H <= 22) & (S > 110) & (V > 90))
blue = ((H >= 95) & (H <= 130) & (S > 70) & (V > 50))
purple = ((H >= 115) & (H <= 150) & (S > 50) & (V > 40))
carve = (orange | blue | purple).astype(np.uint8)
# protect face / skin
carve[1130:1330, 860:1020] = 0; carve[2250:2450, 800:1120] = 0; carve[1420:1500, 770:850] = 0
m0 = cv2.imread('/home/claude/leo_mask.png', 0)
mask = np.full((h, w), cv2.GC_BGD, np.uint8)
mask[m0 > 128] = cv2.GC_PR_FGD
mask[carve > 0] = cv2.GC_BGD
mask[1170:1300, 905:995] = cv2.GC_FGD; mask[2000:2150, 905:990] = cv2.GC_BGD; mask[2280:2400, 845:905] = cv2.GC_FGD; mask[2280:2400, 1000:1060] = cv2.GC_FGD
mask[1360:1760, 830:1080] = cv2.GC_FGD
mask[1440:1480, 790:840] = cv2.GC_FGD
mask[1800:2250, 840:900] = cv2.GC_FGD; mask[1800:2250, 990:1050] = cv2.GC_FGD
bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
cv2.grabCut(src, mask, None, bg, fg, 8, cv2.GC_INIT_WITH_MASK)
m = ((mask == 1) | (mask == 3)).astype(np.uint8) * 255
m[carve > 0] = 0
m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, 4]); m = ((lab == k) * 255).astype(np.uint8)
m = cv2.erode(m, np.ones((3, 3), np.uint8)); m = cv2.GaussianBlur(m, (0, 0), 1.6)
cv2.imwrite('/home/claude/leo_mask.png', m)
prev = (src.astype(float) * (m[..., None] / 255) + np.array([60, 20, 120]) * (1 - m[..., None] / 255)).astype(np.uint8)
cv2.imwrite('/home/claude/leo_prev.jpg', cv2.resize(prev[1050:2600, 600:1300], None, fx=0.6, fy=0.6))
ys, xs = np.where(m > 128); print('bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
