import cv2, numpy as np
src=cv2.imread('/mnt/user-data/uploads/1000133287.jpg'); h,w=src.shape[:2]
mask=np.full((h,w),cv2.GC_BGD,np.uint8)
mask[90:1900,0:1080]=cv2.GC_PR_FGD
mask[90:820,0:250]=cv2.GC_BGD; mask[90:930,900:1080]=cv2.GC_BGD; mask[1500:1982,1000:1080]=cv2.GC_BGD
mask[90:150,0:400]=cv2.GC_BGD; mask[90:130,600:1080]=cv2.GC_BGD
mask[230:620,330:540]=cv2.GC_FGD; mask[130:200,420:640]=cv2.GC_FGD; mask[260:640,660:840]=cv2.GC_FGD
mask[950:1750,150:950]=cv2.GC_FGD
bg=np.zeros((1,65));fg=np.zeros((1,65))
cv2.grabCut(src,mask,None,bg,fg,10,cv2.GC_INIT_WITH_MASK)
m=((mask==1)|(mask==3)).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=((lab==k)*255).astype(np.uint8)
m=cv2.erode(m,np.ones((3,3),np.uint8)); m=cv2.GaussianBlur(m,(0,0),1.6)
cv2.imwrite('leo_mask.png',m)
prev=(src.astype(float)*(m[...,None]/255)+np.array([60,20,120])*(1-m[...,None]/255)).astype(np.uint8)
cv2.imwrite('leo_prev.jpg',cv2.resize(prev,None,fx=0.5,fy=0.5))
ys,xs=np.where(m>128); print('leo bbox x',xs.min(),xs.max(),'y',ys.min(),ys.max())
