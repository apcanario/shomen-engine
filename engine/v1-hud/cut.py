import cv2, numpy as np
src=cv2.imread('leo-000.png'); h,w=src.shape[:2]
mask=np.full((h,w),cv2.GC_BGD,np.uint8)
mask[520:1800,220:990]=cv2.GC_PR_FGD
mask[520:900,220:380]=cv2.GC_BGD; mask[520:900,860:990]=cv2.GC_BGD
mask[640:900,520:670]=cv2.GC_FGD
mask[1050:1750,400:850]=cv2.GC_FGD
bg=np.zeros((1,65));fg=np.zeros((1,65))
cv2.grabCut(src,mask,None,bg,fg,10,cv2.GC_INIT_WITH_MASK)
m=((mask==1)|(mask==3)).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=((lab==k)*255).astype(np.uint8)
m=cv2.erode(m,np.ones((3,3),np.uint8))
m=cv2.GaussianBlur(m,(0,0),1.6)
cv2.imwrite('leo_mask.png',m)
prev=(src.astype(float)*(m[...,None]/255)+np.array([60,20,20])*(1-m[...,None]/255)).astype(np.uint8)
cv2.imwrite('leo_prev.jpg',cv2.resize(prev,None,fx=0.5,fy=0.5))
ys,xs=np.where(m>128); print(xs.min(),xs.max(),ys.min(),ys.max())
