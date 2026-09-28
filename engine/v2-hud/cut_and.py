import cv2, numpy as np
full=cv2.imread('/mnt/user-data/uploads/1000133289.jpg'); H,W=full.shape[:2]
f=0.25; src=cv2.resize(full,None,fx=f,fy=f,interpolation=cv2.INTER_AREA); h,w=src.shape[:2]
R=lambda v:int(v*f)
mask=np.full((h,w),cv2.GC_BGD,np.uint8)
mask[R(440):h,R(1700):R(3900)]=cv2.GC_PR_FGD
mask[0:R(1450),R(3050):w]=cv2.GC_BGD; mask[0:R(1300),0:R(2090)]=cv2.GC_BGD; mask[0:R(1280),R(2600):w]=cv2.GC_BGD; mask[R(2650):h,0:R(2150)]=cv2.GC_BGD
mask[R(2200):h,R(3500):w]=cv2.GC_BGD
mask[R(620):R(1250),R(2190):R(2500)]=cv2.GC_FGD; mask[R(505):R(660),R(2215):R(2495)]=cv2.GC_FGD; mask[R(1500):R(2950),R(2200):R(3000)]=cv2.GC_FGD
mask[R(2260):R(2500),R(2120):R(2400)]=cv2.GC_FGD; mask[R(1790):R(2040),R(3560):R(3740)]=cv2.GC_FGD
mask[R(1750):R(2600),R(1900):R(2200)]=cv2.GC_FGD
bg=np.zeros((1,65));fg=np.zeros((1,65))
cv2.grabCut(src,mask,None,bg,fg,10,cv2.GC_INIT_WITH_MASK)
m=((mask==1)|(mask==3)).astype(np.uint8)*255
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m); k=1+np.argmax(st[1:,4]); m=((lab==k)*255).astype(np.uint8)
m=cv2.resize(m,(W,H),interpolation=cv2.INTER_CUBIC); m=cv2.GaussianBlur(m,(0,0),4)
cv2.imwrite('and_mask.png',m)
prev=(full.astype(float)*(m[...,None]/255)+np.array([60,20,120])*(1-m[...,None]/255)).astype(np.uint8)
cv2.imwrite('and_prev.jpg',cv2.resize(prev,None,fx=0.2,fy=0.2))
ys,xs=np.where(m>128); print('and bbox x',xs.min(),xs.max(),'y',ys.min(),ys.max())

# --- pass 2: soft luminance key on the hair top (flat GrabCut box edge vs near-black backdrop) ---
m=cv2.imread('and_mask.png',0).astype(np.float32)
y0,y1,x0,x1=480,720,2150,2560
hsv=cv2.cvtColor(full[y0:y1,x0:x1],cv2.COLOR_BGR2HSV); V=hsv[...,2].astype(np.float32)
key=np.clip((V-18)/22,0,1); key=cv2.GaussianBlur(key,(0,0),2.5)
w=np.clip((y1-np.arange(y0,y1))/60.0,0,1)[:,None]
m[y0:y1,x0:x1]=m[y0:y1,x0:x1]*(1-w+w*key)
m=cv2.GaussianBlur(m,(0,0),1.5); cv2.imwrite('and_mask.png',m.astype(np.uint8))
